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


# Tool outcomes. FAILED exists because a tool that could not run must never be
# reported as a tool that found something.
OK = "ok"
MISSING = "missing"
FAILED = "failed"
FOUND = "found"          # ran cleanly and reported findings (trivy only)
OFF = "off"              # the gate says do not run this tool; absence is not a
                         # failure, so callers skip rather than requiring it


class ToolResult(object):
    def __init__(self, status, output=""):
        self.status = status
        self.output = output

    @property
    def available(self):
        return self.status != MISSING

    @property
    def ok(self):
        return self.status == OK

    def __repr__(self):
        return "ToolResult(status=%r)" % (self.status,)


UNAVAILABLE = ToolResult(MISSING, "")

# Markers that mean trivy could not do its job, rather than that it found
# vulnerabilities. The vulnerability DB is a ~60MB anonymous pull from ghcr.io
# at scan time, so on a wide parallel matrix rate-limiting is expected.
TRIVY_FATAL_MARKERS = (
    "FATAL",
    "failed to download",
    "TOOMANYREQUESTS",
    "toomanyrequests",
    "rate limit",
    "connection refused",
    "context deadline exceeded",
    "unable to initialize",
)


def have(binary):
    return shutil.which(binary) is not None if hasattr(shutil, "which") else False


def _run(argv, env=None):
    merged = dict(os.environ)
    if env:
        merged.update(env)
    try:
        process = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=merged)
        out, err = process.communicate()
    except OSError as exc:
        # shutil.which() only checks the executable bit, so a resolved path can
        # still fail to launch: a wrong-architecture binary (Exec format error)
        # or a missing dynamic loader. Report a failed run instead of letting
        # the OSError escape -- FAILED exists precisely for "installed but
        # unusable", and an escaping error surfaces as a fixture crash with no
        # indication of which tool was at fault.
        #
        # 127 is the shell's "command not found" code, chosen so this maps to
        # FAILED in both wrappers: trivy_sbom treats rc 1 as "vulnerabilities
        # found", so a launch failure must never land on that branch.
        return (127, "", "cannot execute %s: %s" % (argv[0], exc))
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
    return ToolResult(OK if rc == 0 else FAILED, (out + err).strip())


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
    output = (out + err).strip()
    if rc == 0:
        return ToolResult(OK, output)
    # --exit-code 1 means "vulnerabilities found", but trivy also exits non-zero
    # when it simply could not run. Only treat rc 1 with no fatal marker as a
    # real finding; everything else is a failed scan, which callers skip.
    if rc == 1 and not any(m in output for m in TRIVY_FATAL_MARKERS):
        return ToolResult(FOUND, output)
    return ToolResult(FAILED, output)
