import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-xtrabackup-80',
               'percona-xtrabackup-test-80',
               'percona-xtrabackup-dbg-80']

RPMPACKAGES = ['percona-xtrabackup-80',
               'percona-xtrabackup-test-80',
               'percona-xtrabackup-80-debuginfo']


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    cmd = host.run("apt-cache showpkg {}".format(package))
    print(cmd.stdout)
    pkg = host.package(package)
    assert pkg.is_installed
    assert '8.0.11' in pkg.version, pkg.version


@pytest.mark.parametrize("package", RPMPACKAGES)
def test_check_rpm_package(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    cmd = host.run("repoquery -i {}".format(package))
    print(cmd.stdout)
    pkg = host.package(package)
    assert pkg.is_installed
    assert '8.0.11' in pkg.version, pkg.version


def test_binary_version(host):
    cmd = "xtrabackup --version"
    result = host.run(cmd)
    print(result.stderr)
    assert result.rc == 0, result.stderr
    assert '8.0.11' in result.stderr, (result.stdout, result.stdout)


def test_run_backup(host):
    with host.sudo("root"):
        cmd = "/usr/bin/xtrabackup --backup --user=root --target-dir=/tmp/backups/"
        result = host.run(cmd)
        print(result.stdout)
        assert result.rc == 0, result.stderr


def test_run_prepare(host):
    with host.sudo("root"):
        cmd = "/usr/bin/xtrabackup --prepare --user=root --target-dir=/tmp/backups/"
        result = host.run(cmd)
        print(result.stdout)
        assert result.rc == 0, result.stderr
