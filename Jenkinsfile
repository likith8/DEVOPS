pipeline {
    agent any

    environment {
        FLASK_ENV = 'production'
        MONGO_URI = credentials('mongo-uri')  // Store your Mongo URI in Jenkins Credentials
        SECRET_KEY = credentials('flask-secret-key')  // Store your secret key safely
    }

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
                    dockerImage.run("-e FLASK_ENV=${FLASK_ENV} -e MONGO_URI=${MONGO_URI} -e SECRET_KEY=${SECRET_KEY} -p 5000:5000")
                }
            }
        }

        stage('Test (Optional)') {
            steps {
                // Only if you have unit tests
                sh 'docker exec $(docker ps -q -f ancestor=flask-todo-app) pytest tests/'
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
            sh 'docker ps -aq --filter "ancestor=flask-todo-app" | xargs -r docker stop | xargs -r docker rm'
        }
    }
}
