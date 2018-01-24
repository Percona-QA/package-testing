#!/usr/bin/env bash
set -e

/usr/bin/percona-server-mongodb-enable-auth.sh -q > /tmp/psmdb_auth.txt 2>&1

echo "db.getSiblingDB('admin').auth('dba', '$(grep 'Password:' /tmp/psmdb_auth.txt | awk -F ':' '{print $2}')');" >> ~/.mongorc.js

# check auth
result=$(mongo admin --eval "$(cat ~/.mongorc.js); db.getUsers()"|grep -c "admin.dba")
if [ ${result} -ne 1 ]; then
  echo "Authentication is not correctly setup!"
  exit 1
fi
