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


"
+ declare service_name=pgsql_10.166.2.147\n
+ declare 'metric_name=pg_up{collector=\"exporter\"}'\n
+ declare pmm_server_ip=18.225.6.235\n
+ declare agent_type=postgres_exporter\n
+ declare metric_value=1\n

++ pmm-admin list\n
++ grep pgsql_10.166.2.147\n
++ awk '-F ' '{print $4}'\n
+ export service_id=\n
+ service_id=\n
+ '[' -z pgsql_10.166.2.147 ']'\n
++ pmm-admin list\n
++ grep postgres_exporter\n
++ grep\n
Usage: grep [OPTION]... PATTERN [FILE]...\n
++ awk '-F ' '{print $4}'\n
Try 'grep --help' for more information.\n
+ export agent_id=\n
+ agent_id=\n+ '[' -z '' ']'\n
+ export agent_password=\n
+ agent_password=\n
+ '[' -z '' ']'\n
+ export pmm_client_ip=127.0.0.1\n
+ pmm_client_ip=127.0.0.1\n
++ printf %s 'admin:pmm2023fortesting!'\n
++ base64\n
+ export api_auth=YWRtaW46cG1tMjAyM2ZvcnRlc3Rpbmch\n
+ api_auth=YWRtaW46cG1tMjAyM2ZvcnRlc3Rpbmch\n
++ printf %s pmm:\n
++ base64\n
+ export token=cG1tOg==\n+ token=cG1tOg==\n
++ pmm-admin list\n
++ grep\n
++ awk '-F ' '{print $NF}'\n
Usage: grep [OPTION]... PATTERN [FILE]...\n
Try 'grep --help' for more information.\n
+ export listen_port=\n
+ listen_port=\n
+ '[' -z ']'\n
+ echo 'Failed to find port for '\\''pgsql_10.166.2.147'\\'' service'\n
+ pmm-admin list\n
+ exit 1"

"+ echo 'Failed to find port for '\\''pgsql_10.166.2.147'\\'' service'", "+ pmm-admin list", "+ exit 1"],
"Failed to find port for 'pgsql_10.166.2.147' service\n
Service type        Service name                     Address and port                   Service ID
MySQL               mysql_10.166.2.147               /var/run/mysqld/mysqld.sock        /service_id/e3be0f37-50d9-4698-875d-65273c8bb0d1
MongoDB             mongodb_10.166.2.147             127.0.0.1:27017                    /service_id/ae259b30-6430-444e-b8e9-9c417b90cfca
PostgreSQL          pgsql_10.166.2.147               127.0.0.1:5432                     /service_id/6c27c655-6c22-4752-912e-18d709e5d49f
PostgreSQL          pgsql_socket_10.166.2.147        /var/run/postgresql/               /service_id/c439108c-02cf-4fff-b9b7-1b384e7c2d9b
\n
Agent type                       Status      Metrics Mode  Agent ID                                          Service ID                                              Port
pmm_agent                        Connected                 /agent_id/2e610103-f725-4f40-815e-ed3434fb0623                                                            0
node_exporter                    Running     push          /agent_id/b5efc225-aab5-46c1-bcf8-4ef1a5c427b0                                                            42001
mysqld_exporter                  Running     push          /agent_id/4df5e793-4d28-43c2-922a-b56b3f7003e3    /service_id/e3be0f37-50d9-4698-875d-65273c8bb0d1        42002
mongodb_exporter                 Running     push          /agent_id/dd47b67c-2e04-4760-a143-924d555e9ab6    /service_id/ae259b30-6430-444e-b8e9-9c417b90cfca        42003
postgres_exporter                Running     push          /agent_id/3a767517-09b7-424b-a93b-9c965c153200    /service_id/c439108c-02cf-4fff-b9b7-1b384e7c2d9b        42005
postgres_exporter                Running     push          /agent_id/b941360a-19e1-4007-9a0a-42b8e9386b1f    /service_id/6c27c655-6c22-4752-912e-18d709e5d49f        42006
mysql_perfschema_agent           Running                   /agent_id/f5af0bd9-9c36-4a58-a488-49fd484e7e49    /service_id/e3be0f37-50d9-4698-875d-65273c8bb0d1        0
mongodb_profiler_agent           Running                   /agent_id/3290f791-af18-47b1-89c9-102b9608a453    /service_id/ae259b30-6430-444e-b8e9-9c417b90cfca        0
postgresql_pgstatements_agent    Running                   /agent_id/ab5aeabb-caa1-4e26-9498-d4430d8df729    /service_id/c439108c-02cf-4fff-b9b7-1b384e7c2d9b        0
postgresql_pgstatements_agent    Running                   /agent_id/b60d4721-91a3-4f1a-bccb-8c86c6db23b3    /service_id/6c27c655-6c22-4752-912e-18d709e5d49f        0
vmagent                          Running     push          /agent_id/4259da0d-acc5-42d6-ac1c-8c0f5ab2d6d7                                                            42000"

