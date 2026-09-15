"""OCI-attached SBOM checks for docker images.

An SBOM can be attached to an image in the registry as an OCI referrer rather
than shipped inside the filesystem. percona-docker publishes no referrers today,
so this is off unless SBOM_CHECK_OCI is set.

Referrers attach per manifest digest, so a multi-arch image can legitimately
carry one for linux/amd64 and not for linux/arm64. The caller resolves the
digest for the architecture it is running on.
"""

import json
import os

from .backends import DOCKER_BIN
from .external_tools import have, _run

ORAS_BIN = os.environ.get("ORAS_BIN", "oras")
CYCLONEDX_ARTIFACT_TYPE = "application/vnd.cyclonedx+json"


def manifest_digest(image, architecture="amd64"):
    """Resolve the per-arch manifest digest from a multi-arch image index.

    Returns (digest, error). A single-arch image has no manifests[] -- that is
    not an error, it just means the image reference is already per-arch.
    """
    rc, out, err = _run([DOCKER_BIN, "manifest", "inspect", image])
    if rc != 0:
        return None, "docker manifest inspect failed: %s" % err.strip()
    try:
        doc = json.loads(out)
    except ValueError as exc:
        return None, "docker manifest inspect returned non-JSON: %s" % exc

    manifests = doc.get("manifests")
    if not manifests:
        return None, None
    for entry in manifests:
        platform = entry.get("platform") or {}
        if platform.get("architecture") == architecture:
            return entry.get("digest"), None
    return None, ("no %s manifest in the image index (found: %s)" % (
        architecture,
        ", ".join(sorted(set((m.get("platform") or {}).get("architecture", "?")
                            for m in manifests)))))


def discover_referrers(reference):
    """CycloneDX SBOM referrers attached to an image reference."""
    if not have(ORAS_BIN):
        return None, "oras is not installed"
    rc, out, err = _run([ORAS_BIN, "discover", "--format", "json", reference])
    if rc != 0:
        return None, "oras discover failed: %s" % err.strip()
    try:
        doc = json.loads(out)
    except ValueError as exc:
        return None, "oras discover returned non-JSON: %s" % exc
    entries = doc.get("manifests", doc.get("referrers", [])) or []
    return [e for e in entries
            if e.get("artifactType") == CYCLONEDX_ARTIFACT_TYPE], None


def pull_referrer(image_base, digest, dest_dir):
    """Pull an SBOM referrer into dest_dir. Returns (list of files, error)."""
    if not have(ORAS_BIN):
        return [], "oras is not installed"
    rc, out, err = _run([ORAS_BIN, "pull", "--output", dest_dir,
                         "%s@%s" % (image_base, digest)])
    if rc != 0:
        return [], "oras pull failed: %s" % err.strip()
    files = [os.path.join(dest_dir, f) for f in sorted(os.listdir(dest_dir))
             if f.endswith(".cdx.json") or f.endswith(".json")]
    return files, None
