#!/usr/bin/env bash

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done

if [ -z "${service_name}" ]; then
  export agent_id=$(pmm-admin list | grep node_exporter | awk -F' ' '{print $4}')
else
  export service_id=$(pmm-admin list | grep "${service_name}" | awk -F' ' '{print $NF}')
  if [ -z ${service_id} ]; then
    echo "Failed to find Service ID for '${service_name}' service"
    pmm-admin list
    exit 1;
  fi
  export agent_id=$(pmm-admin list | grep "${service_id}" | grep "${agent_type}" | awk -F' ' '{print $4}')
fi

if [ -z "$agent_password" ]; then
  export agent_password=${agent_id}
fi
if [ -z "$pmm_client_ip" ]; then
  export pmm_client_ip=127.0.0.1
fi

export api_auth=$(printf '%s' admin:$ADMIN_PASSWORD | base64)
export token=$(printf '%s' pmm:${agent_password} | base64)
#export listen_port=$(curl -s "https://${pmm_server_ip}/v1/inventory/Agents/List" -H "Authorization: Basic ${api_auth}" --data '{"promise":{}}' --compressed --insecure | jq ".${agent_type}[] | select(.agent_id == "\"${agent_id}"\") | .listen_port")
export listen_port=$(pmm-admin list | grep "${agent_id}" | awk -F' ' '{print $NF}')
if [ -z ${listen_port} ]; then
  echo "Failed to find port for '${service_name}' service"
  pmm-admin list
  exit 1;
fi
if curl -s "http://${pmm_client_ip}:${listen_port}/metrics" | grep -q "${metric_name} ${metric_value}"; then
  echo "Authentication for exporter Broken, metrics fetched without basic auth"
  exit 1;
fi
curl -s -H "Authorization: Basic ${token}" "http://${pmm_client_ip}:${listen_port}/metrics" | grep "${metric_name} ${metric_value}"
