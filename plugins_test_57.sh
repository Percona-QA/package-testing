#!/bin/bash
set -e
mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "INSTALL PLUGIN auth_pam SONAME 'auth_pam.so';"
mysql -e "INSTALL PLUGIN audit_log SONAME 'audit_log.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_AUDIT SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_READ SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_WRITE SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN mysqlx SONAME 'mysqlx.so';"
mysql -e "SHOW PLUGINS;"
mysql -e "CREATE DATABASE world;"
sed -i '18,21 s/^/-- /' /package-testing/world.sql
pv /package-testing/world.sql | mysql -D world
if [ ! -z "$1" ]; then
  if [ "$1" = "ps" ]; then
    mysql -e "CREATE DATABASE world2;"
    pv /package-testing/world.sql | mysql -D world2
    mysql < /package-testing/tokudb_compression.sql
  fi
fi
