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
                # Remove leading/trailing whitespace and skip comments or empty lines
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    # Split the line into key and value
                    key, value = line.split('=', 1)
                    # Remove any surrounding quotes from the value
                    value = value.strip('\'"')
                    # Add to os.environ
                    os.environ[key] = value
                    print(f'{line}')
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Error while sourcing environment file: {e}")

def set_pro_fips_vars():
    """
    Retrieves and returns environment-based settings for PRO, DEBUG, and FIPS_SUPPORTED.
    """
    source_environment_file()

    value = os.getenv('PRO', '').strip().lower()  # Normalize the input
    pro = value in {"yes", "true", "1"}

    print(pro)  # True if value is "yes", "true", or "1", otherwise False

    fips_supported = True if os.getenv('PRO') == "yes" else False
    #fips_supported = os.getenv('FIPS_SUPPORTED') in {"yes", "True"}
    debug = '-debug' if os.getenv('DEBUG') == "yes" else ''
    ps_revision = os.getenv('PS_REVISION')
    ps_version = os.getenv('PS_VERSION')


    if (os.getenv('PRO')):
      base_dir = '/usr/percona-server'
      print(f"PRINTING THE PRO VALUE PRO: {pro}")
    else:
      base_dir = os.getenv('BASE_DIR')


    if pro:
      print(f"TRUE PRO VAR WORKING")
    else:
      print(f"FALSE PRO VAR NOT WORKING")

    ps_version_upstream, ps_version_percona = ps_version.split('-')
    ps_version_major = ps_version_upstream.split('.')[0] + '.' + ps_version_upstream.split('.')[1]

    return {
        'pro': pro,
        'debug': debug,
        'fips_supported': fips_supported,
        'ps_revision': ps_revision,
        'ps_version': ps_version,
        'base_dir': base_dir,
        'ps_version_upstream': ps_version_upstream,
        'ps_version_major': ps_version_major,
        'ps_version_percona': ps_version_percona
    }

@pytest.fixture(scope="module")
def pro_fips_vars():
    """
    Fixture that provides environment-based settings for PRO, DEBUG, and FIPS_SUPPORTED.
    """
    return set_pro_fips_vars()


source_environment_file()


base_dir = os.getenv('BASE_DIR')
ps_version = os.getenv('PS_VERSION')
ps_revision = os.getenv('PS_REVISION')

ps_version_upstream, ps_version_percona = ps_version.split('-')
ps_version_major = ps_version_upstream.split('.')[0] + '.' + ps_version_upstream.split('.')[1]

print("Before variable prints")  # Debugging statement

# 8.0
ps80_binaries = [
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlpump', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor',
  'bin/mysqlrouter', 'bin/mysqlrouter_passwd', 'bin/mysqlrouter_plugin_info', 'bin/mysql_secure_installation', 'bin/mysql_ssl_rsa_setup',
  'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
]
ps80_executables = ps80_binaries + [
  'bin/ps-admin',
  'bin/mysqldumpslow',
  'bin/mysql_config',
]
ps80_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('clone','mysql_clone.so'),('data_masking','data_masking.so'), ('procfs', 'procfs.so')
)
ps80_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT'), ('get_binlog_by_gtid', 'binlog_utils_udf.so', 'STRING'), ('get_last_gtid_from_binlog', 'binlog_utils_udf.so', 'STRING'),
  ('get_gtid_set_by_binlog', 'binlog_utils_udf.so', 'STRING'), ('get_binlog_by_gtid_set', 'binlog_utils_udf.so', 'STRING'), ('get_first_record_timestamp_by_binlog', 'binlog_utils_udf.so', 'STRING'),
  ('get_last_record_timestamp_by_binlog', 'binlog_utils_udf.so', 'STRING')
)

