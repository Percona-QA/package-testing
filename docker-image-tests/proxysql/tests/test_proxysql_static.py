#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
import time
from settings import *


container_name = 'proxy-docker-test-inspect1'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '-p', '16036:6032', '-p', '16037:6033', '-p', '16073:6070', '--name', container_name, '-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestMysqlEnvironment:
    @pytest.mark.parametrize("binary", [
        '/usr/bin/proxysql',
    ])
    def test_binaries_exist(self, host, binary):
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

    def test_proxysql_version(self, host):
        output = host.check_output('proxysql --version')
        expected = f'ProxySQL version {proxysql_version_check}'
        assert expected in output

    def test_process_running(self, host):
        proc = host.process.filter(comm='proxysql')
        assert proc
        assert any('proxysql' in p.args for p in proc)

    def test_proxysql_user(self, host):
        user = host.user('proxysql')
        assert user.exists
        assert 'proxysql' in user.groups or user.group == 'proxysql'

    def test_proxysql_group(self, host):
        group = host.group('proxysql')
        assert group.exists

    def test_datadir_permissions(self, host):
        # Based on proxysql.cnf: datadir="/var/lib/proxysql"
        datadir = host.file('/var/lib/proxysql')
        assert datadir.exists
        assert datadir.user == 'proxysql'
        assert oct(datadir.mode) in ['0o755', '0o750', '0o775']  # Depending on packaging

    def test_config_file(self, host):
        cfg = host.file('/etc/proxysql.cnf')
        assert cfg.exists
        assert cfg.user == 'root'
        assert oct(cfg.mode) in ['0o644', '0o640', '0o600']  # Should not be world-writable

