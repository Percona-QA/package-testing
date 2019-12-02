import os
import pytest
import yaml
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def parse_yaml_string(ys):
    """Parse yaml string to dictionary

    :param ys:
    :return:
    """
    print(ys)
    fd = StringIO(ys)
    dct = yaml.load(fd)
    return dct


@pytest.fixture()
def start_stop_pbm(host):
    """Start and stop pbm-agent service

    :param host:
    :return:
    """
    cmd = "sudo systemctl stop pbm-agent"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    cmd = "sudo systemctl start pbm-agent"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    cmd = "sudo systemctl status pbm-agent"
    return host.run(cmd)


@pytest.fixture()
def restart_pbm_agent(host):
    """Restart pbm-agent service
    """
    cmd = "sudo systemctl restart pbm-agent"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    cmd = "sudo systemctl status pbm-agent"
    return host.run(cmd)


@pytest.fixture()
def set_store(host):
    """Set store for pbm

    :param host:
    :return:
    """
    command = "pbm store set --config=/etc/pbm-agent-storage.conf --mongodb-uri=mongodb://localhost:27017"
    result = host.run(command)
    print(result.stdout)
    return result


@pytest.fixture()
def show_store(host, set_store):
    """Show pbm store

    :param host:
    :param set_store:
    :return:
    """
    command = "pbm store show --mongodb-uri=mongodb://localhost:27017"
    result = host.run(command)
    print(result.stdout)
    assert result.rc == 0, result.stdout
    return parse_yaml_string(result.stdout.split("\n", 2)[2].strip())


@pytest.fixture(scope="module")
def backup(host):
    """Insert data and create backup.

    :param host:
    :return:
    """
    insert_data = """mongo --quiet --eval 'for(
    i=1; i <= 100000; i++) { db.test.insert( {_id: i, name: "Test_"+i })}' test"""
    insert_data_result = host.run(insert_data)
    assert insert_data_result.rc == 0, insert_data_result.stdout
    assert insert_data_result.stdout.strip("\n") == """WriteResult({ "nInserted" : 1 })""", insert_data_result.stdout
    save_hash = """mongo - -quiet - -eval 'db.runCommand({ dbHash: 1 }).md5' test | tail -n1"""
    save_hash_result = host.run(save_hash)
    assert save_hash_result.rc == 0, save_hash_result.stdout
    hash = save_hash_result.stdout.strip("\n")
    backup = """pbm backup --mongodb-uri=mongodb://localhost:27017"""
    backup_result = host.run(backup)
    assert backup_result.rc == 0, backup_result.stdout
    backup_name = backup_result.stdout.split()[2].strip("\'")
    drop_data = """mongo --quiet --eval 'db.dropDatabase()' test"""
    drop_data_result = host.run(drop_data)
    assert drop_data_result.rc == 0, drop_data_result.stdout
    documents_after_drop = """mongo --quiet --eval 'db.test.count()' test|tail -n1"""
    result = host.run(documents_after_drop)
    assert result.rc == 0, result.stdout
    assert result.stdout.split("\n")[0] == "0"
    return hash, backup_name


@pytest.fixture()
def restore(backup, host):
    """Restore database from backup and get hash restored db

    :return:
    """
    restore = """pbm restore --mongodb-uri=mongodb://localhost:27017 {}""".format(backup[1])
    restore_result = host.run(restore)
    assert restore_result.rc == 0, restore_result.stdout
    db_hash_after = """mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1"""
    db_hash_after_result = host.run(db_hash_after)
    assert db_hash_after_result.rc == 0, db_hash_after_result.stdout
    return db_hash_after_result.stdout.strip("\n")


def test_package(host):
    """Check pbm package
    """
    package = host.package("percona-backup-mongodb")
    assert package.is_installed
    assert "1.0-1" in package.version, package.version


def test_service(host):
    """Check pbm-agent service
    """
    service = host.service("pbm-agent")
    assert service.is_enabled
    assert service.is_running


def test_pbm_binary(host):
    """Check pbm binary
    """
    file = host.file("/usr/bin/pbm")
    assert file.user == "root"
    assert file.group == "root"
    assert file.mode == 0o755


def test_pbm_agent_binary(host):
    """Check pbm agent binary
    """
    file = host.file("/usr/bin/pbm-agent")
    assert file.user == "root"
    assert file.group == "root"
    assert file.mode == 0o755


def test_pbm_storage_default_config(host):
    """Check pbm agent binary
    """
    file = host.file("/etc/pbm-storage.conf")
    assert file.user == "pbm"
    assert file.group == "pbm"
    assert file.mode == 0o644


def test_start_stop_service(start_stop_pbm):
    """Start and stop pbm agent

    :param start_stop_pbm:
    """
    assert start_stop_pbm.rc == 0, restart_pbm_agent.stdout
    assert "active" in start_stop_pbm.stdout, restart_pbm_agent.stdout


def test_restart_service(restart_pbm_agent):
    """Restart pbm agent

    :param restart_pbm_agent:
    """
    assert restart_pbm_agent.rc == 0, restart_pbm_agent.stdout
    assert "active" in restart_pbm_agent.stdout


def test_pbm_version(host):
    """Check that pbm version is not empty strings

    :param host:
    :return:
    """
    result = host.run("pbm version")
    assert result.rc == 0, result.stdout
    lines = result.stdout.split("\n")
    parsed_config = {line.split(":")[0]: line.split(":")[1].strip() for line in lines[0:-1]}
    print(parsed_config)
    assert "1.0" in parsed_config['Version']
    assert parsed_config['Platform']
    assert parsed_config['GitCommit']
    assert parsed_config['GitBranch']
    assert parsed_config['BuildTime']
    assert parsed_config['GoVersion']


def test_pbm_help(host):
    """Check that pbm have help message

    :param host:
    :return:
    """
    result = host.run("pbm help")
    assert result.rc == 0


def test_set_store(set_store):
    """Set and show storage test

    :param set_store:
    :return:
    """
    assert set_store.rc == 0, set_store.stdout
    assert "Done" in set_store.stdout


def test_show_store(show_store):
    """Check that all store configuration paramateres presented

    :param show_store:
    :return:
    """
    assert show_store['type'] == 's3'
    assert show_store['s3']
    assert show_store['s3']['region'] == 'us-west'
    assert show_store['s3']['bucket'] == 'pbm'
    assert show_store['s3']['credentials']
    assert show_store['s3']['credentials']['access-key-id']
    assert show_store['s3']['credentials']['secret-access-key']


def test_backup(backup):
    """Create backup

    :param backup:
    :return:
    """
    assert backup[0]
    assert backup[1]


def test_backup_list(host, backup):
    """Show backup list

    :param backup:
    :return:
    """
    cmd = "pbm list --mongodb-uri=mongodb://localhost:27017"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    assert backup[1] in result.stdout


def test_restore(restore, backup):
    """Compare hashes after restore

    :param restore:
    :param backup:
    :return:
    """
    assert backup[0] == restore
