import os
import pytest
import testinfra.utils.ansible_runner
import re
from .settings import *
from packaging import version

VERSION = os.environ.get("VERSION")
DEB_PERCONA_BUILD_VERSION = ''
RPM_PERCONA_BUILD_VERSION = ''

REVISION = os.environ.get('PS_REVISION')

if re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', VERSION): # if full package VERSION 8.0.32-24.2 is passed we need to re-assign it for tests
    DEB_PERCONA_BUILD_VERSION = re.sub(r'.(\d+)$',r'-\g<1>', VERSION) # convert to format passed by host.package.version for deb 8.0.32-24-2
    RPM_PERCONA_BUILD_VERSION = VERSION # re-assign for RPM tests and use 8.0.32-24.2
    VERSION = '.'.join(VERSION.split('.')[:-1]) # use VERSION 8.0.32-24 without package build number for non-package tests

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-server-server', 'percona-server-test',
               'percona-server-dbg', 'percona-server-source',
               'percona-server-client', 'percona-server-rocksdb',
               'percona-mysql-router', 'percona-mysql-shell']

RPMPACKAGES = ['percona-server-server', 'percona-server-client',
               'percona-server-test', 'percona-server-debuginfo',
               'percona-server-devel', 'percona-server-rocksdb',
               'percona-mysql-router', 'percona-mysql-shell']

# Define plugins amd components lists for PS8.0.X releases:
if version.parse(VERSION) > version.parse("8.0.0") and version.parse(VERSION) < version.parse("8.1.0"):
    PLUGIN_COMMANDS = ["mysql -e \"CREATE FUNCTION"
                    " fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_set RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_show RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_edit RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_delete RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_lock_shared RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_lock_exclusive RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_unlock RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " mysql_no_login SONAME 'mysql_no_login.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_get_read_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_get_write_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_release_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " validate_password SONAME 'validate_password.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " version_tokens SONAME 'version_token.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " rpl_semi_sync_master SONAME 'semisync_master.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " rpl_semi_sync_slave SONAME 'semisync_slave.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " connection_control SONAME 'connection_control.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " authentication_ldap_sasl SONAME 'authentication_ldap_sasl.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " authentication_fido SONAME 'authentication_fido.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " connection_control_failed_login_attempts SONAME 'connection_control.so';\""]
    COMPONENTS = ['component_validate_password', 'component_log_sink_syseventlog',
              'component_log_sink_json', 'component_log_filter_dragnet',
              'component_audit_api_message_emit']
# Define plugins amd components lists for PS8.0.1 releases:
elif version.parse(VERSION) >= version.parse("8.1.0"):
    PLUGIN_COMMANDS = ["mysql -e \"CREATE FUNCTION"
                    " version_tokens_set RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_show RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_edit RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_delete RETURNS STRING SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_lock_shared RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_lock_exclusive RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " version_tokens_unlock RETURNS INT SONAME 'version_token.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " mysql_no_login SONAME 'mysql_no_login.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_get_read_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_get_write_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"CREATE FUNCTION"
                    " service_release_locks RETURNS INT SONAME 'locking_service.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " validate_password SONAME 'validate_password.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " version_tokens SONAME 'version_token.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " rpl_semi_sync_master SONAME 'semisync_master.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " rpl_semi_sync_slave SONAME 'semisync_slave.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " connection_control SONAME 'connection_control.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " authentication_ldap_sasl SONAME 'authentication_ldap_sasl.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " authentication_fido SONAME 'authentication_fido.so';\"",
                    "mysql -e \"INSTALL PLUGIN"
                    " connection_control_failed_login_attempts SONAME 'connection_control.so';\""]
    COMPONENTS = ['component_validate_password', 'component_log_sink_syseventlog',
              'component_log_sink_json', 'component_log_filter_dragnet',
              'component_audit_api_message_emit', 'component_binlog_utils_udf',
              'component_percona_udf', 'component_keyring_vault', 'component_audit_log_filter'
              ]
else:
    assert "Incorrect version"

def is_running(host):
    cmd = 'ps auxww| grep -v grep  | grep -c "mysql"'
    result = host.run(cmd)
    stdout = int(result.stdout)
    if stdout == 0:
        return True
    return False


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    # percona-mysql-shell package version does not have percona version value (it is 8.0.32)
    if package == 'percona-mysql-shell':
        assert VERSION.split('-')[0] in pkg.version, (VERSION.split('-')[0], pkg.version)
    else:
        if DEB_PERCONA_BUILD_VERSION:
            assert DEB_PERCONA_BUILD_VERSION in pkg.version, pkg.version
        else:
            assert VERSION in pkg.version, pkg.version


