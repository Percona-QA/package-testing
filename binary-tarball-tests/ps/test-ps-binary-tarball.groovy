
pipeline {
    agent {
        label 'docker'
    }
    environment {
        PRODUCT_TO_TEST = "${params.PRODUCT_TO_TEST}"
    }
    parameters {
        choice(
            choices: ['PS80', 'PS84', 'PS_INN_LTS'],
            description: 'Choose the product version to test',
            name: 'PRODUCT_TO_TEST'
        )
        booleanParam(
            defaultValue: false, 
            name: 'BUILD_TYPE_MINIMAL'
        )
    }
    stages {
        stage('SET PS_VERSION and PS_REVISION') {
            steps {
                script {
                    sh '''
                        rm -rf /package-testing
                        rm -f master.zip
                        wget https://github.com/Percona-QA/package-testing/archive/master.zip
                        unzip master.zip
                        rm -f master.zip
                        mv "package-testing-master" package-testing
                    '''
                    
                    def VERSION = sh(
                        script: '''grep ${PRODUCT_TO_TEST}_VER VERSIONS | awk -F= '{print \$2}' | sed 's/"//g' ''',
                        returnStdout: true
                        ).trim()

                    def REVISION = sh(
                        script: ''' grep ${PRODUCT_TO_TEST}_REV VERSIONS | awk -F= '{print \$2}' | sed 's/"//g' ''',
                        returnStdout: true
                        ).trim()
                    
    
                    env.PS_VERSION = VERSION
                    env.PS_REVISION = REVISION

                    echo "PS_VERSION fetched: ${env.PS_VERSION}"
                    echo "PS_REVISION fetched: ${env.PS_REVISION}"

                }
            }
        }
        stage('Set environmental variable'){
            steps{
                 script {
                    // Now, you can access these global environment variables
                    echo "Using PS_VERSION: ${env.PS_VERSION}"
                    echo "Using PS_REVISION: ${env.PS_REVISION}"
                }
            }
        }
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                                cd package-testing/binary-tarball-tests/ps
                                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                                ./run.sh || true
                            '''
                            junit 'package-testing/binary-tarball-tests/ps/report.xml'
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
                                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
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
