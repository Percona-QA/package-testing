import pytest
import sys

def pytest_configure(config):
    config.addinivalue_line("markers", "install:")
