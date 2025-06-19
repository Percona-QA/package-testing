#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
from settings import *


container_name = 'proxy-docker-test-inspect1'

@pytest.fixture(scope='module')
#def host():
#    docker_id = subprocess.check_output(
#        ['docker', 'run', '-p', '16034:6032', '-p', '16035:6033', '-p', '16072:6070', '--name', container_name, '-d', docker_image]).decode().strip()
#    subprocess.check_call(['docker','exec', container_name, 'yum', '-y', 'install', 'net-tools'])
#    time.sleep(20)
#    yield testinfra.get_host("docker://root@" + docker_id)
#    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def host():
    docker_id = subprocess.check_output(
        [
            'docker', 'run',
            '-p', '16034:6032',
            '-p', '16035:6033',
            '-p', '16072:6070',
            '--name', container_name,
            '-d', docker_image
        ]
    ).decode().strip()

    # Optional wait loop to ensure the container is up
    for _ in range(10):
        try:
            subprocess.check_call(['docker', 'exec', container_name, 'true'])
            break
        except subprocess.CalledProcessError:
            time.sleep(2)

    # Install net-tools using microdnf (RHEL 9.5)
    try:
        subprocess.check_call([
            'docker', 'exec', container_name,
            'microdnf', 'install', '-y', 'net-tools'
        ])
    except subprocess.CalledProcessError as e:
        print("⚠️ Failed to install net-tools:", e)

    time.sleep(10)

    yield testinfra.get_host("docker://root@" + docker_id)

    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestMysqlEnvironment:
    @pytest.mark.parametrize("pkg_name", ['proxysql'])  # Add more packages if applicable
    def test_packages(self, host, pkg_name):
        assert host.package(pkg_name).is_installed
        assert host.package(pkg_name).version.startswith(proxysql_version_upstream)

    @pytest.mark.parametrize("binary", [
        '/usr/bin/proxysql',
        '/usr/sbin/proxysql'  # Add more if needed
    ])
    def test_binaries_exist(self, host, binary):
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

    def test_proxysql_version(self, host):
        output = host.check_output('proxysql --version')
        expected = f'proxysql version {proxysql_version_upstream}'
        assert expected in output

    def test_process_running(self, host):
        proc = host.process.filter(comm='proxysql')
        assert proc
        assert any('proxysql' in p.args for p in proc)

    def test_proxysql_admin_port(self, host):
        # 6032 is the default admin interface port
        assert host.socket("tcp://0.0.0.0:6032").is_listening

    def test_proxysql_mysql_port(self, host):
        # 6033 is the default MySQL client-facing interface
        assert host.socket("tcp://0.0.0.0:6033").is_listening

    def test_proxysql_stats_port(self, host):
        # 6070 is commonly used for stats/prometheus exporters
        assert host.socket("tcp://0.0.0.0:6070").is_listening

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
        assert oct(datadir.mode) in ['0o755', '0o750']  # Depending on packaging

    def test_config_file(self, host):
        cfg = host.file('/etc/proxysql.cnf')
        assert cfg.exists
        assert cfg.user == 'root'
        assert oct(cfg.mode) in ['0o644', '0o600']  # Should not be world-writable

