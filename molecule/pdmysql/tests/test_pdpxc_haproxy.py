import os
import pytest
import testinfra.utils.ansible_runner
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-haproxy', 'percona-haproxy-doc', 'percona-vim-haproxy']

RPMPACKAGES = ['percona-haproxy', 'percona-haproxy-debuginfo']
HAPROXY_VERSION = os.environ.get("HAPROXY_VERSION")


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for Debian based platforms")
    if dist == "ubuntu" and release.startswith("20.04"):
        pytest.skip("Skipping on Ubuntu Focal (20.04)")
    pkg = host.package(package)
    assert pkg.is_installed
    assert HAPROXY_VERSION in pkg.version, pkg.version


@pytest.mark.parametrize("package", RPMPACKAGES)
def test_check_rpm_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert HAPROXY_VERSION in pkg.version, pkg.version
