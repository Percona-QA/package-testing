#!/usr/bin/env bash
# Local runner for the pyinfra PXC package tests.
#
# Usage:
#   export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...
#   export PXC_SSH_KEY_PATH=~/.ssh/molecule-pkg-tests.pem
#   ./run.sh <product> <os> [test_repo] [git_account] [testing_branch]
#
# Example:
#   ./run.sh pxc80 ubuntu-noble testing
#
# Instances are destroyed at the end unless KEEP_INSTANCES=1 is set.
set -euo pipefail
cd "$(dirname "$0")"

PRODUCT=${1:?"usage: $0 <product> <os> [test_repo] [git_account] [testing_branch]"}
OS=${2:?"usage: $0 <product> <os> [test_repo] [git_account] [testing_branch]"}
TEST_REPO=${3:-testing}
GIT_ACCOUNT=${4:-Percona-QA}
TESTING_BRANCH=${5:-master}

export PXC_STATE_FILE=${PXC_STATE_FILE:-$PWD/pxc-state.json}
: "${PXC_SSH_KEY_PATH:?Set PXC_SSH_KEY_PATH to the molecule-pkg-tests private key}"
export PXC_SSH_KEY_PATH

JOB_NAME=${JOB_NAME:-pxc-package-testing-pyinfra-local}
BUILD_NUMBER=${BUILD_NUMBER:-0}

PYINFRA_DATA=(
    --data "product=${PRODUCT}"
    --data "install_repo=${TEST_REPO}"
    --data "check_version=yes"
    --data "git_account=${GIT_ACCOUNT}"
    --data "testing_branch=${TESTING_BRANCH}"
)

cleanup() {
    if [ "${KEEP_INSTANCES:-0}" != "1" ]; then
        python3 destroy.py --state-file "${PXC_STATE_FILE}" || true
    else
        echo "KEEP_INSTANCES=1 - leaving instances running (state: ${PXC_STATE_FILE})"
    fi
}
trap cleanup EXIT

python3 provision.py --os "${OS}" --product "${PRODUCT}" \
    --job-name "${JOB_NAME}" --build-number "${BUILD_NUMBER}" \
    --state-file "${PXC_STATE_FILE}"

pyinfra -y --limit bootstrap inventory.py deploy_bootstrap.py "${PYINFRA_DATA[@]}"
pyinfra -y --limit joiners --serial inventory.py deploy_common.py "${PYINFRA_DATA[@]}"

if [ "${BACKUP_LOGS:-0}" = "1" ]; then
    pyinfra -y inventory.py deploy_logsbackup.py \
        --data "workspace=${PWD}" --data "test_phase=install"
fi

echo "PXC ${PRODUCT} install test on ${OS} finished successfully"
