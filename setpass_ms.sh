#!/bin/bash
set -xe

init_pass=$(grep "temporary password" /var/log/mysqld.log | awk '{print $NF}' | tail -1)
echo "$init_pass" > /tmp/pass
mysql --connect-expired-password -uroot --password="$(< /tmp/pass)" -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'U?fY)9s7|3gxUm';"
