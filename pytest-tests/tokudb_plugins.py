#!/usr/bin/env python3
"""Port of ``bats/ps_tokudb_admin_helper.bash``.

Helper functions for the ps_tokudb_admin integration tests (TokuDB + TokuBackup
only). State is carried between calls, as in the original bats suite.
"""
import time

from common import sh, sql


def _admin(conn, bin_, args):
    return sh('bash -c "{bin} {conn} {args}"'.format(bin=bin_, conn=conn, args=args))


def _restart_mysql():
    res = sh("systemctl restart mysql >/dev/null 3>&-")
    assert res.returncode == 0
    time.sleep(5)


def install_tokudb(conn, bin_):
    assert _admin(conn, bin_, "--enable").returncode == 0
    _restart_mysql()
    assert _admin(conn, bin_, "--enable").returncode == 0


def check_tokudb_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
    assert result == "1"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like BINARY "%TokuDB%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "8"


def uninstall_tokudb(conn, bin_):
    assert _admin(conn, bin_, "--disable").returncode == 0
    _restart_mysql()


def check_tokudb_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
    assert result == "0"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


def install_tokubackup(conn, bin_):
    assert _admin(conn, bin_, "--enable-backup").returncode == 0
    _restart_mysql()
    assert _admin(conn, bin_, "--enable-backup").returncode == 0


def check_tokubackup_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "1"


def uninstall_tokubackup(conn, bin_):
    assert _admin(conn, bin_, "--disable-backup").returncode == 0


def check_tokubackup_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


def install_all(conn, bin_):
    assert _admin(conn, bin_, "--enable --enable-backup").returncode == 0
    _restart_mysql()
    assert _admin(conn, bin_, "--enable --enable-backup").returncode == 0


def uninstall_all(conn, bin_):
    assert _admin(conn, bin_, "--disable --disable-backup").returncode == 0
    _restart_mysql()
    assert _admin(conn, bin_, "--disable --disable-backup").returncode == 0
