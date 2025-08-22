#!/usr/bin/env python3
"""
Comprehensive Agent Test Runner
Orchestrates execution of all test suites for V3.6.9 agent system
"""

import asyncio
import argparse
import json
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import pytest

# Import test frameworks
from agent_test_framework import AgentTestFramework
from agent_test_framework_extended import ExtendedAgentTestFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestSuiteConfig:
    """Configuration for a test suite"""
    name: str
    enabled: bool
    timeout: int
    critical: bool
    parallel: bool
    dependencies: List[str]

@dataclass
class TestExecution:
    """Test execution tracking"""
    suite_name: str
    start_time: float
    end_time: Optional[float]
    status: str
    results: Optional[Dict[str, Any]]
    error: Optional[str]

class ComprehensiveTestRunner:
    """
    Comprehensive test runner for all agent testing
    """
    
    def __init__(self, config_path: str = "tests/config/test-config.yaml"):
        self.config = self._load_config(config_path)
        self.test_framework = ExtendedAgentTestFramework(config_path)
        self.test_executions = []
        self.overall_start_time = None
        self.overall_end_time = None
        
        # Initialize test suites
        self.test_suites = self._initialize_test_suites()
        
        # Initialize reporting
        self.reporter = TestReporter(self.config)
        
        logger.info(f"Test runner initialized with {len(self.test_suites)} test suites")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load test configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            sys.exit(1)
    
    def _initialize_test_suites(self) -> Dict[str, TestSuiteConfig]:
        """Initialize test suite configurations"""
        suites = {}
        
        # Core test suites
        core_suites = [
            TestSuiteConfig("individual_operations", True, 600, True, True, []),
            TestSuiteConfig("inter_agent_communication", True, 900, True, True, ["individual_operations"]),
            TestSuiteConfig("context_preservation", True, 1200, True, False, ["inter_agent_communication"]),
            TestSuiteConfig("error_scenarios", True, 800, True, True, ["individual_operations"]),
            TestSuiteConfig("performance_benchmarks", True, 1500, True, True, ["individual_operations"]),
            TestSuiteConfig("load_testing", True, 2400, False, False, ["performance_benchmarks"]),
            TestSuiteConfig("integration_testing", True, 3600, True, False, ["context_preservation", "error_scenarios"])
        ]
        
        for suite in core_suites:
            suites[suite.name] = suite
        
        # Apply configuration overrides
        execution_config = self.config.get('execution', {})
        for suite_name, suite_config in suites.items():
            # Update from configuration
            suite_specific_config = self.config.get(suite_name.replace('_', '-'), {})
            if suite_specific_config.get('enabled') is not None:
                suite_config.enabled = suite_specific_config['enabled']
            if suite_specific_config.get('timeout'):
                suite_config.timeout = suite_specific_config['timeout']
        
        return suites
    
    async def run_all_tests(self, selected_suites: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all test suites"""
        logger.info("Starting comprehensive agent testing")
        self.overall_start_time = time.time()
        
        # Determine which suites to run
        suites_to_run = selected_suites or [name for name, config in self.test_suites.items() if config.enabled]
        
        # Validate dependencies
        validated_suites = self._validate_dependencies(suites_to_run)
        
        logger.info(f"Running {len(validated_suites)} test suites: {', '.join(validated_suites)}")
        
        # Execute test suites
        suite_results = {}
        
        if self.config.get('execution', {}).get('parallel_execution', True):
            suite_results = await self._run_suites_parallel(validated_suites)
        else:
            suite_results = await self._run_suites_sequential(validated_suites)
        
        self.overall_end_time = time.time()
        
        # Generate comprehensive report
        final_report = await self._generate_final_report(suite_results)
        
        # Save results
        await self._save_results(final_report)
        
        logger.info(f"Comprehensive testing completed in {self.overall_end_time - self.overall_start_time:.2f}s")
        return final_report
    
    def _validate_dependencies(self, suites_to_run: List[str]) -> List[str]:
        """Validate and order test suites based on dependencies"""
        validated = []
        pending = set(suites_to_run)
        
        while pending:
            progress_made = False
            
            for suite_name in list(pending):
                suite_config = self.test_suites[suite_name]
                
                # Check if all dependencies are satisfied
                dependencies_satisfied = all(
                    dep in validated for dep in suite_config.dependencies
                )
                
                if dependencies_satisfied:
                    validated.append(suite_name)
                    pending.remove(suite_name)
                    progress_made = True
            
            if not progress_made and pending:
                # Circular dependencies or missing dependencies
                logger.warning(f"Cannot resolve dependencies for: {pending}")
                # Add remaining suites anyway
                validated.extend(pending)
                break
        
        return validated
    
    async def _run_suites_parallel(self, suites_to_run: List[str]) -> Dict[str, Any]:
        """Run test suites in parallel where possible"""
        logger.info("Running test suites in parallel")
        
        results = {}
        
        # Group suites by dependency level
        dependency_levels = self._group_by_dependency_level(suites_to_run)
        
        for level, suite_names in dependency_levels.items():
            logger.info(f"Running dependency level {level}: {', '.join(suite_names)}")
            
            # Run suites at the same dependency level in parallel
            level_tasks = []
            for suite_name in suite_names:
                task = asyncio.create_task(self._run_single_suite(suite_name))
                level_tasks.append((suite_name, task))
            
            # Wait for all tasks at this level to complete
            for suite_name, task in level_tasks:
                try:
                    result = await task
                    results[suite_name] = result
                except Exception as e:
                    logger.error(f"Suite {suite_name} failed: {e}")
                    results[suite_name] = {
                        'status': 'ERROR',
                        'error': str(e),
                        'execution_time': 0
                    }
        
        return results
    
    async def _run_suites_sequential(self, suites_to_run: List[str]) -> Dict[str, Any]:
        """Run test suites sequentially"""
        logger.info("Running test suites sequentially")
        
        results = {}
        
        for suite_name in suites_to_run:
            try:
                result = await self._run_single_suite(suite_name)
                results[suite_name] = result
            except Exception as e:
                logger.error(f"Suite {suite_name} failed: {e}")
                results[suite_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'execution_time': 0
                }
        
        return results
    
    def _group_by_dependency_level(self, suites_to_run: List[str]) -> Dict[int, List[str]]:
        """Group suites by dependency level for parallel execution"""
        levels = {}
        suite_levels = {}
        
        def calculate_level(suite_name: str) -> int:
            if suite_name in suite_levels:
                return suite_levels[suite_name]
            
            suite_config = self.test_suites[suite_name]
            if not suite_config.dependencies:
                level = 0
            else:
                max_dep_level = max(
                    calculate_level(dep) for dep in suite_config.dependencies
                    if dep in suites_to_run
                )
                level = max_dep_level + 1
            
            suite_levels[suite_name] = level
            return level
        
        # Calculate levels for all suites
        for suite_name in suites_to_run:
            level = calculate_level(suite_name)
            if level not in levels:
                levels[level] = []
            levels[level].append(suite_name)
        
        return levels
    
    async def _run_single_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a single test suite"""
        suite_config = self.test_suites[suite_name]
        
        logger.info(f"Starting test suite: {suite_name}")
        execution = TestExecution(
            suite_name=suite_name,
            start_time=time.time(),
            end_time=None,
            status='RUNNING',
            results=None,
            error=None
        )
        self.test_executions.append(execution)
        
        try:
            # Execute the appropriate test method
            if suite_name == 'individual_operations':
                result = await self.test_framework.test_individual_agent_operations()
            elif suite_name == 'inter_agent_communication':
                result = await self.test_framework.test_inter_agent_communication()
            elif suite_name == 'context_preservation':
                result = await self.test_framework.test_context_preservation()
            elif suite_name == 'error_scenarios':
                result = await self.test_framework.test_error_scenarios()
            elif suite_name == 'performance_benchmarks':
                result = await self.test_framework.test_performance_benchmarks()
            elif suite_name == 'load_testing':
                result = await self._run_load_testing()
            elif suite_name == 'integration_testing':
                result = await self._run_integration_testing()
            else:
                raise ValueError(f"Unknown test suite: {suite_name}")
            
            execution.status = 'COMPLETED'
            execution.results = result
            
            logger.info(f"Test suite {suite_name} completed successfully")
            
        except asyncio.TimeoutError:
            execution.status = 'TIMEOUT'
            execution.error = f"Test suite timed out after {suite_config.timeout}s"
            logger.error(f"Test suite {suite_name} timed out")
            
        except Exception as e:
            execution.status = 'FAILED'
            execution.error = str(e)
            logger.error(f"Test suite {suite_name} failed: {e}")
            
        finally:
            execution.end_time = time.time()
        
        return {
            'status': execution.status,
            'execution_time': execution.end_time - execution.start_time,
            'results': execution.results,
            'error': execution.error
        }
    
    async def _run_load_testing(self) -> Dict[str, Any]:
        """Run load testing scenarios"""
        load_config = self.config.get('load_testing', {})
        if not load_config.get('enabled', True):
            return {'status': 'SKIPPED', 'reason': 'Load testing disabled'}
        
        scenarios = load_config.get('scenarios', {})
        results = {}
        
        for scenario_name, scenario_config in scenarios.items():
            logger.info(f"Running load test scenario: {scenario_name}")
            
            # Use the load tester from extended framework
            load_result = await self.test_framework.load_tester.run_load_test(scenario_config)
            results[scenario_name] = load_result
        
        return results
    
    async def _run_integration_testing(self) -> Dict[str, Any]:
        """Run integration testing scenarios"""
        integration_config = self.config.get('integration_testing', {})
        if not integration_config.get('enabled', True):
            return {'status': 'SKIPPED', 'reason': 'Integration testing disabled'}
        
        scenarios = integration_config.get('core_scenarios', [])
        results = {}
        
        for scenario in scenarios:
            if scenario.get('enabled', True):
                scenario_name = scenario['name']
                logger.info(f"Running integration scenario: {scenario_name}")
                
                # Use the integration orchestrator from extended framework
                integration_result = await self.test_framework.integration_orchestrator.run_integration_scenario(scenario_name)
                results[scenario_name] = integration_result
        
        return results
    
    async def _generate_final_report(self, suite_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        total_execution_time = self.overall_end_time - self.overall_start_time
        
        # Calculate overall statistics
        total_suites = len(suite_results)
        completed_suites = sum(1 for r in suite_results.values() if r['status'] == 'COMPLETED')
        failed_suites = sum(1 for r in suite_results.values() if r['status'] == 'FAILED')
        error_suites = sum(1 for r in suite_results.values() if r['status'] == 'ERROR')
        timeout_suites = sum(1 for r in suite_results.values() if r['status'] == 'TIMEOUT')
        
        overall_success_rate = completed_suites / total_suites if total_suites > 0 else 0.0
        
        # Determine overall status
        if failed_suites > 0 or error_suites > 0:
            overall_status = 'FAILED'
        elif timeout_suites > 0:
            overall_status = 'PARTIAL'
        elif completed_suites == total_suites:
            overall_status = 'PASSED'
        else:
            overall_status = 'UNKNOWN'
        
        # Collect critical failures
        critical_failures = []
        for suite_name, result in suite_results.items():
            suite_config = self.test_suites[suite_name]
            if suite_config.critical and result['status'] != 'COMPLETED':
                critical_failures.append({
                    'suite': suite_name,
                    'status': result['status'],
                    'error': result.get('error')
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(suite_results, critical_failures)
        
        report = {
            'summary': {
                'overall_status': overall_status,
                'total_execution_time': total_execution_time,
                'total_suites': total_suites,
                'completed_suites': completed_suites,
                'failed_suites': failed_suites,
                'error_suites': error_suites,
                'timeout_suites': timeout_suites,
                'success_rate': overall_success_rate,
                'critical_failures': len(critical_failures)
            },
            'suite_results': suite_results,
            'critical_failures': critical_failures,
            'recommendations': recommendations,
            'test_environment': {
                'total_agents': len(self.test_framework.agents),
                'core_agents': len([a for a in self.test_framework.agents if a.tier != 'BMAD']),
                'bmad_agents': len([a for a in self.test_framework.agents if a.tier == 'BMAD']),
                'configuration': self.config.get('execution', {}),
                'timestamp': time.time()
            },
            'detailed_results': {
                'test_executions': [
                    {
                        'suite': exec.suite_name,
                        'start_time': exec.start_time,
                        'end_time': exec.end_time,
                        'status': exec.status,
                        'error': exec.error
                    }
                    for exec in self.test_executions
                ]
            }
        }
        
        return report
    
    def _generate_recommendations(self, suite_results: Dict[str, Any], critical_failures: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Critical failures
        if critical_failures:
            recommendations.append(f"URGENT: Address {len(critical_failures)} critical test failures before deployment")
            for failure in critical_failures:
                recommendations.append(f"- Fix {failure['suite']} suite: {failure['status']}")
        
        # Performance issues
        slow_suites = [
            name for name, result in suite_results.items()
            if result.get('execution_time', 0) > self.test_suites[name].timeout * 0.8
        ]
        if slow_suites:
            recommendations.append(f"Investigate performance issues in: {', '.join(slow_suites)}")
        
        # Error patterns
        error_suites = [name for name, result in suite_results.items() if result['status'] == 'ERROR']
        if error_suites:
            recommendations.append(f"Debug and fix errors in: {', '.join(error_suites)}")
        
        # Timeout issues
        timeout_suites = [name for name, result in suite_results.items() if result['status'] == 'TIMEOUT']
        if timeout_suites:
            recommendations.append(f"Increase timeout or optimize: {', '.join(timeout_suites)}")
        
        # Success case
        if not recommendations:
            recommendations.extend([
                "All tests passed successfully!",
                "Consider running additional stress tests",
                "Monitor performance trends over time",
                "Update baselines with current performance metrics"
            ])
        
        return recommendations
    
    async def _save_results(self, report: Dict[str, Any]):
        """Save test results and generate reports"""
        # Save JSON report
        reports_dir = Path(self.config.get('reporting', {}).get('output_path', 'tests/reports'))
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # JSON report
        json_file = reports_dir / f"test-results-{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test results saved to {json_file}")
        
        # Generate additional report formats
        if self.config.get('reporting', {}).get('enabled', True):
            await self.reporter.generate_reports(report, timestamp)


class TestReporter:
    """Generate test reports in various formats"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reporting_config = config.get('reporting', {})
    
    async def generate_reports(self, report: Dict[str, Any], timestamp: str):
        """Generate reports in configured formats"""
        formats = self.reporting_config.get('formats', ['html', 'json'])
        output_path = Path(self.reporting_config.get('output_path', 'tests/reports'))
        
        for format_type in formats:
            try:
                if format_type == 'html':
                    await self._generate_html_report(report, output_path, timestamp)
                elif format_type == 'junit':
                    await self._generate_junit_report(report, output_path, timestamp)
                elif format_type == 'csv':
                    await self._generate_csv_report(report, output_path, timestamp)
            except Exception as e:
                logger.error(f"Failed to generate {format_type} report: {e}")
    
    async def _generate_html_report(self, report: Dict[str, Any], output_path: Path, timestamp: str):
        """Generate HTML report"""
        html_content = self._create_html_content(report)
        
        html_file = output_path / f"test-report-{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {html_file}")
    
    def _create_html_content(self, report: Dict[str, Any]) -> str:
        """Create HTML report content"""
        summary = report['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Test Report - V3.6.9</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .status-passed {{ background-color: #d4edda; color: #155724; }}
        .status-failed {{ background-color: #f8d7da; color: #721c24; }}
        .status-partial {{ background-color: #fff3cd; color: #856404; }}
        .suite-results {{ margin: 20px 0; }}
        .suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .recommendations {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Agent Test Report - V3.6.9</h1>
        <p>Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="metric status-{summary['overall_status'].lower()}">
            <h3>Overall Status</h3>
            <div>{summary['overall_status']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div>{summary['success_rate']:.1%}</div>
        </div>
        <div class="metric">
            <h3>Total Suites</h3>
            <div>{summary['total_suites']}</div>
        </div>
        <div class="metric">
            <h3>Execution Time</h3>
            <div>{summary['total_execution_time']:.1f}s</div>
        </div>
    </div>
    
    <div class="suite-results">
        <h2>Test Suite Results</h2>
"""
        
        for suite_name, suite_result in report['suite_results'].items():
            status_class = f"status-{suite_result['status'].lower()}"
            html += f"""
        <div class="suite {status_class}">
            <h3>{suite_name.replace('_', ' ').title()}</h3>
            <p>Status: {suite_result['status']}</p>
            <p>Execution Time: {suite_result.get('execution_time', 0):.1f}s</p>
            {f"<p>Error: {suite_result['error']}</p>" if suite_result.get('error') else ""}
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for recommendation in report['recommendations']:
            html += f"            <li>{recommendation}</li>\n"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html
    
    async def _generate_junit_report(self, report: Dict[str, Any], output_path: Path, timestamp: str):
        """Generate JUnit XML report"""
        import xml.etree.ElementTree as ET
        
        testsuites = ET.Element('testsuites')
        testsuites.set('name', 'Agent Tests V3.6.9')
        testsuites.set('tests', str(report['summary']['total_suites']))
        testsuites.set('failures', str(report['summary']['failed_suites']))
        testsuites.set('errors', str(report['summary']['error_suites']))
        testsuites.set('time', str(report['summary']['total_execution_time']))
        
        for suite_name, suite_result in report['suite_results'].items():
            testsuite = ET.SubElement(testsuites, 'testsuite')
            testsuite.set('name', suite_name)
            testsuite.set('tests', '1')
            testsuite.set('time', str(suite_result.get('execution_time', 0)))
            
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', suite_name)
            testcase.set('classname', 'AgentTests')
            testcase.set('time', str(suite_result.get('execution_time', 0)))
            
            if suite_result['status'] == 'FAILED':
                failure = ET.SubElement(testcase, 'failure')
                failure.set('message', suite_result.get('error', 'Test failed'))
                failure.text = suite_result.get('error', 'Test failed')
            elif suite_result['status'] == 'ERROR':
                error = ET.SubElement(testcase, 'error')
                error.set('message', suite_result.get('error', 'Test error'))
                error.text = suite_result.get('error', 'Test error')
        
        xml_file = output_path / f"junit-results-{timestamp}.xml"
        tree = ET.ElementTree(testsuites)
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        
        logger.info(f"JUnit report generated: {xml_file}")
    
    async def _generate_csv_report(self, report: Dict[str, Any], output_path: Path, timestamp: str):
        """Generate CSV report"""
        import csv
        
        csv_file = output_path / f"test-results-{timestamp}.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Suite Name', 'Status', 'Execution Time', 'Error'])
            
            # Data rows
            for suite_name, suite_result in report['suite_results'].items():
                writer.writerow([
                    suite_name,
                    suite_result['status'],
                    suite_result.get('execution_time', 0),
                    suite_result.get('error', '')
                ])
        
        logger.info(f"CSV report generated: {csv_file}")


async def main():
    """Main function for test runner"""
    parser = argparse.ArgumentParser(description='Comprehensive Agent Test Runner')
    parser.add_argument('--config', default='tests/config/test-config.yaml',
                      help='Path to test configuration file')
    parser.add_argument('--suites', nargs='*',
                      help='Specific test suites to run (default: all enabled)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose logging')
    parser.add_argument('--output', help='Output directory for reports')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize test runner
        runner = ComprehensiveTestRunner(args.config)
        
        if args.output:
            runner.config['reporting']['output_path'] = args.output
        
        # Run tests
        results = await runner.run_all_tests(args.suites)
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE AGENT TEST RESULTS")
        print("="*60)
        print(f"Overall Status: {results['summary']['overall_status']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1%}")
        print(f"Total Execution Time: {results['summary']['total_execution_time']:.1f}s")
        print(f"Suites: {results['summary']['completed_suites']}/{results['summary']['total_suites']} completed")
        
        if results['critical_failures']:
            print(f"\n❌ CRITICAL FAILURES: {len(results['critical_failures'])}")
            for failure in results['critical_failures']:
                print(f"  - {failure['suite']}: {failure['status']}")
        
        print(f"\n📊 Reports saved to: {runner.config.get('reporting', {}).get('output_path', 'tests/reports')}")
        
        # Exit with appropriate code
        if results['summary']['overall_status'] == 'FAILED':
            sys.exit(1)
        elif results['summary']['overall_status'] == 'PARTIAL':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"❌ Test execution failed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())