#!/usr/bin/env python3
"""Collect the facts of a property-test run for the HTML report.

Reads the runner's report (summary.json) and extra/qa/known_bugs.md and writes
one JSON file with everything the report shows that code can decide: run data,
totals, properties per test program, issues with their failures, and the list
of issues the Claude Code agent is asked to analyse. Python standard library
only; the agent never writes this file.

Usage: prepare.py --results DIR --source DIR --out FILE [--scope all|new]
                  [--workdir-prefix /work]

--scope all  the agent analyses every issue of the run;
--scope new  only new issues, regressions, flaky failures and possibly fixed
             issues (known issues keep their known_bugs.md description).
"""

import argparse
import fnmatch
import json
import re
import shlex
from pathlib import Path

SEVERITIES = ("high", "medium", "low")

# Default component per test program; the agent may refine it.
COMPONENTS = {
    "gtid_set_property_test": "GTID sets",
    "byte_span_codec_property_test": "Utilities",
    "units_property_test": "Utilities",
    "cipher_context_property_test": "Encryption",
    "composite_binlog_name_property_test": "Binlog names",
    "event_property_test": "Binlog events",
    "reader_context_property_test": "Event reader",
    "rewriter_property_test": "Rewrite mode",
    "storage_property_test": "Storage",
    "config_property_test": "Configuration",
    "cli_property_test": "CLI",
    "mysql_property_test": "MySQL system tests",
}


def strip_md(cell):
    cell = cell.strip()
    if len(cell) >= 2 and cell[0] == "`" and cell[-1] == "`" and cell.count("`") == 2:
        cell = cell[1:-1]
    return cell.replace("\\|", "|")


