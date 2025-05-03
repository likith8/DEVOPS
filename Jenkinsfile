pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'todo-app3'
        CONTAINER_NAME = 'todo-app-container3'
    }

    stages {
        stage('Clean Jenkins Workspace') {
            steps {
                // Clean Jenkins workspace to free up disk space
                cleanWs()
            }
        }

        stage('Clean Docker Resources') {
            steps {
                // Optional: cleans up unused Docker resources and volumes
                sh "docker system prune -af --volumes || true"
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
                    // Run tests inside Docker, pass .env into container
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
                    // Stop and remove old container if exists
                    sh "docker rm -f $CONTAINER_NAME || true"

                    // Run the new container with resource limits
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
            echo "🧹 Cleaning up container..."
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
