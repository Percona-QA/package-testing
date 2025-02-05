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
        relay_log={{ ansible_hostname }}-relay-bin
        innodb_dedicated_server=ON
        replica_preserve_commit_order=ON
        replica_parallel_type=LOGICAL_CLOCK
        binlog_transaction_dependency_tracking=WRITESET
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
}

create_new_user(){
    for N in 1 2 3 4
      do sudo docker exec -it mysql$N mysql -uroot -proot \
      -e "CREATE USER 'inno'@'%' IDENTIFIED BY 'inno';" \
      -e "GRANT ALL privileges ON *.* TO 'inno'@'%' with grant option;" \
      -e "reset master;"
    done
    sleep 30
}

verify_new_user(){
    for N in 1 2 3 4
      do sudo docker exec -it mysql$N mysql -uinno -pinno \
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
    sudo docker exec -it mysql1 mysqlsh -uinno -pinno -- dba create-cluster testCluster
}

add_slave(){
    sudo docker exec -it mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql2 --recoveryMethod=incremental

    sleep 10

    sudo docker exec -it mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql3 --recoveryMethod=incremental

    sleep 10

    sudo docker exec -it mysql1 mysqlsh -uinno -pinno -- cluster add-instance --uri=inno@mysql4 --recoveryMethod=incremental

    sleep 10
}	

Router_Bootstrap(){

    sudo docker run -d --name mysql-router --net=innodbnet -e MYSQL_HOST=mysql1 -e MYSQL_PORT=3306 -e MYSQL_USER=inno -e MYSQL_PASSWORD=inno -e MYSQL_INNODB_CLUSTER_MEMBERS=4 $1

	
}

data_add(){

    sudo docker run -d --name=mysql-client --hostname=mysql-client --net=innodbnet -e MYSQL_ROOT_PASSWORD=root -e PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport $1
    
    sleep 10
        
    echo "Adding sbtest user"

    sudo docker exec -it mysql-client mysql -h mysql-router -P 6446 -uinno -pinno \
    -e "CREATE SCHEMA sbtest; CREATE USER sbtest@'%' IDENTIFIED with mysql_native_password by  'password';" \
    -e "GRANT ALL PRIVILEGES ON sbtest.* to sbtest@'%';"

    echo "Verify sbtest user"
    
    sudo docker exec -it mysql-client mysql -h mysql-router -P 6447 -uinno -pinno -e "select host , user from mysql.user where user='sbtest';"
    
    sleep 5
        
    echo "sysbench run"

    sudo docker run --rm=true --net=innodbnet --name=sb-prepare severalnines/sysbench sysbench --db-driver=mysql --table-size=10000 --tables=1 --threads=1 --mysql-host=mysql-router --mysql-port=6446--mysql-user=sbtest --mysql-password=password /usr/share/sysbench/oltp_insert.lua prepare

    sleep 20

    echo "verify if data is inserted or not"
    
    sudo docker exec -it mysql-client mysql -h mysql-router -P 6447 -uinno -pinno -e "SELECT count(*) from sbtest.sbtest1;"
}

verify_replication(){

    for N in 1 2 3 4; 
      do 
      sudo docker exec -it mysql$N mysql -uinno -pinno   -e "SHOW VARIABLES WHERE Variable_name = 'hostname';"   -e "SELECT count(*) from sbtest.sbtest1;"; 
    done
}

Fault_tolerance(){

    echo "Stop One node"

    sudo docker stop mysql1

    sleep 10

    echo "check status"

    sudo docker exec -it mysql-client mysqlsh -h mysql-router -P 6446 -uinno -pinno -- cluster status >> cluster1.json

    sed '1d' cluster1.json >> cluster.json

    status=$(jq -r '.defaultReplicaSet.status' cluster.json)

    echo $status
}

verify_status(){

    if [[ "${status}" = "OK_PARTIAL" ]]; then
      echo "Innodb cluster looks good"
      exit 0
    else 
      echo "Issue in Innodb Cluster"
      exit 1      
    fi

}

cleanup
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
verify_status
