pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'todo-app3'
        CONTAINER_NAME = 'todo-app-container3'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/likith8/TODO-Appl'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t $DOCKER_IMAGE ."
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Stop and remove any existing container with the same name
                    sh "docker rm -f $CONTAINER_NAME || true"
                    // Run a new container
                    sh "docker run -d --name $CONTAINER_NAME -p 5000:5000 $DOCKER_IMAGE"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests inside the running container
                    sh "docker exec $CONTAINER_NAME pytest || true"
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    // Stop and remove the container
                    sh "docker stop $CONTAINER_NAME || true"
                    sh "docker rm $CONTAINER_NAME || true"
                }
            }
        }
    }

    post {
        always {
            // Optionally remove Docker image (if needed)
            script {
                sh "docker rmi $DOCKER_IMAGE || true"
            }
        }
    }
}
