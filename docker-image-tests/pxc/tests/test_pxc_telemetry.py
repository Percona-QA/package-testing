#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'pxc-docker-test-static'

@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd,
         '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport',
         '-e', 'PERCONA_TELEMETRY_ENABLE=1',
         '-d', docker_image]).decode().strip()
    exec_command = ['microdnf', 'install', 'net-tools']
    subprocess.check_call(['docker','exec','--user','root',container_name] + exec_command)
    time.sleep(80)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

class TestMysqlEnvironment:
    def test_ta_process_running(self, host):
        cmd = 'ps auxww| grep -v grep  | grep -c "percona-telemetry-agent"'
        result = host.run(cmd)
        stdout = int(result.stdout)
        assert stdout == 1

    def test_telemetry_agent_supervisor_running(self, host):
        cmd = 'ps auxww| grep -v grep  | grep -c "telemetry-agent-supervisor.sh"'
        result = host.run(cmd)
        stdout = int(result.stdout)
        assert stdout == 1

    def test_telemetry_agent_dirs_present(self, host):
        assert host.file("/usr/local/percona/telemetry/").is_directory
        assert host.file("/usr/local/percona/telemetry/").user == 'daemon'
        assert host.file("/usr/local/percona/telemetry/").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/").mode) == '0o755'
        assert host.file("/usr/local/percona/telemetry/history").is_directory
        assert host.file("/usr/local/percona/telemetry/history").user == 'mysql'
        assert host.file("/usr/local/percona/telemetry/history").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/history").mode) == '0o6755'
        assert host.file("/usr/local/percona/telemetry_uuid").is_file
        assert host.file("/usr/local/percona/telemetry_uuid").group == 'mysql'
        assert oct(host.file("/usr/local/percona/telemetry_uuid").mode) == '0o644'
        assert host.file("/usr/local/percona/telemetry/pxc").is_directory
        assert host.file("/usr/local/percona/telemetry/pxc").user == 'mysql'
        assert host.file("/usr/local/percona/telemetry/pxc").group == 'percona-telemetry'
        assert oct(host.file("/usr/local/percona/telemetry/pxc").mode) == '0o2775'
