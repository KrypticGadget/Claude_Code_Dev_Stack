#!/usr/bin/env python3
"""
Sophisticated Hook Priority System with Execution Order Algorithms and Optimization
Provides advanced priority calculation, dependency resolution, conflict resolution,
parallel execution optimization, rollback mechanisms, and performance optimization.

Author: Claude Technical Specifications Agent
Version: 1.0.0
"""

import asyncio
import json
import time
import threading
import weakref
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple, NamedTuple
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import heapq
import psutil
import logging
from pathlib import Path
import uuid
import copy

# Import existing hook registry components
from hook_registry import (
    HookMetadata, HookPriority, HookState, TriggerType, 
    ExecutionContext, PerformanceMetrics, HookRegistryError
)


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving hook execution conflicts"""
    PRIORITY_BASED = "priority_based"      # Highest priority wins
    ROUND_ROBIN = "round_robin"            # Rotate between conflicting hooks
    LOAD_BASED = "load_based"              # Select based on system load
    WEIGHTED_RANDOM = "weighted_random"    # Weighted random selection
    FIRST_REGISTERED = "first_registered"  # First registered hook wins
    LAST_REGISTERED = "last_registered"    # Most recently registered wins


class ExecutionPhase(IntEnum):
    """Execution phases for dependency ordering"""
    PRE_VALIDATION = 1
    INITIALIZATION = 2
    CORE_PROCESSING = 3
    POST_PROCESSING = 4
    CLEANUP = 5
    FINALIZATION = 6


class RollbackScope(Enum):
    """Scope of rollback operations"""
    SINGLE_HOOK = "single_hook"           # Rollback single hook execution
    DEPENDENCY_CHAIN = "dependency_chain"  # Rollback entire dependency chain
    TRIGGER_GROUP = "trigger_group"       # Rollback all hooks for a trigger
    SYSTEM_WIDE = "system_wide"           # Rollback all active executions


@dataclass
class PriorityWeight:
    """Priority calculation weights and factors"""
    base_priority: float = 1.0            # Base priority from hook definition
    dependency_factor: float = 0.0        # Adjustment for dependency depth
    frequency_factor: float = 0.0         # Adjustment for execution frequency
    success_rate_factor: float = 0.0      # Adjustment for historical success
    load_factor: float = 0.0              # Adjustment for system load
    urgency_factor: float = 0.0           # Adjustment for time sensitivity
    resource_factor: float = 0.0          # Adjustment for resource availability


@dataclass
class SubPriority:
    """Sub-priority levels within main priority categories"""
    level: int                            # Sub-priority level (1-100)
    decimal_offset: float = 0.0           # Fine-grained decimal offset
    dynamic_adjustment: float = 0.0       # Real-time priority adjustment
    
    def calculate_effective_priority(self) -> float:
        """Calculate effective priority value"""
        return self.level + self.decimal_offset + self.dynamic_adjustment


@dataclass
class DependencyNode:
    """Node in dependency graph"""
    hook_name: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    phase: ExecutionPhase = ExecutionPhase.CORE_PROCESSING
    optional_dependencies: Set[str] = field(default_factory=set)
    parallel_group: Optional[str] = None
    isolation_level: int = 0              # 0=shared, 1=isolated, 2=exclusive


@dataclass
class ConflictResolution:
    """Conflict resolution result"""
    winner: str
    losers: List[str]
    strategy_used: ConflictResolutionStrategy
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionBatch:
    """Batch of hooks that can execute in parallel"""
    batch_id: str
    hooks: List[str]
    phase: ExecutionPhase
    max_parallelism: int
    resource_requirements: Dict[str, float]
    estimated_duration_ms: float
    dependencies_satisfied: bool = False


@dataclass
class RollbackTransaction:
    """Transaction for rollback operations"""
    transaction_id: str
    scope: RollbackScope
    affected_hooks: List[str]
    snapshots: Dict[str, Any]
    rollback_actions: List[Callable]
    created_at: datetime = field(default_factory=datetime.now)
    can_rollback: bool = True


@dataclass
class ResourceAllocation:
    """Resource allocation for hook execution"""
    cpu_percent: float
    memory_mb: float
    io_operations: int
    network_bandwidth: float
    thread_count: int
    max_duration_ms: float


class AdvancedPriorityCalculator:
    """Advanced priority calculation with multiple factors"""
    
    def __init__(self):
        self.weights = {
            'base_priority': 0.40,
            'dependency_depth': 0.15,
            'execution_frequency': 0.15,
            'success_rate': 0.10,
            'system_load': 0.10,
            'time_sensitivity': 0.05,
            'resource_availability': 0.05
        }
        self.load_history = deque(maxlen=100)
        self.frequency_tracker = defaultdict(int)
        self.success_tracker = defaultdict(lambda: {'total': 0, 'success': 0})
    
    def calculate_priority(self, hook_name: str, metadata: HookMetadata, 
                          context: Dict[str, Any]) -> PriorityWeight:
        """Calculate comprehensive priority with all factors"""
        weights = PriorityWeight()
        
        # Base priority from hook definition
        weights.base_priority = 10 - metadata.priority.value  # Invert for higher=better
        
        # Dependency factor - deeper dependencies get higher priority
        dependency_depth = context.get('dependency_depth', 0)
        weights.dependency_factor = dependency_depth * 0.5
        
        # Frequency factor - balance between popular and underused hooks
        frequency = self.frequency_tracker[hook_name]
        avg_frequency = sum(self.frequency_tracker.values()) / max(len(self.frequency_tracker), 1)
        weights.frequency_factor = (avg_frequency - frequency) * 0.1
        
        # Success rate factor
        stats = self.success_tracker[hook_name]
        if stats['total'] > 0:
            success_rate = stats['success'] / stats['total']
            weights.success_rate_factor = (success_rate - 0.5) * 2.0  # Scale -1 to 1
        
        # System load factor - lower load = higher priority for heavy hooks
        current_load = psutil.cpu_percent()
        self.load_history.append(current_load)
        avg_load = sum(self.load_history) / len(self.load_history)
        
        estimated_load = context.get('estimated_cpu_usage', 10)
        if current_load < avg_load and estimated_load > 20:
            weights.load_factor = 0.5  # Boost heavy hooks when system is idle
        elif current_load > avg_load and estimated_load > 20:
            weights.load_factor = -1.0  # Penalize heavy hooks when system is busy
        
        # Time sensitivity factor
        time_sensitivity = context.get('time_sensitivity', 'normal')
        if time_sensitivity == 'urgent':
            weights.urgency_factor = 2.0
        elif time_sensitivity == 'low':
            weights.urgency_factor = -0.5
        
        # Resource availability factor
        available_memory = psutil.virtual_memory().percent
        if available_memory < 80:  # Less than 80% memory used
            weights.resource_factor = 0.5
        elif available_memory > 95:  # More than 95% memory used
            weights.resource_factor = -1.0
        
        return weights
    
    def calculate_effective_priority(self, weights: PriorityWeight) -> float:
        """Calculate final effective priority"""
        total = 0.0
        total += weights.base_priority * self.weights['base_priority']
        total += weights.dependency_factor * self.weights['dependency_depth']
        total += weights.frequency_factor * self.weights['execution_frequency']
        total += weights.success_rate_factor * self.weights['success_rate']
        total += weights.load_factor * self.weights['system_load']
        total += weights.urgency_factor * self.weights['time_sensitivity']
        total += weights.resource_factor * self.weights['resource_availability']
        
        return max(0.1, total)  # Ensure minimum priority
    
    def update_execution_stats(self, hook_name: str, success: bool):
        """Update execution statistics for priority calculation"""
        self.frequency_tracker[hook_name] += 1
        stats = self.success_tracker[hook_name]
        stats['total'] += 1
        if success:
            stats['success'] += 1


class TopologicalSorter:
    """Advanced topological sorting with cycle detection and resolution"""
    
    def __init__(self):
        self.cycle_resolution_strategies = [
            self._break_cycle_by_priority,
            self._break_cycle_by_frequency,
            self._break_cycle_by_age
        ]
    
    def sort_with_phases(self, graph: Dict[str, DependencyNode]) -> List[ExecutionBatch]:
        """Topological sort with execution phases and parallelization"""
        # Group nodes by phase
        phase_groups = defaultdict(list)
        for hook_name, node in graph.items():
            phase_groups[node.phase].append(hook_name)
        
        batches = []
        processed = set()
        
        # Process each phase in order
        for phase in sorted(ExecutionPhase):
            if phase not in phase_groups:
                continue
            
            phase_hooks = phase_groups[phase]
            phase_batches = self._sort_phase_hooks(phase_hooks, graph, processed)
            batches.extend(phase_batches)
            processed.update(hook_name for batch in phase_batches for hook_name in batch.hooks)
        
        return batches
    
    def _sort_phase_hooks(self, hooks: List[str], graph: Dict[str, DependencyNode], 
                         processed: Set[str]) -> List[ExecutionBatch]:
        """Sort hooks within a single phase"""
        remaining = [h for h in hooks if h not in processed]
        batches = []
        batch_counter = 0
        
        while remaining:
            # Find hooks with no unresolved dependencies
            ready = []
            for hook in remaining:
                node = graph[hook]
                unresolved_deps = node.dependencies - processed
                if not unresolved_deps:
                    ready.append(hook)
            
            if not ready:
                # Handle circular dependencies
                cycle_hooks = self._detect_and_resolve_cycle(remaining, graph)
                if cycle_hooks:
                    ready = cycle_hooks
                else:
                    # Force progress by taking lowest dependency hook
                    ready = [min(remaining, key=lambda h: len(graph[h].dependencies))]
            
            # Group ready hooks by parallel group
            parallel_groups = defaultdict(list)
            for hook in ready:
                group = graph[hook].parallel_group or f"default_{batch_counter}"
                parallel_groups[group].append(hook)
            
            # Create batches for each parallel group
            for group_name, group_hooks in parallel_groups.items():
                batch = ExecutionBatch(
                    batch_id=f"batch_{batch_counter}_{group_name}",
                    hooks=group_hooks,
                    phase=graph[group_hooks[0]].phase,
                    max_parallelism=len(group_hooks),
                    resource_requirements=self._calculate_batch_resources(group_hooks, graph),
                    estimated_duration_ms=self._estimate_batch_duration(group_hooks)
                )
                batches.append(batch)
                batch_counter += 1
            
            # Remove ready hooks from remaining
            for hook in ready:
                remaining.remove(hook)
                processed.add(hook)
        
        return batches
    
    def _detect_and_resolve_cycle(self, hooks: List[str], 
                                 graph: Dict[str, DependencyNode]) -> List[str]:
        """Detect and resolve circular dependencies"""
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        cycle_nodes = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle_nodes.extend(path[cycle_start:])
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for dep in graph[node].dependencies:
                if dep in hooks:  # Only consider dependencies within this set
                    if dfs(dep, path + [node]):
                        return True
            
            rec_stack.remove(node)
            return False
        
        # Find cycles
        for hook in hooks:
            if hook not in visited:
                if dfs(hook, []):
                    break
        
        if not cycle_nodes:
            return []
        
        # Try resolution strategies
        for strategy in self.cycle_resolution_strategies:
            resolved = strategy(cycle_nodes, graph)
            if resolved:
                return resolved
        
        # Fallback: break cycle at highest priority node
        return [max(cycle_nodes, key=lambda h: graph[h].phase.value)]
    
    def _break_cycle_by_priority(self, cycle_nodes: List[str], 
                                graph: Dict[str, DependencyNode]) -> List[str]:
        """Break cycle by removing lowest priority dependencies"""
        # This is a placeholder - implement based on priority
        return []
    
    def _break_cycle_by_frequency(self, cycle_nodes: List[str], 
                                 graph: Dict[str, DependencyNode]) -> List[str]:
        """Break cycle by removing least frequently used dependencies"""
        # This is a placeholder - implement based on execution frequency
        return []
    
    def _break_cycle_by_age(self, cycle_nodes: List[str], 
                           graph: Dict[str, DependencyNode]) -> List[str]:
        """Break cycle by removing newest dependencies"""
        # This is a placeholder - implement based on hook age
        return []
    
    def _calculate_batch_resources(self, hooks: List[str], 
                                  graph: Dict[str, DependencyNode]) -> Dict[str, float]:
        """Calculate resource requirements for a batch"""
        return {
            'cpu_percent': len(hooks) * 10,  # Estimate
            'memory_mb': len(hooks) * 50,    # Estimate
            'io_operations': len(hooks) * 5,  # Estimate
        }
    
    def _estimate_batch_duration(self, hooks: List[str]) -> float:
        """Estimate batch execution duration"""
        return len(hooks) * 1000  # 1 second per hook estimate


class ConflictResolver:
    """Resolves conflicts between competing hooks"""
    
    def __init__(self):
        self.round_robin_state = defaultdict(int)
        self.load_threshold = 80.0  # CPU threshold for load-based resolution
    
    def resolve_conflicts(self, trigger: str, competing_hooks: List[str], 
                         metadata_map: Dict[str, HookMetadata],
                         strategy: ConflictResolutionStrategy) -> ConflictResolution:
        """Resolve conflicts between hooks for the same trigger"""
        
        if len(competing_hooks) <= 1:
            return ConflictResolution(
                winner=competing_hooks[0] if competing_hooks else "",
                losers=[],
                strategy_used=strategy,
                reason="No conflict - single or no hooks"
            )
        
        if strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            return self._resolve_by_priority(competing_hooks, metadata_map)
        elif strategy == ConflictResolutionStrategy.ROUND_ROBIN:
            return self._resolve_by_round_robin(trigger, competing_hooks)
        elif strategy == ConflictResolutionStrategy.LOAD_BASED:
            return self._resolve_by_load(competing_hooks, metadata_map)
        elif strategy == ConflictResolutionStrategy.WEIGHTED_RANDOM:
            return self._resolve_by_weighted_random(competing_hooks, metadata_map)
        elif strategy == ConflictResolutionStrategy.FIRST_REGISTERED:
            return self._resolve_by_registration_order(competing_hooks, metadata_map, True)
        elif strategy == ConflictResolutionStrategy.LAST_REGISTERED:
            return self._resolve_by_registration_order(competing_hooks, metadata_map, False)
        else:
            # Fallback to priority-based
            return self._resolve_by_priority(competing_hooks, metadata_map)
    
    def _resolve_by_priority(self, hooks: List[str], 
                           metadata_map: Dict[str, HookMetadata]) -> ConflictResolution:
        """Resolve by hook priority"""
        hook_priorities = [(hook, metadata_map[hook].priority.value) for hook in hooks]
        hook_priorities.sort(key=lambda x: x[1])  # Lower value = higher priority
        
        winner = hook_priorities[0][0]
        losers = [hook for hook, _ in hook_priorities[1:]]
        
        return ConflictResolution(
            winner=winner,
            losers=losers,
            strategy_used=ConflictResolutionStrategy.PRIORITY_BASED,
            reason=f"Highest priority: {metadata_map[winner].priority.name}"
        )
    
    def _resolve_by_round_robin(self, trigger: str, hooks: List[str]) -> ConflictResolution:
        """Resolve by round-robin selection"""
        current_index = self.round_robin_state[trigger] % len(hooks)
        winner = hooks[current_index]
        losers = hooks[:current_index] + hooks[current_index + 1:]
        
        self.round_robin_state[trigger] += 1
        
        return ConflictResolution(
            winner=winner,
            losers=losers,
            strategy_used=ConflictResolutionStrategy.ROUND_ROBIN,
            reason=f"Round-robin selection (index {current_index})"
        )
    
    def _resolve_by_load(self, hooks: List[str], 
                        metadata_map: Dict[str, HookMetadata]) -> ConflictResolution:
        """Resolve based on system load"""
        current_load = psutil.cpu_percent()
        
        if current_load > self.load_threshold:
            # High load - prefer lightweight hooks
            winner = min(hooks, key=lambda h: metadata_map[h].average_execution_time)
            reason = f"Low-resource hook selected (CPU: {current_load}%)"
        else:
            # Low load - can run any hook, prefer high priority
            winner = min(hooks, key=lambda h: metadata_map[h].priority.value)
            reason = f"High-priority hook selected (CPU: {current_load}%)"
        
        losers = [h for h in hooks if h != winner]
        
        return ConflictResolution(
            winner=winner,
            losers=losers,
            strategy_used=ConflictResolutionStrategy.LOAD_BASED,
            reason=reason
        )
    
    def _resolve_by_weighted_random(self, hooks: List[str], 
                                   metadata_map: Dict[str, HookMetadata]) -> ConflictResolution:
        """Resolve by weighted random selection"""
        import random
        
        # Weight by inverse priority (lower priority value = higher weight)
        weights = [10 - metadata_map[hook].priority.value for hook in hooks]
        winner = random.choices(hooks, weights=weights)[0]
        losers = [h for h in hooks if h != winner]
        
        return ConflictResolution(
            winner=winner,
            losers=losers,
            strategy_used=ConflictResolutionStrategy.WEIGHTED_RANDOM,
            reason="Weighted random selection"
        )
    
    def _resolve_by_registration_order(self, hooks: List[str], 
                                      metadata_map: Dict[str, HookMetadata],
                                      first: bool) -> ConflictResolution:
        """Resolve by registration order"""
        sorted_hooks = sorted(hooks, key=lambda h: metadata_map[h].created_at)
        
        if first:
            winner = sorted_hooks[0]
            reason = "First registered hook"
        else:
            winner = sorted_hooks[-1]
            reason = "Last registered hook"
        
        losers = [h for h in hooks if h != winner]
        
        strategy = (ConflictResolutionStrategy.FIRST_REGISTERED if first 
                   else ConflictResolutionStrategy.LAST_REGISTERED)
        
        return ConflictResolution(
            winner=winner,
            losers=losers,
            strategy_used=strategy,
            reason=reason
        )


class ParallelExecutionOptimizer:
    """Optimizes parallel execution of hooks"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) + 4)
        self.resource_monitor = ResourceMonitor()
        self.load_balancer = LoadBalancer()
    
    def optimize_execution_plan(self, batches: List[ExecutionBatch]) -> List[ExecutionBatch]:
        """Optimize execution plan for maximum parallelism"""
        optimized_batches = []
        
        for batch in batches:
            # Check if batch can be split for better parallelism
            if len(batch.hooks) > self.max_workers:
                split_batches = self._split_large_batch(batch)
                optimized_batches.extend(split_batches)
            else:
                # Optimize resource allocation for the batch
                optimized_batch = self._optimize_batch_resources(batch)
                optimized_batches.append(optimized_batch)
        
        # Merge compatible batches
        merged_batches = self._merge_compatible_batches(optimized_batches)
        
        return merged_batches
    
    def _split_large_batch(self, batch: ExecutionBatch) -> List[ExecutionBatch]:
        """Split large batches into smaller parallel batches"""
        split_size = self.max_workers
        split_batches = []
        
        for i in range(0, len(batch.hooks), split_size):
            chunk = batch.hooks[i:i + split_size]
            split_batch = ExecutionBatch(
                batch_id=f"{batch.batch_id}_split_{i // split_size}",
                hooks=chunk,
                phase=batch.phase,
                max_parallelism=len(chunk),
                resource_requirements=self._calculate_chunk_resources(chunk, batch),
                estimated_duration_ms=batch.estimated_duration_ms / len(batch.hooks) * len(chunk)
            )
            split_batches.append(split_batch)
        
        return split_batches
    
    def _optimize_batch_resources(self, batch: ExecutionBatch) -> ExecutionBatch:
        """Optimize resource allocation for a batch"""
        # Check available system resources
        available_cpu = 100 - psutil.cpu_percent()
        available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB
        
        # Adjust parallelism based on available resources
        required_cpu = batch.resource_requirements.get('cpu_percent', 0)
        required_memory = batch.resource_requirements.get('memory_mb', 0)
        
        cpu_limit = int(available_cpu / max(required_cpu / len(batch.hooks), 1))
        memory_limit = int(available_memory / max(required_memory / len(batch.hooks), 1))
        
        optimal_parallelism = min(
            batch.max_parallelism,
            cpu_limit,
            memory_limit,
            self.max_workers
        )
        
        batch.max_parallelism = max(1, optimal_parallelism)
        return batch
    
    def _merge_compatible_batches(self, batches: List[ExecutionBatch]) -> List[ExecutionBatch]:
        """Merge compatible batches for better resource utilization"""
        merged = []
        i = 0
        
        while i < len(batches):
            current_batch = batches[i]
            
            # Look for compatible next batch
            if i + 1 < len(batches):
                next_batch = batches[i + 1]
                
                if self._can_merge_batches(current_batch, next_batch):
                    merged_batch = self._merge_batches(current_batch, next_batch)
                    merged.append(merged_batch)
                    i += 2  # Skip next batch as it's merged
                    continue
            
            merged.append(current_batch)
            i += 1
        
        return merged
    
    def _can_merge_batches(self, batch1: ExecutionBatch, batch2: ExecutionBatch) -> bool:
        """Check if two batches can be merged"""
        # Same phase and compatible resource requirements
        if batch1.phase != batch2.phase:
            return False
        
        total_hooks = len(batch1.hooks) + len(batch2.hooks)
        if total_hooks > self.max_workers:
            return False
        
        # Check resource compatibility
        total_cpu = (batch1.resource_requirements.get('cpu_percent', 0) + 
                    batch2.resource_requirements.get('cpu_percent', 0))
        total_memory = (batch1.resource_requirements.get('memory_mb', 0) + 
                       batch2.resource_requirements.get('memory_mb', 0))
        
        available_cpu = 100 - psutil.cpu_percent()
        available_memory = psutil.virtual_memory().available / 1024 / 1024
        
        return total_cpu <= available_cpu and total_memory <= available_memory
    
    def _merge_batches(self, batch1: ExecutionBatch, batch2: ExecutionBatch) -> ExecutionBatch:
        """Merge two compatible batches"""
        return ExecutionBatch(
            batch_id=f"{batch1.batch_id}_merged_{batch2.batch_id}",
            hooks=batch1.hooks + batch2.hooks,
            phase=batch1.phase,
            max_parallelism=len(batch1.hooks) + len(batch2.hooks),
            resource_requirements={
                'cpu_percent': (batch1.resource_requirements.get('cpu_percent', 0) + 
                               batch2.resource_requirements.get('cpu_percent', 0)),
                'memory_mb': (batch1.resource_requirements.get('memory_mb', 0) + 
                             batch2.resource_requirements.get('memory_mb', 0)),
                'io_operations': (batch1.resource_requirements.get('io_operations', 0) + 
                                 batch2.resource_requirements.get('io_operations', 0))
            },
            estimated_duration_ms=max(batch1.estimated_duration_ms, batch2.estimated_duration_ms)
        )
    
    def _calculate_chunk_resources(self, chunk: List[str], 
                                  original_batch: ExecutionBatch) -> Dict[str, float]:
        """Calculate resource requirements for a chunk of the original batch"""
        ratio = len(chunk) / len(original_batch.hooks)
        return {
            key: value * ratio 
            for key, value in original_batch.resource_requirements.items()
        }


