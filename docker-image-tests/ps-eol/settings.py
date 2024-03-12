#!/usr/bin/env python3
import os
import re

tag = os.getenv('TAG')
ps_version = os.getenv('PS_VERSION')
ps_revision = os.getenv('PS_REVISION')
docker_image = "percona/percona-server:" + tag
ps_version_upstream = ps_version.split('-')[0]
ps_version_percona1 = ps_version.split('-')[1]
ps_version_percona = ps_version_percona1.split('.')[0]

# 5.7
ps57_packages = (
  'Percona-Server-client-57', 'Percona-Server-rocksdb-57', 'Percona-Server-server-57',
  'Percona-Server-shared-57', 'Percona-Server-tokudb-57'
)
ps57_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/ps-admin', '/usr/bin/mysqladmin', '/usr/bin/mysqlbinlog',
  '/usr/sbin/mysqld-debug', '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow', '/usr/bin/mysqlimport', '/usr/bin/mysqlpump',
  '/usr/bin/mysqlshow', '/usr/bin/mysqlslap', '/usr/bin/mysqlcheck', '/usr/bin/mysql_config_editor', '/usr/bin/mysql_config',
  '/usr/bin/mysql_config-64', '/usr/bin/mysql_ldb', '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_ssl_rsa_setup', '/usr/bin/mysql_upgrade',
  '/usr/bin/mysql_tzinfo_to_sql'
)
ps57_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
ps57_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)
ps57_components = ()

ps_packages = ps57_packages
ps_binaries = ps57_binaries
ps_plugins = ps57_plugins
ps_functions = ps57_functions
ps_components = ps57_components

ps_pwd = 'pwd1234#'
