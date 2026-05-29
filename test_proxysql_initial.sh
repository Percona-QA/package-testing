#!/bin/bash

# Variables
PROXYSQL_HOST="127.0.0.1"
PROXYSQL_PORT="6032"
MYSQL_USER="admin"
MYSQL_PASSWORD="admin"
HOSTGROUP_ID="1"
HOSTNAME="127.0.0.1"
PORT="3306"

# Function to execute a MySQL command
execute_mysql_command() {
    local command="$1"
    mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$PROXYSQL_HOST" -P "$PROXYSQL_PORT" -e "$command"
}

# Log in and insert data
execute_mysql_command "INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES ($HOSTGROUP_ID,'$HOSTNAME',$PORT);"
execute_mysql_command "SAVE MYSQL USERS TO DISK;"

# Check if data is present
data_check=$(execute_mysql_command "SELECT * FROM mysql_servers WHERE hostname='$HOSTNAME' AND port=$PORT;")
if [[ $data_check == *"$HOSTNAME"* && $data_check == *"$PORT"* ]]; then
    echo "Data successfully inserted into mysql_servers."
else
    echo "Failed to insert data into mysql_servers."
    exit 1
fi

# Exit MySQL prompt
# No explicit command needed for this since we are not using an interactive prompt

# Export PROXYSQL_OPTS and restart ProxySQL
export PROXYSQL_OPTS="--initial"
sudo systemctl stop proxysql
sudo systemctl start proxysql

# Wait for ProxySQL to start
sleep 10

# Check if data is still present after restart
data_check_after_restart=$(execute_mysql_command "SELECT * FROM mysql_servers WHERE hostname='$HOSTNAME' AND port=$PORT;")
if [[ $data_check_after_restart == *"$HOSTNAME"* && $data_check_after_restart == *"$PORT"* ]]; then
    echo "Data is still present in mysql_servers after restart. Data was not removed as expected."
    exit 1
else
    echo "Data is not present in mysql_servers after restart. Data was removed as expected."
fi

