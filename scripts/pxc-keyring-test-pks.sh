############################################################
# Created by Mohit Joshi                                   #
# Creation date: 20-Jan-2022                               #
############################################################
#!/bin/bash
set +xe

# Same for the same os

BASEDIR=/usr/

FILE_PLUGIN=0
VAULT_PLUGIN=0

PXC_START_TIMEOUT=120


SSH_EOF=$(ssh root@DB1_PUB """cat /etc/os-release""")
#echo $SSH_EOF


if [[ "$SSH_EOF" =~ "debian" ]]; then

echo "Debian"
MYSQL_LIB_PATH=/usr/lib/mysql
MYSQL_GALERA_LIBPATH=/usr/lib/galera4
CHAR_SETS_DIR=/usr/share/mysql
LC_MSG_DIR=/usr/share/mysql

elif [[ "$SSH_EOF" =~ "rhel" ]]; then

echo "RHEL"
MYSQL_LIB_PATH=/usr/lib64/mysql
MYSQL_GALERA_LIBPATH=/usr/lib64/galera4
CHAR_SETS_DIR=/usr/share/percona-xtradb-cluster
LC_MSG_DIR=/usr/share/percona-xtradb-cluster

elif [[ "$SSH_EOF" =~ "fedora" ]]; then

echo "FEDOROA"
MYSQL_LIB_PATH=/usr/lib64/mysql
MYSQL_GALERA_LIBPATH=/usr/lib64/galera4
CHAR_SETS_DIR=/usr/share/percona-xtradb-cluster
LC_MSG_DIR=/usr/share/percona-xtradb-cluster

else 

echo "Not supported OS"

fi



echo "Path of libs MYSQL: $MYSQL_LIB_PATH GALERA4: $MYSQL_GALERA_LIBPATH"
echo "Path of CHAR SETS: $CHAR_SETS_DIR LC_MSG_DIR: $LC_MSG_DIR"


# Confusion regarding the vault part: I think it should be in any one server (preferably on bootstrap ?)
start_vault_server() {
  #Start vault server for testing
  
  ssh mysql@DB1_PUB """

    echo "Setting up vault server"
    rm -rf ~/vault; mkdir ~/vault
    rm -rf get_download_link.sh 
    rm -rf vault_test_setup.sh

    wget https://raw.githubusercontent.com/Percona-QA/percona-qa/master/vault_test_setup.sh
    chmod +x vault_test_setup.sh

    wget https://raw.githubusercontent.com/Percona-QA/percona-qa/master/get_download_link.sh
    chmod +x get_download_link.sh

    killall vault > /dev/null 2>&1
    ~/vault_test_setup.sh --workdir=~/vault --setup-pxc-mount-points --use-ssl > /dev/null 2>&1
  
  """
}

sysbench_run() {

ssh mysql@DB1_PUB """  
  echo "...Creating sysbench user"
  sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"CREATE USER 'sysbench'@'localhost' IDENTIFIED BY 'test'\"
  echo "Successful"
  echo "...Granting permissions to sysbench user"
  sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"GRANT ALL ON *.* TO 'sysbench'@'localhost'\"
  echo "Successful"
  echo "...Creating sbtest database"
  sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"DROP DATABASE IF EXISTS sbtest\"
  sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"CREATE DATABASE sbtest ENCRYPTION='Y'\"
  echo "Successful"

  echo "...Preparing sysbench data on Node 1"
  sudo sysbench /usr/share/sysbench/oltp_insert.lua --mysql-db=sbtest --mysql-user=sysbench --mysql-password=test --db-driver=mysql --threads=5 --tables=50 --table-size=1000 prepare > /dev/null 2>&1
  echo "Data loaded successfully"
  echo "...Running sysbench load on Node 1 for 30 seconds"
  sudo sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-db=sbtest --mysql-user=sysbench --mysql-password=test --db-driver=mysql --threads=5 --tables=50 --time=30 --report-interval=1 --events=1870000000 --db-ps-mode=disable run > /dev/null 2>&1
  echo "Sysbench run successful"
"""

# Wait for the nodes sync
  sleep 2;
  echo "...Random verification of table counts"
  for X in $(seq 1 10); do
    RAND=$[$RANDOM%50 + 1 ]
  # -N suppresses column names and -s is silent mode
    
    count_1=$(ssh mysql@DB1_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -Ns -e\"SELECT count(*) FROM sbtest.sbtest$RAND\" """)
    count_2=$(ssh mysql@DB2_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -Ns -e\"SELECT count(*) FROM sbtest.sbtest$RAND\" """)
    count_3=$(ssh mysql@DB3_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -Ns -e\"SELECT count(*) FROM sbtest.sbtest$RAND\" """)

  if [ $count_1 -eq $count_2 ]; then
   if [ $count_2 -eq $count_3 ]; then
     echo "Data replicated and matched successfully sbtest$RAND count: $count_1 = $count_2 = $count_3"
   else
     echo "Data mismatch found. sbtest$RAND count: $count_2 : $count_3"
   fi
  else
   echo "Data mismatch found. sbtest$RAND count: $count_1 : $count_2"
   echo "Exiting.."
   exit 1
  fi
done
}

cleanup() {
  component_name=$1
  echo "Deleting global & local manifest files from all 3 nodes"
  for i in $(seq 1 3); do
    if [ $i -eq 1 ]; then
      ssh root@DB1_PUB <<'DB1'
        set -xe
        rm -rf /usr/sbin/mysqld.my || true
        rm -rf /var/lib/mysql
        SSH_EOF=$(cat /etc/os-release)
        if [[ "$SSH_EOF" =~ "rhel" ]]; then 
          echo "Removing the my.cnf in redhat" ; rm -rf /etc/my.cnf* ; 
        elif [[ "$SSH_EOF" =~ "fedora" ]]; then 
          echo "Removing the my.cnf in fedora" ; rm -rf /etc/my.cnf* ; 
        else 
          echo "None of RHEL or FEDORA" ; 
        fi
        echo '--------------END--------------' >> /var/log/mysql/error.log
DB1
    elif [ $i -eq 2 ]; then
      ssh root@DB2_PUB <<'DB2'
        set -xe
        SSH_EOF=$(cat /etc/os-release)
        rm -rf /usr/sbin/mysqld.my || true
        rm -rf /var/lib/mysql
        if [[ "$SSH_EOF" =~ "rhel" ]]; then 

          echo "Removing the my.cnf in redhat" ; rm -rf /etc/my.cnf* ; 
        elif [[ "$SSH_EOF" =~ "fedora" ]]; then 
         
          echo "Removing the my.cnf in fedora" ; rm -rf /etc/my.cnf* ; 
        else 
          echo "None of RHEL or FEDORA" ; 
        fi
        echo '--------------END--------------' >> /var/log/mysql/error.log
DB2
    elif [ $i -eq 3 ]; then
      ssh root@DB3_PUB <<'DB3'
        set -xe
        rm -rf /usr/sbin/mysqld.my || true
        rm -rf /var/lib/mysql
        SSH_EOF=$(cat /etc/os-release)
        if [[ "$SSH_EOF" =~ "rhel" ]]; then 
         
          echo "Removing the my.cnf in redhat" ; rm -rf /etc/my.cnf* ; 
        elif [[ "$SSH_EOF" =~ "fedora" ]]; then 
         
          echo "Removing the my.cnf in fedora" ; rm -rf /etc/my.cnf* ; 
        else 
          echo "None of RHEL or FEDORA" ; 
        fi
        echo '--------------END--------------' >> /var/log/mysql/error.log
DB3
    fi
  done

  echo "Deleting global & local config files from all 3 nodes"
  for i in $(seq 1 3); do
    if [ $i -eq 1 ]; then
      ssh root@DB1_PUB """
        set -xe
        rm -rf $MYSQL_LIB_PATH/plugin/component_$component_name.cnf || true
      """   
    elif [ $i -eq 2 ]; then
      ssh root@DB2_PUB """
        set -xe
        rm -rf $MYSQL_LIB_PATH/plugin/component_$component_name.cnf || true
      """
    elif [ $i -eq 3 ]; then
      ssh root@DB3_PUB """
        set -xe
        rm -rf $MYSQL_LIB_PATH/plugin/component_$component_name.cnf || true
      """
    fi
  done


}

