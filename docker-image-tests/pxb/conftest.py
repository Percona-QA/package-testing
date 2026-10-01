#!/usr/bin/env python3
"""Put the package-testing repo root on sys.path so `import sbom_checks` works.

pytest already adds this job directory (because tests/__init__.py exists), which
is what makes `from settings import *` resolve, but it never adds the repo root.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))
