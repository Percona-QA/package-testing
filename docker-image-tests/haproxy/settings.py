import os

haproxy_version = os.getenv('HAPROXY_VERSION')
docker_tag = os.getenv('HAPROXY_VERSION')
docker_acc = os.getenv('DOCKER_ACC')

docker_product = 'haproxy'
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag


RHEL_DISTS = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]

DEB_DISTS = ["debian", "ubuntu"]
