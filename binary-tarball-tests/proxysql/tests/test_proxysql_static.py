#!/usr/bin/env python3
import re
import pytest
import testinfra

from settings import *

proxysql2x_binaries, proxysql2x_files = get_artifact_sets()

def test_proxysql_version(host):
    if proxysql_major_version in ['2.7' ,'3.0.1' ]:
        expected_version = 'ProxySQL version' + proxysql_version + '-percona-1.2'
        output = host.check_output(base_dir + '/usr/bin/proxysql --version')

        # Use regex to check if the expected version is in the output
        match = re.search(rf'{re.escape(expected_version)}', output)
        assert match, f"Expected version string not found in output: {output}"

def test_proxysql_admin_version(host):
    if proxysql_major_version in ['2.7','3.0.1']:
        expected_version = 'proxysql-admin version' + proxysql_version 
        output = host.check_output(base_dir + '/usr/bin/proxysql-admin --version')

        # Use regex to check if the expected version is in the output
        match = re.search(rf'{re.escape(expected_version)}', output)
        assert match, f"Expected version string not found in output: {output}"

def test_proxysql_scheduler_admin_version(host):
    if proxysql_major_version in ['2.7','3.0.1']:
        expected_version = 'percona-scheduler-admin Version:' + proxysql_version 
        output = host.check_output(base_dir + '/usr/bin//percona-scheduler-admin --version')

        # Use regex to check if the expected version is in the output
        match = re.search(rf'{re.escape(expected_version)}', output)
        assert match, f"Expected version string not found in output: {output}"

def test_files_exist(host):
    for f in proxysql2x_files:
        file_path = f"{base_dir}/{f}"
        assert host.file(file_path).exists, f"{file_path} does not exist"
        assert host.file(file_path).size > 0, f"{file_path} is empty"


#def test_mysql_version(host):
 #   if proxysql_version_major in ['5.7', '5.6']:
  #      expected_version = 'mysql  Ver 14.14 Distrib ' + proxysql57_client_version
   #     output = host.check_output(base_dir + '/bin/mysql --version')

        # Use regex to check if the expected version is in the output
     #   match = re.search(rf'{re.escape(expected_version)}', output)
    #    assert match, f"Expected version string not found in output: {output}"

#def test_mysqld_version(host):
 #   if proxysql_version_major in ['5.7','5.6']:
  #      expected = (
   #         'mysqld  Ver ' + proxysql57_server_version_norel + ' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) ' +
    #        proxysql57_server_version + ', Revision ' + proxysql_revision + ', wsrep_' + wsrep_version + ')'
     #   )
      #  assert expected in host.check_output(base_dir+'/bin/mysqld --version')
