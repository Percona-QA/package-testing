#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import mysql

from settings import *

@pytest.fixture(scope='module')
def mysql_server(request):
    mysql_server = mysql.MySQL(base_dir)
    mysql_server.start()
    yield mysql_server
    mysql_server.stop()

def test_install_functions(mysql_server):
    for function in pxc_functions:
        mysql_server.install_function(function[0], function[1], function[2])

def test_install_plugin(mysql_server):
    for plugin in pxc_plugins:
        mysql_server.install_plugin(plugin[0], plugin[1])

def test_cluster_size(mysql_server):
    output = mysql_server.run_query('SHOW STATUS LIKE "wsrep_cluster_size";')
    assert output.split('\t')[1].strip() == "3"

def test_backup_command(mysql_server):
    # Define the command
    command = base_dir + "/bin/pxc_extra/pxb-8.0/bin/xtrabackup --backup --user=root --target-dir=/tmp/backups/ --port=3306 --socket=/tmp/node1_mysql.sock"

    # Execute the command
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Check if the command was successful
    assert result.returncode == 0, f"Backup command failed: {result.stderr}"

def test_prepare_command(mysql_server):
    # Define the command
    command = base_dir + "/bin/pxc_extra/pxb-8.0/bin/xtrabackup --prepare --target-dir=/tmp/backups/"
    
    # Execute the command
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Check if the command was successful
    assert result.returncode == 0, f"Prepare command failed: {result.stderr}"
