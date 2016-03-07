#!/bin/bash

version="5.7.10-3"
log="/tmp/ps_run.log"
echo -n > /tmp/ps_run.log

set -e

echo "checking if all packages are installed"
if [ -f /etc/redhat-release ]; then
        if [ "$(rpm -qa | grep Percona | grep -c ${version})" == "7" ]; then
                echo "all packages are installed"
        else
                for package in Percona-Server-server-57 Percona-Server-test-57 Percona-Server-57-debuginfo Percona-Server-devel-57 Percona-Server-tokudb-57 Percona-Server-shared-57 Percona-Server-client-57; do
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
                for package in percona-server-server-5.7 percona-server-test-5.7 percona-server-5.7-dbg percona-server-source-5.7 percona-server-tokudb-5.7; do
			deb_version="$(dpkg -l | grep ${package} | awk '{print $3}')"
			echo ${package}-${deb_version}
                        if [ "$(dpkg -l | grep ${package} | grep -c ${deb_version})" != 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" 
                        else
                                echo "WARNING: ${package} is not installed"
                        fi
                done
        fi
fi

