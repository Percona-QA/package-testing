#!/bin/bash
set -e
mysql -e "SELECT @@TOKUDB_VERSION;"
mysql -e "SELECT @@INNODB_VERSION;"
mysql -e "SELECT @@VERSION;"
mysql -e "SELECT @@VERSION_COMMENT;"