ps80_components = (
  'component_masking_functions', 'component_encryption_udf', 'component_keyring_kmip', 'component_keyring_kms',
)
ps80_files = (
  'lib/libcoredumper.a',
  'lib/mysqlrouter/private/libmysqlrouter_http.so.1', 'lib/mysqlrouter/private/libmysqlrouter.so.1', 'lib/libmysqlservices.a',
  'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.21.2.42' ,'lib/mysql/libjemalloc.so.1',
  'lib/plugin/ha_rocksdb.so', 'lib/plugin/audit_log.so',
  'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so', 'lib/plugin/data_masking.so',
  'lib/plugin/data_masking.ini','lib/plugin/keyring_file.so',
  'lib/plugin/keyring_udf.so', 'lib/plugin/keyring_vault.so', 'lib/plugin/binlog_utils_udf.so',
  'lib/plugin/audit_log_filter.so', 'lib/plugin/component_masking_functions.so', 'lib/plugin/component_percona_telemetry.so'
)
ps80_symlinks = (
  ('lib/libperconaserverclient.so.21','lib/libperconaserverclient.so.21.2.42'),
  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.21.2.42'),('lib/mysql/libjemalloc.so','lib/mysql/libjemalloc.so.1')
)
ps80_openssl_files = (
  'lib/libcrypto.so', 'lib/libk5crypto.so', 'lib/libssl.so', 'lib/libsasl2.so'
)
# 5.7
ps57_binaries = [
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlpump', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor', 'bin/mysql_ldb',
  'bin/mysql_secure_installation', 'bin/mysql_ssl_rsa_setup', 'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
]
ps57_executables = ps57_binaries + [
  'bin/ps-admin',
  'bin/mysqldumpslow',
  'bin/mysql_config',
]
ps57_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
)
ps57_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER'),
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'),
  ('service_release_locks', 'locking_service.so', 'INT')
)
ps57_files = (
  'lib/libHotBackup.so', 'lib/libmysqlservices.a', 'lib/libcoredumper.a',
  'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.20.3.31' ,'lib/mysql/libjemalloc.so.1',
  'lib/mysql/plugin/ha_tokudb.so', 'lib/mysql/plugin/ha_rocksdb.so', 'lib/mysql/plugin/audit_log.so',
  'lib/mysql/plugin/auth_pam.so', 'lib/mysql/plugin/auth_pam_compat.so', 'lib/mysql/plugin/tokudb_backup.so',
  'lib/mysql/plugin/keyring_file.so', 'lib/mysql/plugin/keyring_udf.so', 'lib/mysql/plugin/keyring_vault.so'
)
ps57_symlinks = (
  ('lib/libperconaserverclient.so.20','lib/libperconaserverclient.so.20.3.31'),
  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.20.3.31')
)

# 5.6
ps56_binaries = [
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog', 'bin/mysqldump',
  'bin/mysqlimport', 'bin/mysqlshow', 'bin/mysqlslap', 'bin/mysqlcheck',
  'bin/mysql_config_editor', 'bin/mysql_upgrade', 'bin/mysql_tzinfo_to_sql'
]
ps56_executables = ps56_binaries + [
  'bin/mysqldumpslow',
]
ps56_plugins = (
  ('audit_log','audit_log.so'),('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so')
)
ps56_functions = (
  ('fnv1a_64', 'libfnv1a_udf.so', 'INTEGER'),('fnv_64', 'libfnv_udf.so', 'INTEGER'),('murmur_hash', 'libmurmur_udf.so', 'INTEGER')
)
ps56_files = (
  'lib/libHotBackup.so', 'lib/libmysqlservices.a',
  'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.18.1.0' ,'lib/mysql/libjemalloc.so.1',
  'lib/mysql/plugin/ha_tokudb.so', 'lib/mysql/plugin/audit_log.so',
  'lib/mysql/plugin/auth_pam.so', 'lib/mysql/plugin/auth_pam_compat.so', 'lib/mysql/plugin/tokudb_backup.so'
)
ps56_symlinks = (
  ('lib/libperconaserverclient.so.18','lib/libperconaserverclient.so.18.1.0'),('lib/libperconaserverclient.so','lib/libperconaserverclient.so.18.1.0'),
  ('lib/libperconaserverclient_r.a','lib/libperconaserverclient.a'),('lib/libperconaserverclient_r.so','lib/libperconaserverclient.so.18.1.0'),
  ('lib/libperconaserverclient_r.so.18','lib/libperconaserverclient.so.18.1.0'),('lib/libperconaserverclient_r.so.18.1.0','lib/libperconaserverclient.so.18.1.0')
)

