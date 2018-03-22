#!/usr/bin/env bash
set -e

if [ -f /etc/mysql/my.cnf ]; then
  MYCNF="/etc/mysql/my.cnf"
else
  MYCNF="/etc/my.cnf"
fi

service mysql stop
sleep 10
if [ $(grep -c "\[mysqld\]" ${MYCNF}) -eq 0 ]; then
  echo -e "\n[mysqld]" >> ${MYCNF}
fi
sed -i '/\[mysqld\]/a early_plugin_load=keyring_file.so' ${MYCNF}
sed -i '/\[mysqld\]/a encrypt_binlog=ON' ${MYCNF}
sed -i '/\[mysqld\]/a master_verify_checksum=ON' ${MYCNF}
sed -i '/\[mysqld\]/a binlog_checksum=CRC32' ${MYCNF}
service mysql start
sleep 10

# install keyring udf functions
mysql -e "CREATE FUNCTION keyring_key_fetch returns string SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_type_fetch returns string SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_length_fetch returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_remove returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_generate returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_store returns integer SONAME 'keyring_udf.so';"

# keyring_file plugin test
#mysql -e "INSTALL PLUGIN keyring_file SONAME 'keyring_file.so';"
mysql -e "CREATE DATABASE IF NOT EXISTS test;"
mysql --database=test -e "CREATE TABLESPACE ts1 ADD DATAFILE 'ts1.ibd' ENCRYPTION='Y';"
mysql --database=test -e "CREATE TABLE keyring_file_test (a INT PRIMARY KEY) TABLESPACE ts1 ENCRYPTION='Y';"
mysql --database=test -e "INSERT INTO keyring_file_test VALUES (1),(2),(3);"
mysql --database=test -e "ALTER INSTANCE ROTATE INNODB MASTER KEY;"
result=$(mysql --database=test -N -s -e "CHECKSUM TABLE keyring_file_test;" | awk -F' ' '{print $2}')
if [ "${result}" != "2050879373" ]; then
  echo "Data in keyring_file_test table is corrupted!"
  exit 1
fi
mysql --database=test -e "DROP TABLE keyring_file_test;"
mysql --database=test -e "DROP TABLESPACE ts1;"
#mysql -e "UNINSTALL PLUGIN keyring_file;"

# service restart so that plugins don't mess with eachother
service mysql stop
sleep 10
sed -i '/early_plugin_load=/d' ${MYCNF}
sed -i '/\[mysqld\]/a early_plugin_load=keyring_vault.so' ${MYCNF}
sed -i '/\[mysqld\]/a keyring_vault_config="/package-testing/scripts/ps_keyring_plugins_test/keyring_vault_test.cnf"' ${MYCNF}
service mysql start
sleep 10

# keyring_vault plugin test
#mysql -e "INSTALL PLUGIN keyring_vault SONAME 'keyring_vault.so';"
#mysql -e "SET GLOBAL keyring_vault_config='/package-testing/scripts/ps_keyring_plugins_test/keyring_vault_test.cnf';"
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
#mysql -e "UNINSTALL PLUGIN keyring_vault;"

# drop keyring udf functions
mysql -e "DROP FUNCTION keyring_key_fetch;"
mysql -e "DROP FUNCTION keyring_key_type_fetch;"
mysql -e "DROP FUNCTION keyring_key_length_fetch;"
mysql -e "DROP FUNCTION keyring_key_remove;"
mysql -e "DROP FUNCTION keyring_key_generate;"
mysql -e "DROP FUNCTION keyring_key_store;"

sed -i '/early_plugin_load=/d' ${MYCNF}
sed -i '/keyring_vault_config=/d' ${MYCNF}
sed -i '/encrypt_binlog=/d' ${MYCNF}
sed -i '/master_verify_checksum=/d' ${MYCNF}
sed -i '/binlog_checksum=/d' ${MYCNF}
service mysql restart
sleep 10
