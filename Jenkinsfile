    // Modular CI Template (Repo-Root): modules.json → Packages + Services, Tree-Tags, partieller Build
    // Skripte: scripts/ci_*.py (Python 3.11+)

    pipeline {
        agent any

        options {
            timestamps()
            timeout(time: 60, unit: 'MINUTES')
        }

        stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }

            stage('Fetch git tags') {
                steps {
                    sh '''
                        set -e
                        git remote get-url origin >/dev/null 2>&1 && git fetch origin --tags --force || git fetch --tags --force || true
                        git tag -l 'v*' | tail -5 || true
                    '''
                }
            }

            stage('Resolve version & tree') {
                steps {
                    sh '''
                        set -e
                        python3.11 scripts/ci_resolve_version.py
                        . ./.jenkins_runtime.env
                        echo "SOFTWARE_VERSION=${SOFTWARE_VERSION}"
                    '''
                }
            }

            stage('Build plan') {
                steps {
                    sh '''
                        set -e
                        python3.11 scripts/ci_build_plan.py
                        cat .jenkins_skip_pipeline || true
                    '''
                }
            }

            stage('Cleanup containers') {
                when {
                    expression {
                        return !fileExists('.jenkins_skip_pipeline') || readFile('.jenkins_skip_pipeline').trim() != 'true'
                    }
                }
                steps {
                    sh '''
                        docker container stop $(docker container ls -aq) 2>/dev/null || true
                        docker container rm $(docker container ls -aq) 2>/dev/null || true
                    '''
                }
            }

            stage('Generate Dockerfile') {
                when {
                    expression {
                        return !fileExists('.jenkins_skip_pipeline') || readFile('.jenkins_skip_pipeline').trim() != 'true'
                    }
                }
                steps {
                    sh '''
                        set -e
                        python3.11 scripts/ci_generate_dockerfile.py
                    '''
                }
            }

            stage('AWS ECR Login') {
                steps {
                    sh '''
                        set -e
                        aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-central-1.amazonaws.com
                    '''
                }
            }

            stage('Docker build (selective)') {
                when {
                    expression {
                        return !fileExists('.jenkins_skip_pipeline') || readFile('.jenkins_skip_pipeline').trim() != 'true'
                    }
                }
                steps {
                    sh '''
                        set -e
                        python3.11 scripts/ci_docker_build.py
                    '''
                }
            }

            stage('AWS ECR push') {
                when {
                    expression {
                        return !fileExists('.jenkins_skip_pipeline') || readFile('.jenkins_skip_pipeline').trim() != 'true'
                    }
                }
                steps {
                    sh '''
                        set -e
                        . ./.jenkins_runtime.env
                        . ./.jenkins_build_plan.env
                        python3.11 scripts/ci_docker_push.py
                    '''
                }
            }

            stage('Deploy Lambda') {
                when {
                    expression {
                        return !fileExists('.jenkins_skip_pipeline') || readFile('.jenkins_skip_pipeline').trim() != 'true'
                    }
                }
                steps {
                    sh '''
                        set -e
                        . ./.jenkins_runtime.env
                        # Assuming ECR_IMAGE_URI is constructed from registry and image name
                        # You can customize this based on how you want to target the specific Lambda image
                        export LAMBDA_ROLE_ARN="arn:aws:iam::423623826655:instance-profile/jenkins-deployment-role"
                        export ECR_IMAGE_URI="423623826655.dkr.ecr.eu-central-1.amazonaws.com/dflowp/news-archive-lambda:latest"
                        pip3 install boto3
                        python3.11 scripts/deploy_lambda.py
                    '''
                }
            }
        }

        post {
            success {
                script {
                    if (fileExists('.jenkins_skip_pipeline') && readFile('.jenkins_skip_pipeline').trim() == 'true') {
                        echo '=== SKIP: Stack entspricht bereits den erwarteten Tree-Tags. ==='
                    }
                }
            }
        }
    }
