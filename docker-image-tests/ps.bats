#!/usr/bin/env bats

PS_MAJ_VER="5.7.18"
SERVER_VERSION="5.7.18-15"
SERVER_REVISION="bff2cd9"

DOCKER_NAME="ps_image"
DOCKER_REPO="percona/percona-server"

# do "export NOCLEANUP=1" if you wish to leave environment after test
export NOCLEANUP=${NOCLEANUP:-0}

cleanup(){
  docker stop ${DOCKER_NAME} >/dev/null 2>&1 || true
  docker rm ${DOCKER_NAME} >/dev/null 2>&1 || true
}

@test "run container" {
  run bash -c "docker run -d -e MYSQL_ROOT_PASSWORD=secret --name=${DOCKER_NAME} percona/percona-server:${PS_MAJ_VER}"
  [ $status -eq 0 ]
}

@test "check PS server version" {
  sleep 100
  result=$(docker exec -ti ${DOCKER_NAME} mysql -uroot -psecret -e "SHOW VARIABLES LIKE 'version';" | grep -c ${SERVER_VERSION})
  [ $result -eq 1 ]
}

@test "check PS innodb version" {
  result=$(docker exec -ti ${DOCKER_NAME} mysql -uroot -psecret -e "SHOW VARIABLES LIKE 'innodb_version';" | grep -c ${SERVER_VERSION})
  [ $result -eq 1 ]
}

@test "check PS comment version" {
  result=$(docker exec -ti ${DOCKER_NAME} mysql -uroot -psecret -e "SHOW VARIABLES LIKE 'version_comment';" | grep -c ${SERVER_REVISION})
  [ $result -eq 1 ]
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
