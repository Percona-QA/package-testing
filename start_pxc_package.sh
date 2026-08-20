#!/bin/bash
set -e

# Detect OS family to set Galera provider path
if [[ -d /usr/lib64/galera4 ]]; then
    galera_provider="/usr/lib64/galera4/libgalera_smm.so"
elif [[ -d /usr/lib/galera4 ]]; then
    galera_provider="/usr/lib/galera4/libgalera_smm.so"
else
    echo "❌ Could not detect Galera provider path (/usr/lib*/galera4)."
    exit 1
fi

# Node-specific ports and directories
declare -A nodes=(
  [1]=23100
  [2]=23200
  [3]=23300
)

# Galera listen ports per node
declare -A listen_ports=(
  [1]=23108
  [2]=23208
  [3]=23308
)

cluster_address="gcomm://127.0.0.1:23108,127.0.0.1:23208,127.0.0.1:23308"

# Create mysql group/user if not present
getent group mysql >/dev/null || sudo groupadd mysql
getent passwd mysql >/dev/null || sudo useradd -r -g mysql -s /sbin/nologin mysql

# Step 1: Prepare directories and config files
for i in 1 2 3; do
  datadir="/var/lib/mysql$i"
  cnf="/etc/percona${i}.cnf"
  socket="$datadir/mysql.sock"
  pidfile="$datadir/mysql.pid"
  port="${nodes[$i]}"
  listen_port="${listen_ports[$i]}"
  server_id=$((10 + i))

  echo "🔧 Setting up MySQL node $i..."

  sudo mkdir -p "$datadir"
  sudo chown -R mysql:mysql "$datadir"

  sudo tee "$cnf" > /dev/null <<EOF
[mysqld]
datadir=$datadir
socket=$socket
pid-file=$pidfile
log-error=$datadir/error.log
port=$port
server_id=$server_id

# Galera/PXC settings
wsrep_provider=$galera_provider
wsrep_sst_method=xtrabackup-v2
wsrep_cluster_address=$cluster_address
wsrep_provider_options=gmcast.listen_addr=tcp://127.0.0.1:$listen_port
wsrep_node_address=127.0.0.1
wsrep_node_incoming_address=127.0.0.1

wsrep-debug=1
innodb_file_per_table
innodb_autoinc_lock_mode=2
innodb_flush_log_at_trx_commit=0
core-file
log-output=none
log_error_verbosity=3
pxc_encrypt_cluster_traffic=OFF
gtid_mode=ON
enforce_gtid_consistency=ON
log_slave_updates=ON
log_bin=binlog
binlog_format=ROW
pxc_maint_transition_period=1
EOF
done

# Step 2: Initialize data directories
for i in 1 2 3; do
  echo "🧹 Initializing MySQL node $i..."
  sudo mysqld --defaults-file="/etc/percona${i}.cnf" --initialize-insecure --user=mysql
done

# Step 3: Bootstrap first node
echo "🚀 Bootstrapping Node 1..."
sudo mysqld --defaults-file="/etc/percona1.cnf" --user=mysql --wsrep-new-cluster &
sleep 10

# Step 4: Start node 2 and 3
echo "🔄 Starting Node 2..."
sudo mysqld --defaults-file="/etc/percona2.cnf" --user=mysql &
sleep 5

echo "🔄 Starting Node 3..."
sudo mysqld --defaults-file="/etc/percona3.cnf" --user=mysql &
sleep 10

# Step 5: Verify cluster status
for i in 1 2 3; do
  echo "🔍 Checking cluster size on Node $i..."
  mysql -u root --socket="/var/lib/mysql$i/mysql.sock" -e "SHOW STATUS LIKE 'wsrep_cluster_size';"
done

echo -e "\n✅ 3-node PXC cluster setup complete.\n"

# Print connection info
echo "🔗 You can connect to each MySQL node using the following commands:"
for i in 1 2 3; do
  echo "Node $i: mysql -u root --socket=/var/lib/mysql${i}/mysql.sock"
done
echo
