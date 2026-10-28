#!/usr/bin/env python3
"""Run the report agent: Claude Code, headless, on Amazon Bedrock.

Follows Percona-Lab/ci-ai-kit (engines/claude_code.py and
examples/jobs-report): a pinned Claude Code, credentials from the EC2 worker's
instance role (nothing stored in Jenkins), a tool allowlist, one console line
per agent step and the full transcript for the audit. The job runs this in a
container where input/, results/ and source/ are read-only and only work/,
analysis/ and log/ are writable.

The transcript (Claude Code's stream-json events) goes to stdout, which the
job writes to a file outside the container, so the agent cannot rewrite what
the audit reads. Progress lines go to stderr. Writes work/agent-result.json.
Exit code 0 when the session finished, 1 otherwise (the analysis written so
far is kept).

Environment: AI_MODEL (catalog name), AI_EFFORT, AI_MAX_TURNS,
CLAUDE_CODE_VERSION, BEDROCK_REGION (optional), HOME.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROMPT = Path(__file__).with_name("agent-prompt.md")

# Bedrock inference profiles, as in ci-ai-kit models/catalog.toml (us-east-1).
MODELS = {
    "claude-opus-5-5": "us.anthropic.claude-opus-5-5",
    "claude-fable-5-1": "us.anthropic.claude-fable-5-1",
    "claude-opus-5": "us.anthropic.claude-opus-5",
    "claude-sonnet-5": "us.anthropic.claude-sonnet-5",
}
HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Files and Python only: no network tools, no git, no other shell commands.
ALLOWED = "Read,Glob,Grep,Write,Edit,Bash(python3:*),Bash(ls:*),Bash(head:*),Bash(wc:*)"
# Subagents are off so that every tool call is in the transcript the audit reads.
DISALLOWED = "WebFetch,WebSearch,Task,Agent"


def install(version):
    """Install the pinned Claude Code into ~/.local/bin and return its path."""
    subprocess.run(["bash", "-c", f"curl -fsSL https://claude.ai/install.sh | bash -s {version}"],
                   check=True, stdout=subprocess.DEVNULL)
    claude = Path.home() / ".local/bin/claude"
    subprocess.run([str(claude), "--version"], check=True, stdout=sys.stderr)
    return claude


def describe(event):
    """One console line per agent step."""
    if event.get("type") == "system" and event.get("subtype") == "init":
        return f"session: model={event.get('model')} tools={len(event.get('tools', []))}"
    if event.get("type") != "assistant":
        return None
    lines = []
    for block in event["message"].get("content", []):
        if block.get("type") == "text" and block["text"].strip():
            lines.append("agent: " + block["text"].strip().splitlines()[0][:160])
        elif block.get("type") == "tool_use":
            arguments = block.get("input", {})
            detail = next((str(arguments[k]) for k in ("command", "file_path", "pattern") if arguments.get(k)), "")
            lines.append(f"tool:  {block['name']} {detail.splitlines()[0][:140] if detail else ''}")
    return "\n".join(lines) or None


def main():
    model = os.environ.get("AI_MODEL") or "claude-opus-5-5"
    if model not in MODELS:
        sys.exit(f"unknown AI_MODEL {model!r}, known: {', '.join(MODELS)}")
    effort = os.environ.get("AI_EFFORT") or "medium"
    max_turns = os.environ.get("AI_MAX_TURNS") or "300"
    Path("analysis").mkdir(exist_ok=True)
    Path("work").mkdir(exist_ok=True)
    Path.home().mkdir(parents=True, exist_ok=True)

    claude = install(os.environ["CLAUDE_CODE_VERSION"])
    env = dict(
        os.environ,
        CLAUDE_CODE_USE_BEDROCK="1",
        AWS_REGION=os.environ.get("BEDROCK_REGION") or "us-east-1",
        ANTHROPIC_MODEL=MODELS[model],
        ANTHROPIC_DEFAULT_HAIKU_MODEL=HAIKU,
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
        DISABLE_AUTOUPDATER="1",
    )
    command = [str(claude), "-p", PROMPT.read_text(), "--output-format", "stream-json", "--verbose",
               "--max-turns", max_turns, "--effort", effort,
               "--allowedTools", ALLOWED, "--disallowedTools", DISALLOWED]

    started = time.time()
    result = None
    with subprocess.Popen(command, env=env, stdout=subprocess.PIPE, text=True) as agent:
        for line in agent.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "result":
                result = event
            message = describe(event)
            if message:
                print(message, file=sys.stderr, flush=True)

    result = result or {}
    finished = agent.returncode == 0 and not result.get("is_error") and result.get("subtype") == "success"
    summary = {
        "model": model,
        "bedrock_id": MODELS[model],
        "effort": effort,
        "max_turns": int(max_turns),
        "status": result.get("subtype") or f"exit code {agent.returncode}, no result event",
        "finished": finished,
        "turns": result.get("num_turns"),
        "cost_usd": result.get("total_cost_usd"),
        "duration_s": round(time.time() - started),
        "usage": result.get("usage"),
        "final_message": result.get("result"),
    }
    Path("work/agent-result.json").write_text(json.dumps(summary, indent=2))
    written = len([p for p in Path("analysis").glob("*.json") if p.name != "overview.json"])
    cost = summary["cost_usd"] or 0
    print(f"agent: {summary['status']}, {summary['turns']} turns, estimated cost ${cost:.2f}, "
          f"{written} issue files written", file=sys.stderr)
    sys.exit(0 if finished else 1)


if __name__ == "__main__":
    main()
