"""Orchestration: load one SbomSet, validate it, report.

Kept separate from the pytest entrypoints so the same logic backs the CLI, the
molecule target-host test and the docker test.
"""

import os
import tempfile

from . import config, consistency, external_tools, parsers, structural
from .models import Finding, render


class Report(object):
    def __init__(self, sbom_set):
        self.sbom_set = sbom_set
        self.findings = []          # structural + consistency problems
        self.notes = []             # informational, always printed
        self.by_format = {}
        self.vuln_findings = []     # trivy, gated separately
        self.tool_notes = []
        # Explicit per-tool outcome, so a caller can tell "did not run" from
        # "ran and found nothing". Without this a missing binary produced no
        # findings and the tests passed having validated nothing.
        self.tool_status = {}

    @property
    def ok(self):
        return not self.findings

    @property
    def vuln_ok(self):
        return not self.vuln_findings

    def text(self):
        lines = []
        if self.notes:
            lines.extend(self.notes)
        if self.findings:
            lines.append("problems:")
            lines.append(render(self.findings))
        return "\n".join(lines)

    def vuln_text(self):
        return render(self.vuln_findings)


def load_set(backend, sbom_set):
    """Parse every present format. -> (by_format, findings)"""
    by_format = {}
    findings = []
    for fmt in sbom_set.FORMATS:
        path = sbom_set.paths.get(fmt)
        if not path:
            continue
        try:
            raw = backend.read_bytes(path)
        except Exception as exc:                       # noqa: BLE001 - report, never crash
            findings.append(Finding(fmt, "cannot read %s: %s" % (path, exc)))
            continue
        try:
            loaded = parsers.LOADERS[fmt](raw)
        except parsers.ParseError as exc:
            findings.append(Finding(fmt, "%s: %s" % (os.path.basename(path), exc)))
            continue
        if fmt in ("cdx", "spdx"):
            doc, root, components = loaded
            by_format[fmt] = components
            findings.append(None)                      # placeholder, stripped below
            findings.pop()
            by_format.setdefault("_docs", {})[fmt] = (doc, root)
        else:
            by_format[fmt] = loaded
    return by_format, findings


def audit(backend, sbom_set, expect_name=None, expect_version=None,
          strict_licenses=None, run_tools=True):
    """Validate one SBOM file set end to end."""
    if strict_licenses is None:
        strict_licenses = config.license_strict()

    report = Report(sbom_set)
    report.notes.append("SBOM set %r" % sbom_set.stem)
    for fmt in sbom_set.FORMATS:
        path = sbom_set.paths.get(fmt)
        report.notes.append("  %-9s %s" % (fmt, path or "MISSING"))

    missing = sbom_set.missing()
    if missing:
        report.findings.append(Finding(
            "set", "incomplete SBOM set %r: missing %s" % (sbom_set.stem, ", ".join(missing))))

    by_format, parse_findings = load_set(backend, sbom_set)
    report.findings.extend(parse_findings)
    docs = by_format.pop("_docs", {})
    report.by_format = by_format

    if not by_format:
        report.findings.append(Finding("set", "no SBOM file could be parsed"))
        return report

    if expect_name:
        report.notes.append("  expecting root component %s %s"
                            % (expect_name, expect_version or "(any version)"))

    if "cdx" in docs:
        doc, root = docs["cdx"]
        report.findings.extend(structural.check_cyclonedx(
            doc, root, by_format.get("cdx", []), expect_name, expect_version))
    if "spdx" in docs:
        doc, root = docs["spdx"]
        report.findings.extend(structural.check_spdx(
            doc, root, by_format.get("spdx", []), expect_name, expect_version))
    if "table" in by_format:
        report.findings.extend(structural.check_component_list(by_format["table"], "table"))
    if "licenses" in by_format:
        report.findings.extend(
            structural.check_component_list(by_format["licenses"], "licenses"))

    report.notes.append("  compared: %s" % consistency.summary(by_format))
    report.findings.extend(consistency.check_all(by_format, strict_licenses=strict_licenses))

    if run_tools:
        _run_tools(backend, sbom_set, report)

    return report


def _run_tools(backend, sbom_set, report):
    """trivy + cyclonedx-cli, both optional and both non-fatal when absent."""
    # Seed trivy from the gate: with SBOM_VULN_MODE=off the scan is not run at
    # all, and every early return below must say "off" rather than "missing" --
    # otherwise a deliberately disabled tool is reported as a setup failure.
    vuln_off = config.vuln_mode() == config.OFF
    report.tool_status = {
        "cyclonedx": external_tools.MISSING,
        "trivy": external_tools.OFF if vuln_off else external_tools.MISSING,
    }

    cdx_path = sbom_set.paths.get("cdx")
    if not cdx_path:
        report.tool_notes.append("no CycloneDX document -- external tools not run")
        return
    workdir = tempfile.mkdtemp(prefix="pxb-sbom-")
    try:
        local = backend.export(cdx_path, workdir)
    except Exception as exc:                           # noqa: BLE001
        report.tool_notes.append("could not materialise %s: %s" % (cdx_path, exc))
        report.tool_status["cyclonedx"] = external_tools.FAILED
        if not vuln_off:
            report.tool_status["trivy"] = external_tools.FAILED
        return

    validated = external_tools.cyclonedx_validate(local)
    report.tool_status["cyclonedx"] = validated.status
    if validated.status == external_tools.MISSING:
        report.tool_notes.append("cyclonedx-cli not installed -- schema validation skipped")
    elif validated.status == external_tools.OK:
        report.tool_notes.append("cyclonedx-cli validate: OK (%s)"
                                 % (external_tools.spec_version(local) or "unknown spec"))
    else:
        report.findings.append(Finding("cyclonedx-cli", validated.output))

    if vuln_off:
        report.tool_notes.append("%s=off -- vulnerability scan not run"
                                 % config.ENV_VULN_MODE)
        return

    scanned = external_tools.trivy_sbom(local)
    report.tool_status["trivy"] = scanned.status
    if scanned.status == external_tools.MISSING:
        report.tool_notes.append("trivy not installed -- vulnerability scan skipped")
    elif scanned.status == external_tools.OK:
        report.tool_notes.append("trivy sbom: no unfixed HIGH/CRITICAL findings")
    elif scanned.status == external_tools.FAILED:
        # Could not run -- a DB download failure, a rate limit. Reporting this
        # as a vulnerability would be a phantom CVE.
        report.tool_notes.append("trivy could not complete the scan:\n%s" % scanned.output)
    else:
        report.vuln_findings.append(Finding("trivy", scanned.output))