kill_server(){

  for i in $(seq 1 3); do
    if [ $i -eq 1 ]; then
      ssh mysql@DB1_PUB """
        sudo systemctl stop mysql@bootstrap
        sudo systemctl disable mysql@bootstrap
      """
    elif [ $i -eq 2 ]; then
      ssh mysql@DB2_PUB """
        sudo systemctl stop mysql
        sudo systemctl disable mysql
      """
    elif [ $i -eq 3 ]; then
      ssh mysql@DB3_PUB """
        sudo systemctl stop mysql
        sudo systemctl disable mysql
      """
    fi
  done

}


kill_kmip_server(){

      ssh mysql@DB1_PUB """
        set -xe

        sudo killall pykmip-server
        sudo rm -rf /home/mysql/PyKMIP
        
      """

}

create_global_manifest() {
  component_name=$1
  node=$2

  echo "Node$node: Creating global manifest file for component: $component_name"
  if [ "$component_name" == "keyring_file" ]; then
    STRING="file://component_keyring_file"
  elif [ "$component_name" == "keyring_kmip" ]; then
    STRING="file://component_keyring_kmip"
  elif [ "$component_name" == "keyring_kms" ]; then
    STRING="file://component_keyring_kms"
  fi

  if [ $node -eq 1 ]; then
    ssh root@DB1_PUB """
  set -xe

  cat << EOF > /usr/sbin/mysqld.my
{ 
\"components\":\"$STRING\"
}
EOF

    """  
  elif [ $node -eq 2 ]; then

    ssh root@DB2_PUB """
  set -xe

  cat << EOF >  /usr/sbin/mysqld.my
{ 
\"components\":\"$STRING\"
}
EOF


    """
  elif [ $node -eq 3 ]; then

    ssh root@DB3_PUB """
  set -xe

  cat << EOF >  /usr/sbin/mysqld.my
{ 
\"components\":\"$STRING\"
}
EOF

    """
  fi
}
# Local manifest file is used in pair with Global manifest file
create_local_manifest() {
  component_name=$1
  node=$2

  echo "Node$node: Creating local manifest file for component: $component_name"
  if [ "$component_name" == "keyring_file" ]; then
    STRING="file://component_keyring_file"
  elif [ "$component_name" == "keyring_kmip" ]; then
    STRING="file://component_keyring_kmip"
  elif [ "$component_name" == "keyring_kms" ]; then
    STRING="file://component_keyring_kms"
  fi

  if [ $node -eq 1 ]; then
ssh root@DB1_PUB """
  set -xe
    echo "Node$node: Creating global manifest file for component: $component_name"
    cat << EOF > /usr/sbin/mysqld.my
{
\"read_local_manifest\":true
}
EOF

    cat << EOF > /var/lib/mysql/mysqld.my
{
 \"components\": \"$STRING\"
}
EOF

"""
  elif [ $node -eq 2 ]; then
ssh root@DB2_PUB """
  set -xe
    echo "Node$node: Creating global manifest file for component: $component_name"
    cat << EOF > /usr/sbin/mysqld.my
{
\"read_local_manifest\":true
}
EOF

    cat << EOF > /var/lib/mysql/mysqld.my
{
 \"components\": \"$STRING\"
}
EOF

"""
  elif [ $node -eq 3 ]; then
ssh root@DB3_PUB """
  set -xe
    echo "Node$node: Creating global manifest file for component: $component_name"
    cat << EOF > /usr/sbin/mysqld.my
{
\"read_local_manifest\":true
}
EOF

    cat << EOF > /var/lib/mysql/mysqld.my
{
 \"components\": \"$STRING\"
}
EOF

"""
  fi

}

# Copy the config

create_global_config() {
  component_name="$1"
  node=$2
  if [ $node -eq 1 ]; then
    BASEDIR=$BASEDIR1
    WORKDIR=$WORKDIR1
ssh root@DB1_PUB """

  set -xe

  echo "Node$node: Creating global configuration file for component: $component_name"
  if [ "$component_name" = "keyring_file" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
 \"server_addr\": \"127.0.0.1\",
 \"server_port\": \"5696\",
 \"client_ca\": \"/etc/mysql/certs/kmip/client_certificate_john_smith.pem\",
 \"client_key\": \"/etc/mysql/certs/kmip/client_key_john_smith.pem\",
 \"server_ca\": \"/etc/mysql/certs/kmip/root_certificate.pem\"
}
EOF
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Not Supported"
  fi  
"""

  elif [ $node -eq 2 ]; then
    BASEDIR=$BASEDIR2
    WORKDIR=$WORKDIR2
ssh root@DB2_PUB """
  set -xe

  echo "Node$node: Creating global configuration file for component: $component_name"
  if [ "$component_name" = "keyring_file" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
 \"server_addr\": \"DB1_PRIV\",
 \"server_port\": \"5696\",
 \"client_ca\": \"/etc/mysql/certs/kmip/client_certificate_john_smith.pem\",
 \"client_key\": \"/etc/mysql/certs/kmip/client_key_john_smith.pem\",
 \"server_ca\": \"/etc/mysql/certs/kmip/root_certificate.pem\"
}
EOF
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Not Supported"
  fi  
"""

  elif [ $node -eq 3 ]; then
    BASEDIR=$BASEDIR3
    WORKDIR=$WORKDIR3
ssh root@DB3_PUB """
  set -xe

  echo "Node$node: Creating global configuration file for component: $component_name"
  if [ "$component_name" = "keyring_file" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
 \"server_addr\": \"DB1_PRIV\",
 \"server_port\": \"5696\",
 \"client_ca\": \"/etc/mysql/certs/kmip/client_certificate_john_smith.pem\",
 \"client_key\": \"/etc/mysql/certs/kmip/client_key_john_smith.pem\",
 \"server_ca\": \"/etc/mysql/certs/kmip/root_certificate.pem\"
}
EOF
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Not Supported"
  fi  
"""
  fi

}

