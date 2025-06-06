pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDS_ID = 'docker-hub-credentials'
        DOCKER_HUB_USERNAME = 'hasabnistejas' // Please ensure this is your correct Docker Hub username
    }

    stages {
        stage('1. Build Backend Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_HUB_USERNAME}/s3-backend:latest ./backend'
                }
            }
        }

        stage('2. Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CREDS_ID, passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USER')]) {
                    sh 'echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USER --password-stdin'
                    sh 'docker push ${DOCKER_HUB_USERNAME}/s3-backend:latest'
                }
            }
        }

        stage('3. Deploy to EC2') {
            steps {
                withCredentials([string(credentialsId: 'aws-env-file', variable: 'DOT_ENV_CONTENT')]) {
                    script {
                        echo "Deploying the application using Docker Compose..."
                        
                        // Create the .env file in the workspace from the Jenkins secret text
                        sh 'echo "$DOT_ENV_CONTENT" > .env'
                        
                        // Grant read/execute permissions to the frontend folder for Nginx
                        sh 'chmod -R 755 frontend'
                        
                        // Now run the correct docker compose commands (with a space)
                        sh 'docker compose down'
                        sh 'docker compose up --build -d'
                        
                        echo "Deployment complete!"
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up the workspace after the build
            cleanWs()
            // Log out from Docker Hub
            sh 'docker logout'
        }
    }
}