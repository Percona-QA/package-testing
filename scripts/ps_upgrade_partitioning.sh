#!/usr/bin/env bash
set -e

if [ -f /etc/mysql/my.cnf ]; then
  MYCNF="/etc/mysql/my.cnf"
else
  MYCNF="/etc/my.cnf"
fi

echo "Adding the config vars"
systemctl stop mysql
sleep 10
if [ $(grep -c "\[mysqld\]" ${MYCNF}) -eq 0 ]; then
  echo -e "\n[mysqld]" >> ${MYCNF}
fi
sed -i '/\[mysqld\]/a rocksdb_enable_native_partition=ON' ${MYCNF}
sed -i '/\[mysqld\]/a tokudb_enable_native_partition=ON' ${MYCNF}
systemctl start mysql
sleep 10

echo "upgrade tables"
mysql -e "ALTER TABLE comp_test.t1_RocksDB_default UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_RocksDB_lz4 UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_RocksDB_no UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_RocksDB_zlib UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_RocksDB_zstd UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_default UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_lzma UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_no UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_quicklz UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_snappy UPGRADE PARTITIONING;"
mysql -e "ALTER TABLE comp_test.t1_TokuDB_zlib UPGRADE PARTITIONING;"

echo "remove the config vars"
sed -i '/rocksdb_enable_native_partition=/d' ${MYCNF}
sed -i '/tokudb_enable_native_partition=/d' ${MYCNF}
systemctl restart mysql
sleep 10
