import os
import time

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

VERSION = os.getenv("VERSION")

# Prepare for the test: create users, restart services
@pytest.fixture
def prepare_test(host):
    with host.sudo("root"):
        cmd = "mysql -e \"CREATE USER 'clustercheckuser'@'%' IDENTIFIED WITH mysql_native_password by 'clustercheckpassword!';\
            GRANT PROCESS ON *.* TO 'clustercheckuser'@'%';\
            CREATE USER 'haproxy_user'@'%' IDENTIFIED WITH mysql_native_password by '$3Kr$t';\""
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = 'service xinetd restart'
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        cmd = 'service haproxy restart'
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        time.sleep(2)

def test_haproxy_service(host):
    assert host.service("haproxy").is_running

def test_haproxy_clustercheck(host, prepare_test):
    with host.sudo("root"):
        cmd = "/usr/bin/clustercheck"
        result = host.run(cmd)
        assert result.rc == 0, result.stdout
        assert 'Percona XtraDB Cluster Node is synced.' in result.stdout, result.stdout

def test_haproxy_connect(host):
    with host.sudo("root"):
        wait=0
        timeout=120
        cmd = "mysql --port=9201 -h127.0.0.1 -uhaproxy_user -p$3Kr$t -e \"SELECT VERSION();\" "
        # wait till ha-proxy is ready to send requests to mysql for 2 mins
        while wait < timeout:
            result = host.run(cmd)
            if "ERROR 2013 (HY000): Lost connection to MySQL server at 'reading initial communication packet', system error: 0" not in result.stdout:
                break
            time.sleep(1)
            wait+=1
        result = host.run(cmd)
        assert result.rc == 0, result.stderr
        assert VERSION in result.stdout, result.stdout
