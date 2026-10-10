"""Collect a target's SBOM files for checking elsewhere.

    python3 -m sbom_checks.collect --product pxb --label rocky-8 --out /var/tmp/pxb_sbom

In the molecule jobs the checks no longer run on the targets. Each target only
does what genuinely needs the installed system:

  * discovery -- which files the package declares (rpm -ql / dpkg -L, with the
    find(1) fallback), exactly as the checks themselves would find them;
  * the installed package's name and version, for the root-component check.

It copies the discovered files, byte for byte and .gz included, under
<out>/files/ with their absolute paths preserved, and writes <out>/manifest.json.
The Jenkins agent then runs the whole suite -- structure, consistency, licences,
cyclonedx-cli and trivy -- once per platform over what arrived
(pytest-tests/sbom_package_checks.py, fetched mode).

Running the tools on every target is what caused most of this suite's operational
trouble: a missing tar on some AMIs, sudo secure_path, wrong-architecture
binaries, a .NET binary needing ICU, and a 1.4 GB vulnerability DB per target.
None of that exists on the agent.

A manifest is written even when nothing is found, and even when discovery
fails. Absence is then an explicit statement from the platform, and the agent
can tell "no SBOM shipped" from "this platform never reported".

Stdlib only and python 3.6 compatible, like the rest of the library: this runs
on every target in the matrix.
"""

import argparse
import json
import os
import shutil
import sys
import zipfile

from . import config, discovery
from .backends import LocalBackend

MANIFEST = "manifest.json"
FILES_DIR = "files"
SCHEMA = 1


def _copy_into(out, path):
    """Copy an absolute path to out/files/<path>, returning the relative location."""
    absolute = os.path.abspath(path)
    relative = os.path.join(FILES_DIR, absolute.lstrip(os.sep))
    dest = os.path.join(out, relative)
    if not os.path.isdir(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    shutil.copy2(absolute, dest)
    return relative


def collect(product, label, out, sbom_dir=None, backend=None):
    """-> manifest dict. Writes the files and the manifest under out."""
    backend = backend or LocalBackend()
    manifest = {
        "schema": SCHEMA,
        "product": product.key,
        "label": label,
        "considered": [],
        "sets": [],
        "expect_name": None,
        "expect_version": None,
        "version_problem": None,
        "error": None,
    }
    try:
        sets, considered = discovery.discover(backend, sbom_dir=sbom_dir, product=product)
        manifest["considered"] = considered
        for sbom_set in sets:
            files = {}
            for fmt in sbom_set.FORMATS:
                path = sbom_set.paths.get(fmt)
                if path:
                    files[fmt] = _copy_into(out, path)
            manifest["sets"].append({
                "stem": sbom_set.stem,
                "directory": sbom_set.directory,
                "package": sbom_set.package,
                "files": files,
            })
        if sets:
            # Read here because it needs the installed package: the agent has
            # none, so this is the only place the expectation can come from.
            package = discovery.expected_root_name(backend, sets[0], product)
            version, problem = discovery.version_to_assert(backend, package, product=product)
            manifest["expect_name"] = package
            manifest["expect_version"] = version
            manifest["version_problem"] = problem
    except Exception as exc:                               # noqa: BLE001
        # Recorded, not raised: the manifest must still be written, so the agent
        # reports this platform's failure by name instead of as a missing file.
        manifest["error"] = "%s: %s" % (type(exc).__name__, exc)

    with open(os.path.join(out, MANIFEST), "w") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    return manifest


def read_zip_manifest(path):
    """The manifest inside a zip of a collection -> (member name, dict), or None.

    None when the file is not a readable zip, holds no manifest or more than
    one, or the manifest is not JSON. Shared by the agent-side checks and the
    artifact export, so both agree on what a collection zip is.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if os.path.basename(n) == MANIFEST]
            if len(names) != 1:
                return None
            return names[0], json.loads(archive.read(names[0]).decode("utf-8"))
    except (zipfile.BadZipFile, ValueError, IOError, OSError, KeyError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="collect", description="Collect a target's SBOM files for checking elsewhere.")
    parser.add_argument("--product", help="pxb or ps (default: $%s, else %s)"
                        % (config.ENV_PRODUCT, "pxb"))
    parser.add_argument("--label", required=True,
                        help="platform label, e.g. the molecule scenario name")
    parser.add_argument("--out", required=True, help="output directory; replaced if present")
    args = parser.parse_args(argv)

    product = config.product(args.product)
    # Replace, never merge: a surviving directory from an earlier run on a
    # reused host would otherwise ship stale files under this run's label.
    if os.path.exists(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out)

    manifest = collect(product, args.label, args.out, sbom_dir=config.sbom_dir())

    print("%s SBOM collection for %s:" % (product.display_name, args.label))
    for note in manifest["considered"]:
        print("  %s" % note)
    for sbom_set in manifest["sets"]:
        print("  collected %s from %s (owned by %s): %s"
              % (sbom_set["stem"], sbom_set["directory"],
                 sbom_set.get("package") or "no package", ", ".join(sorted(sbom_set["files"]))))
    if manifest["expect_name"]:
        print("  installed package: %s %s" % (manifest["expect_name"],
                                            manifest["expect_version"] or "(version unknown)"))
    if manifest["error"]:
        print("  ERROR: %s" % manifest["error"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
