// Fichier: Jenkinsfile

pipeline {
    // Fait tourner le pipeline sur n'importe quel agent Jenkins disponible
    agent any

    // Variables d'environnement utilisées dans le pipeline
    environment {
        // L'URL de ton SonarQube (à adapter si besoin)
        SONARQUBE_URL = 'http://167.86.118.59:32771/' 
        // L'URL de ton registry Docker JFrog
        JFROG_REGISTRY = 'trial29h9yf.jfrog.io'
        // Le nom de ton dépôt Docker dans JFrog (doit exister)
        JFROG_DOCKER_REPO = 'docker-trial' 
        // Le nom de notre image Docker
        IMAGE_NAME = "node-express-hello-world"
    }

    stages {
        // =================================================================
        // PHASE 1 : Intégration Continue (CI)
        // =================================================================

        stage('1. Checkout Code') {
            steps {
                script {
                    echo 'Récupération du code depuis GitHub...'
                    // Utilise le credential 'github-token' pour se connecter
                    git credentialsId: 'github-token', url: 'https://github.com/georgesmomo/node-express-hello-world.git', branch: 'master'
                }
            }
        }

        stage('2. SonarQube Code Analysis') {
            steps {
                script {
                    echo 'Analyse du code avec SonarQube...'
                    // Prépare l'environnement SonarQube avec le token
                    withSonarQubeEnv(credentialsId: 'sonarqube-token') {
                        // Utilise l'outil 'SonarScanner-latest' qu'on a configuré dans Jenkins
                        def sonarScanner = tool 'SonarScanner'
                        // Lance l'analyse
                        sh "${sonarScanner}/bin/sonar-scanner -Dsonar.projectKey=node-express-hello-world -Dsonar.sources=. -Dsonar.host.url=${SONARQUBE_URL}"
                    }
                }
            }
        }

        stage('3. Build Docker Image') {
            steps {
                script {
                    echo "Construction de l'image Docker..."
                    // Construit l'image et la tague avec le numéro de build Jenkins (ex: hello-world-app:1)
                    sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                }
            }
        }

        // =================================================================
        // PHASE 2 : Déploiement Continu (CD)
        // =================================================================
        
        stage('4. Push Image to JFrog Artifactory') {
            steps {
                script {
                    echo "Envoi de l'image vers JFrog Artifactory..."
                    
                    // On se connecte à JFrog en utilisant les identifiants stockés
                    withCredentials([usernamePassword(credentialsId: 'jfrog-credentials', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                        sh "docker login -u ${JFROG_USER} -p ${JFROG_PASS} ${JFROG_REGISTRY}"
                    }
                    
                    // On tague l'image avec le nom complet du registry pour savoir où la pousser
                    def fullImageName = "${JFROG_REGISTRY}/${JFROG_DOCKER_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    sh "docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${fullImageName}"

                    // On pousse l'image
                    sh "docker push ${fullImageName}"

                    // On se déconnecte pour ne pas laisser de session ouverte
                    sh "docker logout ${JFROG_REGISTRY}"
                }
            }
        }

        stage('5. JFrog Xray Scan') {
            steps {
                echo "L'analyse de sécurité Xray est déclenchée automatiquement par JFrog."
                echo "Consulte l'interface JFrog pour voir les résultats."
                // Note : Pour une intégration avancée, on utiliserait le plugin JFrog pour attendre le résultat du scan.
            }
        }

        stage('6. Deploy to Production VPS') {
            steps {
                script {
                    echo "Déploiement de l'application sur le VPS..."
                    def fullImageName = "${JFROG_REGISTRY}/${JFROG_DOCKER_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    
                    // Connexion à JFrog pour pouvoir tirer l'image
                    withCredentials([usernamePassword(credentialsId: 'jfrog-credentials', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                        sh "docker login -u ${JFROG_USER} -p ${JFROG_PASS} ${JFROG_REGISTRY}"
                    }

                    // Arrête et supprime l'ancien conteneur s'il existe (le '|| true' évite une erreur si le conteneur n'existe pas)
                    sh "docker stop node-express-hello-world || true"
                    sh "docker rm node-express-hello-world || true"
                    
                    // Tire la nouvelle image depuis JFrog
                    sh "docker pull ${fullImageName}"

                    // Lance le nouveau conteneur
                    sh "docker run -d --name node-express-hello-world -p 3000:3000 ${fullImageName}"

                    sh "docker logout ${JFROG_REGISTRY}"
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Nettoyage automatique (post build)...!!!!"

                // Nettoyer le workspace Jenkins
                cleanWs()

                // Nettoyage Docker si nécessaire
                sh "docker container prune -f || true"
                sh "docker image prune -f || true"
                sh "docker volume prune -f || true"
            }
        }
    }
}