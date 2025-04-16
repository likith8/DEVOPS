pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'todo-app'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from GitHub
                git 'https://github.com/likith8/TODO-Appl'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image
                    sh 'docker build -t $DOCKER_IMAGE .'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Run the Docker container
                    sh 'docker run -d -p 5000:5000 $DOCKER_IMAGE'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run your tests inside the container
                    sh 'docker exec -t $(docker ps -q --filter ancestor=$DOCKER_IMAGE) pytest'
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    // Stop and remove the container after tests
                    sh 'docker stop $(docker ps -q --filter ancestor=$DOCKER_IMAGE)'
                    sh 'docker rm $(docker ps -a -q --filter ancestor=$DOCKER_IMAGE)'
                }
            }
        }
    }

    post {
        always {
            // Clean up Docker images and containers after the build
            sh 'docker rmi $DOCKER_IMAGE || true'
        }
    }
}
