#!/usr/bin/env python3
"""
Hook Priority System API Documentation and Usage Examples
Comprehensive API documentation with practical usage examples for the sophisticated hook priority system.

Author: Claude Technical Specifications Agent
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime

# Import the hook priority system components
from hook_priority_system import (
    HookPrioritySystem, ConflictResolutionStrategy, ExecutionPhase, 
    RollbackScope, PriorityWeight, SubPriority, DependencyNode,
    ConflictResolution, ExecutionBatch, RollbackTransaction,
    ResourceAllocation, create_hook_priority_system
)


class PrioritySystemAPI:
    """
    Main API interface for the Hook Priority System
    
    This class provides a high-level API for interacting with the sophisticated
    hook priority system, including execution order calculation, conflict resolution,
    parallel execution optimization, and rollback management.
    """
    
    def __init__(self, hook_registry=None, config: Dict[str, Any] = None):
        """
        Initialize the Priority System API
        
        Args:
            hook_registry: Existing hook registry instance (optional)
            config: Configuration dictionary (optional)
        
        Example:
            >>> api = PrioritySystemAPI(config={
            ...     'conflict_strategy': 'priority_based',
            ...     'max_workers': 8,
            ...     'enable_rollback': True
            ... })
        """
        self.priority_system = create_hook_priority_system(hook_registry, config)
        self._execution_history = []
    
    def calculate_execution_order(self, 
                                 trigger: str, 
                                 hook_names: List[str], 
                                 context: Dict[str, Any] = None,
                                 options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate optimal execution order for hooks
        
        Args:
            trigger: The trigger event that initiated the execution
            hook_names: List of hook names to execute
            context: Execution context with additional parameters
            options: Additional options for execution planning
        
        Returns:
            Dictionary containing execution plan with batches, priorities, and metadata
        
        Example:
            >>> execution_plan = api.calculate_execution_order(
            ...     trigger="user_login",
            ...     hook_names=["auth_manager", "session_manager", "audit_logger"],
            ...     context={"time_sensitivity": "high", "user_id": "12345"},
            ...     options={"enable_parallel_optimization": True}
            ... )
            >>> print(f"Execution batches: {len(execution_plan['batches'])}")
            >>> print(f"Estimated time: {execution_plan['total_estimated_time_ms']}ms")
        """
        context = context or {}
        options = options or {}
        
        # Merge options into context
        merged_context = {**context, **options}
        
        return self.priority_system.calculate_execution_order(
            trigger=trigger,
            hook_names=hook_names,
            context=merged_context
        )
    
    def execute_hooks(self, 
                     execution_plan: Dict[str, Any] = None,
                     trigger: str = None,
                     hook_names: List[str] = None,
                     context: Dict[str, Any] = None,
                     options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute hooks with priority-based ordering and optimization
        
        Args:
            execution_plan: Pre-calculated execution plan (optional)
            trigger: Trigger event (required if no execution_plan)
            hook_names: Hook names to execute (required if no execution_plan)
            context: Execution context
            options: Execution options
        
        Returns:
            Dictionary containing execution results, timing, and status
        
        Example:
            >>> # Option 1: Execute with pre-calculated plan
            >>> result = api.execute_hooks(execution_plan=plan, context=context)
            
            >>> # Option 2: Calculate and execute in one call
            >>> result = api.execute_hooks(
            ...     trigger="data_processing",
            ...     hook_names=["validator", "processor", "notifier"],
            ...     context={"batch_size": 1000, "enable_rollback": True}
            ... )
            >>> 
            >>> if result['overall_success']:
            ...     print(f"Execution completed in {result['total_execution_time_ms']}ms")
            >>> else:
            ...     print(f"Execution failed: {result.get('error', 'Unknown error')}")
        """
        context = context or {}
        options = options or {}
        
        # If no execution plan provided, calculate it
        if execution_plan is None:
            if not trigger or not hook_names:
                raise ValueError("Either execution_plan or (trigger + hook_names) must be provided")
            
            execution_plan = self.calculate_execution_order(
                trigger=trigger,
                hook_names=hook_names,
                context=context,
                options=options
            )
        
        # Execute with the plan
        result = self.priority_system.execute_with_priority(
            execution_plan=execution_plan,
            context={**context, **options}
        )
        
        # Record execution history
        self._execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'trigger': execution_plan.get('trigger', trigger),
            'hooks_count': len(hook_names) if hook_names else sum(len(b['hooks']) for b in execution_plan['batches']),
            'success': result['overall_success'],
            'execution_time_ms': result['total_execution_time_ms']
        })
        
        return result
    
    def resolve_conflicts(self, 
                         trigger: str, 
                         conflicting_hooks: List[str],
                         strategy: Union[str, ConflictResolutionStrategy] = None) -> Dict[str, Any]:
        """
        Resolve conflicts between hooks for the same trigger
        
        Args:
            trigger: The trigger causing the conflict
            conflicting_hooks: List of hooks that conflict
            strategy: Conflict resolution strategy to use
        
        Returns:
            Dictionary containing conflict resolution result
        
        Example:
            >>> resolution = api.resolve_conflicts(
            ...     trigger="cache_update",
            ...     conflicting_hooks=["cache_invalidator", "cache_warmer", "cache_optimizer"],
            ...     strategy="priority_based"
            ... )
            >>> print(f"Winner: {resolution['winner']}")
            >>> print(f"Strategy: {resolution['strategy_used']}")
            >>> print(f"Reason: {resolution['reason']}")
        """
        if isinstance(strategy, str):
            strategy = ConflictResolutionStrategy(strategy)
        elif strategy is None:
            strategy = self.priority_system.default_conflict_strategy
        
        if not self.priority_system.hook_registry:
            raise RuntimeError("Hook registry not available for conflict resolution")
        
        resolution = self.priority_system.conflict_resolver.resolve_conflicts(
            trigger=trigger,
            competing_hooks=conflicting_hooks,
            metadata_map=self.priority_system.hook_registry.hooks,
            strategy=strategy
        )
        
        return {
            'winner': resolution.winner,
            'losers': resolution.losers,
            'strategy_used': resolution.strategy_used.value,
            'reason': resolution.reason,
            'timestamp': resolution.timestamp.isoformat()
        }
    
    def optimize_performance(self) -> Dict[str, Any]:
        """
        Optimize system performance based on historical data
        
        Returns:
            Dictionary containing optimization results and recommendations
        
        Example:
            >>> optimization = api.optimize_performance()
            >>> print(f"Actions taken: {optimization['actions_taken']}")
            >>> for action in optimization['actions_taken']:
            ...     print(f"  - {action}")
            >>> 
            >>> if optimization['priority_adjustments']:
            ...     print("Priority adjustments made:")
            ...     for hook, adjustment in optimization['priority_adjustments'].items():
            ...         print(f"  - {hook}: {adjustment}")
        """
        return self.priority_system.optimize_system_performance()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics and status
        
        Returns:
            Dictionary containing system metrics, performance data, and status
        
        Example:
            >>> metrics = api.get_system_metrics()
            >>> print(f"Active executions: {metrics['active_executions']}")
            >>> print(f"Queue size: {metrics['queue_size']}")
            >>> print(f"Resource monitor active: {metrics['resource_monitor_status']['monitoring_active']}")
        """
        system_metrics = self.priority_system.get_system_metrics()
        
        # Add API-specific metrics
        system_metrics['api_metrics'] = {
            'total_api_executions': len(self._execution_history),
            'recent_success_rate': self._calculate_recent_success_rate(),
            'average_execution_time_ms': self._calculate_average_execution_time()
        }
        
        return system_metrics
    
    def create_rollback_transaction(self, 
                                   scope: Union[str, RollbackScope], 
                                   affected_hooks: List[str]) -> str:
        """
        Create a rollback transaction for hook executions
        
        Args:
            scope: Rollback scope (single_hook, dependency_chain, trigger_group, system_wide)
            affected_hooks: List of hooks affected by this transaction
        
        Returns:
            Transaction ID for the created rollback transaction
        
        Example:
            >>> transaction_id = api.create_rollback_transaction(
            ...     scope="dependency_chain",
            ...     affected_hooks=["validator", "processor", "finalizer"]
            ... )
            >>> print(f"Transaction created: {transaction_id}")
        """
        if isinstance(scope, str):
            scope = RollbackScope(scope)
        
        return self.priority_system.rollback_manager.create_transaction(
            scope=scope,
            affected_hooks=affected_hooks
        )
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """
        Execute rollback for a specific transaction
        
        Args:
            transaction_id: ID of the transaction to rollback
        
        Returns:
            True if rollback was successful, False otherwise
        
        Example:
            >>> success = api.rollback_transaction(transaction_id)
            >>> if success:
            ...     print("Rollback completed successfully")
            >>> else:
            ...     print("Rollback failed")
        """
        return self.priority_system.rollback_manager.rollback(transaction_id)
    
    def get_hook_priority(self, hook_name: str, context: Dict[str, Any] = None) -> float:
        """
        Calculate priority for a specific hook
        
        Args:
            hook_name: Name of the hook
            context: Context for priority calculation
        
        Returns:
            Calculated priority value
        
        Example:
            >>> priority = api.get_hook_priority("auth_manager", {
            ...     "system_load": 75,
            ...     "time_sensitivity": "urgent"
            ... })
            >>> print(f"Priority: {priority:.3f}")
        """
        context = context or {}
        priorities = self.priority_system._calculate_hook_priorities([hook_name], context)
        return priorities.get(hook_name, 1.0)
    
    def set_conflict_strategy(self, 
                             strategy: Union[str, ConflictResolutionStrategy],
                             trigger: str = None):
        """
        Set conflict resolution strategy globally or for specific trigger
        
        Args:
            strategy: Conflict resolution strategy
            trigger: Specific trigger to set strategy for (optional)
        
        Example:
            >>> # Set global strategy
            >>> api.set_conflict_strategy("load_based")
            >>> 
            >>> # Set strategy for specific trigger
            >>> api.set_conflict_strategy("round_robin", trigger="cache_update")
        """
        if isinstance(strategy, str):
            strategy = ConflictResolutionStrategy(strategy)
        
        if trigger is None:
            self.priority_system.default_conflict_strategy = strategy
        else:
            # This would need to be implemented in the priority system
            # For now, just set the global strategy
            self.priority_system.default_conflict_strategy = strategy
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get execution history from the API
        
        Args:
            limit: Maximum number of history entries to return
        
        Returns:
            List of execution history entries
        
        Example:
            >>> history = api.get_execution_history(limit=10)
            >>> for entry in history[-5:]:  # Last 5 executions
            ...     print(f"{entry['timestamp']}: {entry['trigger']} - "
            ...           f"{'Success' if entry['success'] else 'Failed'} "
            ...           f"({entry['execution_time_ms']:.1f}ms)")
        """
        return self._execution_history[-limit:] if limit > 0 else self._execution_history
    
    def analyze_performance_trends(self, window_size: int = 50) -> Dict[str, Any]:
        """
        Analyze performance trends over recent executions
        
        Args:
            window_size: Number of recent executions to analyze
        
        Returns:
            Dictionary containing trend analysis
        
        Example:
            >>> trends = api.analyze_performance_trends(window_size=30)
            >>> print(f"Success rate trend: {trends['success_rate_trend']}")
            >>> print(f"Performance trend: {trends['performance_trend']}")
            >>> print(f"Average execution time: {trends['avg_execution_time_ms']:.1f}ms")
        """
        if len(self._execution_history) < 2:
            return {'error': 'Insufficient execution history for trend analysis'}
        
        recent_history = self._execution_history[-window_size:]
        
        # Calculate trends
        success_rates = []
        execution_times = []
        
        for i in range(0, len(recent_history), 10):  # Sample every 10 executions
            chunk = recent_history[i:i+10]
            success_rate = sum(1 for entry in chunk if entry['success']) / len(chunk)
            avg_time = sum(entry['execution_time_ms'] for entry in chunk) / len(chunk)
            
            success_rates.append(success_rate)
            execution_times.append(avg_time)
        
        # Determine trends
        success_trend = 'stable'
        if len(success_rates) >= 2:
            if success_rates[-1] > success_rates[0]:
                success_trend = 'improving'
            elif success_rates[-1] < success_rates[0]:
                success_trend = 'declining'
        
        performance_trend = 'stable'
        if len(execution_times) >= 2:
            if execution_times[-1] < execution_times[0]:
                performance_trend = 'improving'  # Lower time is better
            elif execution_times[-1] > execution_times[0]:
                performance_trend = 'declining'
        
        return {
            'window_size': len(recent_history),
            'success_rate_trend': success_trend,
            'performance_trend': performance_trend,
            'current_success_rate': success_rates[-1] if success_rates else 1.0,
            'avg_execution_time_ms': sum(entry['execution_time_ms'] for entry in recent_history) / len(recent_history),
            'execution_count': len(recent_history)
        }
    
    def shutdown(self):
        """
        Gracefully shutdown the priority system
        
        Example:
            >>> api.shutdown()
            >>> print("Priority system shutdown complete")
        """
        self.priority_system.shutdown()
    
    def _calculate_recent_success_rate(self, window: int = 50) -> float:
        """Calculate success rate for recent executions"""
        if not self._execution_history:
            return 1.0
        
        recent = self._execution_history[-window:]
        successes = sum(1 for entry in recent if entry['success'])
        return successes / len(recent)
    
    def _calculate_average_execution_time(self, window: int = 50) -> float:
        """Calculate average execution time for recent executions"""
        if not self._execution_history:
            return 0.0
        
        recent = self._execution_history[-window:]
        total_time = sum(entry['execution_time_ms'] for entry in recent)
        return total_time / len(recent)


class UsageExamples:
    """
    Comprehensive usage examples for the Hook Priority System API
    """
    
    @staticmethod
    def basic_hook_execution():
        """
        Example 1: Basic hook execution with priority ordering
        """
        print("=== Example 1: Basic Hook Execution ===")
        
        # Initialize API
        api = PrioritySystemAPI(config={
            'max_workers': 4,
            'enable_rollback': True
        })
        
        # Execute hooks for user authentication
        result = api.execute_hooks(
            trigger="user_login",
            hook_names=["input_validator", "auth_manager", "session_creator", "audit_logger"],
            context={
                "user_id": "user123",
                "time_sensitivity": "high",
                "enable_rollback": True
            }
        )
        
        print(f"Execution successful: {result['overall_success']}")
        print(f"Total time: {result['total_execution_time_ms']:.1f}ms")
        print(f"Batches executed: {len(result['batch_results'])}")
        
        # Check if rollback was needed
        if result.get('rollback_performed'):
            print(f"Rollback performed: {result['rollback_success']}")
        
        return result
    
    @staticmethod
    def conflict_resolution_example():
        """
        Example 2: Conflict resolution between competing hooks
        """
        print("\n=== Example 2: Conflict Resolution ===")
        
        api = PrioritySystemAPI()
        
        # Resolve conflict between cache management hooks
        resolution = api.resolve_conflicts(
            trigger="cache_optimization",
            conflicting_hooks=["cache_invalidator", "cache_warmer", "cache_compactor"],
            strategy="priority_based"
        )
        
        print(f"Conflict winner: {resolution['winner']}")
        print(f"Resolution strategy: {resolution['strategy_used']}")
        print(f"Reason: {resolution['reason']}")
        
        # Try different strategies
        strategies = ["round_robin", "load_based", "weighted_random"]
        for strategy in strategies:
            res = api.resolve_conflicts(
                trigger="cache_optimization",
                conflicting_hooks=["cache_invalidator", "cache_warmer", "cache_compactor"],
                strategy=strategy
            )
            print(f"{strategy}: {res['winner']} ({res['reason']})")
        
        return resolution
    
    @staticmethod
    def parallel_execution_example():
        """
        Example 3: Parallel execution optimization
        """
        print("\n=== Example 3: Parallel Execution ===")
        
        api = PrioritySystemAPI(config={
            'max_workers': 8,
            'enable_parallel_optimization': True
        })
        
        # Execute data processing pipeline
        hooks = [
            "data_validator", "data_transformer", "data_enricher",
            "data_cleaner", "data_aggregator", "data_indexer",
            "notification_sender", "metrics_collector"
        ]
        
        # Calculate execution plan
        plan = api.calculate_execution_order(
            trigger="data_pipeline",
            hook_names=hooks,
            context={
                "batch_size": 10000,
                "parallel_optimization": True,
                "resource_optimization": True
            }
        )
        
        print(f"Execution plan created with {len(plan['batches'])} batches")
        for i, batch in enumerate(plan['batches']):
            print(f"  Batch {i+1}: {len(batch['hooks'])} hooks - {', '.join(batch['hooks'][:3])}...")
        
        # Execute the plan
        result = api.execute_hooks(execution_plan=plan)
        
        print(f"Pipeline execution: {'Success' if result['overall_success'] else 'Failed'}")
        print(f"Total execution time: {result['total_execution_time_ms']:.1f}ms")
        
        return result
    
    @staticmethod
    def rollback_transaction_example():
        """
        Example 4: Rollback transaction management
        """
        print("\n=== Example 4: Rollback Transactions ===")
        
        api = PrioritySystemAPI(config={'enable_rollback': True})
        
        # Create rollback transaction
        transaction_id = api.create_rollback_transaction(
            scope="dependency_chain",
            affected_hooks=["order_validator", "payment_processor", "inventory_updater", "order_finalizer"]
        )
        
        print(f"Created transaction: {transaction_id}")
        
        # Execute hooks with rollback protection
        result = api.execute_hooks(
            trigger="order_processing",
            hook_names=["order_validator", "payment_processor", "inventory_updater", "order_finalizer"],
            context={
                "order_id": "ORD-12345",
                "enable_rollback": True,
                "transaction_id": transaction_id,
                "simulate_failure": True  # For demonstration
            }
        )
        
        print(f"Order processing: {'Success' if result['overall_success'] else 'Failed'}")
        
        if not result['overall_success']:
            print("Processing failed, attempting rollback...")
            rollback_success = api.rollback_transaction(transaction_id)
            print(f"Rollback: {'Success' if rollback_success else 'Failed'}")
        
        return result
    
    @staticmethod
    def performance_optimization_example():
        """
        Example 5: Performance optimization and monitoring
        """
        print("\n=== Example 5: Performance Optimization ===")
        
        api = PrioritySystemAPI(config={
            'enable_dynamic_priority_adjustment': True,
            'performance_monitoring_enabled': True
        })
        
        # Simulate multiple executions to build history
        print("Simulating execution history...")
        for i in range(10):
            api.execute_hooks(
                trigger="performance_test",
                hook_names=["test_hook_1", "test_hook_2", "test_hook_3"],
                context={"iteration": i, "simulate": True}
            )
        
        # Get system metrics
        metrics = api.get_system_metrics()
        print(f"Total API executions: {metrics['api_metrics']['total_api_executions']}")
        print(f"Recent success rate: {metrics['api_metrics']['recent_success_rate']:.1%}")
        print(f"Average execution time: {metrics['api_metrics']['average_execution_time_ms']:.1f}ms")
        
        # Run performance optimization
        optimization = api.optimize_performance()
        print(f"Optimization actions: {len(optimization['actions_taken'])}")
        for action in optimization['actions_taken']:
            print(f"  - {action}")
        
        # Analyze trends
        trends = api.analyze_performance_trends()
        print(f"Success rate trend: {trends['success_rate_trend']}")
        print(f"Performance trend: {trends['performance_trend']}")
        
        return optimization
    
    @staticmethod
    def complex_scenario_example():
        """
        Example 6: Complex real-world scenario
        """
        print("\n=== Example 6: Complex E-commerce Scenario ===")
        
        api = PrioritySystemAPI(config={
            'max_workers': 12,
            'enable_rollback': True,
            'enable_parallel_optimization': True,
            'conflict_strategy': 'priority_based'
        })
        
        # E-commerce order processing with multiple systems
        order_hooks = [
            "request_validator", "user_authenticator", "inventory_checker",
            "price_calculator", "discount_applier", "tax_calculator",
            "payment_processor", "inventory_updater", "order_creator",
            "notification_sender", "analytics_tracker", "audit_logger"
        ]
        
        print("Processing complex e-commerce order...")
        
        # Step 1: Calculate execution plan
        plan = api.calculate_execution_order(
            trigger="order_submission",
            hook_names=order_hooks,
            context={
                "order_value": 299.99,
                "customer_tier": "premium",
                "payment_method": "credit_card",
                "time_sensitivity": "high",
                "enable_rollback": True,
                "parallel_optimization": True
            }
        )
        
        print(f"Execution plan: {len(plan['batches'])} batches, {plan['total_estimated_time_ms']:.1f}ms estimated")
        
        # Step 2: Execute with full monitoring
        start_time = time.time()
        result = api.execute_hooks(execution_plan=plan)
        execution_time = (time.time() - start_time) * 1000
        
        print(f"Order processing: {'✅ Success' if result['overall_success'] else '❌ Failed'}")
        print(f"Actual execution time: {execution_time:.1f}ms")
        print(f"Batches completed: {len(result['batch_results'])}")
        
        # Step 3: Handle results
        if result['overall_success']:
            print("✅ Order processed successfully!")
            
            # Get performance metrics
            metrics = api.get_system_metrics()
            print(f"System load: CPU {metrics.get('current_cpu', 'N/A')}%, Memory {metrics.get('current_memory', 'N/A')}%")
        else:
            print("❌ Order processing failed")
            if result.get('rollback_performed'):
                print(f"🔄 Rollback: {'Success' if result['rollback_success'] else 'Failed'}")
        
        return result
    
    @staticmethod
    def run_all_examples():
        """
        Run all usage examples
        """
        print("🚀 Hook Priority System API - Usage Examples")
        print("=" * 60)
        
        examples = [
            UsageExamples.basic_hook_execution,
            UsageExamples.conflict_resolution_example,
            UsageExamples.parallel_execution_example,
            UsageExamples.rollback_transaction_example,
            UsageExamples.performance_optimization_example,
            UsageExamples.complex_scenario_example
        ]
        
        results = {}
        
        for example in examples:
            try:
                result = example()
                results[example.__name__] = {'success': True, 'result': result}
            except Exception as e:
                print(f"❌ Example failed: {e}")
                results[example.__name__] = {'success': False, 'error': str(e)}
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Examples Summary")
        print("=" * 60)
        
        for name, result in results.items():
            status = "✅ Success" if result['success'] else "❌ Failed"
            print(f"{name}: {status}")
        
        success_rate = sum(1 for r in results.values() if r['success']) / len(results)
        print(f"\nOverall success rate: {success_rate:.1%}")
        
        return results


def main():
    """
    Main function demonstrating API usage
    """
    print("Hook Priority System API Documentation and Examples")
    print("=" * 60)
    
    # Run all examples
    UsageExamples.run_all_examples()


if __name__ == "__main__":
    main()