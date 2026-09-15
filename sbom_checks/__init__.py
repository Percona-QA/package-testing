"""Percona XtraBackup SBOM verification.

Validates the four files PXB ships per artifact -- CycloneDX (.cdx.json),
SPDX (.spdx.json), a fixed-width table (.sbom.txt) and a flat licence list
(.licenses.txt) -- in installed rpm/deb packages and in docker images.

Stdlib only, python 3.6 compatible: the molecule targets span centos-7 through
debian-13 on two architectures and the docker suite is pinned to pytest 5.2.1,
so a third-party dependency would be a new failure mode on every platform.

Entry points:
    sbom_checks.discovery.discover(backend)  find the SBOM files
    sbom_checks.audit.audit(backend, set)    validate one set
    sbom_checks.config                       the off/warn/enforce gate
"""

from . import audit, backends, config, consistency, discovery  # noqa: F401
from . import external_tools, licenses, models, oci, parsers, structural  # noqa: F401

__all__ = [
    "audit", "backends", "config", "consistency", "discovery",
    "external_tools", "licenses", "models", "oci", "parsers", "structural",
]
