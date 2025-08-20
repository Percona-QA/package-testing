#!/usr/bin/env python3
import os
import re
import pytest


def source_environment_file(filepath="/etc/environment"):
    """
    Loads environment variables from a given file into os.environ.

    :param filepath: Path to the environment file (default is /etc/environment).
    """
    try:
        with open(filepath, 'r') as file:
          for line in file:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip('\'"')
                os.environ[key] = value
                print(f'{line}')
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Error while sourcing environment file: {e}")

def set_pro_vars():
    """
    Retrieves and returns environment-based settings for PRO, DEBUG, and FIPS_SUPPORTED.
    """
    source_environment_file()
    value = os.getenv('PRO', '').strip().lower()  # Normalize the input
    pro = value in {"yes", "true", "1"} 
    pxc_revision = os.getenv('PXC_REVISION')
    pxc_version = os.getenv('PXC_VERSION')

    if (os.getenv('PRO')):
        base_dir = os.getenv('BASE_DIR')
        print(f"PRINTING THE PRO VALUE PRO: {pro}")
    else:
      base_dir = os.getenv('BASE_DIR')

    if pro:
      print(f"TRUE PRO VAR WORKING")
    else:
      print(f"FALSE PRO VAR NOT WORKING")

    pxc57_pkg_version = os.getenv('PXC57_PKG_VERSION')
    wsrep_version = os.getenv('WSREP_VERSION')
    glibc_version = os.getenv('GLIBC_VERSION')
    pxc_version_percona,pxc_version_upstream = pxc_version.split('-')
    pxc_version_pro_percona = ".".join(pxc_version.split(".")[:-1])
    pxc_version_major = pxc_version_percona.split('.')[0] + '.' + pxc_version_percona.split('.')[1]
    TARBALL_NAME = os.getenv('TARBALL_NAME')

    return {
        'pro': pro,
        #'debug': debug,
        #'fipxc_supported': fipxc_supported,
        'pxc_revision': pxc_revision,
        'pxc_version': pxc_version,
        'base_dir': base_dir,
        'pxc_version_upstream': pxc_version_upstream,
        'pxc_version_major': pxc_version_major,
        'pxc_version_percona': pxc_version_percona,
        'pxc57_pkg_version': pxc57_pkg_version,
        'wsrep_version': wsrep_version,
        'glibc_version': glibc_version,
        'pxc_version_pro_percona': pxc_version_pro_percona,
        'TARBALL_NAME' : TARBALL_NAME
    }

source_environment_file()
vars = set_pro_vars()
pro = vars['pro']
pxc_revision = vars['pxc_revision']
pxc_version = vars['pxc_version']
base_dir = vars['base_dir']
pxc_version_upstream = vars['pxc_version_upstream']
pxc_version_major = vars['pxc_version_major']
pxc_version_percona = vars['pxc_version_percona']
pxc57_pkg_version = vars['pxc57_pkg_version']
glibc_version = vars['glibc_version']
pxc_version_pro_percona = vars['pxc_version_pro_percona']
wsrep_version = vars['wsrep_version']  
TARBALL_NAME = vars['TARBALL_NAME']

if pxc_version_major == "5.7":
    print(pxc_version)
    print(pxc57_pkg_version)
    pxc57_client_version = pxc57_pkg_version.split('-')[0] + '-' + pxc57_pkg_version.split('-')[1][3:]
    pxc57_server_version_norel = pxc57_pkg_version.split('-')[0] + '-' + pxc57_pkg_version.split('-')[1][3:] + '-' + pxc57_pkg_version.split('-')[2].split('.')[0]
    pxc57_server_version = pxc57_pkg_version.split('-')[0] + '-' + pxc57_pkg_version.split('-')[1] + '-' + pxc57_pkg_version.split('-')[2].split('.')[0]
    pxc57_client_version_using = "8.1"

# 8.X
pxc8x_binaries = [
    'bin/garbd',
    'bin/pxc_extra/pxb-8.0/bin/xtrabackup', 'bin/pxc_extra/pxb-8.0/bin/xbcloud',
    'bin/pxc_extra/pxb-8.0/bin/xbcrypt', 'bin/pxc_extra/pxb-8.0/bin/xbstream',
    'bin/pxc_extra/pxb-8.4/bin/xtrabackup', 'bin/pxc_extra/pxb-8.4/bin/xbcloud',
    'bin/pxc_extra/pxb-8.4/bin/xbcrypt', 'bin/pxc_extra/pxb-8.4/bin/xbstream',
    #'bin/pxc_extra/pxb-8.2/bin/xtrabackup', 'bin/pxc_extra/pxb-8.2/bin/xbcloud',
  # 'bin/pxc_extra/pxb-8.2/bin/xbcrypt', 'bin/pxc_extra/pxb-8.2/bin/xbstream',
    #'bin/pxc_extra/pxb-8.3/bin/xtrabackup', 'bin/pxc_extra/pxb-8.3/bin/xbcloud',
    #'bin/pxc_extra/pxb-8.3/bin/xbcrypt', 'bin/pxc_extra/pxb-8.3/bin/xbstream',
    'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
    'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlshow',
    'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor',
    'bin/mysqlrouter', 'bin/mysqlrouter_passwd', 'bin/mysqlrouter_plugin_info', 'bin/mysql_secure_installation',
    'bin/mysql_tzinfo_to_sql'
  ]
