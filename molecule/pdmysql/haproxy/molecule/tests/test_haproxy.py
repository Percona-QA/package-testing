import os

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

VERSION = os.getenv("PROXYSQL_VERSION")


@pytest.fixture
def create_user(host):
    with host.sudo("root"):
        cmd = "mysql -e \"CREATE USER 'haproxy_user'@'%' IDENTIFIED WITH mysql_native_password by '$3Kr$t';\""
        result = host.run(cmd)
        assert result.rc == 0, result.stdout


def test_haproxy_service(host):
    assert host.service("haproxy").is_running


def test_haproxy(host, create_user):
    with host.sudo("root"):
        cmd = "mysql -e \"SELECT VERSION();\""
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = "mysql --port=9201 -e \"SELECT VERSION();\" "
        result = host.run(cmd)
        print(result.stdout)
        assert result.rc == 0, result.stdout
