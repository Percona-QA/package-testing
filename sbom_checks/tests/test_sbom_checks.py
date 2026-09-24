#!/usr/bin/env python3
"""Self-test for the SBOM checks, run against the prototype fixtures.

The packages do not ship SBOM files yet, so this is the only thing proving the
parsers, structural checks and consistency logic work before packaging lands.
Needs no VM, no container and no installed package. Run from the repo root:

    ~/.venvs/pxb-sbom/bin/python -m pytest -v sbom_checks/tests/

Tests that hold for any product run once per product in testdata/ (pxb, ps),
with ids like test_clean_fixtures_pass[ps]. PS failures are deliberately left
visible while the PS formats settle, so select a product with its marker:

    ... -m "not ps"      PXB only
    ... -m ps            PS only

-m rather than -k: -k is substring matching on test names, and would silently
drop test_non_object_relationships_... ("relationshiPS") from a "not ps" run.
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

from sbom_checks import (audit, check_sbom, config, consistency, discovery,
                         external_tools, label_junit, licenses, parsers,
                         products, structural)
from sbom_checks.backends import LocalBackend
from sbom_checks.models import Component, SbomSet

TESTDATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "testdata"))


class FixtureSet(object):
    """One product's example SBOM files, and what they are known to contain.

    Each points at a flat product directory, never at TESTDATA_ROOT: the copy
    loops use shutil.copy, which raises IsADirectoryError on a subdirectory,
    and the discover()-based tests take sets[0], which would silently become
    another product's set if the root were searched.
    """

    def __init__(self, key, stem, root_name, root_version, components):
        self.key = key
        self.directory = os.path.join(TESTDATA_ROOT, key)
        self.stem = stem
        self.root_name = root_name
        self.root_version = root_version
        self.components = components

    def __repr__(self):
        return "FixtureSet(%r)" % self.key


FIXTURE_SETS = {
    "pxb": FixtureSet("pxb", stem="percona-xtrabackup-97",
                      root_name="percona-xtrabackup-97", root_version="9.7.1-rc1",
                      components=18),
    "ps": FixtureSet("ps", stem="percona-server",
                     root_name="percona-server", root_version="9.7.2-2",
                     components=25),
}
PXB = FIXTURE_SETS["pxb"]

# Tests below that depend on PXB-specific content or format -- the per-component
# .licenses.txt rows, the .sbom.txt column layout, the xxhash-lz4 component --
# stay PXB-only and read these. Everything that holds for any product takes the
# fixture_set fixture instead.
TESTDATA = PXB.directory
STEM = PXB.stem
ROOT_NAME = PXB.root_name
ROOT_VERSION = PXB.root_version
EXPECTED_COMPONENTS = PXB.components


@pytest.fixture(params=[pytest.param(key, marks=getattr(pytest.mark, key), id=key)
                        for key in sorted(FIXTURE_SETS)])
def fixture_set(request):
    """Each product's fixtures in turn. Marked per product (pytest.mark.pxb,
    pytest.mark.ps) so a run can select one with -m."""
    return FIXTURE_SETS[request.param]


def _copy_fixtures(fixture_set_, prefix):
    path = tempfile.mkdtemp(prefix=prefix)
    for name in os.listdir(fixture_set_.directory):
        shutil.copy(os.path.join(fixture_set_.directory, name), os.path.join(path, name))
    return path


@pytest.fixture
def workdir():
    """A scratch copy of the PXB fixtures -- for PXB-only tests, and for tests
    that only need a temporary directory to put stubs in."""
    path = _copy_fixtures(PXB, "pxb-sbom-test-")
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def product_workdir(fixture_set):
    """A scratch copy of the current fixture_set's files."""
    path = _copy_fixtures(fixture_set, "%s-sbom-test-" % fixture_set.key)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def _audit(path, fixture_set_=None, **kwargs):
    fixture_set_ = fixture_set_ or PXB
    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=path)
    assert sets, "discovery found no SBOM set in %s" % path
    kwargs.setdefault("expect_name", fixture_set_.root_name)
    kwargs.setdefault("expect_version", fixture_set_.root_version)
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

def test_fixtures_are_a_complete_set(fixture_set, product_workdir):
    backend = LocalBackend()
    sets, considered = discovery.discover(backend, sbom_dir=product_workdir)
    assert len(sets) == 1, considered
    assert sets[0].stem == fixture_set.stem
    assert sets[0].missing() == []


def test_clean_fixtures_pass(fixture_set, product_workdir):
    report = _audit(product_workdir, fixture_set)
    assert report.ok, _messages(report)


def test_every_format_parses_the_same_component_count(fixture_set, product_workdir):
    report = _audit(product_workdir, fixture_set)
    # Every format, not just the ones that happened to parse: iterating
    # by_format alone passed for a set where two of the four formats failed to
    # parse and were simply absent from it.
    assert sorted(report.by_format) == sorted(SbomSet.FORMATS), (
        "parsed %s of %s" % (sorted(report.by_format), sorted(SbomSet.FORMATS)))
    for fmt, components in report.by_format.items():
        assert len(components) == fixture_set.components, (
            "%s parsed %d components, expected %d" % (fmt, len(components), fixture_set.components))


def test_duplicate_xxhash_entries_are_not_a_finding(workdir):
    """xxhash 0.8.3 and xxhash-lz4 1.10.0 are both legitimate -- the standalone
    copy plus the one bundled in lz4. Keying on name alone would false-positive."""
    report = _audit(workdir)
    names = [c.name for c in report.by_format["cdx"]]
    assert "xxhash" in names and "xxhash-lz4" in names
    assert report.ok, _messages(report)


# --- the checks must actually catch things --------------------------------

def test_missing_file_is_reported(fixture_set, product_workdir):
    os.remove(os.path.join(product_workdir, fixture_set.stem + ".licenses.txt"))
    report = _audit(product_workdir, fixture_set)
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


def test_version_mismatch_between_formats_is_caught(fixture_set, product_workdir):
    _rewrite_json(os.path.join(product_workdir, fixture_set.stem + ".spdx.json"),
                  lambda d: [p.update(versionInfo="0.0.0")
                             for p in d["packages"] if p["name"] == "zlib"])
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "zlib" in _messages(report)


def test_wrong_root_component_is_caught(fixture_set, product_workdir):
    _rewrite_json(os.path.join(product_workdir, fixture_set.stem + ".cdx.json"),
                  lambda d: d["metadata"]["component"].update(version="1.2.3"))
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "metadata.component.version" in _messages(report)


