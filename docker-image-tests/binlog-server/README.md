Before running set environment variables, eg.:
```
export DOCKER_ACC="perconalab"
export PBS_VERSION="0.4.1-1"
export PS_VERSION="8.0.42-33"
```

`docker_client` is a session-scoped fixture (`tests/conftest.py`) that pulls
both the `percona-binlog-server` and `percona-server` images once.

`tests/test_binlog_server_static.py` runs the image with no source server:
`binlog_server version`, bare usage output, and the container's unprivileged
user.

`tests/test_binlog_server_fetch.py` starts a standalone Percona Server
container as the replication source (position-based mode, no GTID), creates
a `REPLICATION SLAVE` user, generates some data, then runs
`binlog_server fetch <config>` against it with a local-filesystem storage
backend and checks binlog files land on disk and `binlog_server list`
reports them. This only covers `fetch` mode against a `file` storage
backend — `pull` (long-running/reconnecting) mode and the `s3` backend are
not exercised here.
