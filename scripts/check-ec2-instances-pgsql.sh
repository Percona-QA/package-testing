#!/bin/bash

awsRegions=("us-west-1" "us-west-2" "us-east-1" "us-east-2" "eu-west-1" "eu-west-2" "eu-west-3" "eu-north-1" "eu-central-1")

checkec2-pgsql-to-terminate(){
           threshold_date=$(date -u -d "$2 hours ago" +%Y-%m-%dT%H:%M:%S)
           aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[?LaunchTime<='"${threshold_date}"' && (Tags[?Key=='iit-billing-tag' && (contains(Value,'jenkins-pg-worker') || contains(Value,'jenkins-pg-molecule-rhel'))])].[Tags[?Key=='Name'].Value[],Tags[?Key=='job-name'].Value[], InstanceId, LaunchTime]" --output yaml --region $1 | sed -e 's/\- \[\]//g' -e '/^$/d'
    }

checkec2-pgsql-to-stop(){
           threshold_date=$(date -u -d "$2 hours ago" +%Y-%m-%dT%H:%M:%S)
           aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[?LaunchTime<='"${threshold_date}"' && (KeyName=='mohit.joshi-keyeu1' || KeyName=='shahid-key' || KeyName=='naeem')].[Tags[?Key=='Name'].Value[],Tags[?Key=='job-name'].Value[], InstanceId, LaunchTime]" --output yaml --region $1 | sed -e 's/\- \[\]//g' -e '/^$/d'
    }

hours_terminate="6"
hours_stop="12"

for region in "${awsRegions[@]}"
do

serversqa_pgsql_to_terminate=$(checkec2-pgsql-to-terminate "$region" "$hours_terminate" | /opt/yq 'length')
serversqa_pgsql_to_stop=$(checkec2-pgsql-to-stop "$region" "$hours_stop" | /opt/yq 'length')

# Instances that needs to be Terminated
echo "--------------Region $region has $serversqa_pgsql_to_terminate INSTANCES WITH MOLECULE QA TESTS running since past $hours_terminate hours-----------------" >> DESTROY-QA-PGSQL.txt
checkec2-pgsql-to-terminate "$region" "$hours_terminate"  >> DESTROY-QA-PGSQL.txt
echo "-------------------------------------------------------------------------------------"  >> DESTROY-QA-PGSQL.txt
echo "Region $region has $serversqa_pgsql_to_terminate INSTANCES WITH PGSQL MOLECULE QA TESTS INSTANCES running since past $hours_terminate hours" >> overview-qa-pgsql-to-terminate.txt

# Instances that need to stopped
echo "--------------Region $region has $serversqa_pgsql_to_stop INSTANCES WITH MOLECULE QA TESTS running since past $hours_terminate hours-----------------" >> STOP-QA-PGSQL.txt
checkec2-pgsql-to-terminate "$region" "$hours_stop"  >> STOP-QA-PGSQL.txt
echo "-------------------------------------------------------------------------------------"  >> STOP-QA-PGSQL.txt
echo "Region $region has $serversqa_pgsql_to_stop INSTANCES WITH PGSQL MOLECULE QA TESTS INSTANCES running since past $hours_terminate hours" >> overview-qa-pgsql-to-stop.txt








done
