#!/usr/bin/env bats

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

if [ -f /etc/mongod.conf ]; then
  MONGOCONF=/etc/mongod.conf
fi

function is_running(){
  if [ $(ps aux | grep -v grep | grep "mongod " | wc -l) -eq 0 ]; then
    return 1
  fi

  if [ ${SYSTEMCTL} -eq 1 ]; then
    if [ "$(systemctl is-active mongod)" !=  "active" ]; then
      return 1
    fi
  fi

  return 0
}

function stopit(){
  if is_running; then
    if [ ${SYSTEMCTL} -eq 1 ]; then
      run systemctl stop mongod
      [ $status -eq 0 ]
    else
      run service mongod stop
      [ $status -eq 0 ]
    fi
    run is_running
    [ $status -eq 1 ]
  fi
}

function teardown(){
  if [ -f ${MONGOCONF} ]; then
    sed -i '${/nonexistingoption: true/d}' ${MONGOCONF}
  fi
}

@test "stop mongo if running" {
  stopit
}

@test "start mongo with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl start mongod
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "stop mongo with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl stop mongod
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "restart mongo with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    run systemctl restart mongod
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "stop mongo with /etc/init.d/mongod start with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 -a -f /etc/init.d/mongod ]; then
    run /etc/init.d/mongod stop
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
    run systemctl start mongod
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "start mongo with /etc/init.d/mongod stop with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 -a -f /etc/init.d/mongd ]; then
    if is_running; then
      run systemctl stop mongod
      [ $status -eq 0 ]
      run is_running
      [ $status -eq 1 ]
    fi
    /etc/init.d/mongod start 3>&-
    [ $? -eq 0 ]
    run is_running
    [ $status -eq 0 ]
    run systemctl stop mongod
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl"
  fi
}

@test "start mongo with service" {
  if [ ${SERVICE} -eq 1 ]; then
    service mongod start 3>&-
    [ $? -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "stop mongo with service" {
  if [ ${SERVICE} -eq 1 ]; then
    run service mongod stop
    [ $status -eq 0 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "restart mongo with service" {
  if [ ${SERVICE} -eq 1 ]; then
    service mongod restart 3>&-
    [ $? -eq 0 ]
    run is_running
    [ $status -eq 0 ]
  else
    skip "system doesn't have service command"
  fi
}

@test "check if mongo service is enabled in systemd" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    result=$(systemctl is-enabled mongod)
    [ $result == "enabled" ]
  else
    skip "system doesn't have systemctl command"
  fi
}

@test "check if mongo service is enabled in sysvinit" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    skip "init system is systemd so other test will do the check"
  elif [ ${SYSVCONFIG} -eq 1 ]; then
    result=$(sysv-rc-conf --list mongod|grep -o ":on"|wc -l)
    [ $result -gt 3 ]
  elif [ ${CHKCONFIG} -eq 1 ]; then
    result=$(chkconfig --list mongod|grep -o ":on"|wc -l)
    [ $result -gt 2 ]
  else
    skip "system doesn't have chkconfig or sysv-rc-conf commands"
  fi
}

@test "add nonexisting option to config file (/etc/mongod.conf) and start with systemctl" {
  if [ ${SYSTEMCTL} -eq 1 ]; then
    stopit
    echo "nonexistingoption: true" >> ${MONGOCONF}
    run systemctl start mongod
    [ $status -eq 1 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have systemctl command"
  fi
}

@test "add nonexisting option to config file (/etc/mongod.conf) and start with service" {
  if [ ${SERVICE} -eq 1 ]; then
    stopit
    echo "nonexistingoption: true" >> ${MONGOCONF}
    run service mongod start
    [ $status -eq 1 ]
    run is_running
    [ $status -eq 1 ]
  else
    skip "system doesn't have service command"
  fi
}
