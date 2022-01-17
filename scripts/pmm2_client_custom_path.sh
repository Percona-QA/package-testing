#!/bin/bash

VERSION=${PMM_VERSION:-2.26.0}
wget https://downloads.percona.com/downloads/TESTING/pmm/pmm2-client-${VERSION}.tar.gz
tar -xvf pmm2-client-${VERSION}.tar.gz
pushd /
mkdir pmm2-client-custom-path
pushd pmm2-client-custom-path
export PMM_DIR=$(pwd)
popd
popd
mv pmm2-client-${VERSION} pmm2-client
cd pmm2-client
./install_tarball
