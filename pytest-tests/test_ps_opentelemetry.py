#!/usr/bin/env python3
"""OpenTelemetry component and client plugin tests for a live Percona Server.

Covers ``component_telemetry`` (the native OpenTelemetry exporter, installed
via ``INSTALL COMPONENT``) and ``telemetry_client`` (the mysql CLI client
plugin, loaded via ``--telemetry_client``). Both ship from PS 9.7 onwards.
"""
import os
import re

import pytest

from common import sh, sql, sql_result

LOADED_MARKER = "=== TELEMETRY_CLIENT PLUGIN VARIABLES ==="


def _supports_opentelemetry(version):
    return re.match(r"^9\.[7-9]$", version) is not None


def _mysql(conn, extra_args):
    return sh("mysql {conn} {args}".format(conn=conn, args=extra_args))


@pytest.fixture(autouse=True)
def _skip_if_unsupported(mysql_version):
    if not _supports_opentelemetry(mysql_version):
        pytest.skip("OpenTelemetry is available from PS 9.7 onwards")


def test_install_component(connection):
    install = sql_result(connection, "INSTALL COMPONENT 'file://component_telemetry';")
    assert install.returncode == 0, install.output
    result = sql(connection, "SELECT component_urn FROM mysql.component WHERE component_urn = 'file://component_telemetry';")
    assert "file://component_telemetry" in result


def test_default_variables(connection):
    # SELECT @@global.<var> returns MySQL's raw 0/1 for boolean sysvars,
    # not the ON/OFF text shown by SHOW VARIABLES/SHOW STATUS.
    expected = {
        "telemetry.trace_enabled": "0",
        "telemetry.metrics_enabled": "0",
        "telemetry.log_enabled": "0",
        "telemetry.query_text_enabled": "1",
        "telemetry.otel_log_level": "info",
    }
    for variable, value in expected.items():
        assert sql(connection, "SELECT @@global.{};".format(variable)) == value


def test_status_variables(connection):
    for status_var in ("Telemetry_logs_supported", "Telemetry_metrics_supported", "Telemetry_traces_supported"):
        assert "ON" in sql(connection, "SHOW GLOBAL STATUS LIKE '{}';".format(status_var))
    assert "READY" in sql(connection, "SHOW GLOBAL STATUS LIKE 'telemetry.run_level';")


def test_enable_dynamic_variables(connection):
    for variable in ("telemetry.trace_enabled", "telemetry.log_enabled"):
        sql(connection, "SET GLOBAL {}=ON;".format(variable))
        assert sql(connection, "SELECT @@global.{};".format(variable)) == "1"


def test_metrics_enabled_is_startup_only(connection):
    # telemetry.metrics_enabled is startup-only, so a runtime SET must fail.
    result = _mysql(connection, "-N -s -e \"SET GLOBAL telemetry.metrics_enabled=ON;\"")
    assert result.returncode != 0


def test_uninstall_component(connection):
    sql(connection, "UNINSTALL COMPONENT 'file://component_telemetry';")
    result = sql(connection, "SELECT component_urn FROM mysql.component WHERE component_urn = 'file://component_telemetry';")
    assert "file://component_telemetry" not in result


def test_client_plugin_loads_when_enabled(connection):
    plugin_dir = sql(connection, "SELECT @@global.plugin_dir;")
    assert os.path.exists(os.path.join(plugin_dir, "telemetry_client.so"))

    # --otel-help is registered by the telemetry_client plugin itself, so it
    # only succeeds and prints the plugin variables banner when the plugin
    # is loaded via --telemetry_client.
    enabled = _mysql(connection, "--telemetry_client --otel-help")
    assert enabled.returncode == 0
    assert LOADED_MARKER in enabled.output


def test_client_plugin_not_loaded_by_default(connection):
    disabled = _mysql(connection, "--otel-help")
    assert disabled.returncode != 0
    assert LOADED_MARKER not in disabled.output
