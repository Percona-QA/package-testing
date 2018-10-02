#!/usr/bin/env bats

if [ -S /run/mysqld/mysqld.sock ]; then
  CONNECTION=${CONNECTION:--S/run/mysqld/mysqld.sock}
else
  CONNECTION=${CONNECTION:--S/var/lib/mysql/mysql.sock}
fi

@test "check auth_pam and auth_pam_compat are installed" {
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";' 2>/dev/null)
  [ "$result" -eq 2 ]
}

@test "check auth_pam successful connect" {
  run mysql ${CONNECTION} -N -s -utest_pam -ptest1234 -e "SELECT * FROM test_pam_table;" test_pam
  [ "$status" -eq 0 ]
}

@test "check auth_pam unsuccessful connect" {
  run mysql ${CONNECTION} -N -s -utest_pam -ptest12345 -e "SELECT * FROM test_pam_table;" test_pam
  [ "$status" -eq 1 ]
}

@test "check auth_pam_compat successful connect" {
  export LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN=1
  # notice there's also --enable-cleartext-plugin option for this
  run mysql ${CONNECTION} -N -s -utest_pam_compat -ptest1234 -e "SELECT * FROM test_pam_table;" test_pam
  [ "$status" -eq 0 ]
}

@test "check auth_pam_compat unsuccessful connect" {
  export LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN=1
  # notice there's also --enable-cleartext-plugin option for this
  run mysql ${CONNECTION} -N -s -utest_pam_compat -ptest12345 -e "SELECT * FROM test_pam_table;" test_pam
  [ "$status" -eq 1 ]
}

@test "check proxy mappings" {
  result=$(mysql ${CONNECTION} -N -s -utest_pam2 -ptest1234 -e 'SELECT CONCAT(USER(), CURRENT_USER(), @@PROXY_USER);' 2>/dev/null)
  [ "$result" = "test_pam2@localhostdb_dev@localhost''@''" ]
  result=$(mysql ${CONNECTION} -N -s -utest_pam3 -ptest1234 -e 'SELECT CONCAT(USER(), CURRENT_USER(), @@PROXY_USER);' 2>/dev/null)
  [ "$result" = "test_pam3@localhostdb_admin@localhost''@''" ]
}
