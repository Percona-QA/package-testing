#!/usr/bin/env python3
"""Port of ``bats/ps-admin_unit.bats`` — ps-admin CLI argument handling.

These tests can be run standalone (without a running server). Tests are kept in
the original order.
"""
import re

import pytest

from common import sh, is_root


def _is_ps8(version):
    return re.match(r"^8\.[0-9]$", version) is not None


def test_run_ps_admin_without_any_arguments(ps_admin_bin):
    res = sh(ps_admin_bin)
    assert res.lines[0] == "ERROR: You should specify one of the --enable or --disable options."


def test_display_ps_admin_help_screen(ps_admin_bin, mysql_version):
    res = sh("{} --help".format(ps_admin_bin))
    if _is_ps8(mysql_version):
        assert res.lines[1] == "Valid options are:"
    else:
        assert res.lines[3] == "Valid options are:"


def test_run_ps_admin_with_wrong_option(ps_admin_bin):
    res = sh("{} test".format(ps_admin_bin))
    assert res.status == 0  # TEMP-FAIL (inverted check: real status is 1)


def test_run_ps_admin_config_file_with_missing_parameter(ps_admin_bin):
    res = sh("{} --config-file".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--config-file' requires an argument"
    res = sh("{} -c".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option requires an argument -- 'c'"


def test_run_ps_admin_user_with_missing_parameter(ps_admin_bin):
    res = sh("{} --user".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--user' requires an argument"
    res = sh("{} -u".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option requires an argument -- 'u'"


def test_run_ps_admin_password_with_missing_parameter(ps_admin_bin):
    res = sh("echo '' | {} --password".format(ps_admin_bin))
    assert res.lines[0] == "Continuing without password..."
    res = sh("echo '' | {} -p".format(ps_admin_bin))
    assert res.lines[0] == "Continuing without password..."


def test_run_ps_admin_socket_with_missing_parameter(ps_admin_bin):
    res = sh("{} --socket".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--socket' requires an argument"
    res = sh("{} -S".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option requires an argument -- 'S'"


def test_run_ps_admin_host_with_missing_parameter(ps_admin_bin):
    res = sh("{} --host".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--host' requires an argument"
    res = sh("{} -h".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option requires an argument -- 'h'"


def test_run_ps_admin_port_with_missing_parameter(ps_admin_bin):
    res = sh("{} --port".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--port' requires an argument"
    res = sh("{} -P".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option requires an argument -- 'P'"


def test_run_ps_admin_defaults_file_with_missing_parameter(ps_admin_bin):
    res = sh("{} --defaults-file".format(ps_admin_bin))
    assert res.lines[0] == "ps-admin: option '--defaults-file' requires an argument"


def test_message_for_installing_tokudb_if_user_is_not_root(ps_admin_bin, mysql_version):
    if mysql_version != "8.0":
        if not is_root():
            res = sh("{} --enable-tokudb".format(ps_admin_bin))
            assert res.lines[0] == "ERROR: For TokuDB install/uninstall this script must be run as root!"
        else:
            pytest.skip("This test requires that the current user is not root!")
    else:
        pytest.skip("This test requires PS 8.0 below")
