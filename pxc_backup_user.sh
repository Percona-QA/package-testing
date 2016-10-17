#!/bin/bash

set -e

mysql -e "CREATE USER 'sstuser'@'localhost' IDENTIFIED BY 's3cretPass';"
mysql -e "GRANT PROCESS, RELOAD, LOCK TABLES, REPLICATION CLIENT ON *.* TO 'sstuser'@'localhost'";
