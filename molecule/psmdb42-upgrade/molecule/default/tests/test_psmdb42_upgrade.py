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
        result = host.run("command: /package-testing/version_check.sh psmdb42")
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


# @pytest.mark.parametrize("engine", ENGINES)
def test_functional(host):
    with host.sudo():
        result = host.run("/package-testing/scripts/psmdb_test.sh 4.2")
    assert result.rc == 0, result.stderr
    # with host.sudo():
    #     backup_config_cmd = "cp {} {}".format(CONFIGFILE, BACKUP_CONFIGFILE)
    #     backup_config = host.run(backup_config_cmd)
    #     assert backup_config.rc == 0, backup_config.stdout
    #     stop_service(host)
    #     clean_datadir(host)
    #     set_engine_cmd = 'sed -i "/engine: *{}/s/#//g" {}'.format(engine, CONFIGFILE)
    #     set_engine = host.run(set_engine_cmd)
    #     print(set_engine.stdout)
    #     print(set_engine.stderr)
    #     assert set_engine.rc == 0, set_engine.stdout
    #     start_service(host)
    #     check_engine_cmd = "mongo --eval \"db.serverStatus().storageEngine\" | tee -a {}".format(LOG)
    #     check_engine = host.run(check_engine_cmd)
    #     assert check_engine.rc == 0, check_engine.stdout
    #     insert_data_cmd = "mongo < /package-testing/scripts/mongo_insert.js >> {}".format(LOG)
    #     insert_data = host.run(insert_data_cmd)
    #     assert insert_data.rc == 0, insert_data.stdout
    #     if engine == 'wiredTiger':
    #        hotbackup(host)
    #     stop_service(host)
    #     disable_engine_cmd = "sed -i \"/engine: *{}/s//#engine: {}/g\" {}".format(engine, engine, LOG)
    #     disable_engine = host.run(disable_engine_cmd)
    #     assert disable_engine.rc == 0, disable_engine.stdout


# @pytest.mark.parametrize("cipher", ['AES256-CBC', 'AES256-GCM'])
# def test_encryption_keyfile(host, cipher):
    # with host.sudo():
    #     backup_config_cmd = "cp {} {}".format(CONFIGFILE, BACKUP_CONFIGFILE)
    #     backup_config = host.run(backup_config_cmd)
    #     assert backup_config.rc == 0, backup_config.stdout
    #     chmod_key_cmd = "chmod 600 {}".format(KEY_FILE)
    #     chmod_key = host.run(chmod_key_cmd)
    #     assert chmod_key.rc == 0, chmod_key.stdout
    #     chown_cmd = "chown mongod:mongod -R {}".format(KEY_FILE)
    #     chown = host.run(chown_cmd)
    #     assert chown.rc == 0, chown.stdout
    #     stop_service(host)
    #     clean_datadir(host)
    #     sed_cmd = "sed -i \"/^  engine: /s/^/#/g\" {}".format(CONFIGFILE)
    #     sed = host.run(sed_cmd)
    #     assert sed.rc == 0, sed.stdout
    #     set_engine_cmd = "sed -i \"/engine: *wiredTiger/s/#//g\" {}"
    #     set_engine = host.run(set_engine_cmd)
    #     assert set_engine.rc == 0, set_engine.stdout
    #     if cipher == "AES256-CBC":
    #         set_encr_cmd = "sed -i \"s|#security:|security:\n  enableEncryption: true\n" \
    #                         "  encryptionCipherMode: {}\n  encryptionKeyFile: {}|\" {}".format(cipher, KEY_FILE, CONFIGFILE)
    #     else:
    #         set_encr_cmd = "sed -i \"s/encryptionCipherMode: AES256-CBC/encryptionCipherMode: AES256-GCM/\" {}".format(
    #             CONFIGFILE)
    #     set_encr = host.run(set_encr_cmd)
    #     assert set_encr.rc == 0, set_encr.stdout
    #     start_service(host)
    #     check_enc_enabled_cmd = "mongo --quiet --eval" \
    #                             " \"db.serverCmdLineOpts().parsed.security.enableEncryption\" | tail -n1"
    #     check_enc_mode_cmd = "mongo --quiet --eval" \
    #                          " \"db.serverCmdLineOpts().parsed.security.encryptionCipherMode\" | tail -n1"
    #     check_enc_key_file_cmd = "mongo --quiet --eval" \
    #                              " \"db.serverCmdLineOpts().parsed.security.encryptionKeyFile\" | tail -n1"
    #     check_enc_enabled = host.run(check_enc_enabled_cmd)
    #     assert check_enc_enabled.rc == 0, check_enc_enabled.stdout
    #     assert 'true' == check_enc_enabled.stdout.strip("\n")
    #     check_enc_mode = host.run(check_enc_mode_cmd)
    #     assert check_enc_mode.rc == 0, check_enc_mode.stdout
    #     assert cipher == check_enc_mode.stdout.strip("\n")
    #     check_enc_key_file = host.run(check_enc_key_file_cmd)
    #     assert check_enc_key_file.rc == 0, check_enc_key_file.stdout
    #     assert KEY_FILE == check_enc_key_file.stdout.strip("\n")
    #     add_data_cmd = 'mongo localhost:27017/test --eval ' \
    #                    '"for(i=1; i <= 100000; i++) { db.series.insert( {{ id: i, name: \'series\'+i }})}" >> {}'.format(LOG
    #                                                                                                                      )
    #     add_data = host.run(add_data_cmd)
    #     assert add_data.rc == 0, add_data.stdout
    #     add_index_cmd = "mongo localhost:27017/test --eval \"db.series.ensureIndex({{ name: 1 }})\" >> {}".format(LOG)
    #     add_index = host.run(add_index_cmd)
    #     assert add_index.rc == 0, add_index.stdout
    #     hotbackup(host)


