#!/usr/bin/env bash
set -e

/usr/bin/percona-server-mongodb-enable-auth.sh -q > /tmp/psmdb_auth.txt 2>&1

echo "db.getSiblingDB('admin').auth('dba', '$(grep 'Password:' /tmp/psmdb_auth.txt | awk -F ':' '{print $2}')');" >> ~/.mongorc.js

