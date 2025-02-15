pipeline {
    agent any

    environment {
        TS = credentials('jc_turnstile')
        DISCORD = credentials('jc_discord')
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
                    credentialsId: 'jenkins',
                    url: 'git@git.jakecharman.co.uk:jake/jc-ng.git'

                sh "./build.sh registry.jakecharman.co.uk/jakecharman.co.uk $BUILD_NUMBER"
            }
        }

        stage('Push to registry') {
            when {
                expression { 
                   return params.Build == true
                }
            }
            steps {
                sh "docker push registry.jakecharman.co.uk/jakecharman.co.uk:$BUILD_NUMBER"
                sh "docker push registry.jakecharman.co.uk/jakecharman.co.uk:latest"
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
                    sh "docker pull registry.jakecharman.co.uk/jakecharman.co.uk:latest"
                    sh "docker stop jake || true"
                    sh "docker rm jake || true"
                    sh "docker run --name jake -e DISCORD_WEBHOOK=$DISCORD -e TURNSTILE_SECRET=$TS --restart always --network containers_default -v /opt/containers/jc/projects/:/var/www/jc/projects/ -d registry.jakecharman.co.uk/jakecharman.co.uk:latest"
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
                        credentialsId: 'jenkins',
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
                    sh "docker pull registry.jakecharman.co.uk/jakecharman.co.uk:latest"
                    sh "docker stop jake || true"
                    sh "docker rm jake || true"
                    sh "docker run --name jake -e DISCORD_WEBHOOK=$DISCORD -e TURNSTILE_SECRET=$TS --restart always --network containers_default -v /opt/containers/jc/projects/:/var/www/jc/projects/ -d registry.jakecharman.co.uk/jakecharman.co.uk:latest"
                    sh "/home/jenkins/clearCFCache/clearCache.py 5e240c6ea7864f5f7456af530e6ca988"
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
                        credentialsId: 'jenkins',
                        url: 'git@git.jakecharman.co.uk:jake/jc-content.git'
                    sh "rsync -rv --delete ./ /opt/containers/jc/projects/"
                }
            }
        }
    }
}