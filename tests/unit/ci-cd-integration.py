#!/usr/bin/env python3
"""
CI/CD Integration for Agent Test Suite
Provides integration with GitHub Actions, Jenkins, and other CI/CD platforms
"""

import os
import json
import yaml
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CICDIntegration:
    """CI/CD integration for automated testing"""
    
    def __init__(self, config_path: str = "tests/config/test-config.yaml"):
        self.config = self._load_config(config_path)
        self.ci_config = self.config.get('ci_cd', {})
        self.quality_gates = self.ci_config.get('quality_gates', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load CI/CD configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def should_run_tests(self, changed_files: List[str] = None) -> bool:
        """Determine if tests should run based on changes"""
        if not changed_files:
            # Run all tests if no specific files changed
            return True
        
        # Define file patterns that trigger testing
        test_triggers = [
            'core/agents/**',
            'tier1/**',
            'tier2/**',
            'tests/**',
            '*.py',
            '*.md',
            '*.yaml',
            '*.yml'
        ]
        
        # Check if any changed files match trigger patterns
        for file_path in changed_files:
            for pattern in test_triggers:
                if self._matches_pattern(file_path, pattern):
                    return True
        
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def get_test_selection(self, changed_files: List[str] = None) -> List[str]:
        """Get intelligent test selection based on changes"""
        if not changed_files:
            return []  # Run all tests
        
        # Map file changes to relevant test suites
        test_mapping = {
            'core/agents/**': ['individual_operations', 'inter_agent_communication'],
            'tier1/**': ['individual_operations', 'bmad_testing'],
            'tier2/**': ['individual_operations', 'bmad_testing'],
            'tests/**': [],  # Run all tests for test changes
            'performance/**': ['performance_benchmarks', 'load_testing'],
            'security/**': ['security_testing'],
            'docs/**': ['integration_testing']  # Documentation changes might affect integration
        }
        
        selected_tests = set()
        
        for file_path in changed_files:
            for pattern, tests in test_mapping.items():
                if self._matches_pattern(file_path, pattern):
                    selected_tests.update(tests)
        
        return list(selected_tests)
    
    def validate_quality_gates(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test results against quality gates"""
        gate_results = {}
        overall_passed = True
        
        # Test coverage gate
        coverage_threshold = self.quality_gates.get('minimum_test_coverage', 0.8)
        actual_coverage = test_results.get('coverage', {}).get('overall', 0.0)
        coverage_passed = actual_coverage >= coverage_threshold
        gate_results['test_coverage'] = {
            'passed': coverage_passed,
            'threshold': coverage_threshold,
            'actual': actual_coverage
        }
        overall_passed &= coverage_passed
        
        # Failure rate gate
        max_failure_rate = self.quality_gates.get('maximum_failure_rate', 0.05)
        actual_failure_rate = 1.0 - test_results.get('summary', {}).get('success_rate', 1.0)
        failure_rate_passed = actual_failure_rate <= max_failure_rate
        gate_results['failure_rate'] = {
            'passed': failure_rate_passed,
            'threshold': max_failure_rate,
            'actual': actual_failure_rate
        }
        overall_passed &= failure_rate_passed
        
        # Regression count gate
        max_regressions = self.quality_gates.get('maximum_regression_count', 3)
        actual_regressions = test_results.get('regressions', {}).get('count', 0)
        regression_passed = actual_regressions <= max_regressions
        gate_results['regressions'] = {
            'passed': regression_passed,
            'threshold': max_regressions,
            'actual': actual_regressions
        }
        overall_passed &= regression_passed
        
        # Performance gate
        min_performance = self.quality_gates.get('minimum_performance_score', 0.75)
        actual_performance = test_results.get('performance', {}).get('overall_score', 1.0)
        performance_passed = actual_performance >= min_performance
        gate_results['performance'] = {
            'passed': performance_passed,
            'threshold': min_performance,
            'actual': actual_performance
        }
        overall_passed &= performance_passed
        
        return {
            'overall_passed': overall_passed,
            'gate_results': gate_results
        }
    
    def should_fail_pipeline(self, test_results: Dict[str, Any], quality_gates: Dict[str, Any]) -> bool:
        """Determine if pipeline should fail based on results"""
        # Critical failure check
        if self.ci_config.get('fail_pipeline_on_critical_failure', True):
            critical_failures = test_results.get('critical_failures', [])
            if critical_failures:
                return True
        
        # Regression check
        if self.ci_config.get('fail_pipeline_on_regression', True):
            if not quality_gates.get('gate_results', {}).get('regressions', {}).get('passed', True):
                return True
        
        # Security check
        if self.ci_config.get('fail_pipeline_on_security_issues', True):
            security_issues = test_results.get('security', {}).get('issues', [])
            critical_security = [issue for issue in security_issues if issue.get('severity') == 'critical']
            if critical_security:
                return True
        
        # Overall quality gates
        if not quality_gates.get('overall_passed', True):
            return True
        
        return False
    
    def generate_github_actions_workflow(self) -> str:
        """Generate GitHub Actions workflow file"""
        workflow = {
            'name': 'Agent Test Suite',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main', 'develop']},
                'schedule': [{'cron': '0 2 * * *'}]  # Daily at 2 AM
            },
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',
                    'timeout-minutes': 120,
                    'strategy': {
                        'matrix': {
                            'python-version': ['3.9', '3.10', '3.11'],
                            'test-suite': [
                                'individual_operations',
                                'inter_agent_communication',
                                'context_preservation',
                                'error_scenarios'
                            ]
                        }
                    },
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '${{ matrix.python-version }}'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r tests/requirements.txt'
                        },
                        {
                            'name': 'Run tests',
                            'run': 'python tests/test-runner.py --suites ${{ matrix.test-suite }} --verbose'
                        },
                        {
                            'name': 'Upload test results',
                            'uses': 'actions/upload-artifact@v3',
                            'if': 'always()',
                            'with': {
                                'name': 'test-results-${{ matrix.python-version }}-${{ matrix.test-suite }}',
                                'path': 'tests/reports/'
                            }
                        }
                    ]
                },
                'performance': {
                    'runs-on': 'ubuntu-latest',
                    'needs': 'test',
                    'timeout-minutes': 60,
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r tests/requirements.txt'
                        },
                        {
                            'name': 'Run performance tests',
                            'run': 'python tests/test-runner.py --suites performance_benchmarks load_testing'
                        },
                        {
                            'name': 'Upload performance results',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'performance-results',
                                'path': 'tests/reports/'
                            }
                        }
                    ]
                },
                'integration': {
                    'runs-on': 'ubuntu-latest',
                    'needs': ['test', 'performance'],
                    'if': "github.event_name == 'push' || github.event_name == 'schedule'",
                    'timeout-minutes': 90,
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r tests/requirements.txt'
                        },
                        {
                            'name': 'Run integration tests',
                            'run': 'python tests/test-runner.py --suites integration_testing'
                        },
                        {
                            'name': 'Validate quality gates',
                            'run': 'python tests/validate-quality-gates.py'
                        },
                        {
                            'name': 'Upload integration results',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'integration-results',
                                'path': 'tests/reports/'
                            }
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False)
    
    def generate_jenkins_pipeline(self) -> str:
        """Generate Jenkins pipeline script"""
        pipeline = f"""
pipeline {{
    agent any
    
    options {{
        timeout(time: 2, unit: 'HOURS')
        retry(3)
        parallelsAlwaysFailFast()
    }}
    
    environment {{
        PYTHON_PATH = '/usr/bin/python3'
        TEST_CONFIG = 'tests/config/test-config.yaml'
    }}
    
    stages {{
        stage('Preparation') {{
            steps {{
                checkout scm
                sh 'pip install -r tests/requirements.txt'
            }}
        }}
        
        stage('Parallel Testing') {{
            parallel {{
                stage('Unit Tests') {{
                    steps {{
                        sh 'python tests/test-runner.py --suites individual_operations inter_agent_communication'
                    }}
                    post {{
                        always {{
                            publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
                            archiveArtifacts artifacts: 'tests/reports/**/*', fingerprint: true
                        }}
                    }}
                }}
                
                stage('Context & Error Tests') {{
                    steps {{
                        sh 'python tests/test-runner.py --suites context_preservation error_scenarios'
                    }}
                    post {{
                        always {{
                            publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
                        }}
                    }}
                }}
                
                stage('Performance Tests') {{
                    steps {{
                        sh 'python tests/test-runner.py --suites performance_benchmarks'
                    }}
                    post {{
                        always {{
                            publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'tests/reports',
                                reportFiles: 'test-report-*.html',
                                reportName: 'Performance Report'
                            ])
                        }}
                    }}
                }}
            }}
        }}
        
        stage('Integration Tests') {{
            when {{
                anyOf {{
                    branch 'main'
                    branch 'develop'
                }}
            }}
            steps {{
                sh 'python tests/test-runner.py --suites integration_testing'
            }}
            post {{
                always {{
                    publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
                }}
            }}
        }}
        
        stage('Load Testing') {{
            when {{
                branch 'main'
            }}
            steps {{
                sh 'python tests/test-runner.py --suites load_testing'
            }}
            post {{
                always {{
                    publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
                }}
            }}
        }}
        
        stage('Quality Gates') {{
            steps {{
                script {{
                    def qualityGates = sh(
                        script: 'python tests/validate-quality-gates.py --json',
                        returnStdout: true
                    ).trim()
                    
                    def gates = readJSON text: qualityGates
                    
                    if (!gates.overall_passed) {{
                        error("Quality gates failed: ${{gates.gate_results}}")
                    }}
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            publishTestResults testResultsPattern: 'tests/reports/junit-*.xml'
            archiveArtifacts artifacts: 'tests/reports/**/*', fingerprint: true
            
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'tests/reports',
                reportFiles: 'test-report-*.html',
                reportName: 'Test Report'
            ])
        }}
        
        failure {{
            emailext (
                subject: "Agent Test Suite Failed - Build ${{env.BUILD_NUMBER}}",
                body: "The agent test suite has failed. Please check the build logs for details.",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
        
        success {{
            echo 'All tests passed successfully!'
        }}
    }}
}}
"""
        return pipeline
    
    def get_changed_files_from_git(self, base_branch: str = 'main') -> List[str]:
        """Get list of changed files from git"""
        try:
            # Get changed files between current HEAD and base branch
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return changed_files
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not get changed files from git: {e}")
            return []
    
    def setup_pre_commit_hooks(self):
        """Setup pre-commit hooks for automated testing"""
        pre_commit_config = {
            'repos': [
                {
                    'repo': 'https://github.com/pre-commit/pre-commit-hooks',
                    'rev': 'v4.4.0',
                    'hooks': [
                        {'id': 'trailing-whitespace'},
                        {'id': 'end-of-file-fixer'},
                        {'id': 'check-yaml'},
                        {'id': 'check-json'},
                        {'id': 'check-merge-conflict'}
                    ]
                },
                {
                    'repo': 'https://github.com/psf/black',
                    'rev': '23.1.0',
                    'hooks': [{'id': 'black', 'language_version': 'python3'}]
                },
                {
                    'repo': 'local',
                    'hooks': [
                        {
                            'id': 'agent-tests',
                            'name': 'Run Agent Tests',
                            'entry': 'python tests/test-runner.py --suites individual_operations',
                            'language': 'system',
                            'files': r'^(core/agents/|tier[12]/|tests/).*\.(py|md|yaml|yml)$',
                            'pass_filenames': False
                        }
                    ]
                }
            ]
        }
        
        pre_commit_file = Path('.pre-commit-config.yaml')
        with open(pre_commit_file, 'w') as f:
            yaml.dump(pre_commit_config, f, default_flow_style=False)
        
        logger.info(f"Pre-commit configuration saved to {pre_commit_file}")


def main():
    """Main function for CI/CD integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD Integration for Agent Tests')
    parser.add_argument('--action', choices=['generate-github', 'generate-jenkins', 'setup-hooks', 'validate-gates'],
                      required=True, help='Action to perform')
    parser.add_argument('--config', default='tests/config/test-config.yaml',
                      help='Test configuration file')
    parser.add_argument('--output', help='Output file for generated content')
    
    args = parser.parse_args()
    
    integration = CICDIntegration(args.config)
    
    if args.action == 'generate-github':
        content = integration.generate_github_actions_workflow()
        output_file = args.output or '.github/workflows/agent-tests.yml'
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"GitHub Actions workflow generated: {output_path}")
    
    elif args.action == 'generate-jenkins':
        content = integration.generate_jenkins_pipeline()
        output_file = args.output or 'Jenkinsfile'
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"Jenkins pipeline generated: {output_file}")
    
    elif args.action == 'setup-hooks':
        integration.setup_pre_commit_hooks()
        print("Pre-commit hooks configured")
    
    elif args.action == 'validate-gates':
        # This would be called after test execution
        print("Quality gate validation would be performed here")
        # Implementation would read test results and validate against gates


if __name__ == "__main__":
    main()