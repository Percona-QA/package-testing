#!/usr/bin/env python3
"""PXB SBOM checks for a docker image.

Collected by the existing ./run.sh (pytest -v --junit-xml report.xml), so it
lands in the report the pxb-docker-tests job already publishes.

Gated by SBOM_CHECK_MODE (off/warn/enforce, default warn): absence is a skip,
malformed SBOM files are a failure. PXB images do not ship SBOMs yet, so the
default keeps the job green.

Unlike the target-host suite this runs on a Jenkins agent where trivy and
cyclonedx-cli can be provisioned, so the deep validation happens here.
"""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from settings import *                                    # noqa: F401,F403,E402
from sbom_checks import audit, config, discovery            # noqa: E402
from sbom_checks import external_tools                     # noqa: E402
from sbom_checks.backends import DOCKER_BIN, DockerBackend  # noqa: E402
from sbom_checks.models import Finding, render             # noqa: E402

# Its own container: each test file in this suite starts one.
container_name = 'pxb-docker-test-sbom'


@pytest.fixture(scope='module')
def backend():
    """A running container started from the image under test.

    Same pattern as tests/test_container_att.py -- the image has no long-running
    service, so the entrypoint is replaced with `sleep infinity`.
    """
    subprocess.call([DOCKER_BIN, 'rm', '-f', container_name],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    docker_id = subprocess.check_output(
        [DOCKER_BIN, 'run', '--name', container_name, '--entrypoint', 'sleep',
         '-d', docker_image, 'infinity']
    ).decode().strip()
    yield DockerBackend(docker_id)
    subprocess.check_call([DOCKER_BIN, 'rm', '-f', docker_id])


@pytest.fixture(scope='module')
def sbom(backend):
    sets, considered = discovery.discover(backend, sbom_dir=config.sbom_dir())

    print("\nSBOM discovery in %s:" % docker_image)
    for note in considered:
        print("  %s" % note)

    mode = config.check_mode()
    decision = config.decide(mode, bool(sets))

    if decision == config.SKIP_ALL:
        pytest.skip("%s=off" % config.ENV_CHECK_MODE)
    if decision == config.SKIP_ABSENT:
        pytest.skip(config.absent_message(docker_image, considered))
    if decision == config.FAIL_ABSENT:
        pytest.fail(config.absent_message(docker_image, considered))

    package = discovery.expected_root_name(backend, sets[0])
    version, version_problem = discovery.version_to_assert(backend, package)
    print("  installed package: %s %s" % (package, version or "(version unknown)"))

    report = audit.audit(backend, sets[0], expect_name=package,
                         expect_version=version,
                         run_tools=config.external_tools_on_target())

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


class TestPxbSbom:
    def test_sbom_set_is_complete(self, sbom):
        assert not _only(sbom, "set"), render(_only(sbom, "set"))

    def test_root_component_is_the_expected_release(self, sbom):
        """The SBOM describes the package and version installed in the image."""
        assert not _only(sbom, "root"), render(_only(sbom, "root"))

    def test_cyclonedx_is_well_formed(self, sbom):
        assert not _only(sbom, "cdx"), render(_only(sbom, "cdx"))

    def test_spdx_is_well_formed(self, sbom):
        assert not _only(sbom, "spdx"), render(_only(sbom, "spdx"))

    def test_sbom_table_is_well_formed(self, sbom):
        assert not _only(sbom, "table"), render(_only(sbom, "table"))

    def test_licenses_list_is_well_formed(self, sbom):
        assert not _only(sbom, "licenses"), render(_only(sbom, "licenses"))

    def test_formats_agree_with_each_other(self, sbom):
        assert not _only(sbom, "consistency"), render(_only(sbom, "consistency"))

    def test_cyclonedx_passes_schema_validation(self, sbom):
        if not config.external_tools_on_target():
            pytest.skip("%s is off" % config.ENV_EXTERNAL_TOOLS)
        findings = _only(sbom, "cyclonedx-cli")
        if not findings:
            _require_tool(sbom, "cyclonedx", "cyclonedx-cli")
        assert not findings, render(findings)

    def test_no_known_vulnerabilities(self, sbom):
        """Separate gate: a new upstream CVE is a different signal from a
        malformed SBOM and must not share the same red light."""
        if not config.external_tools_on_target():
            pytest.skip("%s is off" % config.ENV_EXTERNAL_TOOLS)
        # Before _require_tool: with the scan disabled, a missing or broken
        # trivy must not fail a check that was never going to run.
        if config.vuln_mode() == config.OFF:
            pytest.skip("%s is off" % config.ENV_VULN_MODE)
        if not sbom.vuln_findings:
            _require_tool(sbom, "trivy", "trivy")
            return
        if config.vuln_mode() != config.ENFORCE:
            pytest.skip("%s=%s\n%s" % (config.ENV_VULN_MODE, config.vuln_mode(),
                                       sbom.vuln_text()))
        pytest.fail(sbom.vuln_text())
