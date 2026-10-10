"""Self-test configuration."""


def pytest_configure(config):
    # One marker per product in testdata/. The fixture_set fixture applies them
    # to its parameters, so -m "not ps" runs PXB alone and -m ps runs only PS.
    config.addinivalue_line("markers", "pxb: runs against the PXB example SBOM files")
    config.addinivalue_line("markers", "ps: runs against the PS example SBOM files")
