"""Finding the SBOM files.

The final install path and filename are not fixed yet, so nothing here
hardcodes a filename, and everything product-specific -- package names, install
locations -- comes from products.py. The ladder is:

  1. $SBOM_DIR                         explicit override
  2. rpm -ql / dpkg -L                 whatever the installed package declares
  3. find in the usual doc locations   fallback if packaging puts them elsewhere

Discovery is the single point of failure for this whole feature: if it returns
nothing, every downstream check is dead code, and in the default `warn` mode
that looks exactly like "no SBOM shipped yet". So every candidate location and
every rejection is recorded in `considered` and printed even on a skip.
"""

import os
import re
import shlex

from . import config
from .models import SbomSet

# Suffix -> format key. Longest first so .cdx.json wins over .json.
SUFFIXES = (
    (".cdx.json", "cdx"),
    (".spdx.json", "spdx"),
    (".sbom.txt", "table"),
    (".licenses.txt", "licenses"),
)

# Package names, the main-package pattern and the find(1) fallback locations are
# per product (products.py). Searching only the product's own directories keeps
# the fallback from picking up unrelated SBOMs belonging to other packages.


def classify(path):
    """-> (format key, stem) or (None, None) if this is not an SBOM file."""
    name = os.path.basename(path)
    if name.endswith(".gz"):
        name = name[:-3]
    for suffix, fmt in SUFFIXES:
        if name.endswith(suffix):
            return fmt, name[:-len(suffix)]
    return None, None


def _package_manager(backend):
    if backend.run("command -v rpm").ok:
        return "rpm"
    if backend.run("command -v dpkg-query").ok:
        return "dpkg"
    return None


def _dpkg_status_lines(result):
    """-> [(status abbrev, value)] from `dpkg-query -W -f='${db:Status-Abbrev} X'`."""
    pairs = []
    for line in result.lines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            pairs.append((parts[0], parts[1].strip()))
    return pairs


def _dpkg_installed(status):
    """True for an installed package. The second letter of db:Status-Abbrev is
    the current state: "ii" and "hi" (held) are installed; "un" (never
    installed, only referenced) and "rc" (removed, config left) are not."""
    return len(status) >= 2 and status[1] == "i"


def installed_packages(backend, product=None):
    """Installed packages of the product, main ones first."""
    product = product or config.product()
    manager = _package_manager(backend)
    # package_glob is a registry constant, and its literal single quotes are
    # deliberate: they stop the *shell* from globbing so that rpm and dpkg-query
    # do the pattern matching themselves. Not a candidate for shlex.quote.
    glob = product.package_glob
    if manager == "rpm":
        result = backend.run("rpm -qa --qf '%{NAME}\\n' '" + glob + "'")
        if not result.ok:
            return []
        names = sorted(set(result.lines()))
    elif manager == "dpkg":
        # With the status, not just the name: dpkg-query -W also lists packages
        # dpkg merely knows about. PXB 9.7 names percona-xtrabackup and the older
        # lines in Conflicts/Replaces, so on Debian they all appear in state "un"
        # (not installed) -- and the first of them alphabetically,
        # percona-xtrabackup, was taken as the package the SBOM describes.
        result = backend.run(
            "dpkg-query -W -f='${db:Status-Abbrev} ${Package}\\n' '" + glob
            + "' 2>/dev/null")
        if not result.ok:
            return []
        names = sorted(set(name for status, name in _dpkg_status_lines(result)
                           if _dpkg_installed(status)))
    else:
        return []
    main = [n for n in names if product.main_package_re.match(n)]
    rest = [n for n in names if n not in main]
    return main + rest


def _list_package_files(backend, package):
    manager = _package_manager(backend)
    if manager == "rpm":
        result = backend.run("rpm -ql %s" % shlex.quote(package))
    elif manager == "dpkg":
        result = backend.run("dpkg -L %s" % shlex.quote(package))
    else:
        return []
    return result.lines() if result.ok else []