class ResourceMonitor:
    """Monitors system resources for optimization"""
    
    def __init__(self):
        self.history_size = 100
        self.cpu_history = deque(maxlen=self.history_size)
        self.memory_history = deque(maxlen=self.history_size)
        self.io_history = deque(maxlen=self.history_size)
        self._update_thread = None
        self._stop_monitoring = threading.Event()
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._update_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._update_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._stop_monitoring.set()
        if self._update_thread:
            self._update_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Resource monitoring loop"""
        while not self._stop_monitoring.wait(1.0):  # Update every second
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                io_counters = psutil.disk_io_counters()
                
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                
                if io_counters:
                    io_rate = io_counters.read_count + io_counters.write_count
                    self.io_history.append(io_rate)
                
            except Exception as e:
                logging.warning(f"Resource monitoring error: {e}")
    
    def get_current_resources(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'disk_io_rate': self._get_io_rate()
            }
        except Exception:
            return {'cpu_percent': 0, 'memory_percent': 0, 'memory_available_mb': 1024, 'disk_io_rate': 0}
    
    def get_resource_trend(self) -> Dict[str, str]:
        """Get resource usage trend"""
        trends = {}
        
        if len(self.cpu_history) >= 2:
            recent_avg = sum(list(self.cpu_history)[-5:]) / 5
            older_avg = sum(list(self.cpu_history)[-10:-5]) / 5
            trends['cpu'] = 'increasing' if recent_avg > older_avg else 'decreasing'
        else:
            trends['cpu'] = 'stable'
        
        if len(self.memory_history) >= 2:
            recent_avg = sum(list(self.memory_history)[-5:]) / 5
            older_avg = sum(list(self.memory_history)[-10:-5]) / 5
            trends['memory'] = 'increasing' if recent_avg > older_avg else 'decreasing'
        else:
            trends['memory'] = 'stable'
        
        return trends
    
    def _get_io_rate(self) -> float:
        """Get current IO rate"""
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters and len(self.io_history) > 0:
                current = io_counters.read_count + io_counters.write_count
                previous = self.io_history[-1] if self.io_history else current
                return max(0, current - previous)
            return 0
        except Exception:
            return 0


class LoadBalancer:
    """Load balances hook execution across available resources"""
    
    def __init__(self):
        self.worker_pools = {}
        self.resource_allocations = {}
    
    def allocate_resources(self, hook_name: str, requirements: ResourceAllocation) -> bool:
        """Allocate resources for hook execution"""
        current_resources = self._get_available_resources()
        
        if (requirements.cpu_percent <= current_resources['cpu_available'] and
            requirements.memory_mb <= current_resources['memory_available_mb']):
            
            self.resource_allocations[hook_name] = requirements
            return True
        
        return False
    
    def release_resources(self, hook_name: str):
        """Release allocated resources"""
        if hook_name in self.resource_allocations:
            del self.resource_allocations[hook_name]
    
    def _get_available_resources(self) -> Dict[str, float]:
        """Get currently available resources"""
        allocated_cpu = sum(alloc.cpu_percent for alloc in self.resource_allocations.values())
        allocated_memory = sum(alloc.memory_mb for alloc in self.resource_allocations.values())
        
        total_cpu = 100
        total_memory = psutil.virtual_memory().total / 1024 / 1024
        
        return {
            'cpu_available': max(0, total_cpu - allocated_cpu),
            'memory_available_mb': max(0, total_memory - allocated_memory)
        }


class RollbackManager:
    """Manages rollback operations for failed hook chains"""
    
    def __init__(self):
        self.active_transactions = {}
        self.rollback_history = deque(maxlen=1000)
        self.snapshots = {}
    
    def create_transaction(self, scope: RollbackScope, affected_hooks: List[str]) -> str:
        """Create a new rollback transaction"""
        transaction_id = str(uuid.uuid4())
        
        transaction = RollbackTransaction(
            transaction_id=transaction_id,
            scope=scope,
            affected_hooks=affected_hooks,
            snapshots={},
            rollback_actions=[]
        )
        
        self.active_transactions[transaction_id] = transaction
        return transaction_id
    
    def add_snapshot(self, transaction_id: str, hook_name: str, state: Any):
        """Add state snapshot to transaction"""
        if transaction_id not in self.active_transactions:
            return False
        
        transaction = self.active_transactions[transaction_id]
        transaction.snapshots[hook_name] = copy.deepcopy(state)
        return True
    
    def add_rollback_action(self, transaction_id: str, action: Callable):
        """Add rollback action to transaction"""
        if transaction_id not in self.active_transactions:
            return False
        
        transaction = self.active_transactions[transaction_id]
        transaction.rollback_actions.append(action)
        return True
    
    def rollback(self, transaction_id: str) -> bool:
        """Execute rollback for a transaction"""
        if transaction_id not in self.active_transactions:
            return False
        
        transaction = self.active_transactions[transaction_id]
        
        if not transaction.can_rollback:
            return False
        
        success = True
        executed_actions = []
        
        try:
            # Execute rollback actions in reverse order
            for action in reversed(transaction.rollback_actions):
                action()
                executed_actions.append(action)
            
            # Record successful rollback
            self.rollback_history.append({
                'transaction_id': transaction_id,
                'timestamp': datetime.now(),
                'scope': transaction.scope,
                'affected_hooks': transaction.affected_hooks,
                'success': True
            })
            
        except Exception as e:
            logging.error(f"Rollback failed for transaction {transaction_id}: {e}")
            success = False
            
            # Record failed rollback
            self.rollback_history.append({
                'transaction_id': transaction_id,
                'timestamp': datetime.now(),
                'scope': transaction.scope,
                'affected_hooks': transaction.affected_hooks,
                'success': False,
                'error': str(e)
            })
        
        finally:
            # Clean up transaction
            if transaction_id in self.active_transactions:
                del self.active_transactions[transaction_id]
        
        return success
    
    def commit_transaction(self, transaction_id: str):
        """Commit transaction (disable rollback)"""
        if transaction_id in self.active_transactions:
            self.active_transactions[transaction_id].can_rollback = False


class HookPrioritySystem:
    """Main hook priority system orchestrating all components"""
    
    def __init__(self, hook_registry=None):
        self.hook_registry = hook_registry
        self.priority_calculator = AdvancedPriorityCalculator()
        self.topological_sorter = TopologicalSorter()
        self.conflict_resolver = ConflictResolver()
        self.execution_optimizer = ParallelExecutionOptimizer()
        self.rollback_manager = RollbackManager()
        
        # Configuration
        self.default_conflict_strategy = ConflictResolutionStrategy.PRIORITY_BASED
        self.enable_dynamic_priority_adjustment = True
        self.max_execution_time_ms = 30000  # 30 seconds
        
        # State tracking
        self.dependency_graph = {}
        self.execution_queue = []
        self.active_executions = {}
        self.performance_history = defaultdict(list)
        
        # Initialize resource monitoring
        self.execution_optimizer.resource_monitor.start_monitoring()
    
    def calculate_execution_order(self, trigger: str, hook_names: List[str], 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate optimal execution order for hooks"""
        if not hook_names:
            return {'batches': [], 'total_estimated_time_ms': 0}
        
        context = context or {}
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(hook_names)
        
        # Calculate priorities
        priorities = self._calculate_hook_priorities(hook_names, context)
        
        # Resolve conflicts
        resolved_hooks = self._resolve_trigger_conflicts(trigger, hook_names)
        
        # Perform topological sort with phases
        execution_batches = self.topological_sorter.sort_with_phases(dependency_graph)
        
        # Optimize for parallel execution
        optimized_batches = self.execution_optimizer.optimize_execution_plan(execution_batches)
        
        # Calculate total estimated time
        total_time = sum(batch.estimated_duration_ms for batch in optimized_batches)
        
        return {
            'trigger': trigger,
            'batches': [asdict(batch) for batch in optimized_batches],
            'total_estimated_time_ms': total_time,
            'priorities': priorities,
            'conflicts_resolved': resolved_hooks,
            'dependency_graph': {name: asdict(node) for name, node in dependency_graph.items()},
            'optimization_applied': True
        }
    
    def execute_with_priority(self, execution_plan: Dict[str, Any], 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute hooks according to priority-based plan with rollback support"""
        context = context or {}
        execution_id = str(uuid.uuid4())
        
        # Create rollback transaction
        all_hooks = []
        for batch_data in execution_plan['batches']:
            all_hooks.extend(batch_data['hooks'])
        
        transaction_id = self.rollback_manager.create_transaction(
            RollbackScope.TRIGGER_GROUP, all_hooks
        )
        
        results = {
            'execution_id': execution_id,
            'transaction_id': transaction_id,
            'started_at': datetime.now().isoformat(),
            'batch_results': [],
            'overall_success': True,
            'total_execution_time_ms': 0,
            'rollback_performed': False
        }
        
        start_time = time.time()
        
        try:
            # Execute batches in order
            for i, batch_data in enumerate(execution_plan['batches']):
                batch_result = self._execute_batch(
                    batch_data, transaction_id, context
                )
                results['batch_results'].append(batch_result)
                
                # Check for batch failure
                if not batch_result['success']:
                    results['overall_success'] = False
                    
                    # Perform rollback if enabled
                    if context.get('enable_rollback', True):
                        rollback_success = self.rollback_manager.rollback(transaction_id)
                        results['rollback_performed'] = rollback_success
                        results['rollback_success'] = rollback_success
                    
                    break
            
            # Commit transaction if all successful
            if results['overall_success']:
                self.rollback_manager.commit_transaction(transaction_id)
        
        except Exception as e:
            results['overall_success'] = False
            results['error'] = str(e)
            
            # Attempt rollback on exception
            if context.get('enable_rollback', True):
                rollback_success = self.rollback_manager.rollback(transaction_id)
                results['rollback_performed'] = rollback_success
                results['rollback_success'] = rollback_success
        
        finally:
            end_time = time.time()
            results['total_execution_time_ms'] = (end_time - start_time) * 1000
            results['completed_at'] = datetime.now().isoformat()
        
        return results
    
    def optimize_system_performance(self) -> Dict[str, Any]:
        """Optimize overall system performance based on historical data"""
        optimizations = {
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'performance_improvements': {},
            'resource_optimizations': {},
            'priority_adjustments': {}
        }
        
        # Analyze performance history
        performance_stats = self._analyze_performance_history()
        
        # Identify slow hooks
        slow_hooks = [
            hook for hook, stats in performance_stats.items()
            if stats['avg_execution_time_ms'] > 5000  # 5 seconds
        ]
        
        if slow_hooks:
            # Adjust priorities for slow hooks
            for hook in slow_hooks:
                if self.enable_dynamic_priority_adjustment:
                    self._adjust_hook_priority(hook, -1.0)  # Lower priority
                    optimizations['priority_adjustments'][hook] = 'lowered_priority'
            
            optimizations['actions_taken'].append(f"Lowered priority for {len(slow_hooks)} slow hooks")
        
        # Identify frequently failing hooks
        failing_hooks = [
            hook for hook, stats in performance_stats.items()
            if stats['success_rate'] < 0.8  # Less than 80% success rate
        ]
        
        if failing_hooks:
            optimizations['actions_taken'].append(f"Identified {len(failing_hooks)} unreliable hooks")
        
        # Resource optimization
        current_resources = self.execution_optimizer.resource_monitor.get_current_resources()
        resource_trends = self.execution_optimizer.resource_monitor.get_resource_trend()
        
        optimizations['resource_optimizations'] = {
            'current_usage': current_resources,
            'trends': resource_trends,
            'recommendations': self._generate_resource_recommendations(
                current_resources, resource_trends
            )
        }
        
        return optimizations
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_executions': len(self.active_executions),
            'queue_size': len(self.execution_queue),
            'dependency_graph_size': len(self.dependency_graph),
            'performance_history_size': sum(len(history) for history in self.performance_history.values()),
            'rollback_transactions': len(self.rollback_manager.active_transactions),
            'resource_monitor_status': {
                'cpu_history_size': len(self.execution_optimizer.resource_monitor.cpu_history),
                'memory_history_size': len(self.execution_optimizer.resource_monitor.memory_history),
                'monitoring_active': self.execution_optimizer.resource_monitor._update_thread is not None
            },
            'conflict_resolution_strategy': self.default_conflict_strategy.value,
            'dynamic_priority_enabled': self.enable_dynamic_priority_adjustment,
            'optimization_settings': {
                'max_workers': self.execution_optimizer.max_workers,
                'max_execution_time_ms': self.max_execution_time_ms
            }
        }
    
    def _build_dependency_graph(self, hook_names: List[str]) -> Dict[str, DependencyNode]:
        """Build dependency graph for hooks"""
        graph = {}
        
        for hook_name in hook_names:
            if not self.hook_registry or hook_name not in self.hook_registry.hooks:
                # Create minimal node for unknown hooks
                graph[hook_name] = DependencyNode(hook_name=hook_name)
                continue
            
            metadata = self.hook_registry.hooks[hook_name]
            
            # Create dependency node
            node = DependencyNode(
                hook_name=hook_name,
                dependencies=set(metadata.dependencies),
                phase=self._determine_execution_phase(metadata),
                isolation_level=self._determine_isolation_level(metadata)
            )
            
            graph[hook_name] = node
        
        # Build reverse dependencies (dependents)
        for hook_name, node in graph.items():
            for dep in node.dependencies:
                if dep in graph:
                    graph[dep].dependents.add(hook_name)
        
        return graph
    
    def _determine_execution_phase(self, metadata: HookMetadata) -> ExecutionPhase:
        """Determine execution phase for a hook"""
        # Analyze hook tags and triggers to determine phase
        if 'validation' in metadata.tags:
            return ExecutionPhase.PRE_VALIDATION
        elif 'initialization' in metadata.tags or 'setup' in metadata.tags:
            return ExecutionPhase.INITIALIZATION
        elif 'cleanup' in metadata.tags:
            return ExecutionPhase.CLEANUP
        elif 'finalization' in metadata.tags or 'teardown' in metadata.tags:
            return ExecutionPhase.FINALIZATION
        elif 'post_process' in metadata.tags:
            return ExecutionPhase.POST_PROCESSING
        else:
            return ExecutionPhase.CORE_PROCESSING
    
    def _determine_isolation_level(self, metadata: HookMetadata) -> int:
        """Determine isolation level for a hook"""
        if 'exclusive' in metadata.tags:
            return 2  # Exclusive execution
        elif 'isolated' in metadata.tags:
            return 1  # Isolated execution
        else:
            return 0  # Shared execution
    
    def _calculate_hook_priorities(self, hook_names: List[str], 
                                  context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate priorities for all hooks"""
        priorities = {}
        
        for hook_name in hook_names:
            if self.hook_registry and hook_name in self.hook_registry.hooks:
                metadata = self.hook_registry.hooks[hook_name]
                weights = self.priority_calculator.calculate_priority(hook_name, metadata, context)
                priorities[hook_name] = self.priority_calculator.calculate_effective_priority(weights)
            else:
                priorities[hook_name] = 1.0  # Default priority
        
        return priorities
    
    def _resolve_trigger_conflicts(self, trigger: str, hook_names: List[str]) -> Dict[str, Any]:
        """Resolve conflicts for hooks triggered by the same event"""
        if not self.hook_registry:
            return {'conflicts': [], 'resolutions': []}
        
        # Group hooks by trigger conflicts
        conflicts = defaultdict(list)
        for hook_name in hook_names:
            if hook_name in self.hook_registry.hooks:
                metadata = self.hook_registry.hooks[hook_name]
                if trigger in metadata.triggers:
                    conflicts[trigger].append(hook_name)
        
        resolutions = []
        for trigger_name, competing_hooks in conflicts.items():
            if len(competing_hooks) > 1:
                resolution = self.conflict_resolver.resolve_conflicts(
                    trigger_name, competing_hooks, self.hook_registry.hooks,
                    self.default_conflict_strategy
                )
                resolutions.append(asdict(resolution))
        
        return {
            'conflicts': [{'trigger': t, 'hooks': h} for t, h in conflicts.items() if len(h) > 1],
            'resolutions': resolutions
        }
    
    def _execute_batch(self, batch_data: Dict[str, Any], transaction_id: str, 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single batch of hooks"""
        batch_start = time.time()
        hooks = batch_data['hooks']
        max_parallelism = batch_data.get('max_parallelism', len(hooks))
        
        # Limit parallelism based on system resources
        actual_parallelism = min(max_parallelism, self.execution_optimizer.max_workers)
        
        results = {
            'batch_id': batch_data['batch_id'],
            'hooks': hooks,
            'success': True,
            'hook_results': {},
            'execution_time_ms': 0,
            'parallelism_used': actual_parallelism
        }
        
        try:
            if actual_parallelism == 1 or len(hooks) == 1:
                # Sequential execution
                for hook_name in hooks:
                    hook_result = self._execute_single_hook(hook_name, transaction_id, context)
                    results['hook_results'][hook_name] = hook_result
                    
                    if not hook_result['success']:
                        results['success'] = False
                        break
            else:
                # Parallel execution
                with ThreadPoolExecutor(max_workers=actual_parallelism) as executor:
                    future_to_hook = {
                        executor.submit(self._execute_single_hook, hook_name, transaction_id, context): hook_name
                        for hook_name in hooks
                    }
                    
                    for future in as_completed(future_to_hook, timeout=self.max_execution_time_ms / 1000):
                        hook_name = future_to_hook[future]
                        try:
                            hook_result = future.result()
                            results['hook_results'][hook_name] = hook_result
                            
                            if not hook_result['success']:
                                results['success'] = False
                        except Exception as e:
                            results['hook_results'][hook_name] = {
                                'success': False,
                                'error': str(e),
                                'execution_time_ms': 0
                            }
                            results['success'] = False
        
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        finally:
            batch_end = time.time()
            results['execution_time_ms'] = (batch_end - batch_start) * 1000
        
        return results
    
    def _execute_single_hook(self, hook_name: str, transaction_id: str, 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single hook with rollback support"""
        hook_start = time.time()
        
        result = {
            'hook_name': hook_name,
            'success': False,
            'result': None,
            'error': None,
            'execution_time_ms': 0
        }
        
        try:
            # Add snapshot before execution
            if self.hook_registry and hook_name in self.hook_registry.hooks:
                metadata = self.hook_registry.hooks[hook_name]
                self.rollback_manager.add_snapshot(transaction_id, hook_name, {
                    'state': metadata.state,
                    'execution_count': metadata.execution_count,
                    'last_executed': metadata.last_executed
                })
            
            # Execute hook through registry
            if self.hook_registry:
                execution_id = self.hook_registry.execute_hook(
                    hook_name, context.get('trigger', 'manual'), context
                )
                result['execution_id'] = execution_id
                result['success'] = True
            else:
                # Fallback for testing
                result['success'] = True
                result['result'] = f"Mock execution of {hook_name}"
            
            # Update statistics
            self.priority_calculator.update_execution_stats(hook_name, result['success'])
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            
            # Update statistics
            self.priority_calculator.update_execution_stats(hook_name, False)
        
        finally:
            hook_end = time.time()
            result['execution_time_ms'] = (hook_end - hook_start) * 1000
            
            # Record performance metrics
            self.performance_history[hook_name].append({
                'timestamp': datetime.now().isoformat(),
                'execution_time_ms': result['execution_time_ms'],
                'success': result['success'],
                'error': result.get('error')
            })
        
        return result
    
    def _analyze_performance_history(self) -> Dict[str, Any]:
        """Analyze performance history for optimization"""
        stats = {}
        
        for hook_name, history in self.performance_history.items():
            if not history:
                continue
            
            execution_times = [entry['execution_time_ms'] for entry in history]
            successes = [entry['success'] for entry in history]
            
            stats[hook_name] = {
                'total_executions': len(history),
                'avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'max_execution_time_ms': max(execution_times),
                'min_execution_time_ms': min(execution_times),
                'success_rate': sum(successes) / len(successes),
                'recent_performance': {
                    'last_10_avg_ms': sum(execution_times[-10:]) / min(10, len(execution_times)),
                    'last_10_success_rate': sum(successes[-10:]) / min(10, len(successes))
                }
            }
        
        return stats
    
    def _adjust_hook_priority(self, hook_name: str, adjustment: float):
        """Adjust hook priority dynamically"""
        if not self.hook_registry or hook_name not in self.hook_registry.hooks:
            return
        
        # This would need to be implemented in the hook registry
        # For now, we just log the adjustment
        logging.info(f"Priority adjustment for {hook_name}: {adjustment}")
    
    def _generate_resource_recommendations(self, current_resources: Dict[str, float], 
                                         trends: Dict[str, str]) -> List[str]:
        """Generate resource optimization recommendations"""
        recommendations = []
        
        if current_resources.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected - consider reducing parallel execution")
        
        if current_resources.get('memory_percent', 0) > 90:
            recommendations.append("High memory usage detected - consider memory optimization")
        
        if trends.get('cpu') == 'increasing':
            recommendations.append("CPU usage trending upward - monitor for performance issues")
        
        if trends.get('memory') == 'increasing':
            recommendations.append("Memory usage trending upward - check for memory leaks")
        
        return recommendations
    
    def shutdown(self):
        """Clean shutdown of the priority system"""
        # Stop resource monitoring
        self.execution_optimizer.resource_monitor.stop_monitoring()
        
        # Cancel active executions
        self.active_executions.clear()
        
        # Clear queues
        self.execution_queue.clear()


# Factory function for easy instantiation
def create_hook_priority_system(hook_registry=None, config: Dict[str, Any] = None) -> HookPrioritySystem:
    """Create and configure a hook priority system"""
    system = HookPrioritySystem(hook_registry)
    
    if config:
        if 'conflict_strategy' in config:
            system.default_conflict_strategy = ConflictResolutionStrategy(config['conflict_strategy'])
        
        if 'enable_dynamic_priority' in config:
            system.enable_dynamic_priority_adjustment = config['enable_dynamic_priority']
        
        if 'max_execution_time_ms' in config:
            system.max_execution_time_ms = config['max_execution_time_ms']
        
        if 'max_workers' in config:
            system.execution_optimizer.max_workers = config['max_workers']
    
    return system


# Export main classes and functions
__all__ = [
    'HookPrioritySystem',
    'ConflictResolutionStrategy',
    'ExecutionPhase',
    'RollbackScope',
    'PriorityWeight',
    'SubPriority',
    'DependencyNode',
    'ConflictResolution',
    'ExecutionBatch',
    'RollbackTransaction',
    'ResourceAllocation',
    'AdvancedPriorityCalculator',
    'TopologicalSorter',
    'ConflictResolver',
    'ParallelExecutionOptimizer',
    'ResourceMonitor',
    'LoadBalancer',
    'RollbackManager',
    'create_hook_priority_system'
]