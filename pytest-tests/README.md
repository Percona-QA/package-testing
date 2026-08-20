# pytest package tests

These are the pytest port of the legacy `bats/` tests (the original bash tests
are archived under `bats/old/`). They run locally on the target host where the
Percona packages are installed and drive the system through plain `subprocess`
calls.

Explanation of files:

* `test_ps_admin_integration.py` - these tests need to be run when PS is installed
* `test_ps_admin_unit.py` - these tests can be run standalone (without server)
* `ps_admin_plugins.py` - helper functions for the ps-admin integration tests
* `test_mysql_init_scripts.py` - tests for mysql init scripts
* `test_pxc_init_scripts.py` - tests for pxc init scripts
* `test_mongo_init_scripts.py` - tests for mongo init scripts
* `test_ps_tokudb_admin_integration.py` - these tests need to be run when PS is installed
* `test_ps_tokudb_admin_unit.py` - these tests can be run standalone (without server)
* `tokudb_plugins.py` - helper functions for the ps_tokudb_admin integration tests
* `service_helpers.py` - shared init-system helpers (systemctl/service detection, etc.)
* `common.py` - shared subprocess helper and version/connection detection
* `conftest.py` - shared pytest fixtures

Environment variables for testrun customization (if not specified defaults are used):
* `CONNECTION` - specify a way for mysql client to connect and authorize to mysqld, example: `export CONNECTION="-S/run/mysqld/mysqld.sock"`
* `PS_ADMIN_BIN` - specify full path to ps-admin script, example: `export PS_ADMIN_BIN="/usr/bin/ps-admin"`
* `PS_TOKUDB_ADMIN_BIN` - specify full path to ps_tokudb_admin script, example: `export PS_TOKUDB_ADMIN_BIN="/usr/bin/ps_tokudb_admin"`

## Running

Install pytest and run a single file (mirrors how the Ansible jobs invoke them):

```bash
pip3 install pytest
python3 -m pytest -v test_ps_admin_unit.py
```
