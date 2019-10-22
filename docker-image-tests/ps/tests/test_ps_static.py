#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time

from settings import *

container_name = 'ps-docker-test-static'

@pytest.fixture(scope='module')
def host(request):
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    subprocess.check_call(['docker','exec','--user','root',container_name,'yum','install','-y','net-tools'])
    time.sleep(20)
    # return a testinfra connection to the container
    yield testinfra.get_host("docker://root@" + docker_id)
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def test_packages(host):
    for package in ps_packages:
        assert host.package(package).is_installed
        assert host.package(package).version == ps_version_upstream

def test_binaries_exist(host):
    for binary in ps_binaries:
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

def test_binaries_version(host):
    if ps_version_major in ['5.7','5.6']:
        assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+ps_version+', for Linux (x86_64) using  6.2'
        assert host.check_output('mysqld --version') == 'mysqld  Ver '+ps_version+' for Linux on x86_64 (Percona Server (GPL), Release '+ps_version_percona+', Revision '+ps_revision+')'
    else:
        assert host.check_output('mysql --version') == 'mysql  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'
        assert host.check_output('mysqld --version') == '/usr/sbin/mysqld  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'

def test_process_running(host):
    assert host.process.get(user="mysql", comm="mysqld")

def test_mysql_port_3306(host):
    assert host.socket('tcp://127.0.0.1:3306').is_listening

def test_mysql_port_33060(host):
    if ps_version_major in ['5.7','5.6']:
        pytest.skip('X protocol is available from 8.0')
    else:
        assert host.socket('tcp://127.0.0.1:33060').is_listening

def test_mysql_socket_mysql(host):
    assert host.socket('unix:///var/lib/mysql/mysql.sock').is_listening

def test_mysql_socket_mysqlx(host):
    if ps_version_major in ['5.7','5.6']:
        pytest.skip('X protocol is available from 8.0')
    else:
        assert host.socket('unix:///var/lib/mysql/mysqlx.sock').is_listening

def test_mysql_user(host):
    assert host.user('mysql').exists
    assert host.user('mysql').uid == 1001
    assert host.user('mysql').gid == 1001
    assert 'mysql' in host.user('mysql').groups

def test_mysql_group(host):
    assert host.group('mysql').exists
    assert host.group('mysql').gid == 1001

def test_datadir_permissions(host):
    assert host.file('/var/lib/mysql').user == 'mysql'
    assert host.file('/var/lib/mysql').group == 'root'
    assert oct(host.file('/var/lib/mysql').mode) == '0o775'

def test_mysql_files_permissions(host):
    assert host.file('/var/lib/mysql-files').user == 'mysql'
    assert host.file('/var/lib/mysql-files').group == 'mysql'
    assert oct(host.file('/var/lib/mysql-files').mode) == '0o750'

def test_mysql_keyring_permissions(host):
    if ps_version_major == '5.6':
        pytest.skip('mysql-keyring not available in 5.6')
    else:
        assert host.file('/var/lib/mysql-keyring').user == 'mysql'
        assert host.file('/var/lib/mysql-keyring').group == 'mysql'
        assert oct(host.file('/var/lib/mysql-keyring').mode) == '0o750'
