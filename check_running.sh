#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "This script requires product parameter: mysql, mongodb, proxysql and status like running|stopped!"
  echo "Usage: ./check_running.sh <prod> <status>"
  exit 1
fi

product=$1
status=$2
log="/tmp/${product}_check_running.log"
echo -n > ${log}

if [ ${product} = "mysql" ]; then
  process="bin/mysqld"
elif [ ${product} = "mongodb" ]; then
  process="bin/mongod"
elif [ ${product} = "proxysql" ]; then
  process="bin/proxysql"
else
  echo "Unknown product!"
  exit 1
fi

ps aux >> ${log}
psoutput=$(ps aux | grep -v "grep" | grep -v "check_running.sh" | grep -c "${process}")
echo ${psoutput}

if [ ${psoutput} -eq 0 -a ${status} = "stopped" ]; then
  exit 0
elif [ ${psoutput} -gt 0 -a ${status} = "running" ]; then
  exit 0
else
  exit 1
fi
