#!/usr/bin/env python3
"""
Quality Gate Validation for Agent Test Suite
Validates test results against defined quality thresholds
"""

import json
import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityGateValidator:
    """Validates test results against quality gates"""
    
    def __init__(self, config_path: str = "tests/config/test-config.yaml"):
        self.config = self._load_config(config_path)
        self.quality_gates = self.config.get('ci_cd', {}).get('quality_gates', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            return {}
    
    def validate_results(self, results_file: str) -> Dict[str, Any]:
        """Validate test results against quality gates"""
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            logger.error(f"Results file {results_file} not found")
            return {'overall_passed': False, 'error': 'Results file not found'}
        
        validation_results = {
            'overall_passed': True,
            'gate_results': {},
            'violations': [],
            'recommendations': []
        }
        
        # Test Coverage Gate
        coverage_result = self._validate_test_coverage(results)
        validation_results['gate_results']['test_coverage'] = coverage_result
        if not coverage_result['passed']:
            validation_results['overall_passed'] = False
            validation_results['violations'].append('Test coverage below threshold')
        
        # Failure Rate Gate
        failure_result = self._validate_failure_rate(results)
        validation_results['gate_results']['failure_rate'] = failure_result
        if not failure_result['passed']:
            validation_results['overall_passed'] = False
            validation_results['violations'].append('Failure rate above threshold')
        
        # Performance Gate
        performance_result = self._validate_performance(results)
        validation_results['gate_results']['performance'] = performance_result
        if not performance_result['passed']:
            validation_results['overall_passed'] = False
            validation_results['violations'].append('Performance below threshold')
        
        # Critical Failures Gate
        critical_result = self._validate_critical_failures(results)
        validation_results['gate_results']['critical_failures'] = critical_result
        if not critical_result['passed']:
            validation_results['overall_passed'] = False
            validation_results['violations'].append('Critical failures detected')
        
        # Regression Gate
        regression_result = self._validate_regressions(results)
        validation_results['gate_results']['regressions'] = regression_result
        if not regression_result['passed']:
            validation_results['overall_passed'] = False
            validation_results['violations'].append('Too many regressions detected')
        
        # Generate recommendations
        validation_results['recommendations'] = self._generate_recommendations(validation_results)
        
        return validation_results
    
    def _validate_test_coverage(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test coverage threshold"""
        threshold = self.quality_gates.get('minimum_test_coverage', 0.8)
        
        # Calculate coverage from results
        total_agents = results.get('test_environment', {}).get('total_agents', 37)
        tested_agents = 0
        
        # Count successfully tested agents from individual operations
        individual_results = results.get('suite_results', {}).get('individual_operations', {})
        if individual_results and individual_results.get('status') == 'COMPLETED':
            agent_results = individual_results.get('results', {})
            tested_agents = sum(1 for result in agent_results.values() 
                              if result.get('overall_status') in ['PASS', 'PARTIAL'])
        
        actual_coverage = tested_agents / total_agents if total_agents > 0 else 0.0
        passed = actual_coverage >= threshold
        
        return {
            'passed': passed,
            'threshold': threshold,
            'actual': actual_coverage,
            'tested_agents': tested_agents,
            'total_agents': total_agents
        }
    
    def _validate_failure_rate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate failure rate threshold"""
        threshold = self.quality_gates.get('maximum_failure_rate', 0.05)
        
        summary = results.get('summary', {})
        success_rate = summary.get('success_rate', 1.0)
        actual_failure_rate = 1.0 - success_rate
        
        passed = actual_failure_rate <= threshold
        
        return {
            'passed': passed,
            'threshold': threshold,
            'actual': actual_failure_rate,
            'success_rate': success_rate
        }
    
    def _validate_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance threshold"""
        threshold = self.quality_gates.get('minimum_performance_score', 0.75)
        
        # Calculate performance score from benchmark results
        performance_results = results.get('suite_results', {}).get('performance_benchmarks', {})
        
        if performance_results and performance_results.get('status') == 'COMPLETED':
            benchmark_data = performance_results.get('results', {})
            if 'single_agent_performance' in benchmark_data:
                performance_score = benchmark_data['single_agent_performance'].get('performance_score', 1.0)
            else:
                performance_score = 0.8  # Default if no specific score
        else:
            performance_score = 0.0  # No performance data available
        
        passed = performance_score >= threshold
        
        return {
            'passed': passed,
            'threshold': threshold,
            'actual': performance_score
        }
    
    def _validate_critical_failures(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate critical failures"""
        critical_failures = results.get('critical_failures', [])
        max_critical = self.quality_gates.get('maximum_critical_failures', 0)
        
        actual_critical = len(critical_failures)
        passed = actual_critical <= max_critical
        
        return {
            'passed': passed,
            'threshold': max_critical,
            'actual': actual_critical,
            'failures': critical_failures
        }
    
    def _validate_regressions(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate regression count"""
        threshold = self.quality_gates.get('maximum_regression_count', 3)
        
        # Look for regression data in performance results
        performance_results = results.get('suite_results', {}).get('performance_benchmarks', {})
        regression_count = 0
        
        if performance_results and performance_results.get('status') == 'COMPLETED':
            benchmark_data = performance_results.get('results', {})
            if 'single_agent_performance' in benchmark_data:
                regression_count = benchmark_data['single_agent_performance'].get('regression_count', 0)
        
        passed = regression_count <= threshold
        
        return {
            'passed': passed,
            'threshold': threshold,
            'actual': regression_count
        }
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        gate_results = validation_results['gate_results']
        
        # Test coverage recommendations
        coverage = gate_results.get('test_coverage', {})
        if not coverage.get('passed', True):
            recommendations.append(
                f"Increase test coverage from {coverage.get('actual', 0):.1%} to "
                f"{coverage.get('threshold', 0.8):.1%} by testing more agents"
            )
        
        # Failure rate recommendations
        failure_rate = gate_results.get('failure_rate', {})
        if not failure_rate.get('passed', True):
            recommendations.append(
                f"Reduce failure rate from {failure_rate.get('actual', 0):.1%} to "
                f"below {failure_rate.get('threshold', 0.05):.1%} by fixing failing tests"
            )
        
        # Performance recommendations
        performance = gate_results.get('performance', {})
        if not performance.get('passed', True):
            recommendations.append(
                f"Improve performance score from {performance.get('actual', 0):.1%} to "
                f"above {performance.get('threshold', 0.75):.1%} by optimizing slow agents"
            )
        
        # Critical failure recommendations
        critical = gate_results.get('critical_failures', {})
        if not critical.get('passed', True):
            recommendations.append(
                f"Fix {critical.get('actual', 0)} critical failures before proceeding"
            )
        
        # Regression recommendations
        regressions = gate_results.get('regressions', {})
        if not regressions.get('passed', True):
            recommendations.append(
                f"Address {regressions.get('actual', 0)} performance regressions"
            )
        
        # Success recommendations
        if validation_results['overall_passed']:
            recommendations.extend([
                "All quality gates passed successfully!",
                "Consider updating baselines with current performance metrics",
                "Monitor trends to maintain quality standards"
            ])
        
        return recommendations
    
    def get_latest_results_file(self) -> str:
        """Get the latest test results file"""
        reports_dir = Path("tests/reports")
        if not reports_dir.exists():
            raise FileNotFoundError("Reports directory not found")
        
        # Find the latest JSON results file
        json_files = list(reports_dir.glob("test-results-*.json"))
        if not json_files:
            raise FileNotFoundError("No test results files found")
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)
    
    def print_validation_summary(self, validation_results: Dict[str, Any]):
        """Print validation summary to console"""
        print("\n" + "="*60)
        print("QUALITY GATE VALIDATION RESULTS")
        print("="*60)
        
        overall_status = "PASSED" if validation_results['overall_passed'] else "FAILED"
        print(f"Overall Status: {overall_status}")
        
        print(f"\n📊 Gate Results:")
        for gate_name, gate_result in validation_results['gate_results'].items():
            status = "✅ PASS" if gate_result['passed'] else "❌ FAIL"
            threshold = gate_result.get('threshold', 'N/A')
            actual = gate_result.get('actual', 'N/A')
            
            if isinstance(actual, float):
                if gate_name in ['test_coverage', 'failure_rate', 'performance']:
                    actual_str = f"{actual:.1%}"
                else:
                    actual_str = f"{actual:.2f}"
            else:
                actual_str = str(actual)
            
            if isinstance(threshold, float):
                if gate_name in ['test_coverage', 'failure_rate', 'performance']:
                    threshold_str = f"{threshold:.1%}"
                else:
                    threshold_str = f"{threshold:.2f}"
            else:
                threshold_str = str(threshold)
            
            print(f"  {status} {gate_name.replace('_', ' ').title()}: {actual_str} (threshold: {threshold_str})")
        
        if validation_results['violations']:
            print(f"\n❌ Violations:")
            for violation in validation_results['violations']:
                print(f"  - {violation}")
        
        if validation_results['recommendations']:
            print(f"\n💡 Recommendations:")
            for recommendation in validation_results['recommendations']:
                print(f"  - {recommendation}")
        
        print("="*60)


def main():
    """Main function for quality gate validation"""
    parser = argparse.ArgumentParser(description='Validate Agent Test Quality Gates')
    parser.add_argument('--results', help='Test results file (default: latest)')
    parser.add_argument('--config', default='tests/config/test-config.yaml',
                      help='Test configuration file')
    parser.add_argument('--json', action='store_true',
                      help='Output results as JSON')
    parser.add_argument('--fail-on-violation', action='store_true',
                      help='Exit with error code if gates fail')
    parser.add_argument('--quiet', action='store_true',
                      help='Suppress detailed output')
    
    args = parser.parse_args()
    
    try:
        validator = QualityGateValidator(args.config)
        
        # Get results file
        if args.results:
            results_file = args.results
        else:
            results_file = validator.get_latest_results_file()
            if not args.quiet:
                print(f"Using latest results file: {results_file}")
        
        # Validate results
        validation_results = validator.validate_results(results_file)
        
        # Output results
        if args.json:
            print(json.dumps(validation_results, indent=2))
        elif not args.quiet:
            validator.print_validation_summary(validation_results)
        
        # Exit with appropriate code
        if args.fail_on_violation and not validation_results['overall_passed']:
            if not args.quiet:
                print("\n❌ Quality gates failed - exiting with error code 1")
            sys.exit(1)
        elif validation_results['overall_passed']:
            if not args.quiet:
                print("\n✅ All quality gates passed!")
            sys.exit(0)
        else:
            if not args.quiet:
                print("\n⚠️  Quality gates failed but not failing pipeline")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Quality gate validation failed: {e}")
        if args.json:
            print(json.dumps({'error': str(e), 'overall_passed': False}))
        else:
            print(f"❌ Validation error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()