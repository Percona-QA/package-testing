#!/bin/bash

version="3.0.8-1.3"
log="/tmp/psmdb_run.log"
#echo -n > /tmp/psmdb_run.log

set -e

echo "checking if all packages are installed"
if [ -f /etc/redhat-release ]; then
        if [ "$(rpm -qa | grep Percona | grep -c ${version})" == "6" ]; then
                echo "all packages are installed"
        else
                for package in Percona-Server-MongoDB-debuginfo Percona-Server-MongoDB Percona-Server-MongoDB-mongos Percona-Server-MongoDB-server Percona-Server-MongoDB-shell Percona-Server-MongoDB-tools; do
                        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
                        else
                                echo "WARNING: ${package} is not installed"
                        fi
                done
        fi
else
        if [ "$(dpkg -l | grep percona | grep -c ${version})" == "6" ]; then
                echo "all packages are installed"
        else
                for package in percona-server-mongodb percona-server-mongodb-dbg percona-server-mongodb-mongos percona-server-mongodb-server percona-server-mongodb-shell percona-server-mongodb-tools; do
                        if [ "$(dpkg -l | grep -c ${package}-${version})" -gt 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
                        else
                                echo "WARNING: ${package} is not installed"
                        fi
                done
        fi
fi

