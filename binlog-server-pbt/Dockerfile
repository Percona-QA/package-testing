# Build and test image for the percona-binlog-server property-based tests
# (Jenkins job percona-binlog-server-pbt, see README.md).
#
# Same toolchain as the upstream GitHub CI (.github/workflows/cmake.yml in
# percona-binlog-server): Ubuntu 24.04, g++-14 from the distribution,
# libmysqlclient-dev (MySQL 8.0 client) and libcurl4-openssl-dev.
# The Percona Server tarball mysqld (layer D tests) needs libaio / libnuma /
# libncurses at run time.
#
# The image hash is part of the S3 cache key of the Boost / AWS SDK builds,
# so any change here rebuilds them on the next run.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git make cmake pkg-config \
      gcc-14 g++-14 \
      python3 \
      libmysqlclient-dev libcurl4-openssl-dev libssl-dev zlib1g-dev \
      openssl tar gzip xz-utils procps psmisc util-linux \
      libaio1t64 libnuma1 libncurses6 \
 && ln -sf libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1 \
 && rm -rf /var/lib/apt/lists/*

# The job runs the container as the Jenkins user (-u uid:gid) with
# HOME=/tmp/home; git must accept the bind-mounted checkout.
RUN git config --system --add safe.directory '*'

ENV LANG=C.UTF-8