def test_broken_bom_format_is_caught(fixture_set, product_workdir):
    _rewrite_json(os.path.join(product_workdir, fixture_set.stem + ".cdx.json"),
                  lambda d: d.update(bomFormat="NotCycloneDX"))
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "bomFormat" in _messages(report)


def test_expected_version_is_asserted(fixture_set, product_workdir):
    """A directory of downloaded files has no installed package, so the
    product's version variable is the only way to check which release the
    SBOM is for."""
    report = _audit(product_workdir, fixture_set, expect_version="9.9.9")
    root = [f for f in report.findings if f.where == "root"]
    assert root, "a wrong expected version must be reported"
    assert "9.9.9" in _messages(report)
    # Reported under its own category so the failure names the real problem
    # rather than hiding inside a "document is malformed" test.
    assert all(f.where == "root" for f in root)


def test_expected_version_tolerates_a_package_release_suffix(fixture_set, product_workdir):
    """The SBOM says e.g. 9.7.1-rc1; an rpm or a job parameter may say
    9.7.1-rc1.2. Derived from each product's own version -- a PXB literal here
    would fail for PS for a reason unrelated to anything under test."""
    report = _audit(product_workdir, fixture_set,
                    expect_version=fixture_set.root_version + ".2")
    assert not [f for f in report.findings if f.where == "root"], _messages(report)


@pytest.mark.parametrize("key,variable", [("pxb", "PXB_VERSION"), ("ps", "PS_VERSION")])
def test_expected_version_is_read_from_the_environment(monkeypatch, key, variable):
    product = config.product(key)
    assert config.expect_version_env(product) == variable
    monkeypatch.delenv(variable, raising=False)
    assert config.expect_version(product) is None
    monkeypatch.setenv(variable, "9.7.1-rc1")
    assert config.expect_version(product) == "9.7.1-rc1"
    monkeypatch.setenv(variable, "   ")
    assert config.expect_version(product) is None


def test_each_product_reads_only_its_own_version_variable(monkeypatch):
    """A PS job must not pick up PXB_VERSION, or the reverse -- each suite
    already has its own spelling, and one shared name would be read by the
    wrong job."""
    monkeypatch.setenv("PXB_VERSION", "9.7.1-rc1")
    monkeypatch.delenv("PS_VERSION", raising=False)
    assert config.expect_version(config.product("pxb")) == "9.7.1-rc1"
    assert config.expect_version(config.product("ps")) is None


def test_wrong_expected_name_is_reported_under_root(fixture_set, product_workdir):
    report = _audit(product_workdir, fixture_set, expect_name="percona-xtrabackup-84")
    root = [f for f in report.findings if f.where == "root"]
    assert root, "a wrong expected name must be reported"
    assert "percona-xtrabackup-84" in _messages(report)


def test_invalid_json_is_reported_not_raised(fixture_set, product_workdir):
    with open(os.path.join(product_workdir, fixture_set.stem + ".cdx.json"), "w") as handle:
        handle.write("{ this is not json")
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "not valid JSON" in _messages(report)


def test_missing_licence_is_caught(fixture_set, product_workdir):
    _rewrite_json(os.path.join(product_workdir, fixture_set.stem + ".spdx.json"),
                  lambda d: [p.update(licenseConcluded="NOASSERTION",
                                      licenseDeclared="NOASSERTION")
                             for p in d["packages"] if p["name"] == "lz4"])
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "lz4" in _messages(report)


def test_duplicate_spdxid_is_caught(fixture_set, product_workdir):
    def mutate(doc):
        doc["packages"][2]["SPDXID"] = doc["packages"][1]["SPDXID"]
    _rewrite_json(os.path.join(product_workdir, fixture_set.stem + ".spdx.json"), mutate)
    report = _audit(product_workdir, fixture_set)
    assert not report.ok
    assert "is used by both" in _messages(report)


def test_licence_disagreement_is_caught(workdir):
    path = os.path.join(workdir, STEM + ".licenses.txt")
    text = open(path).read().replace("zlib 1.3.2 Zlib", "zlib 1.3.2 GPL-3.0-only")
    open(path, "w").write(text)
    report = _audit(workdir)
    assert not report.ok
    assert "licence disagrees" in _messages(report)


def test_sbom_dir_containing_a_space_is_searched(fixture_set, product_workdir):
    """An unquoted path split into two arguments and reported the directory as
    empty -- indistinguishable from a package that ships no SBOM."""
    spaced = tempfile.mkdtemp(prefix="pxb sbom dir ")
    try:
        for name in os.listdir(fixture_set.directory):
            shutil.copy(os.path.join(fixture_set.directory, name), os.path.join(spaced, name))
        sets, considered = discovery.discover(LocalBackend(), sbom_dir=spaced)
        assert len(sets) == 1, considered
        assert sets[0].missing() == []
    finally:
        shutil.rmtree(spaced, ignore_errors=True)


def test_sbom_dir_containing_a_quote_is_searched(fixture_set, product_workdir):
    """A path with a single quote used to break the command outright.

    The literal quotes around the interpolated value were not escaping: the
    command became `find '/tmp/a'b' ...`, which exits 2 with "unexpected EOF",
    and the non-zero status was reported as "directory is empty or unreadable"
    -- a silent false negative rather than an error.
    """
    quoted = tempfile.mkdtemp(prefix="pxb'sbom")
    try:
        for name in os.listdir(fixture_set.directory):
            shutil.copy(os.path.join(fixture_set.directory, name), os.path.join(quoted, name))
        sets, considered = discovery.discover(LocalBackend(), sbom_dir=quoted)
        assert len(sets) == 1, considered
        assert sets[0].missing() == []
    finally:
        shutil.rmtree(quoted, ignore_errors=True)


def test_sbom_dir_cannot_inject_shell_commands(workdir):
    """$SBOM_DIR reaches a shell on every target, so a crafted value must be
    treated as one literal path, never as syntax."""
    sentinel = os.path.join(workdir, "INJECTED")
    payload = "/tmp'; touch %s; echo '" % sentinel

    sets, considered = discovery.discover(LocalBackend(), sbom_dir=payload)

    assert not os.path.exists(sentinel), "the injected command executed"
    assert sets == [], considered


