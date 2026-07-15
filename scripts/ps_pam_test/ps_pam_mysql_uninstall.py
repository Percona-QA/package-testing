#!/usr/bin/env python3
"""Port of ``ps_pam_mysql_uninstall.bats`` — removes the PAM plugins."""
from pam_common import run_mysql

PLUGIN_COUNT_QUERY = (
    'select count(*) from information_schema.PLUGINS '
    'where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";'
)


def test_uninstall_auth_pam_and_auth_pam_compat_plugins(connection):
    run_mysql(connection, "UNINSTALL PLUGIN auth_pam;")
    run_mysql(connection, "UNINSTALL PLUGIN auth_pam_compat;")
    result = run_mysql(connection, PLUGIN_COUNT_QUERY, suppress_stderr=True).out
    assert result == "0"
