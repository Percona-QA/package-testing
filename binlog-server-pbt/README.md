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
| `report/` | the HTML report and its Claude Code analysis (see "Report") |

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
6. **Report**: `report/report.html`, linked from the build description (see
   below).

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `PBS_REPO`, `PBS_BRANCH` | tplavcic fork, `pbt-init-tomislav` | percona-binlog-server source |
| `BUILD_TYPE` | `asan_gcc14` | `asan_gcc14`, `asan_gcc14-ubsan`, `release_gcc14`, `debug_gcc14` |
| `PS_VERSION` | `8.4.10-10` | Percona Server for the private mysqld of the MySQL tests |
| `CASES_SCALE` | `1` | `PBT_CASES_SCALE`: 0.1 smoke run, 10 nightly |
| `EXTRA_RUN_ARGS` | | more `run_property_tests.py` arguments, split on spaces, no quoting |
| `KNOWN_AS` | `failure` | how known bugs appear in JUnit (`failure` or `skipped`) |
| `REBUILD_DEPS` | false | rebuild Boost and the AWS SDK and replace the cache |
| `AI_REPORT` | true | let Claude Code write up the issues in the report |
| `AI_MODEL`, `AI_EFFORT` | `claude-opus-5-5`, `medium` | model and thinking effort of the analysis |
| `AI_SCOPE` | `all` | `all` issues, or only `new` issues, regressions, flaky failures and possibly fixed issues |
| `AI_MAX_TURNS`, `AI_TIMEOUT_MINUTES` | `300`, `120` | limits of the Claude Code session |
| `TESTING_REPO`, `TESTING_BRANCH` | Percona-QA, `pbt-jenkins` | this repository |

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

## Report

`report/report.html` is one self-contained page (no external scripts or
fonts): the run's totals, properties per test program, what is new in this
run, and every issue with a filter by severity, component and text. A click
on an issue opens its write-up (what happens, root cause, suggested fix,
impact, how to verify), its `known_bugs.md` description and its failures with
the minimal counterexample, the reproduce command and a link to the full log.
`#<ISSUE>` links straight to an issue. `report/report.json` holds the same
data.

| File | Step |
|---|---|
| `report/prepare.py` | facts decided by code: totals, issues grouped by `known_bugs.md` ID (new failures get `NEW-nn`), failures, possibly fixed issues, and the issues to analyse (`AI_SCOPE`) -> `ai/input/base.json` |
| `report/run_agent.py`, `report/agent-prompt.md` | Claude Code, headless on Amazon Bedrock, writes `ai/analysis/<ISSUE>.json` per issue and `ai/analysis/overview.json` |
| `report/audit_agent.py` | checks the session transcript: no network, processes or dynamic code in what the agent wrote or ran, no writes outside `analysis/` and `work/` |
| `report/render_report.py`, `report/template.html` | checks the analysis (fields, lengths, every file it names must exist in the source) and builds the page |

The analysis follows [ci-ai-kit](https://github.com/Percona-Lab/ci-ai-kit)
(`examples/jobs-report/claude-code.Jenkinsfile`):

- the job runs on the EC2 label `docker-32gb`; its instance role
  (`jenkins-ps80-worker`) may call Claude on Bedrock, so no key is stored in
  Jenkins. Hetzner workers have no AWS role;
- Claude Code is pinned (`CLAUDE_CODE_VERSION` in the job) and allowed only
  file tools and `python3`; web tools and subagents are off;
- its container mounts the results, the source and `ai/input` read-only, and
  may write only `ai/analysis` and `ai/work`. Its transcript is its stdout,
  written to `ai/log/` outside the container;
- a failed audit keeps the analysis out of the report; a session that does
  not finish (turn or time limit) leaves the issues it wrote up, and the
  others show their `known_bugs.md` description. Either way the Report stage
  is marked failed and the build result does not change;
- with `AI_REPORT` off the report is built from the test results and
  `known_bugs.md` only.

To build the page from an archived build (or a QA host run) without Jenkins:

```bash
python3 report/prepare.py --results <run dir> --source <percona-binlog-server> --out base.json
python3 report/render_report.py --base base.json --source <percona-binlog-server> --out out --ai off
```
