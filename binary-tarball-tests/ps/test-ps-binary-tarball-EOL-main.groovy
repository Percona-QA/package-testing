pipeline {
    agent {
        label 'docker'
    }
    parameters {
        string(name: 'PS_VERSION', defaultValue: '5.7.44-49', description: 'PS full version')
        string(name: 'PS_REVISION', defaultValue: 'c643a1242d8', description: 'PS revision')
        choice(name: 'REPO', choices: ['testing', 'main'], description: 'Choose repository: testing or main')
        booleanParam(defaultValue: false, name: 'BUILD_TYPE_MINIMAL')
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
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}-${REPO}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.jammy${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.focal${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                        }
                    }
                }
                stage('Ubuntu Bionic') {
                    agent {
                        label "min-bionic-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.bionic${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.bookworm${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                        }
                    }
                }
                stage('Debian Bullseye') {
                    agent {
                        label "min-bullseye-x64"
                    }
                    steps {
                        script {
                            currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
                        }
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.bullseye${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.buster${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ol9${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.el8${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
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
                        withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
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
                                TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.el7${MINIMAL}.tar.gz"
                                if [ "${REPO}" = "main" ]; then
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/ps-57-eol/tarballs/Percona-Server-${PS_VERSION}/"
                                else
                                    TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/ps-gated-${PS_VERSION}/"
                                fi
                                rm -rf package-testing
                                git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps-eol --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                        }
                    }
                }
            }
        }
    }
}
