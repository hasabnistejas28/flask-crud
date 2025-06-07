pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDS_ID = 'docker-hub-credentials'
        DOCKER_HUB_USERNAME = 'hasabnistejas28' // Please double-check this is your correct Docker Hub username
    }

    stages {
        stage('1. Build Backend Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_HUB_USERNAME}/s3-backend:latest ./backend'
                }
            }
        } // End of Stage 1

        stage('2. Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CREDS_ID, passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USER')]) {
                    sh 'echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USER --password-stdin'
                    sh 'docker push ${DOCKER_HUB_USERNAME}/s3-backend:latest'
                }
            }
        } // End of Stage 2

        stage('3. Deploy to EC2') {
            steps {
                // Use the 'aws-env-file' credential to create the .env file
                withCredentials([string(credentialsId: 'aws-env-file', variable: 'DOT_ENV_CONTENT')]) {
                    script {
                        echo "Deploying the application using Docker Compose..."
                        
                        // Create the .env file in the workspace from the Jenkins secret text
                        sh 'echo "$DOT_ENV_CONTENT" > .env'
                        
                        // Now run the correct docker compose commands (with a space)
                        sh 'docker compose down'
                        sh 'docker compose up --build -d'
                        
                        echo "Deployment complete!"
                    }
                } // End of withCredentials
            }
        } // End of Stage 3
    } // End of stages

    post {
        always {
            cleanWs()
            sh 'docker logout'
        }
    } // End of post
} // End of pipeline