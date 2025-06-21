#!/usr/bin/env python3
import os
import re

docker_acc = os.getenv('DOCKER_ACC')
proxysql_version = os.getenv('PROXYSQL_VERSION')
docker_product = os.getenv('DOCKER_PRODUCT')

proxysql_version_upstream = proxysql_version.split('-')[0]
proxysql_version_major = proxysql_version_upstream.split('.')[0] + '.' + proxysql_version_upstream.split('.')[1]
proxysql_version_check = proxysql_version.split('-')[0] + '-' + 'percona' + '-' + proxysql_version.split('-')[1]

docker_tag = proxysql_version
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag
docker_image_latest = docker_acc + "/" + docker_product + ":" + "latest"
docker_image_upstream = docker_acc + "/" + docker_product + ":" + proxysql_version_upstream
docker_image_major = docker_acc + "/" + docker_product + ":" + proxysql_version_major

