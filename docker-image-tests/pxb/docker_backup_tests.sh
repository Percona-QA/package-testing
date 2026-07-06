#!/bin/bash

###################################################################################################
# Created By Manish Chawla, Percona LLC                                                           #
# Modified By Mohit Joshi, Percona LLC                                                            #
# Updated for Jenkins Docker Worker                                                               #
# This script runs PXB against Percona Server and MySQL server in a docker container              #
###################################################################################################

help() {
    echo "Usage: $0 repo_name server ps_tag pxb_tag"
    echo "Accepted values of repo_name: pxb-24, pxb-80, pxb-8x-innovation, pxb-84-lts, pxb-9x-innovation"
    echo "Accepted value of server: ps, ms"
    echo "ps_tag and pxb_tag must be full Docker Hub tags, e.g. 9.6.0-1"
    echo "Image accounts are picked from \$PS_DOCKER_ACC and \$PXB_DOCKER_ACC env vars (default: percona)."
    exit 1
}

if [ "$#" -ne 4 ]; then
    help
fi

repo_name=$1
server=$2
ps_tag=$3
pxb_tag=$4

# Jenkins worker environment variables
WORKSPACE=${WORKSPACE:-$(pwd)}
DOCKER_CMD=${DOCKER_CMD:-"docker"}  # Allow override for different Docker setups

# Use workspace-relative paths for Jenkins
MYSQL_DATA_DIR="${WORKSPACE}/mysql_data"
BACKUP_LOG="${WORKSPACE}/backup_log"

# Function to check if running as root (Jenkins workers often are)
check_permissions() {
    if [ "$EUID" -eq 0 ]; then
        SUDO_CMD=""
    else
        SUDO_CMD="sudo"
    fi
}

clean_setup() {
    echo "Cleaning up previous setup..."
    
    # Stop and remove container if exists
    if $DOCKER_CMD ps -a --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        echo "Stopping and removing existing container: $container_name"
        $SUDO_CMD $DOCKER_CMD stop $container_name >/dev/null 2>&1 || true
        $SUDO_CMD $DOCKER_CMD rm $container_name >/dev/null 2>&1 || true
    fi
    
    # Clean up data directory
    if [ -d "$MYSQL_DATA_DIR" ]; then
        echo "Removing MySQL data directory: $MYSQL_DATA_DIR"
        $SUDO_CMD rm -rf "$MYSQL_DATA_DIR"
    fi
    
    # Clean up backup volumes
    echo "Removing unused Docker volumes..."
    $SUDO_CMD $DOCKER_CMD volume prune -f >/dev/null 2>&1 || true
}

setup_mysql_data_dir() {
    echo "Setting up MySQL data directory..."
    mkdir -p "$MYSQL_DATA_DIR"
    
    # Set permissions - Jenkins workers might run as root
    if [ "$EUID" -eq 0 ]; then
        chmod -R 777 "$MYSQL_DATA_DIR"
    else
        $SUDO_CMD chmod -R 777 "$MYSQL_DATA_DIR"
    fi
}

# Docker image and configuration logic (same as original)
if [ "$repo_name" = "pxb-9x-innovation" ] || [ "$repo_name" = "pxb-8x-innovation" ]; then
    if [ "$server" = "ms" ]; then
        container_name="mysql-$ps_tag"
        mysql_docker_image="mysql:$ps_tag"
    elif [ "$server" = "ps" ]; then
        container_name="percona-server-$ps_tag"
        mysql_docker_image="${PS_DOCKER_ACC:-percona}/percona-server:$ps_tag"
    else
        echo "Invalid product!"
        help
    fi

    pxb_docker_image="${PXB_DOCKER_ACC:-percona}/percona-xtrabackup:$pxb_tag"

    pxb_backup_dir="pxb_backup_data:/backup_$pxb_tag"
    target_backup_dir="/backup_$pxb_tag"
    mount_dir="-v $MYSQL_DATA_DIR:/var/lib/mysql"

