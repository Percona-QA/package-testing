#!/bin/bash

if [ -f /etc/debian_version ]; then
  if [ "$(md5sum /etc/mysql/my.cnf | awk {'print $1'})"  == "$(cat /tmp/mycnf_sum)" ]; then
    echo "this is ok"
  else
    echo "NOT OK!!"
    exit 1
  fi
else
  echo " this is centos"
  if [ "$(md5sum /etc/my.cnf | awk {'print $1'})"  == "$(cat /tmp/mycnf_sum)" ]; then
    echo "this is ok"
  else
    echo "NOT OK!!"
    exit 1
  fi
fi
