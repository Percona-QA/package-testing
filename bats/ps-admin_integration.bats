#!/usr/bin/env bats

load ps-admin_helper

@test "uninstall plugins for cleanup before testing" {
  uninstall_all
  check_qrt_notexists
  check_audit_notexists
  check_pam_notexists
  if [ ${MYSQL_VERSION} != "5.5" ]; then
    check_tokubackup_notexists
    check_tokudb_notexists
  fi
  if [ ${MYSQL_VERSION} != "5.5" -a ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_notexists
  fi
}

@test "install QRT plugin" {
  install_qrt
  check_qrt_exists
}

@test "uninstall QRT plugin" {
  uninstall_qrt
  check_qrt_notexists
}

@test "install Audit Log plugin" {
  install_audit
  check_audit_exists
}

@test "uninstall Audit Log plugin" {
  uninstall_audit
  check_audit_notexists
}

@test "install PAM plugin" {
  install_pam
  check_pam_exists
}

@test "uninstall PAM plugin" {
  uninstall_pam
  check_pam_notexists
}

@test "install MySQL X plugin" {
  if [ ${MYSQL_VERSION} = "5.5" -o ${MYSQL_VERSION} = "5.6" ]; then
    skip "MySQL version is not 5.7+"
  fi
  install_mysqlx
  check_mysqlx_exists
}

@test "uninstall MySQL X plugin" {
  if [ ${MYSQL_VERSION} = "5.5" -o ${MYSQL_VERSION} = "5.6" ]; then
    skip "MySQL version is not 5.7+"
  fi
  uninstall_mysqlx
  check_mysqlx_notexists
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
  install_all
  check_qrt_exists
  check_audit_exists
  check_pam_exists
  if [ ${MYSQL_VERSION} != "5.5" ]; then
    check_tokudb_exists
    check_tokubackup_exists
  fi
  if [ ${MYSQL_VERSION} != "5.5" -a ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_exists
  fi
}

@test "uninstall ALL plugins at once" {
  uninstall_all
  check_qrt_notexists
  check_audit_notexists
  check_pam_notexists
  if [ ${MYSQL_VERSION} != "5.5" ]; then
    check_tokubackup_notexists
    check_tokudb_notexists
  fi
  if [ ${MYSQL_VERSION} != "5.5" -a ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_notexists
  fi
}