def test_sbom_dir_finds_files_nested_several_levels_deep(fixture_set, product_workdir):
    """An extracted archive can nest; the search depth must match the one used
    for the package-owned paths."""
    nested = os.path.join(product_workdir, "a", "b", "c")
    os.makedirs(nested)
    for name in os.listdir(fixture_set.directory):
        shutil.move(os.path.join(product_workdir, name), os.path.join(nested, name))
    sets, considered = discovery.discover(LocalBackend(), sbom_dir=product_workdir)
    assert len(sets) == 1, considered
    assert sets[0].missing() == []


def test_sibling_directories_do_not_merge_into_one_set(fixture_set, product_workdir):
    """A backup or leftover copy next to the real SBOM must stay a separate set.

    Keyed on the stem alone these merged, and the merged set could take
    CycloneDX from one directory and SPDX from the other -- so cross-format
    consistency would have compared unrelated documents and passed.
    """
    real = os.path.join(product_workdir, "sbom")
    backup = os.path.join(product_workdir, "sbom-backup")
    os.makedirs(real)
    os.makedirs(backup)
    for name in os.listdir(fixture_set.directory):
        shutil.copy(os.path.join(fixture_set.directory, name), os.path.join(real, name))
        shutil.copy(os.path.join(fixture_set.directory, name), os.path.join(backup, name))
    for name in os.listdir(product_workdir):
        path = os.path.join(product_workdir, name)
        if os.path.isfile(path):
            os.remove(path)

    sets, considered = discovery.discover(LocalBackend(), sbom_dir=product_workdir)
    assert len(sets) == 2, considered
    directories = sorted(s.directory for s in sets)
    assert directories == sorted([real, backup])
    # Every file in a set comes from that set's own directory.
    for sbom_set in sets:
        for path in sbom_set.paths.values():
            assert os.path.dirname(path) == sbom_set.directory


def test_default_search_is_limited_to_the_package_directory():
    """Both rpm and deb install PXB under /usr/share/percona-xtrabackup*/;
    searching wider picked up SBOMs belonging to other packages."""
    assert products.PXB.search_dirs == ("/usr/share/percona-xtrabackup*",)


@pytest.mark.parametrize("key", sorted(products.PRODUCTS))
def test_each_product_searches_only_its_own_directories(key):
    """No product's fallback may reach into another product's directories."""
    product = products.get(key)
    for directory in product.search_dirs:
        assert directory.startswith("/usr/share/"), directory
        for other in products.PRODUCTS.values():
            if other is not product:
                for theirs in other.search_dirs:
                    assert directory != theirs, (key, directory)


def test_empty_directory_yields_no_sets(workdir):
    empty = tempfile.mkdtemp(prefix="pxb-sbom-empty-")
    try:
        sets, considered = discovery.discover(LocalBackend(), sbom_dir=empty)
        assert sets == []
        assert considered, "discovery must always explain what it looked at"
    finally:
        shutil.rmtree(empty, ignore_errors=True)


# --- junit platform labelling ---------------------------------------------

# pytest 6+ wraps the suite in <testsuites>; pytest 5.2.1 (pinned in the docker
# suite) emits <testsuite> at the root. Both must work.
JUNIT_NESTED = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3">
<testcase classname="pytest-tests.test_pxb_sbom" name="test_cyclonedx_is_well_formed"/>
<testcase classname="tests.test_container_att.TestPxbBinaries" name="test_binary_exists[xbcloud]"/>
<testcase classname="tests.test_pxb_sbom.TestPxbSbom" name="test_no_known_vulnerabilities"/>
</testsuite></testsuites>"""

JUNIT_FLAT = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="pytest" tests="1">
<testcase classname="tests.test_pxb_sbom.TestPxbSbom" name="test_sbom_set_is_complete"/>
</testsuite>"""


def _names(path):
    import xml.etree.ElementTree as ET
    return dict((tc.get("classname"), tc.get("name"))
                for tc in ET.parse(path).getroot().iter("testcase"))


def _write(directory, name, text):
    path = os.path.join(directory, name)
    with open(path, "w") as handle:
        handle.write(text)
    return path


def test_junit_label_is_appended_to_matching_testcases(workdir):
    path = _write(workdir, "nested.xml", JUNIT_NESTED)
    assert label_junit.main([path, "--label", "ubuntu-noble",
                             "--only", "test_pxb_sbom"]) == 0
    names = _names(path)
    assert names["pytest-tests.test_pxb_sbom"] == \
        "test_cyclonedx_is_well_formed.ubuntu-noble"
    assert names["tests.test_pxb_sbom.TestPxbSbom"] == \
        "test_no_known_vulnerabilities.ubuntu-noble"


def test_junit_label_leaves_other_test_modules_alone(workdir):
    """The docker report.xml carries test_container_att.py in the same file."""
    path = _write(workdir, "nested.xml", JUNIT_NESTED)
    label_junit.main([path, "--label", "amd64", "--only", "test_pxb_sbom"])
    names = _names(path)
    assert names["tests.test_container_att.TestPxbBinaries"] == \
        "test_binary_exists[xbcloud]"


def test_junit_label_handles_the_pytest5_flat_root(workdir):
    path = _write(workdir, "flat.xml", JUNIT_FLAT)
    assert label_junit.main([path, "--label", "rhel-9",
                             "--only", "test_pxb_sbom"]) == 0
    assert list(_names(path).values()) == ["test_sbom_set_is_complete.rhel-9"]


def test_junit_label_is_idempotent(workdir):
    path = _write(workdir, "nested.xml", JUNIT_NESTED)
    for _ in range(3):
        label_junit.main([path, "--label", "debian-12", "--only", "test_pxb_sbom"])
    for name in _names(path).values():
        assert name.count(".debian-12") <= 1, name


def test_junit_label_leaves_a_malformed_report_untouched(workdir):
    """A mangled report is worse than an ambiguous one."""
    path = _write(workdir, "bad.xml", '<testsuite><testcase name="a"')
    original = open(path).read()
    assert label_junit.main([path, "--label", "x"]) == 1
    assert open(path).read() == original


def test_junit_label_on_a_missing_file_is_not_an_error(workdir):
    assert label_junit.main([os.path.join(workdir, "absent.xml"),
                             "--label", "x"]) == 0


def test_junit_label_ignores_an_empty_label(workdir):
    path = _write(workdir, "nested.xml", JUNIT_NESTED)
    original = open(path).read()
    assert label_junit.main([path, "--label", "   "]) == 0
    assert open(path).read() == original


# --- the exported copy, and cleaning it up --------------------------------

