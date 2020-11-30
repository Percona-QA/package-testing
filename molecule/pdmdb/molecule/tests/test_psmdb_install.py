import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEB_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-server', 'percona-server-mongodb-mongos',
                'percona-server-mongodb-shell', 'percona-server-mongodb-tools', 'percona-server-mongodb-dbg']
RPM_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-server', 'percona-server-mongodb-mongos',
                'percona-server-mongodb-shell', 'percona-server-mongodb-tools', 'percona-server-mongodb-debuginfo']
RPM_NEW_CENTOS_PACKAGES = ['percona-server-mongodb', 'percona-server-mongodb-mongos-debuginfo',
                           'percona-server-mongodb-server-debuginfo', 'percona-server-mongodb-shell-debuginfo',
                           'percona-server-mongodb-tools-debuginfo', 'percona-server-mongodb-debugsource']

BINARIES = ['mongo', 'mongod', 'mongos', 'bsondump', 'mongoexport',
            'mongofiles', 'mongoimport', 'mongorestore', 'mongotop', 'mongostat']

PSMDB_VER = os.environ.get("VERSION").lstrip("pdmdb-")


def test_mongod_service(host):
    mongod = host.service("mongod")
    assert mongod.is_running


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_packages(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB_VER in pkg.version


# TODO add check that minor version is correct
@pytest.mark.parametrize("package", RPM_PACKAGES)
def test_rpm_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) >= 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB_VER in pkg.version


@pytest.mark.parametrize("package", RPM_NEW_CENTOS_PACKAGES)
def test_rpm8_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) < 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB_VER in pkg.version


@pytest.mark.parametrize("binary", BINARIES)
def test_binary_version(host, binary):
    # cmd = '{} --version|head -n1|grep -c "{}"'.format(binary, PSMDB_VER)
    # result = host.run(cmd)
    result = host.run(f"{binary} --version")
    assert PSMDB_VER in result.stdout, result.stdout
    # assert result.rc == 0, host.run(f"{binary} --version").stdout
