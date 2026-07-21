#!/usr/bin/env bats

if [ -S /run/mysqld/mysqld.sock ]; then
  CONNECTION=${CONNECTION:--S/run/mysqld/mysqld.sock}
else
  CONNECTION=${CONNECTION:--S/var/lib/mysql/mysql.sock}
fi

@test "install auth_pam and auth_pam_compat plugins" {
  mysql ${CONNECTION} -N -s -e "INSTALL PLUGIN auth_pam SONAME 'auth_pam.so';"
  mysql ${CONNECTION} -N -s -e "INSTALL PLUGIN auth_pam_compat SONAME 'auth_pam_compat.so';"
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";' 2>/dev/null)
  [ "$result" -eq 2 ]
}

@test "create mysql user and add privileges" {
  # anonymous user is interfering with proxy user
  nr_anon=$(mysql ${CONNECTION} -N -s -e "SELECT count(*) FROM mysql.user WHERE user='' AND host='localhost';" 2>/dev/null)
  if [ ${nr_anon} -ne 0 ]; then
    mysql ${CONNECTION} -N -s -e "DROP USER ''@'localhost';"
  fi
  mysql ${CONNECTION} -N -s -e "CREATE DATABASE test_pam;"
  mysql ${CONNECTION} -N -s -e "CREATE TABLE test_pam_table (a int);" test_pam
  mysql ${CONNECTION} -N -s -e "INSERT INTO test_pam_table values (1),(2),(3);" test_pam
  mysql ${CONNECTION} -N -s -e "CREATE USER 'test_pam'@'localhost' IDENTIFIED WITH auth_pam;"
  mysql ${CONNECTION} -N -s -e "GRANT ALL PRIVILEGES ON test_pam.* TO test_pam@'localhost';"
  mysql ${CONNECTION} -N -s -e "CREATE USER 'test_pam_compat'@'localhost' IDENTIFIED WITH auth_pam_compat;"
  mysql ${CONNECTION} -N -s -e "GRANT ALL PRIVILEGES ON test_pam.* TO test_pam_compat@'localhost';"
  mysql ${CONNECTION} -N -s -e "FLUSH PRIVILEGES;"
}

@test "create mysql proxy and proxied users" {
  mysql ${CONNECTION} -N -s -e "CREATE USER ''@'' IDENTIFIED WITH auth_pam AS 'mysqld, developer=db_dev, dbadmin=db_admin';"
  mysql ${CONNECTION} -N -s -e "CREATE USER 'db_dev'@'localhost' IDENTIFIED BY 'Test1234!';"
  mysql ${CONNECTION} -N -s -e "GRANT PROXY ON 'db_dev'@'localhost' TO ''@'';"
  mysql ${CONNECTION} -N -s -e "CREATE USER 'db_admin'@'localhost' IDENTIFIED BY 'Test1234!';"
  mysql ${CONNECTION} -N -s -e "GRANT PROXY ON 'db_admin'@'localhost' TO ''@'';"
  mysql ${CONNECTION} -N -s -e "FLUSH PRIVILEGES;"
}

