#!/usr/bin/env python3
"""Self-test for the SBOM checks, run against the prototype fixtures.

PXB packages do not ship SBOM files yet, so this is the only thing proving the
parsers, structural checks and consistency logic work before packaging lands.
Needs no VM, no container and no installed package.

    python3 -m pytest -v sbom_checks/tests/
"""

import copy
import json
import os
import shutil
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))

from sbom_checks import (audit, config, consistency, discovery, external_tools,
                         licenses, parsers, structural)
from sbom_checks.backends import LocalBackend
from sbom_checks.models import Component

TESTDATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "testdata"))
STEM = "percona-xtrabackup-97"
ROOT_NAME = "percona-xtrabackup-97"
ROOT_VERSION = "9.7.1-rc1"
EXPECTED_COMPONENTS = 18


@pytest.fixture
def workdir():
    path = tempfile.mkdtemp(prefix="pxb-sbom-test-")
    for name in os.listdir(TESTDATA):
        shutil.copy(os.path.join(TESTDATA, name), os.path.join(path, name))
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _audit(path, **kwargs):
    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=path)
    assert sets, "discovery found no SBOM set in %s" % path
    kwargs.setdefault("expect_name", ROOT_NAME)
    kwargs.setdefault("expect_version", ROOT_VERSION)
    kwargs.setdefault("run_tools", False)
    return audit.audit(backend, sets[0], **kwargs)


def _rewrite_json(path, mutate):
    with open(path) as handle:
        doc = json.load(handle)
    mutate(doc)
    with open(path, "w") as handle:
        json.dump(doc, handle)


def _messages(report):
    return "\n".join(str(f) for f in report.findings)


# --- the happy path -------------------------------------------------------

def test_fixtures_are_a_complete_set(workdir):
    backend = LocalBackend()
    sets, considered = discovery.discover(backend, sbom_dir=workdir)
    assert len(sets) == 1, considered
    assert sets[0].stem == STEM
    assert sets[0].missing() == []


def test_clean_fixtures_pass(workdir):
    report = _audit(workdir)
    assert report.ok, _messages(report)


def test_every_format_parses_the_same_component_count(workdir):
    report = _audit(workdir)
    for fmt, components in report.by_format.items():
        assert len(components) == EXPECTED_COMPONENTS, (
            "%s parsed %d components, expected %d" % (fmt, len(components), EXPECTED_COMPONENTS))


def test_duplicate_xxhash_entries_are_not_a_finding(workdir):
    """xxhash 0.8.3 and xxhash-lz4 1.10.0 are both legitimate -- the standalone
    copy plus the one bundled in lz4. Keying on name alone would false-positive."""
    report = _audit(workdir)
    names = [c.name for c in report.by_format["cdx"]]
    assert "xxhash" in names and "xxhash-lz4" in names
    assert report.ok, _messages(report)


# --- the checks must actually catch things --------------------------------

def test_missing_file_is_reported(workdir):
    os.remove(os.path.join(workdir, STEM + ".licenses.txt"))
    report = _audit(workdir)
    assert not report.ok
    assert "missing licenses" in _messages(report)


def test_dropped_component_breaks_consistency(workdir):
    path = os.path.join(workdir, STEM + ".licenses.txt")
    lines = [l for l in open(path).read().splitlines() if not l.startswith("zstd ")]
    open(path, "w").write("\n".join(lines) + "\n")
    report = _audit(workdir)
    assert not report.ok
    assert "zstd" in _messages(report)
    assert "missing from .licenses.txt" in _messages(report)


def test_version_mismatch_between_formats_is_caught(workdir):
    _rewrite_json(os.path.join(workdir, STEM + ".spdx.json"),
                  lambda d: [p.update(versionInfo="0.0.0")
                             for p in d["packages"] if p["name"] == "zlib"])
    report = _audit(workdir)
    assert not report.ok
    assert "zlib" in _messages(report)


