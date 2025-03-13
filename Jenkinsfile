pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials') // Stocké dans Jenkins
        SERVER_CREDENTIALS = credentials('ssh-server-credentials') // Stocké dans Jenkins
        DOCKER_IMAGE = "myrepo/segmentation-app"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/username/your-repo.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest tests/'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $DOCKER_IMAGE:latest ."
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry([credentialsId: 'docker-hub-credentials', url: '']) {
                    sh "docker push $DOCKER_IMAGE:latest"
                }
            }
        }

        stage('Deploy to Server') {
            steps {
                sshagent(['ssh-server-credentials']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no user@server << EOF
                    docker pull $DOCKER_IMAGE:latest
                    docker stop segmentation-app || true
                    docker rm segmentation-app || true
                    docker run -d --name segmentation-app -p 5005:5005 $DOCKER_IMAGE:latest
                    EOF
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Déploiement réussi !'
        }
        failure {
            echo '❌ Échec du pipeline.'
        }
    }
}
