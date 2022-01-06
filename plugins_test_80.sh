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

WARNINGS_BEFORE=$(grep -c "\[Warning\]" ${ERROR_LOG} || true)
ERRORS_BEFORE=$(grep -c "\[ERROR\]" ${ERROR_LOG} || true)

mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "INSTALL PLUGIN audit_log SONAME 'audit_log.so';"
mysql -e "CREATE FUNCTION version_tokens_set RETURNS STRING SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_show RETURNS STRING SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_edit RETURNS STRING SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_delete RETURNS STRING SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_lock_shared RETURNS INT SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_lock_exclusive RETURNS INT SONAME 'version_token.so';"
mysql -e "CREATE FUNCTION version_tokens_unlock RETURNS INT SONAME 'version_token.so';"
mysql -e "INSTALL PLUGIN mysql_no_login SONAME 'mysql_no_login.so';"
mysql -e "CREATE FUNCTION service_get_read_locks RETURNS INT SONAME 'locking_service.so';"
mysql -e "CREATE FUNCTION service_get_write_locks RETURNS INT SONAME 'locking_service.so';"
mysql -e "CREATE FUNCTION service_release_locks RETURNS INT SONAME 'locking_service.so';"
mysql -e "INSTALL PLUGIN validate_password SONAME 'validate_password.so';"
mysql -e "INSTALL PLUGIN version_tokens SONAME 'version_token.so';"
#mysql -e "INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';"
#mysql -e "INSTALL PLUGIN rpl_semi_sync_replica SONAME 'semisync_replica.so';"
#mysql -e "INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';"
#mysql -e "INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';"
mysql -e "INSTALL PLUGIN connection_control SONAME 'connection_control.so';"
mysql -e "INSTALL PLUGIN connection_control_failed_login_attempts SONAME 'connection_control.so';"
mysql -e "INSTALL PLUGIN authentication_ldap_simple SONAME 'authentication_ldap_simple.so';"
mysql -e "INSTALL PLUGIN binlog_utils_udf SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_binlog_by_gtid RETURNS STRING SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_last_gtid_from_binlog RETURNS STRING SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_gtid_set_by_binlog RETURNS STRING SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_binlog_by_gtid_set RETURNS STRING SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_first_record_timestamp_by_binlog RETURNS STRING SONAME 'binlog_utils_udf.so';"
mysql -e "CREATE FUNCTION get_last_record_timestamp_by_binlog RETURNS STRING SONAME 'binlog_utils_udf.so';"

for component in component_validate_password component_log_sink_syseventlog component_log_sink_json component_log_filter_dragnet component_audit_api_message_emit; do
  if [ $(mysql -Ns -e "select count(*) from mysql.component where component_urn=\"file://${component}\";") -eq 0 ]; then
    mysql -e "INSTALL COMPONENT \"file://${component}\";"
  fi
  if [ $(mysql -Ns -e "select count(*) from mysql.component where component_urn=\"file://${component}\";") -ne 1 ]; then
    echo "MySQL Component ${component} failed to install!"
    exit 1
  fi
done

mysql -e "SHOW PLUGINS;"
mysql -e "CREATE DATABASE IF NOT EXISTS world;"
sed -i '18,21 s/^/-- /' /package-testing/world.sql
cat /package-testing/world.sql | mysql -D world
if [ ! -z "$1" ]; then
  if [ "$1" = "ps" ]; then
    mysql -e "CREATE DATABASE IF NOT EXISTS world2;"
    mysql -e "CREATE DATABASE IF NOT EXISTS world3;"
    cat /package-testing/world.sql | mysql -D world2
    cat /package-testing/world.sql | mysql -D world3
    mysql < /package-testing/tokudb_compression.sql
    mysql < /package-testing/rocksdb_test.sql
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
