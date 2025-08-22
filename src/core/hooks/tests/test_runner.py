#!/usr/bin/env python3
"""
Hook Test Runner - V3.6.9
Automated test runner with CI/CD integration for comprehensive hook testing
Features:
- Parallel test execution
- Test discovery and scheduling
- Results aggregation and reporting
- CI/CD pipeline integration
- Performance regression detection
- Automated baseline updates
"""

import asyncio
import json
import logging
import os
import sys
import time
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
import argparse
import signal
import subprocess
import yaml

# Import test framework components
from .test_framework import HookTestFramework, TestResult, TestSuite
from .test_utilities import (
    TestDataGenerator, TestEnvironmentManager, PerformanceProfiler,
    ConcurrencyTester, TestValidator, HookExecutionHelper
)

logger = logging.getLogger(__name__)


class TestScheduler:
    """Schedules and manages test execution"""
    
    def __init__(self, max_parallel_suites: int = 3, max_parallel_tests: int = 8):
        self.max_parallel_suites = max_parallel_suites
        self.max_parallel_tests = max_parallel_tests
        self.test_queue = []
        self.running_tests = {}
        self.completed_tests = {}
        self.failed_tests = {}
        
    def schedule_test_suite(self, suite_name: str, priority: int = 5) -> str:
        """Schedule a test suite for execution"""
        test_id = f"{suite_name}_{int(time.time())}"
        
        self.test_queue.append({
            "test_id": test_id,
            "suite_name": suite_name,
            "priority": priority,
            "scheduled_time": datetime.now(),
            "status": "queued"
        })
        
        # Sort by priority (lower number = higher priority)
        self.test_queue.sort(key=lambda x: x["priority"])
        
        return test_id
        
    def get_next_test(self) -> Optional[Dict[str, Any]]:
        """Get next test to execute"""
        if self.test_queue and len(self.running_tests) < self.max_parallel_suites:
            return self.test_queue.pop(0)
        return None
        
    def mark_test_running(self, test_info: Dict[str, Any]):
        """Mark test as currently running"""
        test_info["status"] = "running"
        test_info["start_time"] = datetime.now()
        self.running_tests[test_info["test_id"]] = test_info
        
    def mark_test_completed(self, test_id: str, results: List[TestResult]):
        """Mark test as completed"""
        if test_id in self.running_tests:
            test_info = self.running_tests.pop(test_id)
            test_info["status"] = "completed"
            test_info["end_time"] = datetime.now()
            test_info["results"] = results
            self.completed_tests[test_id] = test_info
            
    def mark_test_failed(self, test_id: str, error: str):
        """Mark test as failed"""
        if test_id in self.running_tests:
            test_info = self.running_tests.pop(test_id)
            test_info["status"] = "failed"
            test_info["end_time"] = datetime.now()
            test_info["error"] = error
            self.failed_tests[test_id] = test_info
            
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "queued_tests": len(self.test_queue),
            "running_tests": len(self.running_tests),
            "completed_tests": len(self.completed_tests),
            "failed_tests": len(self.failed_tests),
            "queue_details": self.test_queue,
            "running_details": list(self.running_tests.values()),
            "completion_rate": len(self.completed_tests) / (len(self.completed_tests) + len(self.failed_tests)) * 100 if (self.completed_tests or self.failed_tests) else 0
        }


