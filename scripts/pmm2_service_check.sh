#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: mysql or mongodb !"
  echo "Usage: ./pmm_service_check.sh <prod>"
  exit 1
fi

if [ "$1" = "mysql" ]; then
  if [[ $(pmm-admin list | grep "MySQL" | awk -F" " '{print $2}') ]]; then
    echo "all is good"
  else
    echo "mysql monitoring isn NOT working, check the logs"
    exit 1
  fi
elif [ "$1" = "mongodb" ]; then
  if [[ $(pmm-admin list | grep "MongoDB" | awk -F" " '{print $2}') ]]; then
    echo "all is good"
  else
    echo "mongodb monitoring isn NOT working, check the logs"
    exit 1
  fi
else
  echo "Illegal product selected!"
  exit 1
fi
