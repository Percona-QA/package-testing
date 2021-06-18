import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_ps_server_version(host):
    cmd = host.run("/usr/sbin/mysqld --version")
    assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout
    assert os.environ['PS_REVISION'] in cmd.stdout

def test_ps_client_version(host):
    cmd = host.run("mysql --version")
    assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout
    assert os.environ['PS_REVISION'] in cmd.stdout

def test_group_replication_plugin(host):
    cmd = host.run("mysql -uroot -pTest1234# -Ns -e \"select PLUGIN_STATUS from information_schema.PLUGINS where PLUGIN_NAME='group_replication';\"")
    assert "ACTIVE" in cmd.stdout

def test_clone_plugin(host):
    cmd = host.run("mysql -uroot -pTest1234# -Ns -e \"select PLUGIN_STATUS from information_schema.PLUGINS where PLUGIN_NAME='clone';\"")
    assert "ACTIVE" in cmd.stdout
