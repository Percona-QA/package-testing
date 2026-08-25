import os

docker_acc = os.getenv('DOCKER_ACC')
docker_product = 'percona-binlog-server'
pbs_version = os.getenv('PBS_VERSION')
docker_tag = pbs_version
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag

ps_version = os.getenv('PS_VERSION')
ps_docker_image = docker_acc + "/percona-server:" + ps_version

RHEL_DISTS = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]

DEB_DISTS = ["debian", "ubuntu"]

network_name = 'binlog-server-net'
source_container = 'binlog-server-source-ps'
gtid_source_container = 'binlog-server-source-ps-gtid'
pull_source_container = 'binlog-server-source-ps-pull'
inspect_source_container = 'binlog-server-source-ps-inspect'
pull_pbs_container = 'binlog-server-pull-test'

ps_pwd = 'pwd1234#'
repl_user = 'repl_user'
repl_pwd = 'replpwd1234#'

test_pwd = os.path.dirname(os.path.realpath(__file__))
