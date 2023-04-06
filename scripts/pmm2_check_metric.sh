#!/usr/bin/env bash

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done

export service_id=$(pmm-admin list | grep ${service_name} | awk -F' ' '{print $4}')
if [ -z "${service_name}" ]; then
        export agent_id=$(pmm-admin list | grep node_exporter | awk -F' ' '{print $4}')
else
        export agent_id=$(pmm-admin list | grep ${service_id} | grep ${agent_type} | awk -F' ' '{print $4}')
fi

if [ -z "$agent_password" ]; then
        export agent_password=${agent_id}
fi
if [ -z "$pmm_client_ip" ]; then
        export pmm_client_ip=127.0.0.1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
        export api_auth=$(printf '%s' admin:admin | base64)
else
        export api_auth=$(printf '%s' admin:$ADMIN_PASSWORD} | base64)
fi


export token=$(printf '%s' pmm:${agent_password} | base64)
export listen_port=$(curl -s "https://${pmm_server_ip}/v1/inventory/Agents/List" -H "Authorization: Basic ${api_auth}" --data '{"promise":{}}' --compressed --insecure | jq ".${agent_type}[] | select(.agent_id == "\"${agent_id}"\") | .listen_port")
if [ -z ${listen_port} ]; then
        echo "Failed to find port for '${service_name}' service"
        exit 1;
fi
if curl -s "http://${pmm_client_ip}:${listen_port}/metrics" | grep -q "${metric_name} ${metric_value}"; then
        echo "Authentication for exporter Broken, metrics fetched without basic auth"
        exit 1;
fi
curl -s -H "Authorization: Basic ${token}" "http://${pmm_client_ip}:${listen_port}/metrics" | grep "${metric_name} ${metric_value}"
