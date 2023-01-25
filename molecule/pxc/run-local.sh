#!/usr/bin/env bash

# This bash script is used to manually run on the local setup using vagrant

set -e

function fail {
  echo "Usage: ./run-local.sh version test [action]"
  exit 1
}

actions="${3:-"create converge destroy"}"
test="$2"
version="$1"

case "$test" in
  "install")
    export install_repo="${test_repo:-"testing"}"
    export check_version="yes" ;;
  "upgrade")
    export install_repo="main"
    export check_version="no" ;;
  *)
    echo 'Error: `test` must be "install" or "upgrade"'
    fail ;;
esac

case "$version" in
  "80"|"57"|"56") ;;
  *)
    echo 'Error: `version` must be "80", "57" or "56"'
    fail ;;
esac

export TEST_DIST="${TEST_DIST:-"bento/ubuntu-20.04"}"
export PXC1_IP="192.168.70.151"
export PXC2_IP="192.168.70.152"
export PXC3_IP="192.168.70.153"

for action in $actions; do
  cd "pxc$version-bootstrap"
  molecule "$action" -s vagrant
  cd -

  cd "pxc$version-common"
  molecule "$action" -s vagrant
  cd -

  if [ "$test" == "upgrade" ] && [ "$action" == "converge" ]; then
    export install_repo="${test_repo:-"testing"}"
    export check_version="yes"

    cd "pxc$version-bootstrap"
    molecule "$action" -s vagrant
    cd -
  fi
done
