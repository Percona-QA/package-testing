#!/usr/bin/env python3
import os

docker_acc = os.getenv('DOCKER_ACC')
ps_version = os.getenv('PS_VERSION')
ps_revision = os.getenv('PS_REVISION')

ps_version_upstream, ps_version_percona = ps_version.split('-')
ps_version_major = ps_version_upstream.split('.')[0] + '.' + ps_version_upstream.split('.')[1]

docker_product = 'percona-server'
docker_tag = ps_version
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag

# 8.0
ps80_packages = (
  'percona-server-client', 'percona-server-rocksdb', 'percona-server-server',
  'percona-server-shared', 'percona-server-shared-compat'
)
ps80_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/ps-admin', '/usr/bin/mysqladmin', '/usr/bin/mysqlbinlog',
  '/usr/sbin/mysqld-debug', '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow', '/usr/bin/mysqlimport', '/usr/bin/mysqlpump',
  '/usr/bin/mysqlshow', '/usr/bin/mysqlslap', '/usr/bin/mysqlcheck', '/usr/bin/mysql_config_editor', '/usr/bin/mysql_config',
  '/usr/bin/mysql_config-64', '/usr/bin/mysql_ldb', '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_ssl_rsa_setup', '/usr/bin/mysql_upgrade',
  '/usr/bin/mysql_tzinfo_to_sql'
)
ps80_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('group_replication','group_replication.so'),('clone','mysql_clone.so'),('data_masking','data_masking.so')
)
ps80_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)

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

# 5.6
ps56_packages = (
  'Percona-Server-client-56', 'Percona-Server-server-56', 'Percona-Server-shared-56',
  'Percona-Server-tokudb-56'
)
ps56_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/mysqladmin', '/usr/bin/mysqlbinlog', '/usr/sbin/mysqld-debug',
  '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow', '/usr/bin/mysqlimport', '/usr/bin/mysqlshow', '/usr/bin/mysqlslap',
  '/usr/bin/mysqlcheck', '/usr/bin/mysql_config_editor', '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_upgrade', '/usr/bin/mysql_tzinfo_to_sql'
)
ps56_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
ps56_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER')
)
#####

if ps_version_major == '8.0':
    ps_packages = ps80_packages
    ps_binaries = ps80_binaries
    ps_plugins = ps80_plugins
    ps_functions = ps80_functions
elif ps_version_major == '5.7':
    ps_packages = ps57_packages
    ps_binaries = ps57_binaries
    ps_plugins = ps57_plugins
    ps_functions = ps57_functions
elif ps_version_major == '5.6':
    ps_packages = ps56_packages
    ps_binaries = ps56_binaries
    ps_plugins = ps56_plugins
    ps_functions = ps56_functions

ps_pwd = 'pwd1234#'
