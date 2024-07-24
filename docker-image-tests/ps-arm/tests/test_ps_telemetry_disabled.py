#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-e',
         'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport',
         '-e', 'PERCONA_TELEMETRY_DISABLED=1', '-d', docker_image]).decode().strip()
    if ps_version_major in ['5.7', '5.6']:
        subprocess.check_call(['docker', 'exec', '--user', 'root', container_name, 'microdnf', 'install', 'net-tools'])
    else:
        subprocess.check_call(['docker', 'exec', '--user', 'root', container_name, 'yum', '-y', 'install', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestMysqlEnvironment:
    
    def test_telemetry_disabled(self, host):
        if ps_version_major in ['5.6']:
            pytest.skip('telemetry was added in 5.7, 8.0 and 8.x')
        else:
            assert not host.file('/usr/local/percona/telemetry_uuid').exists
    def test_ta_process_running(self, host):
        cmd = 'ps auxww| grep -v grep  | grep -c "percona-telemetry-agent"'
        result = host.run(cmd)
        stdout = int(result.stdout)
        assert stdout == 0

    def test_telemetry_agent_supervisor_running(self, host):
        cmd = 'ps auxww| grep -v grep  | grep -c "telemetry-agent-supervisor.sh"'
        result = host.run(cmd)
        stdout = int(result.stdout)
        assert stdout == 0

    def test_telemetry_agent_dirs(self, host):
        assert host.file("/usr/local/percona/telemetry/").is_directory
        assert host.file("/usr/local/percona/telemetry/").user == 'daemon'
        assert host.file("/usr/local/percona/telemetry/").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/").mode) == '0o755'
        assert host.file("/usr/local/percona/telemetry/history").is_directory
        assert host.file("/usr/local/percona/telemetry/history").user == 'mysql'
        assert host.file("/usr/local/percona/telemetry/history").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/history").mode) == '0o6755'
