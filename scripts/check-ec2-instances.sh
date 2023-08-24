#!/bin/bash
#
## Calculate the threshold date (1 day ago)
awsRegions=("us-west-1" "us-west-2" "us-east-1" "us-east-2" "eu-west-1" "eu-west-2" "eu-west-3" "eu-north-1" "eu-central-1")


checkec2-qa(){
           threshold_date=$(date -d "$2 day ago" +%Y-%m-%d)
           aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" "Name=tag:job-name,Values=*package-testing*,*ps*,*pxc*,*pbm*,*pdmdb*,*orchestrator_docker*" --query "Reservations[].Instances[?LaunchTime<='${threshold_date}'].[Tags[?Key=='Name'].Value[],Tags[?Key=='job-name'].Value[], InstanceId, LaunchTime]" --output yaml --region $1 | sed -e 's/\- \[\]//g' -e '/^$/d'

    }

checkec2-all(){
           threshold_date=$(date -d "$2 day ago" +%Y-%m-%d)
           aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[?LaunchTime<='${threshold_date}'].[Tags[?Key=='Name'].Value[],Tags[?Key=='job-name'].Value[], InstanceId, LaunchTime]" --output yaml --region $1 | sed -e 's/\- \[\]//g' -e '/^$/d'

    }

#
days="2"

for region in "${awsRegions[@]}"
do
#
#
serversall=$(checkec2-all "$region" "$days" | /opt/yq 'length')
serversqa=$(checkec2-qa "$region" "$days" | /opt/yq 'length')


echo "--------------Region $region has $serversall servers running since past $days Days-----------------" >> OUTPUT-ALL.txt
checkec2-all "$region" "$days"  >> OUTPUT-ALL.txt
echo "-------------------------------------------------------------------------------------"  >> OUTPUT-ALL.txt

echo "Region $region has $serversall running servers since past $days days" >> overview-all.txt


echo "--------------Region $region has $serversqa INSTANCES WITH MOLECULE QA TESTS running since past $days days-----------------" >> OUTPUT-QA.txt
checkec2-qa "$region" "$days"  >> OUTPUT-QA.txt
echo "-------------------------------------------------------------------------------------"  >> OUTPUT-QA.txt

echo "Region $region has $serversqa INSTANCES WITH MOLECULE QA TESTS running since past $days days" >> overview-qa.txt


done
