pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'todo-app3'
        CONTAINER_NAME = 'todo-app-container3'
        MONGO_URI = credentials('MONGO_URI')         // Jenkins credential ID
        SECRET_KEY = credentials('SECRET_KEY')       // Jenkins credential ID
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

                    sh """
                        docker run -d --name $CONTAINER_NAME \
                        -e MONGO_URI=$MONGO_URI \
                        -e SECRET_KEY=$SECRET_KEY \
                        -p 5000:5000 $DOCKER_IMAGE
                    """
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
    }
}
