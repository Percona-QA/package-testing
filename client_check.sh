#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps55, ps56, ps57, ps80, pxc56, or pxc57 !"
  echo "Usage: ./client_check.sh <prod>"
  exit 1
fi

if [ "$1" = "ps55" ]; then
  deb_version="-5.5"
  rpm_version="-55"
elif [ "$1" = "ps56" ]; then
  deb_version="-5.6"
  rpm_version="-56"
elif [ "$1" = "ps57" ]; then
  deb_version="-5.7"
  rpm_version="-57"
elif [ "$1" = "ps80" ]; then
  deb_version=""
  rpm_version=""
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

if [ -f /etc/redhat-release ]; then
  if [ "${product}" = "ps55" -o "${product}" = "ps56" -o "${product}" = "ps57" ]; then
    yum install -y Percona-Server-client-${rpm_version} --enablerepo=percona-testing-x86_64
  elif [ "${product}" = "pxc56" -o "${product}" = "pxc57" ]; then
    yum install -y Percona-XtraDB-Cluster-client-${rpm_version} --enablerepo=percona-testing-x86_64
  else
    echo "client version is incorrect"
    exit 1
  fi
else
 if [ "${product}" = "ps55" -o "${product}" = "ps56" -o "${product}" = "ps57" -o "${product}" = "ps80" ]; then
    apt-get install -y percona-server-client${deb_version}
  elif [ "${product}" = "pxc56" -o "${product}" = "pxc57" ]; then
    apt-get install -y percona-xtradb-cluster-client${deb_version}
  else
    echo "client version is incorrect"
    exit 1
  fi
fi

mysql --help
echo $?
