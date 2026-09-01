#!/usr/bin/env python3
"""Port of ``bats/ps_tokudb_admin_integration.bats``.

Needs a running Percona Server. Stateful and order-dependent; order preserved.
"""
import pytest

import tokudb_plugins as t
from common import is_root


def test_uninstall_plugins_for_cleanup_before_testing(connection, ps_tokudb_admin_bin):
    t.uninstall_all(connection, ps_tokudb_admin_bin)
    t.check_tokubackup_notexists(connection)
    t.check_tokudb_notexists(connection)


def test_install_tokudb_plugin(connection, ps_tokudb_admin_bin):
    if not is_root():
        pytest.skip("This test requires that the current user is root!")
    t.install_tokudb(connection, ps_tokudb_admin_bin)
    t.check_tokudb_exists(connection)


def test_uninstall_tokudb_plugin(connection, ps_tokudb_admin_bin):
    t.uninstall_tokudb(connection, ps_tokudb_admin_bin)
    t.check_tokudb_notexists(connection)


def test_install_tokubackup_plugin(connection, ps_tokudb_admin_bin):
    if not is_root():
        pytest.skip("This test requires that the current user is root!")
    t.install_tokubackup(connection, ps_tokudb_admin_bin)
    t.check_tokudb_exists(connection)
    t.check_tokubackup_exists(connection)


def test_uninstall_tokudb_and_tokubackup_plugin(connection, ps_tokudb_admin_bin):
    t.uninstall_tokudb(connection, ps_tokudb_admin_bin)
    t.check_tokubackup_notexists(connection)
    t.check_tokudb_notexists(connection)


def test_install_all_plugins_at_once(connection, ps_tokudb_admin_bin):
    t.install_all(connection, ps_tokudb_admin_bin)
    t.check_tokudb_exists(connection)
    t.check_tokubackup_exists(connection)


def test_uninstall_all_plugins_at_once(connection, ps_tokudb_admin_bin):
    t.uninstall_all(connection, ps_tokudb_admin_bin)
    t.check_tokubackup_notexists(connection)
    t.check_tokudb_notexists(connection)


def test_reinstall_all_plugins_for_upgrade_test(connection, ps_tokudb_admin_bin):
    t.install_all(connection, ps_tokudb_admin_bin)
    t.check_tokudb_exists(connection)
    t.check_tokubackup_exists(connection)
