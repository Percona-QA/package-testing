#!/usr/bin/env python3
import os
import re

base_dir = os.getenv('BASE_DIR')
pxc_version = os.getenv('PXC_VERSION')
pxc_revision = os.getenv('PXC_REVISION')
pxc57_pkg_version = os.getenv('PXC57_PKG_VERSION')
wsrep_version = os.getenv('WSREP_VERSION')
glibc_version = os.getenv('GLIBC_VERSION')

pxc_version_percona = pxc_version.split('-')[0]
pxc_version_major = pxc_version_percona.split('.')[0] + '.' + pxc_version_percona.split('.')[1]

  
# 8.0
pxc80_binaries = [
  'bin/garbd',
  'bin/pxc_extra/pxb-2.4/bin/xtrabackup', 'bin/pxc_extra/pxb-2.4/bin/xbcloud',
  'bin/pxc_extra/pxb-2.4/bin/xbcrypt', 'bin/pxc_extra/pxb-2.4/bin/xbstream',
  'bin/pxc_extra/pxb-8.0/bin/xtrabackup', 'bin/pxc_extra/pxb-8.0/bin/xbcloud',
  'bin/pxc_extra/pxb-8.0/bin/xbcrypt', 'bin/pxc_extra/pxb-8.0/bin/xbstream',
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlpump', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor',
  'bin/mysqlrouter', 'bin/mysqlrouter_passwd', 'bin/mysqlrouter_plugin_info', 'bin/mysql_secure_installation', 'bin/mysql_ssl_rsa_setup',
  'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
]
pxc80_executables = pxc80_binaries + [
  'bin/clustercheck', 'bin/wsrep_sst_common', 'bin/wsrep_sst_xtrabackup-v2',
  'bin/pxc_extra/pxb-2.4/bin/xbcloud_osenv',
  'bin/pxc_extra/pxb-8.0/bin/xbcloud_osenv',
  'bin/ps-admin',
  'bin/mysqldumpslow',
  'bin/mysql_config',
]
pxc80_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('clone','mysql_clone.so'),('data_masking','data_masking.so')
)
pxc80_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)
pxc80_files = (
  'lib/libgalera_smm.so', 'lib/libperconaserverclient.a',
  'lib/libmysqlservices.a' , 'lib/plugin/audit_log.so',
  'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so', 'lib/plugin/data_masking.so',
  'lib/plugin/data_masking.ini', 'lib/plugin/keyring_file.so',
  'lib/plugin/keyring_udf.so', 'lib/plugin/keyring_vault.so'
)
pxc80_symlinks = (
    ('lib/libnuma.so','lib/private/libnuma.so.1.0.0'), ('lib/libaio.so','lib/private/libaio.so.1.0.1'),
    ('lib/libboost_program_options.so','lib/private/libboost_program_options.so.1.66.0'),
    ('lib/libldap_r-2.4','lib/private/libldap_r-2.4.so.2.10.9'), ('lib/libtinfo.so','lib/private/libtinfo.so.6.1'),
    ('lib/liblber-2.4','lib/private/liblber-2.4.so.2.10.9'),
    ('lib/libtirpc.so','lib/private/libtirpc.so.3.0.0'), ('lib/libsasl2.so','lib/private/libsasl2.so.3.0.0')
)

pxc_binaries = pxc80_binaries
pxc_executables = pxc80_executables
pxc_plugins = pxc80_plugins
pxc_functions = pxc80_functions
pxc_files = pxc80_files
pxc_symlinks = pxc80_symlinks
