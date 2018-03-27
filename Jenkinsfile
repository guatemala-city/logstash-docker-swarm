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
                    checkout scm: [$class: 'GitSCM', branches: [[name: upstream_branch_name]], userRemoteConfigs: [[url: 'git@github.com:guatemala-city/logstash-docker-swarm.git']]]
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
                    //TODO: select source file

                } else if (upstream_branch_name.contains('prod')) {
                    //TODO: select worker3
                    //TODO: select source file
                }
            }

        docker.withRegistry("https://${env.DOCKER_REGISTRY_HOST}", env.DOCKER_REGISTRY_CREDENTIALS_ID) {
            //TODO: sh "docker login -u ${USERNAME} -p ${PASSWORD}"
            pythonHelper = docker.image('guatemalacityex/python-helper:1.0-logstash')

            stage('Configure') {
                pythonHelper.inside("-u root ") {
                    ls_heap_size = "1g"
                    //TODO Jinja --> fill source files
                    //TODO Jinja --> configure
                    //TODO Jinja --> select node
                }
            }


            stage('Build') {
                //TODO: add labels
                //build and tag
            }


            stage('Test') {
                try {
                }finally {
                    junit 'tests/reports/*.xml'
                }
            }

                stage('Push') {
                    // check if pushing and deploying are allowed
                    if ((key == "test") || (build_branch == "master")) {
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
        }//withReg


    }//node
}//timestamps

} catch (ex) {
    // If there was an exception thrown, the build failed
    if (currentBuild.result != "ABORTED") {
        // Send e-mail notifications for failed or unstable builds.
        // currentBuild.result must be non-null for this step to work.
        emailext(
                recipientProviders: [
                        [$class: 'DevelopersRecipientProvider'],
                        [$class: 'RequesterRecipientProvider']],
                subject: "Job '${env.JOB_NAME}' - Build ${env.BUILD_DISPLAY_NAME} - FAILED!",
                body: """<p>Job '${env.JOB_NAME}' - Build ${env.BUILD_DISPLAY_NAME} - FAILED:</p>
                        <p>Check console output &QUOT;<a href='${env.BUILD_URL}'>${env.BUILD_DISPLAY_NAME}</a>&QUOT;
                        to view the results.</p>"""
        )
    }

    // Must re-throw exception to propagate error:
    throw ex
}
