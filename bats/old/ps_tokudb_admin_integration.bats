#!/usr/bin/env bats

load ps_tokudb_admin_helper

@test "uninstall plugins for cleanup before testing" {
  uninstall_all
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "install TokuDB plugin" {
  if [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  install_tokudb
  check_tokudb_exists
}

@test "uninstall TokuDB plugin" {
  uninstall_tokudb
  check_tokudb_notexists
}

@test "install TokuBackup plugin" {
  if [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  install_tokubackup
  check_tokudb_exists
  check_tokubackup_exists
}

@test "uninstall TokuDB and TokuBackup plugin" {
  uninstall_tokudb
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "install ALL plugins at once" {
  install_all
  check_tokudb_exists
  check_tokubackup_exists
}

@test "uninstall ALL plugins at once" {
  uninstall_all
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "reinstall ALL plugins for upgrade test" {
  install_all
  check_tokudb_exists
  check_tokubackup_exists
}
