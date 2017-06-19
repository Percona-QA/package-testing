#!/bin/bash
set -e
WARNINGS_BEFORE=0
WARNINGS_AFTER=0
ERROR_LOG=""
ERROR_LOG=$(mysql -N -s -e "show variables like 'log_error';" | grep -v "Warning:" | grep -o "\/.*$")
if [ ! -f ${ERROR_LOG} ]; then
  echo "Error log was not found!"
  exit 1
fi
WARNINGS_BEFORE=$(grep -c "\[Warning\]" ${ERROR_LOG})

mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "INSTALL PLUGIN auth_pam SONAME 'auth_pam.so';"
mysql -e "INSTALL PLUGIN audit_log SONAME 'audit_log.so';"
mysql -e "INSTALL PLUGIN handlersocket SONAME 'handlersocket.so';"
mysql -e "INSTALL PLUGIN scalability_metrics SONAME 'scalability_metrics.so';"
mysql -e "SHOW PLUGINS;"
mysql -e "CREATE DATABASE world;"
sed -i '18,21 s/^/-- /' /package-testing/world.sql
pv /package-testing/world.sql | mysql -D world

if [ "$(grep -c "\[ERROR\]" ${ERROR_LOG})" != "0" ]; then
  echo "There's an error in error log!"
  exit 1
fi

WARNINGS_AFTER=$(grep -c "\[Warning\]" ${ERROR_LOG})
if [ "${WARNINGS_BEFORE}" != "${WARNINGS_AFTER}" ]; then
  echo "There's a difference in number of warnings before installing plugins and after!"
  exit 1
fi
