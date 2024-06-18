#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-rocksdb'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
    ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e', 'INIT_ROCKSDB=1', '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport','-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    # Capture and print Docker logs
    try:
        logs = subprocess.check_output(['docker', 'logs', docker_id]).decode()
        print("\nDocker logs for container '{}':\n".format(container_name))
        print(logs)
    except subprocess.CalledProcessError as e:
        print("Failed to get Docker logs:", e)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestDynamic:
    def test_rocksdb_installed(self, host):
        cmd = host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "select SUPPORT from information_schema.ENGINES where ENGINE = \'ROCKSDB\';"')
        assert cmd.succeeded
        assert 'YES' in cmd.stdout

