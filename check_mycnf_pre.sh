#!/bin/bash

if [ -f /etc/debian_version ]; then
  echo " this is debian/ubuntu"
  echo "#this is test" >> /etc/mysql/my.cnf
  md5sum /etc/mysql/my.cnf | awk {'print $1'} > /tmp/mycnf_sum
else
  echo " this is centos"
  echo "#this is test" >> /etc/my.cnf
  md5sum /etc/my.cnf | awk {'print $1'} > /tmp/mycnf_sum
fi  

