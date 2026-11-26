Before running set environment variables, eg.:

export DOCKER_ACC="percona"
export PS_VERSION="8.0.32-24"
export ROUTER_VERSION="8.0.32"
export PSHELL_VERSION="8.4.10"        # mysqlsh version in the PS image (tests/test_router_cluster_ha.py)
export PSHELL_BUILT_FOR="8.4.13-13"   # optional: PS release mysqlsh is built for
export TESTING_BRANCH="master"
This is based on: https://testinfra.readthedocs.io/en/latest/examples.html#test-docker-images
