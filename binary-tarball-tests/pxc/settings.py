#!/usr/bin/env python3
import os

base_dir = os.getenv('BASE_DIR')
pxc_version = os.getenv('PXC_VERSION')
pxc_revision = os.getenv('PXC_REVISION')
wsrep_version = os.getenv('WSREP_VERSION')

pxc_version_percona = pxc_version.split('-')[0]
pxc_version_major = pxc_version_percona.split('.')[0] + '.' + pxc_version_percona.split('.')[1]
if pxc_version_major != "8.0":
  pxc57_client_version = pxc_version.split('-')[0] + '-' + pxc_version.split('-')[1]
  pxc57_server_version = pxc_version.split('-')[0] + '-rel' + pxc_version.split('-')[1] + '-' + pxc_version.split('-')[
    2]

# 8.0
pxc80_binaries = (
  'bin/clustercheck', 'bin/garbd', 'bin/wsrep_sst_common', 'bin/wsrep_sst_xtrabackup-v2',
  'bin/pxc_extra/pxb-2.4/bin/xtrabackup', 'bin/pxc_extra/pxb-2.4/bin/xbcloud', 'bin/pxc_extra/pxb-2.4/bin/xbcloud_osenv',
  'bin/pxc_extra/pxb-2.4/bin/xbcrypt', 'bin/pxc_extra/pxb-2.4/bin/xbstream',
  'bin/pxc_extra/pxb-8.0/bin/xtrabackup', 'bin/pxc_extra/pxb-8.0/bin/xbcloud', 'bin/pxc_extra/pxb-8.0/bin/xbcloud_osenv',
  'bin/pxc_extra/pxb-8.0/bin/xbcrypt', 'bin/pxc_extra/pxb-8.0/bin/xbstream',
  'bin/mysql', 'bin/mysqld', 'bin/ps-admin', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqldumpslow', 'bin/mysqlimport', 'bin/mysqlpump', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor', 'bin/mysql_config',
  'bin/mysqlrouter', 'bin/mysqlrouter_passwd', 'bin/mysqlrouter_plugin_info', 'bin/mysql_secure_installation', 'bin/mysql_ssl_rsa_setup',
  'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
)
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
  'lib/libgalera_smm.so', 'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.21.1.21' ,
  'lib/libmysqlservices.a' , 'lib/plugin/audit_log.so',
  'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so', 'lib/plugin/data_masking.so',
  'lib/plugin/data_masking.ini', 'lib/plugin/keyring_file.so',
  'lib/plugin/keyring_udf.so', 'lib/plugin/keyring_vault.so'
)
pxc80_symlinks = (
  ('lib/libcrypto.so','lib/private/libcrypto.so.1.0.2k'), ('lib/libfreebl3.so','lib/private/libfreebl3.so'),
  ('lib/libgcrypt.so','lib/private/libgcrypt.so.11.8.2'), ('lib/libgssapi_krb5.so','lib/private/libgssapi_krb5.so.2.2'),
  ('lib/libk5crypto.so','lib/private/libk5crypto.so.3.1'), ('lib/libkrb5.so','lib/private/libkrb5.so.3.3'),
  ('lib/libkrb5support.so','lib/private/libkrb5support.so.0.1'), ('lib/libnspr4.so','lib/private/libnspr4.so'),
  ('lib/libnss3.so','lib/private/libnss3.so'),  ('lib/libnssutil3.so','lib/private/libnssutil3.so'),
  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.21.1.20'), ('lib/libplc4.so','lib/private/libplc4.so'),
  ('lib/libplds4.so','lib/private/libplds4.so'), ('lib/libsasl2.so','lib/private/libsasl2.so.2.0.23'),
  ('lib/libsmime3.so','lib/private/libsmime3.so'), ('lib/libssl.so','lib/private/libssl.so.1.0.1e'),
  ('lib/libssl3.so','lib/private/libssl3.so'), ('lib/libtinfo.so','lib/private/libtinfo.so.5.7'),
)

