#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import mysql

from settings import *

@pytest.fixture(scope='module')
def mysql_server(request):
    mysql_server = mysql.MySQL(base_dir)
    try:
        mysql_server.start()
    except RuntimeError as e:
        pytest.skip(f"Skipping dynamic tests: {e}")
    yield mysql_server
    mysql_server.stop()

def test_install_functions(mysql_server):
    for function in pxc_functions:
        mysql_server.install_function(function[0], function[1], function[2])

def test_install_plugin(mysql_server):
    for plugin in pxc_plugins:
        mysql_server.install_plugin(plugin[0], plugin[1])

def test_cluster_size(mysql_server):
    try:
        output = mysql_server.run_query('SHOW STATUS LIKE "wsrep_cluster_size";')
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Unable to query cluster size: {e}")
    assert output.split('\t')[1].strip() == "3"