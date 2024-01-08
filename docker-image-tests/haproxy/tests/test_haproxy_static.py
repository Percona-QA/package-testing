#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *

container_name = 'haproxy-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-d', docker_image ], stderr=subprocess.STDOUT ).decode().strip()
    time.sleep(20)
    subprocess.check_call(['docker','exec','--user','root',container_name,'microdnf','install', '-y', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestHAproxyEnvironment:
    def test_packages(self, host):
        pkg = host.package("percona-haproxy")
        dist = host.system_info.distribution
        assert pkg.is_installed
        if dist.lower() in RHEL_DISTS:
            assert haproxy_version in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
        else:
            assert haproxy_version in pkg.version, pkg.version

    def test_binaries_exist(self, host):
        haproxy_binary="/usr/sbin/haproxy"
        assert host.file(haproxy_binary).exists
        assert oct(host.file(haproxy_binary).mode) == '0o755'

    def test_binaries_version(self, host):
        version_output=host.run("haproxy --version")
        assert haproxy_version in version_output.stdout

    def test_process_running(self, host):
        assert host.process.filter(user="mysql", comm="haproxy")

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups

    def test_mysql_group(self, host):
        assert host.group('mysql').exists
        assert host.group('mysql').gid == 1001

    def test_haproxy_permissions(self, host):
        assert host.file('/usr/sbin/haproxy').user == 'root'
        assert host.file('/usr/sbin/haproxy').group == 'root'
        assert oct(host.file('/usr/sbin/haproxy').mode) == '0o755'

    def test_check_pxc_permissions(self, host):
        assert host.file('/usr/local/bin/check_pxc.sh').user == 'mysql'
        assert host.file('/usr/local/bin/check_pxc.sh').group == 'mysql'
        assert oct(host.file('/usr/local/bin/check_pxc.sh').mode) == '0o755'

    def test_haproxy_conf_permissions(self, host):
        assert host.file('/etc/haproxy/haproxy.cfg').user == 'mysql'
        assert host.file('/etc/haproxy/haproxy.cfg').group == 'mysql'
        assert oct(host.file('/etc/haproxy/haproxy.cfg').mode) == '0o644'

    def test_haproxy_global_conf_permissions(self, host):
        assert host.file('/etc/haproxy/haproxy-global.cfg').user == 'mysql'
        assert host.file('/etc/haproxy/haproxy-global.cfg').group == 'mysql'
        assert oct(host.file('//etc/haproxy/haproxy-global.cfg').mode) == '0o644'
