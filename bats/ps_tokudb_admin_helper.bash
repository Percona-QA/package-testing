MYSQL_VERSION=$(mysqld --version|grep -o "[0-9]\.[0-9]")
if [ -S /run/mysqld/mysqld.sock ]; then
  CONNECTION=${CONNECTION:--S/run/mysqld/mysqld.sock}
else
  CONNECTION=${CONNECTION:--S/var/lib/mysql/mysql.sock}
fi
PS_TOKUDB_ADMIN_BIN=${PS_TOKUDB_ADMIN_BIN:-/usr/bin/ps_tokudb_admin}

install_tokudb() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable"
  [ $status -eq 0 ]

  systemctl restart mysql >/dev/null 3>&-
  [ $? -eq 0 ]
  sleep 5

  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable"
  [ $status -eq 0 ]
}

check_tokudb_exists() {
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
  [ "$result" -eq 1 ]

  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like BINARY "%TokuDB%" and PLUGIN_STATUS like "ACTIVE";')
  [ "$result" -eq 8 ]
}

uninstall_tokudb() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --disable"
  [ $status -eq 0 ]

  systemctl restart mysql >/dev/null 3>&-
  [ $? -eq 0 ]
  sleep 5
}

check_tokudb_notexists() {
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.ENGINES where ENGINE="TokuDB" and SUPPORT <> "NO";')
  [ "$result" -eq 0 ]

  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb%" and PLUGIN_STATUS like "ACTIVE";')
  [ "$result" -eq 0 ]
}

install_tokubackup() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable-backup"
  [ $status -eq 0 ]

  systemctl restart mysql >/dev/null 3>&-
  [ $? -eq 0 ]
  sleep 5

  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable-backup"
  [ $status -eq 0 ]
}

check_tokubackup_exists() {
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
  [ "$result" -eq 1 ]
}

uninstall_tokubackup() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --disable-backup"
  [ $status -eq 0 ]
}

check_tokubackup_notexists() {
  result=$(mysql ${CONNECTION} -N -s -e 'select count(*) from information_schema.PLUGINS where PLUGIN_NAME like "%tokudb_backup%" and PLUGIN_STATUS like "ACTIVE";')
  [ "$result" -eq 0 ]
}

install_all() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable --enable-backup"
  [ $status -eq 0 ]

  systemctl restart mysql >/dev/null 3>&-
  [ $? -eq 0 ]
  sleep 5

  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --enable --enable-backup"
  [ $status -eq 0 ]
}

uninstall_all() {
  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --disable --disable-backup"
  [ $status -eq 0 ]

  systemctl restart mysql >/dev/null 3>&-
  [ $? -eq 0 ]
  sleep 5

  run bash -c "${PS_TOKUDB_ADMIN_BIN} ${CONNECTION} --disable --disable-backup"
  [ $status -eq 0 ]
}
