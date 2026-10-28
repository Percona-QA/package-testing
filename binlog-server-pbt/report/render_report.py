#!/usr/bin/env python3
"""Build the HTML report of a property-test run.

Merges the facts from prepare.py (input/base.json) with the analysis the
Claude Code agent wrote (analysis/<ISSUE>.json and analysis/overview.json),
checks that analysis first, and writes one self-contained HTML page plus the
merged data as JSON. Without analysis (no agent, a failed agent or a failed
audit) the page shows the known_bugs.md descriptions instead. Python standard
library only.

Usage: render_report.py --base FILE --source DIR --out DIR
                        [--analysis DIR] [--agent-result FILE]
                        [--ai claude|off|failed|rejected] [--ai-error TEXT]
"""

import argparse
import json
import os
import re
from pathlib import Path

TEMPLATE = Path(__file__).with_name("template.html")
SEVERITIES = ("high", "medium", "low")
CONFIDENCE = ("confirmed", "likely", "unverified")
TEXT_FIELDS = {
    # field: (required, max length)
    "title": (True, 200),
    "component": (False, 60),
    "summary": (True, 1500),
    "description": (True, 8000),
    "root_cause": (True, 8000),
    "fix": (True, 8000),
    "impact": (True, 4000),
    "verification": (False, 4000),
}
# `src/binsrv/gtids/gtid_set.cpp`, optionally with :line or :line-line
CODE_REF = re.compile(r"`((?:src|tests|extra|cmake|mtr|packaging)/[A-Za-z0-9_./-]+?)(?::\d+(?:-\d+)?)?`")


def load_json(path, warnings):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        warnings.append(f"{path.name}: not readable JSON ({error.__class__.__name__})")
        return None


def check_issue(issue_id, analysis, base_issue, source, warnings):
    """The fields of one analysis file that pass the checks; problems go to warnings."""
    if not isinstance(analysis, dict):
        warnings.append(f"{issue_id}: analysis is not a JSON object")
        return {}
    if analysis.get("id", issue_id) != issue_id:
        warnings.append(f"{issue_id}: file names issue {analysis.get('id')!r}")
        return {}
    accepted = {}
    for field, (required, limit) in TEXT_FIELDS.items():
        value = analysis.get(field)
        if value is None or value == "":
            if required:
                warnings.append(f"{issue_id}: '{field}' is missing")
            continue
        if not isinstance(value, str):
            warnings.append(f"{issue_id}: '{field}' is not text")
            continue
        if len(value) > limit:
            warnings.append(f"{issue_id}: '{field}' is longer than {limit} characters, cut")
            value = value[:limit].rstrip() + " …"
        accepted[field] = value.strip()
    confidence = analysis.get("confidence")
    if confidence in CONFIDENCE:
        accepted["confidence"] = confidence
    elif confidence is not None:
        warnings.append(f"{issue_id}: confidence {confidence!r} is not one of {', '.join(CONFIDENCE)}")
    severity = analysis.get("severity")
    if base_issue["status"] == "new":
        if severity in SEVERITIES:
            accepted["proposed_severity"] = severity
        elif severity is not None:
            warnings.append(f"{issue_id}: proposed severity {severity!r} is not one of {', '.join(SEVERITIES)}")
    # Every file the analysis names must exist in the tested revision.
    text = "\n".join(v for k, v in accepted.items() if k in TEXT_FIELDS)
    missing = sorted({m for m in CODE_REF.findall(text) if not (source / m).exists()})
    for path in missing:
        warnings.append(f"{issue_id}: names `{path}`, which is not in the source tree")
    return accepted


def fallback_title(issue):
    known = issue.get("known_description") or []
    if known:
        first = re.split(r"(?<=[.!?])\s+", known[0].strip(), maxsplit=1)[0]
        first = first.replace("`", "")
        return first if len(first) <= 140 else first[:137].rstrip() + "…"
    if issue["failures"]:
        return issue["failures"][0]["test"].split("::")[-1]
    return issue["id"]


