pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        HOOKS_DIRECTORY = 'core/hooks'
        TEST_TIMEOUT_MINUTES = '30'
        VENV_PATH = '.venv'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 2, unit: 'HOURS')
        retry(1)
        skipStagesAfterUnstable()
    }
    
    triggers {
        // Poll SCM every 15 minutes during work hours
        pollSCM('H/15 6-18 * * 1-5')
        
        // Run nightly comprehensive tests
        cron('H 2 * * *')
    }
    
    parameters {
        choice(
            name: 'TEST_FILTER',
            choices: ['all', 'smoke', 'performance', 'regression'],
            description: 'Type of tests to run'
        )
        booleanParam(
            name: 'UPDATE_BASELINES',
            defaultValue: false,
            description: 'Update performance baselines'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: 'Enable parallel test execution'
        )
    }
    
    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    // Clean workspace
                    cleanWs()
                    
                    // Checkout code
                    checkout scm
                    
                    // Setup Python virtual environment
                    sh """
                        python${env.PYTHON_VERSION} -m venv ${env.VENV_PATH}
                        . ${env.VENV_PATH}/bin/activate
                        pip install --upgrade pip setuptools wheel
                    """
                    
                    // Install dependencies
                    sh """
                        . ${env.VENV_PATH}/bin/activate
                        cd ${env.HOOKS_DIRECTORY}
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-html pytest-json-report
                    """
                }
            }
        }
        
        stage('Code Quality Checks') {
            parallel {
                stage('Lint Code') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}
                            flake8 --max-line-length=120 --ignore=E203,W503 . || true
                            pylint --rcfile=.pylintrc . || true
                        """
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tools: [
                                flake8(pattern: '**/flake8.log'),
                                pyLint(pattern: '**/pylint.log')
                            ]
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}
                            bandit -r . -f json -o bandit-report.json || true
                            safety check --json --output safety-report.json || true
                        """
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '**/bandit-report.json,**/safety-report.json', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Dependency Check') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}
                            pip-audit --format=json --output=pip-audit-report.json || true
                        """
                    }
                }
            }
        }
        
        stage('Smoke Tests') {
            steps {
                script {
                    sh """
                        . ${env.VENV_PATH}/bin/activate
                        cd ${env.HOOKS_DIRECTORY}/tests
                        python -m pytest test_pytest_integration.py -m smoke \\
                            --timeout=60 \\
                            --junit-xml=smoke_results.xml \\
                            --html=smoke_report.html \\
                            --json-report --json-report-file=smoke_report.json \\
                            --cov=../ --cov-report=xml:smoke_coverage.xml \\
                            -v
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/smoke_results.xml"
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${env.HOOKS_DIRECTORY}/tests",
                        reportFiles: 'smoke_report.html',
                        reportName: 'Smoke Test Report'
                    ])
                }
            }
        }
        
        stage('Core Tests') {
            when {
                anyOf {
                    params.TEST_FILTER == 'all'
                    params.TEST_FILTER == 'smoke'
                }
            }
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}/tests
                            python -m pytest test_pytest_integration.py -m unit \\
                                --timeout=300 \\
                                --junit-xml=unit_results.xml \\
                                --html=unit_report.html \\
                                --json-report --json-report-file=unit_report.json \\
                                --cov=../ --cov-report=xml:unit_coverage.xml \\
                                ${params.PARALLEL_EXECUTION ? '-n auto' : ''} \\
                                -v
                        """
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/unit_results.xml"
                        }
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}/tests
                            python -m pytest test_pytest_integration.py -m integration \\
                                --timeout=600 \\
                                --junit-xml=integration_results.xml \\
                                --html=integration_report.html \\
                                --json-report --json-report-file=integration_report.json \\
                                --cov=../ --cov-report=xml:integration_coverage.xml \\
                                -v
                        """
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/integration_results.xml"
                        }
                    }
                }
            }
        }
        
        stage('Advanced Tests') {
            when {
                anyOf {
                    params.TEST_FILTER == 'all'
                    params.TEST_FILTER == 'performance'
                    triggeredBy 'TimerTrigger'
                }
            }
            parallel {
                stage('Performance Tests') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}/tests
                            python -m pytest test_pytest_integration.py -m performance \\
                                --timeout=1800 \\
                                --junit-xml=performance_results.xml \\
                                --html=performance_report.html \\
                                --json-report --json-report-file=performance_report.json \\
                                -v
                        """
                        
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}/tests
                            python test_runner.py --mode ci --filter performance \\
                                --junit-xml performance_framework_results.xml \\
                                --html-report performance_framework_report.html
                        """
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/performance_*.xml"
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: "${env.HOOKS_DIRECTORY}/tests",
                                reportFiles: 'performance_framework_report.html',
                                reportName: 'Performance Test Report'
                            ])
                        }
                    }
                }
                
                stage('Concurrency Tests') {
                    steps {
                        sh """
                            . ${env.VENV_PATH}/bin/activate
                            cd ${env.HOOKS_DIRECTORY}/tests
                            python -m pytest test_pytest_integration.py -m concurrency \\
                                --timeout=900 \\
                                --junit-xml=concurrency_results.xml \\
                                --html=concurrency_report.html \\
                                --json-report --json-report-file=concurrency_report.json \\
                                --cov=../ --cov-report=xml:concurrency_coverage.xml \\
                                -v
                        """
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/concurrency_results.xml"
                        }
                    }
                }
            }
        }
        
        stage('Regression Tests') {
            when {
                anyOf {
                    params.TEST_FILTER == 'all'
                    params.TEST_FILTER == 'regression'
                    branch 'main'
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                sh """
                    . ${env.VENV_PATH}/bin/activate
                    cd ${env.HOOKS_DIRECTORY}/tests
                    python -m pytest test_pytest_integration.py -m regression \\
                        --timeout=1200 \\
                        --junit-xml=regression_results.xml \\
                        --html=regression_report.html \\
                        --json-report --json-report-file=regression_report.json \\
                        --cov=../ --cov-report=xml:regression_coverage.xml \\
                        -v
                """
            }
            post {
                always {
                    publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/regression_results.xml"
                }
            }
        }
        
        stage('Comprehensive Test Framework') {
            when {
                anyOf {
                    params.TEST_FILTER == 'all'
                    branch 'main'
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                sh """
                    . ${env.VENV_PATH}/bin/activate
                    cd ${env.HOOKS_DIRECTORY}/tests
                    python test_runner.py --mode ci \\
                        --junit-xml comprehensive_results.xml \\
                        --html-report comprehensive_report.html \\
                        --required-pass-rate 85.0 \\
                        --parallel-suites 3 \\
                        --parallel-tests 8 \\
                        --timeout 60 \\
                        ${params.UPDATE_BASELINES ? '--update-baselines' : ''}
                """
            }
            post {
                always {
                    publishTestResults testResultsPattern: "${env.HOOKS_DIRECTORY}/tests/comprehensive_results.xml"
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${env.HOOKS_DIRECTORY}/tests",
                        reportFiles: 'comprehensive_report.html',
                        reportName: 'Comprehensive Test Report'
                    ])
                }
            }
        }
        
        stage('Coverage Analysis') {
            steps {
                sh """
                    . ${env.VENV_PATH}/bin/activate
                    cd ${env.HOOKS_DIRECTORY}/tests
                    
                    # Combine coverage reports
                    coverage combine || true
                    coverage xml -o combined_coverage.xml || true
                    coverage html -d coverage_html || true
                    coverage report --format=text > coverage_report.txt || true
                """
            }
            post {
                always {
                    publishCoverage adapters: [coberturaAdapter('**/combined_coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${env.HOOKS_DIRECTORY}/tests/coverage_html",
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
    
    post {
        always {
            // Archive test artifacts
            archiveArtifacts artifacts: """
                ${env.HOOKS_DIRECTORY}/tests/*.xml,
                ${env.HOOKS_DIRECTORY}/tests/*.html,
                ${env.HOOKS_DIRECTORY}/tests/*.json,
                ${env.HOOKS_DIRECTORY}/tests/test_reports/**/*,
                ${env.HOOKS_DIRECTORY}/tests/coverage_html/**/*
            """, allowEmptyArchive: true
            
            // Clean up virtual environment
            sh "rm -rf ${env.VENV_PATH}"
        }
        
        success {
            script {
                // Send success notification
                if (env.BRANCH_NAME == 'main' || params.TEST_FILTER == 'all') {
                    slackSend(
                        channel: '#ci-cd',
                        color: 'good',
                        message: """
                            ✅ Hook Test Framework Pipeline Successful
                            Branch: ${env.BRANCH_NAME}
                            Build: ${env.BUILD_NUMBER}
                            Test Filter: ${params.TEST_FILTER}
                        """
                    )
                }
            }
        }
        
        failure {
            script {
                // Send failure notification
                slackSend(
                    channel: '#ci-cd',
                    color: 'danger',
                    message: """
                        ❌ Hook Test Framework Pipeline Failed
                        Branch: ${env.BRANCH_NAME}
                        Build: ${env.BUILD_NUMBER}
                        Test Filter: ${params.TEST_FILTER}
                        Console: ${env.BUILD_URL}console
                    """
                )
                
                // Email notification for main branch failures
                if (env.BRANCH_NAME == 'main') {
                    emailext(
                        subject: "Hook Test Framework Pipeline Failed - Build ${env.BUILD_NUMBER}",
                        body: """
                            The Hook Test Framework pipeline has failed on the main branch.
                            
                            Build: ${env.BUILD_NUMBER}
                            Test Filter: ${params.TEST_FILTER}
                            
                            Please check the build logs and test reports for details.
                            
                            Build URL: ${env.BUILD_URL}
                        """,
                        to: "${env.CHANGE_AUTHOR_EMAIL}, dev-team@company.com"
                    )
                }
            }
        }
        
        unstable {
            script {
                slackSend(
                    channel: '#ci-cd',
                    color: 'warning',
                    message: """
                        ⚠️ Hook Test Framework Pipeline Unstable
                        Branch: ${env.BRANCH_NAME}
                        Build: ${env.BUILD_NUMBER}
                        Test Filter: ${params.TEST_FILTER}
                        Some tests may have failed
                    """
                )
            }
        }
        
        changed {
            script {
                // Notify when build status changes
                def previousResult = currentBuild.getPreviousBuild()?.getResult()
                def currentResult = currentBuild.getResult()
                
                if (previousResult != currentResult) {
                    slackSend(
                        channel: '#ci-cd',
                        color: currentResult == 'SUCCESS' ? 'good' : 'warning',
                        message: """
                            🔄 Hook Test Framework Build Status Changed
                            Branch: ${env.BRANCH_NAME}
                            Previous: ${previousResult}
                            Current: ${currentResult}
                            Build: ${env.BUILD_NUMBER}
                        """
                    )
                }
            }
        }
    }
}