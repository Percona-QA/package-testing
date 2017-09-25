#!/usr/bin/env bats

PSMDB_MAJ_VER="3.4.7"
SERVER_VERSION="3.4.7-1.8"

DOCKER_NAME="psmdb_image"
DOCKER_REPO="percona/percona-server-mongodb"

# do "export NOCLEANUP=1" if you wish to leave environment after test
export NOCLEANUP=${NOCLEANUP:-0}

cleanup(){
  docker stop ${DOCKER_NAME} >/dev/null 2>&1 || true
  docker rm ${DOCKER_NAME} >/dev/null 2>&1 || true
}

@test "run container" {
  run bash -c "docker run -d --name=${DOCKER_NAME} percona/percona-server-mongodb:${PSMDB_MAJ_VER}"
  [ $status -eq 0 ]
}

@test "check PSMDB server version" {
  sleep 100
  result=$(docker exec -ti ${DOCKER_NAME} mongo --eval "db.version()" | grep -c ${SERVER_VERSION})
  [ $result -gt 1 ]
}

@test "stop container" {
  run bash -c "docker stop ${DOCKER_NAME}"
  [ $status -eq 0 ]
}

@test "start container again" {
  run bash -c "docker start ${DOCKER_NAME}"
  [ $status -eq 0 ]
}

@test "cleanup after test" {
  if [ -z ${NOCLEANUP} -o ${NOCLEANUP} -eq 0 ]; then
    cleanup
  else
    skip
  fi
}
