#!/usr/bin/env python3
"""PXB SBOM checks for an installed rpm/deb package.

In the molecule job this runs ON THE JENKINS AGENT, once per platform, over
the collections each target fetched back (tasks/check_pxb_sbom.yml runs only
sbom_checks.collect on the targets):

    SBOM_FETCHED='*_sbom.zip' SBOM_EXPECTED_PLATFORMS=rocky-8,... \
        python -m pytest -v pytest-tests/test_pxb_sbom.py

It also runs directly on a host with the package installed, or against a
directory of files with SBOM_DIR. The checks live in sbom_package_checks.py,
shared with test_ps_sbom.py; this file only binds them to PXB, and the job runs
it by this path.
"""

import os
import sys

# Explicitly, rather than relying on pytest's rootdir import mode to put this
# directory on sys.path -- that differs across the pytest versions on the
# targets (7.0.1 on the python 3.6 ones) and with --import-mode=importlib.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCT = "pxb"

from sbom_package_checks import *  # noqa: E402,F401,F403
