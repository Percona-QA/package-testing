# percona-binlog-server property-based tests in Jenkins

Files for the ps80 Jenkins job `percona-binlog-server-pbt`
(jenkins-pipelines `ps/jenkins/percona-binlog-server-pbt.groovy`). The job
builds percona-binlog-server with its property-based tests and runs them
with the scripts in `extra/qa` of percona-binlog-server (see
`extra/qa/README.md` there).

| File | Purpose |
|---|---|
| `Dockerfile` | build and test image: Ubuntu 24.04, g++-14, libmysqlclient-dev, libcurl, runtime libraries of the Percona Server tarball |
| `pbt.sh` | the job's steps; every step except `deps-key` runs in the image |

## What a build does

All files stay in the Jenkins workspace. `ws/` is mounted as `/work`
(`WORKDIR`) and holds the percona-binlog-server checkout, as
`extra/qa` expects.

1. **Prepare**: clones package-testing and percona-binlog-server, builds the
   image, lowers `vm.mmap_rnd_bits` to 28 when it is higher (gcc-14
   AddressSanitizer cannot start otherwise).
2. **Boost and AWS SDK** (`pbt.sh deps`): both are built from source for the
   CMake preset (`README.md` of percona-binlog-server). The installed trees
   are cached in
   `s3://percona-jenkins-artifactory/percona-binlog-server-pbt/deps/<key>.tar.gz`.
   The key (`pbt.sh deps-key`) contains the preset, the Boost and AWS SDK
   versions (read from `.github/workflows/cmake.yml` of the branch), a hash
   of their CMake presets and a hash of the `Dockerfile`, so any change
   there rebuilds them. `REBUILD_DEPS` forces a rebuild.
3. **Test environment** (`pbt.sh setup`): `extra/qa/setup_pbt_env.sh
   --with-mysql`, which installs libhegel, hegel-cpp, SeaweedFS and the
   Percona Server minimal tarball for `PS_VERSION`.
4. **Build** (`pbt.sh build`): `extra/qa/build_property_tests.sh`.
5. **Property tests** (`pbt.sh run`): `extra/qa/run_property_tests.py
   --fail-on new`. New issues, regressions and infrastructure errors make
   the build UNSTABLE. The report is archived as `results/`; `junit.xml` is
   published, `summary.md` printed and summarised in the build description.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `PBS_REPO`, `PBS_BRANCH` | tplavcic fork, `pbt-init-tomislav` | percona-binlog-server source |
| `BUILD_TYPE` | `asan_gcc14` | `asan_gcc14`, `asan_gcc14-ubsan`, `release_gcc14`, `debug_gcc14` |
| `PS_VERSION` | `8.4.5-5` | Percona Server for the private mysqld of the MySQL tests |
| `CASES_SCALE` | `1` | `PBT_CASES_SCALE`: 0.1 smoke run, 10 nightly |
| `EXTRA_RUN_ARGS` | | more `run_property_tests.py` arguments, split on spaces, no quoting |
| `KNOWN_AS` | `failure` | how known bugs appear in JUnit (`failure` or `skipped`) |
| `REBUILD_DEPS` | false | rebuild Boost and the AWS SDK and replace the cache |
| `TESTING_REPO`, `TESTING_BRANCH` | Percona-QA, `master` | this repository |

## Running it without Jenkins

```bash
docker build -t pbs-pbt binlog-server-pbt
mkdir -p ws && git clone -b pbt-init-tomislav https://github.com/tplavcic/percona-binlog-server.git ws/percona-binlog-server
for step in deps setup build run; do
  docker run --rm --init -u "$(id -u):$(id -g)" -e HOME=/tmp/home --cap-add SYS_PTRACE --shm-size 2g \
    -e BUILD_TYPE=asan_gcc14 -v "$PWD/ws:/work" -v "$PWD/binlog-server-pbt:/pbt:ro" -w /work \
    pbs-pbt /pbt/pbt.sh "${step}" || break
done
```

## Later: Claude Code analysis

The job is laid out for an analysis stage with
[ci-ai-kit](https://github.com/Percona-Lab/ci-ai-kit)
(`examples/jobs-report/claude-code.Jenkinsfile`): it runs on the EC2 label
`docker-32gb`, whose instance role may call Claude on Bedrock (Hetzner
workers have no AWS role), every step runs in a container, the only AWS key
credential is bound around the S3 cache transfers, and the report is in
`results/` for an agent stage to mount read-only.
