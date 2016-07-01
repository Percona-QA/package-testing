#!/bin/bash

set -e

version="5.7.13-6"
release="6"
revision="e3d58bb"

log="/tmp/version_check.log"
echo -n > $log

for i in @@INNODB_VERSION @@VERSION @@TOKUDB_VERSION; do
        if [ "$(mysql -e "SELECT $i; "| grep -c $version)" = 1 ]; then
                echo "$i is correct" >> $log
        else
                echo "@@INNODB_VERSION is incorrect"
                exit 1
        fi
done

if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep $revision | grep -c $release)" = 1 ]; then
        echo "@@VERSION COMMENT is correct" >> $log
else
        echo "@@VERSION_COMMENT is incorrect"
        exit 1
fi
       
echo "versions are OK"
