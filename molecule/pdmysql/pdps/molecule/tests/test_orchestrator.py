import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


PACKAGES = ['percona-orchestrator-cli', 'percona-orchestrator-client', 'percona-orchestrator']
VERSION = os.getenv("ORCHESTRATOR_VERSION")


@pytest.mark.parametrize("package", PACKAGES)
def test_check_package(host, package):
    pkg = host.package(package)
    assert pkg.is_installed
    assert VERSION in pkg.version, pkg.version


def test_version(host):
    cmd = 'orchestrator --version'
    dist = host.system_info.distribution
    if dist.lower() in ["redhat", "centos", 'rhel', 'oracleserver','ol']:
        cmd = "/usr/local/orchestrator/orchestrator --version"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr


def test_client(host):
    cmd = 'orchestrator-client --help h'
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
