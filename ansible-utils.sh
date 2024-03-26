#!/bin/bash

# Functionality of script1.sh
function task2playbook() {
# Define the path to the task book
task_book="$1"

# Define the path to the playbook
playbook="$2"

# Define the changes to be added to the beginning of the playbook
changes=$(cat <<EOF
- name: Playbook initialization
  hosts: localhost
  gather_facts: true
  tasks:
EOF
)

# Append changes to the beginning of the task book
awk -v changes="$changes" 'NR==2 {print changes} {print}' "$task_book" > temp && mv temp "$task_book"

# Rename the task book to a playbook
mv "$task_book" "$playbook"
}

# Functionality of script2.sh
function taskcomment() {

playbook_file=$1
task_name="include tasks for test env setup"
task_name="$2"

check=0
start_line=$(grep -n "$task_name" $playbook_file | cut -d: -f1)
echo "$start_line is the start line"
echo "Checking each lines for - name:"

lines=$(wc -l $playbook_file | awk '{print $1}')

end_line=$start_line+$lines

awk -v line="$start_line" 'NR==line {$0="#"$0} {print}' "$playbook_file" > temp && mv temp "$playbook_file"

start_line=$start_line+1


for ((i=start_line; i<end_line; i++)); do
    if awk -v line="$i" 'NR==line {print}' $playbook_file | grep -q "\- name:"; then
        echo "Line $i contains '- name:'"
        break
    else
        echo "Line $i does not contain '- name:'"
        awk -v line="$i" 'NR==line {$0="#"$0} {print}' "$playbook_file" > temp && mv temp "$playbook_file"
    fi
done

}

# Check the command-line argument
if [[ "$1" == "task2playbook" ]]; then
    # Execute task2playbook function with parameters passed after task2playbook argument
    shift
    task2playbook "$@"
elif [[ "$1" == "taskcomment" ]]; then
    # Execute task2playbook function with parameters passed after task2playbook argument
    shift
    taskcomment "$@"
else
    echo "Usage: $0 {task2playbook|taskcomment} [parameters]"
    exit 1
fi
