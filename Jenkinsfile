pipeline {
    agent any // Nous allons affiner cela. Pour l'instant, n'importe quel agent disponible fera l'affaire.

    environment {
        // Variables d'environnement non secrètes
        REGISTRY_URL_NEXUS = 'http://167.86.118.59:32772'
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
                    //sh 'npm install --prefer-offline --no-audit'

                    // Exécution des tests avec options pour debug
                    //sh 'npm test -- --detectOpenHandles --verbose'
                }
            }
        }

   stage('Fluffy Test - TO_DELETE') {
      parallel {
        stage('Backend') {
          steps {
            echo "Backend ..."
          }
        }
        stage('Frontend') {
          steps {
          echo "Frontend ..."
          }
        }
        stage('Performance') {
          steps {
            echo "Performance ..."
          }
        }
        stage('Static') {
          steps {
            echo "Static ..."
          }
        }
      }
    }

    stage('SonarQube Analysis & Quality Gate') {
        steps {
            withSonarQubeEnv('SonarScanner') {
                script {
                    def scannerHome = tool 'SonarScanner'

                   /* withVault([
                        vaultSecrets: [
                            [path: 'secret/secret/devops/sonarqube', engineVersion: 2, secretValues: [
                                [envVar: 'SONAR_TOKEN', vaultKey: 'token']
                            ]]
                        ],
                        vaultCredentialId: 'vault-approle-creds'
                    ]) {
                        sh """
                            ${scannerHome}/bin/sonar-scanner -Dsonar.login=${SONAR_TOKEN} || true
                        """
                    } */
                }
            }

            timeout(time: 1, unit: 'HOURS') {
                //si à true, le test tombe en echec si qualitygate est pas bon
                //waitForQualityGate abortPipeline: false
            }
        }
    }

    //... après le stage 'SonarQube Analysis'
    stage('Build & Scan Image') {
        steps {
            script {
                // Installation de Trivy si nécessaire (peut être pré-installé sur l'agent, normalement à installer via ansible par exemple)
                // sh 'sudo apt-get update && sudo apt-get install -y wget apt-transport-https gnupg lsb-release'
                // sh 'wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -'
                // sh 'echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/trivy.list'
                // sh 'sudo apt-get update && sudo apt-get install -y trivy'

                def shortCommit = env.GIT_COMMIT.take(7)
                // Pour une build sur la branche 'develop'
                def imageTag = "1.0.0-develop.${env.BUILD_NUMBER}.${shortCommit}"
                
                // Stocker dans l'environnement pour les étapes suivantes
                env.IMAGE_FULL_NAME = "${env.APP_NAME}:${imageTag}"

                // Construire l'image Docker
                docker.build(env.IMAGE_FULL_NAME, ".")

                // Scanner l'image avec Trivy. --exit-code 1 fait échouer le build si des vulnérabilités sont trouvées. et 0 non
                sh "trivy image --exit-code 0 --severity HIGH,CRITICAL ${env.IMAGE_FULL_NAME} || true"
            }
        }
    }
    stage('Publish Artifact') {
        steps {
            script {
                echo "⏬ Début du stage Publish Artifact"

                try {
                    withVault([
                        vaultSecrets: [
                            [path: 'secret/secret/devops/jfrog', engineVersion: 2, secretValues: [
                                [envVar: 'JFROG_USER', vaultKey: 'user'],
                                [envVar: 'JFROG_PASS', vaultKey: 'password']
                            ]],
                            [path: 'secret/secret/devops/nexus', engineVersion: 2, secretValues: [
                                [envVar: 'NEXUS_USER', vaultKey: 'user'],
                                [envVar: 'NEXUS_PASS', vaultKey: 'password']
                            ]],
                            [path: 'secret/secret/devops/dockerhub', engineVersion: 2, secretValues: [
                                [envVar: 'DOCKERHUB_USER', vaultKey: 'user'],
                                [envVar: 'DOCKERHUB_PASS', vaultKey: 'password']
                            ]]
                        ],
                        vaultCredentialId: 'vault-approle-creds'
                    ]) {

                        echo "🔐 Secrets JFrog, Nexus et Docker Hub récupérés via Vault"

                        // --- JFrog Artifactory ---
                        /*def jfrogImageName = "${env.REGISTRY_URL_JFROG}/${env.APP_NAME}/${env.IMAGE_FULL_NAME.split(':')[0]}:${env.IMAGE_FULL_NAME.split(':')[1]}"
                        echo "📦 JFrog Image Name: ${jfrogImageName}"

                        sh """
                            echo ${JFROG_PASS} | docker login ${env.REGISTRY_URL_JFROG} -u ${JFROG_USER} --password-stdin
                            docker tag ${env.IMAGE_FULL_NAME} ${jfrogImageName}
                            docker push ${jfrogImageName}
                            docker logout ${env.REGISTRY_URL_JFROG}
                        """*/


                        // --- Docker Hub ---
                        def dockerhubImageName = "${DOCKERHUB_USER}/${env.IMAGE_FULL_NAME}"
                        echo "📦 Docker Hub Image Name: ${dockerhubImageName}"

                      /*  sh """
                            echo ${DOCKERHUB_PASS} | docker login -u ${DOCKERHUB_USER} --password-stdin
                            docker tag ${env.IMAGE_FULL_NAME} ${dockerhubImageName}
                            docker push ${dockerhubImageName}
                            docker logout
                        """

                        echo "✅ Artifact publié sur JFrog, Nexus et Docker Hub avec succès"

                        // --- Nexus Registry ---
                        def nexusImageName = "${env.REGISTRY_URL_NEXUS}/${env.IMAGE_FULL_NAME}"
                        echo "📦 Nexus Image Name: ${nexusImageName}"

                        sh """
                            echo ${NEXUS_PASS} | docker login ${env.REGISTRY_URL_NEXUS} -u ${NEXUS_USER} --password-stdin
                            docker tag ${env.IMAGE_FULL_NAME} ${nexusImageName}
                            docker push ${nexusImageName}
                            docker logout ${env.REGISTRY_URL_NEXUS}
                        """
                    */
                    }

                } catch (Exception e) {
                    echo "❌ Erreur lors du stage Publish Artifact: ${e.message}"
                    currentBuild.result = 'UNSTABLE'
                }
            }
        }
    }


    //... après le stage 'Publish Artifact!'
