#!/bin/bash

deb_version="5.6"
rpm_version="56"
version="5.6.30-rel76.3"
log="/tmp/ps_run.log"
echo -n > /tmp/ps_run.log

set -e

echo "checking if all packages are installed"
if [ -f /etc/redhat-release ]; then
        if [ "$(rpm -qa | grep Percona-Server | grep -c ${version})" == "7" ]; then
                echo "all packages are installed"
        else
                for package in Percona-Server-server-${rpm_version} Percona-Server-test-${rpm_version} Percona-Server-${rpm_version}-debuginfo Percona-Server-devel-${rpm_version} Percona-Server-tokudb-${rpm_version} Percona-Server-shared-${rpm_version} Percona-Server-client-${rpm_version}; do
                        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
                        else
                                echo "WARNING: ${package}-${version} is not installed"
                        fi
                done
        fi
else
        if [ "$(dpkg -l | grep percona-server | grep -c ${version})" == "6" ]; then
                echo "all packages are installed"
        else
                for package in percona-server-server-${deb_version} percona-server-test-${deb_version} percona-server-${deb_version}-dbg percona-server-source-${deb_version} percona-server-tokudb-${deb_version} percona-server-common-${deb_version}; do
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

