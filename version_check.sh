#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps55, ps56 or ps57 !"
  echo "Usage: ./version_check.sh <prod>"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)

source ${SCRIPT_PWD}/VERSIONS

if [ $1 = "ps55" ]; then
  version=${PS55_VER}
  release=${PS55_VER#*-}
  revision=${PS55_REV}
elif [ $1 = "ps56" ]; then
  version=${PS56_VER}
  release=${PS56_VER#*-}
  revision=${PS56_REV}
elif [ $1 = "ps57" ]; then
  version=${PS57_VER}
  release=${PS57_VER#*-}
  revision=${PS57_REV}
else
  echo "Illegal product selected!"
  exit 1
fi

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
