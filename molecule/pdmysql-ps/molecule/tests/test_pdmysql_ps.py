import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-server-server', 'percona-server-test',
               'percona-server-dbg', 'percona-server-source',
               'percona-server-client', 'percona-server-tokudb',
               'percona-server-rocksdb', 'percona-mysql-router',
               'percona-mysql-shell']

RPMPACKAGES = ['percona-server-server', 'percona-server-client',
               'percona-server-test', 'percona-server-debuginfo',
               'percona-server-devel', 'percona-server-tokudb',
               'percona-server-rocksdb', 'percona-mysql-router',
               'percona-mysql-shell']


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    cmd = host.run("apt-cache showpkg {}".format(package))
    print(cmd.stdout)
    pkg = host.package(package)
    assert pkg.is_installed
    assert '8.0.18' in pkg.version, pkg.version


@pytest.mark.parametrize("package", RPMPACKAGES)
def test_check_rpm_package(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    cmd = host.run("repoquery -i {}".format(package))
    print(cmd.stdout)
    pkg = host.package(package)
    assert pkg.is_installed
    assert '8.0.18' in pkg.version, pkg.version


@pytest.mark.parametrize("binary", ['mysqlsh', 'mysql', 'mysqlrouter'])
def test_binary_version(host, binary):
    cmd = "{} --version".format(binary)
    result = host.run(cmd)
    print(result.stdout)
    assert result.rc == 0, result.stderr
    assert '8.0.18' in result.stdout, result.stdout
