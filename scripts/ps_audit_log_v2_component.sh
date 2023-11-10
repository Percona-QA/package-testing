#!/bin/bash
set -e

#install the Audit log filter component
ALv2_component=$(mysql -uroot -NBe "source /usr/share/mysql/audit_log_filter_linux_install.sql;");

# make sure AUDIT component is in place
AUDIT_COMPONENT=$(mysql -NBe "select * from mysql.component;" | grep -c component_audit_log_filter)

if [ ${AUDIT_COMPONENT} == 1 ]; then
   echo "AUDIT component is installed"
else
   echo "ERROR: AUDIT component isn't installed"
   exit 1
fi

# Create dictionary of variables and their default values.
declare -A variables=( ["audit_log_filter.buffer_size"]="1048576" ["audit_log_filter.database"]="mysql" \
                ["audit_log_filter.disable"]="0" ["audit_log_filter.file"]="audit_filter.log"\
                ["audit_log_filter.format"]="NEW" ["audit_log_filter.format_unix_timestamp"]="0" \
                ["audit_log_filter.handler"]="FILE" ["audit_log_filter.key_derivation_iterations_count_mean"]="600000" \
                ["audit_log_filter.max_size"]="1073741824" ["audit_log_filter.password_history_keep_days"]="0" \
                ["audit_log_filter.prune_seconds"]="0" ["audit_log_filter.read_buffer_size"]="32768" ["audit_log_filter.rotate_on_size"]="1073741824" \
                ["audit_log_filter.strategy"]="ASYNCHRONOUS" ["audit_log_filter.syslog_facility"]="LOG_USER" ["audit_log_filter.syslog_priority"]="LOG_INFO" \
                ["audit_log_filter.syslog_tag"]="audit-filter")

# Create dictionary of audit log v2 plugin functions
functions_list=("audit_log_rotate" "audit_log_encryption_password_set" \
    "audit_log_encryption_password_get" "audit_log_filter_remove_user" \
    "audit_log_read_bookmark" "audit_log_filter_set_user" \
    "audit_log_filter_set_filter" "audit_log_filter_remove_filter" \
    "audit_log_filter_flush" "audit_log_read")

# Check that all variables are present and have correct default values
for al_variable in ${!variables[@]}; do
    result=$(mysql -uroot -NBe "SELECT @@${al_variable}")
    if [[ "${result}" != ${variables[${al_variable}]} ]]; then
        echo "${al_variable} result is incorrect. Current result is: ${result}. Expected result is:  ${variables[${al_variable}]}}"
        fails='1'
    fi
done

# Check that all UDFs are present
for al_function in ${functions_list[@]}; do
    result=$(mysql -uroot -NBe "SELECT * FROM performance_schema.user_defined_functions WHERE udf_name=\"${al_function}\";")
    if [[ -z ${result} ]]; then
        fails='1'
        echo "${al_function} has empty result."
    fi
done

# Functional tests

# get logfile location
data_dir=$(mysql -uroot -NBe "SELECT @@datadir";)
al_file_name=$(mysql -uroot -NBe "SELECT @@audit_log_filter.file;")
al_file_pattern=$(echo ${al_file_name}|awk -F'.' '{print $1}')
al_file_location=${data_dir}${al_file_name}

# Enable audit_log_v2 for all users and check that log file grows.
al_file_rows=$(wc -l ${al_file_location}|awk '{print $1}')
mysql -uroot -NBe "SELECT audit_log_filter_set_filter('log_all', '{ \"filter\": { \"log\": true } }');"
mysql -uroot -NBe "SELECT audit_log_filter_set_user('%', 'log_all');"
mysql -uroot -NBe "SELECT 1;"
sleep 1
al_file_rows_after=$(wc -l ${al_file_location}|awk '{print $1}')
if [[ ${al_file_rows} -ge ${al_file_rows_after} ]]; then
    echo "Enabled plugin. Smth wrong with audit log file growth! Rows num before SQL=${al_file_rows}. Rows num after SQL=${al_file_rows_after}!"
    exit 1
else
    echo "Enabled plugin OK. Rows num before SQL=${al_file_rows}. Rows num after SQL=${al_file_rows_after}"
fi

# Check dynamic variables

# audit_log_filter_disable
mysql -uroot -NBe "set global audit_log_filter.disable='ON';"
sleep 1
al_file_rows=$(wc -l ${al_file_location}|awk '{print $1}')
mysql -uroot -NBe "SELECT 1;"
sleep 1
al_file_rows_after=$(wc -l ${al_file_location}|awk '{print $1}')
if [[ ${al_file_rows_after} -gt ${al_file_rows} ]]; then
    echo "audit_log_filter_disable. Smth wrong with audit log file growth! Rows num before SQL=${al_file_rows}. Rows num after SQL=${al_file_rows_after}!"
    exit 1