setup_kmip_server(){

ssh root@DB1_PUB <<'SHELL'

set -xe

cd /home/mysql/

git clone https://github.com/OpenKMIP/PyKMIP.git

cat << EOF >/home/mysql/PyKMIP/server.conf

[server]
hostname=0.0.0.0
port=5696
certificate_path=/etc/mysql/certs/kmip/server_certificate.pem
key_path=/etc/mysql/certs/kmip/server_key.pem
ca_path=/etc/mysql/certs/kmip/root_certificate.pem
auth_suite=TLS1.2
policy_path=/etc/mysql/certs/kmip
enable_tls_client_auth=True
logging_level=DEBUG
database_path=/home/mysql/PyKMIP/pykmip.db

EOF

touch /home/mysql/PyKMIP/logfile

pip3 install --upgrade pip

sudo pip3 install SQLAlchemy==1.4.46

if [ $(cat /etc/os-release  | grep -o buster | uniq | wc -l) -eq 1 ]
then

echo "Detected Buster"

elif [ $(cat /etc/os-release  | grep -o bullseye | uniq | wc -l) -eq 1 ]
then

echo "Detected Bullseye"

elif [ $(cat /etc/os-release  | grep -o focal | uniq | wc -l) -eq 1 ]
then

echo "Detected Ubuntu Focal"

else

echo "Not buster,bullseye or Ubuntu Focal so installing required packages"
sudo pip3 install urllib3==1.26.15
sudo pip3 install setuptools_rust

fi

pip3 show sqlalchemy

cd PyKMIP

sudo python3 setup.py install

export PATH=$PATH:/usr/local/bin/

cd bin

python3 create_certificates.py

scp -o StrictHostKeyChecking=no -r *.pem root@DB1_PRIV:/etc/mysql/certs/kmip/
scp -o StrictHostKeyChecking=no -r *.pem root@DB2_PRIV:/etc/mysql/certs/kmip/
scp -o StrictHostKeyChecking=no -r *.pem root@DB3_PRIV:/etc/mysql/certs/kmip/

cd ..

tmux new -d 'pykmip-server -f server.conf -l logfile'

sleep 120

ps -aux | grep pykmip

SHELL
}

create_local_config() {
  component_name=$1
  node=$2
  if [ $node -eq 1 ]; then
    BASEDIR=$BASEDIR1
    WORKDIR=$WORKDIR1
ssh root@DB1_PUB """
  if [ "$component_name" = "keyring_file" ]; then
    echo "Node$node: Creating global configuration file component_keyring_file.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
  \"read_local_config\": true
}
EOF
  echo "Node$node: Creating local configuration file"
  cat << EOF >/var/lib/mysql/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kmip.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kms.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kms.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  fi
"""
  elif [ $node -eq 2 ]; then
    BASEDIR=$BASEDIR2
    WORKDIR=$WORKDIR2
ssh root@DB2_PUB """
  if [ "$component_name" = "keyring_file" ]; then
    echo "Node$node: Creating global configuration file component_keyring_file.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
  \"read_local_config\": true
}
EOF
  echo "Node$node: Creating local configuration file"
  cat << EOF >/var/lib/mysql/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kmip.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kms.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kms.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  fi
"""
  elif [ $node -eq 3 ]; then
    BASEDIR=$BASEDIR3
    WORKDIR=$WORKDIR3
ssh root@DB3_PUB """
  if [ "$component_name" = "keyring_file" ]; then
    echo "Node$node: Creating global configuration file component_keyring_file.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_file.cnf
{
  \"read_local_config\": true
}
EOF
  echo "Node$node: Creating local configuration file"
  cat << EOF >/var/lib/mysql/component_keyring_file.cnf
{
 \"path\": \"/var/lib/mysql/component_keyring_file\",
 \"read_only\": false
}
EOF
  elif [ "$component_name" = "keyring_kmip" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kmip.cnf"
    cat << EOF >$MYSQL_LIB_PATH/plugin/component_keyring_kmip.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  elif [ "$component_name" = "keyring_kms" ]; then
    echo "Node$node: Creating global configuration file component_keyring_kms.cnf"
    cat << EOF >${BASEDIR}/lib/plugin/component_keyring_kms.cnf
{
  \"read_local_config\": true
}
EOF
    echo "Node$node: Creating local configuration file for component: $component_name"
    echo "Not Supported"
  fi
"""
  fi
}

