import os
import pytest
import testinfra.utils.ansible_runner
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PACKAGES = ['percona-replication-manager']

REPL_MANAGER_VERSION = os.environ.get("REPL_MANAGER_VERSION")


@pytest.mark.parametrize("package", PACKAGES)
def test_check_package(host, package):
    pkg = host.package(package)
    assert pkg.is_installed
    assert REPL_MANAGER_VERSION in pkg.version, pkg.version


# @pytest.mark.parametrize("package", PACKAGES)
# def test_check_rpm_package(host, package):
#     dist = host.system_info.distribution
#     if dist.lower() in DEB_DISTS:
#         pytest.skip("This test only for RHEL based platforms")
#     pkg = host.package(package)
#     assert pkg.is_installed
#     assert REPL_MANAGER_VERSION in pkg.version, pkg.version