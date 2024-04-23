#!/usr/bin/env python3
import os

tag = os.getenv('TAG')
pxc_version = os.getenv('PXC_VERSION')
pxc_revision = os.getenv('PXC_REVISION')
pxc_pxb_version = os.getenv('PXC_PXB_VERSION')
pxc_wsrep_version = os.getenv('PXC_WSREP_VERSION')
test_pwd = os.path.dirname(os.path.realpath(__file__))
parts = tag.split("-")
tag_1 = "-".join(parts[:2])
docker_image = "percona/percona-xtradb-cluster:" + tag_1

pxc_version_upstream, pxc_version_percona = pxc_version.split('-')
pxc_version_major = pxc_version_upstream.split('.')[0] + '.' + pxc_version_upstream.split('.')[1]
pxc_rel=pxc_version_percona.split('.')[0]
pxc57_server_version_norel = pxc_version + '-' + pxc_version_major.replace('.', '')
pxc57_server_release = pxc_version.split('-')[1]
docker_network = 'pxc-network'
base_node_name = 'pxc-docker-test-cluster-node'
cluster_name = 'pxc-cluster1'

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

pxc_packages = pxc57_packages
pxc_binaries = pxc57_binaries
pxc_plugins = pxc57_plugins
pxc_functions = pxc57_functions

pxc_pwd = 'pwd1234#'
