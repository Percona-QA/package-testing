#!/usr/bin/env bash
# Resolve the repo root from this script's own location rather than from cwd, so
# the sbom_checks package is importable however run.sh was invoked.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

pytest -v --junit-xml report.xml "$@"
rc=$?

# Capture the report path before the subshell below: pytest writes it relative
# to the current directory, and $PWD inside the subshell would resolve to $REPO.
REPORT="$PWD/report.xml"

# Label the SBOM results with the architecture before exiting.
#
# This lives here, not in pxb-docker-tests.groovy, for two reasons. The job
# definition pins the pipeline to jenkins-pipelines master, while package-testing
# is cloned per build from PACKAGE_TESTING_REPO_BRANCH -- so labelling from the
# groovy only takes effect after a master merge. And the Jenkins sh step runs
# under /bin/sh -xe, so anything placed after a failing ./run.sh never runs,
# which would drop the labels on exactly the builds that have failures to
# attribute.
#
# pytest's exit code is preserved: labelling must never turn a red build green.
case "${SBOM_PLATFORM_LABEL:-$(uname -m)}" in
    aarch64|arm64) LABEL=arm64 ;;
    x86_64|amd64)  LABEL=amd64 ;;
    *)             LABEL="${SBOM_PLATFORM_LABEL:-unknown}" ;;
esac
(cd "$REPO" && python3 -m sbom_checks.label_junit \
    "$REPORT" --label "$LABEL" --only test_pxb_sbom) || true

exit $rc
