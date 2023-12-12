import pytest
import sys

def pytest_configure(config):
    config.addinivalue_line("markers", "install:")
    config.addinivalue_line("markers", "orch_source:")
    config.addinivalue_line("markers", "pkg_source:")
    config.addinivalue_line("markers", "telemetry_enabled:")
    config.addinivalue_line("markers", "telemetry_disabled:")
