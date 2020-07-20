#!/bin/bash
set -e

#check if service is running
function is_running {
  if [ $(ps auxww| grep -v grep  |grep -v "router" | grep -c "mysql") -gt 0 ]; then
    # "service is running"
    echo 1
  else
    # service is NOT running
    echo 0
  fi	
}

run=$(is_running)
echo $run

if [ $run -eq 1 ]; then
  echo "running mysqladmin shutdown"
  mysqladmin shutdown
  sleep 5
else
  echo "Make sure that service is running before stopping it"
  exit 1
fi

run=$(is_running)
echo $run

if [ $run -eq 0 ]; then
  echo "service has been stopped successfully"
else
  echo "service is still running"
  exit 1
fi

echo "starting mysql service"
service mysql start

run=$(is_running)
echo $run

if [ $run -eq 1 ]; then
  echo "service been started successfully"
else
  echo "service didn't start"
  exit 1
fi
