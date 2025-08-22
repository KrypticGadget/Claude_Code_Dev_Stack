#!/usr/bin/env python3
"""
Hook Priority System Integration Test Suite
Comprehensive test suite for validating the sophisticated hook priority system functionality.

Author: Claude Technical Specifications Agent
Version: 1.0.0
"""

import unittest
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the hook priority system components
from hook_priority_system import (
    HookPrioritySystem, ConflictResolutionStrategy, ExecutionPhase, 
    RollbackScope, PriorityWeight, create_hook_priority_system
)
from hook_registry import (
    HookMetadata, HookPriority, HookState, TriggerType, HookRegistry
)
from priority_system_config import ConfigurationManager, PrioritySystemConfig
from priority_system_api import PrioritySystemAPI


class TestHookPrioritySystem(unittest.TestCase):
    """Test cases for the core hook priority system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_registry = Mock(spec=HookRegistry)
        self.mock_registry.hooks = {}
        
        # Create test hooks
        self.test_hooks = self._create_test_hooks()
        self.mock_registry.hooks.update(self.test_hooks)
        
        # Create priority system
        self.priority_system = create_hook_priority_system(
            self.mock_registry,
            config={
                'conflict_strategy': 'priority_based',
                'max_workers': 4,
                'enable_rollback': True
            }
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        if hasattr(self.priority_system, 'shutdown'):
            self.priority_system.shutdown()
    
    def _create_test_hooks(self) -> Dict[str, HookMetadata]:
        """Create test hook metadata"""
        hooks = {}
        
        hook_configs = [
            {
                'name': 'validator',
                'priority': HookPriority.CRITICAL,
                'dependencies': [],
                'provides': ['validation'],
                'tags': ['validation', 'critical']
            },
            {
                'name': 'authenticator',
                'priority': HookPriority.HIGH,
                'dependencies': ['validation'],
                'provides': ['authentication'],
                'tags': ['auth', 'security']
            },
            {
                'name': 'processor',
                'priority': HookPriority.NORMAL,
                'dependencies': ['authentication'],
                'provides': ['processing'],
                'tags': ['processing', 'core']
            },
            {
                'name': 'notifier',
                'priority': HookPriority.LOW,
                'dependencies': ['processing'],
                'provides': ['notifications'],
                'tags': ['notifications', 'optional']
            },
            {
                'name': 'logger',
                'priority': HookPriority.LOW,
                'dependencies': ['processing'],
                'provides': ['logging'],
                'tags': ['logging', 'audit']
            }
        ]
        
        for config in hook_configs:
            metadata = HookMetadata(
                name=config['name'],
                file_path=str(self.temp_dir / f"{config['name']}.py"),
                priority=config['priority'],
                dependencies=config['dependencies'],
                provides=config['provides'],
                tags=config['tags'],
                triggers=['test_trigger'],
                state=HookState.ACTIVE
            )
            hooks[config['name']] = metadata
        
        return hooks
    
    def test_priority_calculation(self):
        """Test priority calculation with multiple factors"""
        context = {
            'system_load': 75,
            'time_sensitivity': 'high',
            'dependency_depth': 2
        }
        
        priorities = self.priority_system._calculate_hook_priorities(
            ['validator', 'processor', 'notifier'], context
        )
        
        # Validator should have highest priority (CRITICAL)
        self.assertGreater(priorities['validator'], priorities['processor'])
        self.assertGreater(priorities['processor'], priorities['notifier'])
        
        # All priorities should be positive
        for priority in priorities.values():
            self.assertGreater(priority, 0)
    
    def test_dependency_resolution(self):
        """Test dependency resolution and topological sorting"""
        hook_names = ['validator', 'authenticator', 'processor', 'notifier']
        
        execution_plan = self.priority_system.calculate_execution_order(
            trigger='test_trigger',
            hook_names=hook_names
        )
        
        # Should have multiple batches due to dependencies
        self.assertGreater(len(execution_plan['batches']), 1)
        
        # Validator should be in first batch (no dependencies)
        first_batch = execution_plan['batches'][0]
        self.assertIn('validator', first_batch['hooks'])
        
        # Check dependency order is respected
        hook_positions = {}
        for i, batch in enumerate(execution_plan['batches']):
            for hook in batch['hooks']:
                hook_positions[hook] = i
        
        # Authenticator should come after validator
        self.assertGreater(hook_positions['authenticator'], hook_positions['validator'])
        # Processor should come after authenticator
        self.assertGreater(hook_positions['processor'], hook_positions['authenticator'])
    
    def test_conflict_resolution(self):
        """Test conflict resolution strategies"""
        conflicting_hooks = ['processor', 'notifier', 'logger']
        trigger = 'test_trigger'
        
        # Test priority-based resolution
        resolution = self.priority_system.conflict_resolver.resolve_conflicts(
            trigger, conflicting_hooks, self.test_hooks, 
            ConflictResolutionStrategy.PRIORITY_BASED
        )
        
        # Processor should win (NORMAL priority vs LOW)
        self.assertEqual(resolution.winner, 'processor')
        self.assertEqual(len(resolution.losers), 2)
        
        # Test round-robin resolution
        winners = []
        for _ in range(3):
            resolution = self.priority_system.conflict_resolver.resolve_conflicts(
                trigger, conflicting_hooks, self.test_hooks,
                ConflictResolutionStrategy.ROUND_ROBIN
            )
            winners.append(resolution.winner)
        
        # Should cycle through different winners
        self.assertEqual(len(set(winners)), 3)
    
    def test_parallel_execution_optimization(self):
        """Test parallel execution optimization"""
        # Create execution batches
        from hook_priority_system import ExecutionBatch, ExecutionPhase
        
        batches = [
            ExecutionBatch(
                batch_id='batch_1',
                hooks=['validator'],
                phase=ExecutionPhase.PRE_VALIDATION,
                max_parallelism=1,
                resource_requirements={'cpu_percent': 10, 'memory_mb': 50},
                estimated_duration_ms=1000
            ),
            ExecutionBatch(
                batch_id='batch_2',
                hooks=['authenticator', 'processor'],
                phase=ExecutionPhase.CORE_PROCESSING,
                max_parallelism=2,
                resource_requirements={'cpu_percent': 20, 'memory_mb': 100},
                estimated_duration_ms=2000
            )
        ]
        
        optimized_batches = self.priority_system.execution_optimizer.optimize_execution_plan(batches)
        
        # Should return optimized batches
        self.assertIsInstance(optimized_batches, list)
        self.assertGreater(len(optimized_batches), 0)
        
        # Check resource optimization was applied
        for batch in optimized_batches:
            self.assertGreater(batch.max_parallelism, 0)
    
    def test_rollback_mechanism(self):
        """Test rollback transaction management"""
        affected_hooks = ['validator', 'authenticator', 'processor']
        
        # Create transaction
        transaction_id = self.priority_system.rollback_manager.create_transaction(
            RollbackScope.DEPENDENCY_CHAIN, affected_hooks
        )
        
        self.assertIsNotNone(transaction_id)
        self.assertIn(transaction_id, self.priority_system.rollback_manager.active_transactions)
        
        # Add snapshots
        for hook in affected_hooks:
            success = self.priority_system.rollback_manager.add_snapshot(
                transaction_id, hook, {'test_state': f'state_{hook}'}
            )
            self.assertTrue(success)
        
        # Add rollback action
        rollback_called = False
        def test_rollback_action():
            nonlocal rollback_called
            rollback_called = True
        
        success = self.priority_system.rollback_manager.add_rollback_action(
            transaction_id, test_rollback_action
        )
        self.assertTrue(success)
        
        # Execute rollback
        rollback_success = self.priority_system.rollback_manager.rollback(transaction_id)
        self.assertTrue(rollback_success)
        self.assertTrue(rollback_called)
        
        # Transaction should be cleaned up
        self.assertNotIn(transaction_id, self.priority_system.rollback_manager.active_transactions)
    
    def test_performance_optimization(self):
        """Test performance optimization features"""
        # Add some performance history
        for hook_name in ['validator', 'processor']:
            for i in range(10):
                self.priority_system.performance_history[hook_name].append({
                    'timestamp': f'2024-01-01T{i:02d}:00:00',
                    'execution_time_ms': 1000 + (i * 100),
                    'success': i < 8,  # 80% success rate
                    'error': None if i < 8 else 'Test error'
                })
        
        # Run optimization
        optimization_result = self.priority_system.optimize_system_performance()
        
        self.assertIn('timestamp', optimization_result)
        self.assertIn('actions_taken', optimization_result)
        self.assertIsInstance(optimization_result['actions_taken'], list)
    
    def test_system_metrics(self):
        """Test system metrics collection"""
        metrics = self.priority_system.get_system_metrics()
        
        required_fields = [
            'timestamp', 'active_executions', 'queue_size',
            'dependency_graph_size', 'performance_history_size',
            'rollback_transactions', 'conflict_resolution_strategy'
        ]
        
        for field in required_fields:
            self.assertIn(field, metrics)
        
        # Check data types
        self.assertIsInstance(metrics['active_executions'], int)
        self.assertIsInstance(metrics['queue_size'], int)
        self.assertIsInstance(metrics['rollback_transactions'], int)


class TestConfigurationManager(unittest.TestCase):
    """Test cases for configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_config.json"
        self.config_manager = ConfigurationManager(str(self.config_file))
    
    def tearDown(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_default_configuration(self):
        """Test default configuration creation"""
        self.assertIsInstance(self.config_manager.config, PrioritySystemConfig)
        self.assertTrue(self.config_manager.config.enabled)
        self.assertGreater(self.config_manager.config.max_workers, 0)
    
    def test_configuration_save_load(self):
        """Test configuration save and load"""
        # Modify configuration
        self.config_manager.config.max_workers = 16
        self.config_manager.config.enable_rollback = False
        
        # Save configuration
        success = self.config_manager.save_configuration()
        self.assertTrue(success)
        self.assertTrue(self.config_file.exists())
        
        # Create new manager and load
        new_manager = ConfigurationManager(str(self.config_file))
        self.assertEqual(new_manager.config.max_workers, 16)
        self.assertEqual(new_manager.config.enable_rollback, False)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test valid configuration
        issues = self.config_manager.validate_configuration()
        self.assertEqual(len(issues), 0)
        
        # Test invalid configuration
        self.config_manager.config.max_workers = -1
        self.config_manager.config.priority_weights = {'invalid': 2.0}
        
        issues = self.config_manager.validate_configuration()
        self.assertGreater(len(issues), 0)
        
        # Check specific issues
        self.assertTrue(any('max_workers' in issue for issue in issues))
        self.assertTrue(any('weights' in issue for issue in issues))
    
    def test_configuration_update(self):
        """Test configuration updates"""
        updates = {
            'max_workers': 12,
            'enable_dynamic_priority_adjustment': False,
            'optimization_interval_seconds': 600
        }
        
        success = self.config_manager.update_configuration(updates)
        self.assertTrue(success)
        
        # Verify updates
        self.assertEqual(self.config_manager.config.max_workers, 12)
        self.assertEqual(self.config_manager.config.enable_dynamic_priority_adjustment, False)
        self.assertEqual(self.config_manager.config.optimization_interval_seconds, 600)


class TestPrioritySystemAPI(unittest.TestCase):
    """Test cases for the priority system API"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock hook registry
        self.mock_registry = Mock(spec=HookRegistry)
        self.mock_registry.hooks = self._create_mock_hooks()
        
        # Create API instance
        self.api = PrioritySystemAPI(
            hook_registry=self.mock_registry,
            config={'max_workers': 4, 'enable_rollback': True}
        )
    
    def _create_mock_hooks(self) -> Dict[str, HookMetadata]:
        """Create mock hooks for testing"""
        hooks = {}
        hook_names = ['validator', 'processor', 'finalizer']
        
        for i, name in enumerate(hook_names):
            metadata = HookMetadata(
                name=name,
                file_path=f"/tmp/{name}.py",
                priority=HookPriority.NORMAL,
                dependencies=[hook_names[i-1]] if i > 0 else [],
                provides=[f"{name}_output"],
                tags=['test'],
                triggers=['test_trigger'],
                state=HookState.ACTIVE
            )
            hooks[name] = metadata
        
        return hooks
    
    def test_calculate_execution_order(self):
        """Test execution order calculation via API"""
        execution_plan = self.api.calculate_execution_order(
            trigger='test_trigger',
            hook_names=['validator', 'processor', 'finalizer'],
            context={'test': True}
        )
        
        self.assertIn('batches', execution_plan)
        self.assertIn('total_estimated_time_ms', execution_plan)
        self.assertIsInstance(execution_plan['batches'], list)
        self.assertGreater(execution_plan['total_estimated_time_ms'], 0)
    
    def test_conflict_resolution_api(self):
        """Test conflict resolution via API"""
        resolution = self.api.resolve_conflicts(
            trigger='test_trigger',
            conflicting_hooks=['validator', 'processor'],
            strategy='priority_based'
        )
        
        required_fields = ['winner', 'losers', 'strategy_used', 'reason', 'timestamp']
        for field in required_fields:
            self.assertIn(field, resolution)
        
        self.assertIn(resolution['winner'], ['validator', 'processor'])
        self.assertEqual(resolution['strategy_used'], 'priority_based')
    
    def test_rollback_transaction_api(self):
        """Test rollback transaction management via API"""
        affected_hooks = ['validator', 'processor']
        
        # Create transaction
        transaction_id = self.api.create_rollback_transaction(
            scope='dependency_chain',
            affected_hooks=affected_hooks
        )
        
        self.assertIsNotNone(transaction_id)
        
        # Test rollback
        success = self.api.rollback_transaction(transaction_id)
        self.assertTrue(success)
    
    def test_system_metrics_api(self):
        """Test system metrics via API"""
        metrics = self.api.get_system_metrics()
        
        self.assertIn('api_metrics', metrics)
        self.assertIn('total_api_executions', metrics['api_metrics'])
        self.assertIn('recent_success_rate', metrics['api_metrics'])
        self.assertIn('average_execution_time_ms', metrics['api_metrics'])
    
    def test_performance_optimization_api(self):
        """Test performance optimization via API"""
        # Add some execution history
        for _ in range(5):
            self.api._execution_history.append({
                'timestamp': '2024-01-01T10:00:00',
                'trigger': 'test',
                'hooks_count': 3,
                'success': True,
                'execution_time_ms': 1000
            })
        
        optimization = self.api.optimize_performance()
        
        self.assertIn('timestamp', optimization)
        self.assertIn('actions_taken', optimization)
    
    def test_execution_history_tracking(self):
        """Test execution history tracking"""
        initial_count = len(self.api.get_execution_history())
        
        # Mock execution
        self.api._execution_history.append({
            'timestamp': '2024-01-01T10:00:00',
            'trigger': 'test',
            'hooks_count': 2,
            'success': True,
            'execution_time_ms': 500
        })
        
        history = self.api.get_execution_history(limit=10)
        self.assertEqual(len(history), initial_count + 1)
        
        # Test limit functionality
        limited_history = self.api.get_execution_history(limit=1)
        self.assertEqual(len(limited_history), 1)
    
    def test_performance_trends_analysis(self):
        """Test performance trends analysis"""
        # Add varied execution history
        for i in range(20):
            self.api._execution_history.append({
                'timestamp': f'2024-01-01T{i:02d}:00:00',
                'trigger': 'test',
                'hooks_count': 3,
                'success': i % 5 != 0,  # 80% success rate
                'execution_time_ms': 1000 + (i * 50)  # Increasing execution time
            })
        
        trends = self.api.analyze_performance_trends(window_size=15)
        
        required_fields = [
            'window_size', 'success_rate_trend', 'performance_trend',
            'current_success_rate', 'avg_execution_time_ms', 'execution_count'
        ]
        
        for field in required_fields:
            self.assertIn(field, trends)
        
        self.assertEqual(trends['window_size'], 15)
        self.assertIn(trends['performance_trend'], ['improving', 'declining', 'stable'])


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create realistic hook registry
        self.registry = Mock(spec=HookRegistry)
        self.registry.hooks = self._create_realistic_hooks()
        
        # Create API with full configuration
        self.api = PrioritySystemAPI(
            hook_registry=self.registry,
            config={
                'max_workers': 8,
                'enable_rollback': True,
                'enable_parallel_optimization': True,
                'conflict_strategy': 'priority_based'
            }
        )
    
    def tearDown(self):
        """Clean up integration test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        if hasattr(self.api, 'shutdown'):
            self.api.shutdown()
    
    def _create_realistic_hooks(self) -> Dict[str, HookMetadata]:
        """Create realistic hooks for integration testing"""
        hooks = {}
        
        hook_configs = [
            # Authentication chain
            {'name': 'request_validator', 'priority': HookPriority.CRITICAL, 'deps': [], 'phase': ExecutionPhase.PRE_VALIDATION},
            {'name': 'auth_manager', 'priority': HookPriority.HIGH, 'deps': ['request_validator'], 'phase': ExecutionPhase.INITIALIZATION},
            {'name': 'session_manager', 'priority': HookPriority.HIGH, 'deps': ['auth_manager'], 'phase': ExecutionPhase.INITIALIZATION},
            
            # Core processing
            {'name': 'data_processor', 'priority': HookPriority.NORMAL, 'deps': ['session_manager'], 'phase': ExecutionPhase.CORE_PROCESSING},
            {'name': 'business_logic', 'priority': HookPriority.NORMAL, 'deps': ['data_processor'], 'phase': ExecutionPhase.CORE_PROCESSING},
            {'name': 'cache_manager', 'priority': HookPriority.NORMAL, 'deps': ['session_manager'], 'phase': ExecutionPhase.CORE_PROCESSING},
            
            # Post processing
            {'name': 'result_formatter', 'priority': HookPriority.LOW, 'deps': ['business_logic'], 'phase': ExecutionPhase.POST_PROCESSING},
            {'name': 'notification_sender', 'priority': HookPriority.LOW, 'deps': ['business_logic'], 'phase': ExecutionPhase.POST_PROCESSING},
            {'name': 'audit_logger', 'priority': HookPriority.MAINTENANCE, 'deps': ['business_logic'], 'phase': ExecutionPhase.POST_PROCESSING},
            
            # Cleanup
            {'name': 'cleanup_service', 'priority': HookPriority.MAINTENANCE, 'deps': [], 'phase': ExecutionPhase.CLEANUP}
        ]
        
        for config in hook_configs:
            metadata = HookMetadata(
                name=config['name'],
                file_path=str(self.temp_dir / f"{config['name']}.py"),
                priority=config['priority'],
                dependencies=config['deps'],
                provides=[f"{config['name']}_output"],
                tags=['integration_test'],
                triggers=['api_request', 'user_action'],
                state=HookState.ACTIVE
            )
            hooks[config['name']] = metadata
        
        return hooks
    
    def test_end_to_end_execution(self):
        """Test end-to-end execution scenario"""
        hook_names = list(self.registry.hooks.keys())
        
        # Calculate execution plan
        execution_plan = self.api.calculate_execution_order(
            trigger='api_request',
            hook_names=hook_names,
            context={
                'user_id': 'test_user',
                'time_sensitivity': 'high',
                'enable_rollback': True
            }
        )
        
        # Verify plan structure
        self.assertGreater(len(execution_plan['batches']), 1)
        self.assertGreater(execution_plan['total_estimated_time_ms'], 0)
        
        # Verify dependency ordering
        executed_hooks = set()
        for batch in execution_plan['batches']:
            for hook_name in batch['hooks']:
                hook_metadata = self.registry.hooks[hook_name]
                for dep in hook_metadata.dependencies:
                    self.assertIn(dep, executed_hooks, 
                                 f"Dependency {dep} not executed before {hook_name}")
                executed_hooks.add(hook_name)
    
    def test_failure_and_rollback_scenario(self):
        """Test failure handling and rollback scenario"""
        critical_hooks = ['request_validator', 'auth_manager', 'data_processor']
        
        # Create rollback transaction
        transaction_id = self.api.create_rollback_transaction(
            scope='dependency_chain',
            affected_hooks=critical_hooks
        )
        
        self.assertIsNotNone(transaction_id)
        
        # Simulate execution with failure
        try:
            # This would normally execute hooks, but we're testing the rollback mechanism
            rollback_success = self.api.rollback_transaction(transaction_id)
            self.assertTrue(rollback_success)
        except Exception as e:
            self.fail(f"Rollback scenario failed: {e}")
    
    def test_high_load_scenario(self):
        """Test system behavior under high load"""
        # Simulate high system load
        high_load_context = {
            'system_load': 90,
            'memory_usage': 85,
            'time_sensitivity': 'urgent',
            'concurrent_requests': 100
        }
        
        # Test with multiple hook sets
        hook_sets = [
            ['request_validator', 'auth_manager', 'session_manager'],
            ['data_processor', 'business_logic', 'cache_manager'],
            ['result_formatter', 'notification_sender', 'audit_logger']
        ]
        
        results = []
        for i, hooks in enumerate(hook_sets):
            execution_plan = self.api.calculate_execution_order(
                trigger=f'high_load_test_{i}',
                hook_names=hooks,
                context=high_load_context
            )
            results.append(execution_plan)
        
        # Verify all plans were generated successfully
        self.assertEqual(len(results), len(hook_sets))
        for result in results:
            self.assertIn('batches', result)
            self.assertGreater(len(result['batches']), 0)
    
    def test_concurrent_execution_scenario(self):
        """Test concurrent execution handling"""
        import threading
        import concurrent.futures
        
        def execute_hook_set(hook_set, trigger_suffix):
            try:
                return self.api.calculate_execution_order(
                    trigger=f'concurrent_test_{trigger_suffix}',
                    hook_names=hook_set,
                    context={'concurrent_test': True}
                )
            except Exception as e:
                return {'error': str(e)}
        
        # Define concurrent hook sets
        concurrent_sets = [
            (['request_validator', 'auth_manager'], 'auth'),
            (['data_processor', 'business_logic'], 'processing'),
            (['result_formatter', 'notification_sender'], 'output'),
            (['cache_manager', 'cleanup_service'], 'maintenance')
        ]
        
        # Execute concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(execute_hook_set, hooks, suffix)
                for hooks, suffix in concurrent_sets
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify all executions completed
        self.assertEqual(len(results), len(concurrent_sets))
        
        # Check for errors
        errors = [r for r in results if 'error' in r]
        self.assertEqual(len(errors), 0, f"Concurrent execution errors: {errors}")


def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🧪 Running Hook Priority System Comprehensive Test Suite")
    print("=" * 70)
    
    # Create test suite
    test_classes = [
        TestHookPrioritySystem,
        TestConfigurationManager,
        TestPrioritySystemAPI,
        TestIntegrationScenarios
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    successful = total_tests - failures - errors - skipped
    
    print(f"Total tests run: {total_tests}")
    print(f"Successful: {successful}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    
    success_rate = (successful / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if failures > 0:
        print(f"\n❌ {failures} test(s) failed:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if errors > 0:
        print(f"\n💥 {errors} test(s) had errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("\n" + "=" * 70)
    if failures == 0 and errors == 0:
        print("🎉 All tests passed! Hook Priority System is ready for production.")
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
    print("=" * 70)
    
    return result


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hook Priority System Test Suite")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--test-class', '-c', type=str, help='Run specific test class')
    parser.add_argument('--test-method', '-m', type=str, help='Run specific test method')
    
    args = parser.parse_args()
    
    if args.test_class:
        # Run specific test class
        if args.test_class in globals():
            test_class = globals()[args.test_class]
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
            runner.run(suite)
        else:
            print(f"Test class '{args.test_class}' not found")
    elif args.test_method:
        # Run specific test method
        suite = unittest.TestLoader().loadTestsFromName(args.test_method)
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        runner.run(suite)
    else:
        # Run comprehensive tests
        run_comprehensive_tests()


if __name__ == "__main__":
    main()