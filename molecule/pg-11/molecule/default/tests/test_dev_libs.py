import os
import pytest

import testinfra.utils.ansible_runner

from .settings import DEB_PKG_VERSIONS


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PACKAGES = ["libecpg-compat3", "libecpg-compat3-dbgsym", "libecpg-dev-dbgsym", "libecpg-dev", "libecpg6-dbgsym",
            'libecpg6', "libpgtypes3", "libpgtypes3-dbgsym", "libpq-dev", "libpq5-dbgsym", "libpq5"]


@pytest.mark.parametrize("package", PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert pkg.version in DEB_PKG_VERSIONS
