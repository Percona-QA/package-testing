#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
import time
from settings import *


container_name = 'proxy-docker-test-inspect4'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '-p', '16042:6032', '-p', '16043:6033', '-p', '16076:6070', '--name', container_name, '-d', docker_image_latest]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestMysqlEnvironment:

    def test_proxysql_version(self, host):
        output = host.check_output('proxysql --version')
        expected = f'ProxySQL version {proxysql_version}'
        assert expected in output

    def test_process_running(self, host):
        proc = host.process.filter(comm='proxysql')
        assert proc
        assert any('proxysql' in p.args for p in proc)

