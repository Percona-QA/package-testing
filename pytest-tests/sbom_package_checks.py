"""SBOM checks for an installed rpm/deb package, shared by every product.

Not collected on its own -- the name deliberately lacks the test_ prefix. Each
product has a thin entrypoint that binds the checks to it:

    test_pxb_sbom.py   PRODUCT = "pxb"
    test_ps_sbom.py    PRODUCT = "ps"

and does `from sbom_package_checks import *`. The fixture reads the product from
that importing module (request.module.PRODUCT), so a product is selected by
which file is run -- visible in the junit names -- rather than by an environment
variable that is easy to forget on the wrong host.

One file per product, not one for both: junit names come from the filename. One
implementation, not a copy per product: the package and docker entrypoints have
already drifted apart twice when their logic was duplicated.

Two ways to run:

  installed  discover on this host (rpm -ql / dpkg -L / find, or $SBOM_DIR) --
             for a local directory of files, or a host with the package.
  fetched    $SBOM_FETCHED is a glob of zips made by sbom_checks.collect on each
             molecule target. The sbom fixture is parametrized over them, one
             platform per zip, so every test reads test_x[<platform>]. This is
             how the molecule jobs run: targets only collect, and the whole
             suite -- cyclonedx-cli and trivy included -- runs once per platform
             on the Jenkins agent. $SBOM_EXPECTED_PLATFORMS names the platforms
             the job launched; one that never reported is a failure.

Gated by SBOM_CHECK_MODE (off/warn/enforce, default warn): absence of SBOM files
is a skip, malformed SBOM files are a failure. Packages do not ship SBOMs yet, so
the default keeps the job green while making every assertion live the moment
packaging lands.

The two tool-backed tests need trivy and cyclonedx-cli and run only when
SBOM_EXTERNAL_TOOLS is on. The molecule jobs install both on the agent; a plain
local run leaves it off, so those two tests skip.
"""

import glob
import json
import os
import shutil
import sys
import tempfile
import zipfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sbom_checks import audit, collect, config, discovery    # noqa: E402
from sbom_checks import external_tools                    # noqa: E402
from sbom_checks.backends import LocalBackend             # noqa: E402
from sbom_checks.models import Finding, SbomSet, render    # noqa: E402

# Exactly what an entrypoint's `import *` picks up: the fixture, the collection
# hook that parametrizes it in fetched mode, and the tests. Explicit, so
# importing this module can never overwrite an entrypoint's PRODUCT.
__all__ = [
    "pytest_generate_tests",
    "sbom",
    "test_every_expected_platform_reported",
    "test_sbom_set_is_complete",
    "test_root_component_is_the_expected_release",
    "test_cyclonedx_is_well_formed",
    "test_spdx_is_well_formed",
    "test_sbom_table_is_well_formed",
    "test_licenses_list_is_well_formed",
    "test_formats_agree_with_each_other",
    "test_cyclonedx_passes_schema_validation",
    "test_no_known_vulnerabilities",
]

# Deliberately not audit.TEMP_PREFIX: the self-test detects leaked audit copies
# by that prefix, and an extraction directory is not an audit copy.
FETCHED_PREFIX = "sbom-fetched-"


def _product_key(module):
    key = getattr(module, "PRODUCT", None)
    if not key:
        pytest.fail("%s does not set PRODUCT; an SBOM entrypoint must bind its "
                    "product, e.g. PRODUCT = \"pxb\"" % module.__name__)
    return key


def _product(request):
    """The product the running entrypoint is bound to."""
    return config.product(_product_key(request.module))


# --- fetched mode: collection ---------------------------------------------

def _zip_manifest(path):
    """The manifest inside a collector zip, or None if it cannot be read."""
    found = collect.read_zip_manifest(path)
    return found[1] if found else None


