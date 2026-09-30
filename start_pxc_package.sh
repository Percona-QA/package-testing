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

# Start mysqld detached in its own session. Backgrounding sudo itself leaves
# it running with use_pty, holding the terminal in raw mode (staircase output);
# setsid -f lets sudo exit right away and restore the terminal.
start_node() {
  local i=$1; shift
  sudo setsid -f mysqld --defaults-file="/etc/percona${i}.cnf" --user=mysql "$@" \
    </dev/null >/dev/null 2>&1
}

node_running() {
  pgrep -f -- "mysqld --defaults-file=/etc/percona$1.cnf " >/dev/null
}

# Wait until a node reports Synced (a joiner only opens its socket after SST)
wait_for_synced() {
  local i=$1 timeout=${2:-300} elapsed=0 state=""
  local socket="/var/lib/mysql$i/mysql.sock"

  while (( elapsed < timeout )); do
    if ! node_running "$i"; then
      echo "❌ Node $i mysqld exited. Check /var/lib/mysql$i/error.log"
      exit 1
    fi
    state=$(mysql -u root --socket="$socket" -N -s \
      -e "SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME='wsrep_local_state_comment'" \
      2>/dev/null || true)
    if [[ "$state" == "Synced" ]]; then
      echo "✅ Node $i is Synced (${elapsed}s)"
      return 0
    fi
    sleep 2
    (( elapsed += 2 ))
  done

  echo "❌ Node $i not Synced after ${timeout}s (state: ${state:-no connection}). Check /var/lib/mysql$i/error.log"
  exit 1
}

# Step 3: Bootstrap first node
echo "🚀 Bootstrapping Node 1..."
start_node 1 --wsrep-new-cluster
wait_for_synced 1

# Step 4: Start node 2 and 3
echo "🔄 Starting Node 2..."
start_node 2
wait_for_synced 2

echo "🔄 Starting Node 3..."
start_node 3
wait_for_synced 3

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
