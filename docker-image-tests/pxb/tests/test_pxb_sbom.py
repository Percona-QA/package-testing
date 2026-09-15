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
from sbom_checks import audit, config, discovery, oci      # noqa: E402
from sbom_checks.backends import DOCKER_BIN, DockerBackend  # noqa: E402
from sbom_checks.models import render                      # noqa: E402

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
    version = discovery.installed_version(backend, package)
    print("  installed package: %s %s" % (package, version or "(version unknown)"))

    report = audit.audit(backend, sets[0], expect_name=package,
                         expect_version=version, run_tools=True)
    print(report.text())
    for note in report.tool_notes:
        print("  %s" % note)
    return report


def _only(report, where):
    return [f for f in report.findings if f.where == where]


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
        findings = _only(sbom, "cyclonedx-cli")
        if not findings and any("cyclonedx-cli not installed" in n
                                for n in sbom.tool_notes):
            pytest.skip("cyclonedx-cli is not installed on this agent")
        assert not findings, render(findings)

    def test_no_known_vulnerabilities(self, sbom):
        """Separate gate: a new upstream CVE is a different signal from a
        malformed SBOM and must not share the same red light."""
        if any("trivy not installed" in n for n in sbom.tool_notes):
            pytest.skip("trivy is not installed on this agent")
        if not sbom.vuln_findings:
            return
        if config.vuln_mode() != config.ENFORCE:
            pytest.skip("%s=%s\n%s" % (config.ENV_VULN_MODE, config.vuln_mode(),
                                       sbom.vuln_text()))
        pytest.fail(sbom.vuln_text())


@pytest.fixture(scope='module')
def referrers():
    """CycloneDX SBOM referrers attached to the image for this architecture."""
    if not config.check_oci():
        pytest.skip("%s is not set" % config.ENV_OCI)

    architecture = 'arm64' if os.uname()[4] in ('aarch64', 'arm64') else 'amd64'
    digest, error = oci.manifest_digest(docker_image, architecture)
    if error:
        pytest.fail(error)

    base = docker_image.split(':')[0]
    reference = "%s@%s" % (base, digest) if digest else docker_image
    print("\nresolving OCI referrers on %s" % reference)

    found, error = oci.discover_referrers(reference)
    if error:
        pytest.fail(error)
    return base, found


class TestPxbOciSbom:
    """SBOM attached to the image in the registry as an OCI referrer.

    percona-docker publishes no referrers today, so this is off unless
    SBOM_CHECK_OCI is set. Referrers attach per manifest digest, so on a
    multi-arch image one architecture can legitimately carry one and another not
    -- the pxb-docker-tests job runs this on both ARM and AMD agents.
    """

    def test_image_has_a_cyclonedx_referrer(self, referrers):
        base, found = referrers
        assert found, ("no CycloneDX SBOM referrer attached to %s for this architecture"
                       % docker_image)

    def test_attached_sbom_is_valid(self, referrers, tmpdir):
        base, found = referrers
        if not found:
            pytest.skip("no referrer to validate")
        files, error = oci.pull_referrer(base, found[0]['digest'], str(tmpdir))
        if error:
            pytest.fail(error)
        assert files, "oras pull produced no files"

        from sbom_checks import external_tools
        result = external_tools.cyclonedx_validate(files[0])
        if not result.available:
            pytest.skip("cyclonedx-cli is not installed on this agent")
        assert result.ok, result.output
