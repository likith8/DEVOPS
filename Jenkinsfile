pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'todo-app3'
        CONTAINER_NAME = 'todo-app-container3'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                // Optional: cleans up dangling Docker resources
                sh "docker system prune -f || true"
            }
        }

        stage('Checkout') {
            steps {
                git 'https://github.com/likith8/TODO-Appl'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build --no-cache -t $DOCKER_IMAGE ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests in the Docker image using the test discovery
                    sh """
                        docker run --rm \
                        -v \$(pwd)/.env:/app/.env \
                        $DOCKER_IMAGE \
                        pytest || exit 1
                    """
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Ensure previous container is stopped
                    sh "docker rm -f $CONTAINER_NAME || true"

                    // Run the new container
                    sh """
                        docker run -d --name $CONTAINER_NAME \
                        -p 5000:5000 \
                        --memory 1g --memory-swap 1g \
                        $DOCKER_IMAGE
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
            sh "docker rm -f $CONTAINER_NAME || true"
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Please check logs."
        }
    }
}
