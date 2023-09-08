import os

router_version = os.getenv('ROUTER_VERSION')
docker_tag = os.getenv('ROUTER_VERSION')
docker_acc = os.getenv('DOCKER_ACC')

docker_product = 'percona-mysql-router'
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag
ps_pwd = 'inno'

RHEL_DISTS = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]

DEB_DISTS = ["debian", "ubuntu"]

