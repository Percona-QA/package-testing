"""trivy and cyclonedx-cli wrappers.

Both are optional. Every tool-backed check reports "unavailable" rather than
failing when its binary is missing -- that is what lets the same test file run
on a bare molecule target and in a fully provisioned Jenkins stage.
"""

import json
import os
import shutil
import subprocess

CYCLONEDX_BIN = os.environ.get("CYCLONEDX_BIN", "cyclonedx")
TRIVY_BIN = os.environ.get("TRIVY_BIN", "trivy")


class ToolResult(object):
    def __init__(self, available, ok, output=""):
        self.available = available
        self.ok = ok
        self.output = output

    def __repr__(self):
        return "ToolResult(available=%r, ok=%r)" % (self.available, self.ok)


UNAVAILABLE = ToolResult(False, True, "")


def have(binary):
    return shutil.which(binary) is not None if hasattr(shutil, "which") else False


def _run(argv, env=None):
    merged = dict(os.environ)
    if env:
        merged.update(env)
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=merged)
    out, err = process.communicate()
    return (process.returncode,
            out.decode("utf-8", "replace"),
            err.decode("utf-8", "replace"))


def spec_version(path):
    """CycloneDX spec version of a document, as a cyclonedx-cli --input-version.

    Derived from the file rather than hardcoded: the PXB prototype is 1.5 while
    the PBM/PCSM tests pin v1_6, and pinning would fail every PXB run.
    """
    try:
        with open(path, "rb") as handle:
            doc = json.loads(handle.read().decode("utf-8", "replace"))
    except (ValueError, IOError):
        return None
    version = doc.get("specVersion")
    if not version:
        return None
    return "v" + str(version).replace(".", "_")


def cyclonedx_validate(path):
    """Validate a CycloneDX document against its own declared spec version."""
    if not have(CYCLONEDX_BIN):
        return UNAVAILABLE
    version = spec_version(path)
    argv = [CYCLONEDX_BIN, "validate", "--input-file", path, "--input-format", "json"]
    if version:
        argv += ["--input-version", version]
    rc, out, err = _run(argv, {"DOTNET_SYSTEM_GLOBALIZATION_INVARIANT": "1"})
    return ToolResult(True, rc == 0, (out + err).strip())


def trivy_sbom(path, severity="HIGH,CRITICAL"):
    """Vulnerability scan of an SBOM document.

    Gated separately from structural validation (SBOM_VULN_MODE): a new upstream
    CVE in a vendored library is a different signal from a malformed SBOM, and
    sharing one red light means people learn to ignore both.
    """
    if not have(TRIVY_BIN):
        return UNAVAILABLE
    rc, out, err = _run([
        TRIVY_BIN, "sbom", "--severity", severity, "--ignore-unfixed",
        "--exit-code", "1", path,
    ])
    return ToolResult(True, rc == 0, (out + err).strip())