# @pytest.mark.parametrize("cipher", ['AES256-CBC', 'AES256-GCM'])
# def test_encryption_vault(host, cipher):
#     with host.sudo():
#         backup_config_cmd = "cp {} {}".format(CONFIGFILE, BACKUP_CONFIGFILE)
#         backup_config = host.run(backup_config_cmd)
#         assert backup_config.rc == 0, backup_config.stdout
#         chmod_ca_cmd = "chmod 600 {}".format(CA_FILE)
#         chmod_ca = host.run(chmod_ca_cmd)
#         assert chmod_ca.rc == 0, chmod_ca.stdout
#         chmod_token_cmd = "chmod 600 {}".format(TOKEN_FILE)
#         chmod_token = host.run(chmod_token_cmd)
#         assert chmod_token.rc == 0, chmod_token.stdout
#         chown_cmd = "chown mongod:mongod {}".format(CA_FILE)
#         chown = host.run(chown_cmd)
#         assert chown.rc == 0, chown.stdout
#         stop_service(host)
#         clean_datadir(host)
#         sed_cmd = "sed -i \"/^  engine: /s/^/#/g\" {}".format(CONFIGFILE)
#         sed = host.run(sed_cmd)
#         assert sed.rc == 0, sed.stdout
#         print(host.run("cat {}").format(CONFIGFILE).stdout)
#         set_engine_cmd = "sed -i \"/engine: *wiredTiger/s/#//g\" {}"
#         set_engine = host.run(set_engine_cmd)
#         assert set_engine.rc == 0, set_engine.stdout
#         if cipher == "AES256-CBC":
#             set_encr_cmd = "sed -i \"s|#security:|security:\n  enableEncryption: true\n" \
#                            "  encryptionCipherMode: {}\n  vault:\n    serverName: 10.30.6.213\n" \
#                            "    port: 8200\n    tokenFile: {}\n    serverCAFile: {}\n" \
#                            "    secret: secret_v2/data/psmdb-test/package-test|\" {}".format(cipher, TOKEN_FILE,
#                                                                                              CA_FILE, CONFIGFILE)
#         else:
#             set_encr_cmd = "sed -i \"s/encryptionCipherMode: AES256-CBC/encryptionCipherMode: AES256-GCM/\" {}".format(
#                 CONFIGFILE)
#         set_encr = host.run(set_encr_cmd)
#         print(host.run("cat {}").format(CONFIGFILE).stdout)
#         assert set_encr.rc == 0, set_encr.stdout
#         start_service(host)
#         check_enc_enabled_cmd = "mongo --quiet --eval" \
#                                 " \"db.serverCmdLineOpts().parsed.security.enableEncryption\" | tail -n1"
#         check_enc_mode_cmd = "mongo --quiet --eval" \
#                              " \"db.serverCmdLineOpts().parsed.security.encryptionCipherMode\" | tail -n1"
#         check_enc_ip_cmd = "mongo --quiet --eval" \
#                            " \"db.serverCmdLineOpts().parsed.security.encryptionKeyFile\" | tail -n1"
#         check_enc_enabled = host.run(check_enc_enabled_cmd)
#         assert check_enc_enabled.rc == 0, check_enc_enabled.stdout
#         assert 'true' == check_enc_enabled.stdout.strip("\n")
#         check_enc_mode = host.run(check_enc_mode_cmd)
#         assert check_enc_mode.rc == 0, check_enc_mode.stdout
#         assert cipher == check_enc_mode.stdout.strip("\n")
#         check_enc_ip = host.run(check_enc_ip_cmd)
#         assert check_enc_ip.rc == 0, check_enc_ip.stdout
#         assert "10.30.6.213" == check_enc_ip.stdout.strip("\n")
#         add_data_cmd = 'mongo localhost:27017/test --eval ' \
#                        '"for(i=1; i <= 100000; i++) { db.series.insert( {{ id: i, name: \'series\'+i }})}" >> {}'.format(LOG
#                                                                                                                          )
#         add_data = host.run(add_data_cmd)
#         assert add_data.rc == 0, add_data.stdout
#         add_index_cmd = "mongo localhost:27017/test --eval \"db.series.ensureIndex({{ name: 1 }})\" >> {}".format(LOG)
#         add_index = host.run(add_index_cmd)
#         assert add_index.rc == 0, add_index.stdout
#         hotbackup(host)


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


def test_service(host):
    with host.sudo():
        start_service(host)

    assert host.service("mongod").is_running

