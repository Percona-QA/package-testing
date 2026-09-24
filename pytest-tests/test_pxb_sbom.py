#!/usr/bin/env python3
"""PXB SBOM checks for an installed rpm/deb package.

Runs ON THE MOLECULE TARGET HOST, the same way the other pytest-tests do:

    python3 -m pytest -v /package-testing/pytest-tests/test_pxb_sbom.py

The checks live in sbom_package_checks.py, shared with test_ps_sbom.py; this
file only binds them to PXB. Keep its name: tasks/check_pxb_sbom.yml runs it by
path, and the junit platform labelling selects its results by it
(--only test_pxb_sbom).
"""

import os
import sys

# Explicitly, rather than relying on pytest's rootdir import mode to put this
# directory on sys.path -- that differs across the pytest versions on the
# targets (7.0.1 on the python 3.6 ones) and with --import-mode=importlib.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCT = "pxb"

from sbom_package_checks import *  # noqa: E402,F401,F403
