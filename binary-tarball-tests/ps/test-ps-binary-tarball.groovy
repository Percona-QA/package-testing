def osConfigs = [
    "min-noble-x64"     : "2.35",
    "min-jammy-x64"     : "2.35",
    "min-focal-x64"     : "2.31",
    "min-bookworm-x64"  : "2.35",
    "min-bullseye-x64"  : "2.31",
    "min-trixie-x64"    : "2.31",
    "min-ol-9-x64"      : "2.34",
    "min-ol-8-x64"      : "2.28",
    "min-rhel-10-x64"   : "2.35",
    "min-al2023-x64"    : "2.35",
]

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
                        wget -O master.zip https://github.com/kaushikpuneet07/package-testing/archive/refs/heads/ps84-up.zip
                        unzip master.zip
                        rm -f master.zip
                        mv "package-testing-ps84-up" package-testing
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

                    currentBuild.displayName = "#${BUILD_NUMBER}-${env.PS_VERSION}-${env.PS_REVISION}"
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

        stage('Test on Multiple OS') {
            steps {
                script {
                    PS_VERSION = env.PS_VERSION

                    def parallelStages = [:]
                    def unstabilityFlag = false  // Flag to track test failures

                    osConfigs.each { label, version ->
                        parallelStages[label] = {
                            node(label) {
                                stage("Test on ${label}") {
                                    script {
                                        echo "Starting tests on: ${label}"
                                        
                                        // Run the test function
                                        runtarballtests(PS_VERSION, params.BUILD_TYPE_MINIMAL, version)
                                        
                                        // Check the report file existence
                                        sh """
                                            echo 'Checking report file existence:' 
                                            ls -la /tmp/package-testing/binary-tarball-tests/ps/
                                        """

                                        // Rename the report file to avoid conflicts
                                        sh "mv /tmp/package-testing/binary-tarball-tests/ps/report.xml ${WORKSPACE}/report-${label}.xml"

                                        // Stash the test report
                                        stash name: "report-${label}", includes: "report-${label}.xml"

                                        // Extract failure count without additional dependencies
                                        def failures = sh(
                                            script: "grep -o 'failures=\"[0-9]*\"' ${WORKSPACE}/report-${label}.xml | sed 's/failures=\"//;s/\"//'",
                                            returnStdout: true
                                        ).trim()

                                        echo "Failure count for ${label}: ${failures}"

                                        // Convert to integer and check
                                        if (failures.isInteger() && failures.toInteger() > 0) {
                                            unstabilityFlag = true
                                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                                sh "exit ${failures}"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Run all generated parallel stages
                    parallel parallelStages

                    // Mark build unstable if any test failed
                    if (unstabilityFlag) {
                        currentBuild.result = 'UNSTABLE'
                        echo "Marking build as UNSTABLE due to test failures"
                    }
                }
            }
        }




    }


    post {
        always {
            script {

                osConfigs.each { label, version ->
                    try {
                        unstash name: "report-${label}"

                        //sh "sed -i \"s#hostname=\\\"[^\\\"]*\\\"#hostname=\\\"${label}\\\"#g\" ${env.WORKSPACE}/report-${label}.xml"

                        sh "sed -i \"s#classname=\\\"\\([^\\\"]*\\)\\\"#classname=\\\"\\1-${label}\\\"#g\" ${env.WORKSPACE}/report-${label}.xml"


                    } catch (Exception e) {
                        echo " Warning: Stash report-${label} not found, skipping..."
                    }
                }
            }
            junit '**/*.xml'
            archiveArtifacts artifacts: '**/*.xml', fingerprint: true
        }

        success {
            script {
                
                if (params.PRODUCT_TO_TEST == "PS80") {
                    product_to_test = "ps_80"
                } else if (params.PRODUCT_TO_TEST == "PS84") {
                    product_to_test = "ps_84"
                } else if (params.PRODUCT_TO_TEST == "PS_INN_LTS") {
                    product_to_test = "ps_lts_innovation"
                } else if (params.PRODUCT_TO_TEST == "PS57") {
                    product_to_test = "ps_57"
                }

                def eol_param = (product_to_test == "ps_57") ? "yes" : "no"

                build job: 'ps-package-testing-molecule-parallel', propagate: false, wait: false, parameters: [
                    string(name: 'product_to_test', value: "${product_to_test}"),
                    string(name: 'install_repo', value: "testing"),
                    string(name: 'EOL', value: "${eol_param}"),
                    string(name: 'git_repo', value: "https://github.com/kaushikpuneet07/package-testing.git"),
                    string(name: 'git_branch', value: "ps84-up"),
                    string(name: 'check_warnings', value: "yes"),
                    string(name: 'install_mysql_shell', value: "yes")
                ]

            }
        }
        failure {
            error "Binary tarball tests failed. Skipping PT integration tests"
        }



    }


}



def runtarballtests(String psVersion, boolean buildMinimal, String glibcVersion) {
    sh """
        echo "PS_VERSION is ${psVersion}"
        echo "BUILD_TYPE_MINIMAL=${buildMinimal}"
        MINIMAL=""
        if [ "\${buildMinimal}" = "true" ]; then
            MINIMAL="-minimal"
        fi

        if [ -f /usr/bin/yum ]; then
            sudo yum install -y git wget
        else
            sudo apt install -y git wget
        fi

        TARBALL_NAME="Percona-Server-${psVersion}-Linux.x86_64.glibc${glibcVersion}\${MINIMAL}.tar.gz"
        TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-${psVersion}/"

        rm -rf /usr/local/package-testing
        cd /tmp
        git clone https://github.com/kaushikpuneet07/package-testing.git --branch ps84-up --depth 1
        cd /tmp/package-testing/binary-tarball-tests/ps

        wget "\${TARBALL_LINK}\${TARBALL_NAME}"

        ls -la 

        echo "Checking if run.sh exists..."
        if [ ! -f ./run.sh ]; then
            echo "ERROR: run.sh not found!"
            exit 1
        fi

        echo "Making run.sh executable..."
        chmod +x ./run.sh
        
        echo "Running ./run.sh..."
        ./run.sh 2>&1 | tee output.log
        
        if [ \$? -ne 0 ]; then
            echo "ERROR: run.sh failed to execute!"
            exit 1
        fi
        
        echo "run.sh execution completed."
        ls -la 

        cp report.xml ${WORKSPACE}/report.xml
    """
}
