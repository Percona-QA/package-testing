#!/usr/bin/env bash
set -e

if [ -f /etc/mysql/my.cnf ]; then
  MYCNF="/etc/mysql/my.cnf"
else
  MYCNF="/etc/my.cnf"
fi

LOG="/tmp/keyring_plugins_test_run.log"
echo -n > ${LOG}

if [ -z "$1" ]; then
  echo "This script needs parameter ps57|ps80|ps81"
  exit 1
elif [ "$1" != "ps57" -a "$1" != "ps80" -a "$1" != "ps81" ]; then
  echo "Version not recognized!"
  exit 1
#else
#  VERSION="$1"
fi

#if [ "$VERSION" == "ps57" ]; then
opt_enc="ENCRYPTION='Y'"
#  binlog_enc="encrypt_binlog=ON"
#else
#  opt_enc=""
# binlog_enc="encrypt_binlog=ON"
# binlog_enc="binlog_encryption=ON"
#fi

echo "Adding the config vars" | tee -a ${LOG}
systemctl stop mysql
sleep 10
if [ $(grep -c "\[mysqld\]" ${MYCNF}) -eq 0 ]; then
  echo -e "\n[mysqld]" >> ${MYCNF}
fi
sed -i '/\[mysqld\]/a early_plugin_load=keyring_file.so' ${MYCNF}
#sed -i "/\[mysqld\]/a ${binlog_enc}" ${MYCNF}
sed -i '/\[mysqld\]/a master_verify_checksum=ON' ${MYCNF}
sed -i '/\[mysqld\]/a binlog_checksum=CRC32' ${MYCNF}
systemctl start mysql
sleep 10

echo "install keyring udf functions" | tee -a ${LOG}
# install keyring udf functions
mysql -e "CREATE FUNCTION keyring_key_fetch returns string SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_type_fetch returns string SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_length_fetch returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_remove returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_generate returns integer SONAME 'keyring_udf.so';"
mysql -e "CREATE FUNCTION keyring_key_store returns integer SONAME 'keyring_udf.so';"

echo "keyring_file plugin test" | tee -a ${LOG}
# keyring_file plugin test
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
mysql -e "DROP DATABASE test;"
mysql -e "UNINSTALL PLUGIN keyring_file;"
