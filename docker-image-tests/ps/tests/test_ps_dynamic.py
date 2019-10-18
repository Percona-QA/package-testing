#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time

from settings import *

# scope='session' uses the same container for all the tests;
# scope='function' uses a new container per test function.
@pytest.fixture(scope='class')
def host(request):
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', 'ps-docker-test', '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    time.sleep(20)
    # return a testinfra connection to the container
    yield testinfra.get_host("docker://" + docker_id)
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def test_install_rocksdb(host):
    # 'host' now binds to the container
    cmd = host.run("ps-admin --enable-rocksdb --user=root --password="+ps_pwd+" -S/var/lib/mysql/mysql.sock")
    assert cmd.succeeded
