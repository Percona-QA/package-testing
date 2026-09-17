"""Append a platform label to junit testcase names.

Every molecule platform and every docker architecture publishes into one Jenkins
result set, so without this the table shows the same test name many times over
and a skip or failure cannot be attributed to a platform:

    test_cyclonedx_passes_schema_validation      <- which of the 24 platforms?

pytest cannot do this itself. In `_pytest/junitxml.py` the junit `name` is the
last component of the nodeid, and `--junit-prefix` is inserted into *classname*
only -- nothing appends to `name`. Rewriting the finished XML is therefore the
portable route, and it works identically for the modern pytest on the molecule
targets and the pinned pytest 5.2.1 in the docker suite.

    python3 -m sbom_checks.label_junit report.xml --label ubuntu-noble \\
        --only test_pxb_sbom

Exit codes: 0 done (or nothing to do), 1 the file could not be processed.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

EXIT_OK = 0
EXIT_FAIL = 1


def label_tree(root, label, only=None):
    """Append '.<label>' to matching testcase names. Returns the count changed.

    Matching is on `classname`, so one report holding several test modules can
    be labelled selectively -- the docker suite's report.xml carries
    test_container_att.py alongside the SBOM tests.
    """
    suffix = "." + label
    changed = 0
    for testcase in root.iter("testcase"):
        classname = testcase.get("classname") or ""
        name = testcase.get("name") or ""
        if only and only not in classname:
            continue
        if not name or name.endswith(suffix):
            # Already labelled: re-running must not yield test_x.noble.noble.
            continue
        testcase.set("name", name + suffix)
        changed += 1
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="label_junit",
        description="Append a platform label to junit testcase names.")
    parser.add_argument("path", help="junit XML file to rewrite in place")
    parser.add_argument("--label", required=True,
                        help="platform label, e.g. ubuntu-noble or amd64")
    parser.add_argument("--only",
                        help="only label testcases whose classname contains this")
    args = parser.parse_args(argv)

    label = (args.label or "").strip()
    if not label:
        print("label_junit: empty --label, nothing to do")
        return EXIT_OK

    if not os.path.exists(args.path):
        # The checks may legitimately not have run; that is not an error here.
        print("label_junit: %s does not exist, nothing to do" % args.path)
        return EXIT_OK

    try:
        tree = ET.parse(args.path)
    except ET.ParseError as exc:
        # Leave the file alone. An ambiguous report is better than a mangled one.
        print("label_junit: %s is not parseable (%s); left unchanged"
              % (args.path, exc))
        return EXIT_FAIL

    changed = label_tree(tree.getroot(), label, args.only)
    if not changed:
        print("label_junit: no matching testcases in %s" % args.path)
        return EXIT_OK

    try:
        tree.write(args.path, encoding="utf-8", xml_declaration=True)
    except (IOError, OSError) as exc:
        print("label_junit: could not write %s (%s)" % (args.path, exc))
        return EXIT_FAIL

    print("label_junit: labelled %d testcase(s) in %s with .%s"
          % (changed, args.path, label))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
