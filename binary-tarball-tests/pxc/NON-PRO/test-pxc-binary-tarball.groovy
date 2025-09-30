pipeline {
    agent {
        label 'docker'
    }
    parameters {
        string(name: 'PXC_VERSION', defaultValue: '8.0.37-29.1', description: 'PXC full version')
        string(name: 'PXC_REVISION', defaultValue: 'f735605', description: 'PXC revision')
        string(name: 'WSREP_VERSION', defaultValue: '26.1.4.3', description: 'WSREP version')
        string(name: 'PXC_VERSION_MAJOR', defaultValue: '8.0.37', description: 'PXC_VERSION_MAJOR')
        booleanParam(
            defaultValue: false,
            name: 'BUILD_TYPE_MINIMAL'
        )
    }
    stages {
        stage('Binary tarball test') {
            parallel {
                stage('Ubuntu Noble') {
                    agent {
                        label "min-noble-x64"
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
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo apt install -y git wget tar socat
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
                        }
                    }
                }
                stage('Ubuntu Jammy') {
                    agent {
                        label "min-jammy-x64"
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
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo apt install -y git wget tar socat
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.31${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo apt install -y git wget tar
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.31${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo apt install -y git wget tar
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo apt install -y git wget tar
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                               TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.28${MINIMAL}.tar.gz"
                               TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                               rm -rf package-testing
                               sudo yum install -y git wget tar
                               git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                               cd package-testing/binary-tarball-tests/pxc/NON-PRO
                               wget -q ${TARBALL_LINK}${TARBALL_NAME}
                              ./run.sh || true
                              '''
                            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                                echo "${BUILD_TYPE_MINIMAL}"
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                  MINIMAL="-minimal"
                                fi
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.34${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo yum install -y git wget tar
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q "${TARBALL_LINK}${TARBALL_NAME}"
                               ./run.sh || true
                               '''
                             junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
                        }
                    }  
                }
                stage('RHEL-10') {
                    agent {
                        label "min-rhel-10-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', user>
                            sh '''
                                echo "${BUILD_TYPE_MINIMAL}"
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                  MINIMAL="-minimal"
                                fi
                                TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
                                rm -rf package-testing
                                sudo yum install -y git wget tar
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                                wget -q "${TARBALL_LINK}${TARBALL_NAME}"
                               ./run.sh || true
                               '''
                             junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
