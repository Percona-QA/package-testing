#!/usr/bin/env python3
"""Audit what the Claude Code report agent did.

Adapted from Percona-Lab/ci-ai-kit examples/jobs-report/audit_agent.py. The
agent may run Python it writes, so its tool allowlist limits intent, not
effect; the container mounts its inputs read-only. This gate reads the
transcript and fails when a script or command the agent wrote reaches for the
network, starts processes, builds code at run time or touches the instance
metadata service, and when it writes outside work/ and analysis/. It catches
mistakes and plain prompt injection, not code that hides itself. A failed
audit means the job does not publish the agent's analysis.

Usage: audit_agent.py [log/agent-transcript.jsonl] [analysis]. Exit 1 on any
finding, and when there is analysis but no transcript.
"""

import json
import posixpath
import re
import sys
from pathlib import Path

ROOT = "/ai"  # the agent's working directory in the job container
WRITABLE = (f"{ROOT}/work/", f"{ROOT}/analysis/")

CODE_PATTERNS = {
    "socket": r"\bimport\s+socket\b|\bfrom\s+socket\b|\bsocket\.\w+\(",
    "urllib": r"\burllib\b",
    "requests": r"\bimport\s+requests\b|\bfrom\s+requests\b|\brequests\.(get|post|put|delete|head|request|Session)\b",
    "http.client": r"\bhttp\.client\b",
    "subprocess": r"\bsubprocess\b",
    "os.system": r"\bos\.system\b",
    "os.popen": r"\bos\.popen\b",
    "os.exec/spawn": r"\bos\.(exec\w*|spawn\w*|fork)\s*\(",
    "pty": r"\bimport\s+pty\b|\bfrom\s+pty\b|\bpty\.\w+\(",
    "eval": r"(?<![\w.])eval\s*\(",
    "exec": r"(?<![\w.])exec\s*\(",
    "__import__": r"__import__",
    "compile": r"(?<![\w.])compile\s*\(",
    "importlib": r"\bimportlib\b",
    "boto3": r"\bboto3\b",
    "botocore": r"\bbotocore\b",
    "ctypes": r"\bctypes\b",
    "metadata service": r"169\.254\.169\.254|fd00:ec2::254",
}
# Shell commands only: an analysis text may well mention curl.
SHELL_PATTERNS = {
    "network tool": r"(?:^|[\s;&|(`$])(curl|wget|nc|ncat|socat|telnet|ssh|scp)(?=\s|$)",
    # analysis files are not scanned, so they must not be run either
    "runs an analysis file": r"python3?\s+(?:-\S+\s+)*\S*analysis/",
}
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def tool_calls(lines):
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content") or []:
            if block.get("type") == "tool_use":
                yield block["name"], block.get("input") or {}


def texts(name, arguments):
    """The code a tool call carries: (label, text, is_shell)."""
    if name == "Bash":
        yield "command", arguments.get("command") or "", True
    elif name == "Write":
        path = arguments.get("file_path", "")
        if not is_analysis(path):
            yield path, arguments.get("content") or "", False
    elif name == "Edit":
        path = arguments.get("file_path", "")
        if not is_analysis(path):
            yield path, arguments.get("new_string") or "", False
    elif name == "MultiEdit":
        for edit in arguments.get("edits") or []:
            yield arguments.get("file_path", ""), edit.get("new_string") or "", False


def is_analysis(path):
    """analysis/*.json is prose about C++ code for the report, never run: not scanned for code patterns."""
    normal = posixpath.normpath(posixpath.join(ROOT, path))
    return normal.startswith(f"{ROOT}/analysis/") and normal.endswith(".json")


def writable(path):
    normal = posixpath.normpath(posixpath.join(ROOT, path))
    return any((normal + "/").startswith(root) for root in WRITABLE)


def snippet(text, match):
    start = max(match.start() - 30, 0)
    return " ".join(text[start: match.end() + 30].split())[:100]


def audit(lines):
    lines = list(lines)
    findings, calls = [], 0
    for name, arguments in tool_calls(lines):
        calls += 1
        if name in WRITE_TOOLS:
            path = arguments.get("file_path") or arguments.get("notebook_path") or ""
            if not writable(path):
                findings.append(f"{name} outside work/ and analysis/: {path}")
        elif name not in ("Read", "Glob", "Grep", "Bash", "TodoWrite"):
            findings.append(f"unexpected tool {name}")
        for label, text, shell in texts(name, arguments):
            patterns = {**CODE_PATTERNS, **(SHELL_PATTERNS if shell else {})}
            for rule, pattern in patterns.items():
                match = re.search(pattern, text, flags=re.MULTILINE)
                if match:
                    findings.append(f"{name} {label}: {rule}: {snippet(text, match)}")
    notes = []
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            for denial in event.get("permission_denials") or []:
                tool_input = denial.get("tool_input") or {}
                command = tool_input.get("command") or json.dumps(tool_input)
                notes.append(f"denied {denial.get('tool_name')}: {' '.join(command.split())[:100]}")
    return findings, notes, calls


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "log/agent-transcript.jsonl")
    analysis = Path(sys.argv[2] if len(sys.argv) > 2 else "analysis")
    lines = path.read_text().splitlines() if path.exists() else []
    if not lines:
        written = list(analysis.glob("*.json")) if analysis.is_dir() else []
        print(f"audit: no transcript in {path}, {len(written)} analysis files")
        sys.exit(1 if written else 0)
    findings, notes, calls = audit(lines)
    for note in notes:
        print(f"info  {note}")
    for finding in findings:
        print(f"FAIL  {finding}")
    print(f"audit: {calls} tool calls, {len(findings)} findings, {len(notes)} denied by Claude Code")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
