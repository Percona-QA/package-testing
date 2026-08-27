#!/usr/bin/env python3
"""Shared pytest fixtures for the package-testing suites.

These tests are the pytest port of the old ``bats/`` tests. They run locally on
the target host (where the Percona packages are installed) and drive the system
through plain ``subprocess`` calls (see :mod:`common`), mirroring the way the
original bats ``run`` helper worked.
"""
import os

import pytest

from common import detect_connection, detect_mongo_version, detect_mysql_version


@pytest.fixture(scope="session")
def mysql_version():
    return detect_mysql_version()


@pytest.fixture(scope="session")
def mongo_version():
    return detect_mongo_version()


@pytest.fixture(scope="session")
def connection():
    return detect_connection()


@pytest.fixture(scope="session")
def ps_admin_bin():
    return os.getenv("PS_ADMIN_BIN", "/usr/bin/ps-admin")


@pytest.fixture(scope="session")
def ps_tokudb_admin_bin():
    return os.getenv("PS_TOKUDB_ADMIN_BIN", "/usr/bin/ps_tokudb_admin")
