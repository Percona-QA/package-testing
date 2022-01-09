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


def test_haproxy(host, create_user):
    with host.sudo("root"):
        cmd = "curl http://localhost:9200"
        curl = host.run(cmd)
        print(curl.stdout)
        assert curl.rc == 0, curl.stderr
        cmd = "mysql -e \"SELECT VERSION();\""
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = "mysql -e \"SELECT VERSION();\" --port"
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
