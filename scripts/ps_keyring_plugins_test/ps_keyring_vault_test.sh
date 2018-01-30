#!/usr/bin/env bash
set -e

mysql -e "SET GLOBAL keyring_vault_config='/package-testing/scripts/ps_keyring_plugins_test/keyring_vault_test.cnf';"
mysql -e "INSTALL PLUGIN keyring_vault SONAME 'keyring_vault.so';"
mysql -e "CREATE DATABASE IF NOT EXISTS test;"
mysql --database=test -e "CREATE TABLE keyring_vault_test (a INT PRIMARY KEY) ENCRYPTION='Y';"
mysql --database=test -e "INSERT INTO keyring_vault_test VALUES (1),(2),(3);"
mysql --database=test -e "ALTER INSTANCE ROTATE INNODB MASTER KEY;"
result=$(mysql --database=test -N -s -e "CHECKSUM TABLE keyring_vault_test;" | awk -F' ' '{print $2}')
if [ "${result}" != "2050879373" ]; then
  echo "Data in keyring_vault_test table is corrupted!"
  exit 1
fi
mysql --database=test -e "DROP TABLE keyring_vault_test;"
mysql -e "UNINSTALL PLUGIN keyring_vault;"
