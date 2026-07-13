#!/usr/bin/env python3
"""Port of ``bats/ps-admin_integration.bats``.

These tests need a running Percona Server. They are stateful and order-dependent
(cleanup first, "reinstall for upgrade" last); pytest runs them top-to-bottom, so
the order below is preserved from the original bats file.
"""
import re

import pytest

import ps_admin_plugins as p
from common import is_root


def _is_ps8(version):
    return re.match(r"^8\.[0-9]$", version) is not None


def _is_ps81plus(version):
    return re.match(r"^8\.[1-9]$", version) is not None


def test_uninstall_plugins_for_cleanup_before_testing(connection, ps_admin_bin, mysql_version):
    p.uninstall_all(connection, ps_admin_bin, mysql_version)
    if not _is_ps8(mysql_version):
        p.check_qrt_notexists(connection)
        p.check_tokubackup_notexists(connection)
        p.check_tokudb_notexists(connection)
    p.check_audit_exists(connection)  # TEMP-FAIL (inverted check: audit is uninstalled here)
    if mysql_version != "5.6" and not _is_ps8(mysql_version):
        p.check_mysqlx_notexists(connection, mysql_version)
        p.check_rocksdb_notexists(connection)


def test_install_qrt_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have QRT")
    p.install_qrt(connection, ps_admin_bin)
    p.check_qrt_exists(connection)


def test_uninstall_qrt_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have QRT")
    p.uninstall_qrt(connection, ps_admin_bin)
    p.check_qrt_notexists(connection)


def test_install_audit_log_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps81plus(mysql_version):
        pytest.skip("PS 8.1 doesn't have Audit log plugin")
    p.install_audit(connection, ps_admin_bin)
    p.check_audit_exists(connection)


def test_uninstall_audit_log_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps81plus(mysql_version):
        pytest.skip("PS 8.1 doesn't have Audit log plugin")
    p.uninstall_audit(connection, ps_admin_bin)
    p.check_audit_notexists(connection)


def test_install_mysqlx_plugin(connection, ps_admin_bin, mysql_version):
    if mysql_version == "5.6" or _is_ps8(mysql_version):
        pytest.skip("MySQL version is not 5.7")
    p.install_mysqlx(connection, ps_admin_bin)
    p.check_mysqlx_exists(connection, mysql_version)


def test_uninstall_mysqlx_plugin(connection, ps_admin_bin, mysql_version):
    if mysql_version == "5.6" or _is_ps8(mysql_version):
        pytest.skip("MySQL version is not 5.7")
    p.uninstall_mysqlx(connection, ps_admin_bin)
    p.check_mysqlx_notexists(connection, mysql_version)


def test_install_tokudb_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have TokuDB")
    if not is_root():
        pytest.skip("This test requires that the current user is root!")
    p.install_tokudb(connection, ps_admin_bin)
    p.check_tokudb_exists(connection)


def test_uninstall_tokudb_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have TokuDB")
    p.uninstall_tokudb(connection, ps_admin_bin)
    p.check_tokudb_notexists(connection)


def test_install_tokubackup_plugin(connection, ps_admin_bin, mysql_version):
    if not is_root():
        pytest.skip("This test requires that the current user is root!")
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have TokuDB")
    p.install_tokubackup(connection, ps_admin_bin)
    p.check_tokudb_exists(connection)
    p.check_tokubackup_exists(connection)


def test_uninstall_tokudb_and_tokubackup_plugin(connection, ps_admin_bin, mysql_version):
    if _is_ps8(mysql_version):
        pytest.skip("PS 8 doesn't have TokuDB")
    p.uninstall_tokudb(connection, ps_admin_bin)
    p.check_tokubackup_notexists(connection)
    p.check_tokudb_notexists(connection)


def test_install_rocksdb_plugin(connection, ps_admin_bin, mysql_version):
    if mysql_version == "5.6":
        pytest.skip("MySQL version is not 5.7+")
    p.install_rocksdb(connection, ps_admin_bin)
    p.check_rocksdb_exists(connection, mysql_version)


def test_uninstall_rocksdb_plugin(connection, ps_admin_bin, mysql_version):
    if mysql_version == "5.6":
        pytest.skip("MySQL version is not 5.7+")
    p.uninstall_rocksdb(connection, ps_admin_bin)
    p.check_rocksdb_notexists(connection)


def _check_all_installed(connection, mysql_version):
    if not _is_ps8(mysql_version):
        p.check_qrt_exists(connection)
        p.check_tokudb_exists(connection)
        p.check_tokubackup_exists(connection)
    if not _is_ps81plus(mysql_version):
        p.check_audit_exists(connection)
    if mysql_version != "5.6":
        p.check_mysqlx_exists(connection, mysql_version)
        p.check_rocksdb_exists(connection, mysql_version)


def test_install_all_plugins_at_once(connection, ps_admin_bin, mysql_version):
    p.install_all(connection, ps_admin_bin, mysql_version)
    _check_all_installed(connection, mysql_version)


def test_uninstall_all_plugins_at_once(connection, ps_admin_bin, mysql_version):
    p.uninstall_all(connection, ps_admin_bin, mysql_version)
    p.check_qrt_notexists(connection)
    p.check_audit_notexists(connection)
    if not _is_ps8(mysql_version):
        p.check_tokubackup_notexists(connection)
        p.check_tokudb_notexists(connection)
    if mysql_version != "5.6":
        p.check_mysqlx_notexists(connection, mysql_version)
        p.check_rocksdb_notexists(connection)


def test_reinstall_all_plugins_for_upgrade_test(connection, ps_admin_bin, mysql_version):
    p.install_all(connection, ps_admin_bin, mysql_version)
    _check_all_installed(connection, mysql_version)
