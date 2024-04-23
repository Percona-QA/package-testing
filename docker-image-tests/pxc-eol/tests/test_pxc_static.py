#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'pxc-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd,
         '-e', 'PERCONA_TELEMETRY_DISABLE=1',
         '-d', docker_image]).decode().strip()
    exec_command = ['microdnf', 'install', 'net-tools']
    subprocess.check_call(['docker','exec','--user','root',container_name] + exec_command)
    time.sleep(80)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestMysqlEnvironment:
    @pytest.mark.parametrize("pkg_name,pkg_version", pxc_packages)
    def test_packages(self, host, pkg_name, pkg_version):
        assert host.package(pkg_name).is_installed
        assert host.package(pkg_name).version == pkg_version

    @pytest.mark.parametrize("binary", pxc_binaries)
    def test_binaries_exist(self, host, binary):
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

    def test_mysql_version(self, host):
        assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+pxc_version+', for Linux (x86_64) using  7.0'

    def test_mysqld_version(self, host):
        assert host.check_output('mysqld --version') == 'mysqld  Ver '+pxc57_server_version_norel+' for Linux on x86_64 (Percona XtraDB Cluster (GPL), Release rel'+pxc57_server_release+', Revision '+pxc_revision+', WSREP version '+ pxc_wsrep_version +', wsrep_'+ pxc_wsrep_version +')'

    def test_process_running(self, host):
        assert host.process.get(user="mysql", comm="mysqld")

    def test_mysql_port_3306(self, host):
        assert host.socket('tcp://0.0.0.0:3306').is_listening

    def test_mysql_port_4567(self, host):
        assert host.socket('tcp://0.0.0.0:4567').is_listening

    def test_mysql_port_33060(self, host):
        if pxc_version_major in ['5.7','5.6']:
            pytest.skip('X protocol is available from 8.0')
        else:
            assert host.socket('tcp://0.0.0.0:33060').is_listening

    def test_mysql_socket_mysql(self, host):
        assert host.socket('unix:///tmp/mysql.sock').is_listening

    def test_mysql_socket_mysqlx(self, host):
        if pxc_version_major in ['5.7','5.6']:
            pytest.skip('X protocol is available from 8.0')
        else:
            assert host.socket('unix:///var/lib/mysql/mysqlx.sock').is_listening

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
        assert host.file('/var/lib/mysql').group == 'mysql'
        assert oct(host.file('/var/lib/mysql').mode) == '0o775'

    def test_mysql_files_permissions(self, host):
        assert host.file('/var/lib/mysql-files').user == 'mysql'
        assert host.file('/var/lib/mysql-files').group == 'mysql'
        assert oct(host.file('/var/lib/mysql-files').mode) == '0o750'

    def test_mysql_keyring_permissions(self, host):
        if pxc_version_major == '5.6':
            pytest.skip('mysql-keyring not available in 5.6')
        else:
            assert host.file('/var/lib/mysql-keyring').user == 'mysql'
            assert host.file('/var/lib/mysql-keyring').group == 'mysql'
            assert oct(host.file('/var/lib/mysql-keyring').mode) == '0o750'

    def test_telemetry_disabled(self, host):
        if pxc_version_major in ['5.7','5.6']:
            pytest.skip('telemetry was added in 8.0')
        else:
            assert not host.file('/usr/local/percona/telemetry_uuid').exists
