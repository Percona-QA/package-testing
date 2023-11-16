#!/usr/bin/env bash
set -e

#check that Keyring Vault component is disabled
KV_component=$(mysql -NBe "select STATUS_VALUE FROM performance_schema.keyring_component_status where STATUS_KEY='Component_status';" | grep -c ACTIVE)

if [ ${KV_component} == 1 ]; then
   echo "Keyring Vault Component is installed and active"
else
   echo "Keyring Vault Component isn't installed or active"
   exit 1
fi

echo "keyring vault component test" | tee -a ${LOG}

mysql -e "CREATE DATABASE IF NOT EXISTS test;"
mysql --database=test -e "CREATE TABLESPACE ts1 ADD DATAFILE 'ts1.ibd' ENCRYPTION='Y';"
mysql --database=test -e "CREATE TABLE keyring_vault_test (a INT PRIMARY KEY) TABLESPACE ts1 ENCRYPTION='Y';"
mysql --database=test -e "INSERT INTO keyring_vault_test VALUES (1),(2),(3);"
mysql --database=test -e "ALTER INSTANCE ROTATE INNODB MASTER KEY;"
result=$(mysql --database=test -N -s -e "CHECKSUM TABLE keyring_vault_test;" | awk -F' ' '{print $2}')
if [ "${result}" != "2050879373" ]; then
  echo "Data in keyring_vault_test table is corrupted!"
  exit 1
fi
mysql --database=test -e "DROP TABLE keyring_vault_test;"
mysql --database=test -e "DROP TABLESPACE ts1;"