def _find_in_dirs(backend, dirs):
    # dirs are a product's search_dirs registry constants and are deliberately
    # NOT shell-escaped: they contain globs (/usr/share/percona-xtrabackup*) that
    # the shell has to expand. They take no external input, so the injection
    # concern that applies to $SBOM_DIR does not reach here.
    patterns = " -o ".join(
        "-name '*%s' -o -name '*%s.gz'" % (suffix, suffix) for suffix, _ in SUFFIXES)
    # "exit 0" matters: the loop's status is that of the last [ -d ] test, which
    # is false whenever the last directory does not exist -- which discarded the
    # output of a search that had in fact succeeded.
    command = (
        "for d in %s; do [ -d \"$d\" ] && find \"$d\" -maxdepth 4 -type f \\( %s \\) "
        "2>/dev/null; done; exit 0" % (" ".join(dirs), patterns)
    )
    return backend.run(command).lines()


def group(paths, owners=None):
    """Group SBOM file paths into SbomSets keyed by (directory, filename stem).

    Keying on the stem alone would merge sibling directories that hold the same
    filenames -- a stale or backup copy next to the real one -- and the merged
    set could take CycloneDX from one directory and SPDX from the other, so the
    cross-format consistency check would compare unrelated documents.
    """
    sets = {}
    for path in paths:
        fmt, stem = classify(path)
        if not fmt:
            continue
        key = (os.path.dirname(path), stem)
        if key not in sets:
            sets[key] = SbomSet(stem, directory=key[0],
                                package=(owners or {}).get(path))
        # First hit wins; discovery yields package-declared paths before find(1).
        if not sets[key].paths.get(fmt):
            sets[key].paths[fmt] = path
    return [sets[key] for key in sorted(sets)]


def discover(backend, sbom_dir=None, product=None):
    """-> (list of SbomSet, list of human-readable notes about what was searched)"""
    product = product or config.product()
    considered = []

    if sbom_dir:
        considered.append("$SBOM_DIR override: %s" % sbom_dir)
        # shlex.quote, not literal quotes: this value arrives from the
        # environment, so a path containing a quote would break the command
        # (silently, as "directory is empty") and a crafted value could inject
        # shell syntax. Depth matches the package search below, because an
        # extracted archive can nest more than a couple of levels.
        result = backend.run(
            "find %s -maxdepth 4 -type f 2>/dev/null" % shlex.quote(sbom_dir))
        paths = result.lines() if result.ok else []
        if not paths:
            considered.append("  -> directory is empty or unreadable")
        sets = group(paths)
        considered.append("  -> %d SBOM file set(s): %s"
                          % (len(sets), ", ".join(s.label() for s in sets) or "none"))
        return sets, considered

    paths = []

    packages = installed_packages(backend, product)
    if packages:
        considered.append("installed packages matching %s: %s"
                          % (product.package_glob, ", ".join(packages)))
    else:
        considered.append("no installed package matches %s (or no rpm/dpkg available)"
                          % product.package_glob)

    owners = {}
    for package in packages:
        files = _list_package_files(backend, package)
        hits = [p for p in files if classify(p)[0]]
        considered.append("  %s: %d file(s) declared, %d look like SBOM files"
                          % (package, len(files), len(hits)))
        paths.extend(hits)
        for path in hits:
            owners.setdefault(path, package)

    if not paths:
        considered.append("falling back to find(1) in: %s"
                          % ", ".join(product.search_dirs))
        hits = _find_in_dirs(backend, product.search_dirs)
        considered.append("  -> %d candidate file(s)" % len(hits))
        paths.extend(hits)

    sets = group(paths, owners)
    considered.append("grouped into %d SBOM file set(s): %s"
                      % (len(sets), ", ".join(s.label() for s in sets) or "none"))
    return sets, considered


