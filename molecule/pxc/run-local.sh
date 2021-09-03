#!/usr/bin/env bash
set -e

function fail {
  echo "Usage: ./run-local.sh version command"
  exit 1
}

command="$2"
if [ -z "$command" ]; then fail; fi

case "$1" in
  "80"|"57"|"56") version="$1" ;;
  *)
    echo 'Error: `version` must be one of [80, 57, 56]'
    fail ;;
esac

export TEST_DIST="${TEST_DIST:-"bento/ubuntu-20.04"}"
export install_repo="testing"
export PXC1_IP="192.168.70.151"
export PXC2_IP="192.168.70.152"
export PXC3_IP="192.168.70.153"

cd "pxc$version-bootstrap"
molecule "$command" -s vagrant
cd -

cd "pxc$version-common"
molecule "$command" -s vagrant
cd -