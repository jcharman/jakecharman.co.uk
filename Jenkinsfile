pipeline {
    agent any

    environment {
        TS = credentials('jc_turnstile')
        DISCORD = credentials('jc_discord')
        DISCORD_ERR_STAGING = credentials('jc_discord_err_staging')
        DISCORD_ERR_PROD = credentials('jc_discord_err_prod')
    }

    stages{
        stage ('Set up parameters') {
            steps {
                script{
                properties ([
                    parameters([
                        booleanParam(defaultValue: true, description: 'Build from source', name: 'Build'),
                        booleanParam(defaultValue: true, description: 'Deploy to servers', name: 'Deploy'),
                        booleanParam(defaultValue: true, description: 'Update posts', name: 'Update'),
                        ])
                    ])
                }
            }
        }
        stage('Build') {
            when {
                expression { 
                   return params.Build == true
                }
            }
            steps {
                git branch: 'master',
                    credentialsId: 'Git',
                    url: 'git@git.jakecharman.co.uk:jake/jc-ng.git'

                sh "./build.sh git.jakecharman.co.uk/jake/jakecharman.co.uk $BUILD_NUMBER"
                sh "./build.sh europe-west2-docker.pkg.dev/jakecharman/web/jakecharman.co.uk $BUILD_NUMBER"
            }
        }

        stage('Security scan') {
            steps {
                sh "docker kill sectest || true"
                sh "docker rm sectest || true"
                sh "docker run -d --name sectest git.jakecharman.co.uk/jake/jakecharman.co.uk:$BUILD_NUMBER"
                sh "docker exec sectest pip3 install pip-audit --break-system-packages"
                sh "docker exec sectest pip-audit"
                sh "docker stop sectest"
                sh "docker rm sectest"
            }
        }

        stage('Push to registry') {
            when {
                expression { 
                   return params.Build == true
                }
            }
            steps {
                sh "docker push git.jakecharman.co.uk/jake/jakecharman.co.uk:$BUILD_NUMBER"
                sh "docker push git.jakecharman.co.uk/jake/jakecharman.co.uk:latest"
                sh "docker push europe-west2-docker.pkg.dev/jakecharman/web/jakecharman.co.uk:latest"
            }
        }

        stage('Deploy to staging server') {
            when {
                expression { 
                   return params.Deploy == true
                }
            }
            steps{
                node('web-staging') {
                    sh "docker pull git.jakecharman.co.uk/jake/jakecharman.co.uk:latest"
                    sh "docker stop jake || true"
                    sh "docker rm jake || true"
                    sh "docker run --name jake -e DISCORD_ERR_HOOK=$DISCORD_ERR_STAGING -e DISCORD_WEBHOOK=$DISCORD -e TURNSTILE_SECRET=$TS --restart always --network containers_default -v /opt/containers/jc/projects/:/var/www/jc/projects/ -d git.jakecharman.co.uk/jake/jakecharman.co.uk:latest"
                }
            }
        }

        stage('Update content on staging server') {
            when {
                expression { 
                   return params.Update == true
                }
            }
            steps {
                node('web-staging') {
                    git branch: 'master',
                        credentialsId: 'Git',
                        url: 'git@git.jakecharman.co.uk:jake/jc-content.git'
                    sh "rsync -rv --delete ./ /opt/containers/jc/projects/"
                }
            }
        }

        stage('Wait for confirmation to push to prod') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                       input "Deploy to production?"
                }
            }
        }

        stage('Deploy to production server') {
            when {
                expression { 
                   return params.Deploy == true
                }
            }
            steps{
                node('web-server') {
                    sh "docker pull git.jakecharman.co.uk/jake/jakecharman.co.uk:latest"
                    sh "docker stop jake || true"
                    sh "docker rm jake || true"
                    sh "docker run --name jake -e DISCORD_ERR_HOOK=$DISCORD_ERR_PROD -e DISCORD_WEBHOOK=$DISCORD -e TURNSTILE_SECRET=$TS --restart always --network containers_default -v /opt/containers/jc/projects/:/var/www/jc/projects/ -d git.jakecharman.co.uk/jake/jakecharman.co.uk:latest"
                    sh "/home/jenkins/clearCFCache/clearCache.py a514fb61e1413b88aabbb19df16b8508"
                }
            }
        }

        stage('Update content on production server') {
            when {
                expression { 
                   return params.Update == true
                }
            }
            steps {
                node('web-server') {
                    git branch: 'master',
                        credentialsId: 'Git',
                        url: 'git@git.jakecharman.co.uk:jake/jc-content.git'
                    sh "rsync -rv --delete ./ /opt/containers/jc/projects/"
                }
            }
        }
    }
}