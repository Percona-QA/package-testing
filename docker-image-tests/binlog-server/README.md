Before running set environment variables, eg.:
```
export DOCKER_ACC="perconalab"
export PBS_VERSION="0.4.1-1"
export PS_VERSION="9.7.1-1"
```

`docker_client` is a session-scoped fixture (`tests/conftest.py`) that pulls
both the `percona-binlog-server` and `percona-server` images once.
`pbs_helpers.run_pbs()` (at the job root, alongside `settings.py`, so it
imports the same way `settings` does) runs one `binlog_server` invocation
against a mounted config/data dir, either waiting for it to exit
(one-shot modes) or handing back the running container (`pull` mode).

All storage is the local-filesystem backend — the `s3`/MinIO backend is
not covered here.

- `tests/test_binlog_server_static.py` — runs the image with no source
  server: `binlog_server version`, bare usage output listing all modes,
  and the container's unprivileged user.
- `tests/test_binlog_server_fetch.py` — standalone Percona Server source,
  position-based mode (no GTID), `fetch` + `list`.
- `tests/test_binlog_server_gtid.py` — same, but with `gtid_mode=ON` on
  the source and `replication.mode="gtid"`: `fetch` + `search_by_gtid_set`
  (queries the source's actual `gtid_executed` to build the search value).
- `tests/test_binlog_server_pull.py` — long-running `pull` mode: starts it
  in the background, generates new data on the source while it's running,
  and checks the storage directory grows without restarting it.
- `tests/test_binlog_server_inspect.py` — read-only inspection modes
  against an already-`fetch`ed storage directory with multiple binlog
  files: `search_by_timestamp` and `purge_binlogs`.
