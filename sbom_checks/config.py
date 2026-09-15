"""The gate.

PXB packages and docker images do not ship SBOM files yet, so a hard-failing
check would break two currently-green jobs on every run. The rule is:

    absence is tolerated, presence is strict.

Two independent gates, because "the SBOM is malformed" and "a vendored library
has a new CVE" are different signals and must not share one red light:

  SBOM_CHECK_MODE  structural + consistency validation
  SBOM_VULN_MODE   trivy vulnerability scan

Both are one of off / warn / enforce.

                 | files absent        | files present and bad
  ---------------+---------------------+----------------------
  off            | skip                | skip
  warn (default) | skip                | FAIL
  enforce        | FAIL                | FAIL

Every gating decision in this package goes through resolve_mode()/decide().
Nothing else calls os.getenv for gating.
"""

import os

OFF = "off"
WARN = "warn"
ENFORCE = "enforce"
MODES = (OFF, WARN, ENFORCE)

# Grep-able token so a permanently-skipping check is visible in job output
# rather than silently green forever.
NOT_SHIPPED = "SBOM-NOT-SHIPPED"

ENV_CHECK_MODE = "SBOM_CHECK_MODE"
ENV_VULN_MODE = "SBOM_VULN_MODE"
ENV_LICENSE_STRICT = "SBOM_LICENSE_STRICT"
ENV_EXTERNAL_TOOLS = "SBOM_EXTERNAL_TOOLS"
ENV_OCI = "SBOM_CHECK_OCI"
ENV_DIR = "SBOM_DIR"

# Not a gate: the version the SBOM is expected to describe. Named PXB_VERSION to
# match the rest of the PXB suite (PXB_DOCKER_ACC / PXB_VERSION / PXB_REVISION)
# rather than inventing a second spelling.
ENV_EXPECT_VERSION = "PXB_VERSION"


def _mode(name, default=WARN):
    value = (os.environ.get(name) or "").strip().lower()
    if value not in MODES:
        return default
    return value


def check_mode():
    return _mode(ENV_CHECK_MODE)


def vuln_mode():
    return _mode(ENV_VULN_MODE)


def _flag(name, default=False):
    value = (os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on", ENFORCE)


def license_strict():
    """Require identical license operand sets across formats, not just overlap."""
    return _flag(ENV_LICENSE_STRICT)


def external_tools_on_target():
    """Run trivy/cyclonedx on the molecule target host. Off by default: the
    24-platform matrix spans centos-7 through debian-13 on two architectures and
    cyclonedx-cli is a self-contained .NET binary. Deep validation belongs in the
    docker job's controlled environment."""
    return _flag(ENV_EXTERNAL_TOOLS)


def check_oci():
    """percona-docker publishes no OCI referrers today, so this is off unless
    asked for explicitly."""
    return _flag(ENV_OCI)


def sbom_dir():
    """Explicit override for the SBOM location. Escape hatch for verifying a
    pre-release package before the install path is finalised."""
    return os.environ.get(ENV_DIR) or None


def expect_version():
    """Version the SBOM root component must describe, or None.

    Needed because a directory of downloaded SBOM files has no installed package
    to compare against -- without this, a local run can check structure and
    cross-format consistency but not which release the files are for.
    """
    return (os.environ.get(ENV_EXPECT_VERSION) or "").strip() or None


SKIP_ABSENT = "skip-absent"
FAIL_ABSENT = "fail-absent"
SKIP_ALL = "skip-all"
ACTIVE = "active"


def decide(mode, found):
    """What to do given a gate mode and whether any SBOM file was found."""
    if mode == OFF:
        return SKIP_ALL
    if found:
        return ACTIVE
    return FAIL_ABSENT if mode == ENFORCE else SKIP_ABSENT


def absent_message(where, considered):
    """Skip/failure text for 'no SBOM found'. Always lists what was searched --
    otherwise a broken discovery ladder is indistinguishable from a package that
    genuinely ships no SBOM, and in warn mode that difference is invisible."""
    lines = ["%s: no SBOM files found for %s" % (NOT_SHIPPED, where)]
    if considered:
        lines.append("candidate locations considered:")
        lines.extend("  - %s" % c for c in considered)
    else:
        lines.append("(discovery produced no candidate locations at all)")
    return "\n".join(lines)
