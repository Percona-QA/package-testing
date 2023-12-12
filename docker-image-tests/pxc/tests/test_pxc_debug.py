#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *

docker_acc = os.getenv('DOCKER_ACC')
container_name = 'pxc-docker-test-static3'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd, '-e', 'PERCONA_TELEMETRY_DISABLE=1', '-d', docker_image_debug]).decode().strip()
    if pxc_version_major in ['8.0','5.7','5.6']:
        exec_command = ['microdnf', 'install', 'net-tools']
    else:
         exec_command = ['yum', 'install', '-y', 'net-tools']
    subprocess.check_call(['docker','exec','--user','root',container_name] + exec_command)
    time.sleep(80)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestMysqlEnvironment:
    @pytest.mark.parametrize("pkg_name,pkg_version", pxc_packages)
    def test_packages(self, host, pkg_name, pkg_version):
        assert host.package(pkg_name).is_installed
        assert host.package(pkg_name).version == pkg_version

    @pytest.mark.skipif(docker_acc == "perconalab", reason="Skipping tests in 'testing' repo")
    def test_mysql_version(self, host):
        if pxc_version_major in ['5.7','5.6']:
            assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+pxc57_client_version+', for Linux (x86_64) using  7.0'
        else:
            assert host.check_output('mysql --version') == 'mysql  Ver '+ pxc_version +' for Linux on x86_64 (Percona XtraDB Cluster (GPL), Release rel'+ pxc_rel +', Revision '+ pxc_revision +', WSREP version '+ pxc_wsrep_version +')'

    @pytest.mark.skipif(docker_acc == "perconalab", reason="Skipping tests in 'testing' repo")
    def test_mysqld_version(self, host):
        if pxc_version_major in ['5.7','5.6']:
            assert host.check_output('mysqld --version') == '/usr/sbin/mysqld-ps  Ver '+pxc57_server_version_norel+' for Linux on x86_64 (Percona XtraDB Cluster (GPL), Release '+pxc57_server_release+', Revision '+pxc_revision+', WSREP version '+ pxc_wsrep_version +', wsrep_'+ pxc_wsrep_version +')'
        else:
            assert host.check_output('mysqld --version') == '/usr/sbin/mysqld-ps  Ver '+ pxc_version +' for Linux on x86_64 (Percona XtraDB Cluster (GPL), Release rel'+ pxc_rel +', Revision '+ pxc_revision +', WSREP version '+ pxc_wsrep_version +')'
