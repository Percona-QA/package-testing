#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-opentelemetry-plugin'
# telemetry_client (OpenTelemetry client plugin for the mysql CLI) ships from PS 9.7 onwards
otel_supported = bool(re.match(r'^9\.[7-9]$', ps_version_major))

pytestmark = pytest.mark.skipif(not otel_supported, reason='OpenTelemetry client plugin is available from 9.7 onwards')

LOADED_MESSAGE = 'Telemetry plugin <telemetry_client> is loaded.'


def run_mysql(host, extra_args):
    return host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock '+extra_args)


@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestOpenTelemetryClientPlugin:
    def test_plugin_file_exists(self, host):
        cmd = run_mysql(host, '-s -N -e "SELECT @@global.plugin_dir;"')
        assert cmd.succeeded
        plugin_dir = cmd.stdout.strip()
        assert host.file(plugin_dir+'/telemetry_client.so').exists

    def test_plugin_loads_when_enabled(self, host):
        cmd = run_mysql(host, '--telemetry_client --otel-help')
        assert cmd.succeeded
        assert LOADED_MESSAGE in cmd.stdout + cmd.stderr

    def test_plugin_not_loaded_by_default(self, host):
        # --otel-help is registered by the telemetry_client plugin itself, so
        # without --telemetry_client the mysql client rejects it as unknown.
        cmd = run_mysql(host, '--otel-help')
        assert not cmd.succeeded
        assert LOADED_MESSAGE not in cmd.stdout + cmd.stderr
