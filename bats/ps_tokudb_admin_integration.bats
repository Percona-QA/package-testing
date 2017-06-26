#!/usr/bin/env bats

load ps_tokudb_admin_helper

@test "uninstall plugins for cleanup before testing" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version 5.5 doesn't support TokuDB."
  fi
  uninstall_all
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "install TokuDB plugin" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version is not 5.6+"
  elif [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  install_tokudb
  check_tokudb_exists
}

@test "uninstall TokuDB plugin" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version is not 5.6+"
  fi
  uninstall_tokudb
  check_tokudb_notexists
}

@test "install TokuBackup plugin" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version is not 5.6+"
  elif [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  install_tokubackup
  check_tokudb_exists
  check_tokubackup_exists
}

@test "uninstall TokuDB and TokuBackup plugin" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version is not 5.6+"
  fi
  uninstall_tokudb
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "install ALL plugins at once" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version 5.5 doesn't support TokuDB."
  fi
  install_all
  check_tokudb_exists
  check_tokubackup_exists
}

@test "uninstall ALL plugins at once" {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    skip "MySQL version 5.5 doesn't support TokuDB."
  fi
  uninstall_all
  check_tokubackup_notexists
  check_tokudb_notexists
}
