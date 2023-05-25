#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *

container_name = 'router-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-d', docker_image ], stderr=subprocess.STDOUT ).decode().strip()
    time.sleep(20)
    subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install', '-y', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestRouterEnvironment:
    def test_packages(self, host):
        pkg = host.package("percona-mysql-router")
        dist = host.system_info.distribution
        assert pkg.is_installed
        if dist.lower() in RHEL_DISTS:
            assert router_version in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
        else:
            assert router_version in pkg.version, pkg.version

    def test_mysqlsh_version(self, host):
        cmd = host.run("mysqlsh --version")
        assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout

    def test_mysqlrouter_version(self, host):
        cmd = host.run("mysqlrouter --version")
        assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout
        assert os.environ['PS_REVISION'] in cmd.stdout    

    def test_binaries_exist(self, host):
        router_binary="/tmp/mysqlrouter"
        assert host.file(router_binary).exists
        assert oct(host.file(router_binary).mode) == '0o755'

    def test_binaries_version(self, host):
        assert router_version in host.check_output("/tmp/mysqlrouter --version")
    
    def test_mysqlsh_version(self, host):
        assert router_version in host.check_output("/tmp/mysqlrouter --version")

#    def test_process_running(self, host):
#        assert host.process.get(user="mysql", comm="orchestrator")

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

    def test_orch_permissions(self, host):
        assert host.file('/var/lib/mysqlrouter').user == 'mysql'
        assert host.file('/var/lib/mysqlrouter').group == 'mysql'
        assert oct(host.file('/var/lib/mysqlrouter').mode) == '0o755'
