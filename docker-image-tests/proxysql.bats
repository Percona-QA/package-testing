#!/usr/bin/env bats

# do "export NOCLEANUP=1" if you wish to leave environment after test
export NOCLEANUP=${NOCLEANUP:-0}
#
export CLUSTER_NAME=cluster1
export ETCD_HOST=$(nslookup $(hostname)|grep Address|sed '0,/Address/{//d;}'|tail -n1|sed 's/Address: //')
if [ -z ${ETCD_HOST} ]; then
  export ETCD_HOST=$(nslookup "$(hostname).ci.percona.com"|grep Address|sed '0,/Address/{//d;}'|tail -n1|sed 's/Address: //')
fi

if [ -z ${ETCD_HOST} ]; then
  echo "Local IP address was not correctly discovered."
  exit 1
fi

cleanup(){
  docker stop pxc_node1 >/dev/null 2>&1 || true
  docker stop pxc_node2 >/dev/null 2>&1 || true
  docker stop pxc_node3 >/dev/null 2>&1 || true
  docker stop etcd >/dev/null 2>&1 || true
  docker stop ${CLUSTER_NAME}_proxysql >/dev/null 2>&1 || true
  docker rm pxc_node1 >/dev/null 2>&1 || true
  docker rm pxc_node2 >/dev/null 2>&1 || true
  docker rm pxc_node3 >/dev/null 2>&1 || true
  docker rm etcd >/dev/null 2>&1 || true
  docker rm ${CLUSTER_NAME}_proxysql >/dev/null 2>&1 || true
  docker network rm ${CLUSTER_NAME}_net >/dev/null 2>&1 || true
}

@test "cleanup before test" {
  cleanup
}

@test "create docker overlay network" {
  run bash -c "docker network create -d bridge ${CLUSTER_NAME}_net"
  [ $status -eq 0 ]
}

@test "start etcd discovery service" {
  run bash -c "docker run -d -v \/usr\/share\/ca-certificates\/:\/etc\/ssl\/certs -p 4001:4001 -p 2380:2380 -p 2379:2379 --name etcd quay.io\/coreos\/etcd:v2.3.8 -name etcd0 -advertise-client-urls http:\/\/${ETCD_HOST}:2379,http:\/\/${ETCD_HOST}:4001 -listen-client-urls http:\/\/0.0.0.0:2379,http:\/\/0.0.0.0:4001 -initial-advertise-peer-urls http:\/\/${ETCD_HOST}:2380 -listen-peer-urls http:\/\/0.0.0.0:2380 -initial-cluster-token etcd-cluster-1 -initial-cluster etcd0=http:\/\/${ETCD_HOST}:2380 -initial-cluster-state new"
  [ $status -eq 0 ]
}

@test "start pxc node 1" {
  run bash -c "docker run -d -p 3306 --name=pxc_node1 --net=${CLUSTER_NAME}_net -e DISCOVERY_SERVICE=${ETCD_HOST}:2379 -e MYSQL_ROOT_PASSWORD=Theistareyk -e XTRABACKUP_PASSWORD=Theistare -e CLUSTER_NAME=${CLUSTER_NAME} percona\/percona-xtradb-cluster"
  [ $status -eq 0 ]
}

@test "start pxc node 2" {
  run bash -c "docker run -d -p 3306 --name=pxc_node2 --net=${CLUSTER_NAME}_net -e DISCOVERY_SERVICE=${ETCD_HOST}:2379 -e MYSQL_ROOT_PASSWORD=Theistareyk -e XTRABACKUP_PASSWORD=Theistare -e CLUSTER_NAME=${CLUSTER_NAME} percona\/percona-xtradb-cluster"
  [ $status -eq 0 ]
}

@test "start pxc node 3" {
  run bash -c "docker run -d -p 3306 --name=pxc_node3 --net=${CLUSTER_NAME}_net -e DISCOVERY_SERVICE=${ETCD_HOST}:2379 -e MYSQL_ROOT_PASSWORD=Theistareyk -e XTRABACKUP_PASSWORD=Theistare -e CLUSTER_NAME=${CLUSTER_NAME} percona\/percona-xtradb-cluster"
  [ $status -eq 0 ]
}

@test "start proxysql" {
  run bash -c "docker run -d -p 3306:3306 -p 6032:6032 --net=${CLUSTER_NAME}_net --name=${CLUSTER_NAME}_proxysql -e DISCOVERY_SERVICE=${ETCD_HOST}:2379 -e CLUSTER_NAME=${CLUSTER_NAME} -e ETCD_HOST=${ETCD_HOST} -e MYSQL_ROOT_PASSWORD=Theistareyk -e MYSQL_PROXY_USER=proxyuser -e MYSQL_PROXY_PASSWORD=s3cret perconalab\/proxysql"
  [ $status -eq 0 ]
}

@test "check number of registered nodes in etcd" {
  sleep 90
  result=$(curl --silent http://${ETCD_HOST}:2379/v2/keys/pxc-cluster/${CLUSTER_NAME} | jq '.node.nodes[].key' | grep -c "${CLUSTER_NAME}")
  [ $result -eq 3 ]
}

@test "check wsrep_cluster_size is 3" {
  result=$(docker exec -ti pxc_node1 mysql -uroot -pTheistareyk -e "show status;" | grep wsrep_cluster_size | sed 's/ //g' | awk -F '|' '{print $3}')
  [ $result -eq 3 ]
}

@test "add pxc nodes into proxysql" {
  run bash -c "docker exec -it ${CLUSTER_NAME}_proxysql add_cluster_nodes.sh"
  [ $status -eq 0 ]
}

@test "check number of nodes in proxysql mysql_servers table" {
  result=$(docker exec -ti ${CLUSTER_NAME}_proxysql mysql -uadmin -padmin -P6032 -h127.0.0.1 -N -s -e "select count(*) from main.mysql_servers where status='ONLINE';" | grep -v "Warning:" | grep -o "[1-9]")
  [ $result -eq 3 ]
}

@test "check number of nodes in proxysql runtime_mysql_servers table" {
  result=$(docker exec -ti ${CLUSTER_NAME}_proxysql mysql -uadmin -padmin -P6032 -h127.0.0.1 -N -s -e "select count(*) from main.runtime_mysql_servers where status='ONLINE';" | grep -v "Warning:" | grep -o "[1-9]")
  [ $result -eq 3 ]
}

@test "cleanup after test" {
  if [ -z ${NOCLEANUP} -o ${NOCLEANUP} -eq 0 ]; then
    cleanup
  else
    skip
  fi
}

