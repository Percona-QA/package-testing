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

PSMDB40_VER = "4.0"


def test_mongod_service(host):
    mongod = host.service("mongod")
    assert mongod.is_running


def test_package_script(host):
    with host.sudo():
        result = host.run("/package-testing/package_check.sh psmdb40")
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stderr


def test_version_script(host):
    with host.sudo():
        result = host.run("/package-testing/version_check.sh psmdb40")
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stderr


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_packages(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB40_VER in pkg.version


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
    assert PSMDB40_VER in pkg.version


@pytest.mark.parametrize("package", RPM_NEW_CENTOS_PACKAGES)
def test_rpm8_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) < 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB40_VER in pkg.version


@pytest.mark.parametrize("binary", BINARIES)
def test_binary_version(host, binary):
    cmd = '{} --version|head -n1|grep -c "{}"'.format(binary, PSMDB40_VER)
    result = host.run(cmd)
    assert result.rc == 0, result.stdout


def test_functional(host):
    with host.sudo():
        result = host.run("/package-testing/scripts/psmdb_test.sh 4.0")
    assert result.rc == 0, result.stderr


@pytest.mark.parametrize("encryption", ['keyfile', 'vault'])
def test_encryption(host, encryption):
    with host.sudo():
        result = host.run("/package-testing/scripts/psmdb_encryption/psmdb-encryption-test.sh {}".format(encryption))
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stderr


def test_enable_auth(host):
    cmd = "/package-testing/scripts/psmdb_set_auth.sh"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stdout


def test_bats(host):
    cmd = "/usr/local/bin/bats /package-testing/bats/mongo-init-scripts.bats"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stdout


def test_bats_with_numactl(host):
    with host.sudo():
        os = host.system_info.distribution
        cmd = 'apt-get install numactl'
        if os.lower() in ["redhat", "centos", 'rhel']:
            cmd = 'yum install numactl'
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = "/usr/local/bin/bats /package-testing/bats/mongo-init-scripts.bats"
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stdout


def test_start_mongod_service(host):
    cmd = "service mongod start"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stdout
    mongod = host.service("mongod")
    assert mongod.is_running
