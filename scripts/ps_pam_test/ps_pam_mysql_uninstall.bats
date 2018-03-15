#!/usr/bin/env bats

if [ -S /run/mysqld/mysqld.sock ]; then
  CONNECTION=${CONNECTION:--S/run/mysqld/mysqld.sock}
else
  CONNECTION=${CONNECTION:--S/var/lib/mysql/mysql.sock}
fi

@test "uninstall auth_pam and auth_pam_compat plugins" {
  mysql ${CONNECTION} -N -s -e "UNINSTALL PLUGIN auth_pam;"
  mysql ${CONNECTION} -N -s -e "UNINSTALL PLUGIN auth_pam_compat;"
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "auth_pam%" and PLUGIN_STATUS like "ACTIVE";' 2>/dev/null)
  [ "$result" -eq 0 ]
}
