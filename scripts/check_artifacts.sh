#!/bin/sh

## check exporters
ls -la /usr/local/percona/pmm2/exporters | grep -q azure_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q mongodb_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q mysqld_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q node_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q postgres_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q proxysql_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q rds_exporter
ls -la /usr/local/percona/pmm2/exporters | grep -q vmagent

## check tools binary

ls -la /usr/local/percona/pmm2/tools | grep -q pt-mongodb-summary
ls -la /usr/local/percona/pmm2/tools | grep -q pt-mysql-summary
ls -la /usr/local/percona/pmm2/tools | grep -q pt-pg-summary
ls -la /usr/local/percona/pmm2/tools | grep -q pt-summary

## check custom query files

ls -la /usr/local/percona/pmm2/collectors/custom-queries/mysql/medium-resolution | grep -q "queries-mysqld.yml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/mysql/high-resolution | grep -q "queries-mysqld.yml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/mysql/high-resolution | grep -q "queries-mysqld-group-replication.yml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/mysql/low-resolution | grep -q "queries-mysqld.yml"

ls -la /usr/local/percona/pmm2/collectors/custom-queries/postgresql/high-resolution | grep -q "example-queries-postgres.yml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/postgresql/high-resolution | grep -q "queries-postgres-uptime.yml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/postgresql/medium-resolution | grep -q "example-queries-postgres.yml"
## Bug PMM-9407 still open
##ls -la /usr/local/percona/pmm2/collectors/custom-queries/postgresql/medium-resolution | grep -q "queries.yaml"
ls -la /usr/local/percona/pmm2/collectors/custom-queries/postgresql/low-resolution | grep -q "example-queries-postgres.yml"
