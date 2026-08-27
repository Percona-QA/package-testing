#!/usr/bin/env python3
"""Port of ``bats/ps-admin_helper.bash``.

Helper functions for the ps-admin integration tests. Each ``install_*`` /
``uninstall_*`` runs the ps-admin binary and asserts success; each ``check_*``
runs a SQL count query against information_schema and asserts the expected
(version-dependent) count. State is carried between calls, exactly as in the
original bats suite.
"""
import re
import time

from common import sh, sql


def _is_ps8(version):
    # matches bats regex ^8.[0-9]{1}$
    return re.match(r"^8\.[0-9]$", version) is not None


def _is_ps81plus(version):
    # matches bats regex ^8.[1-9]{1}$
    return re.match(r"^8\.[1-9]$", version) is not None


def _admin(conn, ps_admin_bin, args):
    return sh('bash -c "{bin} {conn} {args}"'.format(
        bin=ps_admin_bin, conn=conn, args=args))


def _restart_mysql():
    res = sh("systemctl restart mysql >/dev/null 3>&-")
    assert res.returncode == 0
    time.sleep(5)


# ---- QRT ----
def install_qrt(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-qrt").returncode == 0


def uninstall_qrt(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-qrt").returncode == 0


def check_qrt_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "QUERY_RESPONSE_TIME%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "4"


def check_qrt_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "QUERY_RESPONSE_TIME%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- Audit log ----
def install_audit(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-audit").returncode == 0


def check_audit_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "audit_log%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "1"


def uninstall_audit(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-audit").returncode == 0


def check_audit_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "audit_log%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- PAM (kept for parity; tests currently commented out) ----
def install_pam(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-pam").returncode == 0


def check_pam_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME="auth_pam" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "1"


def uninstall_pam(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-pam").returncode == 0


def check_pam_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME="auth_pam" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


def install_pam_compat(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-pam-compat").returncode == 0


def check_pam_compat_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME="auth_pam_compat" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "1"


def uninstall_pam_compat(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-pam-compat").returncode == 0


def check_pam_compat_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME="auth_pam_compat" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- MySQL X ----
def install_mysqlx(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-mysqlx").returncode == 0


def check_mysqlx_exists(conn, version):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "mysqlx%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == ("2" if _is_ps8(version) else "1")


def uninstall_mysqlx(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-mysqlx").returncode == 0


def check_mysqlx_notexists(conn, version):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "mysqlx%" and PLUGIN_STATUS like "ACTIVE";')
    # mirrors bats: on 8.x it expects 2 (mysqlx is bundled), else 0
    assert result == ("2" if _is_ps8(version) else "0")


# ---- TokuDB ----
def install_tokudb(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-tokudb").returncode == 0
    _restart_mysql()
    assert _admin(conn, ps_admin_bin, "--enable-tokudb").returncode == 0


def check_tokudb_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
    assert result == "1"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like BINARY "%TokuDB%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "8"


def uninstall_tokudb(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-tokudb").returncode == 0


def check_tokudb_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
    assert result == "0"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- TokuBackup ----
def install_tokubackup(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-tokubackup").returncode == 0
    _restart_mysql()
    assert _admin(conn, ps_admin_bin, "--enable-tokubackup").returncode == 0


def check_tokubackup_exists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "1"


def uninstall_tokubackup(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-tokubackup").returncode == 0


def check_tokubackup_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- RocksDB ----
def install_rocksdb(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--enable-rocksdb").returncode == 0


def check_rocksdb_exists(conn, version):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="ROCKSDB" and SUPPORT <> "NO";')
    assert result == "1"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like BINARY "%ROCKSDB%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == ("17" if _is_ps8(version) else "13")


def uninstall_rocksdb(conn, ps_admin_bin):
    assert _admin(conn, ps_admin_bin, "--disable-rocksdb").returncode == 0


def check_rocksdb_notexists(conn):
    result = sql(conn, 'select count(*) from information_schema.ENGINES where ENGINE="ROCKSDB" and SUPPORT <> "NO";')
    assert result == "0"
    result = sql(conn, 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%ROCKSDB%" and PLUGIN_STATUS like "ACTIVE";')
    assert result == "0"


# ---- Aggregate ----
def _all_opt(version):
    if version == "5.6":
        return "--enable-qrt --enable-tokudb --enable-tokubackup"
    if version == "5.7":
        return "--enable-qrt --enable-mysqlx --enable-tokudb --enable-tokubackup --enable-rocksdb"
    return "--enable-rocksdb"


def install_all(conn, ps_admin_bin, version):
    opt = _all_opt(version)
    # First restart works around MYR-204 / PS-3817.
    _restart_mysql()
    if _is_ps81plus(version):
        assert _admin(conn, ps_admin_bin, opt).returncode == 0
    else:
        assert _admin(conn, ps_admin_bin, "--enable-audit " + opt).returncode == 0
    _restart_mysql()
    if _is_ps81plus(version):
        assert _admin(conn, ps_admin_bin, opt).returncode == 0
    else:
        assert _admin(conn, ps_admin_bin, "--enable-audit " + opt).returncode == 0


def _all_disable_opt(version):
    if version == "5.6":
        return "--disable-qrt --disable-tokudb --disable-tokubackup"
    if version == "5.7":
        return "--disable-qrt --disable-mysqlx --disable-tokudb --disable-tokubackup --disable-rocksdb"
    return "--disable-rocksdb"


def uninstall_all(conn, ps_admin_bin, version):
    opt = _all_disable_opt(version)
    if _is_ps81plus(version):
        assert _admin(conn, ps_admin_bin, opt).returncode == 0
    else:
        assert _admin(conn, ps_admin_bin, "--disable-audit " + opt).returncode == 0
    _restart_mysql()
    if _is_ps81plus(version):
        assert _admin(conn, ps_admin_bin, opt).returncode == 0
    else:
        assert _admin(conn, ps_admin_bin, "--disable-audit " + opt).returncode == 0
