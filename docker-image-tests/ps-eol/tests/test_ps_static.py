#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e',
         'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport',
         '-e', 'PERCONA_TELEMETRY_DISABLE=1', '-d', docker_image]).decode().strip()
    subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install','net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestMysqlEnvironment:
    @pytest.mark.parametrize("pkg_name", ps_packages)
    def test_packages(self, host, pkg_name):
        assert host.package(pkg_name).is_installed
        assert host.package(pkg_name).version == ps_version_upstream

    @pytest.mark.parametrize("binary", ps_binaries)
    def test_binaries_exist(self, host, binary):
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

    def test_binaries_version(self, host):
        assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+ps_version+', for Linux (x86_64) using  7.0'
        assert host.check_output('mysqld --version') == 'mysqld  Ver '+ps_version+' for Linux on x86_64 (Percona Server (GPL), Release '+ps_version_percona+', Revision '+ps_revision+')'

    def test_process_running(self, host):
        assert host.process.get(user="mysql", comm="mysqld")

    def test_mysql_port_3306(self, host):
        assert host.socket('tcp://127.0.0.1:3306').is_listening

    def test_mysql_socket_mysql(self, host):
        assert host.socket('unix:///var/lib/mysql/mysql.sock').is_listening

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups

    def test_mysql_group(self, host):
        assert host.group('mysql').exists
        assert host.group('mysql').gid == 1001

    def test_datadir_permissions(self, host):
        assert host.file('/var/lib/mysql').user == 'mysql'
        assert host.file('/var/lib/mysql').group == 'root'
        assert oct(host.file('/var/lib/mysql').mode) == '0o775'

    def test_mysql_files_permissions(self, host):
        assert host.file('/var/lib/mysql-files').user == 'mysql'
        assert host.file('/var/lib/mysql-files').group == 'mysql'
        assert oct(host.file('/var/lib/mysql-files').mode) == '0o750'

    def test_mysql_keyring_permissions(self, host):
        assert host.file('/var/lib/mysql-keyring').user == 'mysql'
        assert host.file('/var/lib/mysql-keyring').group == 'mysql'
        assert oct(host.file('/var/lib/mysql-keyring').mode) == '0o750'

    def test_telemetry_disabled(self, host):
        assert not host.file('/usr/local/percona/telemetry_uuid').exists
