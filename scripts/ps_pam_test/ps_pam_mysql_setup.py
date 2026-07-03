#!/usr/bin/env python3
"""Port of ``ps_pam_mysql_setup.bats`` — installs PAM plugins and sets up users.

Needs a running Percona Server. Stateful and order-dependent; order preserved.
"""
from pam_common import run_mysql

PLUGIN_COUNT_QUERY = (
    'select count(*) from information_schema.PLUGINS '
    'where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";'
)


def test_install_auth_pam_and_auth_pam_compat_plugins(connection):
    run_mysql(connection, "INSTALL PLUGIN auth_pam SONAME 'auth_pam.so';")
    run_mysql(connection, "INSTALL PLUGIN auth_pam_compat SONAME 'auth_pam_compat.so';")
    result = run_mysql(connection, PLUGIN_COUNT_QUERY, suppress_stderr=True).out
    assert result == "2"


def test_create_mysql_user_and_add_privileges(connection):
    # anonymous user is interfering with proxy user
    nr_anon = run_mysql(
        connection,
        "SELECT count(*) FROM mysql.user WHERE user='' AND host='localhost';",
        suppress_stderr=True,
    ).out
    if int(nr_anon) != 0:
        run_mysql(connection, "DROP USER ''@'localhost';", check=True)
    run_mysql(connection, "CREATE DATABASE test_pam;", check=True)
    run_mysql(connection, "CREATE TABLE test_pam_table (a int);", db="test_pam", check=True)
    run_mysql(connection, "INSERT INTO test_pam_table values (1),(2),(3);", db="test_pam", check=True)
    run_mysql(connection, "CREATE USER 'test_pam'@'localhost' IDENTIFIED WITH auth_pam;", check=True)
    run_mysql(connection, "GRANT ALL PRIVILEGES ON test_pam.* TO test_pam@'localhost';", check=True)
    run_mysql(connection, "CREATE USER 'test_pam_compat'@'localhost' IDENTIFIED WITH auth_pam_compat;", check=True)
    run_mysql(connection, "GRANT ALL PRIVILEGES ON test_pam.* TO test_pam_compat@'localhost';", check=True)
    run_mysql(connection, "FLUSH PRIVILEGES;", check=True)


def test_create_mysql_proxy_and_proxied_users(connection):
    run_mysql(connection, "CREATE USER ''@'' IDENTIFIED WITH auth_pam AS 'mysqld, developer=db_dev, dbadmin=db_admin';", check=True)
    run_mysql(connection, "CREATE USER 'db_dev'@'localhost' IDENTIFIED BY 'Test1234!';", check=True)
    run_mysql(connection, "GRANT PROXY ON 'db_dev'@'localhost' TO ''@'';", check=True)
    run_mysql(connection, "CREATE USER 'db_admin'@'localhost' IDENTIFIED BY 'Test1234!';", check=True)
    run_mysql(connection, "GRANT PROXY ON 'db_admin'@'localhost' TO ''@'';", check=True)
    run_mysql(connection, "FLUSH PRIVILEGES;", check=True)
