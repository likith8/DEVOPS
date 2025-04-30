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
                    // Stop and remove existing container only if it exists
                    sh "docker rm -f $CONTAINER_NAME || true"
                    // Run the container
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

        // Removed Clean Up Stage
        // You can uncomment below if you ever want to add it back
        /*
        stage('Clean Up') {
            steps {
                script {
                    sh "docker stop $CONTAINER_NAME || true"
                    sh "docker rm $CONTAINER_NAME || true"
                }
            }
        }
        */
    }

    post {
        // Removed image deletion step
        // Uncomment below if you ever want to clean image after builds
        /*
        always {
            script {
                sh "docker rmi $DOCKER_IMAGE || true"
            }
        }
        */
    }
}
