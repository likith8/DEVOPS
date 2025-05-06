pipeline {
    agent any

    environment {
        FLASK_ENV = 'testing'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'venv\\Scripts\\activate && pytest tests/'
            }
        }
    }
}
