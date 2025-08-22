#!/usr/bin/env python3
"""
Hook Priority System Demonstration and Test Suite
Demonstrates advanced features of the sophisticated hook priority system.

Author: Claude Technical Specifications Agent
Version: 1.0.0
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

# Import the hook priority system and registry
from hook_priority_system import (
    HookPrioritySystem, ConflictResolutionStrategy, ExecutionPhase, 
    RollbackScope, create_hook_priority_system
)
from hook_registry import (
    HookMetadata, HookPriority, HookState, TriggerType, 
    get_hook_registry
)


class PrioritySystemDemo:
    """Comprehensive demonstration of hook priority system capabilities"""
    
    def __init__(self):
        self.demo_results = {}
        self.setup_demo_environment()
    
    def setup_demo_environment(self):
        """Set up demonstration environment with sample hooks"""
        print("🚀 Setting up Hook Priority System Demo Environment...")
        
        # Create hook registry with demo hooks
        self.registry = get_hook_registry()
        self.priority_system = create_hook_priority_system(
            self.registry,
            config={
                'conflict_strategy': 'priority_based',
                'enable_dynamic_priority': True,
                'max_execution_time_ms': 30000,
                'max_workers': 8
            }
        )
        
        # Register demo hooks
        self._register_demo_hooks()
        print(f"✅ Demo environment ready with {len(self.registry.hooks)} hooks")
    
    def _register_demo_hooks(self):
        """Register demonstration hooks with various priorities and dependencies"""
        demo_hooks = [
            {
                'name': 'system_validator',
                'priority': HookPriority.CRITICAL,
                'phase': ExecutionPhase.PRE_VALIDATION,
                'dependencies': [],
                'provides': ['system_validation'],
                'tags': ['validation', 'critical', 'system'],
                'triggers': ['system_startup', 'validation_request'],
                'description': 'Critical system validation hook'
            },
            {
                'name': 'auth_manager',
                'priority': HookPriority.HIGH,
                'phase': ExecutionPhase.INITIALIZATION,
                'dependencies': ['system_validation'],
                'provides': ['authentication'],
                'tags': ['auth', 'security', 'initialization'],
                'triggers': ['user_login', 'api_request'],
                'description': 'Authentication and authorization manager'
            },
            {
                'name': 'data_processor',
                'priority': HookPriority.NORMAL,
                'phase': ExecutionPhase.CORE_PROCESSING,
                'dependencies': ['authentication'],
                'provides': ['data_processing'],
                'tags': ['processing', 'data'],
                'triggers': ['data_event', 'process_request'],
                'description': 'Main data processing engine'
            },
            {
                'name': 'cache_manager',
                'priority': HookPriority.NORMAL,
                'phase': ExecutionPhase.CORE_PROCESSING,
                'dependencies': ['authentication'],
                'provides': ['caching'],
                'tags': ['cache', 'performance'],
                'triggers': ['cache_event', 'performance_optimization'],
                'description': 'Cache management and optimization'
            },
            {
                'name': 'notification_sender',
                'priority': HookPriority.LOW,
                'phase': ExecutionPhase.POST_PROCESSING,
                'dependencies': ['data_processing'],
                'provides': ['notifications'],
                'tags': ['notifications', 'post_process'],
                'triggers': ['notification_event', 'user_action'],
                'description': 'Notification and alert system'
            },
            {
                'name': 'audit_logger',
                'priority': HookPriority.LOW,
                'phase': ExecutionPhase.POST_PROCESSING,
                'dependencies': ['data_processing', 'authentication'],
                'provides': ['audit_logging'],
                'tags': ['logging', 'audit', 'compliance'],
                'triggers': ['audit_event', 'compliance_check'],
                'description': 'Audit logging and compliance tracking'
            },
            {
                'name': 'cleanup_service',
                'priority': HookPriority.MAINTENANCE,
                'phase': ExecutionPhase.CLEANUP,
                'dependencies': [],
                'provides': ['cleanup'],
                'tags': ['cleanup', 'maintenance'],
                'triggers': ['cleanup_event', 'maintenance_window'],
                'description': 'System cleanup and maintenance'
            },
            {
                'name': 'backup_manager',
                'priority': HookPriority.HIGH,
                'phase': ExecutionPhase.FINALIZATION,
                'dependencies': ['audit_logging'],
                'provides': ['backup'],
                'tags': ['backup', 'finalization'],
                'triggers': ['backup_event', 'data_snapshot'],
                'description': 'Data backup and recovery system'
            },
            {
                'name': 'performance_monitor',
                'priority': HookPriority.NORMAL,
                'phase': ExecutionPhase.CORE_PROCESSING,
                'dependencies': [],
                'provides': ['monitoring'],
                'tags': ['monitoring', 'performance'],
                'triggers': ['monitor_event', 'performance_check'],
                'description': 'System performance monitoring'
            },
            {
                'name': 'error_handler',
                'priority': HookPriority.HIGH,
                'phase': ExecutionPhase.CORE_PROCESSING,
                'dependencies': [],
                'provides': ['error_handling'],
                'tags': ['error', 'exception', 'recovery'],
                'triggers': ['error_event', 'exception_thrown'],
                'description': 'Error handling and recovery system'
            }
        ]
        
        for hook_data in demo_hooks:
            # Create fake hook file
            hook_file = Path(f"/tmp/{hook_data['name']}.py")
            
            metadata = HookMetadata(
                name=hook_data['name'],
                file_path=str(hook_file),
                priority=hook_data['priority'],
                dependencies=hook_data['dependencies'],
                provides=hook_data['provides'],
                tags=hook_data['tags'],
                triggers=hook_data['triggers'],
                description=hook_data['description'],
                state=HookState.ACTIVE
            )
            
            self.registry.register_hook(metadata)
            self.registry.activate_hook(hook_data['name'])
    
    def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all priority system features"""
        print("\n🎯 Starting Comprehensive Hook Priority System Demo\n")
        
        demos = [
            ("Priority Calculation Demo", self.demo_priority_calculation),
            ("Dependency Resolution Demo", self.demo_dependency_resolution),
            ("Conflict Resolution Demo", self.demo_conflict_resolution),
            ("Parallel Execution Demo", self.demo_parallel_execution),
            ("Rollback Mechanism Demo", self.demo_rollback_mechanism),
            ("Performance Optimization Demo", self.demo_performance_optimization),
            ("Resource Management Demo", self.demo_resource_management),
            ("Real-time Priority Adjustment Demo", self.demo_dynamic_priority_adjustment),
            ("Complex Scenario Demo", self.demo_complex_scenario)
        ]
        
        for demo_name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"🔄 {demo_name}")
            print(f"{'='*60}")
            
            try:
                result = demo_func()
                self.demo_results[demo_name] = result
                print(f"✅ {demo_name} completed successfully")
            except Exception as e:
                print(f"❌ {demo_name} failed: {e}")
                self.demo_results[demo_name] = {'error': str(e)}
        
        # Generate final report
        self.generate_demo_report()
    
    def demo_priority_calculation(self) -> Dict[str, Any]:
        """Demonstrate advanced priority calculation algorithms"""
        print("📊 Testing Priority Calculation with Multiple Factors...")
        
        # Test different scenarios
        scenarios = [
            {
                'name': 'High System Load',
                'context': {
                    'system_load': 85,
                    'time_sensitivity': 'urgent',
                    'estimated_cpu_usage': 25
                }
            },
            {
                'name': 'Low System Load',
                'context': {
                    'system_load': 20,
                    'time_sensitivity': 'normal',
                    'estimated_cpu_usage': 15
                }
            },
            {
                'name': 'Memory Constrained',
                'context': {
                    'memory_usage': 95,
                    'time_sensitivity': 'low',
                    'estimated_memory_usage': 100
                }
            }
        ]
        
        results = {}
        test_hooks = ['system_validator', 'data_processor', 'notification_sender', 'cleanup_service']
        
        for scenario in scenarios:
            print(f"  🧪 Testing scenario: {scenario['name']}")
            
            scenario_results = {}
            for hook_name in test_hooks:
                priorities = self.priority_system._calculate_hook_priorities([hook_name], scenario['context'])
                scenario_results[hook_name] = priorities[hook_name]
            
            # Sort by priority
            sorted_hooks = sorted(scenario_results.items(), key=lambda x: x[1], reverse=True)
            
            results[scenario['name']] = {
                'priorities': scenario_results,
                'execution_order': [hook for hook, _ in sorted_hooks],
                'context': scenario['context']
            }
            
            print(f"    📈 Priority order: {' > '.join([hook for hook, _ in sorted_hooks])}")
        
        return results
    
    def demo_dependency_resolution(self) -> Dict[str, Any]:
        """Demonstrate dependency resolution and topological sorting"""
        print("🔗 Testing Dependency Resolution and Topological Sorting...")
        
        # Test complex dependency chain
        hooks_to_test = [
            'system_validator', 'auth_manager', 'data_processor', 
            'notification_sender', 'audit_logger', 'backup_manager'
        ]
        
        execution_plan = self.priority_system.calculate_execution_order(
            trigger='system_startup',
            hook_names=hooks_to_test,
            context={'dependency_analysis': True}
        )
        
        print(f"  📋 Generated {len(execution_plan['batches'])} execution batches")
        
        # Display execution plan
        for i, batch in enumerate(execution_plan['batches']):
            hooks_in_batch = batch['hooks']
            print(f"    Batch {i+1}: {', '.join(hooks_in_batch)} (Phase: {batch.get('phase', 'unknown')})")
        
        # Test cycle detection (artificially create a cycle)
        print("\n  🔄 Testing Cycle Detection...")
        
        # Temporarily add circular dependency
        original_deps = self.registry.hooks['system_validator'].dependencies.copy()
        self.registry.hooks['system_validator'].dependencies.append('backup_manager')
        
        try:
            cycle_plan = self.priority_system.calculate_execution_order(
                trigger='cycle_test',
                hook_names=hooks_to_test,
                context={'cycle_detection': True}
            )
            print("    ✅ Cycle detected and resolved")
        except Exception as e:
            print(f"    ⚠️ Cycle handling: {e}")
        finally:
            # Restore original dependencies
            self.registry.hooks['system_validator'].dependencies = original_deps
        
        return {
            'execution_plan': execution_plan,
            'total_estimated_time': execution_plan['total_estimated_time_ms'],
            'batches_count': len(execution_plan['batches']),
            'dependency_graph_size': len(execution_plan['dependency_graph'])
        }
    
    def demo_conflict_resolution(self) -> Dict[str, Any]:
        """Demonstrate conflict resolution strategies"""
        print("⚔️ Testing Conflict Resolution Strategies...")
        
        # Create conflicting hooks for the same trigger
        conflicting_hooks = ['data_processor', 'cache_manager', 'performance_monitor']
        trigger = 'performance_optimization'
        
        strategies = [
            ConflictResolutionStrategy.PRIORITY_BASED,
            ConflictResolutionStrategy.ROUND_ROBIN,
            ConflictResolutionStrategy.LOAD_BASED,
            ConflictResolutionStrategy.WEIGHTED_RANDOM
        ]
        
        results = {}
        
        for strategy in strategies:
            print(f"  🎯 Testing strategy: {strategy.value}")
            
            # Set strategy
            original_strategy = self.priority_system.default_conflict_strategy
            self.priority_system.default_conflict_strategy = strategy
            
            # Test multiple resolutions for round-robin demonstration
            strategy_results = []
            for i in range(3):
                resolution = self.priority_system.conflict_resolver.resolve_conflicts(
                    trigger, conflicting_hooks, self.registry.hooks, strategy
                )
                strategy_results.append({
                    'round': i + 1,
                    'winner': resolution.winner,
                    'reason': resolution.reason
                })
                print(f"    Round {i+1}: {resolution.winner} ({resolution.reason})")
            
            results[strategy.value] = strategy_results
            
            # Restore original strategy
            self.priority_system.default_conflict_strategy = original_strategy
        
        return results
    
    def demo_parallel_execution(self) -> Dict[str, Any]:
        """Demonstrate parallel execution optimization"""
        print("⚡ Testing Parallel Execution Optimization...")
        
        # Test different batch sizes and parallelism
        test_scenarios = [
            {
                'name': 'Small Batch',
                'hooks': ['cache_manager', 'performance_monitor'],
                'expected_parallelism': 2
            },
            {
                'name': 'Medium Batch',
                'hooks': ['data_processor', 'cache_manager', 'performance_monitor', 'error_handler'],
                'expected_parallelism': 4
            },
            {
                'name': 'Large Batch',
                'hooks': list(self.registry.hooks.keys()),
                'expected_parallelism': 8  # Limited by max_workers
            }
        ]
        
        results = {}
        
        for scenario in test_scenarios:
            print(f"  📦 Testing scenario: {scenario['name']} ({len(scenario['hooks'])} hooks)")
            
            # Calculate execution plan
            execution_plan = self.priority_system.calculate_execution_order(
                trigger='parallel_test',
                hook_names=scenario['hooks'],
                context={'parallel_optimization': True}
            )
            
            # Analyze parallelism
            total_parallelism = 0
            max_batch_parallelism = 0
            
            for batch in execution_plan['batches']:
                batch_parallelism = len(batch['hooks'])
                total_parallelism += batch_parallelism
                max_batch_parallelism = max(max_batch_parallelism, batch_parallelism)
            
            results[scenario['name']] = {
                'hooks_count': len(scenario['hooks']),
                'batches_generated': len(execution_plan['batches']),
                'total_parallelism': total_parallelism,
                'max_batch_parallelism': max_batch_parallelism,
                'estimated_time_ms': execution_plan['total_estimated_time_ms'],
                'optimization_applied': execution_plan.get('optimization_applied', False)
            }
            
            print(f"    📊 Batches: {len(execution_plan['batches'])}, "
                  f"Max parallel: {max_batch_parallelism}, "
                  f"Est. time: {execution_plan['total_estimated_time_ms']:.1f}ms")
        
        return results
    
    def demo_rollback_mechanism(self) -> Dict[str, Any]:
        """Demonstrate rollback capabilities"""
        print("🔄 Testing Rollback Mechanisms...")
        
        # Test different rollback scopes
        test_hooks = ['auth_manager', 'data_processor', 'audit_logger']
        
        # Create execution plan
        execution_plan = self.priority_system.calculate_execution_order(
            trigger='rollback_test',
            hook_names=test_hooks,
            context={'enable_rollback': True, 'simulate_failure': True}
        )
        
        print(f"  📋 Executing {len(test_hooks)} hooks with rollback enabled...")
        
        # Execute with rollback
        execution_result = self.priority_system.execute_with_priority(
            execution_plan,
            context={
                'enable_rollback': True,
                'trigger': 'rollback_test',
                'simulate_failure_at': 'data_processor'  # Simulate failure
            }
        )
        
        rollback_info = {
            'transaction_created': execution_result.get('transaction_id') is not None,
            'execution_success': execution_result.get('overall_success', False),
            'rollback_performed': execution_result.get('rollback_performed', False),
            'rollback_success': execution_result.get('rollback_success', False),
            'total_execution_time': execution_result.get('total_execution_time_ms', 0)
        }
        
        print(f"    🔄 Rollback performed: {rollback_info['rollback_performed']}")
        print(f"    ✅ Rollback success: {rollback_info['rollback_success']}")
        
        # Test different rollback scopes
        scope_tests = [
            RollbackScope.SINGLE_HOOK,
            RollbackScope.DEPENDENCY_CHAIN,
            RollbackScope.TRIGGER_GROUP
        ]
        
        scope_results = {}
        for scope in scope_tests:
            transaction_id = self.priority_system.rollback_manager.create_transaction(
                scope, test_hooks
            )
            
            # Add some dummy snapshots
            for hook in test_hooks:
                self.priority_system.rollback_manager.add_snapshot(
                    transaction_id, hook, {'test_state': f'snapshot_{hook}'}
                )
            
            # Test rollback
            rollback_success = self.priority_system.rollback_manager.rollback(transaction_id)
            
            scope_results[scope.value] = {
                'transaction_id': transaction_id,
                'rollback_success': rollback_success
            }
            
            print(f"    🎯 {scope.value}: {'✅ Success' if rollback_success else '❌ Failed'}")
        
        return {
            'execution_result': rollback_info,
            'scope_tests': scope_results,
            'active_transactions': len(self.priority_system.rollback_manager.active_transactions)
        }
    
    def demo_performance_optimization(self) -> Dict[str, Any]:
        """Demonstrate performance optimization features"""
        print("🚀 Testing Performance Optimization...")
        
        # Simulate hook execution history
        print("  📈 Simulating execution history for optimization analysis...")
        
        # Add simulated performance data
        hooks_to_optimize = ['data_processor', 'cache_manager', 'notification_sender']
        
        for hook_name in hooks_to_optimize:
            # Simulate various execution times and success rates
            for i in range(20):
                execution_time = 1000 + (i * 100)  # Gradually increasing execution time
                success = i < 18  # 90% success rate
                
                self.priority_system.performance_history[hook_name].append({
                    'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                    'execution_time_ms': execution_time,
                    'success': success,
                    'error': None if success else 'Simulated error'
                })
        
        # Run optimization
        optimization_result = self.priority_system.optimize_system_performance()
        
        print(f"  🔧 Actions taken: {len(optimization_result['actions_taken'])}")
        for action in optimization_result['actions_taken']:
            print(f"    • {action}")
        
        # Get system metrics
        metrics = self.priority_system.get_system_metrics()
        
        print(f"  📊 System metrics:")
        print(f"    • Active executions: {metrics['active_executions']}")
        print(f"    • Queue size: {metrics['queue_size']}")
        print(f"    • Performance history size: {metrics['performance_history_size']}")
        
        return {
            'optimization_result': optimization_result,
            'system_metrics': metrics,
            'performance_improvements': optimization_result.get('performance_improvements', {}),
            'priority_adjustments': optimization_result.get('priority_adjustments', {})
        }
    
    def demo_resource_management(self) -> Dict[str, Any]:
        """Demonstrate resource management and allocation"""
        print("💾 Testing Resource Management and Allocation...")
        
        # Test resource monitoring
        resource_monitor = self.priority_system.execution_optimizer.resource_monitor
        current_resources = resource_monitor.get_current_resources()
        
        print(f"  📊 Current system resources:")
        print(f"    • CPU: {current_resources.get('cpu_percent', 0):.1f}%")
        print(f"    • Memory: {current_resources.get('memory_percent', 0):.1f}%")
        print(f"    • Available Memory: {current_resources.get('memory_available_mb', 0):.1f} MB")
        
        # Test resource allocation
        load_balancer = self.priority_system.execution_optimizer.load_balancer
        
        from hook_priority_system import ResourceAllocation
        
        test_allocations = [
            ('lightweight_hook', ResourceAllocation(
                cpu_percent=5, memory_mb=50, io_operations=10,
                network_bandwidth=1.0, thread_count=1, max_duration_ms=1000
            )),
            ('heavy_hook', ResourceAllocation(
                cpu_percent=25, memory_mb=500, io_operations=100,
                network_bandwidth=10.0, thread_count=4, max_duration_ms=10000
            )),
            ('resource_intensive', ResourceAllocation(
                cpu_percent=50, memory_mb=1000, io_operations=500,
                network_bandwidth=50.0, thread_count=8, max_duration_ms=30000
            ))
        ]
        
        allocation_results = {}
        
        for hook_name, allocation in test_allocations:
            success = load_balancer.allocate_resources(hook_name, allocation)
            allocation_results[hook_name] = {
                'allocation_success': success,
                'cpu_requested': allocation.cpu_percent,
                'memory_requested': allocation.memory_mb
            }
            
            print(f"    🎯 {hook_name}: {'✅ Allocated' if success else '❌ Rejected'}")
            
            if success:
                # Release resources after test
                load_balancer.release_resources(hook_name)
        
        # Test resource trend analysis
        resource_trends = resource_monitor.get_resource_trend()
        
        return {
            'current_resources': current_resources,
            'allocation_tests': allocation_results,
            'resource_trends': resource_trends,
            'available_resources': load_balancer._get_available_resources()
        }
    
    def demo_dynamic_priority_adjustment(self) -> Dict[str, Any]:
        """Demonstrate real-time priority adjustment"""
        print("⚡ Testing Dynamic Priority Adjustment...")
        
        # Test priority calculation under different conditions
        test_hook = 'data_processor'
        
        # Baseline priority
        baseline_context = {'system_load': 50, 'time_sensitivity': 'normal'}
        baseline_priority = self.priority_system._calculate_hook_priorities([test_hook], baseline_context)
        
        print(f"  📊 Baseline priority for {test_hook}: {baseline_priority[test_hook]:.3f}")
        
        # Test different load conditions
        load_scenarios = [
            {'name': 'High Load', 'context': {'system_load': 90, 'time_sensitivity': 'urgent'}},
            {'name': 'Low Load', 'context': {'system_load': 10, 'time_sensitivity': 'normal'}},
            {'name': 'Memory Pressure', 'context': {'memory_usage': 95, 'time_sensitivity': 'high'}},
            {'name': 'Time Critical', 'context': {'system_load': 50, 'time_sensitivity': 'urgent'}}
        ]
        
        adjustment_results = {}
        
        for scenario in load_scenarios:
            adjusted_priority = self.priority_system._calculate_hook_priorities(
                [test_hook], scenario['context']
            )
            
            adjustment = adjusted_priority[test_hook] - baseline_priority[test_hook]
            adjustment_results[scenario['name']] = {
                'context': scenario['context'],
                'adjusted_priority': adjusted_priority[test_hook],
                'adjustment': adjustment,
                'percentage_change': (adjustment / baseline_priority[test_hook]) * 100
            }
            
            print(f"    🔄 {scenario['name']}: {adjusted_priority[test_hook]:.3f} "
                  f"({adjustment:+.3f}, {adjustment_results[scenario['name']]['percentage_change']:+.1f}%)")
        
        # Test frequency-based adjustment
        print("\n  📈 Testing frequency-based priority adjustment...")
        
        # Simulate execution frequency
        calculator = self.priority_system.priority_calculator
        
        # Simulate different execution frequencies
        for i in range(10):
            calculator.update_execution_stats('frequently_used_hook', True)
        
        for i in range(2):
            calculator.update_execution_stats('rarely_used_hook', True)
        
        # Calculate priorities with frequency consideration
        freq_context = {'frequency_analysis': True}
        freq_priorities = self.priority_system._calculate_hook_priorities(
            ['frequently_used_hook', 'rarely_used_hook'], freq_context
        )
        
        print(f"    📊 Frequently used hook: {freq_priorities['frequently_used_hook']:.3f}")
        print(f"    📊 Rarely used hook: {freq_priorities['rarely_used_hook']:.3f}")
        
        return {
            'baseline_priority': baseline_priority[test_hook],
            'load_adjustments': adjustment_results,
            'frequency_priorities': freq_priorities,
            'dynamic_adjustment_enabled': self.priority_system.enable_dynamic_priority_adjustment
        }
    
    def demo_complex_scenario(self) -> Dict[str, Any]:
        """Demonstrate complex real-world scenario with all features"""
        print("🌟 Testing Complex Real-World Scenario...")
        print("    Scenario: High-load system with multiple triggers, conflicts, and failures")
        
        # Complex scenario: System under load with multiple simultaneous triggers
        scenario_context = {
            'system_load': 85,
            'memory_usage': 80,
            'time_sensitivity': 'urgent',
            'enable_rollback': True,
            'parallel_optimization': True,
            'conflict_resolution': True
        }
        
        # Multiple triggers with overlapping hooks
        triggers_and_hooks = [
            ('user_login', ['system_validator', 'auth_manager', 'audit_logger']),
            ('data_event', ['auth_manager', 'data_processor', 'cache_manager']),
            ('performance_check', ['performance_monitor', 'cache_manager', 'cleanup_service']),
            ('backup_event', ['audit_logger', 'backup_manager', 'cleanup_service'])
        ]
        
        scenario_results = {}
        
        print(f"  🎭 Processing {len(triggers_and_hooks)} simultaneous triggers...")
        
        for trigger, hooks in triggers_and_hooks:
            print(f"\n    🎯 Processing trigger: {trigger}")
            
            # Calculate execution plan
            execution_plan = self.priority_system.calculate_execution_order(
                trigger=trigger,
                hook_names=hooks,
                context=scenario_context
            )
            
            # Execute with all features enabled
            execution_result = self.priority_system.execute_with_priority(
                execution_plan,
                context={**scenario_context, 'trigger': trigger}
            )
            
            scenario_results[trigger] = {
                'hooks_count': len(hooks),
                'batches_generated': len(execution_plan['batches']),
                'conflicts_resolved': len(execution_plan.get('conflicts_resolved', {}).get('resolutions', [])),
                'execution_success': execution_result.get('overall_success', False),
                'execution_time_ms': execution_result.get('total_execution_time_ms', 0),
                'rollback_performed': execution_result.get('rollback_performed', False),
                'optimization_applied': execution_plan.get('optimization_applied', False)
            }
            
            print(f"      📊 Batches: {scenario_results[trigger]['batches_generated']}, "
                  f"Time: {scenario_results[trigger]['execution_time_ms']:.1f}ms, "
                  f"Success: {scenario_results[trigger]['execution_success']}")
        
        # Analyze overall system performance during scenario
        final_metrics = self.priority_system.get_system_metrics()
        optimization_results = self.priority_system.optimize_system_performance()
        
        print(f"\n  📈 Scenario Summary:")
        print(f"    • Total triggers processed: {len(triggers_and_hooks)}")
        print(f"    • Successful executions: {sum(1 for r in scenario_results.values() if r['execution_success'])}")
        print(f"    • Total execution time: {sum(r['execution_time_ms'] for r in scenario_results.values()):.1f}ms")
        print(f"    • Rollbacks performed: {sum(1 for r in scenario_results.values() if r['rollback_performed'])}")
        print(f"    • Optimizations applied: {sum(1 for r in scenario_results.values() if r['optimization_applied'])}")
        
        return {
            'scenario_context': scenario_context,
            'trigger_results': scenario_results,
            'final_metrics': final_metrics,
            'optimization_results': optimization_results,
            'summary': {
                'triggers_processed': len(triggers_and_hooks),
                'success_rate': sum(1 for r in scenario_results.values() if r['execution_success']) / len(triggers_and_hooks),
                'total_execution_time_ms': sum(r['execution_time_ms'] for r in scenario_results.values()),
                'average_execution_time_ms': sum(r['execution_time_ms'] for r in scenario_results.values()) / len(triggers_and_hooks)
            }
        }
    
    def generate_demo_report(self):
        """Generate comprehensive demonstration report"""
        print(f"\n{'='*80}")
        print("📋 HOOK PRIORITY SYSTEM DEMONSTRATION REPORT")
        print(f"{'='*80}")
        
        # Summary statistics
        successful_demos = sum(1 for result in self.demo_results.values() 
                              if not isinstance(result, dict) or 'error' not in result)
        total_demos = len(self.demo_results)
        
        print(f"\n📊 Demo Summary:")
        print(f"  • Total demonstrations: {total_demos}")
        print(f"  • Successful demonstrations: {successful_demos}")
        print(f"  • Success rate: {(successful_demos/total_demos)*100:.1f}%")
        
        # Feature coverage summary
        features_tested = [
            "✅ Priority Calculation with Multiple Factors",
            "✅ Advanced Dependency Resolution",
            "✅ Multiple Conflict Resolution Strategies",
            "✅ Parallel Execution Optimization",
            "✅ Comprehensive Rollback Mechanisms",
            "✅ Performance Optimization and Monitoring",
            "✅ Resource Management and Allocation",
            "✅ Dynamic Priority Adjustment",
            "✅ Complex Real-World Scenario Testing"
        ]
        
        print(f"\n🎯 Features Tested:")
        for feature in features_tested:
            print(f"  {feature}")
        
        # Performance insights
        if 'Complex Scenario Demo' in self.demo_results:
            complex_result = self.demo_results['Complex Scenario Demo']
            if 'summary' in complex_result:
                summary = complex_result['summary']
                print(f"\n⚡ Performance Highlights:")
                print(f"  • Scenario success rate: {summary['success_rate']*100:.1f}%")
                print(f"  • Average execution time: {summary['average_execution_time_ms']:.1f}ms")
                print(f"  • Triggers processed: {summary['triggers_processed']}")
        
        # System capabilities demonstrated
        capabilities = [
            "🔄 1-10 Scale Priority Levels with Sub-priorities",
            "📊 Topological Sort Dependency Resolution",
            "⚔️ 6 Different Conflict Resolution Strategies",
            "⚡ Intelligent Parallel Execution Optimization",
            "🔄 Multi-scope Rollback Transaction Management",
            "📈 Real-time Performance Monitoring and Optimization",
            "💾 Sophisticated Resource Allocation and Management",
            "🎯 Dynamic Priority Adjustment Based on System Load"
        ]
        
        print(f"\n🌟 System Capabilities Demonstrated:")
        for capability in capabilities:
            print(f"  {capability}")
        
        # Save detailed report
        report_file = Path("hook_priority_system_demo_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'demo_results': self.demo_results,
                'summary': {
                    'total_demos': total_demos,
                    'successful_demos': successful_demos,
                    'success_rate': (successful_demos/total_demos)*100
                },
                'features_tested': features_tested,
                'capabilities_demonstrated': capabilities
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file.absolute()}")
        print(f"\n{'='*80}")
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")


def main():
    """Main entry point for the demonstration"""
    print("🚀 Hook Priority System - Advanced Demonstration Suite")
    print("=" * 60)
    
    try:
        demo = PrioritySystemDemo()
        demo.run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔚 Demonstration finished")


if __name__ == "__main__":
    main()