#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: mysql or mongodb !"
  echo "Usage: ./pmm_service_check.sh <prod>"
  exit 1
fi

if [ "$1" = "mysql" ]; then
  if [ "$(pmm-admin list | grep mysql | grep -c "NO")" -gt 0 ]; then
    echo "mysql monitoring isn NOT working, check the logs"
    exit 1
  else
    echo "all is good"
  fi
elif [ "$1" = "mongodb" ]; then
  if [ "$(pmm-admin list | grep mongo | grep -c "NO")" -gt 0 ]; then
    echo "mongodb monitoring isn NOT working, check the logs"
    exit 1
  else
    echo "all is good"
  fi
else
  echo "Illegal product selected!"
  exit 1
fi
