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
                    // Ensure Docker image is built correctly and without cache
                    sh "docker build --no-cache -t $DOCKER_IMAGE ."
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Clean up any previous containers
                    sh "docker rm -f $CONTAINER_NAME || true"
                    // Run container with resource limits to avoid OOM (Out of Memory)
                    sh """
                        docker run -d --name $CONTAINER_NAME \
                        -p 5000:5000 \
                        --memory 1g --memory-swap 1g \
                        $DOCKER_IMAGE
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests and ensure containers exit with proper status
                    sh """
                        docker exec $CONTAINER_NAME pytest || exit 1
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
            // Remove container after execution
            sh "docker rm -f $CONTAINER_NAME || true"
        }
        success {
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Pipeline failed, check the logs above."
        }
    }
}
