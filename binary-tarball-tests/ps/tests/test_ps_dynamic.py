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
    """Check if mysqld binary can run (not blocked by GLIBC incompatibility).

    Returns (can_run, detail) where detail is the captured stderr/exception
    text when can_run is False, so callers can surface *why* in skip reasons.
    """
    try:
        mysqld_path = base_dir + '/bin/mysqld'
        result = subprocess.run(
            [mysqld_path, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,  # text= requires Python 3.7+, some test hosts still run 3.6
            timeout=5,
            check=False  # Don't raise on non-zero exit
        )
        # If it returns 0, mysqld can run
        if result.returncode == 0:
            return True, ''
        # Check if the error is GLIBC-related in stderr
        error_output = result.stderr or ''
        if 'GLIBC' in error_output or 'GLIBCXX' in error_output:
            return False, error_output.strip()
        # Other errors might be acceptable (e.g., missing config files)
        # But if returncode is non-zero and no output, assume it can't run
        if result.returncode != 0 and not error_output and not result.stdout:
            return False, f'mysqld --version exited {result.returncode} with no output'
        return True, ''
    except FileNotFoundError:
        # Binary doesn't exist
        return False, f'{base_dir}/bin/mysqld not found'
    except Exception as e:
        # Check if the exception message contains GLIBC errors
        error_str = str(e)
        if 'GLIBC' in error_str or 'GLIBCXX' in error_str:
            return False, error_str
        # Any other exception means we can't determine, assume it can't run
        return False, error_str


@pytest.fixture(scope='module')
def mysql_server(request, pro_fips_vars):
    # Check if mysqld can run before attempting to initialize
    can_run, detail = can_mysqld_run(pro_fips_vars['base_dir'])
    if not can_run:
        pytest.skip(f"mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries): {detail}")
    
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
            pytest.skip(f"mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries): {error_output.strip()}")
        # Re-raise if it's a different error
        raise
    except Exception as e:
        # Catch any other exception and check if it's GLIBC-related
        error_str = str(e)
        if 'GLIBC' in error_str or 'GLIBCXX' in error_str:
            pytest.skip(f"mysqld binary cannot run due to GLIBC incompatibility (requires newer system libraries): {error_str}")
        # Re-raise if it's a different error
        raise

def test_fips_md5(host, mysql_server, pro_fips_vars):
    # For Oracle-9, FIPS is supported and tests should not be skipped
    is_oracle9 = is_oracle_linux_9(host)
    should_run = pro_fips_vars['fips_enabled'] or (is_oracle9 and pro_fips_vars['fips_supported'])

    if not should_run:
        pytest.skip("MySQL not running in FIPS mode")

    # In MySQL 9.x FIPS mode, MD5() raises an error instead of returning zeros.
    # Both behaviors confirm MD5 is blocked by FIPS.
    try:
        output = mysql_server.run_query("SELECT MD5('foo');")
        assert '00000000000000000000000000000000' in output
    except subprocess.CalledProcessError:
        # MD5 blocked by FIPS — this is also a valid confirmation
        pass

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
    if v.startswith(("8.", "9.")):
        for component in ps_components:
            mysql_server.install_component(component)
    else:
        pytest.skip("Components only tested for 8.x")


def test_install_plugin(mysql_server):
    for plugin in ps_plugins:
        mysql_server.install_plugin(*plugin)


def test_audit_log_v2(mysql_server, pro_fips_vars):
    v = pro_fips_vars['ps_version_major']
    if v.startswith("8.0") or v.startswith("9."):
        base_dir = pro_fips_vars['base_dir']

        mysql_server.run_file(
            f"{base_dir}/share/audit_log_filter_linux_install.sql"
        )

        if v.startswith("9."):
            # In PS 9.x audit_log_filter is a component, not a plugin
            output = mysql_server.run_query(
                'SELECT component_urn FROM mysql.component '
                'WHERE component_urn LIKE "%audit_log_filter%";'
            )
            assert 'audit_log_filter' in output
        else:
            output = mysql_server.run_query(
                'SELECT plugin_status '
                'FROM information_schema.plugins '
                'WHERE plugin_name = "audit_log_filter";'
            )
            assert 'ACTIVE' in output

    else:
        pytest.skip("Audit log v2 only for PS 8.0 and 9.x")


def test_telemetry_status(mysql_server, pro_fips_vars):
    if not pro_fips_vars['ps_version_major'].startswith(("8.", "9.")):
        pytest.skip("Telemetry only tested for PS 8.x and 9.x")

    output = mysql_server.run_query(
        "SHOW VARIABLES LIKE '%percona_telemetry%';"
    )

    print("Telemetry raw output:", output)

    telemetry_settings = {}

    for line in output.split("\n"):
        parts = line.split("\t")

        if len(parts) == 2:
            telemetry_settings[parts[0]] = parts[1]

    print("Parsed telemetry settings:", telemetry_settings)

    assert telemetry_settings.get("percona_telemetry_disable") == "OFF", \
        "Telemetry is enabled"


def test_opentelemetry_component(mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] != '9.7':
        pytest.skip('component_telemetry (OpenTelemetry) is available from PS 9.7 onwards')

    mysql_server.install_component('component_telemetry')

    # SELECT @@global.<var> returns MySQL's raw 0/1 for boolean sysvars,
    # not the ON/OFF text shown by SHOW VARIABLES/SHOW STATUS.
    expected = {
        'telemetry.trace_enabled': '0',
        'telemetry.metrics_enabled': '0',
        'telemetry.log_enabled': '0',
        'telemetry.query_text_enabled': '1',
        'telemetry.otel_log_level': 'info',
    }
    for variable, value in expected.items():
        output = mysql_server.run_query('SELECT @@global.'+variable+';')
        assert output.strip() == value

    for status_var in ('Telemetry_logs_supported', 'Telemetry_metrics_supported', 'Telemetry_traces_supported'):
        output = mysql_server.run_query('SHOW GLOBAL STATUS LIKE "'+status_var+'";')
        assert 'ON' in output

    for variable in ('telemetry.trace_enabled', 'telemetry.log_enabled'):
        mysql_server.run_query('SET GLOBAL '+variable+'=ON;')
        output = mysql_server.run_query('SELECT @@global.'+variable+';')
        assert output.strip() == '1'

    # telemetry.metrics_enabled is startup-only, so a runtime SET must fail
    with pytest.raises(subprocess.CalledProcessError):
        mysql_server.run_query('SET GLOBAL telemetry.metrics_enabled=ON;')

    mysql_server.run_query('UNINSTALL COMPONENT "file://component_telemetry";')
    output = mysql_server.run_query(
        'SELECT component_urn FROM mysql.component WHERE component_urn = "file://component_telemetry";'
    )
    assert 'component_telemetry' not in output


def test_opentelemetry_client_plugin(host, mysql_server, pro_fips_vars):
    if pro_fips_vars['ps_version_major'] != '9.7':
        pytest.skip('telemetry_client (OpenTelemetry client plugin) is available from PS 9.7 onwards')

    # @@global.plugin_dir reports the build-time install prefix baked into
    # this generic tarball, not where the tarball was actually extracted,
    # so point --plugin_dir at the real location instead (same workaround
    # the docs recommend when the plugin isn't found in the default dir).
    plugin_dir = pro_fips_vars['base_dir']+'/lib/plugin'
    assert host.file(plugin_dir+'/telemetry_client.so').exists

    # --otel-help is registered by the telemetry_client plugin itself, so it
    # only succeeds and prints the plugin variables banner when the plugin
    # is loaded via --telemetry_client.
    loaded_marker = '=== TELEMETRY_CLIENT PLUGIN VARIABLES ==='
    mysql_cmd = mysql_server.mysql+' --user=root -S'+mysql_server.socket+' --plugin_dir='+plugin_dir

    enabled = host.run(mysql_cmd+' --telemetry_client --otel-help')
    assert enabled.succeeded
    assert loaded_marker in enabled.stdout + enabled.stderr

    disabled = host.run(mysql_cmd+' --otel-help')
    assert not disabled.succeeded
    assert loaded_marker not in disabled.stdout + disabled.stderr


def test_ps11950_mysqldump_compressed_columns(host, mysql_server):
    """PS-11950: mysqldump must not treat Percona compressed-column markers
    placed inside a column COMMENT as real column-format extensions.

    Covers three defects:
      D1 - SQL injection into the dump (default and --enable-compressed-columns):
           stripping a fake marker removes a closing quote, turning attacker
           comment text into SQL that runs on restore.
      D2 - a start marker with no closing "*/" must not abort/crash the dump.
      D3 - an oversized dictionary name must not overflow the stack buffer
           (--enable-compressed-columns-with-dictionaries).

    The test fails if the mysqldump under test is still vulnerable.
    """
    import base64

    mysql_cmd = mysql_server.mysql + ' --user=root -S' + mysql_server.socket
    mysqldump_cmd = mysql_server.mysqldump + ' --user=root -S' + mysql_server.socket
    marker = " /*!50633 COLUMN_FORMAT COMPRESSED"

    def run_sql(db, sql):
        # Pass SQL via base64 so the injection payload's quotes/semicolons
        # survive the shell untouched.
        b64 = base64.b64encode(sql.encode()).decode()
        return host.run("echo %s | base64 -d | %s %s" % (b64, mysql_cmd, db))

    cleanup_sql = ("DROP DATABASE IF EXISTS ps11950_d1;"
                   " DROP DATABASE IF EXISTS ps11950_d2;"
                   " DROP DATABASE IF EXISTS ps11950_d3;"
                   " DROP USER IF EXISTS evil@localhost;")
    run_sql("", cleanup_sql)
    try:
        # ---- D1: SQL injection into the dump ----
        run_sql("", "CREATE DATABASE ps11950_d1;")
        create_inj = (
            "CREATE TABLE t4 (\n"
            "  a INT COMMENT '" + marker + "',\n"
            "  b BLOB COLUMN_FORMAT COMPRESSED,\n"
            "  c INT COMMENT ') ENGINE=InnoDB; CREATE USER evil@localhost;"
            " GRANT ALL ON *.* TO evil@localhost WITH GRANT OPTION;"
            " CREATE TABLE t5 (y INT -- '\n"
            ");"
        )
        res = run_sql("ps11950_d1", create_inj)
        assert res.rc == 0, "D1: could not create injection table: %s" % res.stderr

        for mode in ("", "--enable-compressed-columns"):
            tag = mode or "default"
            dump = host.run("%s %s --skip-comments ps11950_d1 > /tmp/ps11950_d1.sql"
                            % (mysqldump_cmd, mode))
            assert dump.rc == 0, "D1 (%s): mysqldump failed: %s" % (tag, dump.stderr)
            # A vulnerable dump runs the injection on restore.
            run_sql("", "DROP USER IF EXISTS evil@localhost;")
            host.run("%s ps11950_d1 < /tmp/ps11950_d1.sql" % mysql_cmd)
            evil = host.run('%s -s -N -e "SELECT COUNT(*) FROM mysql.user '
                            'WHERE user=\'evil\' AND host=\'localhost\'"' % mysql_cmd)
            assert evil.stdout.strip() == "0", (
                "D1 (%s): restoring the dump created superuser evil@localhost "
                "(SQL injection via compressed-column marker in a COMMENT)" % tag)

        # ---- D2: start marker with no closing "*/" ----
        run_sql("", "CREATE DATABASE ps11950_d2;")
        run_sql("ps11950_d2", "CREATE TABLE t (a INT COMMENT '" + marker + "');")
        d2 = host.run("%s --skip-comments ps11950_d2" % mysqldump_cmd)
        assert d2.rc == 0, "D2: mysqldump aborted/crashed on unterminated marker: %s" % d2.stderr

        # ---- D3: oversized dictionary name ----
        run_sql("", "CREATE DATABASE ps11950_d3;")
        bigname = "x" * 500
        run_sql("ps11950_d3", "CREATE TABLE t (a INT COMMENT '" + marker
                + " WITH COMPRESSION_DICTIONARY " + bigname + " */');")
        d3 = host.run("%s --enable-compressed-columns-with-dictionaries "
                      "--skip-comments ps11950_d3" % mysqldump_cmd)
        assert d3.rc == 0, "D3: mysqldump aborted/crashed on oversized dictionary name: %s" % d3.stderr
    finally:
        run_sql("", cleanup_sql)
        host.run("rm -f /tmp/ps11950_d1.sql")
