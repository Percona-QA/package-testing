MYSQL_VERSION=$(mysqld --version|grep -o "[0-9]\.[0-9]")
CONNECTION=${CONNECTION:--S/run/mysqld/mysqld.sock}
PS_ADMIN_BIN=${PS_ADMIN_BIN:-/usr/bin/ps-admin}

install_qrt() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-qrt
  [ $status -eq 0 ]
}

uninstall_qrt() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-qrt
  [ $status -eq 0 ]
}

check_qrt_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'QUERY_RESPONSE_TIME.*ACTIVE')"
  [ "$result" -eq 4 ]
}

check_qrt_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'QUERY_RESPONSE_TIME'"
  [ $status -eq 1 ]
}

install_audit() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-audit
  [ $status -eq 0 ]
}

check_audit_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'audit_log.*ACTIVE')"
  [ "$result" -eq 1 ]
}

uninstall_audit() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-audit
  [ $status -eq 0 ]
}

check_audit_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'audit_log'"
  [ $status -eq 1 ]
}

install_pam() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-pam
  [ $status -eq 0 ]
}

check_pam_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'auth_pam.*ACTIVE')"
  [ "$result" -eq 1 ]
}

uninstall_pam() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-pam
  [ $status -eq 0 ]
}

check_pam_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'auth_pam'"
  [ $status -eq 1 ]
}

install_mysqlx() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-mysqlx
  [ $status -eq 0 ]
}

check_mysqlx_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'mysqlx.*ACTIVE')"
  [ "$result" -eq 1 ]
}

uninstall_mysqlx() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-mysqlx
  [ $status -eq 0 ]
}

check_mysqlx_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'mysqlx'"
  [ $status -eq 1 ]
}

install_tokudb() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-tokudb
  [ $status -eq 0 ]

  run service mysql restart
  [ $status -eq 0 ]

  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-tokudb
  [ $status -eq 0 ]
}

check_tokudb_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'TokuDB.*ACTIVE')"
  [ "$result" -eq 8 ]

  result="$(mysql ${CONNECTION} -e 'show engines;' | grep -c 'TokuDB')"
  [ "$result" -eq 1 ]
}

uninstall_tokudb() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-tokudb
  [ $status -eq 0 ]
}

check_tokudb_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'TokuDB'"
  [ $status -eq 1 ]

  run bash -c "mysql ${CONNECTION} -e 'show engines;' | grep 'TokuDB'"
  [ $status -eq 1 ]
}

install_tokubackup() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-tokubackup
  [ $status -eq 0 ]

  run service mysql restart
  [ $status -eq 0 ]

  run ${PS_ADMIN_BIN} ${CONNECTION} --enable-tokubackup
  [ $status -eq 0 ]
}

check_tokubackup_exists() {
  result="$(mysql ${CONNECTION} -e 'show plugins;' | grep -c 'tokudb_backup.*ACTIVE')"
  [ "$result" -eq 1 ]
}

uninstall_tokubackup() {
  run ${PS_ADMIN_BIN} ${CONNECTION} --disable-tokubackup
  [ $status -eq 0 ]
}

check_tokubackup_notexists() {
  run bash -c "mysql ${CONNECTION} -e 'show plugins;' | grep 'tokudb_backup'"
  [ $status -eq 1 ]
}

install_all() {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    OPT=""
  elif [ ${MYSQL_VERSION} = "5.6" ]; then
    OPT="--enable-tokudb --enable-tokubackup"
  else
    OPT="--enable-mysqlx --enable-tokudb --enable-tokubackup"
  fi
  run bash -c "${PS_ADMIN_BIN} ${CONNECTION} --enable-qrt --enable-audit --enable-pam ${OPT}"
  [ $status -eq 0 ]

  run service mysql restart
  [ $status -eq 0 ]

  run bash -c "${PS_ADMIN_BIN} ${CONNECTION} --enable-qrt --enable-audit --enable-pam ${OPT}"
  [ $status -eq 0 ]
}

uninstall_all() {
  if [ ${MYSQL_VERSION} = "5.5" ]; then
    OPT=""
  elif [ ${MYSQL_VERSION} = "5.6" ]; then
    OPT="--disable-tokudb --disable-tokubackup"
  else
    OPT="--disable-mysqlx --disable-tokudb --disable-tokubackup"
  fi
  run bash -c "${PS_ADMIN_BIN} ${CONNECTION} --disable-qrt --disable-audit --disable-pam ${OPT}"
  [ $status -eq 0 ]

  run service mysql restart
  [ $status -eq 0 ]

  run bash -c "${PS_ADMIN_BIN} ${CONNECTION} --disable-qrt --disable-audit --disable-pam ${OPT}"
  [ $status -eq 0 ]
}
