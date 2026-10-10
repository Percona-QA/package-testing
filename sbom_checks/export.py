"""Unpack fetched SBOM collections into per-platform folders, for build artifacts.

    python -m sbom_checks.export --fetched '*_sbom.zip' --out sbom

Each target's collection (sbom_checks.collect) arrives on the Jenkins agent as
<host>_<os>_<arch>_sbom.zip. As artifacts those are named after an EC2 hostname
and have to be downloaded and unzipped before anything can be read. This writes
them out as

    sbom/<platform label>/manifest.json
    sbom/<platform label>/<each collected SBOM file>

so the files open straight from the Jenkins UI.

Only what the manifest lists is written, read from the zip by member name:
nothing is extracted, so no path from inside a zip ever becomes a write
location. An unreadable zip is reported and skipped -- the checks already fail
that platform by name, and storing the others is still worth doing.

Stdlib only, like the rest of the library.
"""

import argparse
import glob
import os
import posixpath
import re
import shutil
import sys
import zipfile

from . import collect

SUFFIX = "_sbom.zip"
_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _folder_name(label, zip_path, taken):
    """A safe, unique directory name for one platform."""
    base = os.path.basename(zip_path)
    if base.endswith(SUFFIX):
        base = base[:-len(SUFFIX)]
    name = _UNSAFE.sub("-", label or base).strip("-.") or "unnamed"
    candidate, n = name, 1
    while candidate in taken:
        n += 1
        candidate = "%s-%d" % (name, n)
    taken.add(candidate)
    return candidate


def export_one(zip_path, out, taken):
    """-> (folder name, number of SBOM files written), or None if unreadable."""
    found = collect.read_zip_manifest(zip_path)
    if found is None:
        return None
    member, manifest = found
    prefix = posixpath.dirname(member)
    folder = os.path.join(out, _folder_name(manifest.get("label"), zip_path, taken))
    os.makedirs(folder)

    written = 0
    with zipfile.ZipFile(zip_path) as archive:
        with open(os.path.join(folder, collect.MANIFEST), "wb") as handle:
            handle.write(archive.read(member))
        used = set()
        for index, sbom_set in enumerate(manifest.get("sets") or [], 1):
            files = sbom_set.get("files") or {}
            names = [posixpath.basename(rel) for rel in files.values()]
            # Flattened to basenames; a second set whose names collide with the
            # first goes into its own subfolder rather than overwriting it.
            target = folder
            if used.intersection(names):
                target = os.path.join(folder, "set-%d" % index)
                os.makedirs(target)
            else:
                used.update(names)
            for relative in sorted(files.values()):
                data = archive.read(posixpath.join(prefix, relative) if prefix else relative)
                with open(os.path.join(target, posixpath.basename(relative)), "wb") as handle:
                    handle.write(data)
                written += 1
    return os.path.basename(folder), written


def export(pattern, out):
    """-> [(zip path, (folder, count) or a reason string)]. Replaces out."""
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    taken = set()
    results = []
    for zip_path in sorted(glob.glob(pattern)):
        try:
            result = export_one(zip_path, out, taken)
        except (zipfile.BadZipFile, KeyError, IOError, OSError) as exc:
            # A member the manifest names but the zip lacks, or a truncated zip
            # that still yielded its manifest.
            result = "%s: %s" % (type(exc).__name__, exc)
        results.append((zip_path, result or "not a readable SBOM collection"))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="export", description="Unpack fetched SBOM collections into per-platform folders.")
    parser.add_argument("--fetched", required=True, help="glob of collection zips, e.g. '*_sbom.zip'")
    parser.add_argument("--out", required=True, help="output directory; replaced if present")
    args = parser.parse_args(argv)

    results = export(args.fetched, args.out)
    if not results:
        print("no SBOM collections match %s" % args.fetched)
    for zip_path, result in results:
        if not isinstance(result, tuple):
            print("WARNING: %s skipped: %s" % (zip_path, result))
        else:
            print("%s: %d files (from %s)" % (result[0], result[1], os.path.basename(zip_path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
