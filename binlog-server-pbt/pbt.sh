#!/usr/bin/env bash
# Driver for the percona-binlog-server property-based tests in Jenkins
# (job percona-binlog-server-pbt). See README.md.
#
#   pbt.sh deps-key           print the S3 cache key of the Boost / AWS SDK
#                             build (runs on the Jenkins host)
#   pbt.sh deps               build + install Boost and AWS SDK for the
#                             preset into WORKDIR unless already there
#   pbt.sh setup              extra/qa/setup_pbt_env.sh --with-mysql
#                             (libhegel, hegel-cpp, SeaweedFS, PS tarball)
#   pbt.sh build              extra/qa/build_property_tests.sh
#   pbt.sh run                extra/qa/run_property_tests.py, report in
#                             $WORKDIR/testruns/jenkins
#   pbt.sh describe           one line of HTML from the report's
#                             summary.json, for the Jenkins build description
#
# Everything except deps-key runs inside the image built from ./Dockerfile.
#
# Environment:
#   WORKDIR          workspace (default /work); the percona-binlog-server
#                    checkout must be $WORKDIR/percona-binlog-server
#   BUILD_TYPE       asan_gcc14 | asan_gcc14-ubsan | release_gcc14 |
#                    debug_gcc14 (default asan_gcc14)
#   PS_VERSION       Percona Server version for the private mysqld, e.g.
#                    8.4.5-5 (default)
#   PS_GLIBC         glibc suffix of the minimal tarball (default glibc2.35)
#   PS_TARBALL_URL   full tarball URL, overrides PS_VERSION / PS_GLIBC
#   CASES_SCALE      PBT_CASES_SCALE for the run (default 1)
#   KNOWN_AS         failure | skipped: known bugs in junit.xml (default failure)
#   EXTRA_RUN_ARGS   more run_property_tests.py arguments, split on spaces
#                    (no quoting), e.g. "--filter gtid_set.*Decode --seed 42"
#   IMAGE_ID         identity of the build image, part of the cache key

set -euo pipefail

case "${1:-}" in
  deps-key|deps|setup|build|run|describe) ;;
  *) sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 2 ;;
esac

: "${WORKDIR:=/work}"
: "${BUILD_TYPE:=asan_gcc14}"
: "${PS_VERSION:=8.4.5-5}"
: "${PS_GLIBC:=glibc2.35}"
: "${CASES_SCALE:=1}"
: "${KNOWN_AS:=failure}"
: "${EXTRA_RUN_ARGS:=}"
: "${IMAGE_ID:=unknown}"

PBS_DIR="${WORKDIR}/percona-binlog-server"
QA_DIR="${PBS_DIR}/extra/qa"
REPORT_DIR="${WORKDIR}/testruns/jenkins"

log() { printf '[pbt %s] %s\n' "$(date '+%H:%M:%S')" "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }

# BUILD_TYPE -> CMake preset + extra sanitizers (extra/qa/README.md, "Build variants")
case "${BUILD_TYPE}" in
  asan_gcc14|release_gcc14|debug_gcc14) PRESET="${BUILD_TYPE}"; SANITIZE="" ;;
  asan_gcc14-ubsan) PRESET="asan_gcc14"; SANITIZE="undefined" ;;
  *) die "unsupported BUILD_TYPE: ${BUILD_TYPE}" ;;
esac
export BUILD_PRESET="${PRESET}" PBT_SANITIZE="${SANITIZE}" WORKDIR

[[ -d "${PBS_DIR}/.git" ]] || die "no percona-binlog-server checkout in ${PBS_DIR}"

# Dependency versions follow the upstream CI definition of the checked out
# branch, so a version bump there rebuilds the cache.
ci_env() { # NAME default
  local v
  v="$(sed -n "s/^ *$1: *\([0-9][0-9]*\) *$/\1/p" "${PBS_DIR}/.github/workflows/cmake.yml" 2>/dev/null | head -1)"
  printf '%s' "${v:-$2}"
}
BOOST_VERSION="$(ci_env BOOST_MAJOR 1).$(ci_env BOOST_MINOR 90).$(ci_env BOOST_PATCH 0)"
AWS_SDK_CPP_VERSION="$(ci_env AWS_SDK_CPP_MAJOR 1).$(ci_env AWS_SDK_CPP_MINOR 11).$(ci_env AWS_SDK_CPP_PATCH 774)"

deps_key() {
  local presets_sum
  presets_sum="$(cat "${PBS_DIR}/extra/cmake_presets/boost/CMakePresets.json" \
                     "${PBS_DIR}/extra/cmake_presets/aws-sdk-cpp/CMakePresets.json" \
                 | sha256sum | cut -c1-12)"
  printf '%s/boost-%s_aws-sdk-cpp-%s_presets-%s_image-%s\n' \
    "${PRESET}" "${BOOST_VERSION}" "${AWS_SDK_CPP_VERSION}" "${presets_sum}" "${IMAGE_ID:0:12}"
}