def _temp_dirs():
    """The audit's temporary copies. Reads audit.TEMP_PREFIX rather than repeating
    it: a stale literal here made every leak test below pass vacuously."""
    root = tempfile.gettempdir()
    return {d for d in os.listdir(root) if d.startswith(audit.TEMP_PREFIX)}


def test_local_backend_needs_no_temporary_copy(fixture_set, product_workdir):
    """The packaged file is on the same filesystem, so the tools read it in
    place and nothing is written to the temp dir at all."""
    before = _temp_dirs()
    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
    report = audit.audit(backend, sets[0], run_tools=True)
    assert _temp_dirs() == before, "a temporary copy was made unnecessarily"
    # and the tools still saw a real document
    assert report.tool_status["cyclonedx"] != external_tools.FAILED


def test_a_copy_is_made_and_removed_when_the_file_is_gzipped(fixture_set, product_workdir):
    """trivy and cyclonedx cannot parse .json.gz, so this path must still copy
    -- and must still clean up after itself."""
    import gzip
    source = os.path.join(product_workdir, fixture_set.stem + ".cdx.json")
    data = open(source, "rb").read()
    os.remove(source)
    with gzip.open(source + ".gz", "wb") as handle:
        handle.write(data)

    before = _temp_dirs()
    backend = LocalBackend()
    assert backend.local_path(source + ".gz") is None, "gzip must force a copy"
    sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
    report = audit.audit(backend, sets[0], run_tools=True)
    assert _temp_dirs() == before, "the temporary copy was left behind"
    assert report.tool_status["cyclonedx"] != external_tools.FAILED


def test_temp_copy_is_removed_when_export_fails(fixture_set, product_workdir):
    """The export-failure path returns early -- it must still clean up."""
    before = _temp_dirs()
    backend = LocalBackend()
    backend.local_path = lambda path: None          # force the copy branch
    def boom(path, dest_dir):
        raise IOError("simulated export failure")
    backend.export = boom

    sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
    report = audit.audit(backend, sets[0], run_tools=True)
    assert _temp_dirs() == before, "the temp dir survived an export failure"
    assert report.tool_status["cyclonedx"] == external_tools.FAILED


def test_temp_copy_is_removed_when_the_vuln_gate_is_off(fixture_set, product_workdir, monkeypatch):
    """SBOM_VULN_MODE=off returns before the trivy block -- also a cleanup path."""
    monkeypatch.setenv(config.ENV_VULN_MODE, "off")
    before = _temp_dirs()
    backend = LocalBackend()
    backend.local_path = lambda path: None          # force the copy branch
    sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
    audit.audit(backend, sets[0], run_tools=True)
    assert _temp_dirs() == before


def test_cleanup_failure_does_not_break_the_audit(fixture_set, product_workdir, monkeypatch):
    """Tidying up must never turn into a failed audit -- the reason for
    ignore_errors rather than TemporaryDirectory."""
    import shutil as _shutil
    real_rmtree = _shutil.rmtree
    before = _temp_dirs()
    backend = LocalBackend()
    backend.local_path = lambda path: None          # force the copy branch
    monkeypatch.setattr(_shutil, "rmtree",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("boom")))
    try:
        sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
        report = audit.audit(backend, sets[0], run_tools=True)
        assert report is not None
    finally:
        # This case deliberately breaks cleanup, so it orphans a directory by
        # design. Remove it with the real rmtree so the suite itself leaks
        # nothing -- which is what the rest of these tests measure.
        for leaked in _temp_dirs() - before:
            real_rmtree(os.path.join(tempfile.gettempdir(), leaked),
                        ignore_errors=True)


# --- external tool status -------------------------------------------------

def _stub(directory, name, body):
    path = os.path.join(directory, name)
    with open(path, "w") as handle:
        handle.write(body)
    os.chmod(path, 0o755)
    return path


def test_missing_tools_are_reported_as_missing_not_as_success(fixture_set, product_workdir):
    """A tool that never ran must not look like a tool that found nothing.

    Before this, an absent binary produced no findings and the corresponding
    tests passed having validated nothing.
    """
    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=product_workdir)
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


def test_tools_are_found_by_absolute_path_when_not_on_PATH(workdir):
    """The molecule play runs under sudo, and RHEL-family secure_path excludes
    /usr/local/bin where the tools are installed -- so the checks address them by
    absolute path. This pins the resolution the fix depends on."""
    stub = _stub(workdir, "trivy", "#!/bin/sh\nexit 0\n")
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = "/nonexistent-bin"
    try:
        assert external_tools.have("trivy") is False, "must not be on the stripped PATH"
        assert external_tools.have(stub) is True, "absolute path must resolve"
        assert external_tools.have("/nonexistent/trivy") is False
    finally:
        os.environ["PATH"] = old_path


def test_tool_binary_overrides_are_honoured(fixture_set, product_workdir):
    """TRIVY_BIN / CYCLONEDX_BIN are how the ansible task passes those paths in."""
    stub = _stub(product_workdir, "trivy-abs", "#!/bin/sh\nexit 0\n")
    old_bin, old_path = external_tools.TRIVY_BIN, os.environ.get("PATH", "")
    external_tools.TRIVY_BIN = stub
    os.environ["PATH"] = "/nonexistent-bin"
    try:
        result = external_tools.trivy_sbom(os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
        assert result.status == external_tools.OK, result.status
    finally:
        external_tools.TRIVY_BIN = old_bin
        os.environ["PATH"] = old_path


def test_vuln_mode_off_does_not_invoke_trivy(fixture_set, product_workdir, monkeypatch):
    """SBOM_VULN_MODE=off must prevent the scan, not merely ignore its result.

    Before this, `off` was behaviourally identical to `warn`: trivy still ran
    (pulling a ~1.4GB DB) and a missing trivy still failed the check.
    """
    sentinel = os.path.join(product_workdir, "INVOKED")
    stub = _stub(product_workdir, "trivy-sentinel",
                 "#!/bin/sh\ntouch %s\nexit 0\n" % sentinel)
    monkeypatch.setattr(external_tools, "TRIVY_BIN", stub)
    monkeypatch.setenv(config.ENV_VULN_MODE, "off")

    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=fixture_set.directory)
    report = audit.audit(backend, sets[0], run_tools=True)

    assert not os.path.exists(sentinel), "trivy was executed despite the gate being off"
    assert report.tool_status["trivy"] == external_tools.OFF
    assert not report.vuln_findings


