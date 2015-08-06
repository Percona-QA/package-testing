#!/bin/bash
set -e
mysql -e "SELECT @@TOKUDB_VERSION;"
mysql -e "SELECT @@INNODB_VERSION;" 
mysql -e "SELECT @@VERSION;" 
mysql -e "SELECT @@VERSION_COMMENT;" 
#mysql -e "SHOW STATUS LIKE 'wsrep_provider_version';"
