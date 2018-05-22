#!/bin/bash

set -e

psoutput=$(pgrep -c proxysql)
echo "${psoutput}"

if [ "${psoutput}" -gt 1 ]; then
	echo "proxysql is running"
   else 
	echo "NOT RUNNING!!!!"
	exit 1
fi
	