def test_wrong_root_component_is_caught(workdir):
    _rewrite_json(os.path.join(workdir, STEM + ".cdx.json"),
                  lambda d: d["metadata"]["component"].update(version="1.2.3"))
    report = _audit(workdir)
    assert not report.ok
    assert "metadata.component.version" in _messages(report)


def test_broken_bom_format_is_caught(workdir):
    _rewrite_json(os.path.join(workdir, STEM + ".cdx.json"),
                  lambda d: d.update(bomFormat="NotCycloneDX"))
    report = _audit(workdir)
    assert not report.ok
    assert "bomFormat" in _messages(report)


def test_expected_version_is_asserted(workdir):
    """A directory of downloaded files has no installed package, so PXB_VERSION
    is the only way to check which release the SBOM is for."""
    report = _audit(workdir, expect_version="9.9.9")
    root = [f for f in report.findings if f.where == "root"]
    assert root, "a wrong expected version must be reported"
    assert "9.9.9" in _messages(report)
    # Reported under its own category so the failure names the real problem
    # rather than hiding inside a "document is malformed" test.
    assert all(f.where == "root" for f in root)


def test_expected_version_tolerates_a_package_release_suffix(workdir):
    """The SBOM says 9.7.1-rc1; an rpm or a job parameter may say 9.7.1-rc1.2."""
    report = _audit(workdir, expect_version="9.7.1-rc1.2")
    assert not [f for f in report.findings if f.where == "root"], _messages(report)


def test_expected_version_is_read_from_the_environment(monkeypatch):
    monkeypatch.delenv(config.ENV_EXPECT_VERSION, raising=False)
    assert config.expect_version() is None
    monkeypatch.setenv(config.ENV_EXPECT_VERSION, "9.7.1-rc1")
    assert config.expect_version() == "9.7.1-rc1"
    monkeypatch.setenv(config.ENV_EXPECT_VERSION, "   ")
    assert config.expect_version() is None


def test_wrong_expected_name_is_reported_under_root(workdir):
    report = _audit(workdir, expect_name="percona-xtrabackup-84")
    root = [f for f in report.findings if f.where == "root"]
    assert root, "a wrong expected name must be reported"
    assert "percona-xtrabackup-84" in _messages(report)


def test_invalid_json_is_reported_not_raised(workdir):
    with open(os.path.join(workdir, STEM + ".cdx.json"), "w") as handle:
        handle.write("{ this is not json")
    report = _audit(workdir)
    assert not report.ok
    assert "not valid JSON" in _messages(report)


def test_missing_licence_is_caught(workdir):
    _rewrite_json(os.path.join(workdir, STEM + ".spdx.json"),
                  lambda d: [p.update(licenseConcluded="NOASSERTION",
                                      licenseDeclared="NOASSERTION")
                             for p in d["packages"] if p["name"] == "lz4"])
    report = _audit(workdir)
    assert not report.ok
    assert "lz4" in _messages(report)


def test_duplicate_spdxid_is_caught(workdir):
    def mutate(doc):
        doc["packages"][2]["SPDXID"] = doc["packages"][1]["SPDXID"]
    _rewrite_json(os.path.join(workdir, STEM + ".spdx.json"), mutate)
    report = _audit(workdir)
    assert not report.ok
    assert "is used by both" in _messages(report)


def test_licence_disagreement_is_caught(workdir):
    path = os.path.join(workdir, STEM + ".licenses.txt")
    text = open(path).read().replace("zlib 1.3.2 Zlib", "zlib 1.3.2 GPL-3.0-only")
    open(path, "w").write(text)
    report = _audit(workdir)
    assert not report.ok
    assert "licence disagrees" in _messages(report)


def test_sbom_dir_containing_a_space_is_searched(workdir):
    """An unquoted path split into two arguments and reported the directory as
    empty -- indistinguishable from a package that ships no SBOM."""
    spaced = tempfile.mkdtemp(prefix="pxb sbom dir ")
    try:
        for name in os.listdir(TESTDATA):
            shutil.copy(os.path.join(TESTDATA, name), os.path.join(spaced, name))
        sets, considered = discovery.discover(LocalBackend(), sbom_dir=spaced)
        assert len(sets) == 1, considered
        assert sets[0].missing() == []
    finally:
        shutil.rmtree(spaced, ignore_errors=True)