def _fetched_for(key, pattern):
    """-> [(zip path, platform label)] for one product, sorted by label.

    A zip whose manifest cannot be read is kept, labelled by its filename, so it
    fails visibly in the fixture instead of silently dropping out of the run.
    """
    found = []
    for path in sorted(glob.glob(pattern)):
        manifest = _zip_manifest(path)
        if manifest is None:
            found.append((path, os.path.basename(path)))
        elif manifest.get("product") == key:
            found.append((path, manifest.get("label") or os.path.basename(path)))
    return sorted(found, key=lambda item: item[1])


def pytest_generate_tests(metafunc):
    """In fetched mode, run the sbom fixture once per collected platform."""
    pattern = config.fetched_glob()
    if not pattern or "sbom" not in metafunc.fixturenames:
        return
    fetched = _fetched_for(_product_key(metafunc.module), pattern)
    metafunc.parametrize("sbom", [path for path, _ in fetched], indirect=True,
                         ids=[label for _, label in fetched], scope="module")


# --- fetched mode: one platform -------------------------------------------

def _inside(root, path):
    root = os.path.realpath(root)
    return os.path.realpath(path) == root or \
        os.path.realpath(path).startswith(root + os.sep)


def _open_fetched(path, workdir):
    """Extract a collector zip. -> (manifest, directory holding the manifest)"""
    try:
        archive = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, IOError, OSError) as exc:
        # A truncated fetch lands here; name the file rather than raise a
        # traceback that points at zipfile internals.
        pytest.fail("%s is not a readable zip (%s) -- the fetch from the target "
                    "was probably incomplete" % (path, exc))
    with archive:
        for name in archive.namelist():
            # These come from our own targets, but a path escaping the
            # extraction directory would still write anywhere on the agent.
            if not _inside(workdir, os.path.join(workdir, name)):
                pytest.fail("%s: refusing entry outside the archive: %r" % (path, name))
        archive.extractall(workdir)
    for directory, _, files in os.walk(workdir):
        if collect.MANIFEST in files:
            with open(os.path.join(directory, collect.MANIFEST)) as handle:
                return json.load(handle), directory
    pytest.fail("%s has no %s -- it was not made by sbom_checks.collect"
                % (path, collect.MANIFEST))


def _gate(sets, considered, where):
    """Apply SBOM_CHECK_MODE to whether anything was found."""
    decision = config.decide(config.check_mode(), bool(sets))
    if decision == config.SKIP_ALL:
        pytest.skip("%s=off" % config.ENV_CHECK_MODE)
    if decision == config.SKIP_ABSENT:
        pytest.skip(config.absent_message(where, considered))
    if decision == config.FAIL_ABSENT:
        pytest.fail(config.absent_message(where, considered))


def _finish(report, sets, version_problem):
    """Findings the audit itself cannot know about, then the printed report."""
    # Without a version, structural.check_* skips the comparison and reports
    # nothing, so the root test would pass having verified nothing. Record it as
    # a root finding so the failure lands on the test that promises this check.
    if version_problem:
        report.findings.append(Finding("root", version_problem))

    # Every run validates sets[0]. If discovery turned up more than one, say so
    # loudly rather than silently ignoring the rest -- two SBOM sets under the
    # package directory means a stale or leftover copy is shipped alongside the
    # real one.
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