else
    echo "audit_log_filter_disable OK. Rows num before SQL=${al_file_rows}. Rows num after SQL=${al_file_rows_after}"
fi
# revert setting and enable audit log
mysql -uroot -NBe "set global audit_log_filter.disable='OFF';"


# audit_log_filter_rotate_on_size. 
mysql -uroot -NBe "set global audit_log_filter.rotate_on_size=4096;"
sleep 1
cur_value=$(mysql -uroot -NBe "select @@audit_log_filter.rotate_on_size")
if [[ ${cur_value} != 4096 ]]; then
    echo "audit_log_filter.rotate_on_size value is incorrect!"
    exit 1
fi
files_num_before=$(ls -lht ${data_dir}|grep ${al_file_pattern}|wc -l)
#run some sqls
for i in {1..100}; do mysql -uroot -NBe "select '1'; select '2'; select '3';" > /dev/null; done
sleep 1
for i in {1..100}; do mysql -uroot -NBe "select '1'; select '2'; select '3';" > /dev/null; done
sleep 1
files_num_after=$(ls -lht ${data_dir}|grep ${al_file_pattern}|wc -l)
if [[ ${files_num_before} -ge ${files_num_after} ]]; then
    echo "audit_log_filter_rotate_on_size. Smth wrong with audit log rotation! Number of log files before: ${files_num_before}; after: ${files_num_after}."
    exit 1
else
    echo "audit_log_filter_rotate_on_size OK. Number of log files before SQL=${files_num_before}. Number of log files after SQL=${files_num_after}"
fi

# audit_log_filter_max_size. When log files size => audit_log_filter_max_size, the extra files are pruned. Prunning is triggered during files rotation.
# audit_log_filter_prune_seconds should be 0
mysql -uroot -NBe "set global audit_log_filter.max_size=8192;"
prune_sec_value=$(mysql -uroot -NBe "select @@audit_log_filter.prune_seconds")
if [[ ${prune_sec_value} != 0 ]]; then
    echo "audit_log_filter_prune_seconds value is incorrect!"
    exit 1
fi
sleep 1
for i in {1..200}; do mysql -uroot -NBe "select '1'; select '2'; select '3';" > /dev/null; done
sleep 1
files_num_after=$(ls -lht ${data_dir}|grep ${al_file_pattern}|wc -l)
if [[ ${files_num_after} -gt 2 ]]; then
    echo "audit_log_filter_max_size. Smth wrong with audit log pruning! Number of log files after pruning is ${files_num_after}."
    exit 1
else
    echo "audit_log_filter_max_size OK. Number of log files after SQL=${files_num_after}"
fi
mysql -uroot -NBe "set global audit_log_filter.max_size=default;"

# audit_log_filter_prune_seconds. When log files creation => audit_log_filter_prune_seconds, the extra files are pruned. Prunning is triggered during files rotation.
# audit_log_filter_max_size should be 0
mysql -uroot -NBe "set global audit_log_filter.prune_seconds=10;"
max_size_value=$(mysql -uroot -NBe "select @@audit_log_filter.max_size;")
if [[ ${max_size_value} != 0 ]]; then
    echo "audit_log_filter_max_size value is incorrect!"
    exit 1
fi
sleep 1
for i in {1..1000}; do mysql -uroot -NBe "select '1';" > /dev/null; done
files_num_before=$(ls -lht ${data_dir}|grep ${al_file_pattern}|wc -l)
sleep 11
mysql -uroot -NBe "select audit_log_rotate();"
files_num_after=$(ls -lht ${data_dir}|grep ${al_file_pattern}|wc -l)
if [[ ${files_num_after} -ge ${files_num_before} ]]; then
    echo "audit_log_filter_prune_seconds. Smth wrong with audit log pruning! Number of log files befor = ${files_num_before}; after pruning = ${files_num_after}."
    exit 1
else
    echo "audit_log_filter_prune_seconds OK. Number of log files before = ${files_num_before}; after pruning = ${files_num_after}."
fi
mysql -uroot -NBe "set global audit_log_filter.max_size=1073741824;"

# check UDFs for default format
mysql -uroot -NBe "select audit_log_filter_flush();"
mysql -uroot -NBe "select audit_log_filter_remove_user('%');"
mysql -uroot -NBe "select audit_log_filter_remove_filter('log_all');"

#remove tables
mysql -uroot -NBe "DROP TABLE IF EXISTS mysql.audit_log_user;DROP TABLE IF EXISTS mysql.audit_log_filter;"

#Exit script with an error if any of the checks failed.
if [[ "${fails}" == '1' ]]; then
    echo "Exiting because there were failed defaults/UDFs!"
    exit 1
fi