def test_sbom_dir_finds_files_nested_several_levels_deep(workdir):
    """An extracted archive can nest; the search depth must match the one used
    for the package-owned paths."""
    nested = os.path.join(workdir, "a", "b", "c")
    os.makedirs(nested)
    for name in os.listdir(TESTDATA):
        shutil.move(os.path.join(workdir, name), os.path.join(nested, name))
    sets, considered = discovery.discover(LocalBackend(), sbom_dir=workdir)
    assert len(sets) == 1, considered
    assert sets[0].missing() == []


def test_sibling_directories_do_not_merge_into_one_set(workdir):
    """A backup or leftover copy next to the real SBOM must stay a separate set.

    Keyed on the stem alone these merged, and the merged set could take
    CycloneDX from one directory and SPDX from the other -- so cross-format
    consistency would have compared unrelated documents and passed.
    """
    real = os.path.join(workdir, "sbom")
    backup = os.path.join(workdir, "sbom-backup")
    os.makedirs(real)
    os.makedirs(backup)
    for name in os.listdir(TESTDATA):
        shutil.copy(os.path.join(TESTDATA, name), os.path.join(real, name))
        shutil.copy(os.path.join(TESTDATA, name), os.path.join(backup, name))
    for name in os.listdir(workdir):
        path = os.path.join(workdir, name)
        if os.path.isfile(path):
            os.remove(path)

    sets, considered = discovery.discover(LocalBackend(), sbom_dir=workdir)
    assert len(sets) == 2, considered
    directories = sorted(s.directory for s in sets)
    assert directories == sorted([real, backup])
    # Every file in a set comes from that set's own directory.
    for sbom_set in sets:
        for path in sbom_set.paths.values():
            assert os.path.dirname(path) == sbom_set.directory


def test_default_search_is_limited_to_the_package_directory():
    """Both rpm and deb install under /usr/share/percona-xtrabackup*/; searching
    wider picked up SBOMs belonging to other packages."""
    assert discovery.SEARCH_DIRS == ("/usr/share/percona-xtrabackup*",)


def test_empty_directory_yields_no_sets(workdir):
    empty = tempfile.mkdtemp(prefix="pxb-sbom-empty-")
    try:
        sets, considered = discovery.discover(LocalBackend(), sbom_dir=empty)
        assert sets == []
        assert considered, "discovery must always explain what it looked at"
    finally:
        shutil.rmtree(empty, ignore_errors=True)


# --- external tool status -------------------------------------------------

def _stub(directory, name, body):
    path = os.path.join(directory, name)
    with open(path, "w") as handle:
        handle.write(body)
    os.chmod(path, 0o755)
    return path


def test_missing_tools_are_reported_as_missing_not_as_success(workdir):
    """A tool that never ran must not look like a tool that found nothing.

    Before this, an absent binary produced no findings and the corresponding
    tests passed having validated nothing.
    """
    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=workdir)
    old_cdx, old_trivy = external_tools.CYCLONEDX_BIN, external_tools.TRIVY_BIN
    external_tools.CYCLONEDX_BIN = "/nonexistent/cyclonedx"
    external_tools.TRIVY_BIN = "/nonexistent/trivy"
    try:
        report = audit.audit(backend, sets[0], run_tools=True)
    finally:
        external_tools.CYCLONEDX_BIN, external_tools.TRIVY_BIN = old_cdx, old_trivy

    assert report.tool_status["cyclonedx"] == external_tools.MISSING
    assert report.tool_status["trivy"] == external_tools.MISSING
    assert not [f for f in report.findings if f.where == "cyclonedx-cli"]
    assert not report.vuln_findings


