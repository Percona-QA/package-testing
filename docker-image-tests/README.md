These tests are used to test Percona docker images:

* **proxysql.bats** - starts etcd discovery service, 3 pxc nodes, proxysql, adds nodes to proxysql (if you wish to skip cleanup after running tests just do `export NOCLEANUP=1` before running tests which will leave docker containers running)

* **pxc.bats**  - starts etcd discovery service, 3 pxc nodes, checks the version, proxysql, adds nodes to proxysql (if you wish to skip cleanup after running tests just do `export NOCLEANUP=1` before running tests which will leave docker containers running)
