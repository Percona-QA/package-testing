#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


container_name = 'ps-docker-test-opentelemetry-arm'
# component_telemetry (native OpenTelemetry exporter) ships from PS 9.7 onwards
otel_supported = bool(re.match(r'^9\.[7-9]$', ps_version_major))

pytestmark = pytest.mark.skipif(not otel_supported, reason='OpenTelemetry component is available from 9.7 onwards')


def run_sql(host, sql):
    return host.run('mysql --user=root --password='+ps_pwd+' -S/var/lib/mysql/mysql.sock -s -N -e "'+sql+'"')


@pytest.fixture(scope='module')
def host():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    time.sleep(20)
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestOpenTelemetry:
    def test_install_component(self, host):
        cmd = run_sql(host, "INSTALL COMPONENT 'file://component_telemetry';")
        assert cmd.succeeded
        cmd = run_sql(host, "SELECT component_urn FROM mysql.component WHERE component_urn = 'file://component_telemetry';")
        assert cmd.succeeded
        assert 'file://component_telemetry' in cmd.stdout

    def test_default_variables(self, host):
        expected = {
            'telemetry.trace_enabled': 'OFF',
            'telemetry.metrics_enabled': 'OFF',
            'telemetry.log_enabled': 'OFF',
            'telemetry.query_text_enabled': 'ON',
            'telemetry.otel_log_level': 'ERROR',
        }
        for variable, value in expected.items():
            cmd = run_sql(host, 'SELECT @@global.'+variable+';')
            assert cmd.succeeded
            assert cmd.stdout.strip() == value

    def test_status_variables(self, host):
        for status_var in ('Telemetry_logs_supported', 'Telemetry_metrics_supported', 'Telemetry_traces_supported'):
            cmd = run_sql(host, "SHOW GLOBAL STATUS LIKE '"+status_var+"';")
            assert cmd.succeeded
            assert 'ON' in cmd.stdout
        cmd = run_sql(host, "SHOW GLOBAL STATUS LIKE 'telemetry.run_level';")
        assert cmd.succeeded
        assert 'READY' in cmd.stdout

    def test_enable_dynamic_variables(self, host):
        for variable in ('telemetry.trace_enabled', 'telemetry.log_enabled'):
            cmd = run_sql(host, 'SET GLOBAL '+variable+'=ON;')
            assert cmd.succeeded
            cmd = run_sql(host, 'SELECT @@global.'+variable+';')
            assert cmd.succeeded
            assert cmd.stdout.strip() == 'ON'

    def test_metrics_enabled_is_startup_only(self, host):
        cmd = run_sql(host, 'SET GLOBAL telemetry.metrics_enabled=ON;')
        assert not cmd.succeeded

    def test_uninstall_component(self, host):
        cmd = run_sql(host, "UNINSTALL COMPONENT 'file://component_telemetry';")
        assert cmd.succeeded
        cmd = run_sql(host, "SELECT component_urn FROM mysql.component WHERE component_urn = 'file://component_telemetry';")
        assert cmd.succeeded
        assert 'file://component_telemetry' not in cmd.stdout