class TestReporter:
    """Generates comprehensive test reports"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "test_reports"
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_html_report(self, test_results: Dict[str, List[TestResult]], metadata: Dict[str, Any] = None) -> str:
        """Generate HTML test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"hook_test_report_{timestamp}.html"
        
        # Calculate summary statistics
        all_tests = []
        for suite_results in test_results.values():
            all_tests.extend(suite_results)
            
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.status == "PASS")
        failed_tests = sum(1 for test in all_tests if test.status == "FAIL")
        error_tests = sum(1 for test in all_tests if test.status == "ERROR")
        skipped_tests = sum(1 for test in all_tests if test.status == "SKIP")
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_execution_time = sum(test.execution_time for test in all_tests)
        
        # Generate HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Test Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card.pass {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }}
        .summary-card.fail {{ background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }}
        .summary-card.error {{ background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }}
        .summary-card.skip {{ background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%); }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 1.2em; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; }}
        .suite-section {{ margin-bottom: 30px; }}
        .suite-header {{ background-color: #2196F3; color: white; padding: 15px; border-radius: 8px 8px 0 0; }}
        .suite-content {{ border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; }}
        .test-item {{ padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
        .test-item:last-child {{ border-bottom: none; }}
        .test-status {{ padding: 5px 10px; border-radius: 4px; color: white; font-weight: bold; }}
        .status-PASS {{ background-color: #4CAF50; }}
        .status-FAIL {{ background-color: #f44336; }}
        .status-ERROR {{ background-color: #ff9800; }}
        .status-SKIP {{ background-color: #9e9e9e; }}
        .execution-time {{ color: #666; font-size: 0.9em; }}
        .error-message {{ color: #f44336; font-size: 0.9em; margin-top: 5px; }}
        .performance-chart {{ margin: 20px 0; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #ddd; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #4CAF50, #2196F3); transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Hook Test Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="number">{total_tests}</div>
            </div>
            <div class="summary-card pass">
                <h3>Passed</h3>
                <div class="number">{passed_tests}</div>
            </div>
            <div class="summary-card fail">
                <h3>Failed</h3>
                <div class="number">{failed_tests}</div>
            </div>
            <div class="summary-card error">
                <h3>Errors</h3>
                <div class="number">{error_tests}</div>
            </div>
            <div class="summary-card skip">
                <h3>Skipped</h3>
                <div class="number">{skipped_tests}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3>Pass Rate: {pass_rate:.1f}%</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pass_rate}%"></div>
            </div>
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3>Execution Summary</h3>
            <p><strong>Total Execution Time:</strong> {total_execution_time:.2f} seconds</p>
            <p><strong>Average Test Time:</strong> {total_execution_time/total_tests if total_tests > 0 else 0:.3f} seconds</p>
        </div>
"""
        
        # Add suite details
        for suite_name, suite_results in test_results.items():
            suite_passed = sum(1 for test in suite_results if test.status == "PASS")
            suite_total = len(suite_results)
            suite_pass_rate = (suite_passed / suite_total * 100) if suite_total > 0 else 0
            
            html_content += f"""
        <div class="suite-section">
            <div class="suite-header">
                <h3>{suite_name.replace('_', ' ').title()} ({suite_passed}/{suite_total} - {suite_pass_rate:.1f}%)</h3>
            </div>
            <div class="suite-content">
"""
            
            for test in suite_results:
                error_html = ""
                if test.error_message:
                    error_html = f'<div class="error-message">{test.error_message}</div>'
                    
                html_content += f"""
                <div class="test-item">
                    <div>
                        <strong>{test.test_name}</strong> ({test.hook_name})
                        {error_html}
                    </div>
                    <div>
                        <span class="test-status status-{test.status}">{test.status}</span>
                        <span class="execution-time">{test.execution_time:.3f}s</span>
                    </div>
                </div>
"""
            
            html_content += """
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(report_file, 'w') as f:
            f.write(html_content)
            
        logger.info(f"HTML report generated: {report_file}")
        return str(report_file)
        
    def generate_junit_xml(self, test_results: Dict[str, List[TestResult]], output_file: str = None) -> str:
        """Generate JUnit XML report for CI/CD integration"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"junit_results_{timestamp}.xml"
        
        # Calculate totals
        all_tests = []
        for suite_results in test_results.values():
            all_tests.extend(suite_results)
            
        total_tests = len(all_tests)
        failures = sum(1 for test in all_tests if test.status == "FAIL")
        errors = sum(1 for test in all_tests if test.status == "ERROR")
        skipped = sum(1 for test in all_tests if test.status == "SKIP")
        time_total = sum(test.execution_time for test in all_tests)
        
        # Generate XML
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="HookTestFramework" tests="{total_tests}" failures="{failures}" errors="{errors}" time="{time_total:.3f}" timestamp="{datetime.now().isoformat()}">
"""
        
        for suite_name, suite_results in test_results.items():
            suite_tests = len(suite_results)
            suite_failures = sum(1 for test in suite_results if test.status == "FAIL")
            suite_errors = sum(1 for test in suite_results if test.status == "ERROR")
            suite_skipped = sum(1 for test in suite_results if test.status == "SKIP")
            suite_time = sum(test.execution_time for test in suite_results)
            
            xml_content += f"""  <testsuite name="{suite_name}" tests="{suite_tests}" failures="{suite_failures}" errors="{suite_errors}" skipped="{suite_skipped}" time="{suite_time:.3f}">
"""
            
            for test in suite_results:
                xml_content += f"""    <testcase classname="{suite_name}" name="{test.test_name}" time="{test.execution_time:.3f}">
"""
                
                if test.status == "FAIL":
                    xml_content += f"""      <failure message="{test.error_message or 'Test failed'}">{test.error_message or 'Test failed'}</failure>
"""
                elif test.status == "ERROR":
                    xml_content += f"""      <error message="{test.error_message or 'Test error'}">{test.error_message or 'Test error'}</error>
"""
                elif test.status == "SKIP":
                    xml_content += f"""      <skipped message="{test.error_message or 'Test skipped'}" />
"""
                
                xml_content += """    </testcase>
"""
            
            xml_content += """  </testsuite>
"""
        
        xml_content += """</testsuites>
"""
        
        # Write XML file
        with open(output_file, 'w') as f:
            f.write(xml_content)
            
        logger.info(f"JUnit XML report generated: {output_file}")
        return str(output_file)
        
    def generate_performance_report(self, performance_data: Dict[str, Any], output_file: str = None) -> str:
        """Generate performance analysis report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"performance_report_{timestamp}.json"
            
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "performance_summary": performance_data,
            "analysis": {
                "slow_hooks": [],
                "memory_intensive_hooks": [],
                "performance_regressions": [],
                "recommendations": []
            }
        }
        
        # Analyze performance data
        if "benchmarks" in performance_data:
            benchmarks = performance_data["benchmarks"]
            
            # Identify slow hooks (execution time > 2 seconds)
            slow_hooks = [
                {"hook": name, "time": data.current_time}
                for name, data in benchmarks.items()
                if data.current_time > 2000
            ]
            report_data["analysis"]["slow_hooks"] = sorted(slow_hooks, key=lambda x: x["time"], reverse=True)
            
            # Identify memory intensive hooks (> 50MB)
            memory_intensive = [
                {"hook": name, "memory": data.memory_usage}
                for name, data in benchmarks.items()
                if data.memory_usage > 50 * 1024 * 1024
            ]
            report_data["analysis"]["memory_intensive_hooks"] = sorted(memory_intensive, key=lambda x: x["memory"], reverse=True)
            
            # Identify performance regressions
            regressions = [
                {"hook": name, "regression_factor": data.current_time / data.baseline_time}
                for name, data in benchmarks.items()
                if not data.passed and data.baseline_time > 0
            ]
            report_data["analysis"]["performance_regressions"] = sorted(regressions, key=lambda x: x["regression_factor"], reverse=True)
        
        # Generate recommendations
        recommendations = []
        if report_data["analysis"]["slow_hooks"]:
            recommendations.append("Optimize slow-performing hooks to improve overall system responsiveness")
        if report_data["analysis"]["memory_intensive_hooks"]:
            recommendations.append("Review memory usage patterns in memory-intensive hooks")
        if report_data["analysis"]["performance_regressions"]:
            recommendations.append("Address performance regressions before deployment")
            
        report_data["analysis"]["recommendations"] = recommendations
        
        # Write report
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
            
        logger.info(f"Performance report generated: {output_file}")
        return str(output_file)


class ContinuousIntegrationRunner:
    """CI/CD integration for automated testing"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.config = self._load_config()
        self.exit_code = 0
        
    def _load_config(self) -> Dict[str, Any]:
        """Load CI configuration"""
        default_config = {
            "parallel_suites": 3,
            "parallel_tests": 8,
            "timeout_minutes": 30,
            "performance_regression_threshold": 1.5,
            "required_pass_rate": 90.0,
            "fail_on_regression": True,
            "update_baselines": False,
            "notification_webhooks": [],
            "artifact_retention_days": 30
        }
        
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        loaded_config = yaml.safe_load(f)
                    else:
                        loaded_config = json.load(f)
                default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
                
        return default_config
        
    def run_ci_pipeline(self, hooks_directory: str = None, test_filter: str = None) -> int:
        """Run complete CI pipeline"""
        logger.info("Starting CI/CD test pipeline...")
        
        try:
            # Initialize test framework
            framework = HookTestFramework(hooks_directory=hooks_directory)
            
            # Setup test environment
            framework.setup_test_environment()
            
            try:
                # Run tests based on filter
                if test_filter:
                    results = self._run_filtered_tests(framework, test_filter)
                else:
                    results = framework.run_all_tests()
                
                # Analyze results
                analysis = self._analyze_results(results)
                
                # Generate reports
                self._generate_ci_reports(results, analysis, framework)
                
                # Check quality gates
                self._check_quality_gates(analysis)
                
                # Update baselines if configured
                if self.config.get("update_baselines", False):
                    self._update_performance_baselines(framework)
                
                # Send notifications
                self._send_notifications(analysis)
                
                logger.info(f"CI pipeline completed with exit code: {self.exit_code}")
                return self.exit_code
                
            finally:
                framework.teardown_test_environment()
                
        except Exception as e:
            logger.error(f"CI pipeline failed: {e}")
            self.exit_code = 1
            return self.exit_code
            
    def _run_filtered_tests(self, framework: HookTestFramework, test_filter: str) -> Dict[str, List[TestResult]]:
        """Run filtered tests based on criteria"""
        if test_filter == "smoke":
            # Run critical tests only
            critical_suites = ["individual_functionality", "error_scenarios"]
            results = {}
            for suite_name in critical_suites:
                if suite_name in framework.test_suites:
                    results[suite_name] = framework.run_test_suite(suite_name)
            return results
            
        elif test_filter == "performance":
            # Run performance tests only
            return {"performance": framework.run_test_suite("performance")}
            
        elif test_filter == "regression":
            # Run regression tests only
            return {"regression": framework.run_test_suite("regression")}
            
        else:
            # Run specific suite
            if test_filter in framework.test_suites:
                return {test_filter: framework.run_test_suite(test_filter)}
            else:
                logger.warning(f"Unknown test filter: {test_filter}")
                return framework.run_all_tests()
                
    def _analyze_results(self, results: Dict[str, List[TestResult]]) -> Dict[str, Any]:
        """Analyze test results"""
        all_tests = []
        for suite_results in results.values():
            all_tests.extend(suite_results)
            
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.status == "PASS")
        failed_tests = sum(1 for test in all_tests if test.status == "FAIL")
        error_tests = sum(1 for test in all_tests if test.status == "ERROR")
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "pass_rate": pass_rate,
            "execution_time": sum(test.execution_time for test in all_tests),
            "failed_test_names": [test.test_name for test in all_tests if test.status == "FAIL"],
            "error_test_names": [test.test_name for test in all_tests if test.status == "ERROR"]
        }
        
    def _generate_ci_reports(self, results: Dict[str, List[TestResult]], analysis: Dict[str, Any], framework: HookTestFramework):
        """Generate CI-specific reports"""
        reporter = TestReporter()
        
        # Generate reports
        html_report = reporter.generate_html_report(results)
        junit_report = reporter.generate_junit_xml(results)
        
        # Generate performance report if benchmarks available
        if framework.performance_benchmarks:
            perf_data = {"benchmarks": framework.performance_benchmarks}
            performance_report = reporter.generate_performance_report(perf_data)
        
        # Set environment variables for CI systems
        os.environ["TEST_REPORT_HTML"] = html_report
        os.environ["TEST_REPORT_JUNIT"] = junit_report
        os.environ["TEST_PASS_RATE"] = str(analysis["pass_rate"])
        os.environ["TEST_TOTAL_COUNT"] = str(analysis["total_tests"])
        os.environ["TEST_FAILED_COUNT"] = str(analysis["failed_tests"])
        
        logger.info(f"Generated CI reports - HTML: {html_report}, JUnit: {junit_report}")
        
    def _check_quality_gates(self, analysis: Dict[str, Any]):
        """Check quality gates and set exit code"""
        required_pass_rate = self.config.get("required_pass_rate", 90.0)
        
        if analysis["pass_rate"] < required_pass_rate:
            logger.error(f"Pass rate {analysis['pass_rate']:.1f}% is below required {required_pass_rate}%")
            self.exit_code = 1
            
        if analysis["error_tests"] > 0:
            logger.error(f"Found {analysis['error_tests']} test errors")
            self.exit_code = 1
            
        # Check for critical test failures
        critical_failures = [
            name for name in analysis["failed_test_names"] 
            if "individual_functionality" in name or "error_scenarios" in name
        ]
        
        if critical_failures:
            logger.error(f"Critical tests failed: {critical_failures}")
            self.exit_code = 1
            
    def _update_performance_baselines(self, framework: HookTestFramework):
        """Update performance baselines"""
        logger.info("Updating performance baselines...")
        framework._save_performance_baselines()
        
    def _send_notifications(self, analysis: Dict[str, Any]):
        """Send notifications to configured webhooks"""
        webhooks = self.config.get("notification_webhooks", [])
        
        if not webhooks:
            return
            
        notification_data = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_status": "success" if self.exit_code == 0 else "failure",
            "test_summary": analysis,
            "exit_code": self.exit_code
        }
        
        for webhook_url in webhooks:
            try:
                import requests
                response = requests.post(webhook_url, json=notification_data, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Notification sent to {webhook_url}")
                else:
                    logger.warning(f"Failed to send notification to {webhook_url}: {response.status_code}")
            except Exception as e:
                logger.warning(f"Failed to send notification to {webhook_url}: {e}")


class TestRunner:
    """Main test runner with multiple execution modes"""
    
    def __init__(self):
        self.scheduler = TestScheduler()
        self.reporter = TestReporter()
        self.ci_runner = ContinuousIntegrationRunner()
        self.interrupted = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.interrupted = True
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def run_interactive_mode(self, hooks_directory: str = None):
        """Run in interactive mode with real-time feedback"""
        logger.info("Starting interactive test runner...")
        
        framework = HookTestFramework(hooks_directory=hooks_directory)
        
        while not self.interrupted:
            try:
                print("\n" + "="*50)
                print("HOOK TEST RUNNER - INTERACTIVE MODE")
                print("="*50)
                print("1. Run all tests")
                print("2. Run specific test suite")
                print("3. Run specific hook test") 
                print("4. View test history")
                print("5. Performance analysis")
                print("6. System status")
                print("0. Exit")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    self._run_all_tests_interactive(framework)
                elif choice == "2":
                    self._run_suite_interactive(framework)
                elif choice == "3":
                    self._run_hook_test_interactive(framework)
                elif choice == "4":
                    self._view_test_history()
                elif choice == "5":
                    self._performance_analysis(framework)
                elif choice == "6":
                    self._system_status(framework)
                else:
                    print("Invalid option")
                    
            except KeyboardInterrupt:
                self.interrupted = True
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                
        logger.info("Interactive test runner stopped")
        
    def _run_all_tests_interactive(self, framework: HookTestFramework):
        """Run all tests with interactive feedback"""
        print("\nRunning all test suites...")
        
        framework.setup_test_environment()
        try:
            results = framework.run_all_tests()
            
            # Display results
            for suite_name, suite_results in results.items():
                passed = sum(1 for test in suite_results if test.status == "PASS")
                total = len(suite_results)
                print(f"{suite_name}: {passed}/{total} tests passed")
                
            # Generate report
            report_file = self.reporter.generate_html_report(results)
            print(f"\nDetailed report saved to: {report_file}")
            
        finally:
            framework.teardown_test_environment()
            
    def _run_suite_interactive(self, framework: HookTestFramework):
        """Run specific test suite interactively"""
        print("\nAvailable test suites:")
        for i, suite_name in enumerate(framework.test_suites.keys(), 1):
            print(f"{i}. {suite_name}")
            
        try:
            choice = int(input("\nSelect suite number: "))
            suite_names = list(framework.test_suites.keys())
            
            if 1 <= choice <= len(suite_names):
                suite_name = suite_names[choice - 1]
                print(f"\nRunning {suite_name}...")
                
                framework.setup_test_environment()
                try:
                    results = framework.run_test_suite(suite_name)
                    passed = sum(1 for test in results if test.status == "PASS")
                    print(f"Results: {passed}/{len(results)} tests passed")
                    
                    # Show failed tests
                    failed_tests = [test for test in results if test.status == "FAIL"]
                    if failed_tests:
                        print("\nFailed tests:")
                        for test in failed_tests:
                            print(f"  - {test.test_name}: {test.error_message}")
                            
                finally:
                    framework.teardown_test_environment()
            else:
                print("Invalid suite number")
                
        except ValueError:
            print("Invalid input")
            
    def _run_hook_test_interactive(self, framework: HookTestFramework):
        """Run specific hook test interactively"""
        hook_names = list(framework.hook_registry_data['hooks'].keys())
        
        print("\nAvailable hooks:")
        for i, hook_name in enumerate(hook_names, 1):
            print(f"{i}. {hook_name}")
            
        try:
            choice = int(input("\nSelect hook number: "))
            
            if 1 <= choice <= len(hook_names):
                hook_name = hook_names[choice - 1]
                print(f"\nTesting {hook_name}...")
                
                framework.setup_test_environment()
                try:
                    result = framework.test_individual_hook(hook_name)
                    print(f"Result: {result.status}")
                    if result.error_message:
                        print(f"Error: {result.error_message}")
                    print(f"Execution time: {result.execution_time:.3f}s")
                    
                finally:
                    framework.teardown_test_environment()
            else:
                print("Invalid hook number")
                
        except ValueError:
            print("Invalid input")
            
    def _view_test_history(self):
        """View test execution history"""
        print("\nTest execution history:")
        status = self.scheduler.get_status()
        
        print(f"Completed tests: {status['completed_tests']}")
        print(f"Failed tests: {status['failed_tests']}")
        print(f"Success rate: {status['completion_rate']:.1f}%")
        
    def _performance_analysis(self, framework: HookTestFramework):
        """Show performance analysis"""
        print("\nPerformance Analysis:")
        
        if framework.performance_benchmarks:
            slow_hooks = [
                (name, bench.current_time)
                for name, bench in framework.performance_benchmarks.items()
                if bench.current_time > 1000  # > 1 second
            ]
            
            if slow_hooks:
                print("Slow hooks (>1s):")
                for hook_name, time_ms in sorted(slow_hooks, key=lambda x: x[1], reverse=True):
                    print(f"  {hook_name}: {time_ms:.0f}ms")
            else:
                print("All hooks performing well")
        else:
            print("No performance data available")
            
    def _system_status(self, framework: HookTestFramework):
        """Show system status"""
        print("\nSystem Status:")
        
        if framework.test_manager:
            try:
                status = framework.test_manager.get_system_status()
                print(f"Initialized: {status.get('initialized', False)}")
                print(f"Running: {status.get('running', False)}")
                print(f"Total hooks: {status.get('stats', {}).get('total_hooks', 0)}")
                print(f"Active hooks: {status.get('stats', {}).get('active_hooks', 0)}")
            except Exception as e:
                print(f"Failed to get system status: {e}")
        else:
            print("Test manager not initialized")


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="Hook Test Runner V3.6.9")
    
    # Mode selection
    parser.add_argument('--mode', choices=['ci', 'interactive', 'batch'], default='batch',
                       help='Execution mode')
    
    # Test configuration
    parser.add_argument('--hooks-dir', help='Directory containing hooks')
    parser.add_argument('--config-file', help='CI configuration file')
    parser.add_argument('--suite', help='Specific test suite to run')
    parser.add_argument('--hook', help='Specific hook to test')
    parser.add_argument('--filter', help='Test filter (smoke, performance, regression)')
    
    # Output configuration
    parser.add_argument('--output-dir', help='Output directory for reports')
    parser.add_argument('--junit-xml', help='Generate JUnit XML report')
    parser.add_argument('--html-report', help='Generate HTML report')
    
    # Execution configuration
    parser.add_argument('--parallel-suites', type=int, default=3, help='Number of parallel test suites')
    parser.add_argument('--parallel-tests', type=int, default=8, help='Number of parallel tests')
    parser.add_argument('--timeout', type=int, default=30, help='Test timeout in minutes')
    
    # CI/CD options
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first failure')
    parser.add_argument('--update-baselines', action='store_true', help='Update performance baselines')
    parser.add_argument('--required-pass-rate', type=float, default=90.0, help='Required pass rate percentage')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.INFO
    if args.mode == 'ci':
        log_level = logging.WARNING
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize test runner
    runner = TestRunner()
    runner.setup_signal_handlers()
    
    exit_code = 0
    
    try:
        if args.mode == 'ci':
            # CI/CD mode
            ci_runner = ContinuousIntegrationRunner(args.config_file)
            exit_code = ci_runner.run_ci_pipeline(args.hooks_dir, args.filter)
            
        elif args.mode == 'interactive':
            # Interactive mode
            runner.run_interactive_mode(args.hooks_dir)
            
        else:
            # Batch mode
            framework = HookTestFramework(hooks_directory=args.hooks_dir)
            
            if args.hook:
                # Test specific hook
                framework.setup_test_environment()
                try:
                    result = framework.test_individual_hook(args.hook)
                    print(f"Hook {args.hook}: {result.status}")
                    if result.status != "PASS":
                        exit_code = 1
                finally:
                    framework.teardown_test_environment()
                    
            elif args.suite:
                # Test specific suite
                framework.setup_test_environment()
                try:
                    results = framework.run_test_suite(args.suite)
                    passed = sum(1 for r in results if r.status == "PASS")
                    print(f"Suite {args.suite}: {passed}/{len(results)} tests passed")
                    if passed < len(results):
                        exit_code = 1
                finally:
                    framework.teardown_test_environment()
                    
            else:
                # Run all tests
                results = framework.run_all_tests()
                
                # Generate reports
                if args.output_dir:
                    reporter = TestReporter(args.output_dir)
                else:
                    reporter = TestReporter()
                    
                if args.html_report or not args.junit_xml:
                    html_file = reporter.generate_html_report(results)
                    print(f"HTML report: {html_file}")
                    
                if args.junit_xml:
                    junit_file = reporter.generate_junit_xml(results, args.junit_xml)
                    print(f"JUnit XML: {junit_file}")
                
                # Check pass rate
                all_tests = []
                for suite_results in results.values():
                    all_tests.extend(suite_results)
                    
                passed = sum(1 for test in all_tests if test.status == "PASS")
                total = len(all_tests)
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                print(f"Overall results: {passed}/{total} tests passed ({pass_rate:.1f}%)")
                
                if pass_rate < args.required_pass_rate:
                    exit_code = 1
                    
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        exit_code = 130
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        exit_code = 1
        
    sys.exit(exit_code)


if __name__ == '__main__':
    main()