#!/usr/bin/env python3
import os
import re

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
docker_image_major = docker_acc + "/" + docker_product + ":" + pxc_version_major
docker_image_latest = docker_acc + "/" + docker_product + ":" + "latest"
docker_image_debug = "${docker_acc}/${docker_product}:${docker_tag%-aarch64}-debug-aarch64"
docker_image_upstream = docker_acc + "/" + docker_product + ":" + pxc_version_upstream

docker_network = 'pxc-network'

base_node_name = 'pxc-docker-test-cluster-node'
cluster_name = 'pxc-cluster1'

# Innovation
pxc8x_packages = [(package, pxc_version_upstream) for package in (
  'percona-xtradb-cluster-client', 'percona-xtradb-cluster-server',
  'percona-xtradb-cluster-shared'
)]
pxc8x_binaries = (
  '/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/mysqladmin',
  '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow',
  '/usr/bin/mysql_secure_installation',
  '/usr/bin/mysql_tzinfo_to_sql','/usr/bin/mysql_keyring_encryption_test','/usr/bin/mysql_migrate_keyring',
  '/usr/bin/mysqld_multi','/usr/bin/mysqld_safe','/usr/bin/mysql-systemd',
  '/usr/bin/mysqlbinlog'
)
pxc8x_plugins = (
  ('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('group_replication','group_replication.so'),('clone','mysql_clone.so')
)
pxc8x_functions = (
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'), ('service_release_locks', 'locking_service.so', 'INT')
)
pxc8x_components = (
  ('file://component_encryption_udf'),('file://component_keyring_kmip'),('file://component_keyring_kms'),('file://component_masking_functions'),('file://component_binlog_utils_udf'),('file://component_percona_udf'),('file://component_audit_log_filter'),('file://component_keyring_vault')
)  

# 8.0
pxc80_packages = [(package, pxc_version_upstream) for package in (
  'percona-xtradb-cluster-client', 'percona-xtradb-cluster-server',
  'percona-xtradb-cluster-shared'
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
  ('group_replication','group_replication.so'),('clone','mysql_clone.so'),('binlog_utils_udf','binlog_utils_udf.so')
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
pxc80_components = (
  ('file://component_encryption_udf'),('file://component_keyring_kmip'),('file://component_keyring_kms'),('file://component_masking_functions')
)


if re.match(r'^8\.[1-9]$', pxc_version_major):
    pxc_packages = pxc8x_packages
    pxc_binaries = pxc8x_binaries
    pxc_plugins = pxc8x_plugins
    pxc_functions = pxc8x_functions
    pxc_components = pxc8x_components
elif pxc_version_major == '8.0':
    pxc_packages = pxc80_packages
    pxc_binaries = pxc80_binaries
    pxc_plugins = pxc80_plugins
    pxc_functions = pxc80_functions
    pxc_components = pxc80_components

pxc_pwd = 'pwd1234#'
