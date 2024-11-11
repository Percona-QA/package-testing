import os
import pytest
import testinfra.utils.ansible_runner
import re
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-xtradb-cluster-full', 'percona-xtradb-cluster-client',
               'percona-xtradb-cluster-common', 'percona-xtradb-cluster-dbg',
               'percona-xtradb-cluster-garbd-debug', 'percona-xtradb-cluster-garbd',
               'percona-xtradb-cluster-server-debug', 'percona-xtradb-cluster-test',
               'percona-xtradb-cluster']

RPMPACKAGES = ['percona-xtradb-cluster-full', 'percona-xtradb-cluster',
               'percona-xtradb-cluster-client', 'percona-xtradb-cluster-debuginfo',
               'percona-xtradb-cluster-devel', 'percona-xtradb-cluster-garbd',
               'percona-xtradb-cluster-server', 'percona-xtradb-cluster-shared',
               'percona-xtradb-cluster-test']

EXTRA_RPMPACKAGE = ['percona-xtradb-cluster-shared-compat']

PLUGIN_COMMANDS = ["mysql -e \"CREATE FUNCTION"
                   " fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so';\"",
                   "mysql -e \"CREATE FUNCTION"
                   " fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so';\"",
                   "mysql -e \"CREATE FUNCTION"
                   " murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so';\"",
                   "mysql -e \"INSTALL PLUGIN"
                   " audit_log SONAME \'audit_log.so\';\"",
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
                   " mysql_native_password SONAME 'mysql_native_password.so';\""]

COMPONENTS = ['component_validate_password', 'component_log_sink_syseventlog',
              'component_log_sink_json', 'component_log_filter_dragnet',
              'component_audit_api_message_emit']

VERSION = os.environ['VERSION']
DEB_PERCONA_BUILD_VERSION = ''
RPM_PERCONA_BUILD_VERSION = ''
if re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', VERSION): # if full package VERSION 8.0.32-24.2 is passed we need to re-assign it for tests
    DEB_PERCONA_BUILD_VERSION = re.sub(r'.(\d+)$',r'-\g<1>', VERSION) # convert to format passed by host.package.version for deb 8.0.32-24-2
    RPM_PERCONA_BUILD_VERSION = VERSION # re-assign for RPM tests and use 8.0.32-24.2
    VERSION = '.'.join(VERSION.split('.')[:-1]) # use VERSION 8.0.32-24 without package build number for non-package tests

REVISION = os.environ.get('PXC_REVISION')

@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
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
    if RPM_PERCONA_BUILD_VERSION:
        assert RPM_PERCONA_BUILD_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
    else:
        assert VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release

@pytest.mark.parametrize("package", EXTRA_RPMPACKAGE)
def test_check_shared_package(host, package):
    dist = host.system_info.distribution
    release = host.system_info.release
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    if dist.lower() in RHEL_DISTS and release == '9.0':
        pytest.skip("This test is for RHEL based platforms except RHEL 9")
    pkg = host.package(package)
    assert pkg.is_installed
    if RPM_PERCONA_BUILD_VERSION:
        assert RPM_PERCONA_BUILD_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
    else:
        assert VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release


def test_binary_version(host):
    with host.sudo("root"):
        cmd = "mysql --version"
        result = host.run(cmd)
        assert result.rc == 0, result.stderr
        assert VERSION in result.stdout, result.stdout

def test_pxc_revision(host):
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
        version = host.check_output("mysql -e \"SELECT {}; \"".format(component))
        assert result.rc == 0, version
        assert int(result.stdout) == 1, result.stdout


def test_version_commnet(host):
    with host.sudo("root"):
        cmd = "mysql -e \"SELECT @@VERSION_COMMENT;\""
        result = host.run(cmd)
        print(result.stdout)
        assert result.rc == 0, result.stdout


def test_wresp_version(host):
    with host.sudo("root"):
        cmd = "mysql -e \"SHOW STATUS LIKE 'wsrep_provider_version';\""
        result = host.run(cmd)
        print(result.stdout)
        assert result.rc == 0, result.stdout


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

@pytest.mark.telemetry_enabled
def test_telemetry_enabled(host):
    assert host.file(TELEMETRY_PATH).exists
    assert host.file(TELEMETRY_PATH).contains('PRODUCT_FAMILY_PXC')
    assert host.file(TELEMETRY_PATH).contains('instanceId:[0-9a-fA-F]\\{8\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{12\\}$')

@pytest.mark.telemetry_disabled
def test_telemetry_disabled(host):
    assert not host.file(TELEMETRY_PATH).exists