# 5.7
pxc57_binaries = (
  'bin/clustercheck', 'bin/garbd', 'bin/wsrep_sst_common', 'bin/wsrep_sst_xtrabackup-v2',
  'bin/wsrep_sst_mysqldump', 'bin/wsrep_sst_rsync', 'bin/pyclustercheck',
  'bin/mysql', 'bin/mysqld', 'bin/ps-admin', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqldumpslow', 'bin/mysqlimport', 'bin/mysqlpump', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor', 'bin/mysql_config', 'bin/mysql_ldb',
  'bin/mysql_secure_installation', 'bin/mysql_ssl_rsa_setup', 'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
)
pxc57_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),
  ('rpl_semi_sync_slave','semisync_slave.so')
)
pxc57_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)
pxc57_files = (
  'lib/libgalera_smm.so', 'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.20.3.18' ,
  'lib/libmysqlservices.a' , 'lib/libcoredumper.a', 'lib/mysql/plugin/audit_log.so',
  'lib/mysql/plugin/auth_pam.so', 'lib/mysql/plugin/auth_pam_compat.so',
  'lib/mysql/plugin/keyring_file.so', 'lib/mysql/plugin/keyring_udf.so', 'lib/mysql/plugin/keyring_vault.so'
)
pxc57_symlinks = (
  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.20.3.18'), ('lib/libncurses.so','lib/private/libncurses.so.5.7'),
  ('lib/libcrypto.so','lib/private/libcrypto.so.1.0.1e'), ('lib/libssl.so','lib/private/libssl.so.1.0.1e'),
  ('lib/libk5crypto.so','lib/private/libk5crypto.so.3.1'), ('lib/libtinfo.so','lib/private/libtinfo.so.5.7'),
  ('lib/libsasl2.so','lib/private/libsasl2.so.2.0.23'), ('lib/libreadline.so','lib/private/libreadline.so.6.0'),
  ('lib/libperconaserverclient.so.20','lib/libperconaserverclient.so.20.3.18'), ('lib/libkrb5support.so','lib/private/libkrb5support.so.0.1'),
  ('lib/libkrb5.so','lib/private/libkrb5.so.3.3'), ('lib/libgssapi_krb5.so','lib/private/libgssapi_krb5.so.2.2')
)

# 5.6
pxc56_binaries = (
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog', 'bin/mysqldump',
  'bin/mysqldumpslow', 'bin/mysqlimport', 'bin/mysqlshow', 'bin/mysqlslap', 'bin/mysqlcheck',
  'bin/mysql_config_editor', 'bin/mysql_secure_installation', 'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql')
pxc56_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
pxc56_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER')
)
pxc56_files = (
  'lib/libHotBackup.so', 'lib/libmysqlservices.a',
  'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.18.1.0' ,'lib/mysql/libjemalloc.so.1',
  'lib/mysql/plugin/ha_tokudb.so', 'lib/mysql/plugin/audit_log.so',
  'lib/mysql/plugin/auth_pam.so', 'lib/mysql/plugin/auth_pam_compat.so', 'lib/mysql/plugin/tokudb_backup.so'
)
pxc56_symlinks = (
  ('lib/libperconaserverclient.so.18','lib/libperconaserverclient.so.18.1.0'),('lib/libperconaserverclient.so','lib/libperconaserverclient.so.18.1.0'),
  ('lib/libperconaserverclient_r.a','lib/libperconaserverclient.a'),('lib/libperconaserverclient_r.so','lib/libperconaserverclient.so.18.1.0'),
  ('lib/libperconaserverclient_r.so.18','lib/libperconaserverclient.so.18.1.0'),('lib/libperconaserverclient_r.so.18.1.0','lib/libperconaserverclient.so.18.1.0')
)
#####

if pxc_version_major == '8.0':
    pxc_binaries = pxc80_binaries
    pxc_plugins = pxc80_plugins
    pxc_functions = pxc80_functions
    pxc_files = pxc80_files
    pxc_symlinks = pxc80_symlinks
elif pxc_version_major == '5.7':
    pxc_binaries = pxc57_binaries
    pxc_plugins = pxc57_plugins
    pxc_functions = pxc57_functions
    pxc_files = pxc57_files
    pxc_symlinks = pxc57_symlinks
elif pxc_version_major == '5.6':
    pxc_binaries = pxc56_binaries
    pxc_plugins = pxc56_plugins
    pxc_functions = pxc56_functions
    pxc_files = pxc56_files
    pxc_symlinks = pxc56_symlinks
