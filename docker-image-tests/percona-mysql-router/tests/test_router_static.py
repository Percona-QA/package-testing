#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *
import json
import os
import requests
import docker

container_name = 'mysql-router-test'
network_name = 'innodbnet1'
docker_tag = os.getenv('ROUTER_VERSION')
docker_acc = os.getenv('DOCKER_ACC')
docker_image = docker_acc + "/" + "percona-mysql-router" + ":" + docker_tag

@pytest.fixture(scope='module')
def host():
    docker_client = docker.from_env()
    docker_client.networks.create(network_name)
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', '--net', network_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', '--MYSQL_INNODB_CLUSTER_MEMBERS', '4', docker_image ], stderr=subprocess.STDOUT ).decode().strip()
    time.sleep(20)
    subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install', '-y', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestRouterEnvironment:
    def test_mysqlsh_version(self, host):
        assert host.check_output("mysqlsh --version") == 'mysqlsh   Ver '+ROUTER_VERSION+' for Linux on x86_64 - for MySQL '+PS_VERSION+' (Source distribution)'

    def test_mysqlrouter_version(self, host):
        assert host.check_output("mysqlrouter --version") == 'MySQL Router  Ver '+PS_VERSION+' for Linux on x86_64 (Percona Server (GPL), Release 25, Revision '+Revision+')'

    def test_binaries_exist(self, host):
        router_binary="/tmp/mysqlrouter"
        assert host.file(router_binary).exists
        assert oct(host.file(router_binary).mode) == '0o755'

    def test_http_port_6447(self, host):
        assert host.socket('tcp://127.0.0.1:6447').is_listening

    def test_raft_port_6446(self, host):
        assert host.socket('tcp://127.0.0.1:6446').is_listening

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups

    def test_mysql_group(self, host):
        assert host.group('mysql').exists
        assert host.group('mysql').gid == 1001

    def test_router_permissions(self, host):
        assert host.file('/var/lib/mysqlrouter').user == 'mysql'
        assert host.file('/var/lib/mysqlrouter').group == 'mysql'
        assert oct(host.file('/var/lib/mysqlrouter').mode) == '0o755'
