#!/usr/bin/env python3
import os

pxb_docker_acc = os.getenv('PXB_DOCKER_ACC')
pxb_version = os.getenv('PXB_VERSION')
pxb_revision = os.getenv('PXB_REVISION')

if not pxb_version:
    raise RuntimeError("PXB_VERSION env var is not set (e.g. '8.0.35-35')")
if not pxb_docker_acc:
    raise RuntimeError("PXB_DOCKER_ACC env var is not set (e.g. 'percona')")

docker_product = 'percona-xtrabackup'
docker_image = pxb_docker_acc + "/" + docker_product + ":" + pxb_version

pxb_binaries = ('xtrabackup', 'xbcloud', 'xbcrypt', 'xbstream')
