#!/bin/bash

version="2.3.4-1"
log="/tmp/pxb_run.log"
#echo -n > /tmp/pxb_run.log

set -e

echo "checking if all packages are installed"
if [ -f /etc/redhat-release ]; then
        if [ "$(rpm -qa | grep Percona | grep -c ${version})" == "6" ]; then
                echo "all packages are installed"
        else
                for package in percona-xtrabackup percona-xtrabackup-test percona-xtrabackup-debuginfo; do
                        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
                        else
                                echo "WARNING: ${package}-${version} is not installed"
                        fi
                done
        fi
else
        if [ "$(dpkg -l | grep percona | grep -c ${version})" == "6" ]; then
                echo "all packages are installed"
        else
                for package in percona-xtrabackup-dbg percona-xtrabackup-test percona-xtrabackup; do
                        if [ "$(dpkg -l | grep -c ${package})" -gt 0 ]; then
                                echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
                        else
                                echo "WARNING: ${package}-${version} is not installed"
                        fi
                done
        fi
fi

