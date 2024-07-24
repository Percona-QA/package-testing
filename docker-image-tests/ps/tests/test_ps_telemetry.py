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
         '-e', 'PERCONA_TELEMETRY_ENABLE=1', '-d', docker_image]).decode().strip()
    if ps_version_major in ['5.7', '5.6']:
        subprocess.check_call(['docker', 'exec', '--user', 'root', container_name, 'microdnf', 'install', 'net-tools'])
    else:
        subprocess.check_call(['docker', 'exec', '--user', 'root', container_name, 'yum', '-y', 'install', 'net-tools'])
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestMysqlEnvironment:
    def test_telemetry_process_running(self, host):
        # Check if telemetry-agent-supervisor.sh process is running
        telemetry_supervisor_process = host.process.filter(comm="telemetry-agent-supervisor.sh")
        assert telemetry_supervisor_process, "/usr/bin/telemetry-agent-supervisor.sh process is not running"

        # Check if percona-telemetry-agent process is running
        telemetry_agent_process = host.process.filter(comm="percona-telemetry-agent")
        assert telemetry_agent_process, "/usr/bin/percona-telemetry-agent process is not running"

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
        assert oct(host.file("/usr/local/percona/telemetry_uuid").mode) == '0o664'
        assert host.file(ps_pillar_dir).is_directory
        assert host.file(ps_pillar_dir).user == 'mysql'
        assert host.file(ps_pillar_dir).group == 'percona-telemetry'
        assert oct(host.file(ps_pillar_dir).mode) == '0o6775'
