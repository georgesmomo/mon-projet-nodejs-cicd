pipeline {
    agent any // Nous allons affiner cela. Pour l'instant, n'importe quel agent disponible fera l'affaire.

    environment {
        // Variables d'environnement non secrètes
        REGISTRY_URL_NEXUS = '167.86.118.59:32772'
        REGISTRY_URL_JFROG = 'trial29h9yf.jfrog.io'
        APP_NAME = 'node-hello-world'
    }

    stages {
        stage('Checkout') {
            steps {
                // Cette étape récupère le code source depuis le SCM (Source Control Management) configuré dans le job Jenkins.
                checkout scm
            }
        }
        // D'autres étapes viendront s'ajouter ici.
        stage('Unit Tests') {
            agent {
                docker {
                    image 'node:18-slim'
                }
            }
            environment {
                // Répertoire local pour le cache npm (évite les erreurs de permission)
                npm_config_cache = "${env.WORKSPACE}/.npm"
            }
            steps {
                script {
                    // Nettoyage avant installation
                    sh 'rm -rf node_modules package-lock.json'
                    sh 'mkdir -p $npm_config_cache'

                    // Installation des dépendances
                    sh 'npm install --prefer-offline --no-audit'

                    // Exécution des tests avec options pour debug
                    sh 'npm test -- --detectOpenHandles --verbose'
                }
            }
        }


    stage('SonarQube Analysis & Quality Gate') {
        steps {
            // Le nom 'MySonarQubeServer' doit correspondre à celui configuré dans Administrer Jenkins -> System
            withSonarQubeEnv('SonarScanner') {
                script {
                    // Le nom 'SonarScanner' doit correspondre à celui configuré dans Administrer Jenkins -> Tools
                    def scannerHome = tool 'SonarScanner'
                    withVault([
                        vaultSecrets: [
                            [path: 'secret/devops/jenkins', engineVersion: 2, secretValues: [
                                [envVar: 'MY_SECRET_USERNAME', vaultKey: 'username'],
                                [envVar: 'MY_SECRET_PASSWORD', vaultKey: 'password']
                            ]]
                        ],
                        vaultCredentialId: 'vault-approle-creds'
                    ]){
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
            // Mettre en pause le pipeline en attendant le résultat de la Quality Gate
            timeout(time: 1, unit: 'HOURS') {
                waitForQualityGate abortPipeline: true
            }
        }
    }
    //... après le stage 'SonarQube Analysis'
    stage('Build & Scan Image') {
        steps {
            script {
                // Installation de Trivy si nécessaire (peut être pré-installé sur l'agent)
                 sh 'sudo apt-get update && sudo apt-get install -y wget apt-transport-https gnupg lsb-release'
                 sh 'wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -'
                 sh 'echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/trivy.list'
                 sh 'sudo apt-get update && sudo apt-get install -y trivy'

                def shortCommit = env.GIT_COMMIT.take(7)
                // Pour une build sur la branche 'develop'
                def imageTag = "1.0.0-develop.${env.BUILD_NUMBER}.${shortCommit}"
                
                // Stocker dans l'environnement pour les étapes suivantes
                env.IMAGE_FULL_NAME = "${env.APP_NAME}:${imageTag}"

                // Construire l'image Docker
                docker.build(env.IMAGE_FULL_NAME, ".")

                // Scanner l'image avec Trivy. --exit-code 1 fait échouer le build si des vulnérabilités sont trouvées.
                sh "trivy image --exit-code 1 --severity HIGH,CRITICAL ${env.IMAGE_FULL_NAME}"
            }
        }
    }
    //... après le stage 'Build & Scan Image'
    stage('Publish Artifact') {
        steps {
            withVault([
                vaultSecrets: [
                    [path: 'secret/data/jenkins', engineVersion: 2, secretValues: [
                        [envVar: 'DB_USER', vaultKey: 'username'],
                        [envVar: 'DB_PASS', vaultKey: 'password']
                    ]]
                ],
                vaultCredentialId: 'vault-approle-creds'
            ]){
                script {
                    // --- Pousser vers JFrog Artifactory ---
                    def jfrogImageName = "${env.REGISTRY_URL_JFROG}/${env.APP_NAME}/${env.IMAGE_FULL_NAME.split(':')}"
                    docker.withRegistry("https://${env.REGISTRY_URL_JFROG}", "jfrog-creds") { // 'jfrog-creds' doit être un credential Jenkins de type Username/Password
                        sh "docker tag ${env.IMAGE_FULL_NAME} ${jfrogImageName}"
                        sh "docker push ${jfrogImageName}"
                    }

                    // --- Pousser vers Nexus ---
                    // docker.withRegistry est la méthode préférée. Elle nécessite un credential Jenkins.
                    // Nous allons créer un credential 'nexus-creds' dans Jenkins qui utilise les variables de Vault.
                    // Alternativement, on peut utiliser docker login en shell.
                    def nexusImageName = "${env.REGISTRY_URL_NEXUS}/${env.IMAGE_FULL_NAME}"
                    withCredentials() {
                        sh "echo ${env.NEXUS_PASS_CRED} | docker login ${env.REGISTRY_URL_NEXUS} -u ${env.NEXUS_USER_CRED} --password-stdin"
                        sh "docker tag ${env.IMAGE_FULL_NAME} ${nexusImageName}"
                        sh "docker push ${nexusImageName}"
                        sh "docker logout ${env.REGISTRY_URL_NEXUS}"
                    }
                }
            }
        }
    }

    //... après le stage 'Publish Artifact!'
    stage('Trigger CD') {
        steps {
            script {
                // Nous avons besoin de credentials pour pousser vers le dépôt de configuration !!
                withCredentials() {
                    
                    // Cloner le dépôt de configuration
                    sh "git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/${GIT_USER}/mon-projet-k8s-config.git"
                    
                    // Se déplacer dans le dépôt cloné
                    dir('mon-projet-k8s-config') {
                        // Configurer git
                        sh "git config user.name 'georgesmomo'"
                        sh "git config user.email 'jenkins@example.com'"

                        // Installer yq si nécessaire
                        sh "wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O./yq && chmod +x./yq"

                        // Mettre à jour la tag de l'image dans values.yaml
                        sh "./yq e '.image.tag = \"${env.IMAGE_FULL_NAME.split(':')}\"' -i my-chart/values.yaml"
                        
                        // Commiter et pousser les changements
                        sh "git add my-chart/values.yaml"
                        sh "git commit -m 'ci: Update image tag to ${env.IMAGE_FULL_NAME.split(':')}'"
                        sh "git push"
                    }
                }
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
                //sh "docker container prune -f || true"
                //sh "docker image prune -f || true"
                //sh "docker volume prune -f || true"
            }
        }
    }
    
}