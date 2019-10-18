#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time

from settings import *

# scope='session' uses the same container for all the tests;
# scope='function' uses a new container per test function.
@pytest.fixture(scope='class')
def host(request):
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', 'ps-docker-test', '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    time.sleep(20)
    # return a testinfra connection to the container
    yield testinfra.get_host("docker://" + docker_id)
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def test_packages(host):
    # 'host' now binds to the container
    for package in ps_packages:
        assert host.package(package).is_installed
        assert host.package(package).version == ps_version_upstream

def test_binaries_exist(host):
    for binary in ps_binaries:
        assert host.file(binary).exists
        assert oct(host.file(binary).mode) == '0o755'

def test_binaries_version(host):
    assert host.check_output('mysql --version') == 'mysql  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'
    assert host.check_output('mysqld --version') == '/usr/sbin/mysqld  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'

def test_process_running(host):
    assert host.process.get(user="mysql", comm="mysqld")

def test_mysql_is_listening(host):
    assert host.socket('tcp://127.0.0.1:3306').is_listening
