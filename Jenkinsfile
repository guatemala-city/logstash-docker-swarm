#!/usr/bin/env groovy

try {
    def docker_registry_host = env.DOCKER_REGISTRY_HOST ?: 'index.docker.io/v2/'
    def docker_registry_credentials_id = env.DOCKER_REGISTRY_CREDENTIALS_ID?: 'dockerhub_cred'
    def organization = 'guatemalacityex'
    def name = 'logstash'
    def uniqueWorkspace = "build-" +env.BUILD_ID


    timestamps {
        node('docker-swarm-manager') {
            def version
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
