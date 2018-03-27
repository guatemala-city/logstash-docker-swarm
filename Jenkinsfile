#!/usr/bin/env groovy

try {
    def docker_registry_host = env.DOCKER_REGISTRY_HOST ?: 'index.docker.io/v2/'
    def docker_registry_credentials_id = env.DOCKER_REGISTRY_CREDENTIALS_ID?: 'dockerhub_cred'
    def organization = 'guatemalacityex'
    def name = 'logstash'
    def uniqueWorkspace = "build-" +env.BUILD_ID
    def version

    def image_name_latest
    def environment
    def key
    def service_name
    def build_branch
    def last_update_time = ""
    def is_service_exist
    def pythonHelper
    String ls_heap_size

    def source_file
    def destination_file

    timestamps {
        node('docker-swarm-manager') {

            def upstream_branch_name



            stage('Checkout') {

                checkout scm

                def build = currentBuild.rawBuild
                def cause = build.getCause(hudson.model.Cause.UpstreamCause.class)

                if (cause != null) {
                    echo "getUpstreamProject: " + cause.getUpstreamProject()
                    echo "getUpstreamBuild: " + cause.getUpstreamBuild()
                    upstream_branch_name = cause.getUpstreamProject().split('/')[2].replace("%2F", "/")
                    echo "upstream_branch_name: " + upstream_branch_name
                } else {
                    print "the cause is: " + currentBuild.rawBuild.getCauses()
                    currentBuild.rawBuild.result = Result.ABORTED
                    throw new hudson.AbortException('Guess what!')
                }
            }

            stage('Checkout upstream branch') {
                dir('config') {
                    checkout scm: [$class: 'GitSCM', branches: [[name: upstream_branch_name]], userRemoteConfigs: [[url: 'https://github.com/guatemala-city/logstash-docker-swarm.git']]]
                }
            }

            stage('Set environment') {
                version = readFile "${env.WORKSPACE}/version.txt"


                key = upstream_branch_name.split('/').last()
                service_name = key + "_" + name

                image_name = name + "-" + key + ":" + version
                image_name_latest = name + "-" + key + ":latest"
                build_branch = env.BRANCH_NAME.split('/').last()

                if (upstream_branch_name.contains('nonprod')) {
                    //TODO: select worker2
                    source_file      = "/vagrant/nonprod_src.txt"
                    destination_file = "/vagrant/nonprod_dst.txt"

                } else if (upstream_branch_name.contains('prod')) {
                    //TODO: select worker3
                    source_file      = "/vagrant/prod_src.txt"
                    destination_file = "/vagrant/prod_dst.txt"
                }
            }

        docker.withRegistry("https://${env.DOCKER_REGISTRY_HOST}", env.DOCKER_REGISTRY_CREDENTIALS_ID) {
            //TODO: sh "docker login -u ${USERNAME} -p ${PASSWORD}"
            pythonHelper = docker.image('guatemalacityex/python-helper:1.0-logstash')

            stage('Configure') {
                pythonHelper.inside("-u root ") {
                    ls_heap_size = "1g"
                    //the parameters are injected into the pipeline.conf
                    sh('#!/bin/sh -e\n' + " jinja2 " +
                            " -D SOURCE_FILE_PATH='${source_file}'" +
                            " -D DESTINATION_FILE_PATH='${destination_file}'"+
                            " config/logstash/pipeline.conf.j2 > build/pipeline.conf")
                }
            }


            stage('Build') {
                //TODO: add labels
                //build and tag
                sh "docker image build -t ${image_name} -t ${image_name_latest}" +
                        " --build-arg LS_JAVA_OPTS=-Xmx${ls_heap_size}" +
                        " --build-arg SRC_IMAGE_VER=${version}" +
                        " --build-arg BRANCH_NAME='${env.BRANCH_NAME}'" +
                        " --build-arg COMMIT_ID='${env.COMMIT_ID}' " +
                        " --build-arg BUILD_ID='${env.BUILD_ID}'  " +
                        " --build-arg JENKINS_URL='${env.JENKINS_URL}' " +
                        " --build-arg JOB_NAME='${env.JOB_NAME}' " +
                        " --build-arg NODE_NAME='${env.NODE_NAME}' " +
                        " --no-cache --rm " +
                        "./build/"
            }


            stage('Test') {
//                try {
//
//                }finally {
//                    junit 'test/reports/*.xml'
//                }
            }

                stage('Push') {
                    // check if pushing and deploying are allowed
                    if ((key == "experimental") || (build_branch == "master")) {
                        // if allowed, tag and push
                        def image_latest = docker.image(image_name_latest)
                        image_latest.push()
                        def image = docker.image(image_name)
                        image.push()
                    } else {
                        currentBuild.rawBuild.result = Result.ABORTED
                        throw new hudson.AbortException('deployment stage is not allowed on this branch')
                    }
                }
                stage('Cleanup') {
                    // clean the image from the host which build the image
                    // this should occur anyway..
                    sh "docker image rm ${image_name}"
                }

            stage('Deploy') {
                //TODO Jinja --> select node
            }

        }//withReg




        }//node
}//timestamps

} catch (ex) {
    // If there was an exception thrown, the build failed
//    if (currentBuild.result != "ABORTED") {
//        // Send e-mail notifications for failed or unstable builds.
//        // currentBuild.result must be non-null for this step to work.
//        emailext(
//                recipientProviders: [
//                        [$class: 'DevelopersRecipientProvider'],
//                        [$class: 'RequesterRecipientProvider']],
//                subject: "Job '${env.JOB_NAME}' - Build ${env.BUILD_DISPLAY_NAME} - FAILED!",
//                body: """<p>Job '${env.JOB_NAME}' - Build ${env.BUILD_DISPLAY_NAME} - FAILED:</p>
//                        <p>Check console output &QUOT;<a href='${env.BUILD_URL}'>${env.BUILD_DISPLAY_NAME}</a>&QUOT;
//                        to view the results.</p>"""
//        )
//    }

    // Must re-throw exception to propagate error:
    throw ex
}
