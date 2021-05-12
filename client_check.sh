#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps56, ps57, ps80, pxc56, or pxc57 !"
  echo "Usage: ./client_check.sh <prod>"
  exit 1
fi

SCRIPT_PWD=$(cd "$(dirname "$0")" && pwd)

source "${SCRIPT_PWD}"/VERSIONS

if [ "$1" = "ps56" ]; then
  deb_version="-5.6"
  rpm_version="-56"
elif [ "$1" = "ps57" ]; then
  deb_version="-5.7"
  rpm_version="-57"
elif [ "$1" = "ps80" ]; then
  deb_version=""
  rpm_version=""
  version=${PS80_VER}
elif [ "$1" = "pxc56" ]; then
  deb_version="-5.6"
  rpm_version="-56"
elif [ "$1" = "pxc57" ]; then
  deb_version="-5.7"
  rpm_version="-57"
else
  echo "Invalid product selected"
  exit 1
fi

product=$1
log="/tmp/${product}_client_check.log"
echo -n > "${log}"

if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
  if [ "${product}" = "ps56" ] || [ "${product}" = "ps57" ]; then
    yum install -y Percona-Server-client${rpm_version}
  elif [ "${product}" = "ps80" ]; then
    yum install -y percona-server-client percona-mysql-router percona-mysql-shell
  elif [ "${product}" = "pxc56" ] || [ "${product}" = "pxc57" ]; then
    yum install -y Percona-XtraDB-Cluster-client-${rpm_version}
  else
    echo "client version is incorrect"
    exit 1
  fi
else
 if [ "${product}" = "ps56" ] || [ "${product}" = "ps57" ]; then
    apt-get update; apt-get install -y percona-server-client${deb_version}
  elif [ "${product}" = "ps80" ]; then
    apt-get update; apt-get install -y percona-server-client percona-mysql-router percona-mysql-shell
  elif [ "${product}" = "pxc56" ] || [ "${product}" = "pxc57" ]; then
    apt-get install -y percona-xtradb-cluster-client${deb_version}
  else
    echo "client version is incorrect"
    exit 1
  fi
fi

if [ "${product}" = "ps80" ]; then
 echo "checking client version"
 if [ "$(mysql --version | grep -c "$version")" == 1 ]; then
     echo "mysql client version is correct"
   else
     echo "ERROR: mysql-client version is incorrect "
     exit 1
 fi
 echo "checking shell version"
 if [ "$(mysqlsh --version | grep -c "$version")" == 1 ]; then
     echo "mysql shell version is correct"
   else
     echo "ERROR: mysql-shell version is incorrect "
     exit 1
 fi
 echo "checking router version"
 if [ "$(mysqlrouter --version | grep -c "$version")" == 1 ]; then
     echo "mysql router version is correct"
   else
     echo "ERROR: mysqlrouter version is incorrect "
     exit 1
 fi
fi

mysql --help
echo $?

