pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDS_ID = 'docker-hub-credentials'
        DOCKER_HUB_USERNAME = 'hasabnistejas' // Make sure this is your Docker Hub username
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
                // Use the 'aws-env-file' credential
                withCredentials([string(credentialsId: 'aws-env-file', variable: 'DOT_ENV_CONTENT')]) {
                    script {
                        echo "Deploying the application using Docker Compose..."
                        // Create the .env file in the workspace from the secret text
                        sh 'echo "$DOT_ENV_CONTENT" > .env'
                        
                        // Now run the docker-compose commands
                        sh 'docker-compose down'
                        sh 'docker-compose up --build -d'
                        echo "Deployment complete!"
                    }
                } // This closing brace for withCredentials might have been missed
            }
        } // This closing brace for the stage might have been missed
    } // This closing brace for stages might have been missed

    post {
        always {
            cleanWs()
            sh 'docker logout'
        }
    }
} // This is the final closing brace for the pipeline