def _audit_fetched(product, path, request):
    workdir = tempfile.mkdtemp(prefix=FETCHED_PREFIX)
    request.addfinalizer(lambda: shutil.rmtree(workdir, ignore_errors=True))
    manifest, root = _open_fetched(path, workdir)
    label = manifest.get("label") or os.path.basename(path)

    print("\n%s SBOM collected on %s (%s):"
          % (product.display_name, label, os.path.basename(path)))
    for note in manifest.get("considered") or []:
        print("  %s" % note)
    if manifest.get("error"):
        pytest.fail("collecting the SBOM on %s failed: %s" % (label, manifest["error"]))

    sets = []
    for entry in manifest.get("sets") or []:
        paths = {}
        for fmt, relative in (entry.get("files") or {}).items():
            local = os.path.join(root, relative)
            if not _inside(root, local):
                pytest.fail("%s: manifest path escapes the archive: %r" % (label, relative))
            paths[fmt] = local
        # directory is where the files were on the target, so findings and the
        # multiple-sets message name the real location, not a temp path.
        sets.append(SbomSet(entry.get("stem", ""), paths=paths,
                            directory=entry.get("directory"),
                            package=entry.get("package")))

    _gate(sets, manifest.get("considered") or [], label)

    # The name and version were read on the target, from the installed package
    # -- the agent has none. An explicit SBOM_PRODUCT_VERSION still wins.
    explicit = config.expect_version()
    version = explicit or manifest.get("expect_version")
    version_problem = None if explicit else manifest.get("version_problem")
    print("  installed package on %s: %s %s"
          % (label, manifest.get("expect_name"), version or "(version unknown)"))

    report = audit.audit(
        LocalBackend(), sets[0],
        expect_name=manifest.get("expect_name"),
        expect_version=version,
        run_tools=config.external_tools_on_target(),
    )
    return _finish(report, sets, version_problem)


# --- installed mode ---------------------------------------------------------

def _audit_installed(product):
    backend = LocalBackend()
    sets, considered = discovery.discover(
        backend, sbom_dir=config.sbom_dir(), product=product)

    # Always print the discovery trail. Without it a broken discovery ladder is
    # indistinguishable from "no SBOM shipped yet", and in warn mode that
    # difference is invisible.
    print("\n%s SBOM discovery:" % product.display_name)
    for note in considered:
        print("  %s" % note)

    _gate(sets, considered, "the installed package")

    package = discovery.expected_root_name(backend, sets[0], product)

    # An explicit version wins over the installed package: if you state an
    # expectation you mean it, and a disagreement with what is installed is
    # exactly the failure you asked for. Checking a downloaded directory has no
    # installed package at all, which is the case this exists for.
    version_env = config.ENV_PRODUCT_VERSION
    explicit = config.expect_version()
    version, version_problem = discovery.version_to_assert(
        backend, package, explicit=explicit, product=product)
    if explicit:
        print("  expected version: %s (from %s)" % (version, version_env))
    else:
        print("  installed package: %s %s"
              % (package, version or "(version unknown -- set %s to assert one)"
                 % version_env))

    report = audit.audit(
        backend, sets[0],
        expect_name=package,
        expect_version=version,
        run_tools=config.external_tools_on_target(),
    )
    return _finish(report, sets, version_problem)


@pytest.fixture(scope="module")
def sbom(request):
    """Discover and audit once per platform; every test reads the same report."""
    product = _product(request)
    fetched = getattr(request, "param", None)
    if fetched is not None:
        return _audit_fetched(product, fetched, request)
    return _audit_installed(product)


def test_every_expected_platform_reported(request):
    """Every platform the job launched sent back a collection.

    Without this, a platform whose fetch failed (the fetch task has
    ignore_errors) or whose converge died before collecting would simply be
    absent from the results -- a gap that looks exactly like a clean run.
    """
    pattern = config.fetched_glob()
    if not pattern:
        pytest.skip("not checking fetched results (%s is unset)" % config.ENV_FETCHED)
    expected = config.expected_platforms()
    if not expected:
        pytest.skip("%s is unset, so there is nothing to compare against"
                    % config.ENV_EXPECTED_PLATFORMS)
    reported = set(label for _, label in
                   _fetched_for(_product_key(request.module), pattern))
    missing = [label for label in expected if label not in reported]
    assert not missing, (
        "no SBOM collection arrived from: %s\n"
        "Each launched platform must send one, even when it finds no SBOM files; "
        "a missing one means the collect or fetch step failed on that platform."
        % ", ".join(missing))


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

    In a directory run this is only meaningful when SBOM_PRODUCT_VERSION is
    set -- there is no installed package to compare against.
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
