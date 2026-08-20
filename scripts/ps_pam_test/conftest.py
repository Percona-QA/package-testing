#!/usr/bin/env python3
"""pytest fixtures for the PAM tests."""
import pytest

from pam_common import detect_connection


@pytest.fixture(scope="session")
def connection():
    return detect_connection()
