#!/usr/bin/env bats

SYSTEMCTL=0
SERVICE=0
SYSVCONFIG=0
CHKCONFIG=0

if [ ! -z "$(which systemctl 2>/dev/null)" ]; then
  SYSTEMCTL=1
fi

if [ ! -z "$(which service 2>/dev/null)" ]; then
  SERVICE=1
fi

if [ ! -z "$(which sysv-rc-conf 2>/dev/null)" ]; then
  SYSVCONFIG=1
fi

if [ ! -z "$(which chkconfig 2>/dev/null)" ]; then
  CHKCONFIG=1
fi

if [ -f /etc/mysql/my.cnf ]; then
  MYSQLCONF=/etc/mysql/my.cnf
elif [ -f /etc/my.cnf ]; then
  MYSQLCONF=/etc/my.cnf
fi

function is_running(){
  if [ $(ps aux | grep -v grep | grep "mysqld" | wc -l) -eq 0 ]; then
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
    sed -i 's/startup_timeout=900/startup_timeout=30/g' /etc/default/mysql
  fi
  if [ ${SYSTEMCTL} -eq 1 ]; then
    if [ -f /lib/systemd/system/mysql.service ]; then
      sed -i 's/TimeoutSec=600/TimeoutSec=30/g' /lib/systemd/system/mysql.service
    #elif [ -f /etc/systemd/system/mysql.service ]; then
    #  sed -i 's/TimeoutSec=600/TimeoutSec=30/g' /etc/systemd/system/mysql.service
    fi
    systemctl daemon-reload
  fi
}

function teardown(){
  if [ -f /etc/default/mysql ]; then
    sed -i 's/STARTTIMEOUT=30/STARTTIMEOUT=900/g' /etc/default/mysql
  fi
  if [ ${SYSTEMCTL} -eq 1 ]; then
    if [ -f /lib/systemd/system/mysql.service ]; then
      sed -i 's/TimeoutSec=30/TimeoutSec=600/g' /lib/systemd/system/mysql.service
    #elif [ -f /etc/systemd/system/mysql.service ]; then
    #  sed -i 's/TimeoutSec=30/TimeoutSec=600/g' /etc/systemd/system/mysql.service
    fi
    systemctl daemon-reload
  fi
  if [ -f ${MYSQLCONF} ]; then
    sed -i '${/nonexistingoption=1/d}' ${MYSQLCONF}
    sed -i '${/\[mysqld\]/d}' ${MYSQLCONF}
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
  if [ ${SYSTEMCTL} -eq 1 -a -f /etc/init.d/mysql ]; then
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
  if [ ${SYSTEMCTL} -eq 1 -a -f /etc/init.d/mysql ]; then
    if is_running; then
      run systemctl stop mysql
      [ $status -eq 0 ]
      run is_running
      [ $status -eq 1 ]
    fi
    /etc/init.d/mysql start #3>- &
    [ $? -eq 0 ]
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
    service mysql start 3>- &
    [ $? -eq 0 ]
    sleep 10
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
    service mysql restart 3>- &
    [ $? -eq 0 ]
    sleep 10
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "check if mysql service is enabled in systemd" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    result=$(systemctl is-enabled mysql)
      if [ $result == 'alias' ]; then
          result=$(systemctl is-enabled mysqld)
      fi
    [ $result == "enabled" ]
  else
    skip "system doesn't have systemctl command"
  fi
}

@test "check if mysql service is enabled in sysvinit" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    skip "init system is systemd so other test will do the check"
  elif [ ${SYSVCONFIG} -eq 1 ]; then
    result=$(sysv-rc-conf --list mysql|grep -o ":on"|wc -l)
    [ $result -gt 3 ]
  elif [ ${CHKCONFIG} -eq 1 ]; then
    result=$(chkconfig --list mysql|grep -o ":on"|wc -l)
    [ $result -gt 2 ]
  else
    skip "system doesn't have chkconfig or sysv-rc-conf commands"
  fi
}

@test "add nonexisting option to config file (/etc/mysql/my.cnf) and start with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    # TODO: Check if this can be somehow done for centos with systemd
    if [ ! -f /etc/redhat-release ] && [ ! -f /etc/system-release ]; then
      stopit
      fix_timeout
      echo "[mysqld]" >> ${MYSQLCONF}
      echo "nonexistingoption=1" >> ${MYSQLCONF}
      run systemctl start mysql
      [ $status -eq 1 ]
      run is_running
      [ $status -eq 1 ]
      run sed -i '/nonexistingoption=/d' ${MYSQLCONF}
    fi
  else
    skip "system doesn't have systemctl command"
  fi
}

# disabled until https://jira.percona.com/browse/BLD-737 is fixed
# @test "add nonexisting option to config file (/etc/mysql/my.cnf) and start with service" {
#   if [ ${SERVICE} -eq 1 ]; then
#     stopit
#     fix_timeout
#     echo "[mysqld]" >> ${MYSQLCONF}
#     echo "nonexistingoption=1" >> ${MYSQLCONF}
#     run service mysql start
#     [ $status -eq 1 ]
#     run is_running
#     [ $status -eq 1 ]
#     run sed -i '/nonexistingoption=/d' ${MYSQLCONF}
#   else
#     skip "system doesn't have service command"
#   fi
# }
