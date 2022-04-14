#!/usr/bin/env python3
import os

docker_acc = os.getenv('DOCKER_ACC')
docker_product = os.getenv('DOCKER_PRODUCT')
docker_tag = os.getenv('DOCKER_TAG')
pxc_version = os.getenv('PXC_VERSION')
pxc_revision = os.getenv('PXC_REVISION')
pxc57_pkg_version = os.getenv('PXC57_PKG_VERSION')
pxc_pxb_version = os.getenv('PXC_PXB_VERSION')
pxc_wsrep_version = os.getenv('PXC_WSREP_VERSION')
test_pwd = os.path.dirname(os.path.realpath(__file__))

pxc_version_upstream, pxc_version_percona = pxc_version.split('-')
pxc_version_major = pxc_version_upstream.split('.')[0] + '.' + pxc_version_upstream.split('.')[1]
pxc_rel=pxc_version_percona.split('.')[0]

if pxc_version_major == '5.7':
  pxc57_client_version = pxc57_pkg_version.split('-')[0] + '-' + pxc57_pkg_version.split('-')[1][3:]
  pxc57_server_release = pxc57_pkg_version.split('-')[1]
  pxc57_server_version_norel = pxc57_pkg_version.split('-')[0] + '-' + pxc57_pkg_version.split('-')[1][3:] + '-' + pxc_version_major.replace('.', '')

docker_image = docker_acc + "/" + docker_product + ":" + docker_tag
docker_network = 'pxc-network'

base_node_name = 'pxc-docker-test-cluster-node'
cluster_name = 'pxc-cluster1'

# 8.0
pxc80_packages = [(package, pxc_version_upstream) for package in (
  'percona-xtradb-cluster-client', 'percona-xtradb-cluster-server',
  'percona-xtradb-cluster-shared', 'percona-xtradb-cluster-shared-compat'
)]
pxc80_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/mysqladmin',
  '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow',
  '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_ssl_rsa_setup', '/usr/bin/mysql_upgrade',
  '/usr/bin/mysql_tzinfo_to_sql','/usr/bin/mysql_keyring_encryption_test','/usr/bin/mysql_migrate_keyring',
  '/usr/bin/mysqld_multi','/usr/bin/mysqld_safe','/usr/bin/mysql-systemd',
  '/usr/bin/mysqlbinlog'
)
pxc80_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('group_replication','group_replication.so'),('clone','mysql_clone.so'),('data_masking','data_masking.so'),
  ('binlog_utils_udf','binlog_utils_udf.so')

)
pxc80_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT'),
  ('get_gtid_set_by_binlog', 'binlog_utils_udf.so', 'STRING'), ('get_binlog_by_gtid_set', 'binlog_utils_udf.so', 'STRING'), ('get_first_record_timestamp_by_binlog', 'binlog_utils_udf.so', 'STRING'),
  ('get_last_record_timestamp_by_binlog', 'binlog_utils_udf.so', 'STRING')
)

# 5.7
pxc57_packages = (
  ('Percona-XtraDB-Cluster-shared-57', pxc_version_upstream),
  ('Percona-XtraDB-Cluster-server-57', pxc_version_upstream),
  ('Percona-XtraDB-Cluster-client-57', pxc_version_upstream),
  ('percona-xtrabackup-24', pxc_pxb_version)
)
pxc57_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld',
  '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow',
  '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_ssl_rsa_setup', '/usr/bin/mysql_upgrade',
  '/usr/bin/mysql_tzinfo_to_sql'
)
pxc57_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
pxc57_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)

# 5.6
pxc56_packages = [(package, pxc_version_upstream) for package in (
  'Percona-Server-client-56', 'Percona-Server-server-56', 'Percona-Server-shared-56',
  'Percona-Server-tokudb-56'
)]
pxc56_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/mysqladmin', '/usr/bin/mysqlbinlog', '/usr/sbin/mysqld-debug',
  '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow', '/usr/bin/mysqlimport', '/usr/bin/mysqlshow', '/usr/bin/mysqlslap',
  '/usr/bin/mysqlcheck', '/usr/bin/mysql_config_editor', '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_upgrade', '/usr/bin/mysql_tzinfo_to_sql'
)
pxc56_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
pxc56_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER')
)
#####

if pxc_version_major == '8.0':
    pxc_packages = pxc80_packages
    pxc_binaries = pxc80_binaries
    pxc_plugins = pxc80_plugins
    pxc_functions = pxc80_functions
elif pxc_version_major == '5.7':
    pxc_packages = pxc57_packages
    pxc_binaries = pxc57_binaries
    pxc_plugins = pxc57_plugins
    pxc_functions = pxc57_functions
elif pxc_version_major == '5.6':
    pxc_packages = pxc56_packages
    pxc_binaries = pxc56_binaries
    pxc_plugins = pxc56_plugins
    pxc_functions = pxc56_functions

pxc_pwd = 'pwd1234#'