# 8.x
ps8x_binaries = [
  'bin/mysql', 'bin/mysqld', 'bin/mysqladmin', 'bin/mysqlbinlog',
  'bin/mysqldump', 'bin/mysqlimport', 'bin/mysqlshow',
  'bin/mysqlslap', 'bin/mysqlcheck', 'bin/mysql_config_editor',
  'bin/mysqlrouter', 'bin/mysqlrouter_passwd', 'bin/mysqlrouter_plugin_info', 'bin/mysql_secure_installation',
  'bin/mysql_tzinfo_to_sql'
]
ps8x_executables = ps8x_binaries + [
  'bin/ps-admin',
  'bin/mysqldumpslow',
  'bin/mysql_config',
]
ps8x_plugins = (
  ('mysql_no_login','mysql_no_login.so'),('validate_password','validate_password.so'),
  ('version_tokens','version_token.so'),('rpl_semi_sync_master','semisync_master.so'),('rpl_semi_sync_slave','semisync_slave.so'),
  ('group_replication','group_replication.so'),('clone','mysql_clone.so'),
  ('procfs', 'procfs.so')
)
ps8x_functions = (
  ('version_tokens_set', 'version_token.so', 'STRING'),('version_tokens_show', 'version_token.so', 'STRING'),('version_tokens_edit', 'version_token.so', 'STRING'),
  ('version_tokens_delete', 'version_token.so', 'STRING'),('version_tokens_lock_shared', 'version_token.so', 'INT'),('version_tokens_lock_exclusive', 'version_token.so', 'INT'),
  ('version_tokens_unlock', 'version_token.so', 'INT'),('service_get_read_locks', 'locking_service.so', 'INT'),('service_get_write_locks', 'locking_service.so', 'INT'), ('service_release_locks', 'locking_service.so', 'INT')
)

ps8x_components = (
  'component_masking_functions', 'component_binlog_utils_udf', 'component_percona_udf', 'component_audit_log_filter', 'component_keyring_vault'
)

ps8x_files = (
  'lib/libcoredumper.a', 
  'lib/mysqlrouter/private/libmysqlrouter_http.so.1', 'lib/mysqlrouter/private/libmysqlrouter.so.1', 'lib/libmysqlservices.a',
  'lib/libperconaserverclient.a', 'lib/libperconaserverclient.so.24.0.5' ,'lib/mysql/libjemalloc.so.1',
  'lib/plugin/ha_rocksdb.so', 'lib/plugin/auth_pam.so', 'lib/plugin/auth_pam_compat.so',
  'lib/plugin/component_binlog_utils_udf.so',
  'lib/plugin/keyring_udf.so', 'lib/plugin/component_keyring_vault.so', 'lib/plugin/component_binlog_utils_udf.so',
  'lib/plugin/component_audit_log_filter.so', 'lib/plugin/component_masking_functions.so'
)

ps8x_symlinks = (
  ('lib/libperconaserverclient.so.24','lib/libperconaserverclient.so.24.0.5'),
  ('lib/libperconaserverclient.so','lib/libperconaserverclient.so.24.0.5'),('lib/mysql/libjemalloc.so','lib/mysql/libjemalloc.so.1')
)

ps8x_openssl_files = (
  'lib/libcrypto.so', 'lib/libk5crypto.so', 'lib/libssl.so', 'lib/libsasl2.so'
)

#####

if re.match(r'^8\.[1-9]$', ps_version_major):
    ps_binaries = ps8x_binaries
    ps_executables = ps8x_executables
    ps_plugins = ps8x_plugins
    ps_functions = ps8x_functions
    ps_files = ps8x_files
    ps_symlinks = ps8x_symlinks
    ps_components = ps8x_components
    ps_openssl_files=ps8x_openssl_files
elif ps_version_major == '8.0':
    ps_binaries = ps80_binaries
    ps_executables = ps80_executables
    ps_plugins = ps80_plugins
    ps_functions = ps80_functions
    ps_files = ps80_files
    ps_symlinks = ps80_symlinks
    ps_components = ps80_components
    ps_openssl_files=ps80_openssl_files
elif ps_version_major == '5.7':
    ps_binaries = ps57_binaries
    ps_executables = ps57_executables
    ps_plugins = ps57_plugins
    ps_functions = ps57_functions
    ps_files = ps57_files
    ps_symlinks = ps57_symlinks
elif ps_version_major == '5.6':
    ps_binaries = ps56_binaries
    ps_executables = ps56_executables
    ps_plugins = ps56_plugins
    ps_functions = ps56_functions
    ps_files = ps56_files
    ps_symlinks = ps56_symlinks
