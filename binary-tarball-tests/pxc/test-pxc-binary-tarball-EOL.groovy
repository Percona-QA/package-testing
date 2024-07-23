pipeline {
    agent {
        label 'docker'
    }
    parameters {
      string(name: 'PXC_VERSION', defaultValue: '5.7.44.2', description: 'PXC full version')
      string(name: 'PXC_REVISION', defaultValue: '38d2944', description: 'PXC revision')
      string(name: 'WSREP_VERSION', defaultValue: '31.65', description: 'WSREP version')
      string(name: 'PXC57_PKG_VERSION', defaultValue: '5.7.44-rel49-65.2', description: 'PXC-5.7 package version')
      choice(name: 'REPO', choices: ['testing', 'main'], description: 'Choose repository: testing or main')
      booleanParam( 
        defaultValue: false,
        name: 'BUILD_TYPE_MINIMAL'
      )
    }
    stages {
        stage('Binary tarball test') {
            parallel {
                stage('Ubuntu Jammy') {
                    agent {
                        label "min-jammy-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}-${REPO}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.jammy${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Ubuntu Focal') {
                    agent {
                        label "min-focal-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.focal${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Ubuntu Bionic') {
                    agent {
                        label "min-bionic-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.bionic${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Debian Bookworm') {
                    agent {
                        label "min-bookworm-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.bookworm${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Debian Bullseye') {
                    agent {
                        label "min-bullseye-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.bullseye${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Debian Buster') {
                    agent {
                        label "min-buster-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo apt install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.buster${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Oracle Linux 9') {
                    agent {
                        label "min-ol-9-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo yum install -y git wget tar
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.ol9${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Oracle Linux 8') {
                    agent {
                        label "min-ol-8-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo yum install -y git wget tar
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.el8${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
                        }
                    }
                }
                stage('Centos 7') {
                    agent {
                        label "min-centos-7-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                sudo yum install -y git wget
                                TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.el7${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/pxc/report.xml' 
                        }
                    }
                }
            }
        }
    }
}
