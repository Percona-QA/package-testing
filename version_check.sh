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
elif [ $1 = "pt" ]; then
  version=${PT_VER}
elif [ $1 = "pxb23" ]; then
  version=${PXB23_VER}
elif [ $1 = "pxb24" ]; then
  version=${PXB24_VER}
elif [ $1 = "pmm" ]; then
  version=${PMM_VER}
else
  echo "Illegal product selected!"
  exit 1
fi

product=$1
log="/tmp/${product}_version_check.log"
echo -n > $log

if [ ${product} = "ps55" -o ${product} = "ps56" -o ${product} = "ps57" ]; then
  for i in @@INNODB_VERSION @@VERSION @@TOKUDB_VERSION; do
    if [ ${product} = "ps55" -a ${i} = "@@TOKUDB_VERSION" ]; then
      echo "${i} is empty" >> $log
    elif [ "$(mysql -e "SELECT ${i}; "| grep -c $version)" = 1 ]; then
      echo "${i} is correct" >> $log
    else
      echo "${i} is incorrect"
      exit 1
    fi
  done

  if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep $revision | grep -c $release)" = 1 ]; then
    echo "@@VERSION COMMENT is correct" >> $log
  else
    echo "@@VERSION_COMMENT is incorrect"
    exit 1
  fi

elif [ ${product} = "pt" ]; then
  for i in `cat /package-testing/pt`; do
    version_check=$($i --version|grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
      echo "$i version is not good!"
      exit 1
    else
      echo "$i version is correct and ${version}" >> $log
    fi
  done

elif [ ${product} = "pmm" ]; then
  version_check=$(pmm-admin --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> $log
  fi

elif [ ${product} = "pxb23" -o ${product} = "pxb24" ]; then
  version_check=$(xtrabackup --version 2>&1|grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
      echo "${product} version is not good!"
      exit 1
    else
      echo "${product} version is correct and ${version}" >> $log
    fi
fi

echo "${product} versions are OK"