stage('Trigger CD') {
    steps {
        script {
            withCredentials([
                usernamePassword(credentialsId: 'GITHUB_CREDENTIALS_DEVOPS', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')
            ]) {

                echo "Git url: https://${GIT_USER}:${GIT_TOKEN}@github.com/${GIT_USER}/mon-projet-k8s-config.git"
                // Cloner le dépôt de configuration
                sh "git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/${GIT_USER}/mon-projet-k8s-config.git"

                dir('mon-projet-k8s-config') {
                    // Configurer git
                    sh "git config user.name 'georgesmomo'"
                    sh "git config user.email 'georgesmomo@users.noreply.github.com'"

                    // Télécharger yq si nécessaire
                    sh "wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O ./yq && chmod +x ./yq"

                    // Mettre à jour le tag de l'image dans values.yaml !
                    def tag = env.IMAGE_FULL_NAME.split(':')[1]
                    sh "./yq e '.image.tag = \"${tag}\"' -i my-chart/values.yaml"

                    // Commit et push
                    sh "git add my-chart/values.yaml"
                    sh "git commit -m 'ci: Update image tag to ${tag}'"
                    sh "git push"
                }
            }
        }
    }
}

stage('E2E Tests') {
    agent {
        docker {
            image 'python:3.9-slim'
        }
    }
    steps {
        script {
            sh '''
                # Créer un environnement virtuel local (pas besoin de pip install virtualenv)
                python3 -m venv venv

                # Activer l’environnement
                . venv/bin/activate

                # Upgrade pip dans l'environnement virtuel uniquement
                pip install --upgrade pip

                # Installer selenium localement dans le venv
                pip install selenium

                # Vérification
                pip show selenium

                # Lancer les tests E2E
                python e2e_test.py
            '''
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
