#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-dynamic'

@pytest.fixture(scope='module')
def host():
    if ps_version_major not in ['8.0']:
        docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_TOKUDB=1', '-e', 'INIT_ROCKSDB=1','-d', docker_image]).decode().strip()
    else:
        docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_ROCKSDB=1','-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
#    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestDynamic:
    def test_rocksdb_installed(self, host):
        if ps_version_major not in ['5.6']:
            cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'ROCKSDB\';"')
            assert cmd.succeeded
            assert 'YES' in cmd.stdout
        else:
            pytest.skip('RocksDB is available from 5.7!')

    def test_tokudb_installed(self, host):
        if ps_version_major not in ['8.0']:
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
        if ps_version_major in ['8.0']:
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
