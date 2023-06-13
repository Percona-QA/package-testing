#!/bin/bash
#
## Calculate the threshold date (1 day ago)
awsRegions=("us-west-1" "us-west-2" "us-east-1" "us-east-2" "eu-west-1" "eu-west-2" "eu-east-1" "us-east-2")


checkec2(){
          threshold_date=$(date -d "$2 day ago" +%Y-%m-%d)

            aws ec2 describe-instances     --filters "Name=instance-state-name,Values=running"     --query "Reservations[].Instances[?LaunchTime<='${threshold_date}'].[Tags[?Key=='Name'].Value[], InstanceId, LaunchTime]" --output yaml --region $1 | sed -e 's/\- \[\]//g' -e '/^$/d'
    }



#
days="2"

for region in "${awsRegions[@]}"
do
#
#
servers=$(checkec2 "$region" "$days" | /opt/yq 'length')

echo "----------------$region has $servers running since past $days Days-----------------" >> OUTPUT.txt
checkec2 "$region" "$days"  >> OUTPUT.txt
echo "-------------------------------------------------------------------------------------"  >> OUTPUT.txt


echo "Region $region has $servers running servers since past $days days" >> overview.txt


done
