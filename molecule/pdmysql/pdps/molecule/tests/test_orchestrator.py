import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


DEBPACKAGES = ['percona-orchestrator-cli', 'percona-orchestrator-client', 'percona-orchestrator']
VERSION = os.getenv("ORCHESTRATOR_VERSION")


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert VERSION in pkg.version, pkg.version


def test_check_rpm_package(host):
    dist = host.system_info.distribution
    if dist.lower() in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package('percona-orchestrator')
    assert pkg.is_installed
    assert VERSION in pkg.version, pkg.version


def test_version(host):
    cmd = 'orchestrator --version'
    dist = host.system_info.distribution
    if dist.lower() in ["redhat", "centos", 'rhel']:
        cmd = "/usr/local/orchestrator/orchestrator --version"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr


def test_client(host):
    cmd = 'orchestrator-client --help h'
    dist = host.system_info.distribution
    if dist.lower() in ["redhat", "centos", 'rhel']:
        cmd = "/usr/local/orchestrator/resources/bin/orchestrator-client --help h"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr


def test_integration(host):
    # command = "mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';\""
    # result = host.run(command)
    # assert result.rc == 0, (result.stderr, result.stdout)
    test_cmd = "cd /root/orchestrator/tests/integration && ./test.sh mysql"
    test = host.run(test_cmd)
    assert test.rc == 0, test.stdout
