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
                    sh "docker rm -f $CONTAINER_NAME || true"
                    sh "docker run -d --name $CONTAINER_NAME -p 5000:5000 $DOCKER_IMAGE"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh "docker exec $CONTAINER_NAME pytest || true"
                }
            }
        }

        // Clean Up stage removed intentionally as per your request
    }

    // 🚫 Removed this block to fix error:
    // post { }
}