build_dep() { # name git-url git-ref
  local name="$1" url="$2" ref="$3"
  local install="${WORKDIR}/${name}-install-${PRESET}"
  if [[ -d "${install}" ]]; then
    log "${name}: ${install} present"
    return
  fi
  log "${name}: cloning ${url} ${ref}"
  rm -rf "${WORKDIR:?}/${name}" "${WORKDIR}/${name}-build-${PRESET}"
  git -c advice.detachedHead=false clone --quiet --depth 1 --recurse-submodules \
    --shallow-submodules --jobs=8 -b "${ref}" "${url}" "${WORKDIR}/${name}"
  cp "${PBS_DIR}/extra/cmake_presets/${name}/CMakePresets.json" "${WORKDIR}/${name}/"
  log "${name}: configuring (preset ${PRESET})"
  cmake "${WORKDIR}/${name}" --preset "${PRESET}"
  log "${name}: building"
  cmake --build "${WORKDIR}/${name}-build-${PRESET}" --parallel "$(nproc)"
  cmake --install "${WORKDIR}/${name}-build-${PRESET}"
  # sources and build trees are not needed any more and are large
  rm -rf "${WORKDIR:?}/${name}" "${WORKDIR}/${name}-build-${PRESET}"
  log "${name}: installed into ${install}"
}

ps_tarball_url() {
  if [[ -n "${PS_TARBALL_URL:-}" ]]; then
    printf '%s' "${PS_TARBALL_URL}"
    return
  fi
  [[ "${PS_VERSION}" =~ ^([0-9]+\.[0-9]+)\.[0-9]+-[0-9]+$ ]] \
    || die "PS_VERSION must look like 8.4.5-5, got '${PS_VERSION}'"
  local series="${BASH_REMATCH[1]}"
  printf 'https://downloads.percona.com/downloads/Percona-Server-%s/Percona-Server-%s/binary/tarball/Percona-Server-%s-Linux.x86_64.%s-minimal.tar.gz' \
    "${series}" "${PS_VERSION}" "${PS_VERSION}" "${PS_GLIBC}"
}

cmd="${1:-}"
case "${cmd}" in
  deps-key)
    deps_key ;;
  deps)
    log "BUILD_TYPE=${BUILD_TYPE} preset=${PRESET} Boost ${BOOST_VERSION} AWS SDK ${AWS_SDK_CPP_VERSION}"
    build_dep boost https://github.com/boostorg/boost.git "boost-${BOOST_VERSION}"
    build_dep aws-sdk-cpp https://github.com/aws/aws-sdk-cpp.git "${AWS_SDK_CPP_VERSION}" ;;
  setup)
    url="$(ps_tarball_url)"
    log "Percona Server tarball: ${url}"
    MYSQLD_TARBALL_URL="${url}" "${QA_DIR}/setup_pbt_env.sh" --with-mysql
    "${WORKDIR}/mysql/bin/mysqld" --version ;;
  build)
    sanitize_args=()
    [[ -n "${SANITIZE}" ]] && sanitize_args=(--sanitize "${SANITIZE}")
    "${QA_DIR}/build_property_tests.sh" --preset "${PRESET}" "${sanitize_args[@]}"
    "${WORKDIR}/percona-binlog-server-build-${BUILD_TYPE}-pbt/binlog_server" version ;;
  run)
    sanitize_args=()
    [[ -n "${SANITIZE}" ]] && sanitize_args=(--sanitize "${SANITIZE}")
    rm -rf "${REPORT_DIR}"
    set -f  # EXTRA_RUN_ARGS holds regexes such as gtid_set.*, never globs
    # shellcheck disable=SC2086  # EXTRA_RUN_ARGS is split on purpose
    exec python3 "${QA_DIR}/run_property_tests.py" \
      --preset "${PRESET}" "${sanitize_args[@]}" \
      --cases-scale "${CASES_SCALE}" \
      --known-as "${KNOWN_AS}" \
      --fail-on new \
      --output-dir "${REPORT_DIR}" \
      ${EXTRA_RUN_ARGS} ;;
  describe)
    python3 - "${REPORT_DIR}/summary.json" <<'PY'
import html, json, sys
try:
    with open(sys.argv[1]) as f:
        s = json.load(f)
except OSError:
    print("no test report")
    sys.exit(0)
t, r = s["totals"], s["run"]
sev = t.get("known_by_severity", {})
print(f"{html.escape(r.get('variant', ''))}: {t['passed']}/{t['total']} passed, "
      f"<b>{t['new_issues']} new</b>, {t['regressions']} regressions, "
      f"{t['errors']} errors, {t['known_issues']} known "
      f"(high {sev.get('high', 0)}, medium {sev.get('medium', 0)}, low {sev.get('low', 0)}), "
      f"{t['possibly_fixed']} possibly fixed")
PY
    ;;
esac
