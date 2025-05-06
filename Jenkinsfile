pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/your-username/your-repo.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build('flask-todo-app')
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Pass the .env file to the container by mounting it
                    dockerImage.run("-p 5000:5000 --env-file .env")
                }
            }
        }

        stage('Test (Optional)') {
            steps {
                // If you have tests
                sh 'docker exec $(docker ps -q -f ancestor=flask-todo-app) pytest tests/'
            }
        }
    }

    post {
        always {
            echo "Cleaning up Docker containers..."
            sh 'docker ps -aq --filter "ancestor=flask-todo-app" | xargs -r docker stop | xargs -r docker rm'
        }
    }
}
