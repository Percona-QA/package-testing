#!/usr/bin/env python3
"""Port of ``bats/ps_tokudb_admin_unit.bats`` — ps_tokudb_admin CLI handling.

Can be run standalone (without a running server). Order preserved.
"""
import pytest

from common import sh, is_root


def test_run_ps_tokudb_admin_without_any_arguments(ps_tokudb_admin_bin, mysql_version):
    res = sh(ps_tokudb_admin_bin)
    expected = "ERROR: You should specify --enable,--disable,--enable-backup or --disable-backup option. Use --help for printing options."
    if mysql_version == "5.7":
        assert res.lines[1] == expected
    else:
        assert res.lines[0] == expected


def test_display_ps_tokudb_admin_help_screen(ps_tokudb_admin_bin, mysql_version):
    res = sh("{} --help".format(ps_tokudb_admin_bin))
    if mysql_version == "5.7":
        assert res.lines[5] == "Valid options are:"
    else:
        assert res.lines[4] == "Valid options are:"


def test_run_ps_tokudb_admin_with_wrong_option(ps_tokudb_admin_bin):
    res = sh("{} test".format(ps_tokudb_admin_bin))
    assert res.status == 1


def test_run_ps_tokudb_admin_user_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("{} --user".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option '--user' requires an argument"
    res = sh("{} -u".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option requires an argument -- 'u'"


def test_run_ps_tokudb_admin_password_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("echo '' | {} --password".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "Continuing without password..."
    res = sh("echo '' | {} -p".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "Continuing without password..."


def test_run_ps_tokudb_admin_socket_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("{} --socket".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option '--socket' requires an argument"
    res = sh("{} -S".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option requires an argument -- 'S'"


def test_run_ps_tokudb_admin_host_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("{} --host".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option '--host' requires an argument"
    res = sh("{} -h".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option requires an argument -- 'h'"


def test_run_ps_tokudb_admin_port_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("{} --port".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option '--port' requires an argument"
    res = sh("{} -P".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option requires an argument -- 'P'"


def test_run_ps_tokudb_admin_defaults_file_with_missing_parameter(ps_tokudb_admin_bin):
    res = sh("{} --defaults-file".format(ps_tokudb_admin_bin))
    assert res.lines[0] == "ps_tokudb_admin: option '--defaults-file' requires an argument"


def test_message_for_installing_tokudb_if_user_is_not_root(ps_tokudb_admin_bin):
    if not is_root():
        res = sh("{} --enable".format(ps_tokudb_admin_bin))
        assert res.lines[0] == "ERROR: This script must be run as root!"
    else:
        pytest.skip("This test requires that the current user is not root!")