def deterministic_notes(issues):
    """One note per failure that is new, a regression or flaky, and per possibly fixed issue."""
    notes = []
    for issue in issues:
        if issue["status"] == "possibly fixed":
            for test in issue.get("passed_properties") or issue["properties"]:
                notes.append({"test": test, "issue": issue["id"],
                              "verdict": f"{issue['id']} possibly fixed",
                              "detail": "Every property of this open known bug passed. Verify and set its status "
                                        "to fixed in known_bugs.md."})
            continue
        for failure in issue["failures"]:
            if issue["status"] == "new":
                verdict = "New, untriaged"
                detail = failure["message"]
            elif issue["status"] == "regression":
                verdict = f"Regression of {issue['id']}"
                detail = failure["message"]
            elif failure["flaky"]:
                verdict = f"Flaky · {issue['id']}"
                detail = failure["message"]
            else:
                continue
            notes.append({"test": failure["test"], "issue": issue["id"], "verdict": verdict, "detail": detail})
    return notes


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--analysis", type=Path)
    parser.add_argument("--agent-result", type=Path)
    parser.add_argument("--ai", choices=["claude", "off", "failed", "rejected"], default="off")
    parser.add_argument("--ai-error", default="")
    args = parser.parse_args()

    base = json.loads(args.base.read_text())
    warnings = []
    use_analysis = args.ai in ("claude", "failed") and args.analysis and args.analysis.is_dir()
    issues = {i["id"]: dict(i, analysed=False) for i in base["issues"]}
    analysed = 0
    overview, agent_notes = None, {}

    if use_analysis:
        for path in sorted(args.analysis.glob("*.json")):
            if path.name == "overview.json":
                continue
            issue_id = path.stem
            if issue_id not in issues:
                warnings.append(f"{path.name}: no issue {issue_id} in this run, ignored")
                continue
            analysis = load_json(path, warnings)
            if analysis is None:
                continue
            accepted = check_issue(issue_id, analysis, issues[issue_id], args.source, warnings)
            if "title" in accepted and "summary" in accepted:
                issues[issue_id].update(accepted, analysed=True)
                analysed += 1
        overview_path = args.analysis / "overview.json"
        if overview_path.exists():
            data = load_json(overview_path, warnings) or {}
            if isinstance(data.get("overview"), str) and data["overview"].strip():
                overview = data["overview"].strip()[:2000]
            tests = {f["test"] for i in issues.values() for f in i["failures"]} | {
                p for i in issues.values() for p in i.get("passed_properties", [])}
            for note in data.get("notes") or []:
                if not isinstance(note, dict) or not isinstance(note.get("detail"), str):
                    warnings.append("overview.json: a note is not {test, detail}")
                elif note.get("test") not in tests:
                    warnings.append(f"overview.json: note for {note.get('test')!r}, which has no failure in this run")
                else:
                    agent_notes[note["test"]] = note["detail"].strip()[:1500]

    for issue in issues.values():
        issue.setdefault("title", fallback_title(issue))
        issue.setdefault("summary", "")
    notes = deterministic_notes(issues.values())
    for note in notes:
        if note["test"] in agent_notes:
            note["detail"] = agent_notes[note["test"]]

    requested = set(base.get("analyse", []))
    ai = {"mode": args.ai, "requested": len(requested),
          "analysed": sum(1 for i in issues.values() if i["analysed"] and i["id"] in requested),
          "warnings": warnings, "error": args.ai_error, "scope": base.get("scope")}
    if args.agent_result and args.agent_result.exists():
        result = load_json(args.agent_result, warnings) or {}
        ai.update({k: result.get(k) for k in ("model", "effort", "turns", "cost_usd", "duration_s")})
        if args.ai == "failed" and not ai["error"]:
            ai["error"] = str(result.get("status") or "")

    build = {}
    if os.environ.get("BUILD_URL"):
        build = {"url": os.environ["BUILD_URL"], "number": os.environ.get("BUILD_NUMBER", ""),
                 "name": os.environ.get("BUILD_DISPLAY_NAME", "")}

    report = {
        "run": base["run"],
        "totals": base["totals"],
        "executables": base["executables"],
        "errors": base.get("errors", []),
        "issues": list(issues.values()),
        "notes": notes,
        "overview": overview,
        "ai": ai,
        "build": build,
        # the page is report/report.html; results/ is archived next to report/
        "artifact_base": "../",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.json").write_text(json.dumps(report, indent=1))
    # JSON inside <script>: no '<' at all, so neither </script> nor <!-- can end it
    payload = json.dumps(report, separators=(",", ":")).replace("<", "\\u003c")
    html = TEMPLATE.read_text(encoding="utf-8").replace("__REPORT_DATA__", payload)
    (args.out / "report.html").write_text(html, encoding="utf-8")

    print(f"report: {len(issues)} issues, {analysed} with Claude analysis (mode {args.ai}), {len(warnings)} warnings")
    for warning in warnings:
        print(f"warning: {warning}")


if __name__ == "__main__":
    main()
