#!/usr/bin/env bats

load ps_tokudb_admin_helper

PS_TOKUDB_ADMIN_BIN=${PS_TOKUDB_ADMIN_BIN:-/usr/bin/ps_tokudb_admin}

@test "run ps_tokudb_admin without any arguments" {
  run ${PS_TOKUDB_ADMIN_BIN}
  if [ ${MYSQL_VERSION} = "5.7" ]; then
    [ "${lines[1]}" = "ERROR: You should specify --enable,--disable,--enable-backup or --disable-backup option. Use --help for printing options." ]
  else
    [ "${lines[0]}" = "ERROR: You should specify --enable,--disable,--enable-backup or --disable-backup option. Use --help for printing options." ]
  fi
}

@test "display ps_tokudb_admin help screen" {
  run ${PS_TOKUDB_ADMIN_BIN} --help
  if [ ${MYSQL_VERSION} = "5.7" ]; then
    [ "${lines[5]}" = "Valid options are:" ]
  else
    [ "${lines[4]}" = "Valid options are:" ]
  fi
}

@test "run ps_tokudb_admin with wrong option" {
  run ${PS_TOKUDB_ADMIN_BIN} test
  [ "$status" -eq 1 ]
}

@test "run ps_tokudb_admin --user with missing parameter" {
  run ${PS_TOKUDB_ADMIN_BIN} --user
  [ "${lines[0]}" = "ps_tokudb_admin: option '--user' requires an argument" ]
  run ${PS_TOKUDB_ADMIN_BIN} -u
  [ "${lines[0]}" = "ps_tokudb_admin: option requires an argument -- 'u'" ]
}

@test "run ps_tokudb_admin --password with missing parameter" {
  run bash -c "echo '' | ${PS_TOKUDB_ADMIN_BIN} --password"
  [ "${lines[0]}" = "Continuing without password..." ]
  run bash -c "echo '' | ${PS_TOKUDB_ADMIN_BIN} -p"
  [ "${lines[0]}" = "Continuing without password..." ]
}

@test "run ps_tokudb_admin --socket with missing parameter" {
  run ${PS_TOKUDB_ADMIN_BIN} --socket
  [ "${lines[0]}" = "ps_tokudb_admin: option '--socket' requires an argument" ]
  run ${PS_TOKUDB_ADMIN_BIN} -S
  [ "${lines[0]}" = "ps_tokudb_admin: option requires an argument -- 'S'" ]
}

@test "run ps_tokudb_admin --host with missing parameter" {
  run ${PS_TOKUDB_ADMIN_BIN} --host
  [ "${lines[0]}" = "ps_tokudb_admin: option '--host' requires an argument" ]
  run ${PS_TOKUDB_ADMIN_BIN} -h
  [ "${lines[0]}" = "ps_tokudb_admin: option requires an argument -- 'h'" ]
}

@test "run ps_tokudb_admin --port with missing parameter" {
  run ${PS_TOKUDB_ADMIN_BIN} --port
  [ "${lines[0]}" = "ps_tokudb_admin: option '--port' requires an argument" ]
  run ${PS_TOKUDB_ADMIN_BIN} -P
  [ "${lines[0]}" = "ps_tokudb_admin: option requires an argument -- 'P'" ]
}

@test "run ps_tokudb_admin --defaults-file with missing parameter" {
  run ${PS_TOKUDB_ADMIN_BIN} --defaults-file
  [ "${lines[0]}" = "ps_tokudb_admin: option '--defaults-file' requires an argument" ]
}

@test "test message for installing TokuDB if user is not root" {
  if [ $(id -u) -ne 0 ]; then
    run ${PS_TOKUDB_ADMIN_BIN} --enable
    [ "${lines[0]}" = "ERROR: This script must be run as root!" ]
  else
    skip "This test requires that the current user is not root!"
  fi
}