def test_vuln_mode_warn_does_invoke_trivy(fixture_set, product_workdir, monkeypatch):
    """The control for the test above -- otherwise it could pass for the wrong
    reason, e.g. because the stub was never wired up."""
    sentinel = os.path.join(product_workdir, "INVOKED")
    stub = _stub(product_workdir, "trivy-sentinel",
                 "#!/bin/sh\ntouch %s\nexit 0\n" % sentinel)
    monkeypatch.setattr(external_tools, "TRIVY_BIN", stub)
    monkeypatch.setenv(config.ENV_VULN_MODE, "warn")

    backend = LocalBackend()
    sets, _ = discovery.discover(backend, sbom_dir=fixture_set.directory)
    report = audit.audit(backend, sets[0], run_tools=True)

    assert os.path.exists(sentinel), "trivy should have been executed"
    assert report.tool_status["trivy"] == external_tools.OK


def _unlaunchable(directory, name, kind):
    """A file shutil.which() resolves but the kernel refuses to run."""
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        if kind == "bad-elf":
            handle.write(b"\x7fELF\x00\x00\x00not-a-real-binary")   # wrong arch
        else:
            handle.write(b"#!/nonexistent/loader\necho hi\n")         # missing loader
    os.chmod(path, 0o755)
    return path


def test_unlaunchable_cyclonedx_is_failed_not_an_exception(fixture_set, product_workdir):
    """shutil.which() only checks the executable bit, so a resolved path can
    still fail to launch. That must be a FAILED status, not an escaping OSError
    that surfaces as a fixture crash naming no tool."""
    stub = _unlaunchable(product_workdir, "cyclonedx", "bad-elf")
    old = external_tools.CYCLONEDX_BIN
    external_tools.CYCLONEDX_BIN = stub
    try:
        result = external_tools.cyclonedx_validate(
            os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
    finally:
        external_tools.CYCLONEDX_BIN = old
    assert result.status == external_tools.FAILED
    assert "cannot execute" in result.output


def test_unlaunchable_trivy_is_failed_never_a_vulnerability(fixture_set, product_workdir):
    """The rc==1 branch means "vulnerabilities found", so a launch failure must
    not land there -- otherwise a broken binary reads as a phantom CVE."""
    for kind in ("bad-elf", "missing-loader"):
        stub = _unlaunchable(product_workdir, "trivy-" + kind, kind)
        old = external_tools.TRIVY_BIN
        external_tools.TRIVY_BIN = stub
        try:
            result = external_tools.trivy_sbom(
                os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
        finally:
            external_tools.TRIVY_BIN = old
        assert result.status == external_tools.FAILED, kind
        assert result.status != external_tools.FOUND, kind
        assert "cannot execute" in result.output, kind


def test_backend_run_degrades_when_the_command_cannot_launch(workdir):
    """A missing or unlaunchable docker CLI must make discovery report nothing,
    not raise -- consumers only use .ok and .lines()."""
    from sbom_checks.backends import DockerBackend
    stub = _unlaunchable(workdir, "fake-docker", "bad-elf")
    backend = DockerBackend("no-such-container", docker=stub)

    result = backend.run("echo hi")
    assert result.ok is False
    assert "cannot execute" in result.stderr

    sets, considered = discovery.discover(backend)
    assert sets == []
    assert considered, "discovery must still explain what it looked at"


def test_trivy_failure_is_not_reported_as_a_vulnerability(fixture_set, product_workdir):
    """trivy exits non-zero when it cannot run at all -- a rate-limited DB pull
    from ghcr.io, say. Treating that as a finding would be a phantom CVE."""
    stub = _stub(product_workdir, "trivy-fatal",
                 "#!/bin/sh\necho 'FATAL failed to download vulnerability DB' >&2\nexit 1\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.FAILED
    assert result.status != external_tools.FOUND


def test_trivy_findings_are_still_reported(fixture_set, product_workdir):
    """rc 1 with no fatal marker is a genuine finding and must stay one."""
    stub = _stub(product_workdir, "trivy-vuln",
                 "#!/bin/sh\necho 'zlib CVE-2023-45853 HIGH'\nexit 1\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.FOUND
    assert "CVE-2023-45853" in result.output


def test_trivy_clean_scan_is_ok(fixture_set, product_workdir):
    stub = _stub(product_workdir, "trivy-clean", "#!/bin/sh\nexit 0\n")
    old = external_tools.TRIVY_BIN
    external_tools.TRIVY_BIN = stub
    try:
        result = external_tools.trivy_sbom(os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"))
    finally:
        external_tools.TRIVY_BIN = old
    assert result.status == external_tools.OK


# --- malformed but valid JSON ---------------------------------------------

# Valid JSON of the wrong shape. Each of these used to raise out of the parser
# or the structural check and abort the whole pytest run; a document checker
# must report them instead.
MALFORMED = [
    ('{"metadata": "bad"}', "cdx"),
    ('{"metadata": {"component": "x"}}', "cdx"),
    ('{"metadata": {"component": ["a"]}}', "cdx"),
    ('{"components": "notalist"}', "cdx"),
    ('{"components": [{"name": "a", "version": "1"}, "junk"]}', "cdx"),
    ('{"components": [{"licenses": "x"}]}', "cdx"),
    ('{"components": [{"properties": "x"}]}', "cdx"),
    ('{"packages": "notalist"}', "spdx"),
    ('{"packages": ["plain"]}', "spdx"),
    ('{"packages": [{"name": "a", "SPDXID": "SPDXRef-a"}, "junk"]}', "spdx"),
    ('{"relationships": "x"}', "spdx"),
    ('{"relationships": [{"relationshipType": "DESCRIBES"}, "junk"],'
     ' "packages": [{"name": "a", "SPDXID": "SPDXRef-a"}]}', "spdx"),
    ('{"documentDescribes": {"a": 1}}', "spdx"),
    ('{"documentDescribes": "abc"}', "spdx"),
    # An SPDX document with no packages[] returns early, before the relationship
    # and documentDescribes block is ever reached -- so the cases above prove
    # less than they appear to. These carry a package so that block runs.
    ('{"packages": [{"name": "a", "SPDXID": "SPDXRef-a", "versionInfo": "1",'
     ' "licenseConcluded": "MIT"}], "documentDescribes": {"a": 1}}', "spdx"),
    ('{"packages": [{"name": "a", "SPDXID": "SPDXRef-a", "versionInfo": "1",'
     ' "licenseConcluded": "MIT"}], "documentDescribes": "abc"}', "spdx"),
    ('{"packages": [{"name": "a", "SPDXID": "SPDXRef-a", "versionInfo": "1",'
     ' "licenseConcluded": "MIT"}], "relationships": [{"relationshipType":'
     ' "DESCRIBES", "relatedSpdxElement": "SPDXRef-a"}, "junk", null]}', "spdx"),
]


@pytest.mark.parametrize("raw,kind", MALFORMED)
def test_malformed_documents_are_reported_not_raised(raw, kind):
    load = parsers.load_cyclonedx if kind == "cdx" else parsers.load_spdx
    check = structural.check_cyclonedx if kind == "cdx" else structural.check_spdx
    try:
        doc, root, components = load(raw)
    except parsers.ParseError:
        return                      # a reported parse failure is a valid outcome
    findings = check(doc, root, components)
    assert findings, "a malformed document produced no findings at all"


def _spdx_with(**extra):
    doc = {"spdxVersion": "SPDX-2.3", "SPDXID": "SPDXRef-DOCUMENT",
           "dataLicense": "CC0-1.0", "name": "pxb",
           "documentNamespace": "http://example/x",
           "packages": [{"name": "pxb", "SPDXID": "SPDXRef-pxb",
                         "versionInfo": "9.7.1", "licenseConcluded": "GPL-2.0"}]}
    doc.update(extra)
    return json.dumps(doc)


def test_non_object_relationships_are_reported_not_silently_dropped():
    """Filtering alone is not enough: a dropped relationship changes which
    packages look contained, so it has to be reported."""
    raw = _spdx_with(relationships=[
        {"relationshipType": "DESCRIBES", "spdxElementId": "SPDXRef-DOCUMENT",
         "relatedSpdxElement": "SPDXRef-pxb"}, "junk", None])
    doc, root, components = parsers.load_spdx(raw)
    messages = "\n".join(str(f) for f in
                         structural.check_spdx(doc, root, components))
    assert "relationships[1] is str, expected an object" in messages
    assert "relationships[2] is NoneType, expected an object" in messages


def test_object_documentdescribes_is_reported_not_raised():
    """structural.check_spdx keeps its own copy of the root-id lookup that
    parsers._spdx_root_id guards; indexing [0] on an object raised KeyError."""
    doc, root, components = parsers.load_spdx(_spdx_with(documentDescribes={"a": 1}))
    messages = "\n".join(str(f) for f in
                         structural.check_spdx(doc, root, components))
    assert "documentDescribes is dict, expected an array" in messages


def test_non_object_metadata_gives_a_missing_root_finding():
    """The reviewer's exact input."""
    doc, root, components = parsers.load_cyclonedx('{"metadata": "bad"}')
    assert root is None
    messages = "\n".join(str(f) for f in
                          structural.check_cyclonedx(doc, root, components))
    assert "metadata is str, expected an object" in messages
    assert "metadata.component is missing" in messages


def test_broken_metadata_does_not_discard_valid_components():
    """Normalising rather than raising ParseError means the rest of the document
    is still checked -- otherwise one bad key would hide every real finding."""
    raw = ('{"bomFormat":"CycloneDX","specVersion":"1.5","serialNumber":"urn:uuid:x",'
           '"metadata":"bad",'
           '"components":[{"name":"zlib","version":"1.3.2",'
           '"purl":"pkg:generic/zlib@1.3.2","bom-ref":"r1",'
           '"licenses":[{"license":{"id":"Zlib"}}]}]}')
    doc, root, components = parsers.load_cyclonedx(raw)
    assert [(c.name, c.version) for c in components] == [("zlib", "1.3.2")]


def test_audit_reports_rather_than_aborts_on_a_malformed_document(fixture_set, product_workdir):
    """End to end: a malformed CycloneDX file must make audit() return findings,
    not raise through the pytest fixture."""
    with open(os.path.join(product_workdir, fixture_set.stem + ".cdx.json"), "w") as handle:
        handle.write('{"metadata": "bad"}')
    report = _audit(product_workdir, fixture_set, run_tools=False)
    assert not report.ok
    assert any(f.where == "cdx" for f in report.findings)


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


def test_cyclonedx_licence_expression_form_is_read(fixture_set):
    doc, root, components = parsers.load_cyclonedx(
        open(os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json"), "rb").read())
    kmip = [c for c in components if c.name == "libkmip"][0]
    assert kmip.license == "Apache-2.0 OR BSD-3-Clause"


def test_spdx_root_package_is_excluded_from_components(fixture_set):
    doc, root, components = parsers.load_spdx(
        open(os.path.join(fixture_set.directory, fixture_set.stem + ".spdx.json"), "rb").read())
    assert root.name == fixture_set.root_name
    assert fixture_set.root_name not in [c.name for c in components]
    assert len(components) == fixture_set.components


def test_spdxid_mangling_does_not_break_matching(fixture_set):
    """unordered_dense is SPDXRef-Package-unordered-dense; matching on SPDXID
    instead of name would lose it."""
    doc, root, components = parsers.load_spdx(
        open(os.path.join(fixture_set.directory, fixture_set.stem + ".spdx.json"), "rb").read())
    assert "unordered_dense" in [c.name for c in components]


def test_gzipped_sbom_is_read_transparently(fixture_set, product_workdir):
    """Debian gzips files under /usr/share/doc."""
    import gzip
    source = os.path.join(product_workdir, fixture_set.stem + ".cdx.json")
    data = open(source, "rb").read()
    os.remove(source)
    with gzip.open(source + ".gz", "wb") as handle:
        handle.write(data)
    report = _audit(product_workdir, fixture_set)
    assert report.ok, _messages(report)


def test_licence_normalisation():
    assert licenses.equivalent("GPL-2.0", "GPL-2.0-only")
    assert licenses.equivalent("Apache-2.0 OR BSD-3-Clause", "Apache-2.0")
    assert not licenses.equivalent("Apache-2.0 OR BSD-3-Clause", "Apache-2.0",
                                   strict=True)
    assert not licenses.equivalent("MIT", "GPL-3.0-only")
    assert licenses.is_null("NOASSERTION")


def test_spec_version_is_derived_not_hardcoded(fixture_set):
    from sbom_checks import external_tools
    assert external_tools.spec_version(
        os.path.join(fixture_set.directory, fixture_set.stem + ".cdx.json")) == "v1_5"


# --- CLI enforces tool_status --------------------------------------------

def _stub_tool(directory, name, rc):
    """An executable that exits with rc, to drive a tool status."""
    path = os.path.join(directory, name)
    with open(path, "w") as handle:
        handle.write("#!/bin/sh\nexit %d\n" % rc)
    os.chmod(path, 0o755)
    return path


# (label, cyclonedx rc or None=absent, trivy rc or None=absent, vuln off,
#  no-tools, expected exit)
# rc 0 -> OK; rc 2 -> FAILED (trivy maps rc 1 to "vulnerabilities found", so a
# broken scan must exit with something else); absent -> MISSING.
CLI_TOOL_CASES = [
    ("both usable",              0,    0,    False, False, 0),
    ("cyclonedx absent",         None, 0,    False, False, 1),
    ("trivy absent",             0,    None, False, False, 1),
    ("both absent",              None, None, False, False, 1),
    ("trivy scan failed",        0,    2,    False, False, 1),
    ("trivy absent, vuln off",   0,    None, True,  False, 0),
    ("both absent, --no-tools",  None, None, False, True,  0),
]


@pytest.mark.parametrize("label,cdx_rc,trivy_rc,vuln_off,no_tools,expected",
                         CLI_TOOL_CASES)
def test_cli_exit_code_reflects_tool_status(workdir, monkeypatch, label, cdx_rc,
                                            trivy_rc, vuln_off, no_tools, expected):
    """A requested tool that never ran must not exit 0.

    The CLI used to read only report.ok and vuln_findings, so a missing
    cyclonedx-cli, a missing trivy, or a trivy scan that could not complete all
    passed silently -- a run that validated nothing looked like a clean one.
    """
    bindir = tempfile.mkdtemp(prefix="pxb-sbom-bin-")
    try:
        cdx = _stub_tool(bindir, "cdx", cdx_rc) if cdx_rc is not None else "no-such-cdx"
        trivy = _stub_tool(bindir, "trv", trivy_rc) if trivy_rc is not None else "no-such-trivy"
        monkeypatch.setattr(external_tools, "CYCLONEDX_BIN", cdx)
        monkeypatch.setattr(external_tools, "TRIVY_BIN", trivy)
        monkeypatch.setenv(config.ENV_VULN_MODE, "off" if vuln_off else "warn")
        monkeypatch.setenv(config.ENV_CHECK_MODE, "warn")

        argv = ["--mode", "dir", "--path", workdir]
        if no_tools:
            argv.append("--no-tools")
        assert check_sbom.main(argv) == expected, label
    finally:
        shutil.rmtree(bindir, ignore_errors=True)


def test_cli_does_not_blame_the_tool_when_there_is_no_cyclonedx_document(fixture_set, product_workdir, monkeypatch):
    """With no .cdx.json the tools never run, leaving cyclonedx MISSING. That
    means "did not run", not "binary absent", so it must not be reported as a
    missing tool on a host where it is installed."""
    os.remove(os.path.join(product_workdir, fixture_set.stem + ".cdx.json"))
    monkeypatch.setattr(external_tools, "CYCLONEDX_BIN", "definitely-not-installed")
    monkeypatch.setattr(external_tools, "TRIVY_BIN", "definitely-not-installed")
    monkeypatch.setenv(config.ENV_VULN_MODE, "warn")

    report = _audit(product_workdir, fixture_set, run_tools=True)
    assert check_sbom._tool_problems(report, report.sbom_set, True) == []


def test_unusable_predicate_matches_require_tool_semantics():
    """The CLI and the pytest entrypoint must agree on which statuses are a
    setup failure; OFF and FOUND never are."""
    assert external_tools.unusable(external_tools.MISSING)
    assert external_tools.unusable(external_tools.FAILED)
    assert not external_tools.unusable(external_tools.OK)
    assert not external_tools.unusable(external_tools.FOUND)
    assert not external_tools.unusable(external_tools.OFF)


# --- strict licence comparison is the default -----------------------------

def _widen_spdx_licence(path, component="zlib", value="Zlib OR Apache-2.0"):
    """Make one SPDX licence a superset of the CycloneDX one: the two still
    overlap, so only strict comparison notices."""
    _rewrite_json(path, lambda d: [p.update(licenseConcluded=value,
                                            licenseDeclared=value)
                                   for p in d["packages"]
                                   if p["name"] == component])


def test_license_strict_is_on_by_default(monkeypatch):
    """All four files come from one generator in one run, so a licence that
    differs between them is a generator bug rather than a legitimate variation.
    Overlap-only comparison passed that silently."""
    monkeypatch.delenv(config.ENV_LICENSE_STRICT, raising=False)
    assert config.license_strict() is True


@pytest.mark.parametrize("value,expected", [
    ("0", False), ("false", False), ("off", False), ("no", False),
    ("1", True), ("true", True), ("on", True),
    ("", True),          # unset-but-present, as ansible passes it
])
def test_license_strict_is_overridable(monkeypatch, value, expected):
    monkeypatch.setenv(config.ENV_LICENSE_STRICT, value)
    assert config.license_strict() is expected


def test_a_widened_licence_fails_by_default(fixture_set, product_workdir, monkeypatch):
    monkeypatch.delenv(config.ENV_LICENSE_STRICT, raising=False)
    _widen_spdx_licence(os.path.join(product_workdir, fixture_set.stem + ".spdx.json"))
    report = _audit(product_workdir, fixture_set, strict_licenses=None)
    assert not report.ok, "a licence that differs between formats must be caught"
    assert "licence disagrees" in _messages(report)


def test_a_widened_licence_passes_when_strictness_is_turned_off(fixture_set, product_workdir, monkeypatch):
    monkeypatch.setenv(config.ENV_LICENSE_STRICT, "0")
    _widen_spdx_licence(os.path.join(product_workdir, fixture_set.stem + ".spdx.json"))
    report = _audit(product_workdir, fixture_set, strict_licenses=None)
    assert report.ok, _messages(report)


def test_clean_fixtures_still_pass_under_the_strict_default(fixture_set, product_workdir, monkeypatch):
    """The prototype SBOMs must not be broken by turning strictness on."""
    monkeypatch.delenv(config.ENV_LICENSE_STRICT, raising=False)
    report = _audit(product_workdir, fixture_set, strict_licenses=None)
    assert report.ok, _messages(report)


def test_cli_no_strict_licenses_flag_overrides_the_default(workdir, monkeypatch):
    monkeypatch.delenv(config.ENV_LICENSE_STRICT, raising=False)
    _widen_spdx_licence(os.path.join(workdir, STEM + ".spdx.json"))
    base = ["--mode", "dir", "--path", workdir, "--no-tools"]
    assert check_sbom.main(base) == 1
    assert check_sbom.main(base + ["--no-strict-licenses"]) == 0
    assert check_sbom.main(base + ["--strict-licenses"]) == 1


# --- the SBOM version must actually be compared against the package ---------

class _FakeBackend(object):
    """Backend whose rpm/dpkg answers are scripted, so the version-resolution
    rule can be tested without an installed package."""

    def __init__(self, packages=None, version=None, manager="rpm"):
        self.packages = packages or []
        self.version = version
        self.manager = manager

    def run(self, command):
        from sbom_checks.backends import Result
        if command.startswith("command -v"):
            wanted = "rpm" if self.manager == "rpm" else "dpkg-query"
            ok = command.endswith(wanted)
            return Result(0 if ok else 1, "", "")
        if "-qa" in command or "-W -f='${Package}" in command:
            return Result(0, "\n".join(self.packages), "")
        if "-q --qf" in command or "-W -f='${Version}" in command:
            return Result(0, self.version or "", "")
        return Result(1, "", "")


def test_explicit_version_wins_over_the_installed_package():
    backend = _FakeBackend(packages=["percona-xtrabackup-97"], version="9.7.1")
    version, problem = discovery.version_to_assert(
        backend, "percona-xtrabackup-97", explicit="9.9.9")
    assert version == "9.9.9" and problem is None


def test_installed_version_is_used_when_no_explicit_one():
    backend = _FakeBackend(packages=["percona-xtrabackup-97"], version="9.7.1")
    version, problem = discovery.version_to_assert(backend, "percona-xtrabackup-97")
    assert version == "9.7.1" and problem is None


def test_installed_package_with_unreadable_version_is_a_problem():
    """The hole this closes: with no version, structural.check_* skips the
    comparison, so the root test passed having verified nothing."""
    backend = _FakeBackend(packages=["percona-xtrabackup-97"], version=None)
    version, problem = discovery.version_to_assert(backend, "percona-xtrabackup-97")
    assert version is None
    assert problem and "percona-xtrabackup-97" in problem


def test_no_installed_package_is_not_a_problem():
    """A directory of downloaded files has nothing to compare against, which is
    what PXB_VERSION exists for -- it must not be turned into a failure."""
    backend = _FakeBackend(packages=[], version=None)
    version, problem = discovery.version_to_assert(backend, "percona-xtrabackup-97")
    assert version is None and problem is None


def test_release_suffix_is_still_tolerated():
    """rpm reports 9.7.1-rc1-1.el9 for an SBOM saying 9.7.1-rc1; tightening the
    missing-version case must not make the normal rpm/deb versions fail."""
    assert structural._matches("9.7.1-rc1", "9.7.1-rc1-1.el9")
    assert structural._matches("9.7.1-rc1-1.el9", "9.7.1-rc1")
    assert not structural._matches("9.7.1-rc1", "9.7.2")


# --- products are selected, never assumed --------------------------------

def test_the_default_product_is_pxb(monkeypatch):
    """Nothing in the pipelines sets SBOM_PRODUCT, so the default is what keeps
    every existing job checking PXB exactly as before."""
    monkeypatch.delenv(config.ENV_PRODUCT, raising=False)
    assert config.product() is products.PXB
    monkeypatch.setenv(config.ENV_PRODUCT, "ps")
    assert config.product() is products.PS
    assert config.product("pxb") is products.PXB      # explicit beats the env


def test_an_unknown_product_is_an_error_not_a_fallback(monkeypatch):
    """Silently checking PXB when asked for something else would report
    findings that mean nothing."""
    with pytest.raises(ValueError) as excinfo:
        config.product("percona-nope")
    assert "percona-nope" in str(excinfo.value)
    monkeypatch.setenv(config.ENV_PRODUCT, "percona-nope")
    with pytest.raises(ValueError):
        config.product()


def test_every_cyclonedx_component_keeps_its_linkage_and_origin(fixture_set):
    """PXB writes pxb:linkage, PS writes percona:linkage. With "pxb:"
    hard-coded, all 25 PS components silently had empty linkage and origin --
    no error, just lost data."""
    _, _, components = parsers.load_cyclonedx(open(os.path.join(
        fixture_set.directory, fixture_set.stem + ".cdx.json"), "rb").read())
    missing = [c.name for c in components if not c.linkage or not c.origin]
    assert not missing, "linkage/origin lost for: %s" % ", ".join(missing)


def test_a_percona_prefix_is_read_for_pxb_too():
    """The PXB generator is expected to move from "pxb:" to "percona:"; the
    parser must not need changing when it does."""
    raw = json.dumps({
        "bomFormat": "CycloneDX", "specVersion": "1.5",
        "metadata": {"component": {"name": "x", "version": "1"}},
        "components": [{"name": "zlib", "version": "1.3.2", "properties": [
            {"name": "percona:linkage", "value": "static"},
            {"name": "percona:origin", "value": "vendored"}]}]})
    _, _, components = parsers.load_cyclonedx(raw)
    assert (components[0].linkage, components[0].origin) == ("static", "vendored")


def _load_entrypoint(name):
    import importlib.util
    here = os.path.join(os.path.dirname(__file__), "..", "..", "pytest-tests")
    spec = importlib.util.spec_from_file_location(name, os.path.join(here, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("entrypoint,key", [("test_pxb_sbom", "pxb"), ("test_ps_sbom", "ps")])
def test_each_package_entrypoint_binds_its_own_product(entrypoint, key):
    """Each file runs the shared checks against one product, chosen by which
    file is run -- so the junit names say which product a result is for."""
    module = _load_entrypoint(entrypoint)
    assert module.PRODUCT == key
    assert config.product(module.PRODUCT).key == key
    # the shared fixture and all nine tests arrived through the import *
    assert callable(module.sbom) and callable(module.test_no_known_vulnerabilities)


def test_the_shared_module_cannot_overwrite_an_entrypoint_product():
    """The entrypoints set PRODUCT and then `import *` the shared module. If the
    shared module exported a PRODUCT of its own, it would silently rebind every
    entrypoint to it."""
    shared = _load_entrypoint("sbom_package_checks")
    assert "PRODUCT" not in shared.__all__
    assert not hasattr(shared, "PRODUCT")
