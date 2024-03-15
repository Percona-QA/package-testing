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
                    steps {
                        downloadAndRun('jammy')
                    }
                }
                stage('Ubuntu Focal') {
                    steps {
                        downloadAndRun('focal')
                    }
                }
                stage('Ubuntu Bionic') {
                    steps {
                        downloadAndRun('bionic')
                    }
                }
                stage('Debian Bookworm') {
                    steps {
                        downloadAndRun('bookworm')
                    }
                }
                stage('Debian Bullseye') {
                    steps {
                        downloadAndRun('bullseye')
                    }
                }
                stage('Debian Buster') {
                    steps {
                        downloadAndRun('buster')
                    }
                }
                stage('Oracle Linux 9') {
                    steps {
                        downloadAndRun('ol-9')
                    }
                }
                stage('Oracle Linux 8') {
                    steps {
                        downloadAndRun('ol-8')
                    }
                }
                stage('Centos 7') {
                    steps {
                        downloadAndRun('centos-7')
                    }
                }
            }
        }
    }
}

def downloadAndRun(distroCode) {
    script {
        currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}-${distroCode}"
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
            TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.${distroCode}${MINIMAL}.tar.gz"
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

