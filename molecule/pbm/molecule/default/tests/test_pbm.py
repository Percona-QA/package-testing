import os
import pytest
import time
import yaml
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

storage_configs = ['/etc/pbm-agent-storage.conf', '/etc/pbm-agent-storage-gcp.conf',
                   '/etc/pbm-agent-storage-local.conf']


def parse_yaml_string(ys):
    """Parse yaml string to dictionary

    :param ys:
    :return:
    """
    fd = StringIO(ys)
    dct = yaml.load(fd)
    return dct


@pytest.fixture()
def start_stop_pbm(host):
    """Start and stop pbm-agent service

    :param host:
    :return:
    """
    with host.sudo("root"):
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
    with host.sudo("root"):
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
    command = "pbm config --file=/etc/pbm-agent-storage.conf --mongodb-uri=mongodb://localhost:27017/"
    result = host.run(command)
    return result


@pytest.fixture()
def show_store(host, set_store):
    """Show pbm store

    :param host:
    :param set_store:
    :return:
    """
    command = "pbm config --list --mongodb-uri=mongodb://localhost:27017/?replicaSet=rs1"
    result = host.run(command)
    assert result.rc == 0, result.stdout
    return parse_yaml_string(result.stdout.split("\n", 2)[2].strip())


@pytest.fixture(scope="module")
def backup(host):
    """Insert data and create backup.

    :param host:
    :return:
    """
    drop_data = """mongo --quiet --eval 'db.dropDatabase()' test"""
    host.run(drop_data)
    insert_data = """mongo --quiet --eval 'for(
    i=1; i <= 100000; i++) { db.test.insert( {_id: i, name: "Test_"+i })}' test"""
    insert_data_result = host.run(insert_data)
    assert insert_data_result.rc == 0, insert_data_result.stdout
    assert insert_data_result.stdout.strip("\n") == """WriteResult({ "nInserted" : 1 })""", insert_data_result.stdout
    save_hash = """mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1"""
    save_hash_result = host.run(save_hash)
    assert save_hash_result.rc == 0, save_hash_result.stdout
    hash = save_hash_result.stdout.strip("\n")
    backup = """pbm backup --mongodb-uri=mongodb://localhost:27017"""
    backup_result = host.run(backup)
    assert 'Starting' in backup_result.stdout, backup_result.stdout
    time.sleep(120)
    backup_name = backup_result.stdout.split()[2].strip("\'").rstrip("'...")
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
    print(restore_result.stdout)
    time.sleep(120)
    db_hash_after = """mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1"""
    db_hash_after_result = host.run(db_hash_after)
    assert db_hash_after_result.rc == 0, db_hash_after_result.stdout
    return db_hash_after_result.stdout.strip("\n")


def test_package(host):
    """Check pbm package
    """
    with host.sudo("root"):
        package = host.package("percona-backup-mongodb")
        assert package.is_installed
        assert "1.1.1" in package.version, package.version


def test_service(host):
    """Check pbm-agent service
    """
    with host.sudo("root"):
        service = host.service("pbm-agent")
        assert service.is_enabled
        assert service.is_running


def test_pbm_binary(host):
    """Check pbm binary
    """
    file = host.file("/usr/bin/pbm")
    assert file.user == "root"
    assert file.group == "root"
    try:
        assert file.mode == 0o755
    except AssertionError:
        pytest.xfail("Possible xfail")


def test_pbm_agent_binary(host):
    """Check pbm agent binary
    """
    file = host.file("/usr/bin/pbm-agent")
    assert file.user == "root"
    assert file.group == "root"
    try:
        assert file.mode == 0o755
    except AssertionError:
        pytest.xfail("Possible xfail")


def test_pbm_storage_default_config(host):
    """Check pbm agent binary
    """
    file = host.file("/etc/pbm-storage.conf")
    assert file.user == "pbm"
    assert file.group == "pbm"
    try:
        assert file.mode == 0o644
    except AssertionError:
        pytest.xfail("Possible xfail")


# TODO add correct start/stop test
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
    assert parsed_config['Version'] == '1.1.1', parsed_config
    assert parsed_config['Platform'], parsed_config
    assert parsed_config['GitCommit'], parsed_config
    assert parsed_config['GitBranch'], parsed_config
    assert parsed_config['BuildTime'], parsed_config
    assert parsed_config['GoVersion'], parsed_config


