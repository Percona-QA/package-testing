#!/bin/bash
set -e
WARNINGS_BEFORE=0
WARNINGS_AFTER=0
ERROR_LOG=""
ERROR_LOG=$(mysql -N -s -e "show variables like 'log_error';" | grep -v "Warning:" | grep -o "\/.*$") || true
if [ -z ${ERROR_LOG} ]; then
  echo "ERROR_LOG variable is empty!"
  exit 1
fi
if [ ! -f ${ERROR_LOG} ]; then
  echo "Error log file was not found!"
  exit 1
fi

WARNINGS_BEFORE=$(grep -c "\[Warning\]" ${ERROR_LOG} || true)
ERRORS_BEFORE=$(grep -c "\[ERROR\]" ${ERROR_LOG} || true)

mysql -e "DROP FUNCTION IF EXISTS fnv1a_64"
mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "INSTALL PLUGIN audit_log SONAME 'audit_log.so';"
mysql -e "INSTALL PLUGIN scalability_metrics SONAME 'scalability_metrics.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_AUDIT SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_READ SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN QUERY_RESPONSE_TIME_WRITE SONAME 'query_response_time.so';"
mysql -e "INSTALL PLUGIN mysqlx SONAME 'mysqlx.so';"
mysql -e "INSTALL PLUGIN connection_control SONAME 'connection_control.so';"
mysql -e "INSTALL PLUGIN connection_control_failed_login_attempts SONAME 'connection_control.so';"
mysql -e "SHOW PLUGINS;"
mysql -e "CREATE DATABASE world;"
sed -i '18,21 s/^/-- /' /package-testing/world.sql
cat /package-testing/world.sql | mysql -D world
if [ ! -z "$1" ]; then
  if [ "$1" = "ps" ]; then
    mysql -e "CREATE DATABASE world2;"
    mysql -e "CREATE DATABASE world3;"
    cat /package-testing/world.sql | mysql -D world2
    cat /package-testing/world.sql | mysql -D world3
    mysql < /package-testing/tokudb_compression.sql
  fi
fi

#ERRORS_AFTER=$(grep -c "\[ERROR\]" ${ERROR_LOG} || true)
ERRORS_AFTER=$(grep "\[ERROR\]" ${ERROR_LOG} | grep -v "keyring_vault" -c || true)
if [ "${ERRORS_BEFORE}" != "${ERRORS_AFTER}" ]; then
  echo "There's a difference in number of errors before installing plugins and after!"
  exit 1
fi

WARNINGS_AFTER=$(grep -c "\[Warning\]" ${ERROR_LOG} || true)
if [ "${WARNINGS_BEFORE}" != "${WARNINGS_AFTER}" ]; then
  echo "There's a difference in number of warnings before installing plugins and after!"
  exit 1
fi