elif [ "$repo_name" = "pxb-80" ] || [ "$repo_name" = "pxb-24" ] || [ "$repo_name" = "pxb-84-lts" ]; then
    if [ "$server" = "ms" ]; then
        container_name="mysql-$ps_tag"
        mysql_docker_image="mysql:$ps_tag"
    elif [ "$server" = "ps" ]; then
        container_name="percona-server-$ps_tag"
        mysql_docker_image="${PS_DOCKER_ACC:-percona}/percona-server:$ps_tag"
    else
        echo "Invalid product!"
        help
    fi

    pxb_docker_image="${PXB_DOCKER_ACC:-percona}/percona-xtrabackup:$pxb_tag"

    pxb_backup_dir="pxb_backup_data:/backup_$pxb_tag"
    target_backup_dir="/backup_$pxb_tag"
    mount_dir="-v $MYSQL_DATA_DIR:/var/lib/mysql"

else
    echo "Invalid version parameter. Exiting"
    help
fi

test_pxb_docker() {
    echo "=== Starting PXB Docker Test ==="
    echo "Container: $container_name"
    echo "MySQL Image: $mysql_docker_image"
    echo "PXB Image: $pxb_docker_image"
    echo "Data Directory: $MYSQL_DATA_DIR"
    
    # Setup data directory
    setup_mysql_data_dir
    
    # Start MySQL container
    start_mysql_container="$SUDO_CMD $DOCKER_CMD run --name $container_name $mount_dir -p 3306:3306 -e PERCONA_TELEMETRY_DISABLE=1 -e MYSQL_ROOT_HOST=% -e MYSQL_ROOT_PASSWORD=mysql -d $mysql_docker_image"
    
    echo "Starting MySQL container: $start_mysql_container"
    
    if ! $start_mysql_container 2>&1 | tee -a "$BACKUP_LOG"; then
        echo "ERR: Failed to start MySQL container $container_name"
        echo "--- Last lines of backup_log ---"
        tail -n 30 "$BACKUP_LOG" || true
        return 1
    fi
    
    echo "Waiting for MySQL to start..."
    for ((i=1; i<=180; i++)); do
        if ! $DOCKER_CMD ps --format "table {{.Names}} {{.Status}}" | grep "$container_name" | grep -q "Up"; then
            sleep 1
        else
            echo "MySQL container is running"
            break
        fi
        if [[ $i -eq 180 ]]; then
            echo "ERR: MySQL server failed to start in container"
            return 1
        fi
    done
    
    # Wait for MySQL to fully initialize
    sleep 20
    
    # Check MySQL version
    echo -n "MySQL started with version: "
    $SUDO_CMD $DOCKER_CMD exec $container_name mysql -uroot -pmysql -Bse "SELECT @@version;" 2>&1 | grep -v "Using a password" || echo "Unknown (mysql query failed — see container logs)"
    echo "--- $container_name docker logs (tail) ---"
    $SUDO_CMD $DOCKER_CMD logs --tail 30 $container_name 2>&1 || true
    echo "--- end logs ---"
    
    # Create test data
    echo "Creating test database and data..."
    $SUDO_CMD $DOCKER_CMD exec $container_name mysql -uroot -pmysql -e "CREATE DATABASE IF NOT EXISTS test;" >/dev/null 2>&1
    $SUDO_CMD $DOCKER_CMD exec $container_name mysql -uroot -pmysql -e "CREATE TABLE test.t1(i INT);" >/dev/null 2>&1
    $SUDO_CMD $DOCKER_CMD exec $container_name mysql -uroot -pmysql -e "INSERT INTO test.t1 VALUES (1), (2), (3), (4), (5);" >/dev/null 2>&1
    
    # Run PXB backup (FIXED: removed -it flags)
    echo "Running PXB backup..."
    if ! $SUDO_CMD $DOCKER_CMD run --volumes-from $container_name -v $pxb_backup_dir --rm --user root $pxb_docker_image /bin/bash -c "rm -rf $target_backup_dir/* ; xtrabackup --backup --datadir=/var/lib/mysql/ --target-dir=$target_backup_dir --user=root --password=mysql ; xtrabackup --prepare --target-dir=$target_backup_dir" 2>&1 | tee -a "$BACKUP_LOG"; then
        echo "ERR: PXB backup failed"
        echo "--- Last lines of backup_log ---"
        tail -n 50 "$BACKUP_LOG" || true
        return 1
    fi
    
    echo "Backup and prepare completed successfully"
    
    # Stop MySQL container
    echo "Stopping MySQL container..."
    $SUDO_CMD $DOCKER_CMD stop $container_name >>"$BACKUP_LOG" 2>&1
    
    # Clean and recreate data directory for restore
    $SUDO_CMD rm -rf "$MYSQL_DATA_DIR"
    mkdir -p "$MYSQL_DATA_DIR"
    if [ "$EUID" -eq 0 ]; then
        chmod -R 777 "$MYSQL_DATA_DIR"
    else
        $SUDO_CMD chmod -R 777 "$MYSQL_DATA_DIR"
    fi
    
    # Restore backup (FIXED: removed -it flags)
    echo "Restoring backup..."
    if ! $SUDO_CMD $DOCKER_CMD run --volumes-from $container_name -v $pxb_backup_dir --rm --user root $pxb_docker_image /bin/bash -c "xtrabackup --copy-back --datadir=/var/lib/mysql/ --target-dir=$target_backup_dir" 2>&1 | tee -a "$BACKUP_LOG"; then
        echo "ERR: Backup restore failed"
        echo "--- Last lines of backup_log ---"
        tail -n 50 "$BACKUP_LOG" || true
        return 1
    fi
    
    echo "Backup restore completed"
    
    # Set proper permissions
    if [ "$EUID" -eq 0 ]; then
        chmod -R 777 "$MYSQL_DATA_DIR"
    else
        $SUDO_CMD chmod -R 777 "$MYSQL_DATA_DIR"
    fi
    
    # Restart MySQL container with restored data
    echo "Restarting MySQL container with restored data..."
    if ! $SUDO_CMD $DOCKER_CMD start $container_name >>"$BACKUP_LOG" 2>&1; then
        echo "ERR: Failed to restart MySQL container"
        return 1
    fi
    
    # Wait for MySQL to start again
    echo "Waiting for MySQL to restart..."
    for ((i=1; i<=180; i++)); do
        if ! $DOCKER_CMD ps --format "table {{.Names}}" | grep -q "$container_name"; then
            sleep 1
        else
            break
        fi
        if [[ $i -eq 180 ]]; then
            echo "ERR: MySQL failed to restart with restored data"
            return 1
        fi
    done
    
    sleep 20
    
    # Verify data
    echo "Verifying restored data..."
    data_count=$($SUDO_CMD $DOCKER_CMD exec $container_name mysql -uroot -pmysql -Bse 'SELECT COUNT(*) FROM test.t1;' 2>/dev/null | grep -v password | tr -d '\r' || echo "0")
    
    if [ "$data_count" != "5" ]; then
        echo "ERR: Data verification failed. Expected 5 rows, got $data_count"
        return 1
    else
        echo "✅ Data restored successfully - found $data_count rows"
    fi
    
    return 0
}

# Main execution
check_permissions

echo "Starting PXB Docker Test in Jenkins environment"
echo "Workspace: $WORKSPACE"
echo "Docker command: $DOCKER_CMD"
echo "Using sudo: ${SUDO_CMD:-"No"}"

# Clean up any existing setup
if [ -f "$BACKUP_LOG" ]; then
    rm -f "$BACKUP_LOG"
fi

clean_setup

# Run the test (pipefail so tee doesn't mask test_pxb_docker's exit code)
set -o pipefail
if test_pxb_docker 2>&1 | tee -a "$BACKUP_LOG"; then
    echo "✅ PXB Docker test completed successfully"
    TEST_RESULT=0
else
    echo "❌ PXB Docker test failed"
    TEST_RESULT=1
fi
set +o pipefail

# Final cleanup
clean_setup

echo "=========================================="
echo "Test logs available at: $BACKUP_LOG"
echo "=========================================="

exit $TEST_RESULT