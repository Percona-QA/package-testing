#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *

container_name = 'orchestartor-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-d', docker_image ]).decode().strip()
    time.sleep(20)
    subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install', '-y', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestOrchEnvironment:
    def test_packages(self, host):
        pkg = host.package("percona-orchestrator")
        dist = host.system_info.distribution
        assert pkg.is_installed
        if dist.lower() in RHEL_DISTS:
            assert orch_version in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
        else:
            assert orch_version in pkg.version, pkg.version

    def test_binaries_exist(self, host):
        orch_binary="/usr/local/orchestrator/orchestrator"
        assert host.file(orch_binary).exists
        assert oct(host.file(orch_binary).mode) == '0o755'

    def test_binaries_version(self, host):
        assert orch_version in host.check_output("/usr/local/orchestrator/orchestrator --version")

    def test_process_running(self, host):
        assert host.process.get(user="mysql", comm="orchestrator")

    def test_http_port_3000(self, host):
        assert host.socket('tcp://127.0.0.1:3000').is_listening

    def test_raft_port_10008(self, host):
        assert host.socket('tcp://127.0.0.1:10008').is_listening

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups

    def test_mysql_group(self, host):
        assert host.group('mysql').exists
        assert host.group('mysql').gid == 1001

    def test_orch_permissions(self, host):
        assert host.file('/var/lib/orchestrator').user == 'mysql'
        assert host.file('/var/lib/orchestrator').group == 'mysql'
        assert oct(host.file('/var/lib/orchestrator').mode) == '0o755'

    def test_orch_conf_permissions(self, host):
        assert host.file('/etc/orchestrator/orchestrator.conf.json').user == 'mysql'
        assert host.file('/etc/orchestrator/orchestrator.conf.json').group == 'mysql'
        assert oct(host.file('/etc/orchestrator').mode) == '0o775'

    def test_orch_topology_permissions(self, host):
        assert host.file('/etc/orchestrator/orc-topology.cnf').user == 'mysql'
        assert host.file('/etc/orchestrator/orc-topology.cnf').group == 'mysql'
        assert oct(host.file('/etc/orchestrator').mode) == '0o775'