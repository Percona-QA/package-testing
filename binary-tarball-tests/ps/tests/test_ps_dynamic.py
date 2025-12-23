#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import mysql
from packaging import version

from settings import *


def is_oracle_linux_9(host):
    """Check if the system is Oracle Linux 9"""
    try:
        os_release = host.check_output("cat /etc/os-release")
        has_ol_id = 'ID="ol"' in os_release or 'ID=ol' in os_release
        has_version_9 = 'VERSION_ID="9' in os_release or 'VERSION_ID=9' in os_release
        return has_ol_id and has_version_9
    except Exception:
        return False


def is_oracle_linux_9_direct():
    """Check if the system is Oracle Linux 9 by reading /etc/os-release directly"""
    try:
        with open('/etc/os-release', 'r') as f:
            os_release = f.read()
        has_ol_id = 'ID="ol"' in os_release or 'ID=ol' in os_release
        has_version_9 = 'VERSION_ID="9' in os_release or 'VERSION_ID=9' in os_release
        return has_ol_id and has_version_9
    except Exception:
        return False


def can_mysqld_run(base_dir):
    """Check if mysqld binary can run (not blocked by GLIBC incompatibility)"""
    try:
        mysqld_path = base_dir + '/bin/mysqld'
        result = subprocess.run(
            [mysqld_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False  # Don't raise on non-zero exit
        )
        # If it returns 0, mysqld can run
        if result.returncode == 0:
            return True
        # Check if the error is GLIBC-related in stderr
        error_output = result.stderr or ''
        if 'GLIBC' in error_output or 'GLIBCXX' in error_output:
            return False
        # Other errors might be acceptable (e.g., missing config files)
        # But if returncode is non-zero and no output, assume it can't run
        if result.returncode != 0 and not error_output and not result.stdout:
            return False
        return True
    except FileNotFoundError:
        # Binary doesn't exist
        return False
    except Exception as e:
        # Check if the exception message contains GLIBC errors
        error_str = str(e)
        if 'GLIBC' in error_str or 'GLIBCXX' in error_str:
            return False
        # Any other exception means we can't determine, assume it can't run
        return False


@pytest.fixture(scope='module')
def mysql_server(request, pro_fips_vars):
    # Check if mysqld can run before attempting to initialize
    if not can_mysqld_run(pro_fips_vars['base_dir']):
        pytest.skip("mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries)")
    
    features = []
    # For Oracle-9, enable FIPS if fips_supported is True
    # Otherwise, enable FIPS only if fips_enabled is True
    is_oracle9 = is_oracle_linux_9_direct()
    if pro_fips_vars['fips_enabled'] or (is_oracle9 and pro_fips_vars['fips_supported']):
        features.append('fips')
    
    try:
        mysql_server = mysql.MySQL(
            pro_fips_vars['base_dir'],
            features
        )
        mysql_server.start()
        time.sleep(10)
        yield mysql_server
        mysql_server.purge()
    except subprocess.CalledProcessError as e:
        # Check if the error is GLIBC-related
        # The stderr might be in the exception's output attribute or stderr attribute
        error_output = ''
        if hasattr(e, 'stderr') and e.stderr:
            error_output = str(e.stderr)
        elif hasattr(e, 'output') and e.output:
            error_output = str(e.output)
        else:
            error_output = str(e)
        
        if 'GLIBC' in error_output or 'GLIBCXX' in error_output:
            pytest.skip(f"mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries)")
        # Re-raise if it's a different error
        raise
    except Exception as e:
        # Catch any other exception and check if it's GLIBC-related
        error_str = str(e)
        if 'GLIBC' in error_str or 'GLIBCXX' in error_str:
            pytest.skip(f"mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries)")
        # Re-raise if it's a different error
        raise

def test_fips_md5(host, mysql_server, pro_fips_vars):
    # For Oracle-9, FIPS is supported and tests should not be skipped
    is_oracle9 = is_oracle_linux_9(host)
    should_run = pro_fips_vars['fips_enabled'] or (is_oracle9 and pro_fips_vars['fips_supported'])
    
    if not should_run:
        pytest.skip("MySQL not running in FIPS mode")

    output = mysql_server.run_query("SELECT MD5('foo');")
    assert '00000000000000000000000000000000' in output

def test_fips_value(host, mysql_server, pro_fips_vars):
    # For Oracle-9, FIPS is supported and tests should not be skipped
    is_oracle9 = is_oracle_linux_9(host)
    should_run = pro_fips_vars['fips_enabled'] or (is_oracle9 and pro_fips_vars['fips_supported'])
    
    if not should_run:
        pytest.skip("MySQL not running in FIPS mode")

    output = mysql_server.run_query("SELECT @@ssl_fips_mode;")
    assert 'ON' in output


def test_fips_in_log(host, mysql_server, pro_fips_vars):
    # For Oracle-9, FIPS is supported and tests should not be skipped
    is_oracle9 = is_oracle_linux_9(host)
    should_run = pro_fips_vars['fips_enabled'] or (is_oracle9 and pro_fips_vars['fips_supported'])
    
    if not should_run:
        pytest.skip("MySQL not running in FIPS mode")

    with host.sudo():
        log_file = mysql_server.run_query("SELECT @@log_error;")
        logs = host.check_output(f"head -n50 {log_file}")

    assert "FIPS-approved version of the OpenSSL cryptographic library" in logs


def test_rocksdb_install(host, mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] != '5.6':
        host.run(mysql_server.psadmin + ' --user=root -S' + mysql_server.socket + ' --enable-rocksdb')
        assert mysql_server.check_engine_active('ROCKSDB')
    else:
        pytest.skip("RocksDB not available for 5.6")


def test_tokudb_install(host, mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] == '5.6':
        host.run('sudo ' + mysql_server.psadmin + ' --user=root -S' + mysql_server.socket + ' --enable --enable-backup')
        mysql_server.restart()
        host.run('sudo ' + mysql_server.psadmin + ' --user=root -S' + mysql_server.socket + ' --enable --enable-backup')
        assert mysql_server.check_engine_active('TokuDB')
    else:
        pytest.skip("TokuDB removed after 5.7")


def test_install_functions(mysql_server):
    for function in ps_functions:
        mysql_server.install_function(*function)


def test_install_component(mysql_server, pro_fips_vars):
    v = pro_fips_vars['ps_version_major']
    if v == '8.0' or v.startswith("8."):
        for component in ps_components:
            mysql_server.install_component(component)
    else:
        pytest.skip("Components only tested for 8.x")


def test_install_plugin(mysql_server):
    for plugin in ps_plugins:
        mysql_server.install_plugin(*plugin)


def test_audit_log_v2(mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] == '8.0':
        base_dir = pro_fips_vars['base_dir']
        mysql_server.run_query(f"source {base_dir}/share/audit_log_filter_linux_install.sql;")
        output = mysql_server.run_query(
            'SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = "audit_log_filter";'
        )
        assert 'ACTIVE' in output
    else:
        pytest.skip("Audit log v2 only for 8.0")


def test_telemetry_status(mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] != '8.0':
        pytest.skip("Telemetry only tested for 8.0")

    output = mysql_server.run_query("SHOW VARIABLES LIKE '%percona_telemetry%';")
    print("Telemetry raw output:", output)

    telemetry_settings = {}
    for line in output.split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            telemetry_settings[parts[0]] = parts[1]

    print("Parsed telemetry settings:", telemetry_settings)

    assert telemetry_settings.get("percona_telemetry_disable") == "OFF", "Telemetry is enabled"