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
    if ps_version_major in ['5.7','5.6']:
        subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install','net-tools'])
    else:
        subprocess.check_call(['docker','exec','--user','root',container_name,'yum','-y','install','net-tools'])
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
        if ps_version_major in ['5.7','5.6']:
            assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+ps_version+', for Linux (x86_64) using  7.0'
            assert host.check_output('mysqld --version') == 'mysqld  Ver '+ps_version+' for Linux on x86_64 (Percona Server (GPL), Release '+ps_version_percona+', Revision '+ps_revision+')'
        else:
            assert host.check_output('mysql --version') == 'mysql  Ver '+ ps_version_upstream + '-' + ps_version_percona +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'
            assert host.check_output('mysqld --version') == '/usr/sbin/mysqld  Ver '+ ps_version_upstream + '-' + ps_version_percona +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'

    def test_process_running(self, host):
        assert host.process.get(user="mysql", comm="mysqld")

    def test_mysql_port_3306(self, host):
        assert host.socket('tcp://127.0.0.1:3306').is_listening

    def test_mysql_port_33060(self, host):
        if ps_version_major in ['5.7','5.6']:
            pytest.skip('X protocol is available from 8.0')
        else:
            assert host.socket('tcp://127.0.0.1:33060').is_listening

    def test_mysql_socket_mysql(self, host):
        assert host.socket('unix:///var/lib/mysql/mysql.sock').is_listening

    def test_mysql_socket_mysqlx(self, host):
        if ps_version_major in ['5.7','5.6']:
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
        assert host.file('/var/lib/mysql').group == 'root'
        assert oct(host.file('/var/lib/mysql').mode) == '0o775'

    def test_mysql_files_permissions(self, host):
        assert host.file('/var/lib/mysql-files').user == 'mysql'
        assert host.file('/var/lib/mysql-files').group == 'mysql'
        assert oct(host.file('/var/lib/mysql-files').mode) == '0o750'

    def test_mysql_keyring_permissions(self, host):
        if ps_version_major == '5.6':
            pytest.skip('mysql-keyring not available in 5.6')
        else:
            assert host.file('/var/lib/mysql-keyring').user == 'mysql'
            assert host.file('/var/lib/mysql-keyring').group == 'mysql'
            assert oct(host.file('/var/lib/mysql-keyring').mode) == '0o750'

    def test_telemetry_disabled(self, host):
        if ps_version_major in ['5.6']:
            pytest.skip('telemetry was added in 5.7, 8.0 and 8.x')
        else:
            assert not host.file('/usr/local/percona/telemetry_uuid').exists

    def test_telemetry_process(self, host):
        # Check if telemetry-agent-supervisor.sh process is not running
        telemetry_supervisor_process = host.process.filter(comm="telemetry-agent-supervisor.sh")
        assert not telemetry_supervisor_process, "/usr/bin/telemetry-agent-supervisor.sh process is running"

        # Check if percona-telemetry-agent process is not running
        telemetry_agent_process = host.process.filter(comm="percona-telemetry-agent")
        assert not telemetry_agent_process, "/usr/bin/percona-telemetry-agent process is running"

    def test_telemetry_agent_dirs(self, host):
        assert host.file("/usr/local/percona/telemetry/").is_directory
        assert host.file("/usr/local/percona/telemetry/").user == 'daemon'
        assert host.file("/usr/local/percona/telemetry/").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/").mode) == '0o755'
        assert host.file("/usr/local/percona/telemetry/history").is_directory
        assert host.file("/usr/local/percona/telemetry/history").user == 'mysql'
        assert host.file("/usr/local/percona/telemetry/history").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/history").mode) == '0o6755'
        assert host.file("/usr/local/percona/telemetry_uuid").is_file
        assert host.file("/usr/local/percona/telemetry_uuid").group == 'mysql'
        assert oct(host.file("/usr/local/percona/telemetry_uuid").mode) == '0o664'
        assert host.file(ps_pillar_dir).is_directory
        assert host.file(ps_pillar_dir).user == 'mysql'
        assert host.file(ps_pillar_dir).group == 'percona-telemetry'
        assert oct(host.file(ps_pillar_dir).mode) == '0o6775'        
