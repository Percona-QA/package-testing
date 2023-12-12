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
    if ps_version_major in ['8.0', '8.1']:
        for component in ps_components:
            mysql_server.install_component(component)
    else:
        pytest.skip('Component is checked from 8.0!')

def test_install_plugin(mysql_server):
    for plugin in ps_plugins:
        mysql_server.install_plugin(plugin[0], plugin[1])

def test_audit_log_v2(mysql_server):
    if ps_version_major in ['8.0']:
        query='source {}/share/audit_log_filter_linux_install.sql;'.format(base_dir)
        mysql_server.run_query(query)
        query = 'SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = "audit_log_filter";'
        output = mysql_server.run_query(query)
        assert 'ACTIVE' in output
    else:
        pytest.skip('audit_log_v2 is checked from 8.0!')