def test_trivy_failure_is_not_reported_as_a_vulnerability(workdir):
    """trivy exits non-zero when it cannot run at all -- a rate-limited DB pull
    from ghcr.io, say. Treating that as a finding would be a phantom CVE."""
    stub = _stub(workdir, "trivy-fatal",
                 "#!/bin/sh\necho 'FATAL failed to download vulnerability DB' >&2\nexit 1\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(TESTDATA, STEM + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.FAILED
    assert result.status != external_tools.FOUND


def test_trivy_findings_are_still_reported(workdir):
    """rc 1 with no fatal marker is a genuine finding and must stay one."""
    stub = _stub(workdir, "trivy-vuln",
                 "#!/bin/sh\necho 'zlib CVE-2023-45853 HIGH'\nexit 1\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(TESTDATA, STEM + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.FOUND
    assert "CVE-2023-45853" in result.output


def test_trivy_clean_scan_is_ok(workdir):
    stub = _stub(workdir, "trivy-clean", "#!/bin/sh\nexit 0\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(TESTDATA, STEM + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.OK


# --- parser edge cases ----------------------------------------------------

def test_table_licence_column_containing_spaces(workdir):
    components = parsers.load_table(
        open(os.path.join(workdir, STEM + ".sbom.txt"), "rb").read())
    kmip = [c for c in components if c.name == "libkmip"][0]
    assert kmip.license == "Apache-2.0 OR BSD-3-Clause"
    assert kmip.linkage == "static"
    assert kmip.origin == "vendored"


def test_licenses_txt_licence_containing_spaces():
    components = parsers.load_licenses(
        b"libkmip 5eeea Apache-2.0 OR BSD-3-Clause\nzlib 1.3.2 Zlib\n")
    assert components[0].license == "Apache-2.0 OR BSD-3-Clause"
    assert components[1].license == "Zlib"


def test_table_header_change_is_a_clear_error():
    with pytest.raises(parsers.ParseError) as excinfo:
        parsers.load_table(b"NAME VERSION LIC\nzlib 1.3.2 Zlib\n")
    assert "format has changed" in str(excinfo.value)


def test_cyclonedx_licence_expression_form_is_read():
    doc, root, components = parsers.load_cyclonedx(
        open(os.path.join(TESTDATA, STEM + ".cdx.json"), "rb").read())
    kmip = [c for c in components if c.name == "libkmip"][0]
    assert kmip.license == "Apache-2.0 OR BSD-3-Clause"


def test_spdx_root_package_is_excluded_from_components():
    doc, root, components = parsers.load_spdx(
        open(os.path.join(TESTDATA, STEM + ".spdx.json"), "rb").read())
    assert root.name == ROOT_NAME
    assert ROOT_NAME not in [c.name for c in components]
    assert len(components) == EXPECTED_COMPONENTS


def test_spdxid_mangling_does_not_break_matching():
    """unordered_dense is SPDXRef-Package-unordered-dense; matching on SPDXID
    instead of name would lose it."""
    doc, root, components = parsers.load_spdx(
        open(os.path.join(TESTDATA, STEM + ".spdx.json"), "rb").read())
    assert "unordered_dense" in [c.name for c in components]


def test_gzipped_sbom_is_read_transparently(workdir):
    """Debian gzips files under /usr/share/doc."""
    import gzip
    source = os.path.join(workdir, STEM + ".cdx.json")
    data = open(source, "rb").read()
    os.remove(source)
    with gzip.open(source + ".gz", "wb") as handle:
        handle.write(data)
    report = _audit(workdir)
    assert report.ok, _messages(report)


def test_licence_normalisation():
    assert licenses.equivalent("GPL-2.0", "GPL-2.0-only")
    assert licenses.equivalent("Apache-2.0 OR BSD-3-Clause", "Apache-2.0")
    assert not licenses.equivalent("Apache-2.0 OR BSD-3-Clause", "Apache-2.0",
                                   strict=True)
    assert not licenses.equivalent("MIT", "GPL-3.0-only")
    assert licenses.is_null("NOASSERTION")


def test_spec_version_is_derived_not_hardcoded():
    from sbom_checks import external_tools
    assert external_tools.spec_version(
        os.path.join(TESTDATA, STEM + ".cdx.json")) == "v1_5"
