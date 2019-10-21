#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time

from settings import *

container_name = 'ps-docker-test-dynamic'

def install_function(host, fname, soname, return_type):
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "CREATE FUNCTION '+fname+' RETURNS '+return_type+' SONAME \''+soname+'\';"')
    assert cmd.succeeded
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT name FROM mysql.func WHERE dl = \''+soname+'\';"')
    assert cmd.succeeded
    assert fname in cmd.stdout

def install_plugin(host, pname, soname):
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "INSTALL PLUGIN '+pname+' SONAME \''+soname+'\';"')
    assert cmd.succeeded
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = \''+pname+'\';"')
    assert cmd.succeeded
    assert 'ACTIVE' in cmd.stdout

@pytest.fixture(scope='class')
def host(request):
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_TOKUDB=1', '-e', 'INIT_ROCKSDB=1','-d', docker_image]).decode().strip()
    time.sleep(20)
    # return a testinfra connection to the container
    yield testinfra.get_host("docker://root@" + docker_id)
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def test_rocksdb_installed(host):
    #cmd = host.run('ps-admin --enable-rocksdb --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock')
    #assert cmd.succeeded
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'ROCKSDB\';"')
    assert cmd.succeeded
    assert 'YES' in cmd.stdout

def test_tokudb_installed(host):
    #cmd = host.run('ps-admin --enable-tokudb --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock')
    #assert cmd.succeeded
    cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'TokuDB\';"')
    assert cmd.succeeded
    assert 'YES' in cmd.stdout

def test_install_functions(host):
    for function in ps_functions:
        install_function(host, function[0], function[1], function[2])

def test_install_plugin(host):
    for plugin in ps_plugins:
        install_plugin(host, plugin[0], plugin[1])