@pytest.mark.parametrize("package", RPMPACKAGES)
def test_check_rpm_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    # percona-mysql-shell package does not have percona version (it is 8.0.32)
    if package == 'percona-mysql-shell':
        assert VERSION.split('-')[0] in pkg.version, (VERSION.split('-')[0], pkg.version)
    else:
        if RPM_PERCONA_BUILD_VERSION:
            assert RPM_PERCONA_BUILD_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
        else:
            assert VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release


@pytest.mark.parametrize("binary", ['mysqlsh', 'mysql', 'mysqlrouter'])
def test_binary_version(host, binary):
    cmd = "{} --version".format(binary)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert VERSION in result.stdout, result.stdout

def test_ps_revision(host):
    if not REVISION:
        pytest.skip("REVISION parameter was not provided. Skipping this check.")
    cmd = "{} --version".format('mysql')
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert REVISION in result.stdout, result.stdout


@pytest.mark.parametrize('component', ['@@INNODB_VERSION', '@@VERSION'])
def test_mysql_version(host, component):
    with host.sudo("root"):
        cmd = "mysql -e \"SELECT {}; \"| grep -c \"{}\"".format(component, VERSION)
        result = host.run(cmd)
        assert result.rc == 0, (result.stderr, result.stdout)
        assert int(result.stdout) == 1, result.stdout


@pytest.mark.parametrize('plugin_command', PLUGIN_COMMANDS)
def test_plugins(host, plugin_command):
    with host.sudo("root"):
        result = host.run(plugin_command)
        assert result.rc == 0, (result.stderr, result.stdout)


@pytest.mark.parametrize("component", COMPONENTS)
def test_components(component, host):
    with host.sudo("root"):
        cmd = 'mysql -Ns -e "select count(*) from mysql.component where component_urn=\"file://{}\";"'.format(component)
        check_component = host.run(cmd)
        if check_component.rc == 0:
            inst_cmd = 'mysql -e "INSTALL COMPONENT \"file://{}\";"'.format(component)
            inst_res = host.run(inst_cmd)
            assert inst_res.rc == 0, inst_res.stderr
        check_cmd = 'mysql -Ns -e "select count(*) from mysql.component where component_urn=\"file://{}\";"'.format(
            component)
        check_result = host.run(check_cmd)
        assert check_result.rc == 1, (check_result.rc, check_result.stderr, check_result.stdout)


def test_madmin(host):
    with host.sudo("root"):
        mysql = host.service("mysql")
        if not mysql.is_running:
            cmd = 'service mysql start'
            start = host.run(cmd)
            assert start.rc == 0, start.stdout
            mysql = host.service("mysql")
            assert mysql.is_running
        cmd = 'mysqladmin shutdown'
        shutdown = host.run(cmd)
        assert shutdown.rc == 0, shutdown.stdout
        mysql = host.service("mysql")
        assert not mysql.is_running
        cmd = 'service mysql start'
        start = host.run(cmd)
        assert start.rc == 0, start.stdout
        mysql = host.service("mysql")
        assert mysql.is_running

def test_disable_validate_password_plugin(host):
    with host.sudo():
        cmd = "mysql -e \"UNINSTALL PLUGIN validate_password;\""
        plugin = host.run(cmd)
        assert plugin.rc == 0, plugin.stdout
        dist = host.system_info.distribution
        if dist.lower() in RHEL_DISTS:
            cmd = 'service mysql restart'
            restart = host.run(cmd)
            assert restart.rc == 0, (restart.stdout, restart.stderr)

@pytest.mark.pkg_source
def test_sources_ps_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution    
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    if DEB_PERCONA_BUILD_VERSION:
        cmd = "apt-cache madison percona-server | grep Source | grep \"{}\"".format(DEB_PERCONA_BUILD_VERSION)
    else:
        cmd = "apt-cache madison percona-server | grep Source | grep \"{}\"".format(VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert VERSION in result.stdout, result.stdout

@pytest.mark.pkg_source
def test_sources_mysql_shell_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison percona-mysql-shell | grep Source | grep \"{}\"".format(VERSION.split('-')[0])
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert VERSION.split('-')[0] in result.stdout, result.stdout

@pytest.mark.telemetry_enabled
def test_telemetry_enabled(host):
    assert host.file(TELEMETRY_PATH).exists
    assert host.file(TELEMETRY_PATH).contains('PRODUCT_FAMILY_PS')
    assert host.file(TELEMETRY_PATH).contains('instanceId:[0-9a-fA-F]\\{8\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{12\\}$')

@pytest.mark.telemetry_disabled
def test_telemetry_disabled(host):
    assert not host.file(TELEMETRY_PATH).exists