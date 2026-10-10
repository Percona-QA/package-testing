#!/usr/bin/env python3
"""PS SBOM checks for a docker image.

Collected by the existing ./run.sh (pytest -v --junit-xml report.xml), so it
lands in the report the job already publishes. The checks live in
docker-image-tests/sbom_docker_checks.py, shared with the PXB suite; this file
only binds them to PS and the image under test.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

PRODUCT = "ps"

from settings import *                                           # noqa: F401,F403,E402
from sbom_docker_checks import SbomImageChecks, backend, sbom    # noqa: F401,E402


class TestPsSbom(SbomImageChecks):
    pass
