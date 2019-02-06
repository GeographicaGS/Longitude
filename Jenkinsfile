#!/usr/bin/env groovy

// Global Environment variables
FAILURE_EMAIL = "build@geographica.gs"
DESIRED_REPOSITORY = "https://github.com/GeographicaGS/Longitude.git"
PUBLISH_BRANCH = "publish"
REPO_NAME = "longitude"

pipeline{
  agent { node {
    label 'master'
  } }

  options {
    ansiColor('xterm')
  }

  stages {
    stage('Preparing for build') {
      agent { node {
        label 'master'
      } }
      steps {
        prepareBuild()
      }
    }
    stage ('Building') {
      agent { node {
        label 'docker'
      } }
      steps {
        sh "docker build --pull=true -t geographica/${REPO_NAME}:${git_commit} ."
      }
    }
    stage('Linter')
    {
      agent { node {
        label 'docker'
      } }
      steps {
        sh "docker run --rm geographica/${REPO_NAME}:${git_commit} /root/.poetry/bin/poetry run pylint --ignore=samples -E longitude"
      }
    }
    stage('Testing')
    {
      agent { node {
        label 'docker'
      } }
      steps {
        sh "docker run --rm geographica/${REPO_NAME}:${git_commit} /root/.poetry/bin/poetry run pytest --cov=longitude.core longitude/core/tests/"
      }
    }
    stage ('Publish') {
      agent { node {
        label 'docker'
      } }
      when { anyOf {
        branch "${PUBLISH_BRANCH}"
      } }
      steps{
        // TODO: this must be "publish" but we keep "build" while testing the Jenkins pipeline
        sh "docker run --rm geographica/${REPO_NAME}:${git_commit} /root/.poetry/bin/poetry build"
      }
    }
    // TODO: Stage to check that module can be imported
  }
  post {
    always {
      deleteDir() /* clean up our workspace */
    }
    unstable {
      notifyStatus(currentBuild.currentResult)
    }
    failure {
      notifyStatus(currentBuild.currentResult)
    }
  }
}

def prepareBuild() {
  script {
    checkout scm

    sh "git rev-parse --short HEAD > .git/git_commit"
    sh "git --no-pager show -s --format='%ae' HEAD > .git/git_committer_email"

    workspace = pwd()
    branch_name = "${ env.BRANCH_NAME }".replaceAll("/", "_")
    git_commit = readFile(".git/git_commit").replaceAll("\n", "").replaceAll("\r", "")
    //git_commit = sh(returnStdout: true, script: "git describe").trim()
    build_name = "${git_commit}"
    job_name = "${ env.JOB_NAME }".replaceAll("%2F", "/")
    committer_email = readFile(".git/git_committer_email").replaceAll("\n", "").replaceAll("\r", "")
    GIT_URL = sh(returnStdout: true, script: "git config --get remote.origin.url").trim()
    if ( GIT_URL != DESIRED_REPOSITORY ) {
      error("This jenkinsfile is configured for '${ DESIRED_REPOSITORY }' but it was executed from '${ GIT_URL }'.")
    }
  }
}

def notifyStatus(buildStatus) {
  def status
  def send_to

  try {
    switch (branch_name) {
      case 'master':
        send_to = "${ committer_email }, ${ FAILURE_EMAIL }"
        break
      default:
        send_to = "${ committer_email }"
        break
    }
  } catch(Exception ex) {
    send_to = "${ FAILURE_EMAIL }"
  }

  echo "Sending error email to: ${ send_to }"
  try {
    mail  to: "${ send_to }",
          from: "Jenkins Geographica <system@geographica.gs>",
          subject: "[${ buildStatus }]   ${currentBuild.fullDisplayName}",
          body: "Something is wrong in '${currentBuild.fullDisplayName}'. \n\nSee ${env.BUILD_URL} for more details."
  } catch(Exception ex) {
    echo "Something was wrong sending error email :("
  }
}
