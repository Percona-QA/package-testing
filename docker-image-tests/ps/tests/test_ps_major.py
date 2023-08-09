import pytest
import subprocess
import testinfra
import time
from settings import *

docker_acc = os.getenv('DOCKER_ACC')
container_name = 'ps-docker-test-static1'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image_major]).decode().strip()
    if ps_version_major in ['5.7','5.6']:
        subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install','net-tools'])
    else:
        subprocess.check_call(['docker','exec','--user','root',container_name,'yum','-y','install','net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

@pytest.mark.skipif(docker_acc == "perconalab", reason="Skipping tests in 'testing' repo")
class TestMysqlEnvironment:
    @pytest.mark.parametrize("pkg_name", ps_packages)
    def test_packages(self, host, pkg_name):
        assert host.package(pkg_name).is_installed
        assert host.package(pkg_name).version == ps_version_upstream
    
    @pytest.mark.skipif(docker_acc == "perconalab", reason="Skipping tests in 'testing' repo")
    def test_binaries_version(self, host):
        if ps_version_major in ['5.7','5.6']:
            assert host.check_output('mysql --version') == 'mysql  Ver 14.14 Distrib '+ps_version+', for Linux (x86_64) using  7.0'
            assert host.check_output('mysqld --version') == 'mysqld  Ver '+ps_version+' for Linux on x86_64 (Percona Server (GPL), Release '+ps_version_percona+', Revision '+ps_revision+')'
        else:
            assert host.check_output('mysql --version') == 'mysql  Ver '+ ps_version_upstream + '-' + ps_version_percona +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'
            assert host.check_output('mysqld --version') == '/usr/sbin/mysqld  Ver '+ ps_version_upstream + '-' + ps_version_percona +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')'
