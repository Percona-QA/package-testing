#!/usr/bin/env bats

MYSQL_VERSION=$(mysqld --version|grep -o "[0-9]\.[0-9]")

PS_ADMIN_BIN=${PS_ADMIN_BIN:-/usr/bin/ps-admin}

@test "run ps-admin without any arguments" {
  run ${PS_ADMIN_BIN}
  [ "${lines[0]}" = "ERROR: You should specify one of the --enable or --disable options." ]
}

@test "display ps-admin help screen" {
if [[ "${MYSQL_VERSION}" =~ ^9.[0-9]{1}$ ]] || [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
  run ${PS_ADMIN_BIN} --help
  [ "${lines[1]}" = "Valid options are:" ]
else
  run ${PS_ADMIN_BIN} --help
  [ "${lines[3]}" = "Valid options are:" ]
fi
}

@test "run ps-admin with wrong option" {
  run ${PS_ADMIN_BIN} test
  [ "$status" -eq 1 ]
}

@test "run ps-admin --config-file with missing parameter" {
  run ${PS_ADMIN_BIN} --config-file
  [ "${lines[0]}" = "ps-admin: option '--config-file' requires an argument" ]
  run ${PS_ADMIN_BIN} -c
  [ "${lines[0]}" = "ps-admin: option requires an argument -- 'c'" ]
}

@test "run ps-admin --user with missing parameter" {
  run ${PS_ADMIN_BIN} --user
  [ "${lines[0]}" = "ps-admin: option '--user' requires an argument" ]
  run ${PS_ADMIN_BIN} -u
  [ "${lines[0]}" = "ps-admin: option requires an argument -- 'u'" ]
}

@test "run ps-admin --password with missing parameter" {
  run bash -c "echo '' | ${PS_ADMIN_BIN} --password"
  [ "${lines[0]}" = "Continuing without password..." ]
  run bash -c "echo '' | ${PS_ADMIN_BIN} -p"
  [ "${lines[0]}" = "Continuing without password..." ]
}

@test "run ps-admin --socket with missing parameter" {
  run ${PS_ADMIN_BIN} --socket
  [ "${lines[0]}" = "ps-admin: option '--socket' requires an argument" ]
  run ${PS_ADMIN_BIN} -S
  [ "${lines[0]}" = "ps-admin: option requires an argument -- 'S'" ]
}

@test "run ps-admin --host with missing parameter" {
  run ${PS_ADMIN_BIN} --host
  [ "${lines[0]}" = "ps-admin: option '--host' requires an argument" ]
  run ${PS_ADMIN_BIN} -h
  [ "${lines[0]}" = "ps-admin: option requires an argument -- 'h'" ]
}

@test "run ps-admin --port with missing parameter" {
  run ${PS_ADMIN_BIN} --port
  [ "${lines[0]}" = "ps-admin: option '--port' requires an argument" ]
  run ${PS_ADMIN_BIN} -P
  [ "${lines[0]}" = "ps-admin: option requires an argument -- 'P'" ]
}

@test "run ps-admin --defaults-file with missing parameter" {
  run ${PS_ADMIN_BIN} --defaults-file
  [ "${lines[0]}" = "ps-admin: option '--defaults-file' requires an argument" ]
}

@test "test message for installing TokuDB if user is not root" {
 if [ ${MYSQL_VERSION} != "9.0" ] || [ ${MYSQL_VERSION} != "8.0" ]; then
   if [ $(id -u) -ne 0 ]; then
     run ${PS_ADMIN_BIN} --enable-tokudb
     [ "${lines[0]}" = "ERROR: For TokuDB install/uninstall this script must be run as root!" ]
   else
     skip "This test requires that the current user is not root!"
   fi
 else
   skip "This test requires PS 9.0 below"
 fi
}