pipeline {
    agent {
        label 'docker'
    }
    parameters {
        string(name: 'PS_VERSION', defaultValue: '8.0.37-29', description: 'PS full version')
        string(name: 'PS_REVISION', defaultValue: 'e3b0a41f', description: 'PS revision')
        booleanParam(defaultValue: false, name: 'BUILD_TYPE_MINIMAL')
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
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Ubuntu Jammy') {
                    agent {
                        label "min-jammy-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Ubuntu Focal') {
                    agent {
                        label "min-focal-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.31${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Debian Bookworm') {
                    agent {
                        label "min-bookworm-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.35${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Debain Bullseye') {
                    agent {
                        label "min-bullseye-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.31${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Debian Buster') {
                    agent {
                        label "min-buster-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.28${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Oracle Linux 9') {
                    agent {
                        label "min-ol-9-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.34${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Oracle Linux 8') {
                    agent {
                        label "min-ol-8-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.28${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
                stage('Centos 7') {
                    agent {
                        label "min-centos-7-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                            sh '''
                                echo ${BUILD_TYPE_MINIMAL}
                                MINIMAL=""
                                if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
                                    MINIMAL="-minimal"
                                fi
                                if [ -f /usr/bin/yum ]; then
                                    sudo yum install -y git wget
                                else
                                    sudo apt install -y git wget
                                fi
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.17${MINIMAL}.tar.gz"
                                TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch add-dist --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
                        }
                    }
                }
            }
        }
    }
