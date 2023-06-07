import os
import pytest
import testinfra.utils.ansible_runner
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


PACKAGES = ['percona-orchestrator-cli', 'percona-orchestrator-client', 'percona-orchestrator']

VERSION = os.getenv("ORCHESTRATOR_VERSION")
REVISION = os.getenv('ORCHESTRATOR_REVISION')

@pytest.mark.parametrize("package", PACKAGES)
def test_check_package(host, package):
    pkg = host.package(package)
    dist = host.system_info.distribution
    assert pkg.is_installed
    if dist.lower() in RHEL_DISTS:
        assert VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
    else:
        assert VERSION in pkg.version, pkg.version

def test_orchestrator_version(host):
    cmd = 'orchestrator --version'
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        cmd = "/usr/local/orchestrator/orchestrator --version"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert VERSION in result.stdout, result.stderr
    if REVISION:
        assert REVISION in result.stdout, result.stderr


def test_orchestrator_client(host):
    cmd = 'orchestrator-client --help h'
    result = host.run(cmd)
    assert result.rc == 0, result.stderr

@pytest.mark.install
def test_sources_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison percona-orchestrator | grep Source | grep \"{}\"".format(VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert VERSION in result.stdout, result.stdout
