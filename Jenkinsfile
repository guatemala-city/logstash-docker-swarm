#!/usr/bin/env groovy
try {
    node('docker') {



        stage('Trigger dev'){
            build job: './develop'
        }
    }

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
