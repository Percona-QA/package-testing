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
ENGINES = ['mmapv1', 'inMemory', 'wiredTiger']

BINARIES = ['mongo', 'mongod', 'mongos', 'bsondump', 'mongoexport',
            'mongofiles', 'mongoimport', 'mongorestore', 'mongotop', 'mongostat']

PSMDB42_VER = "4.2.1"
LOG = "/tmp/psmdb_run.log"
BACKUPDIR = "/tmp/backup"
CONFIGFILE = "/etc/mongod.conf"
BACKUP_CONFIGFILE = "/tmp/mongod.conf.backup"
SERVICE = 'mongod'
KEY_FILE = "/package-testing/scripts/psmdb_encryption/mongodb-keyfile"
TOKEN_FILE = "/package-testing/scripts/psmdb_encryption/mongodb-test-vault-token"
CA_FILE = "/package-testing/scripts/psmdb_encryption/test.cer"


def start_service(host):
    os = host.system_info.distribution
    cmd = "service mongod start"
    if os == 'debian':
        if host.system_info.codename == 'trusty':
            cmd = "/etc/init.d/mongod start"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
        if result.rc == 1:
            print(host.run("systemctl status mongod.service").stdout)
    assert result.rc == 0, result.stdout

    return result


def stop_service(host):
    os = host.system_info.distribution
    cmd = "service mongod stop"
    if os == 'debian':
        if host.system_info.codename == 'trusty':
            cmd = "/etc/init.d/mongod stop"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
        print(result.stderr)
        if result.rc == 1:
            print(host.run("systemctl status mongod.service").stdout)
    assert result.rc == 0, result.stdout
    return result


def clean_datadir(host):
    DATADIR = "/var/lib/mongodb"
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        DATADIR="/var/lib/mongodb"
    elif os in ['sles']:
        DATADIR = "/var/lib/mongo"
    cmd = "rm -rf {}".format(DATADIR)
    with host.sudo():
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        return result


def hotbackup(host):
    with host.sudo():
        DATADIR = "/var/lib/mongodb"
        os = host.system_info.distribution
        if os in ["debian", "ubuntu"]:
            DATADIR = "/var/lib/mongodb"
        elif os in ['sles']:
            DATADIR = "/var/lib/mongo"
        md5_before_cmd = "mongo localhost:27017/test --quiet --eval \"db.runCommand({ dbHash: 1 }).md5\" | tail -n1)"
        md5_before = host.run(md5_before_cmd)
        assert md5_before.rc == 0, md5_before.stdout
        rm_backup_dir_cmd = "rm -rf {}".format(BACKUPDIR)
        rm_backup_dir = host.run(rm_backup_dir_cmd)
        assert rm_backup_dir.rc == 0, rm_backup_dir.stdout
        mkdir_cmd = "mkdir -p {}".format(BACKUPDIR)
        mkdir = host.run(mkdir_cmd)
        assert mkdir.rc == 0, mkdir.stdout
        chown_cmd = "chown mongod:mongod -R {}".format(BACKUPDIR)
        chown = host.run(chown_cmd)
        assert chown.rc == 0, chown.stdout
        backup_cmd = "mongo localhost:27017/admin --eval" \
                     " \"db.runCommand({createBackup: 1, backupDir: '{}'})\"|grep -c \'\"ok\" : 1\'"
        backup = host.run(backup_cmd)
        assert backup.rc == 0, backup.stdout
        stop_service(host)
        clean_datadir(host)
        cp_dirs_cmd = "cp -r {}/* {}/".format(BACKUPDIR, DATADIR)
        cp_dirs = host.run(cp_dirs_cmd)
        assert cp_dirs.rc == 0, cp_dirs.stdout
        chown_data_cmd = "chown mongod:mongod -R {}".format(DATADIR)
        chown_data = host.run(chown_data_cmd)
        assert chown_data.rc == 0, chown_data.stdout
        start_service(host)
        md5_after_cmd = "mongo localhost:27017/test --quiet --eval \"db.runCommand({ dbHash: 1 }).md5\" | tail -n1)"
        md5_after = host.run(md5_after_cmd)
        assert md5_after.rc == 0, md5_after.stdout
        assert md5_after.stdout == md5_before.stdout
        rm_backup_dir_cmd = "rm -rf {}".format(BACKUPDIR)
        rm_backup_dir = host.run(rm_backup_dir_cmd)
        assert rm_backup_dir.rc == 0, rm_backup_dir.stdout


def list_data(host):
    LOG = "/tmp/psmdb_run.log"
    DATADIR = "/var/lib/mongodb"
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        DATADIR = "/var/lib/mongodb"
    elif os in ['sles']:
        DATADIR = "/var/lib/mongo"
    with host.sudo():
        cmd = "ls -alh {} / >> {}".format(DATADIR, LOG)
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        return result


def test_package_script(host):
    with host.sudo():
        result = host.run("/package-testing/package_check.sh psmdb42")
        print(result.stdout)
        print(result.stderr)
    assert result.rc == 0, result.stderr


def test_version_script(host):
    with host.sudo():
        result = host.run("/package-testing/version_check.sh psmdb42")
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
    assert PSMDB42_VER in pkg.version


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
    assert PSMDB42_VER in pkg.version


@pytest.mark.parametrize("package", RPM_NEW_CENTOS_PACKAGES)
def test_rpm8_packages(host, package):
    os = host.system_info.distribution
    if os in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    if float(host.system_info.release) < 8.0:
        pytest.skip("Only for centos7 tests")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PSMDB42_VER in pkg.version


@pytest.mark.parametrize("binary", BINARIES)
def test_binary_version(host, binary):
    cmd = '{} --version|head -n1|grep -c "{}"'.format(binary, PSMDB42_VER)
    result = host.run(cmd)
    assert result.rc == 0, result.stdout


def test_functional(host):
    with host.sudo():
        result = host.run("/package-testing/scripts/psmdb_test.sh 4.2")
    assert result.rc == 0, result.stderr


@pytest.mark.parametrize("encryption", ['keyfile', 'vault'])
def test_encryption(host, encryption):
    with host.sudo():
        result = host.run("/package-testing/scripts/psmdb_encryption/psmdb-encryption-test.sh {}".format(encryption))
    assert result.rc == 0, result.stderr


def test_enable_auth(host):
    cmd = "/package-testing/scripts/psmdb_set_auth.sh"
    with host.sudo():
        result = host.run(cmd)
    assert result.rc == 0, result.stdout


def test_bats(host):
    cmd = "/usr/local/bin/bats /package-testing/bats/mongo-init-scripts.bats"
    with host.sudo():
        result = host.run(cmd)
    assert result.rc == 0, result.stdout


def test_bats_with_numactl(host):
    with host.sudo():
        os = host.system_info.distribution
        cmd = 'apt-get install numactl -y'
        if os.lower() in ["redhat", "centos", 'rhel']:
            cmd = 'yum install numactl -y'
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = "/usr/local/bin/bats /package-testing/bats/mongo-init-scripts.bats"
        result = host.run(cmd)
    assert result.rc == 0, result.stdout


def test_service(host):
    with host.sudo():
        start_service(host)
        assert host.service("mongod").is_running