create_conf() {

node=$1

echo "parameter val is $node"

if [ $node -eq 1 ]; then

echo "Creating n1.cnf"

ssh root@DB1_PUB """

set -xe

sudo cat << EOF > /etc/mysql/my.cnf
[mysqld]

port = 4000
server-id=1
log-error-verbosity=3
core-file

# file paths
basedir=/usr/
datadir=/var/lib/mysql
plugin_dir=$MYSQL_LIB_PATH/plugin/
log-error=/var/log/mysql/error.log
general_log=1
general_log_file=/var/log/mysql/general.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
socket=/var/run/mysqld/mysqld.sock
character-sets-dir=$CHAR_SETS_DIR/charsets
lc-messages-dir=$LC_MSG_DIR/
pid-file=/var/run/mysqld/mysqld.pid

# pxc variables
log_bin=binlog
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
master_verify_checksum=on
binlog_checksum=CRC32
binlog_encryption=OFF
pxc_encrypt_cluster_traffic=ON

# wsrep variables
wsrep_cluster_address='gcomm://DB2_PRIV:6030,DB3_PRIV:6030'
wsrep_provider=$MYSQL_GALERA_LIBPATH/libgalera_smm.so
wsrep_sst_receive_address=DB1_PRIV:6020
wsrep_node_incoming_address=DB1_PRIV
wsrep_slave_threads=2
wsrep_cluster_name=my_pxc
wsrep_provider_options = \"gmcast.listen_addr=tcp://DB1_PRIV:6030; base_host=DB1_PRIV; base_port=6030; ist.recv_addr=DB1_PRIV;\"
wsrep_sst_method=xtrabackup-v2
wsrep_node_name=node4000
innodb_autoinc_lock_mode=2

ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
[client]
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/client-cert.pem
ssl-key = /etc/mysql/certs/client-key.pem
[sst]
encrypt = 4
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
EOF


if [ $FILE_PLUGIN -eq 1 ]; then
  echo "Sedding"
  sed -i '3i early-plugin-load=keyring_file.so' /etc/mysql/my.cnf
  sed -i '4i keyring_file_data=keyring' /etc/mysql/my.cnf
elif [ $VAULT_PLUGIN -eq 1 ]; then
  sed -i '3i early-plugin-load=keyring_vault.so'  /etc/mysql/my.cnf
  sed -i '4i loose-keyring_vault_config=/home/mohit.joshi/pxc_scripts/vault/keyring_vault_pxc1.cnf'  /etc/mysql/my.cnf
fi

cat /etc/mysql/my.cnf
"""
fi

if [ $node -eq 2 ]; then

echo "Creating n2.cnf"

ssh root@DB2_PUB """
set -xe
sudo cat << EOF > /etc/mysql/my.cnf
[mysqld]

port = 5000
server-id=2
log-error-verbosity=3
core-file

# file paths
basedir=/usr/
datadir=/var/lib/mysql
plugin_dir=$MYSQL_LIB_PATH/plugin/
log-error=/var/log/mysql/error.log
general_log=1
general_log_file=/var/log/mysql/general.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
socket=/var/run/mysqld/mysqld.sock
character-sets-dir=$CHAR_SETS_DIR/charsets
lc-messages-dir=$LC_MSG_DIR/
pid-file=/var/run/mysqld/mysqld.pid

# pxc variables
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
master_verify_checksum=on
binlog_checksum=CRC32
binlog_encryption=OFF
pxc_encrypt_cluster_traffic=ON

# wsrep variables
wsrep_cluster_address='gcomm://DB1_PRIV:6030,DB3_PRIV:6030'
wsrep_provider=$MYSQL_GALERA_LIBPATH/libgalera_smm.so
wsrep_sst_receive_address=DB2_PRIV:6020
wsrep_node_incoming_address=DB2_PRIV
wsrep_slave_threads=2
wsrep_cluster_name=my_pxc
wsrep_provider_options = \"gmcast.listen_addr=tcp://DB2_PRIV:6030; base_host=DB2_PRIV; base_port=6030; ist.recv_addr=DB2_PRIV;\"
wsrep_sst_method=xtrabackup-v2
wsrep_node_name=node5000
innodb_autoinc_lock_mode=2

ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
[client]
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/client-cert.pem
ssl-key = /etc/mysql/certs/client-key.pem
[sst]
encrypt = 4
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
EOF

if [ $FILE_PLUGIN -eq 1 ]; then
  sed -i '3i early-plugin-load=keyring_file.so' /etc/mysql/my.cnf
  sed -i '4i keyring_file_data=keyring' /etc/mysql/my.cnf
elif [ $VAULT_PLUGIN -eq 1 ]; then
  sed -i '3i early-plugin-load=keyring_vault.so' /etc/mysql/my.cnf
  sed -i '4i loose-keyring_vault_config=/home/mohit.joshi/pxc_scripts/vault/keyring_vault_pxc2.cnf' /etc/mysql/my.cnf
fi

cat /etc/mysql/my.cnf

"""


fi

if [ $node -eq 3 ]; then

echo "Creating n3.cnf"
ssh root@DB3_PUB """
set -xe

sudo cat << EOF > /etc/mysql/my.cnf
[mysqld]

port = 6000
server-id=3
log-error-verbosity=3
core-file

# file paths
basedir=/usr/
datadir=/var/lib/mysql
plugin_dir=$MYSQL_LIB_PATH/plugin/
log-error=/var/log/mysql/error.log
general_log=1
general_log_file=/var/log/mysql/general.log
slow_query_log=1
slow_query_log_file=/var/log/mysql/slow.log
socket=/var/run/mysqld/mysqld.sock
character-sets-dir=$CHAR_SETS_DIR/charsets
lc-messages-dir=$LC_MSG_DIR/
pid-file=/var/run/mysqld/mysqld.pid

# pxc variables
binlog_format=ROW
gtid_mode=ON
enforce_gtid_consistency=ON
master_verify_checksum=on
binlog_checksum=CRC32
binlog_encryption=OFF
pxc_encrypt_cluster_traffic=ON

# wsrep variables
wsrep_cluster_address='gcomm://DB1_PRIV:6030,DB2_PRIV:6030'
wsrep_provider=$MYSQL_GALERA_LIBPATH/libgalera_smm.so
wsrep_sst_receive_address=DB3_PRIV:6020
wsrep_node_incoming_address=DB3_PRIV
wsrep_slave_threads=2
wsrep_debug=1
wsrep_cluster_name=my_pxc
wsrep_provider_options = \"gmcast.listen_addr=tcp://DB3_PRIV:6030; base_host=DB3_PRIV; base_port=6030; ist.recv_addr=DB3_PRIV;\"
wsrep_sst_method=xtrabackup-v2
wsrep_node_name=node6000
innodb_autoinc_lock_mode=2

ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
[client]
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/client-cert.pem
ssl-key = /etc/mysql/certs/client-key.pem
[sst]
encrypt = 4
ssl-ca = /etc/mysql/certs/ca.pem
ssl-cert = /etc/mysql/certs/server-cert.pem
ssl-key = /etc/mysql/certs/server-key.pem
EOF

if [ $FILE_PLUGIN -eq 1 ]; then
  sed -i '3i early-plugin-load=keyring_file.so' /etc/mysql/my.cnf
  sed -i '4i keyring_file_data=keyring' /etc/mysql/my.cnf
elif [ $VAULT_PLUGIN -eq 1 ]; then
  sed -i '3i early-plugin-load=keyring_vault.so' /etc/mysql/my.cnf
  sed -i '4i loose-keyring_vault_config=/home/mohit.joshi/pxc_scripts/vault/keyring_vault_pxc3.cnf' /etc/mysql/my.cnf
fi

cat /etc/mysql/my.cnf
"""
fi

}


# how this function will work ?

# how this function will work ?
pxc_startup_status(){
  NR=$1

  for X in $(seq 0 ${PXC_START_TIMEOUT}); do
    sleep 1

    if [ $NR -eq 1 ]; then

      OUTPUT=$(ssh mysql@DB1_PUB """sudo mysqladmin -uroot -S /var/run/mysqld/mysqld.sock ping | grep 'mysqld is alive'""") > /dev/null 2>&1

    elif [ $NR -eq 2 ]; then

      OUTPUT=$(ssh mysql@DB2_PUB """sudo mysqladmin -uroot -S /var/run/mysqld/mysqld.sock ping | grep 'mysqld is alive'""") > /dev/null 2>&1

    elif [ $NR -eq 3 ]; then

      OUTPUT=$(ssh mysql@DB3_PUB """sudo mysqladmin -uroot -S /var/run/mysqld/mysqld.sock ping | grep 'mysqld is alive'""") > /dev/null 2>&1

    fi

    echo "OUTPUT Command response: $OUTPUT"

    if [[ ! -z $OUTPUT ]]; then
      echo "Node$NR started successfully. Error log: $ERR_FILE"
      break
    fi
    if [ $X -eq ${PXC_START_TIMEOUT} ]; then
      echo "Node$NR could not start within the time period. Error log: $ERR_FILE"
      exit 1
    fi
  done
}
# how this function will work ?
init_datadir_template() {

ssh mysql@DB1_PUB /bin/bash <<'EOF'

  set -xe  
  echo $PATH
  export PATH=$PATH:/usr/sbin
  echo "Creating datadir template db1"
  sudo echo " " > /var/log/mysql/error.log
  echo "Listing the mysql dir if present..."
  sudo mkdir /var/lib/mysql-data-dir
  sudo chown mysql:root /var/lib/mysql-data-dir
  mysqld --no-defaults --datadir=/var/lib/mysql-data-dir --basedir=/usr/ --initialize-insecure
  
EOF

ssh mysql@DB2_PUB /bin/bash <<'EOF'

  set -xe
  echo $PATH
  export PATH=$PATH:/usr/sbin
  echo "Creating datadir template db2"
  sudo echo " " > /var/log/mysql/error.log
  echo "Listing the mysql dir if present..."
  sudo mkdir /var/lib/mysql-data-dir
  sudo chown mysql:root /var/lib/mysql-data-dir
  mysqld --no-defaults --datadir=/var/lib/mysql-data-dir --basedir=/usr/ --initialize-insecure

EOF

ssh mysql@DB3_PUB /bin/bash <<'EOF'

  set -xe
  export PATH=$PATH:/usr/sbin
  echo "Creating datadir template  db3"
  sudo echo " " > /var/log/mysql/error.log
  echo "Listing the mysql dir if present..."
  sudo mkdir /var/lib/mysql-data-dir
  sudo chown mysql:root /var/lib/mysql-data-dir
  mysqld --no-defaults --datadir=/var/lib/mysql-data-dir --basedir=/usr/ --initialize-insecure

EOF

  echo "Data template created successfully"
}

