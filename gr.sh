#!/bin/bash

# group replication after install/upgrade script
set -e

if [ -f /etc/redhat-release ]; then
                echo " RHEL copy gr.cnf"
                cp /package-testing/templates/group_replication.j2 /etc/my.cnf.d/gr.cnf
        else
                echo "copy gr.cnf"
                cp /package-testing/templates/group_replication.j2 /etc/mysql/percona-server.conf.d/gr.cnf
fi

echo "restart service"
service mysql restart
sleep 10
echo "install plugins"
mysql -e "INSTALL PLUGIN group_replication SONAME 'group_replication.so';"
mysql -e "INSTALL PLUGIN connection_control SONAME 'connection_control.so';"
echo "check that plugins are available"

for i in group_replication CONNECTION_CONTROL; do
        if [ "$(mysql -e "SHOW PLUGINS;" | grep -ic $i) == 1" ]; then
                echo "$i plugin is installed"
        else
                echo "$i plugin is missing"
        fi
done
