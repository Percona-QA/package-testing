#!/usr/bin/env python3
"""PXB SBOM checks for an installed rpm/deb package.

Runs ON THE MOLECULE TARGET HOST, the same way the other pytest-tests do:

    python3 -m pytest -v /package-testing/pytest-tests/test_pxb_sbom.py

Gated by SBOM_CHECK_MODE (off/warn/enforce, default warn): absence of SBOM files
is a skip, malformed SBOM files are a failure. PXB does not ship SBOMs yet, so
the default keeps the job green while making every assertion live the moment
packaging lands.

trivy and cyclonedx-cli are NOT expected here -- this job spans 24 platforms from
centos-7 to debian-13 on two architectures, and cyclonedx-cli is a self-contained
.NET binary. Those checks run in the docker job's controlled environment; set
SBOM_EXTERNAL_TOOLS=1 to opt in on a target host for debugging.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sbom_checks import audit, config, discovery          # noqa: E402
from sbom_checks import external_tools                    # noqa: E402
from sbom_checks.backends import LocalBackend             # noqa: E402
from sbom_checks.models import Finding, render            # noqa: E402


@pytest.fixture(scope="module")
def sbom():
    """Discover and audit once; every test below reads from the same report."""
    backend = LocalBackend()
    sets, considered = discovery.discover(backend, sbom_dir=config.sbom_dir())

    # Always print the discovery trail. Without it a broken discovery ladder is
    # indistinguishable from "no SBOM shipped yet", and in warn mode that
    # difference is invisible.
    print("\nSBOM discovery:")
    for note in considered:
        print("  %s" % note)

    mode = config.check_mode()
    decision = config.decide(mode, bool(sets))

    if decision == config.SKIP_ALL:
        pytest.skip("%s=off" % config.ENV_CHECK_MODE, allow_module_level=True)
    if decision == config.SKIP_ABSENT:
        pytest.skip(config.absent_message("the installed package", considered),
                    allow_module_level=True)
    if decision == config.FAIL_ABSENT:
        pytest.fail(config.absent_message("the installed package", considered))

    package = discovery.expected_root_name(backend, sets[0])

    # An explicit PXB_VERSION wins over the installed package: if you state an
    # expectation you mean it, and a disagreement with what is installed is
    # exactly the failure you asked for. Checking a downloaded directory has no
    # installed package at all, which is the case this exists for.
    version, version_problem = discovery.version_to_assert(
        backend, package, explicit=config.expect_version())
    if config.expect_version():
        print("  expected version: %s (from %s)" % (version, config.ENV_EXPECT_VERSION))
    else:
        print("  installed package: %s %s"
              % (package, version or "(version unknown -- set %s to assert one)"
                 % config.ENV_EXPECT_VERSION))

    report = audit.audit(
        backend, sets[0],
        expect_name=package,
        expect_version=version,
        run_tools=config.external_tools_on_target(),
    )

    # Without a version, structural.check_* skips the comparison and reports
    # nothing, so the root test would pass having verified nothing. Record it as
    # a root finding so the failure lands on the test that promises this check.
    if version_problem:
        report.findings.append(Finding("root", version_problem))

    # Both entrypoints validate sets[0]. If discovery turned up more than one,
    # say so loudly rather than silently ignoring the rest -- two SBOM sets
    # under the package directory means a stale or leftover copy is shipped
    # alongside the real one.
    if len(sets) > 1:
        report.findings.append(Finding(
            "set",
            "discovery found %d SBOM sets; only %r was checked. Others: %s"
            % (len(sets), sets[0].label(),
               ", ".join(s.label() for s in sets[1:]))))

    print(report.text())
    for note in report.tool_notes:
        print("  %s" % note)
    return report


def _only(report, where):
    return [f for f in report.findings if f.where == where]


def _require_tool(report, tool, label):
    """Fail unless the tool actually ran.

    Only reached when SBOM_EXTERNAL_TOOLS is on, i.e. the tools were explicitly
    asked for -- so a tool that is absent or could not complete is a setup
    failure, not a benign condition. Skipping here is what previously let an
    unusable toolchain look like a green build.
    """
    status = report.tool_status.get(tool, external_tools.MISSING)
    if status == external_tools.OFF:
        # The gate disabled this tool; its absence is intentional, never a
        # failure. Reached only defensively -- callers skip before this point.
        pytest.skip("%s was not run because its gate is off" % label)
    if status == external_tools.MISSING:
        pytest.fail(
            "%s is not installed, but %s is on.\n"
            "The tool is required when external tools are requested; install it "
            "or turn %s off.\n%s"
            % (label, config.ENV_EXTERNAL_TOOLS, config.ENV_EXTERNAL_TOOLS,
               "\n".join(report.tool_notes)))
    if status == external_tools.FAILED:
        pytest.fail(
            "%s is installed but could not complete, and %s is on.\n%s"
            % (label, config.ENV_EXTERNAL_TOOLS, "\n".join(report.tool_notes)))


def test_sbom_set_is_complete(sbom):
    """All four formats are shipped, not just some of them."""
    assert not _only(sbom, "set"), render(_only(sbom, "set"))


def test_root_component_is_the_expected_release(sbom):
    """The SBOM describes the package and version it is supposed to.

    In a directory run this is only meaningful when PXB_VERSION is set -- there
    is no installed package to compare against.
    """
    assert not _only(sbom, "root"), render(_only(sbom, "root"))


def test_cyclonedx_is_well_formed(sbom):
    assert not _only(sbom, "cdx"), render(_only(sbom, "cdx"))


def test_spdx_is_well_formed(sbom):
    assert not _only(sbom, "spdx"), render(_only(sbom, "spdx"))


def test_sbom_table_is_well_formed(sbom):
    assert not _only(sbom, "table"), render(_only(sbom, "table"))


def test_licenses_list_is_well_formed(sbom):
    assert not _only(sbom, "licenses"), render(_only(sbom, "licenses"))


def test_formats_agree_with_each_other(sbom):
    """All four files come from one generator in one run, so they must describe
    the same components with the same licences."""
    assert not _only(sbom, "consistency"), render(_only(sbom, "consistency"))


def test_cyclonedx_passes_schema_validation(sbom):
    if not config.external_tools_on_target():
        pytest.skip("%s is off" % config.ENV_EXTERNAL_TOOLS)
    findings = _only(sbom, "cyclonedx-cli")
    if not findings:
        _require_tool(sbom, "cyclonedx", "cyclonedx-cli")
    assert not findings, render(findings)


def test_no_known_vulnerabilities(sbom):
    """Gated separately from the structural checks: a new upstream CVE in a
    vendored library is a different signal from a malformed SBOM."""
    if not config.external_tools_on_target():
        pytest.skip("%s is off" % config.ENV_EXTERNAL_TOOLS)
    # Before _require_tool: with the scan disabled, a missing or broken trivy
    # must not fail the build for a check that was never going to run.
    if config.vuln_mode() == config.OFF:
        pytest.skip("%s is off" % config.ENV_VULN_MODE)
    if not sbom.vuln_findings:
        _require_tool(sbom, "trivy", "trivy")
        return
    if config.vuln_mode() != config.ENFORCE:
        pytest.skip("%s=%s\n%s" % (config.ENV_VULN_MODE, config.vuln_mode(),
                                   sbom.vuln_text()))
    pytest.fail(sbom.vuln_text())
