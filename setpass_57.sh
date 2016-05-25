#!/bin/bash
set -e

init_pass=$(grep "temporary password" /var/log/mysqld.log | awk '{print $NF}')

mysql --connect-expired-password -uroot -p$init_pass -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'U?fY)9s7|3gxUm';"

