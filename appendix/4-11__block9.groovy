// Jenkinsfile示例
pipeline {
    agent any
    
    environment {
        TEST_ENV = 'staging'
        JAVA_HOME = tool 'JDK11'
        PATH = "${JAVA_HOME}/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh 'pip install -r requirements-test.txt'
                sh 'python setup_test_environment.py'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh 'pytest tests/unit -v --junitxml=reports/unit-results.xml'
            }
            post {
                always {
                    junit 'reports/unit-results.xml'
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh 'pytest tests/integration -v --junitxml=reports/integration-results.xml'
            }
            post {
                always {
                    junit 'reports/integration-results.xml'
                }
            }
        }
        
        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                sh 'python run_performance_tests.py'
            }
            post {
                always {
                    publishHTML([allowMissing: false, 
                               alwaysLinkToLastBuild: true, 
                               keepAll: true, 
                               reportDir: 'reports/performance', 
                               reportFiles: 'index.html', 
                               reportName: '性能测试报告'])
                }
            }
        }
    }
    
    post {
        success {
            echo '测试全部通过！'
            // 可以触发部署流程
        }
        failure {
            echo '测试失败，请检查问题！'
            // 发送失败通知
        }
        always {
            // 清理工作
            sh 'python cleanup_test_environment.py'
        }
    }
}
