#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import mysql

from settings import *

@pytest.fixture(scope='module')
def mysql_server(request):
    mysql_server = mysql.MySQL(base_dir)
    mysql_server.start()
    time.sleep(10)
    yield mysql_server
    mysql_server.purge()

def test_rocksdb_install(host, mysql_server):
    if ps_version_major not in ['5.6']:
        host.run(mysql_server.psadmin+' --user=root -S'+mysql_server.socket+' --enable-rocksdb')
        assert mysql_server.check_engine_active('ROCKSDB')
    else:
        pytest.skip('RocksDB is available from 5.7!')

def test_tokudb_install(host, mysql_server):
    if ps_version_major in ['5.6']:
        host.run('sudo '+mysql_server.psadmin+' --user=root -S'+mysql_server.socket+' --enable --enable-backup')
        mysql_server.restart()
        host.run('sudo '+mysql_server.psadmin+' --user=root -S'+mysql_server.socket+' --enable --enable-backup')
        assert mysql_server.check_engine_active('TokuDB')
    else:
        pytest.skip('TokuDB is skipped from 5.7!')

def test_install_functions(mysql_server):
    for function in ps_functions:
        mysql_server.install_function(function[0], function[1], function[2])

def test_install_component(mysql_server):
    for component in ps_components:
        mysql_server.install_component(component)

def test_install_plugin(mysql_server):
    for plugin in ps_plugins:
        mysql_server.install_plugin(plugin[0], plugin[1])

