import os
import testinfra.utils.ansible_runner
from .settings import *
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

VERSION = os.getenv("PROXYSQL_VERSION")
REPO = os.environ.get("REPO")

def test_package_is_installed(host):
    pkg = host.package('proxysql2')
    assert pkg.is_installed


def test_proxysql2_version(host):
    cmd = 'proxysql --version'
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert VERSION in result.stdout, result.stdout

@pytest.mark.install
def test_sources_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison proxysql2 | grep Source | grep \"{}\"".format(VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert VERSION in result.stdout, result.stdout