# how this function will work ?
init_datadir() {
  echo "Creating data directories [Copying them from the /var/lib/mysql-data-dir location]"
  
  ssh mysql@DB1_PUB  """
    set -xe
    echo "Copy data dir template files to /var/lib/ for Node1"
    sudo cp -ar /var/lib/mysql-data-dir /var/lib/mysql
    sudo chown mysql:root /var/lib/mysql
  """

  ssh mysql@DB2_PUB  """
    set -xe
    echo "Copy data dir template files to /var/lib/ for Node2"
    sudo cp -ar /var/lib/mysql-data-dir /var/lib/mysql
    sudo chown mysql:root /var/lib/mysql
  """


  ssh mysql@DB3_PUB """
    set -xe
    echo "Copy data dir template files to /var/lib/ for Node3"
    sudo cp -ar /var/lib/mysql-data-dir /var/lib/mysql
    sudo chown mysql:root /var/lib/mysql
  """

  echo "Data template copied successfully"


}
#-----------------------

start_node1(){
echo "Starting PXC nodes..."

ssh mysql@DB1_PUB /bin/bash <<'EOF'
    
    set -xe

    sudo systemctl start mysql@bootstrap

EOF

  pxc_startup_status 1
}

start_node2() {


ssh mysql@DB2_PUB /bin/bash <<'EOF'
    
    set -xe

    sudo systemctl enable mysql
    
    sudo systemctl start mysql || true

    sleep 120 

    if [ $(systemctl status mysql | grep -o running | uniq | wc -l) -eq 1 ]; 
    then

          echo "=====================================NODE 2 STARTED Successfully using 'systemctl start mysql' INIT==================================================="

    else

          echo "=====================================NODE 2 FAILED TO Start using 'systemctl start mysql' INIT==================================================="
          cat -n /var/log/mysql/error.log
          
          echo "=====================================RESTARTING THE NODE 2 using 'systemctl restart mysql' INIT==================================================="
          sudo systemctl restart mysql 

    fi


EOF
    pxc_startup_status 2

}

start_node3() {

ssh mysql@DB3_PUB /bin/bash <<'EOF'
  
    set -xe

    sudo systemctl enable mysql

    sudo systemctl start mysql || true

    sleep 120 
    
    if [ $(systemctl status mysql | grep -o running | uniq | wc -l) -eq 1 ]; 
    then

          echo "=====================================NODE 3 STARTED Successfully using 'systemctl start mysql' INIT==================================================="

    else

          echo "=====================================NODE 3 FAILED TO Start using 'systemctl start mysql' INIT==================================================="
          cat -n /var/log/mysql/error.log
          
          echo "=====================================RESTARTING THE NODE 3 using 'systemctl restart mysql'==================================================="
          sudo systemctl restart mysql 

    fi



EOF




    pxc_startup_status 3

}


#-----------------------


#start_node1(){
#echo "Starting PXC nodes..."
#
#ssh mysql@DB1_PUB /bin/bash <<'EOF'
#    
#    set -xe
#
#    sudo systemctl start mysql@bootstrap
#
#EOF
#
#  pxc_startup_status 1
#}
#
#start_node2() {
#
#ssh mysql@DB2_PUB /bin/bash <<'EOF'
#    
#    set -xe
#
#    sudo systemctl enable mysql
#    
#    sudo systemctl start mysql || true
#    
#    echo "Waiting for 120 Seconds"
#
#    sleep 120
#
#    echo "-----------------------------------------------RESTARTING MYSQL-----------------------------------------------" >> /var/log/mysql/error.log
#
#    echo "Restarting the mysql Service"
#
#    sudo systemctl restart mysql
#
#EOF
#    pxc_startup_status 2
#
#}
#
#start_node3() {
#
#ssh mysql@DB3_PUB /bin/bash <<'EOF'
#  
#    set -xe
#
#    sudo systemctl enable mysql
#
#    sudo systemctl start mysql || true
#    
#    echo "Waiting for 120 Seconds"
#
#    sleep 120
#
#    echo "-----------------------------------------------RESTARTING MYSQL-----------------------------------------------" >> /var/log/mysql/error.log
#
#    echo "Restarting the mysql Service"
#
#    sudo systemctl restart mysql
#
#EOF
#    pxc_startup_status 3
#
#}

write_log_error(){

ssh mysql@DB1_PUB "echo "$1" >> /var/log/mysql/error.log"
ssh mysql@DB2_PUB "echo "$1" >> /var/log/mysql/error.log"
ssh mysql@DB3_PUB "echo "$1" >> /var/log/mysql/error.log"

}



