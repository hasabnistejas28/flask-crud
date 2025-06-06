// Jenkinsfile
pipeline {
    agent any

    environment {
        // Use Jenkins Credentials plugin to securely store your Docker Hub credentials
        // DOCKER_HUB_CREDS_ID should be the ID of your 'Username and Password' credential in Jenkins
        DOCKER_HUB_CREDS_ID = 'docker-hub-credentials' 
        DOCKER_HUB_USERNAME = 'your-dockerhub-username'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                // Clones the repository
                git branch: 'main', url: 'https://github.com/your-username/s3-file-manager.git'
            }
        }

        stage('2. Build Backend Docker Image') {
            steps {
                script {
                    // Build the image and tag it
                    sh 'docker build -t ${DOCKER_HUB_USERNAME}/s3-backend:latest ./backend'
                }
            }
        }
        
        stage('3. Push to Docker Hub') {
            steps {
                // Log in to Docker Hub and push the image
                withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CREDS_ID, passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USER')]) {
                    sh 'echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USER --password-stdin'
                    sh 'docker push ${DOCKER_HUB_USERNAME}/s3-backend:latest'
                }
            }
        }

        stage('4. Deploy to EC2') {
            steps {
                script {
                    // Ensure the .env file exists on the server before deploying
                    // This command runs on the Jenkins agent (the EC2 instance itself)
                    echo "Deploying the application using Docker Compose..."
                    sh 'docker-compose down' // Stop any running containers
                    sh 'docker-compose up --build -d' // Build and start new containers
                    echo "Deployment complete!"
                }
            }
        }
    }
    post {
        always {
            // Clean up workspace
            cleanWs()
            // Log out from Docker Hub
            sh 'docker logout'
        }
    }
}