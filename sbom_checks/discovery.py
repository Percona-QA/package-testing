"""Finding the SBOM files.

The final install path and filename are not fixed yet -- PXB packaging ships
only LICENSE and manpages today -- so nothing here hardcodes a filename. The
ladder is:

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

from .models import SbomSet

# Suffix -> format key. Longest first so .cdx.json wins over .json.
SUFFIXES = (
    (".cdx.json", "cdx"),
    (".spdx.json", "spdx"),
    (".sbom.txt", "table"),
    (".licenses.txt", "licenses"),
)

# Both rpm and deb install the SBOM files under the package's own directory,
# e.g. /usr/share/percona-xtrabackup-97/sbom/. Searching only there keeps the
# fallback from picking up unrelated SBOMs belonging to other packages.
SEARCH_DIRS = (
    "/usr/share/percona-xtrabackup*",
)

PACKAGE_GLOB = "percona-xtrabackup*"

# The main package, not -test-, -dbg or -debuginfo subpackages.
MAIN_PACKAGE_RE = re.compile(r"^percona-xtrabackup(-pro)?(-\d+)?$")


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


def installed_packages(backend):
    """Installed percona-xtrabackup packages, main ones first."""
    manager = _package_manager(backend)
    if manager == "rpm":
        result = backend.run("rpm -qa --qf '%{NAME}\\n' '" + PACKAGE_GLOB + "'")
    elif manager == "dpkg":
        result = backend.run(
            "dpkg-query -W -f='${Package}\\n' '" + PACKAGE_GLOB + "' 2>/dev/null")
    else:
        return []
    if not result.ok:
        return []
    names = sorted(set(result.lines()))
    main = [n for n in names if MAIN_PACKAGE_RE.match(n)]
    rest = [n for n in names if n not in main]
    return main + rest


def _list_package_files(backend, package):
    manager = _package_manager(backend)
    if manager == "rpm":
        result = backend.run("rpm -ql %s" % package)
    elif manager == "dpkg":
        result = backend.run("dpkg -L %s" % package)
    else:
        return []
    return result.lines() if result.ok else []


def _find_in_dirs(backend, dirs):
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


def group(paths):
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
            sets[key] = SbomSet(stem, directory=key[0])
        # First hit wins; discovery yields package-declared paths before find(1).
        if not sets[key].paths.get(fmt):
            sets[key].paths[fmt] = path
    return [sets[key] for key in sorted(sets)]


def discover(backend, sbom_dir=None):
    """-> (list of SbomSet, list of human-readable notes about what was searched)"""
    considered = []

    if sbom_dir:
        considered.append("$SBOM_DIR override: %s" % sbom_dir)
        # Quoted, and the same depth as the package search below: an unquoted
        # path breaks on a space, and an extracted archive can nest deeper than
        # a couple of levels. Both failed as "directory is empty or unreadable".
        result = backend.run(
            "find '%s' -maxdepth 4 -type f 2>/dev/null" % sbom_dir)
        paths = result.lines() if result.ok else []
        if not paths:
            considered.append("  -> directory is empty or unreadable")
        sets = group(paths)
        considered.append("  -> %d SBOM file set(s): %s"
                          % (len(sets), ", ".join(s.label() for s in sets) or "none"))
        return sets, considered

    paths = []

    packages = installed_packages(backend)
    if packages:
        considered.append("installed packages matching %s: %s"
                          % (PACKAGE_GLOB, ", ".join(packages)))
    else:
        considered.append("no installed package matches %s (or no rpm/dpkg available)"
                          % PACKAGE_GLOB)

    for package in packages:
        files = _list_package_files(backend, package)
        hits = [p for p in files if classify(p)[0]]
        considered.append("  %s: %d file(s) declared, %d look like SBOM files"
                          % (package, len(files), len(hits)))
        paths.extend(hits)

    if not paths:
        considered.append("falling back to find(1) in: %s" % ", ".join(SEARCH_DIRS))
        hits = _find_in_dirs(backend, SEARCH_DIRS)
        considered.append("  -> %d candidate file(s)" % len(hits))
        paths.extend(hits)

    sets = group(paths)
    considered.append("grouped into %d SBOM file set(s): %s"
                      % (len(sets), ", ".join(s.label() for s in sets) or "none"))
    return sets, considered


def expected_root_name(backend, sbom_set):
    """Best guess at the name the SBOM's root component should carry.

    Prefers the installed package that owns the files; falls back to the
    filename stem, which is how the prototype set is named
    (percona-xtrabackup-97.cdx.json -> percona-xtrabackup-97).
    """
    for package in installed_packages(backend):
        if MAIN_PACKAGE_RE.match(package):
            return package
    return sbom_set.stem


def installed_version(backend, package):
    """Version of an installed package, or None."""
    manager = _package_manager(backend)
    if manager == "rpm":
        # Concatenated, not %-formatted: "%{VERSION}" would break str.__mod__.
        result = backend.run("rpm -q --qf '%{VERSION}' " + package)
    elif manager == "dpkg":
        result = backend.run(
            "dpkg-query -W -f='${Version}' " + package + " 2>/dev/null")
    else:
        return None
    if not result.ok or not result.stdout.strip():
        return None
    return result.stdout.strip()
