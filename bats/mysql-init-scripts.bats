#!/usr/bin/env bats

if [ ! -z "$(which systemctl)" ]; then
  SYSTEMCTL=1
fi

if [ ! -z "$(which service)" ]; then
  SERVICE=1
fi

if [ ! -z "$(which chkconfig)" ]; then
  CHKCONFIG=1
fi

function is_running(){
  if [ $(ps aux | grep -v grep | grep "mysqld " | wc -l) -eq 0 ]; then
    return 1
  fi

  if [ ${SYSTEMCTL} -eq 1 ]; then
    if [ "$(systemctl is-active mysql)" !=  "active" ]; then
      return 1
    fi
  fi

  return 0
}

function stopit(){
  if is_running; then
    if [ ${SYSTEMCTL} -eq 1 ]; then
      run systemctl stop mysql
      [ $status -eq 0 ]
    else
      run service mysql stop
      [ $status -eq 0 ]
    fi
    run is_running
    [ $status -eq 1 ]
  fi
}

function fix_timeout(){
  if [ -f /etc/default/mysql ]; then
    sed -i 's/STARTTIMEOUT=900/STARTTIMEOUT=30/g' /etc/default/mysql
  fi
  if [ ${SYSTEMCTL} -eq 1 -a -f /lib/systemd/system/mysql.service ]; then
    sed -i 's/TimeoutSec=600/TimeoutSec=30/g' /lib/systemd/system/mysql.service
    systemctl daemon-reload
  fi
}

function teardown(){
  if [ -f /etc/default/mysql ]; then
    sed -i 's/STARTTIMEOUT=30/STARTTIMEOUT=900/g' /etc/default/mysql
  fi
  if [ -f /lib/systemd/system/mysql.service ]; then
    sed -i 's/TimeoutSec=30/TimeoutSec=600/g' /lib/systemd/system/mysql.service
    systemctl daemon-reload
  fi
  if [ -f /etc/mysql/my.cnf ]; then
    sed -i '${/nonexistingoption=1/d}' /etc/mysql/my.cnf
    sed -i '${/\[mysqld\]/d}' /etc/mysql/my.cnf
  fi
}

@test "stop mysql if running" {
  stopit
}

@test "start mysql with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl start mysql
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "stop mysql with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl stop mysql
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "restart mysql with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl restart mysql
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "stop mysql with /etc/init.d/mysql start with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run /etc/init.d/mysql stop
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
    run systemctl start mysql
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "start mysql with /etc/init.d/mysql stop with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    if is_running; then
      run systemctl stop mysql
      [ $status -eq 0 ]
      run is_running
      [ $status -eq 1 ]
    fi
    run /etc/init.d/mysql start
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
    run systemctl stop mysql
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "start mysql with service" {
  if [ ${SERVICE} -eq 1 ]; then
    service mysql start
    [ $? -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "stop mysql with service" {
  if [ ${SERVICE} -eq 1 ]; then
    run service mysql stop
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "restart mysql with service" {
  if [ ${SERVICE} -eq 1 ]; then
    service mysql restart
    [ $? -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "add nonexisting option to config file (/etc/mysql/my.cnf) and start with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    stopit
    fix_timeout
    echo "[mysqld]" >> /etc/mysql/my.cnf
    echo "nonexistingoption=1" >> /etc/mysql/my.cnf
    run systemctl start mysql
    [ $status -eq 1 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl command"
  fi
}

@test "add nonexisting option to config file (/etc/mysql/my.cnf) and start with service" {
  if [ ${SERVICE} -eq 1 ]; then
    stopit
    fix_timeout
    echo "[mysqld]" >> /etc/mysql/my.cnf
    echo "nonexistingoption=1" >> /etc/mysql/my.cnf
    run service mysql start
    [ $status -eq 1 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "check if mysql service is enabled in systemd" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    result=$(systemctl is-enabled mysql)
    [ $result == "enabled" ]
  else
    skip "system doesn't have systemctl command"
  fi
}

