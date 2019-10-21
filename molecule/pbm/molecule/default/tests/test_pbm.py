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
    assert result.rc == 0
    cmd = "sudo systemctl start pbm-agent"
    result = host.run(cmd)
    assert result.rc == 0
    cmd = "sudo systemctl status pbm-agent"
    return host.run(cmd)


@pytest.fixture()
def restart_pbm_agent(host):
    """Restart pbm-agent service
    """
    cmd = "sudo systemctl restart pbm-agent"
    result = host.run(cmd)
    assert result.rc == 0
    cmd = "sudo systemctl status pbm-agent"
    return host.run(cmd)


@pytest.fixture()
def set_store(host):
    """

    :param host:
    :return:
    """
    command = "pbm store set --config=/etc/pbm-agent-storage.conf --mongodb-uri=mongodb://localhost:27017"
    result = host.run(command)
    assert result.rc == 0
    return result


@pytest.fixture()
def show_store(host, set_store):
    """

    :param host:
    :param set_store:
    :return:
    """
    command = "pbm store show --mongodb-uri=mongodb://localhost:27017"
    result = host.run(command)
    assert result.rc == 0
    print(result.stdout)
    return parse_yaml_string(result.stdout)


@pytest.fixture(scope="module")
def backup(host):
    """

    :param host:
    :return:
    """
    pass


@pytest.fixture()
def restore():
    """

    :return:
    """
    pass


def test_package(host):
    """Check pbm package
    """
    package = host.package("percona-backup-mongodb")
    assert package.is_installed
    assert "1.0-1" in package.version


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
    assert start_stop_pbm.rc == 0
    assert "active" in start_stop_pbm.stdout


def test_restart_service(restart_pbm_agent):
    """Restart pbm agent

    :param restart_pbm_agent:
    """
    assert restart_pbm_agent.rc == 0
    assert "active" in restart_pbm_agent.stdout


def test_pbm_version(host):
    """Check that pbm version is not empty strings

    :param host:
    :return:
    """
    result = host.run("pbm version")
    assert result.rc == 0
    lines = result.stdout.split("\n")
    parsed_config = {line.split(":")[0]: line.split(":")[1].strip() for line in lines}
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

    :param host:
    :return:
    """
    pass


def test_show_store(show_store):
    """

    :param show_store:
    :return:
    """
    pass


def test_backup(backup):
    """Create backup

    :param backup:
    :return:
    """
    pass


def test_backup_list(backup):
    """Show backup list

    :param backup:
    :return:
    """


def test_restore(restore):
    pass