pxc8x_executables = pxc8x_binaries + [
    'bin/clustercheck', 'bin/wsrep_sst_common', 'bin/wsrep_sst_xtrabackup-v2',
    'bin/pxc_extra/pxb-8.0/bin/xbcloud_osenv',
    'bin/pxc_extra/pxb-8.4/bin/xbcloud_osenv',
    #'bin/pxc_extra/pxb-8.2/bin/xbcloud_osenv',
    #'bin/pxc_extra/pxb-8.3/bin/xbcloud_osenv',
    'bin/ps-admin',
    'bin/mysqldumpslow',
    'bin/mysql_config',
  ]
pxc8x_plugins = (
    ('validate_password','validate_password.so'),
    ('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
    ('clone','mysql_clone.so')
  )
pxc8x_functions = (
    ('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
    ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
    ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
    ('service_release_locks', 'locking_service.so', 'INT')
  )
pxc8x_files = (
    'lib/libgalera_smm.so', 'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.24.0.5' ,
    'lib/libmysqlservices.a' ,
    'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so', #'lib/plugin/keyring_file.so',
    'lib/plugin/keyring_udf.so'
  )
if glibc_version == '2.35':
    pxc8x_symlinks = (
   #   ('lib/libcrypto.so', 'lib/private/libcrypto.so.3'),('lib/libgcrypt.so', 'lib/private/libgcrypt.so.20.3.4',),
      ('lib/libperconaserverclient.so', 'lib/libperconaserverclient.so.24.0.5'),('lib/libsasl2.so', 'lib/private/libsasl2.so.3.0.0'),
    #  ('lib/libssl.so', 'lib/private/libssl.so.3'),
      ('lib/libtinfo.so', 'lib/private/libtinfo.so.6.3'),
      ('lib/libaio.so','lib/private/libaio.so.1.0.1'),('lib/libbrotlicommon.so', 'lib/private/libbrotlicommon.so.1.0.9'),
      ('lib/libbrotlidec.so', 'lib/private/libbrotlidec.so.1.0.9'), ('lib/libprocps.so', 'lib/private/libprocps.so.8.0.3'),
      #('lib/librtmp.so', 'lib/private/librtmp.so.1'),
      ('lib/libtirpc.so', 'lib/private/libtirpc.so.3.0.0')
    )
else:
    pxc8x_symlinks = (
      #   ('lib/libcrypto.so', 'lib/private/libcrypto.so.3'),('lib/libgcrypt.so', 'lib/private/libgcrypt.so.20.3.4',),
      ('lib/libperconaserverclient.so', 'lib/libperconaserverclient.so.24.0.5'),('lib/libsasl2.so', 'lib/private/libsasl2.so.3.0.0'),
    #  ('lib/libssl.so', 'lib/private/libssl.so.3'),
      ('lib/libtinfo.so', 'lib/private/libtinfo.so.6.2'),
      ('lib/libaio.so','lib/private/libaio.so.1.0.1'),('lib/libbrotlicommon.so', 'lib/private/libbrotlicommon.so.1.0.9'),
      ('lib/libbrotlidec.so', 'lib/private/libbrotlidec.so.1.0.9'), ('lib/libprocps.so', 'lib/private/libprocps.so.8.0.3'),
      #('lib/librtmp.so', 'lib/private/librtmp.so.1'), 
      ('lib/libtirpc.so', 'lib/private/libtirpc.so.3.0.0')
    #  ('lib/libcrypto.so','lib/private/libcrypto.so.1.0.2k'), ('lib/libfreebl3.so','lib/private/libfreebl3.so'),
    #  ('lib/libgcrypt.so','lib/private/libgcrypt.so.11.8.2'),
    #  ('lib/libnspr4.so','lib/private/libnspr4.so'),
    #  ('lib/libnss3.so','lib/private/libnss3.so'), ('lib/libnssutil3.so','lib/private/libnssutil3.so'),
    #  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.24.0.4'), ('lib/libplc4.so','lib/private/libplc4.so'),
    #  ('lib/libplds4.so','lib/private/libplds4.so'), ('lib/libsasl2.so','lib/private/libsasl2.so.3.0.0'),
    #  ('lib/libsmime3.so','lib/private/libsmime3.so'), ('lib/libssl.so','lib/private/libssl.so.1.0.2k'),
    #  ('lib/libssl3.so','lib/private/libssl3.so'), ('lib/libtinfo.so','lib/private/libtinfo.so.5.9'),
    )
pxc8x_components = (
    ('file://component_encryption_udf'),('file://component_keyring_kmip'),('file://component_keyring_kms'),('file://component_masking_functions'),('file://component_binlog_utils_udf'),('file://component_percona_udf'),('file://component_audit_log_filter'),('file://component_keyring_vault'),('file://component_binlog_uts_udf')
  )

  # 8.0
pxc80_binaries = [
    'bin/garbd',
    'bin/pxc_extra/pxb-2.4/bin/xtrabackup', 'bin/pxc_extra/pxb-2.4/bin/xbcloud',
    'bin/pxc_extra/pxb-2.4/bin/xbcrypt', 'bin/pxc_extra/pxb-2.4/bin/xbstream',
    'bin/pxc_extra/pxb-8.0/bin/xtrabackup', 'bin/pxc_extra/pxb-8.0/bin/xbcloud',
    'bin/pxc_extra/pxb-8.0/bin/xbcrypt', 'bin/pxc_extra/pxb-8.0/bin/xbstream',
    'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
    'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlshow', #'bin/mysqlpump', 
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
    'lib/libgalera_smm.so', 'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.21.2.42' ,
    'lib/libmysqlservices.a' , 'lib/plugin/audit_log.so',
    'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so', 'lib/plugin/data_masking.so',
    'lib/plugin/data_masking.ini', 'lib/plugin/keyring_file.so',
    'lib/plugin/keyring_udf.so', 'lib/plugin/keyring_vault.so'
  )
if glibc_version == '2.35':
    pxc80_symlinks = (
        #   ('lib/libcrypto.so', 'lib/private/libcrypto.so.3'),('lib/libgcrypt.so', 'lib/private/libgcrypt.so.20.3.4',),
      ('lib/libperconaserverclient.so', 'lib/libperconaserverclient.so.21.2.42'),('lib/libsasl2.so', 'lib/private/libsasl2.so.2.0.25'),
    #  ('lib/libssl.so', 'lib/private/libssl.so.3'),
      ('lib/libtinfo.so', 'lib/private/libtinfo.so.6.3'),
      ('lib/libaio.so','lib/private/libaio.so.1.0.1'),('lib/libbrotlicommon.so', 'lib/private/libbrotlicommon.so.1.0.9'),
      ('lib/libbrotlidec.so', 'lib/private/libbrotlidec.so.1.0.9'), ('lib/libprocps.so', 'lib/private/libprocps.so.8.0.3'),
      # ('lib/librtmp.so', 'lib/private/librtmp.so.1'),
    )
else:
    pxc80_symlinks = (
           #   ('lib/libcrypto.so', 'lib/private/libcrypto.so.3'),('lib/libgcrypt.so', 'lib/private/libgcrypt.so.20.3.4',),
      ('lib/libperconaserverclient.so', 'lib/libperconaserverclient.so.21.2.42'),('lib/libsasl2.so', 'lib/private/libsasl2.so.3.0.0'),
    #  ('lib/libssl.so', 'lib/private/libssl.so.3'),
      ('lib/libtinfo.so', 'lib/private/libtinfo.so.6.2'),
      ('lib/libaio.so','lib/private/libaio.so.1.0.1'),('lib/libbrotlicommon.so', 'lib/private/libbrotlicommon.so.1.0.9'),
      ('lib/libbrotlidec.so', 'lib/private/libbrotlidec.so.1.0.9'), ('lib/libprocps.so', 'lib/private/libprocps.so.8.0.3'),
      #('lib/librtmp.so', 'lib/private/librtmp.so.1'), 
     # ('lib/libtirpc.so', 'lib/private/libtirpc.so.3.0.0')
     # ('lib/libcrypto.so','lib/private/libcrypto.so.1.0.2k'), ('lib/libfreebl3.so','lib/private/libfreebl3.so'),

     # ('lib/libgcrypt.so','lib/private/libgcrypt.so.11.8.2'), ('lib/libnspr4.so','lib/private/libnspr4.so'),
    #  ('lib/libnss3.so','lib/private/libnss3.so'), ('lib/libnssutil3.so','lib/private/libnssutil3.so'),
     # ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.21.2.41'), ('lib/libplc4.so','lib/private/libplc4.so'),
      #('lib/libplds4.so','lib/private/libplds4.so'), ('lib/libsasl2.so','lib/private/libsasl2.so.3.0.0'),
      #('lib/libsmime3.so','lib/private/libsmime3.so'), ('lib/libssl.so','lib/private/libssl.so.1.0.2k'),
      #('lib/libssl3.so','lib/private/libssl3.so'), ('lib/libtinfo.so','lib/private/libtinfo.so.5.9'),
    )

  # 5.7
pxc57_binaries = [
    'bin/garbd', 'bin/innochecksum', 'bin/lz4_decompress', 'bin/my_print_defaults',
    'bin/myisam_ftdump','bin/myisamchk', 'bin/myisamlog', 'bin/myisampack', 'bin/mysql', 'bin/mysql_client_test',
    'bin/mysql_config_editor', 'bin/mysql_install_db', 'bin/mysql_plugin', 'bin/mysql_secure_installation',
    'bin/mysql_ssl_rsa_setup', 'bin/mysql_tzinfo_to_sql', 'bin/mysql_upgrade', 'bin/mysqladmin', 'bin/mysqlbinlog',
    'bin/mysqlcheck', 'bin/mysqld', 'bin/mysqldump',
    'bin/mysqlimport',  'bin/mysqlshow', 'bin/mysqlslap', 'bin/mysqltest', 'bin/mysqlxtest', 'bin/perror' ,'bin/mysqlpump',
    'bin/replace', 'bin/resolve_stack_dump',
    'bin/resolveip',
    'bin/zlib_decompress'
  ]
pxc57_executables = pxc57_binaries + [
    'bin/clustercheck',
    'bin/mysql_config',
    'bin/mysqld_multi', 'bin/mysqld_safe', 'bin/mysqldumpslow',
    'bin/ps-admin', 'bin/pxc_mysqld_helper', 'bin/pxc_tokudb_admin', 'bin/pyclustercheck',
    'bin/wsrep_sst_common', 'bin/wsrep_sst_mysqldump', 'bin/wsrep_sst_rsync', 'bin/wsrep_sst_xtrabackup-v2',
  ]
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
    'lib/libgalera_smm.so', 'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.20.3.31' ,
    'lib/libmysqlservices.a' , 'lib/libcoredumper.a', 'lib/mysql/plugin/audit_log.so',
    'lib/mysql/plugin/auth_pam.so', 'lib/mysql/plugin/auth_pam_compat.so',
    'lib/mysql/plugin/keyring_file.so', 'lib/mysql/plugin/keyring_udf.so', 'lib/mysql/plugin/keyring_vault.so'
  )
pxc57_symlinks = (
    ('lib/libperconaserverclient.so', 'lib/libperconaserverclient.so.20.3.31'),
    ('lib/libperconaserverclient.so.20','lib/libperconaserverclient.so.20.3.31'),
  )

  # 5.6
pxc56_binaries = [
    'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog', 'bin/mysqldump',
    'bin/mysqlimport', 'bin/mysqlshow', 'bin/mysqlslap', 'bin/mysqlcheck',
    'bin/mysql_config_editor', 'bin/mysql_secure_installation', 'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
  ]
pxc56_executables = pxc56_binaries + [
    'bin/mysqldumpslow'
  ]
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

if re.match(r'^8\.[1-9]$', pxc_version_major):
      pxc_binaries = pxc8x_binaries
      pxc_executables = pxc8x_executables
      pxc_plugins = pxc8x_plugins
      pxc_functions = pxc8x_functions
      pxc_files = pxc8x_files
      pxc_symlinks = pxc8x_symlinks
      pxc_components = pxc8x_components
elif pxc_version_major == '8.0':
      pxc_binaries = pxc80_binaries
      pxc_executables = pxc80_executables
      pxc_plugins = pxc80_plugins
      pxc_functions = pxc80_functions
      pxc_files = pxc80_files
      pxc_symlinks = pxc80_symlinks
elif pxc_version_major == '5.7':
      pxc_binaries = pxc57_binaries
      pxc_executables = pxc57_executables
      pxc_plugins = pxc57_plugins
      pxc_functions = pxc57_functions
      pxc_files = pxc57_files
      pxc_symlinks = pxc57_symlinks
elif pxc_version_major == '5.6':
      pxc_binaries = pxc56_binaries
      pxc_executables = pxc56_executables
      pxc_plugins = pxc56_plugins
      pxc_functions = pxc56_functions
      pxc_files = pxc56_files
      pxc_symlinks = pxc56_symlinks

def get_artifact_sets():
    vars = set_pro_vars()
    pxc_version_major = vars['pxc_version_major']
    if re.match(r'^8\.[1-9]$', pxc_version_major):
        return pxc8x_executables, pxc8x_files, pxc8x_symlinks
    elif pxc_version_major == '8.0':
        return pxc80_executables, pxc80_files, pxc80_symlinks
    elif pxc_version_major == '5.7':
        return pxc57_executables, pxc57_files, pxc57_symlinks
    elif pxc_version_major == '5.6':
        return pxc56_executables, pxc56_files, pxc56_symlinks
    else:
        raise ValueError(f"Unsupported PXC version: {pxc_version_major}")
