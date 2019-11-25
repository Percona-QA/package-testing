#!/usr/bin/env bash
export TEST_DIST="bento/centos-7"
export INSTALL_REPO="testing"
export PS_NODE1_IP="192.168.33.50"
export PS_NODE2_IP="192.168.33.51"
export PS_NODE3_IP="192.168.33.52"
export MYSQL_ROUTER_IP="192.168.33.53"
export UPSTREAM_VERSION="8.0.17"
export PS_VERSION="8"
export PS_REVISION="868a4ef"

if [ "$1" == "setup" ]; then
  molecule create
  cd ../ps-innodb-cluster-router
  molecule create
  cd -
  molecule converge
  cd ../ps-innodb-cluster-router
  molecule converge
  cd -
elif [ "$1" == "verify" ]; then
  molecule verify
  cd ../ps-innodb-cluster-router
  molecule verify
  cd -
elif [ "$1" == "destroy" ]; then
  molecule destroy
  cd ../ps-innodb-cluster-router
  molecule destroy
  cd -
fi
