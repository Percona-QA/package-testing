#!/bin/bash

if [ $# -eq 0 ];
then
  echo "$0: Missing arguments"
  exit 1
elif [ $# -gt 2 ];
then
  echo "$0: Too many arguments: $@"
  exit 1
else
  echo "We got some argument(s)"
  
  echo "==========================="
  
  echo "Number of arguments.: $#"
  
  echo "List of arguments...: $@"
  
  echo "Arg #1..............: $1"
  
  echo "Arg #2..............: $2"
  
  echo "==========================="
fi


set -xe

cleanup(){

    sudo docker stop mysql1 mysql2 mysql3 mysql4 mysql-client mysql-router || true

    sudo docker rm mysql1 mysql2 mysql3 mysql4 mysql-client mysql-router   || true

    sudo docker network rm innodbnet  || true

    rm -rf cluster1.json cluster.json || true
}

reclaim_disk_space(){
    # mysql1 has been seen dying mid-startup with InnoDB redo log writes
    # failing "No space left on device" - each run leaves behind stopped
    # containers and unused image layers on this node's docker data-root,
    # and it accumulates across runs until the disk is actually full.
    # cleanup() only removes this job's own named containers/network, not
    # that leftover cruft, so prune it here before creating anything new.
    df -h
    sudo docker system prune -af --volumes || true
    df -h
}

create_network(){

    sudo docker network create innodbnet

}

create_mysql_config(){
for N in 1 2 3 4
  do cat <<EOF > my$N.cnf
        [mysqld]
        plugin_load_add='group_replication.so'
EOF

echo "server_id=$(echo $[ $RANDOM % 40 + 10 ])" >> my$N.cnf

cat <<EOF >> my$N.cnf
        enforce_gtid_consistency=ON
        gtid_mode=ON
        relay_log=mysql$N-relay-bin
        innodb_dedicated_server=ON
        innodb_buffer_pool_size=256M
        replica_preserve_commit_order=ON
        replica_parallel_type=LOGICAL_CLOCK
EOF
done
}

start_mysql_containers(){
    for N in 1 2 3 4
      do sudo docker run -d --name=mysql$N --hostname=mysql$N --net=innodbnet \
      -v $PWD/my$N.cnf:/etc/my.cnf \
      -e MYSQL_ROOT_PASSWORD=root $1
    done
    sleep 60

    # A container that died during startup shows up as a cryptic
    # "container ... is not running" from whatever docker exec touches
    # it next (create_new_user). Dump its log here instead, right where
    # the crash actually happened.
    for N in 1 2 3 4
      do if [ "$(sudo docker inspect -f '{{.State.Running}}' mysql$N)" != "true" ]; then
        echo "mysql$N exited during startup - dumping its log:"
        sudo docker logs mysql$N
        exit 1
      fi
    done
}

create_new_user(){
    for N in 1 2 3 4
      do sudo docker exec mysql$N mysql -uroot -proot \
      -e "CREATE USER 'inno'@'%' IDENTIFIED BY 'inno';" \
      -e "GRANT ALL privileges ON *.* TO 'inno'@'%' with grant option;" \
      -e "reset master;"
    done
    sleep 30
}

verify_new_user(){
    for N in 1 2 3 4
      do sudo docker exec mysql$N mysql -uinno -pinno \
      -e "SHOW VARIABLES WHERE Variable_name = 'hostname';" \
      -e "SELECT user FROM mysql.user where user = 'inno';"
    done
    sleep 30
}    


docker_restart(){

    sudo docker restart mysql1 mysql2 mysql3 mysql4
    sleep 10
}  


create_cluster(){
    sudo docker exec mysql1 mysqlsh -uinno -pinno -- dba create-cluster testCluster
}

add_slave(){
    sudo docker exec mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql2 --recoveryMethod=incremental

    sleep 10

    sudo docker exec mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql3 --recoveryMethod=incremental

    sleep 10

    sudo docker exec mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql4 --recoveryMethod=incremental

    sleep 10
}	

Router_Bootstrap(){

    sudo docker run -d --name mysql-router --net=innodbnet -e MYSQL_HOST=mysql1 -e MYSQL_PORT=3306 -e MYSQL_USER=inno -e MYSQL_PASSWORD=inno -e MYSQL_INNODB_CLUSTER_MEMBERS=4 $1

	
}

data_add(){

    sudo docker run -d --name=mysql-client --hostname=mysql-client --net=innodbnet -e MYSQL_ROOT_PASSWORD=root -e PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport $1
    
    sleep 10
        
    echo "Adding sbtest user"

    sudo docker exec mysql-client mysql -h mysql-router -P 6446 -uinno -pinno \
    -e "CREATE SCHEMA sbtest; CREATE USER sbtest@'%' IDENTIFIED with mysql_native_password by  'password';" \
    -e "GRANT ALL PRIVILEGES ON sbtest.* to sbtest@'%';"

    echo "Verify sbtest user"
    
    sudo docker exec mysql-client mysql -h mysql-router -P 6447 -uinno -pinno -e "select host , user from mysql.user where user='sbtest';"
    
    sleep 5
        
    echo "loading sbtest1 data"

    # severalnines/sysbench has no arm64 build, so this can't run on the
    # aarch64 fleet node. Load an equivalent sbtest1 table (same shape
    # sysbench's oltp_insert.lua prepare would create) directly through
    # the mysql client already in the mysql-client container instead -
    # that image is multi-arch, so this works on both amd64 and arm64.
    sudo docker exec mysql-client mysql -h mysql-router -P 6446 -usbtest -ppassword sbtest -e "
      CREATE TABLE sbtest1 (
        id INT NOT NULL AUTO_INCREMENT,
        k INT NOT NULL DEFAULT 0,
        c CHAR(120) NOT NULL DEFAULT '',
        pad CHAR(60) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
      ) ENGINE=InnoDB;
      INSERT INTO sbtest1 (k, c, pad)
      SELECT ROW_NUMBER() OVER (), REPEAT('a', 120), REPEAT('b', 60)
      FROM information_schema.columns a, information_schema.columns b
      LIMIT 10000;
    "

    sleep 20

    echo "verify if data is inserted or not"
    
    sudo docker exec mysql-client mysql -h mysql-router -P 6447 -uinno -pinno -e "SELECT count(*) from sbtest.sbtest1;"
}

verify_replication(){

    for N in 1 2 3 4; 
      do 
      sudo docker exec mysql$N mysql -uinno -pinno   -e "SHOW VARIABLES WHERE Variable_name = 'hostname';"   -e "SELECT count(*) from sbtest.sbtest1;"; 
    done
}

Fault_tolerance(){

    echo "Stop One node"

    sudo docker stop mysql1

    sleep 10

    echo "check status"

    sudo docker exec mysql2 mysqlsh -uinno -pinno -- cluster status > cluster1.json

    cp cluster1.json cluster.json

    status=$(jq -r '.defaultReplicaSet.status' cluster.json)

    echo $status
}

cleanup
reclaim_disk_space
create_network
create_mysql_config
start_mysql_containers $1
create_new_user
verify_new_user
docker_restart
create_cluster
add_slave
Router_Bootstrap $2
data_add $1 
verify_replication
Fault_tolerance
