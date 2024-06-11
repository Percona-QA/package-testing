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
mysql -e "INSTALL PLUGIN connection_control SONAME 'connection_control.so';"
mysql -e "INSTALL PLUGIN connection_control_failed_login_attempts SONAME 'connection_control.so';"
mysql -e "INSTALL PLUGIN authentication_ldap_simple SONAME 'authentication_ldap_simple.so';"
mysql -e "INSTALL PLUGIN authentication_ldap_sasl SONAME 'authentication_ldap_sasl.so';"

if [ "$(grep "centos:7" /etc/os-release | wc -l)" = 1 ] || [ "$(grep "amazon_linux:2" /etc/os-release | wc -l) = 1" ]; then
  echo "authentication_fido plugin is not supported on CentOS 7"
else
  mysql -e "INSTALL PLUGIN authentication_fido SONAME 'authentication_fido.so';"
fi

mysql -e "INSTALL PLUGIN clone SONAME 'mysql_clone.so';"

for component in component_validate_password component_log_sink_syseventlog component_log_sink_json component_log_filter_dragnet component_audit_api_message_emit component_binlog_utils_udf component_percona_udf component_keyring_vault; do
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
