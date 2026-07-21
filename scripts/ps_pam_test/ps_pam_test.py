#!/usr/bin/env python3
"""Port of ``ps_pam_test.bats`` — verifies PAM auth and proxy mappings.

Needs a running Percona Server with the PAM setup applied. Order preserved.
"""
from pam_common import run_mysql

PLUGIN_COUNT_QUERY = (
    'select count(*) from information_schema.PLUGINS '
    'where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";'
)
CLEARTEXT_ENV = {"LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN": "1"}


def test_check_auth_pam_and_auth_pam_compat_are_installed(connection):
    result = run_mysql(connection, PLUGIN_COUNT_QUERY, suppress_stderr=True).out
    assert result == "2"


def test_check_auth_pam_successful_connect(connection):
    res = run_mysql(connection, "SELECT * FROM test_pam_table;", db="test_pam",
                    user="test_pam", password="test1234")
    assert res.returncode == 0


def test_check_auth_pam_unsuccessful_connect(connection):
    res = run_mysql(connection, "SELECT * FROM test_pam_table;", db="test_pam",
                    user="test_pam", password="test12345")
    assert res.returncode == 1


def test_check_auth_pam_compat_successful_connect(connection):
    # notice there's also --enable-cleartext-plugin option for this
    res = run_mysql(connection, "SELECT * FROM test_pam_table;", db="test_pam",
                    user="test_pam_compat", password="test1234", env=CLEARTEXT_ENV)
    assert res.returncode == 0


def test_check_auth_pam_compat_unsuccessful_connect(connection):
    # notice there's also --enable-cleartext-plugin option for this
    res = run_mysql(connection, "SELECT * FROM test_pam_table;", db="test_pam",
                    user="test_pam_compat", password="test12345", env=CLEARTEXT_ENV)
    assert res.returncode == 1


def test_check_proxy_mappings(connection):
    result = run_mysql(
        connection, "SELECT CONCAT(USER(), CURRENT_USER(), @@PROXY_USER);",
        user="test_pam2", password="test1234", suppress_stderr=True).out
    assert result == "test_pam2@localhostdb_dev@localhost''@''"
    result = run_mysql(
        connection, "SELECT CONCAT(USER(), CURRENT_USER(), @@PROXY_USER);",
        user="test_pam3", password="test1234", suppress_stderr=True).out
    assert result == "test_pam3@localhostdb_admin@localhost''@''"
