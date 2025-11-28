#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import mysql
from packaging import version

from settings import *



@pytest.fixture(scope='module')
def mysql_server(request,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    features=[]
    if pro and fips_supported:
        features.append('fips')
    mysql_server = mysql.MySQL(base_dir, features)
    mysql_server.start()
    time.sleep(10)
    yield mysql_server
    mysql_server.purge()

def test_fips_md5(host, mysql_server,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    debug = pro_fips_vars['debug']

    if pro and fips_supported:
        query="SELECT MD5('foo');"
        output = mysql_server.run_query(query)
        assert '00000000000000000000000000000000' in output
    else:
        pytest.skip("This test is only for PRO tarballs. Skipping")

def test_fips_value(host,mysql_server,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    if pro and fips_supported:
        query="select @@ssl_fips_mode;"
        output = mysql_server.run_query(query)
        assert 'ON' in output
    else:
        pytest.skip("This test is only for PRO tarballs. Skipping")

def test_fips_in_log(host, mysql_server,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    if pro and fips_supported:
        with host.sudo():
            query="SELECT @@log_error;"
            error_log = mysql_server.run_query(query)
            logs=host.check_output(f'head -n30 {error_log}')
            assert "A FIPS-approved version of the OpenSSL cryptographic library has been detected in the operating system with a properly configured FIPS module available for loading. Percona Server for MySQL will load this module and run in FIPS mode." in logs
    else:
        pytest.skip("This test is only for PRO tarballs. Skipping")

def test_rocksdb_install(host, mysql_server,pro_fips_vars):
    ps_version_major = pro_fips_vars['ps_version_major']
    if ps_version_major not in ['5.6']:
        host.run(mysql_server.psadmin+' --user=root -S'+mysql_server.socket+' --enable-rocksdb')
        assert mysql_server.check_engine_active('ROCKSDB')
    else:
        pytest.skip('RocksDB is available from 5.7!')

def test_tokudb_install(host, mysql_server,pro_fips_vars):
    ps_version_major = pro_fips_vars['ps_version_major']
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

def test_install_component(mysql_server,pro_fips_vars):
    ps_version_major = pro_fips_vars['ps_version_major']
    if ps_version_major == '8.0' or re.match(r'^8\.[1-9]$', ps_version_major):
        for component in ps_components:
            mysql_server.install_component(component)
    else:
        pytest.skip('Component is checked from 8.0!')

def test_install_plugin(mysql_server):
    for plugin in ps_plugins:
        mysql_server.install_plugin(plugin[0], plugin[1])

def test_audit_log_v2(mysql_server,pro_fips_vars):
    ps_version_major = pro_fips_vars['ps_version_major']
    if ps_version_major in ['8.0']:
        query='source {}/share/audit_log_filter_linux_install.sql;'.format(base_dir)
        mysql_server.run_query(query)
        query = 'SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = "audit_log_filter";'
        output = mysql_server.run_query(query)
        assert 'ACTIVE' in output
    else:
        pytest.skip('audit_log_v2 is checked from 8.0!')

def test_telemetry_status(mysql_server,pro_fips_vars):
    ps_version_major = pro_fips_vars['ps_version_major']
    if ps_version_major in ['8.0']:
        # Fetch telemetry settings
        query = "SHOW VARIABLES LIKE '%percona_telemetry%';"
        telemetry_vars = mysql_server.run_query(query)

        # Debug: Print the raw output for inspection
        print("Telemetry Query Output:", telemetry_vars)

        # Convert the output to a dictionary
        telemetry_settings = {}
        lines = telemetry_vars.split('\n')
        for line in lines:
            parts = line.split('\t')
            if len(parts) == 2:
                key, value = parts
                telemetry_settings[key] = value
            else:
                print(f"Skipping line due to insufficient data: {line}")

        # Debug: Print the parsed telemetry settings
        print("Parsed Telemetry Settings:", telemetry_settings)

        # Check if telemetry is disabled
        assert telemetry_settings.get('percona_telemetry_disable') == 'OFF', "Telemetry is enabled"

    else:
        pytest.skip('telemetry agent is checked from 8.0!')
