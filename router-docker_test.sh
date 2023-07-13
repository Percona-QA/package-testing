#!/usr/bin/env bash

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
        binlog_checksum=NONE
        enforce_gtid_consistency=ON
        gtid_mode=ON
        relay_log={{ ansible_hostname }}-relay-bin
        innodb_dedicated_server=ON
        binlog_transaction_dependency_tracking=WRITESET
        slave_preserve_commit_order=ON
        slave_parallel_type=LOGICAL_CLOCK
        transaction_write_set_extraction=XXHASH64
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
