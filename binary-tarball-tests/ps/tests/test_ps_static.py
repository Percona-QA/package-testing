#!/usr/bin/env python3
import pytest
import testinfra

from settings import *

def test_executables_exist(host,pro_fips_vars):
    base_dir = pro_fips_vars['base_dir']
    for executable in ps_executables:
        assert host.file(base_dir+'/'+executable).exists
        assert oct(host.file(base_dir+'/'+executable).mode) == '0o755'

def test_binaries_version(host,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    pro = str(pro)
    ps_version_major = pro_fips_vars['ps_version_major']
    base_dir = pro_fips_vars['base_dir']
    ps_version = pro_fips_vars['ps_version']
    ps_revision = pro_fips_vars['ps_revision']
   
    debug = pro_fips_vars['debug']
    ps_version_percona = pro_fips_vars['ps_version_percona']
    base_dir_debug = base_dir + debug
    
    ps_revision_pro = ps_revision
    
    if ps_version_major in ['5.7', '5.6']:
        # Older versions without Pro support
        assert 'mysql  Ver 14.14 Distrib ' + ps_version + ', for Linux (x86_64)' in host.check_output(
            base_dir + '/bin/mysql --version'
        )
        assert 'mysqld  Ver ' + ps_version + ' for Linux on x86_64 (Percona Server (GPL), Release ' + ps_version_percona + ', Revision ' + ps_revision + ')' in host.check_output(
            base_dir + '/bin/mysqld --version'
        )
    else:
        # Newer versions with Pro support
        expected_mysql_output = (
            f"{base_dir}/bin/mysql  Ver {ps_version} for Linux on x86_64 (Percona Server Pro (GPL), "
            f"Release {ps_version_percona}, Revision {ps_revision_pro})"
        )
        expected_mysqld_output = (
            f"{base_dir}/bin/mysqld  Ver {ps_version} for Linux on x86_64 (Percona Server Pro (GPL), "
            f"Release {ps_version_percona}, Revision {ps_revision_pro})"
        )

        # Assert outputs dynamically
        assert expected_mysql_output in host.check_output(base_dir + '/bin/mysql --version')
        assert expected_mysqld_output in host.check_output(base_dir + '/bin/mysqld --version')

def test_files_exist(host,pro_fips_vars):
    base_dir = pro_fips_vars['base_dir']
    for f in ps_files:
        assert host.file(base_dir+'/'+f).exists
        assert host.file(base_dir+'/'+f).size != 0

def test_symlinks(host,pro_fips_vars):
    base_dir = pro_fips_vars['base_dir']
    for symlink in ps_symlinks:
        assert host.file(base_dir+'/'+symlink[0]).is_symlink
        assert host.file(base_dir+'/'+symlink[0]).linked_to == base_dir+'/'+symlink[1]
        assert host.file(base_dir+'/'+symlink[1]).exists

def test_binaries_linked_libraries(host,pro_fips_vars):
    pro = pro_fips_vars['pro']
    base_dir = pro_fips_vars['base_dir']
    for binary in ps_binaries:
        assert '=> not found' not in host.check_output('ldd ' + base_dir + '/' + binary)

def test_pro_openssl_files_not_exist(host,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    base_dir = pro_fips_vars['base_dir']
    if pro:
        for openssl_file in ps_openssl_files:
            assert not host.file(base_dir+'/'+openssl_file).exists
    else:
        pytest.skip("This test is only for PRO tarballs. Skipping")


def test_pro_openssl_files_linked(host,pro_fips_vars):
    pro = pro_fips_vars['pro']
    fips_supported = pro_fips_vars['fips_supported']
    base_dir = pro_fips_vars['base_dir']
    if pro:
        for binary in ps_binaries:
            shared_files = host.check_output('ldd ' + base_dir + '/' + binary)
            for line in shared_files.splitlines():
                for file_name in ['libcrypto.so', 'libssl.so']:
                    if file_name in line:
                        assert not base_dir in line
                        assert not '=> not found' in line
    else:
        pytest.skip("This test is only for PRO tarballs. Skipping")
