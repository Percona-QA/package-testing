#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-dynamic'

@pytest.fixture(scope='module')
def host():
    if ps_version_major != "8.0" and not re.match(r"^8\.[1-9]$", ps_version_major) and not re.match(r"^9\.[0-9]+$", ps_version_major):
        docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_TOKUDB=1', '-e', 'INIT_ROCKSDB=1', '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport','-d', docker_image]).decode().strip()
    else:
        docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_ROCKSDB=1', '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport', '-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestDynamic:
    def test_rocksdb_installed(self, host):
        if ps_version_major not in ['5.6']:
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'ROCKSDB\';"')
            assert cmd.succeeded
            assert 'YES' in cmd.stdout
        else:
            pytest.skip('RocksDB is available from 5.7!')

    def test_tokudb_installed(self, host):
        if ps_version_major != "8.0" and not re.match(r"^8\.[1-9]$", ps_version_major) and not re.match(r"^9\.[0-9]+$", ps_version_major):
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'TokuDB\';"')
            assert cmd.succeeded
            assert 'YES' in cmd.stdout
        else:
            pytest.skip('TokuDB is available in 5.7!')

    @pytest.mark.parametrize("fname,soname,return_type", ps_functions)
    def test_install_functions(self, host, fname, soname, return_type):
        cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "CREATE FUNCTION '+fname+' RETURNS '+return_type+' SONAME \''+soname+'\';"')
        assert cmd.succeeded
        cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT name FROM mysql.func WHERE dl = \''+soname+'\';"')
        assert cmd.succeeded
        assert fname in cmd.stdout

    @pytest.mark.parametrize("pname,soname", ps_plugins)
    def test_install_plugin(self, host, pname, soname):
        cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "INSTALL PLUGIN '+pname+' SONAME \''+soname+'\';"')
        assert cmd.succeeded
        cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = \''+pname+'\';"')
        assert cmd.succeeded
        assert 'ACTIVE' in cmd.stdout

    @pytest.mark.parametrize("cmpt", ps_components)
    def test_install_component(self, host, cmpt):
        if ps_version_major == '8.0' or re.match(r'^8\.[1-9]$', ps_version_major) or re.match(r"^9\.[0-9]+$", ps_version_major):
            if cmpt == 'file://component_masking_functions':
                host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "UNINSTALL PLUGIN data_masking;"')
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "INSTALL component \''+cmpt+'\';"')
            assert cmd.succeeded
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT component_urn from mysql.component WHERE component_urn = \''+cmpt+'\';"')
            assert cmd.succeeded
            assert cmpt in cmd.stdout
        else:
            pytest.mark.skip('Components are available from 8.0 onwards')

    def test_install_audit_log_v2(self, host):
        if ps_version_major in ['8.0']:
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "source /usr/share/mysql/audit_log_filter_linux_install.sql;"')
            assert cmd.succeeded
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = \'audit_log_filter\';"')
            assert cmd.succeeded
            assert 'ACTIVE' in cmd.stdout
        else:
            pytest.mark.skip('Components are available from 8.0 onwards')

    def test_telemetry_enabled(self, host):
        if ps_version_major in ['5.6']:
            pytest.skip('telemetry was added after 5.7')
        else:
            assert host.file('/usr/local/percona/telemetry_uuid').exists
            assert host.file('/usr/local/percona/telemetry_uuid').contains('PRODUCT_FAMILY_PS')
            assert host.file('/usr/local/percona/telemetry_uuid').contains('instanceId:[0-9a-fA-F]\\{8\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{12\\}$')

    def test_ps11950_mysqldump_compressed_columns(self, host):
        """PS-11950: mysqldump must not treat Percona compressed-column markers
        placed inside a column COMMENT as real column-format extensions
        (SQL injection into the dump, dump crash, stack buffer overflow)."""
        import base64

        if ps_version_major in ['5.6', '5.7']:
            pytest.skip('compressed-column mysqldump handling test targets 8.x+')

        mysql_cmd = ("mysql --user=root --password=" + ps_pwd
                     + " -S/var/lib/mysql/mysql.sock")
        mysqldump_cmd = ("mysqldump --user=root --password=" + ps_pwd
                         + " -S/var/lib/mysql/mysql.sock")
        marker = " /*!50633 COLUMN_FORMAT COMPRESSED"

        def run_sql(db, sql):
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
