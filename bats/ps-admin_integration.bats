#!/usr/bin/env bats

load ps-admin_helper

@test "uninstall plugins for cleanup before testing" {
  uninstall_all
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    check_qrt_notexists
    check_tokubackup_notexists
    check_tokudb_notexists
  fi
  check_audit_notexists
# check_pam_notexists
# check_pam_compat_notexists
  if ! [[ ${MYSQL_VERSION} = "5.6" ]] && ! [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    check_mysqlx_notexists
    check_rocksdb_notexists
  fi
}

@test "install QRT plugin" {

  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have QRT"
  fi
  install_qrt
  check_qrt_exists
}

@test "uninstall QRT plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have QRT"
  fi
  uninstall_qrt
  check_qrt_notexists
}

@test "install Audit Log plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[1-9]{1}$ ]]; then
    skip "PS 8.1 doesn't have Audit log plugin"
  fi
  install_audit
  check_audit_exists
}

@test "uninstall Audit Log plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[1-9]{1}$ ]]; then
    skip "PS 8.1 doesn't have Audit log plugin"
  fi
  uninstall_audit
  check_audit_notexists
}

#test "install PAM plugin" {
# install_pam
# check_pam_exists
#

#test "uninstall PAM plugin" {
# uninstall_pam
# check_pam_notexists
#

#test "install PAM compat plugin" {
# install_pam_compat
# check_pam_compat_exists
#

#test "uninstall PAM compat plugin" {
# uninstall_pam_compat
# check_pam_compat_notexists
#

@test "install MySQL X plugin" {
  if [[ ${MYSQL_VERSION} = "5.6" ]] || [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "MySQL version is not 5.7"
  fi
  install_mysqlx
  check_mysqlx_exists
}

@test "uninstall MySQL X plugin" {
  if [[ ${MYSQL_VERSION} = "5.6" ]] || [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "MySQL version is not 5.7"
  fi
  uninstall_mysqlx
  check_mysqlx_notexists
}

@test "install TokuDB plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have TokuDB"
  fi
  if [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  install_tokudb
  check_tokudb_exists
}

@test "uninstall TokuDB plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have TokuDB"
  fi
  uninstall_tokudb
  check_tokudb_notexists
}

@test "install TokuBackup plugin" {
  if [ $(id -u) -ne 0 ]; then
    skip "This test requires that the current user is root!"
  fi
  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have TokuDB"
  fi
  install_tokubackup
  check_tokudb_exists
  check_tokubackup_exists
}

@test "uninstall TokuDB and TokuBackup plugin" {
  if [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    skip "PS 8 doesn't have TokuDB"
  fi
  uninstall_tokudb
  check_tokubackup_notexists
  check_tokudb_notexists
}

@test "install RocksDB plugin" {
  if [ ${MYSQL_VERSION} = "5.6" ]; then
    skip "MySQL version is not 5.7+"
  fi
  install_rocksdb
  check_rocksdb_exists
}

@test "uninstall RocksDB plugin" {
  if [ ${MYSQL_VERSION} = "5.6" ]; then
    skip "MySQL version is not 5.7+"
  fi
  uninstall_rocksdb
  check_rocksdb_notexists
}

@test "install ALL plugins at once" {
  install_all
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    check_qrt_exists
    check_tokudb_exists
    check_tokubackup_exists
  fi
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[1-9]{1}$ ]]; then
    check_audit_exists
  fi
# check_pam_exists
# check_pam_compat_exists
  if [ ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_exists
    check_rocksdb_exists
  fi
}

@test "uninstall ALL plugins at once" {
  uninstall_all
  check_qrt_notexists
  check_audit_notexists
# check_pam_notexists
# check_pam_compat_notexists
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    check_tokubackup_notexists
    check_tokudb_notexists
  fi
  if [ ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_notexists
    check_rocksdb_notexists
  fi
}

@test "reinstall ALL plugins for upgrade test" {
  install_all
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[0-9]{1}$ ]]; then
    check_qrt_exists
    check_tokudb_exists
    check_tokubackup_exists
  fi
  if ! [[ "${MYSQL_VERSION}" =~ ^8.[1-9]{1}$ ]]; then
    check_audit_exists
  fi
# check_pam_exists
# check_pam_compat_exists
  if [ ${MYSQL_VERSION} != "5.6" ]; then
    check_mysqlx_exists
    check_rocksdb_exists
  fi
}