#!/bin/bash

if [[ "$#" -ne 1 ]]; then
  echo "This script requires expected version parameter, ex.: X.XX.X"
  echo "Usage: ./pmm2_client_version_checker.sh 2.30.0"
  exit 1
fi

EXPECTED=$1

if [[ -z "$2" ]]; then
  FLAG=$2
fi

pmm-admin --version ${FLAG}
version_match=$(pmm-admin --version ${FLAG} 2>&1|grep -c "${EXPECTED}")
actual_version=$(pmm-admin --version ${FLAG} 2>&1|grep ^Version | awk -F ' ' '{print $2}')
if [ ${version_match} -eq 0 ]; then
  echo "PMM Client version ${actual_version} is not good! Expected: ${EXPECTED}" >&2;
  exit 1
else
  echo "PMM Client version is correct and ${EXPECTED}"
fi

#check for packages after upgrade

pmm-admin status | grep -q Running
pmm-admin status | grep node_exporter | grep -qv Waiting
pmm-admin status | grep vmagent | grep -qv Waiting
pmm-admin status | grep mysqld_exporter | grep -qv Waiting
pmm-admin status | grep mysql_perfschema_agent | grep -qv Waiting
pmm-admin status | grep mysql_perfschema_agent | grep -qv its_not_a_real_check

server_version=$(pmm-admin status | grep Version | awk -F' ' '{print $2}')
if [ "$server_version" != "$1" ]; then
    echo "PMM Server Version is not equal to expected $1";
    exit 1;
fi
admin_version=$(pmm-admin status | grep pmm-admin | awk -F' ' '{print $3}')
if [ "$admin_version" != "$1" ]; then
    echo "PMM Admin Version is not equal to expected $1";
    exit 1;
fi
agent_version=$(pmm-admin status | grep pmm-agent | awk -F' ' '{print $3}')
if [ "$agent_version" != "$1" ]; then
    echo "PMM Agent Version is not equal to expected $1";
    exit 1;
fi
if [ "$agent_version" != "$admin_version" ]; then
    echo "PMM-Agent Version Does not Match PMM-Admin Version";
    exit 1;
fi
echo "PMM Client versions are OK"

ls -la /usr/local/percona/pmm2/exporters | grep -q azure_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q mongodb_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q mysqld_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q node_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q postgres_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q proxysql_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q rds_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q vmagent
ls -la /usr/local/percona/pmm2/exporters | grep -q its_not_a_real_check