def read_known_bugs(path):
    """Rows of the known-bugs table, as run_property_tests.py reads them."""
    if not path.exists():
        return []
    rows, header = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            header = None
            continue
        cells = [strip_md(c) for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if header is None:
            lowered = [c.lower() for c in cells]
            if "test" in lowered and "issue" in lowered:
                header = lowered
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        row = dict(zip(header, cells, strict=False))
        if row.get("test"):
            rows.append(row)
    return rows


def variant_applies(row, variant):
    pattern = row.get("variant", "").strip()
    return not pattern or fnmatch.fnmatchcase(variant, pattern)


def relative_log(log, results_dir):
    """The runner stores absolute log paths; the report and the agent use results/logs/..."""
    if not log:
        return ""
    marker = "/logs/"
    if marker in log:
        return "results/logs/" + log.split(marker, 1)[1]
    return ""


def reproduce(result, prefix):
    """The command that replays the failure, with WORKDIR in place of the job's path."""
    command = result.get("command", "")
    if not command:
        return ""
    if prefix:
        command = command.replace(prefix.rstrip("/") + "/", "$WORKDIR/")
    if result.get("blob"):
        command = f"PBT_REPRODUCE={shlex.quote(result['blob'])} {command}"
    return command


def failure_entry(result, results_dir, prefix):
    message = result.get("message", "")
    return {
        "test": result["test_id"],
        "kind": result.get("kind", ""),
        "classification": result.get("classification", ""),
        "flaky": message.startswith("FLAKY:"),
        "message": message,
        "report": result.get("report", ""),
        "command": reproduce(result, prefix),
        "duration": round(result.get("duration") or 0, 1),
        "log": relative_log(result.get("log", ""), results_dir),
    }


def build(summary, bugs, results_dir, prefix, scope):
    run, totals, results = summary["run"], summary["totals"], summary["results"]
    variant = run.get("variant", "")
    bugs = [b for b in bugs if variant_applies(b, variant)]
    rows_by_issue = {}
    for row in bugs:
        rows_by_issue.setdefault(row.get("issue", ""), []).append(row)

    executables = {}
    for r in results:
        c = executables.setdefault(r["executable"], {"passed": 0, "failed": 0, "errors": 0})
        key = {"passed": "passed", "failed": "failed"}.get(r["status"], "errors")
        c[key] += 1

    issues, new_ids = {}, {}

    def issue(issue_id, status, severity, component):
        if issue_id not in issues:
            rows = rows_by_issue.get(issue_id, [])
            issues[issue_id] = {
                "id": issue_id,
                "status": status,
                "severity": severity,
                "component": component,
                "known_description": [r.get("description", "") for r in rows if r.get("description")],
                "properties": sorted({r["test"] for r in rows}),
                "failures": [],
                "passed_properties": [],
            }
        return issues[issue_id]

    for r in results:
        if r["status"] != "failed":
            continue
        component = COMPONENTS.get(r["executable"], r["executable"])
        cls = r.get("classification", "")
        if cls == "new":
            issue_id = new_ids.setdefault(r["test_id"], f"NEW-{len(new_ids) + 1:02d}")
            entry = issue(issue_id, "new", "untriaged", component)
        else:
            status = "regression" if cls == "regression" else "open"
            entry = issue(r.get("issue") or "UNKNOWN", status, r.get("severity") or "unknown", component)
            if status == "regression":
                entry["status"] = "regression"
        entry["failures"].append(failure_entry(r, results_dir, prefix))
        if r["test_id"] not in entry["properties"]:
            entry["properties"].append(r["test_id"])

    for bug in summary.get("possibly_fixed", []):
        issue_id = bug.get("issue", "")
        component = COMPONENTS.get(bug.get("test", "").split("::")[0], "")
        entry = issue(issue_id, "possibly fixed", bug.get("severity") or "unknown", component)
        passed = [r["test_id"] for r in results if fnmatch.fnmatchcase(r["test_id"], bug.get("test", ""))]
        entry["passed_properties"].extend(t for t in passed if t not in entry["passed_properties"])

    # Properties of an open issue that passed in this run (the issue has other failures).
    passed_ids = {r["test_id"] for r in results if r["status"] == "passed"}
    for entry in issues.values():
        for prop in entry["properties"]:
            if prop in passed_ids and prop not in entry["passed_properties"]:
                entry["passed_properties"].append(prop)
        entry["properties"].sort()

    order = {"new": 0, "regression": 1, "open": 2, "possibly fixed": 3}
    sev = {"untriaged": 0, "high": 1, "medium": 2, "low": 3}
    ordered = sorted(issues.values(), key=lambda i: (order[i["status"]], sev.get(i["severity"], 4), i["id"]))

    if scope == "all":
        analyse = [i["id"] for i in ordered]
    else:
        analyse = [
            i["id"]
            for i in ordered
            if i["status"] != "open" or any(f["flaky"] for f in i["failures"])
        ]

    errors = [
        {
            "test": r["test_id"],
            "kind": r.get("kind", ""),
            "message": r.get("message", ""),
            "log": relative_log(r.get("log", ""), results_dir),
        }
        for r in results
        if r["status"] == "error"
    ]

    keep = ("run_id", "started", "finished", "duration_s", "host", "variant", "build_preset",
            "sanitizers", "git_revision", "git_branch", "git_dirty", "s3_problem", "mysql_problem")
    return {
        "schema": 1,
        "run": {k: run.get(k) for k in keep},
        "totals": totals,
        "executables": executables,
        "issues": ordered,
        "errors": errors,
        "analyse": analyse,
        "scope": scope,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", required=True, type=Path, help="run_property_tests.py report directory")
    parser.add_argument("--source", required=True, type=Path, help="percona-binlog-server checkout")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scope", choices=["all", "new"], default="all")
    parser.add_argument("--workdir-prefix", default="/work",
                        help="WORKDIR of the run, replaced by $WORKDIR in reproduce commands")
    args = parser.parse_args()

    summary = json.loads((args.results / "summary.json").read_text())
    bugs = read_known_bugs(args.source / "extra/qa/known_bugs.md")
    data = build(summary, bugs, args.results, args.workdir_prefix, args.scope)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=1))
    counts = {}
    for i in data["issues"]:
        counts[i["status"]] = counts.get(i["status"], 0) + 1
    print(f"prepare: {len(data['issues'])} issues {counts}, {len(data['errors'])} infrastructure errors, "
          f"{len(data['analyse'])} to analyse (scope {args.scope})")


if __name__ == "__main__":
    main()
