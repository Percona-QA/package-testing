#!/bin/bash
set -e

init_pass=$(grep "temporary password" /var/log/mysqld.log | awk '{print $NF}')

mysql --connect-expired-password -uroot --password="$init_pass" -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'U?fY)9s7|3gxUm';"

cp /package-testing/templates/my_57.j2 /root/.my.cnf
