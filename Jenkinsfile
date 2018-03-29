#!/usr/bin/env groovy

try {
    def docker_registry_host = env.DOCKER_REGISTRY_HOST ?: 'index.docker.io/v2/'
    def docker_registry_credentials_id = env.DOCKER_REGISTRY_CREDENTIALS_ID?: 'dockerhub_cred'
    def repository = 'guatemalacityex'
    def name = 'logstash'
    def version

    def imageName
    def imageNameLatest
    def environmentId
    def key
    def serviceName
    def lastUpdateTime = ""
    def serviceExists
    def pythonHelper

    String ls_heap_size = "1g"

    def source_file
    def destination_file

    properties([[$class: 'BuildDiscarderProperty',
                 strategy: [$class: 'LogRotator', numToKeepStr: '10']]])

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
                version      = readFile "${env.WORKSPACE}/version.txt"
                key          = upstream_branch_name.split('/').last()
                serviceName  = key + "_" + name

                imageName        = repository + "/" + name + "-" + key + ":" + version
                imageNameLatest  = repository + "/" + name + "-" + key + ":latest"

                if (upstream_branch_name.contains('nonprod')) {
                    environmentId    = "2"
                    source_file      = "/vagrant/nonprod_src.txt"
                    destination_file = "/vagrant/nonprod_dst.txt"

                } else if (upstream_branch_name.contains('prod')) {
                    environmentId    = "3"
                    source_file      = "/vagrant/prod_src.txt"
                    destination_file = "/vagrant/prod_dst.txt"
                }
            }

            docker.withRegistry("https://${docker_registry_host}", docker_registry_credentials_id) {
                //TODO: sh "docker login -u ${USERNAME} -p ${PASSWORD}"
                pythonHelper = docker.image("${repository}/python-helper:1.0-logstash")

                stage('Configure') {
                    pythonHelper.inside("-u root ") {
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
                    sh "docker image build -t ${imageName} -t ${imageNameLatest}" +

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
                    try {
                        pythonHelper.inside("-u root -v /var/run/docker.sock:/var/run/docker.sock") {
                            sh "IMAGE_NAME=${imageName} LS_HEAP_SIZE=${ls_heap_size} " +
                                    "testinfra -v test --junit-xml test/reports/custom-image-tests.junit.xml"
                        }
                    }finally {
                        junit 'test/reports/*.xml'
                    }
                }

                stage('Push') {
                    // check if pushing and deploying are allowed
                    if ((key == "experimental") || (env.BRANCH_NAME == "master")) {
                        // if allowed, tag and push
                        def image_latest = docker.image(imageNameLatest)
                        image_latest.push()
                        def image = docker.image(imageName)
                        image.push()
                    } else {
                        currentBuild.rawBuild.result = Result.ABORTED
                        throw new hudson.AbortException('Deployment and propagation are not allowed on this branch')
                    }
                }

                stage('Deploy') {
                    def is_all_replicas_up
                    def cur_update_time

                    serviceExists = sh script: "docker service ls --filter name=${serviceName} " +
                                                "--format '{{if .}} exist{{end}}' ",
                                                returnStdout: true //returns "exist" if the service exists, none otherwise

                    if (serviceExists.contains('exist')) {
                        // if service exists, get last_update_time
                        lastUpdateTime = sh script: "docker inspect ${serviceName} " +
                                                "--format='{{.UpdatedAt}}' ", returnStdout: true
                    }

                    sh "IMAGE_NAME=${imageNameLatest} WORKER=${environmentId} " +
                            "docker stack deploy --with-registry-auth --compose-file docker-compose.yml ${key}"

                    timeout(5) {
                        waitUntil {
                            is_all_replicas_up = sh script: "docker service ls " +
                                    "--filter name=${service_name} " +
                                    "--format '{{if (eq (index .Replicas 0) (index .Replicas 2))}} ok {{else}} error {{end}}'",
                                    returnStdout: true

                            cur_update_time = sh script: "docker inspect ${service_name} " +
                                    "--format='{{.UpdatedAt}}' ", returnStdout: true

                            return((cur_update_time != last_update_time) && (is_all_replicas_up.contains('ok')))
                        }
                    }
                }

                stage('Cleanup') {
                    sh "docker image rm ${imageName}"
                    sh "docker image rm ${imageNameLatest}"
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