cluster_up_check() {
  echo "Checking 3 node PXC Cluster startup..."
  for X in $(seq 0 10); do
  
    sleep 1
    CLUSTER_UP=0;

    echo "Node1: " 
    ssh mysql@DB1_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}'

    echo "Node2: " 
    ssh mysql@DB2_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}'
    
    echo "Node3: " 
    ssh mysql@DB3_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}'
    

    if [ $(ssh mysql@DB1_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}') -eq 3 ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

    if [ $(ssh mysql@DB2_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}') -eq 3 ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

    if [ $(ssh mysql@DB3_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_cluster_size'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_cluster" """ | awk '{print$2}') -eq 3 ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

    if [ "$(ssh mysql@DB1_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_local_state_comment'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_local" """ | awk '{print$2}')" == "Synced" ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

    if [ "$(ssh mysql@DB2_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_local_state_comment'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_local" """ | awk '{print$2}')" == "Synced" ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

    if [ "$(ssh mysql@DB3_PUB """sudo mysql -uroot -S /var/run/mysqld/mysqld.sock -e\"show global status like 'wsrep_local_state_comment'\" | sed 's/[| \t]\+/\t/g' | grep "wsrep_local" """ | awk '{print$2}')" == "Synced" ]; then CLUSTER_UP=$[ ${CLUSTER_UP} + 1]; fi

  # If count reached 6 (there are 6 checks), then the Cluster is up & running and consistent in it's Cluster topology views (as seen by each node)

    if [ ${CLUSTER_UP} -eq 6 ]; then
      echo "3 Node PXC Cluster started ok. Clients:"
      echo "Node #1: `echo mysql | sed 's|/mysqld|/mysql|'` -uroot"
      echo "Node #2: `echo mysql | sed 's|/mysqld|/mysql|'` -uroot"
      echo "Node #3: `echo mysql | sed 's|/mysqld|/mysql|'` -uroot"
      break
    fi
done
}

###########################################
# Actual testing starts here              #
###########################################


sleep 2
#echo "Cleaning up all previous global and local manifest and config files"
#cleanup keyring_file
#cleanup keyring_kmip

echo "###########################################################################"
echo "#Testing Combo 5: component_keyring_file |local Manifest | local Config #"
echo "###########################################################################" 
init_datadir_template 

# Can be removed after wards as inited in combo 1 
#create_workdir

cleanup keyring_file

init_datadir
create_conf 1
create_conf 2
create_conf 3

create_local_manifest keyring_file 1
create_local_manifest keyring_file 2
create_local_manifest keyring_file 3

create_local_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3

write_log_error ===================COMBO_5_COMPONENT_KEYRING_FILE_LOCAL_MANIFEST_LOCAL_CONFIG===================

start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "....................Listing the local manifest and local config files...................."
ssh root@DB1_PUB """
  echo "Check local manifest in VM1"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB2_PUB """
  echo "Check local manifest in VM2"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB3_PUB """
  echo "Check local manifest in VM3"
  cat /usr/sbin/mysqld.my
"""

start_vault_server

echo "Killing previous running mysqld"
kill_server
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "CLEANED"

echo "###########################################################################"
echo "#Testing Combo 1.1: component_keyring |Global Manifest | Global Config #"
echo "###########################################################################"

init_datadir

create_conf 1
create_conf 2
create_conf 3

create_global_manifest keyring_file 1
create_global_manifest keyring_file 2
create_global_manifest keyring_file 3

create_global_config keyring_file 1
create_global_config keyring_file 2
create_global_config keyring_file 3

write_log_error ===================COMBO_1_1_COMPONENT_KEYRING_GLOBAL_MANIFEST_GLOBAL_CONFIG===================

start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"


cluster_up_check

sysbench_run


echo "....................Listing the global manifest and global config files...................."

ssh root@DB1_PUB """
  echo "Check global manifest in VM1"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB2_PUB """
  echo "Check global manifest in VM2"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB3_PUB """
  echo "Check global manifest in VM3"
  cat /usr/sbin/mysqld.my
"""

#start_vault_server

echo "Killing previous running mysqld"
kill_server
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file




echo "###########################################################################"
echo "#Testing Combo 1.1: keyring_kmip |Global Manifest | Global Config #"
echo "###########################################################################"

init_datadir

create_conf 1
create_conf 2
create_conf 3

create_global_manifest keyring_kmip 1
create_global_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3

create_global_config keyring_kmip 1
create_global_config keyring_kmip 2
create_global_config keyring_kmip 3

write_log_error ===================COMBO_1_1_KEYRING_KMIP_GLOBAL_MANIFEST_GLOBAL_CONFIG===================

setup_kmip_server

start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"


cluster_up_check

sysbench_run

echo "....................Listing the global manifest and global config files...................."

ssh root@DB1_PUB """
  echo "Check global manifest in VM1"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB2_PUB """
  echo "Check global manifest in VM2"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB3_PUB """
  echo "Check global manifest in VM3"
  cat /usr/sbin/mysqld.my
"""

echo "Killing previous running mysqld"
kill_server
kill_kmip_server
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip




echo "###########################################################################"
echo "#Testing Combo 5-Repeat after 1.1 : component_keyring_file |local Manifest | local Config #"
echo "###########################################################################" 
init_datadir 

# Can be removed after wards as inited in combo 1 
#create_workdir
create_conf 1
create_conf 2
create_conf 3

create_local_manifest keyring_file 1
create_local_manifest keyring_file 2
create_local_manifest keyring_file 3

create_local_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3

write_log_error ===================COMBO_5_COMPONENT_KEYRING_FILE_LOCAL_MANIFEST_LOCAL_CONFIG===================

start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "....................Listing the local manifest and local config files...................."
ssh root@DB1_PUB """
  echo "Check local manifest in VM1"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB2_PUB """
  echo "Check local manifest in VM2"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB3_PUB """
  echo "Check local manifest in VM3"
  cat /usr/sbin/mysqld.my
"""

start_vault_server

echo "Killing previous running mysqld"
kill_server
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "CLEANED"


echo "###########################################################################"
echo "#Testing Combo 1.1-Repeat: component_keyring |Global Manifest | Global Config #"
echo "###########################################################################"

init_datadir

create_conf 1
create_conf 2
create_conf 3

create_global_manifest keyring_file 1
create_global_manifest keyring_file 2
create_global_manifest keyring_file 3

create_global_config keyring_file 1
create_global_config keyring_file 2
create_global_config keyring_file 3

write_log_error ===================COMBO_1_1_COMPONENT_KEYRING_GLOBAL_MANIFEST_GLOBAL_CONFIG===================

start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"


cluster_up_check

sysbench_run


echo "....................Listing the global manifest and global config files...................."

ssh root@DB1_PUB """
  echo "Check global manifest in VM1"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB2_PUB """
  echo "Check global manifest in VM2"
  cat /usr/sbin/mysqld.my
"""

ssh root@DB3_PUB """
  echo "Check global manifest in VM3"
  cat /usr/sbin/mysqld.my
"""
echo "Killing previous running mysqld"
kill_server
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "CLEANED"




#echo "###########################################################################"
#echo "#Testing Combo 1: component_keyring_kms |Global Manifest | Global Config #"
#echo "###########################################################################"
#init_datadir
#
#create_conf 1
#create_conf 2
#create_conf 3
#
#create_global_manifest keyring_kms 1
#create_local_manifest keyring_kms 2
#create_global_manifest keyring_kms 3
#
#create_global_config keyring_kms 1
#create_global_config keyring_kms 2
#create_global_config keyring_kms 3
#
#write_log_error ===================COMBO_1_COMPONENT_KEYRING_KMS_GLOBAL_MANIFEST_GLOBAL_CONFIG===================
#
#start_node1;MPID1="$!"
#start_node2;MPID2="$!"
#start_node3;MPID3="$!"
#
#cluster_up_check
#
#sysbench_run
#
#echo "....................Listing the global manifest and global config files...................."
#
#ssh root@DB1_PUB """
#  echo "Check global manifest in VM1"
#  cat /usr/sbin/mysqld.my
#"""
#
#ssh root@DB2_PUB """
#  echo "Check global manifest in VM2"
#  cat /usr/sbin/mysqld.my
#"""
#
#ssh root@DB3_PUB """
#  echo "Check global manifest in VM3"
#  cat /usr/sbin/mysqld.my
#"""
#
#
#
#echo "Killing previous running mysqld"
#kill_server
#remove_workdir
#echo "Cleaning up all previous global and local manifest and config files"
#cleanup keyring_kms
#
#exit 1
#echo "###########################################################################"
#echo "#Testing Combo 2: component_keyring_kms | Global Manifest | Local Config #"
#echo "###########################################################################"
#create_workdir
#create_conf 1
#create_conf 2
#create_conf 3
#init_datadir
#create_global_manifest keyring_kms 1
#create_global_manifest keyring_kms 2
#create_global_manifest keyring_kms 3
#create_local_config keyring_kms 1
#create_local_config keyring_kms 2
#create_local_config keyring_kms 3
#start_node1;MPID1="$!"
#start_node2;MPID2="$!"
#start_node3;MPID3="$!"
#cluster_up_check
#sysbench_run
#echo "Killing previous running mysqld"
#kill_server
#remove_workdir
#echo "Cleaning up all previous global and local manifest and config files"
#cleanup keyring_kms


exit 1


#echo "###########################################################################"
#echo "#Testing Combo 3: component_keyring_kms | Local Manifest | Global Config #"
#echo "###########################################################################"
#create_workdir
#create_conf 1
#create_conf 2
#create_conf 3
#init_datadir
#create_local_manifest keyring_kms 1
#create_local_manifest keyring_kms 2
#create_local_manifest keyring_kms 3
#create_global_config keyring_kms 1
#create_global_config keyring_kms 2
#create_global_config keyring_kms 3
#start_node1;MPID1="$!"
#start_node2;MPID2="$!"
#start_node3;MPID3="$!"
#cluster_up_check
#sysbench_run

#echo "Killing previous running mysqld"
#kill_server
#remove_workdir
#echo "Cleaning up all previous global and local manifest and config files"
#cleanup keyring_kms
#
#echo "###########################################################################"
#echo "#Testing Combo 4: component_keyring_kms | Local Manifest | Local Config  #"
#echo "###########################################################################"
#create_workdir
#create_conf 1
#create_conf 2
#create_conf 3
#init_datadir
#create_local_manifest keyring_kms 1
#create_local_manifest keyring_kms 2
#create_local_manifest keyring_kms 3
#create_local_config keyring_kms 1
#create_local_config keyring_kms 2
#create_local_config keyring_kms 3
#start_node1;MPID1="$!"
#start_node2;MPID2="$!"
#start_node3;MPID3="$!"
#cluster_up_check
#
#echo "Killing previous running mysqld"
#kill_server
#remove_workdir
#echo "Cleaning up all previous global and local manifest and config files"
#cleanup keyring_kms

echo "###########################################################################"
echo "#Testing Combo 5: component_keyring_file |Global Manifest | Global Config #"
echo "###########################################################################" 
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_global_manifest keyring_file 2
create_global_manifest keyring_file 3
create_global_config keyring_file 1
create_global_config keyring_file 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "#Testing Combo 6: component_keyring_file | Global Manifest | Local Config #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_global_manifest keyring_file 2
create_global_manifest keyring_file 3
create_local_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "#Testing Combo 7: component_keyring_file | Local Manifest | Global Config #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_local_manifest keyring_file 2
create_local_manifest keyring_file 3
create_global_config keyring_file 1
create_global_config keyring_file 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "#Testing Combo 8: component_keyring_file | Local Manifest | Local Config  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_local_manifest keyring_file 2
create_local_manifest keyring_file 3
create_local_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "############################################################################"
echo "#Testing Combo 9: component_keyring_kmip | Global Manifest | Global Config #"
echo "############################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kmip 1
create_global_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_global_config keyring_kmip 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "###########################################################################"
echo "#Testing Combo 10: component_keyring_kmip | Global Manifest | Local Config #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kmip 1
create_global_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3
create_local_config keyring_kmip 1
create_local_config keyring_kmip 2
create_local_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "###########################################################################"
echo "#Testing Combo 11: component_keyring_kmip | Local Manifest | Global Config #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_local_manifest keyring_kmip 2
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_global_config keyring_kmip 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "###########################################################################"
echo "#Testing Combo 12: component_keyring_kmip | Local Manifest | Local Config  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_local_manifest keyring_kmip 2
create_local_manifest keyring_kmip 3
create_local_config keyring_kmip 1
create_local_config keyring_kmip 2
create_local_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing any previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file
cleanup keyring_kmip

echo "###########################################################################"
echo "# Testing Combo 13: component_keyring_kms                                 #"
echo "# Node 1: Global Manifest | Global Config                                 #"
echo "# Node 2: Local Manifest  | Local Config                                  #"
echo "# Node 3: Global Manifest | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kms 1
create_local_manifest keyring_kms 2
create_global_manifest keyring_kms 3
create_global_config keyring_kms 1
create_local_config keyring_kms 2
create_local_config keyring_kms 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms

echo "############################################################################"
echo "# Testing Combo 14: component_keyring_kms                                  #"
echo "# Node 1: Global Manifest | Local Config                                   #"
echo "# Node 2: Local Manifest  | Global Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                  #"
echo "############################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kms 1
create_local_manifest keyring_kms 2
create_global_manifest keyring_kms 3
create_local_config keyring_kms 1
create_global_config keyring_kms 2
create_global_config keyring_kms 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms

echo "###########################################################################"
echo "# Testing Combo 15: component_keyring_kms                                 #"
echo "# Node 1: Local Manifest  | Global Config                                 #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Local Manifest  | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kms 1
create_global_manifest keyring_kms 2
create_local_manifest keyring_kms 3
create_global_config keyring_kms 1
create_local_config keyring_kms 2
create_local_config keyring_kms 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms

echo "###########################################################################"
echo "# Testing Combo 16: component_keyring_kms                                 #"
echo "# Node 1: Local Manifest  | Local Config                                  #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                 #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kms 1
create_global_manifest keyring_kms 2
create_global_manifest keyring_kms 3
create_local_config keyring_kms 1
create_local_config keyring_kms 2
create_global_config keyring_kms 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms

echo "###########################################################################"
echo "# Testing Combo 17: component_keyring_file                                 #"
echo "# Node 1: Global Manifest | Global Config                                 #"
echo "# Node 2: Local Manifest  | Local Config                                  #"
echo "# Node 3: Global Manifest | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_local_manifest keyring_file 2
create_global_manifest keyring_file 3
create_global_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "############################################################################"
echo "# Testing Combo 18: component_keyring_file                                 #" 
echo "# Node 1: Global Manifest | Local Config                                   #"
echo "# Node 2: Local Manifest  | Global Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                  #"
echo "############################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_local_manifest keyring_file 2
create_global_manifest keyring_file 3
create_local_config keyring_file 1
create_global_config keyring_file 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "# Testing Combo 19: component_keyring_file                                #"
echo "# Node 1: Local Manifest  | Global Config                                 #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Local Manifest  | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_global_manifest keyring_file 2
create_local_manifest keyring_file 3
create_global_config keyring_file 1
create_local_config keyring_file 2
create_local_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "# Testing Combo 20: component_keyring_file                                #"
echo "# Node 1: Local Manifest  | Local Config                                  #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                 #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_global_manifest keyring_file 2
create_global_manifest keyring_file 3
create_local_config keyring_file 1
create_local_config keyring_file 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_file

echo "###########################################################################"
echo "# Testing Combo 21: component_keyring_kmip                                #"
echo "# Node 1: Global Manifest | Global Config                                 #"
echo "# Node 2: Local Manifest  | Local Config                                  #"
echo "# Node 3: Global Manifest | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kmip 1
create_local_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_local_config keyring_kmip 2
create_local_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "############################################################################"
echo "# Testing Combo 22: component_keyring_kmip                                 #"
echo "# Node 1: Global Manifest | Local Config                                   #"
echo "# Node 2: Local Manifest  | Global Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                  #"
echo "############################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_kmip 1
create_local_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3
create_local_config keyring_kmip 1
create_global_config keyring_kmip 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "###########################################################################"
echo "# Testing Combo 23: component_keyring_kmip                                #"
echo "# Node 1: Local Manifest  | Global Config                                 #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Local Manifest  | Local Config                                  #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_global_manifest keyring_kmip 2
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_local_config keyring_kmip 2
create_local_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "###########################################################################"
echo "# Testing Combo 24: component_keyring_kmip                                #"
echo "# Node 1: Local Manifest  | Local Config                                  #"
echo "# Node 2: Global Manifest | Local Config                                  #"
echo "# Node 3: Global Manifest | Global Config                                 #"
echo "###########################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_global_manifest keyring_kmip 2
create_global_manifest keyring_kmip 3
create_local_config keyring_kmip 1
create_local_config keyring_kmip 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "#####################################################################"
echo "# Testing Combo 25: Cross Component Testing                         #"
echo "# Node 1: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "# Node 2: component_keyring_file | Global Manifest | Local Config   #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_global_manifest keyring_file 2
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_local_config keyring_file 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 26: Cross Component Testing                         #"
echo "# Node 1: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "# Node 2: component_keyring_kms  | Global Manifest | Local Config   #"
echo "# Node 3: component_keyring_file | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_global_manifest keyring_kms 2
create_local_manifest keyring_file 3
create_global_config keyring_kmip 1
create_local_config keyring_kms 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_kms
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 27: Cross Component Testing                         #"
echo "# Node 1: component_keyring_kms | Local Manifest  | Global Config   #"
echo "# Node 2: component_keyring_file  | Global Manifest | Local Config  #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kms 1
create_global_manifest keyring_file 2
create_local_manifest keyring_kmip 3
create_global_config keyring_kms 1
create_local_config keyring_file 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_kms
cleanup keyring_file


echo "#####################################################################"
echo "# Testing Combo 28: Cross Component Testing                         #"
echo "# Node 1: component_keyring_kms  | Local Manifest  | Global Config  #"
echo "# Node 2: component_keyring_kmip | Global Manifest | Local Config   #"
echo "# Node 3: component_keyring_file | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kms 1
create_global_manifest keyring_kmip 2
create_local_manifest keyring_file 3
create_global_config keyring_kms 1
create_local_config keyring_kmip 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_kms
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 29: Cross Component Testing                         #"
echo "# Node 1: component_keyring_file | Local Manifest  | Global Config  #"
echo "# Node 2: component_keyring_kmip  | Global Manifest | Local Config  #"
echo "# Node 3: component_keyring_kms | Local Manifest  | Global Config   #"
echo "#####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_global_manifest keyring_kmip 2
create_local_manifest keyring_kms 3
create_global_config keyring_file 1
create_local_config keyring_kmip 2
create_global_config keyring_kms 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_kms
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 30: Cross Component Testing                         #"
echo "# Node 1: component_keyring_file | Local Manifest  | Global Config  #"
echo "# Node 2: component_keyring_kms  | Global Manifest | Local Config   #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 1
create_global_manifest keyring_kms 2
create_local_manifest keyring_kmip 3
create_global_config keyring_file 1
create_local_config keyring_kms 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_kms
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 31: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "# Node 2: keyring_file                                              #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
FILE_PLUGIN=1
create_conf 2
FILE_PLUGIN=0
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 32: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "# Node 2: keyring_vault                                             #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
start_vault_server
create_workdir
create_conf 1
VAULT_PLUGIN=1
create_conf 2
VAULT_PLUGIN=0
create_conf 3
init_datadir
create_local_manifest keyring_kmip 1
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 1
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "#####################################################################"
echo "# Testing Combo 33: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_kmip | Global Manifest  | Local Config  #"
echo "# Node 2: keyring_file                                              #"
echo "# Node 3: component_keyring_file | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
FILE_PLUGIN=1
create_conf 2
FILE_PLUGIN=0
create_conf 3
init_datadir
create_global_manifest keyring_kmip 1
create_local_manifest keyring_file 3
create_local_config keyring_kmip 1
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 34: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_kms  | Global Manifest | Local Config   #"
echo "# Node 2: keyring_file                                              #"
echo "# Node 3: component_keyring_file | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
FILE_PLUGIN=1
create_conf 2
FILE_PLUGIN=0
create_conf 3
init_datadir
create_global_manifest keyring_kms 1
create_local_manifest keyring_file 3
create_local_config keyring_kms 1
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 35: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_kms | Global Manifest  | Local Config   #"
echo "# Node 2: keyring_vault                                             #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
VAULT_PLUGIN=1
create_conf 2
VAULT_PLUGIN=0
create_conf 3
init_datadir
create_global_manifest keyring_kms 1
create_local_manifest keyring_kmip 3
create_local_config keyring_kms 1
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kms
cleanup keyring_kmip

echo "#####################################################################"
echo "# Testing Combo 36: Component/Plugin Testing                        #"
echo "# Node 1: keyring_file                                              #"
echo "# Node 2: component_keyring_kmip | Local Manifest  | Local Config   #"
echo "# Node 3: component_keyring_file | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
FILE_PLUGIN=1
create_conf 1
FILE_PLUGIN=0
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 2
create_local_manifest keyring_file 3
create_local_config keyring_kmip 2
create_global_config keyring_file 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 37: Component/Plugin Testing                        #"
echo "# Node 1: keyring_file                                              #"
echo "# Node 2: component_keyring_file | Local Manifest  | Local Config   #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
FILE_PLUGIN=1
create_conf 1
FILE_PLUGIN=0
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_file 2
create_local_manifest keyring_kmip 3
create_local_config keyring_file 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file


echo "#####################################################################"
echo "# Testing Combo 38: Component/Plugin Testing                        #"
echo "# Node 1: keyring_file                                              #"
echo "# Node 2: component_keyring_kmip | Local Manifest  | Local Config   #"
echo "# Node 3: keyring_vault                                             #"
echo "#####################################################################"
start_vault_server
create_workdir
FILE_PLUGIN=1
create_conf 1
FILE_PLUGIN=0
create_conf 2
VAULT_PLUGIN=1
create_conf 3
VAULT_PLUGIN=0
init_datadir
create_local_manifest keyring_kmip 2
create_local_config keyring_kmip 2
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip

echo "#####################################################################"
echo "# Testing Combo 39: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_file | Global Manifest | Local Config   #"
echo "# Node 2: keyring_vault                                             #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
start_vault_server
create_workdir
create_conf 1
VAULT_PLUGIN=1
create_conf 2
VAULT_PLUGIN=0
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_local_config keyring_file 1
create_local_manifest keyring_kmip 3
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 40: Component/Plugin Testing                        #"
echo "# Node 1: component_keyring_file | Global Manifest | Local Config   #"
echo "# Node 2: keyring_file                                              #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
create_workdir
create_conf 1
FILE_PLUGIN=1
create_conf 2
FILE_PLUGIN=0
create_conf 3
init_datadir
create_global_manifest keyring_file 1
create_local_manifest keyring_kmip 3
create_local_config keyring_file 1
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file

echo "#####################################################################"
echo "# Testing Combo 41: Component/Plugin Testing                        #"
echo "# Node 1: keyring_vault                                             #"
echo "# Node 2: component_keyring_file | Global Manifest | Local Config   #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
start_vault_server
create_workdir
VAULT_PLUGIN=1
create_conf 1
VAULT_PLUGIN=0
create_conf 2
create_conf 3
init_datadir
create_global_manifest keyring_file 2
create_local_manifest keyring_kmip 3
create_local_config keyring_file 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
cleanup keyring_file


echo "#####################################################################"
echo "# Testing Combo 42: Component/Plugin Testing                        #"
echo "# Node 1: keyring_vault                                             #"
echo "# Node 2: component_keyring_kmip | Local Manifest  | Local Config   #"
echo "# Node 3: component_keyring_kmip | Local Manifest  | Global Config  #"
echo "#####################################################################"
start_vault_server
create_workdir
VAULT_PLUGIN=1
create_conf 1
VAULT_PLUGIN=0
create_conf 2
create_conf 3
init_datadir
create_local_manifest keyring_kmip 2
create_local_manifest keyring_kmip 3
create_local_config keyring_kmip 2
create_global_config keyring_kmip 3
start_node1;MPID1="$!"
start_node2;MPID2="$!"
start_node3;MPID3="$!"
cluster_up_check
sysbench_run

echo "Killing previous running mysqld"
kill_server
remove_workdir
echo "Cleaning up all previous global and local manifest and config files"
cleanup keyring_kmip