def expected_root_name(backend, sbom_set, product=None):
    """Best guess at the name the SBOM's root component should carry.

    The package whose file list declared the SBOM files, when that is a main
    package: it is what the SBOM describes, and it stays right when more than
    one product line is installed. Taking the first main package instead picked
    a merely-referenced "percona-xtrabackup" on Debian. Then any installed main
    package, then the filename stem, which is how the prototype sets are named
    (percona-xtrabackup-97.cdx.json -> percona-xtrabackup-97).
    """
    product = product or config.product()
    if sbom_set.package and product.main_package_re.match(sbom_set.package):
        return sbom_set.package
    for package in installed_packages(backend, product):
        if product.main_package_re.match(package):
            return package
    return sbom_set.stem


def version_to_assert(backend, package, explicit=None, product=None):
    """-> (version, problem) -- the version the SBOM root component must carry.

    `problem` is a message, set when a package of the product IS installed
    but its version could not be read. That case has to be reported: with no
    version, structural.check_* skips the comparison entirely
    ("if expect_version and not _matches(...)"), producing no finding, so the
    root test asserts against an empty list and passes having verified nothing
    -- indistinguishable from a real pass.

    Gated on installed_packages() rather than on $SBOM_DIR so that a directory
    of downloaded files, where no package is installed and there is genuinely
    nothing to compare against, is still allowed to pass.
    """
    product = product or config.product()
    if explicit:
        return explicit, None
    version = installed_version(backend, package)
    if version:
        return version, None
    if installed_packages(backend, product):
        return None, (
            "a %s package is installed but its version could not be read, so the "
            "SBOM root version was not checked against it. Expected the version "
            "of %r from rpm/dpkg." % (product.package_glob, package))
    return None, None


# A pre-release tag in an rpm RELEASE: the "rc1" of 2.rc1.el9.
_RPM_PRERELEASE = re.compile(r"^(rc|alpha|beta)\d*$", re.IGNORECASE)


def rpm_product_version(version, release):
    """rpm VERSION plus the part of RELEASE the SBOM root carries.

    RELEASE holds either a pre-release tag or the Percona release:
      percona-xtrabackup-97-9.7.1-2.rc1.el9  (RELEASE 2.rc1.el9) -> 9.7.1-rc1
        the 2 is a rebuild number; the tag is what the SBOM says
      percona-server-server-9.7.2-2.1.el9     (RELEASE 2.1.el9)  -> 9.7.2-2
        the first part is the Percona release, the .1 a rebuild
    With no RELEASE the version is VERSION alone.
    """
    version = (version or "").strip()
    parts = [p for p in (release or "").strip().split(".") if p]
    for part in parts:
        if _RPM_PRERELEASE.match(part):
            return "%s-%s" % (version, part)
    if parts:
        return "%s-%s" % (version, parts[0])
    return version


def installed_version(backend, package):
    """Version of an installed package as its SBOM states it, or None.

    dpkg: the full Version, unchanged (9.7.1~rc1-2.trixie) -- the Debian and
    Ubuntu SBOMs carry exactly that. rpm: see rpm_product_version.
    """
    manager = _package_manager(backend)
    if manager == "rpm":
        # Concatenated, not %-formatted: "%{VERSION}" would break str.__mod__.
        result = backend.run("rpm -q --qf '%{VERSION} %{RELEASE}' " + shlex.quote(package))
        if not result.ok or not result.stdout.strip():
            return None
        fields = result.stdout.split()
        return rpm_product_version(fields[0], fields[1] if len(fields) > 1 else "")
    elif manager == "dpkg":
        # With the status: for a package in state "un" dpkg-query prints an
        # empty version and still exits 0.
        result = backend.run(
            "dpkg-query -W -f='${db:Status-Abbrev} ${Version}\\n' "
            + shlex.quote(package) + " 2>/dev/null")
        if not result.ok:
            return None
        for status, version in _dpkg_status_lines(result):
            if _dpkg_installed(status) and version:
                return version
        return None
    return None
