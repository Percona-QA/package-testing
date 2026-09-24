#!/usr/bin/env python3
"""PS SBOM checks for an installed rpm/deb package.

Not wired into any pipeline yet -- every job invokes pytest-tests files by
explicit path, so this file is inert until a PS job names it. Meanwhile it runs
by hand against a directory of files:

    SBOM_DIR=sbom_checks/testdata/ps PS_VERSION=9.7.2-2 \\
        python3 -m pytest -v pytest-tests/test_ps_sbom.py

The checks live in sbom_package_checks.py, shared with test_pxb_sbom.py; this
file only binds them to PS.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCT = "ps"

from sbom_package_checks import *  # noqa: E402,F401,F403
