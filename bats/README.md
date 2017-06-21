Explanation of files:

* `ps-admin_integration.bats` - these tests need to be run when PS is installed
* `ps-admin_unit.bats` - these tests can be run standalone
* `ps-admin_helper.bash` - helper functions for integration tests
* `mysql-init-scripts.bats` - bats tests for mysql init scripts

Environment variables for testrun customization (if not specified defaults are used):
* `CONNECTION` - specify a way for mysql client to connect and authorize to mysqld, example: `export CONNECTION="-S/run/mysqld/mysqld.sock"`
* `PS_ADMIN_BIN` - specify full path to ps-admin script, example: `export PS_ADMIN_BIN="/usr/bin/ps-admin"`
