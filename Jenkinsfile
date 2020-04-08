pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
        // Only keep the last 5 builds.
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    stages {
        stage('Run Integration Tests') {
            when {
                anyOf {
                    changeRequest()
                }
            }
            environment {
                //spawns GITHUB_USR and GITHUB_PSW environment variables
                GITHUB=credentials('38b2e4a6-167a-40b2-be6f-d69be42c8190')
            }
            steps {
                sh 'docker build \
                    --build-arg major_release=20.02 \
                    --build-arg platform=mycroft_mark_1 \
                    --build-arg pull_request=$BRANCH_NAME \
                    --build-arg branch_name=$CHANGE_BRANCH \
                    --build-arg github_api_key=$GITHUB_PSW \
                    --no-cache \
                    -t voight-kampff-skill:$BRANCH_NAME .'
                echo 'Running Tests'
                timeout(time: 60, unit: 'MINUTES')
                {
                    sh 'docker run \
                        --volume "$HOME/voight-kampff/identity:/root/.mycroft/identity" \
                        --volume "$HOME/voight-kampff/:/root/allure" \
                        voight-kampff-skill:$BRANCH_NAME \
                        -f allure_behave.formatter:AllureFormatter \
                        -o /root/allure/allure-result --tags ~@xfail'
                }
            }
            post {
                always {
                    echo 'Report Test Results'
                    echo 'Changing ownership...'
                    sh 'docker run \
                        -v "$HOME/voight-kampff/:/root/allure" \
                        --entrypoint=/bin/bash \
                        voight-kampff-skill:$BRANCH_NAME \
                        -x -c "chown $(id -u $USER):$(id -g $USER) \
                        -R /root/allure/"'

                    echo 'Transferring...'
                    sh 'rm -rf allure-result/*'
                    sh 'mv $HOME/voight-kampff/allure-result allure-result'
                    script {
                        allure([
                            includeProperties: false,
                            jdk: '',
                            properties: [],
                            reportBuildPolicy: 'ALWAYS',
                            results: [[path: 'allure-result']]
                        ])
                    }
                    unarchive mapping:['allure-report.zip': 'allure-report.zip']
                    sh (
                        label: 'Publish Report to Web Server',
                        script: '''scp allure-report.zip root@157.245.127.234:~;
                            ssh root@157.245.127.234 "unzip -o ~/allure-report.zip";
                            ssh root@157.245.127.234 "rm -rf /var/www/voight-kampff/skills/${BRANCH_NAME}";
                            ssh root@157.245.127.234 "mv allure-report /var/www/voight-kampff/skills/${BRANCH_NAME}"
                        '''
                    )
                    echo 'Report Published'
                }
                failure {
                    // Send failure email containing a link to the Jenkins build
                    // the results report and the console log messages to Mycroft
                    // developers, the developers of the pull request and the
                    // developers that caused the build to fail.
                    echo 'Sending Failure Email'
                    emailext (
                        attachLog: true,
                        subject: "FAILURE - Skills Integration Tests - Build ${BRANCH_NAME} #${BUILD_NUMBER}",
                        body: """
                            <p>
                                One or more integration tests failed. Use the
                                resources below to identify the issue and fix
                                the failing tests.
                            </p>
                            <br>
                            <p>
                                <a href='${BUILD_URL}'>
                                    Jenkins Build Details
                                </a>
                                &nbsp(Requires account on Mycroft's Jenkins instance)
                            </p>
                            <br>
                            <p>
                                <a href='https://reports.mycroft.ai/core/${BRANCH_ALIAS}'>
                                    Report of Test Results
                                </a>
                            </p>
                            <br>
                            <p>Console log is attached.</p>""",
                        replyTo: 'devops@mycroft.ai',
                        to: 'dev@mycroft.ai',
                        recipientProviders: [
                            [$class: 'RequesterRecipientProvider'],
                            [$class:'CulpritsRecipientProvider'],
                            [$class:'DevelopersRecipientProvider']
                        ]
                    )
                }
                success {
                    // Send success email containing a link to the Jenkins build
                    // and the results report to Mycroft developers, the developers
                    // of the pull request and the developers that caused the
                    // last failed build.
                    echo 'Sending Success Email'
                    emailext (
                        subject: "SUCCESS - Skills Integration Tests - Build ${BRANCH_NAME} #${BUILD_NUMBER}",
                        body: """
                            <p>
                                All integration tests passed. No further action required.
                            </p>
                            <br>
                            <p>
                                <a href='${BUILD_URL}'>
                                    Jenkins Build Details
                                </a>
                                &nbsp(Requires account on Mycroft's Jenkins instance)
                            </p>
                            <br>
                            <p>
                                <a href='https://reports.mycroft.ai/core/${BRANCH_ALIAS}'>
                                    Report of Test Results
                                </a>
                            </p>""",
                        replyTo: 'devops@mycroft.ai',
                        to: 'dev@mycroft.ai',
                        recipientProviders: [
                            [$class: 'RequesterRecipientProvider'],
                            [$class:'CulpritsRecipientProvider'],
                            [$class:'DevelopersRecipientProvider']
                        ]
                    )
                }
            }
        }
    }
    post {
        cleanup {
            sh(
                label: 'Docker Container and Image Cleanup',
                script: '''
                    docker container prune --force;
                    docker image prune --force;
                '''
            )
        }
    }
}