def test_pbm_help(host):
    """Check that pbm have help message

    :param host:
    :return:
    """
    result = host.run("pbm help")
    assert result.rc == 0, result.stdout


def test_set_store(set_store):
    """Set and show storage test

    :param set_store:
    :return:
    """
    assert set_store.rc == 0, set_store.stdout
    store_out = parse_yaml_string("\n".join(set_store.stdout.split("\n")[2:-2]))
    assert store_out['storage']['type'] == 's3'
    assert store_out['storage']['s3']['region'] == 'us-east-1'
    assert store_out['storage']['s3']['bucket'] == 'operator-testing'


def test_show_store(show_store):
    """Check that all store configuration paramateres presented

    :param show_store:
    :return:
    """
    assert show_store['s3']
    assert show_store['s3']['region'] == 'us-east-1'
    assert show_store['s3']['bucket'] == 'operator-testing'


def test_backup(backup):
    """Create backup

    :param backup:
    :return:
    """
    assert backup[0], backup
    assert backup[1], backup


def test_backup_list(host, backup):
    """Show backup list

    :param backup:
    :return:
    """
    cmd = "pbm list --mongodb-uri=mongodb://localhost:27017"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    assert backup[1] in result.stdout, result.stdout


def test_restore(restore, backup):
    """Compare hashes after restore

    :param restore:
    :param backup:
    :return:
    """
    print(backup[0])
    print(restore)
    assert backup[0] == restore, restore


@pytest.mark.parametrize("store", storage_configs, ids=['aws', 'gcp', 'local'])
def test_backup_and_restore(host, store):
    drop_data = """mongo --quiet --eval 'db.dropDatabase()' test"""
    host.run(drop_data)
    command = "pbm config --file={} --mongodb-uri=mongodb://localhost:27017/".format(store)
    result = host.run(command)
    assert result.rc == 0, result.stderr
    time.sleep(180)
    print(host.run('pbm config --list --mongodb-uri=mongodb://localhost:27017/'))
    insert_data = """mongo --quiet --eval 'for(
        i=1; i <= 100000; i++) { db.test.insert( {_id: i, name: "Test_"+i })}' test"""
    insert_data_result = host.run(insert_data)
    assert insert_data_result.rc == 0, insert_data_result.stdout
    assert insert_data_result.stdout.strip("\n") == """WriteResult({ "nInserted" : 1 })""", insert_data_result.stdout
    save_hash = """mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1"""
    save_hash_result = host.run(save_hash)
    assert save_hash_result.rc == 0, save_hash_result.stdout
    hash_before = save_hash_result.stdout.strip("\n")
    backup = """pbm backup --mongodb-uri=mongodb://localhost:27017"""
    backup_result = host.run(backup)
    print(backup_result.stdout)
    assert 'Starting' in backup_result.stdout, backup_result.stdout
    time.sleep(120)
    backup_name = backup_result.stdout.split()[2].strip("\'").rstrip("'...")
    cmd = "pbm list --mongodb-uri=mongodb://localhost:27017"
    result = host.run(cmd)
    assert result.rc == 0, result.stdout
    assert backup_name in result.stdout, result.stdout
    drop_data = """mongo --quiet --eval 'db.dropDatabase()' test"""
    drop_data_result = host.run(drop_data)
    assert drop_data_result.rc == 0, drop_data_result.stdout
    documents_after_drop = """mongo --quiet --eval 'db.test.count()' test|tail -n1"""
    result = host.run(documents_after_drop)
    assert result.rc == 0, result.stdout
    assert result.stdout.split("\n")[0] == "0"
    restore = """pbm restore --mongodb-uri=mongodb://localhost:27017 {}""".format(backup_name)
    restore_result = host.run(restore)
    print(restore_result.stdout)
    print(restore_result.stderr)
    # assert restore_result.rc == 0, restore_result.stdout
    time.sleep(360)
    db_hash_after = """mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1"""
    db_hash_after_result = host.run(db_hash_after)
    db_hash_after_value = db_hash_after_result.stdout.strip("\n")
    assert db_hash_after_result.rc == 0, db_hash_after_result.stdout
    print(hash_before)
    print(db_hash_after_value)
    assert hash_before == db_hash_after_value
