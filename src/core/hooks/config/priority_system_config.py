#!/usr/bin/env python3
"""
Hook Priority System Configuration and Integration
Provides configuration management and integration utilities for the sophisticated hook priority system.

Author: Claude Technical Specifications Agent
Version: 1.0.0
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from hook_priority_system import (
    ConflictResolutionStrategy, RollbackScope, ExecutionPhase
)


@dataclass
class PrioritySystemConfig:
    """Configuration for the hook priority system"""
    
    # Basic configuration
    enabled: bool = True
    max_workers: int = 8
    max_execution_time_ms: int = 30000
    enable_hot_reload: bool = True
    
    # Priority calculation weights
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        'base_priority': 0.40,
        'dependency_depth': 0.15,
        'execution_frequency': 0.15,
        'success_rate': 0.10,
        'system_load': 0.10,
        'time_sensitivity': 0.05,
        'resource_availability': 0.05
    })
    
    # Conflict resolution
    default_conflict_strategy: str = "priority_based"
    conflict_strategies_by_trigger: Dict[str, str] = field(default_factory=dict)
    
    # Parallel execution
    enable_parallel_optimization: bool = True
    max_batch_size: int = 32
    resource_threshold_cpu: float = 80.0
    resource_threshold_memory: float = 90.0
    
    # Rollback configuration
    enable_rollback: bool = True
    default_rollback_scope: str = "dependency_chain"
    rollback_timeout_ms: int = 10000
    max_rollback_history: int = 1000
    
    # Performance optimization
    enable_dynamic_priority_adjustment: bool = True
    performance_monitoring_enabled: bool = True
    optimization_interval_seconds: int = 300  # 5 minutes
    performance_history_size: int = 1000
    
    # Resource management
    enable_resource_monitoring: bool = True
    resource_monitoring_interval_seconds: int = 1
    load_balancing_enabled: bool = True
    
    # Execution phases
    phase_configuration: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'pre_validation': {
            'timeout_ms': 5000,
            'max_parallelism': 2,
            'required': True
        },
        'initialization': {
            'timeout_ms': 10000,
            'max_parallelism': 4,
            'required': True
        },
        'core_processing': {
            'timeout_ms': 20000,
            'max_parallelism': 8,
            'required': False
        },
        'post_processing': {
            'timeout_ms': 15000,
            'max_parallelism': 6,
            'required': False
        },
        'cleanup': {
            'timeout_ms': 8000,
            'max_parallelism': 4,
            'required': False
        },
        'finalization': {
            'timeout_ms': 10000,
            'max_parallelism': 2,
            'required': False
        }
    })
    
    # Logging and debugging
    enable_debug_logging: bool = False
    log_level: str = "INFO"
    log_file_path: Optional[str] = None
    enable_performance_tracing: bool = False


class ConfigurationManager:
    """Manages configuration for the hook priority system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else self._get_default_config_file()
        self.config = PrioritySystemConfig()
        self.load_configuration()
    
    def _get_default_config_file(self) -> Path:
        """Get default configuration file path"""
        # Try user config directory first
        user_config_dir = Path.home() / ".claude" / "hooks"
        user_config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = user_config_dir / "priority_system_config.json"
        
        # If user config doesn't exist, try system config
        if not config_file.exists():
            system_config = Path(__file__).parent / "config" / "priority_system_config.json"
            if system_config.exists():
                return system_config
        
        return config_file
    
    def load_configuration(self) -> bool:
        """Load configuration from file"""
        if not self.config_file.exists():
            self.save_configuration()  # Create default config
            return True
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update config with loaded data
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            return True
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def update_configuration(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    print(f"Warning: Unknown configuration key: {key}")
            
            return self.save_configuration()
        except Exception as e:
            print(f"Failed to update configuration: {e}")
            return False
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return asdict(self.config)
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate basic settings
        if self.config.max_workers <= 0:
            issues.append("max_workers must be greater than 0")
        
        if self.config.max_execution_time_ms <= 0:
            issues.append("max_execution_time_ms must be greater than 0")
        
        # Validate priority weights sum to 1.0
        weight_sum = sum(self.config.priority_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            issues.append(f"Priority weights sum to {weight_sum:.3f}, should sum to 1.0")
        
        # Validate conflict resolution strategies
        valid_strategies = [s.value for s in ConflictResolutionStrategy]
        if self.config.default_conflict_strategy not in valid_strategies:
            issues.append(f"Invalid default conflict strategy: {self.config.default_conflict_strategy}")
        
        for trigger, strategy in self.config.conflict_strategies_by_trigger.items():
            if strategy not in valid_strategies:
                issues.append(f"Invalid conflict strategy for trigger '{trigger}': {strategy}")
        
        # Validate rollback scope
        valid_scopes = [s.value for s in RollbackScope]
        if self.config.default_rollback_scope not in valid_scopes:
            issues.append(f"Invalid default rollback scope: {self.config.default_rollback_scope}")
        
        # Validate resource thresholds
        if not (0 <= self.config.resource_threshold_cpu <= 100):
            issues.append("resource_threshold_cpu must be between 0 and 100")
        
        if not (0 <= self.config.resource_threshold_memory <= 100):
            issues.append("resource_threshold_memory must be between 0 and 100")
        
        # Validate phase configuration
        for phase_name, phase_config in self.config.phase_configuration.items():
            if 'timeout_ms' not in phase_config or phase_config['timeout_ms'] <= 0:
                issues.append(f"Phase '{phase_name}' must have positive timeout_ms")
            
            if 'max_parallelism' not in phase_config or phase_config['max_parallelism'] <= 0:
                issues.append(f"Phase '{phase_name}' must have positive max_parallelism")
        
        return issues


class IntegrationHelper:
    """Helper class for integrating the priority system with existing code"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.config = config_manager.config
    
    def create_priority_system_config(self) -> Dict[str, Any]:
        """Create configuration dict for priority system initialization"""
        return {
            'conflict_strategy': self.config.default_conflict_strategy,
            'enable_dynamic_priority': self.config.enable_dynamic_priority_adjustment,
            'max_execution_time_ms': self.config.max_execution_time_ms,
            'max_workers': self.config.max_workers,
            'enable_rollback': self.config.enable_rollback,
            'enable_resource_monitoring': self.config.enable_resource_monitoring,
            'performance_monitoring_enabled': self.config.performance_monitoring_enabled
        }
    
    def get_hook_registry_config(self) -> Dict[str, Any]:
        """Get configuration for hook registry integration"""
        return {
            'hot_reload_enabled': self.config.enable_hot_reload,
            'performance_monitoring': self.config.performance_monitoring_enabled,
            'max_workers': self.config.max_workers
        }
    
    def setup_logging_config(self) -> Dict[str, Any]:
        """Setup logging configuration"""
        log_config = {
            'level': self.config.log_level,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'enable_debug': self.config.enable_debug_logging
        }
        
        if self.config.log_file_path:
            log_config['file'] = self.config.log_file_path
        
        return log_config
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance monitoring configuration"""
        return {
            'enabled': self.config.performance_monitoring_enabled,
            'history_size': self.config.performance_history_size,
            'optimization_interval': self.config.optimization_interval_seconds,
            'enable_tracing': self.config.enable_performance_tracing
        }
    
    def create_integration_code(self, output_file: str = None) -> str:
        """Generate integration code for existing systems"""
        integration_code = f'''#!/usr/bin/env python3
"""
Generated Hook Priority System Integration
Auto-generated integration code for existing hook systems.
"""

from hook_priority_system import create_hook_priority_system
from hook_registry import get_hook_registry
import logging

# Configuration
CONFIG = {config_dict}

def setup_priority_system():
    """Setup and configure the hook priority system"""
    # Get or create hook registry
    registry = get_hook_registry()
    
    # Create priority system with configuration
    priority_system = create_hook_priority_system(registry, CONFIG)
    
    # Setup logging if enabled
    if CONFIG.get('enable_debug_logging', False):
        logging.basicConfig(
            level=getattr(logging, CONFIG.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    return priority_system

def execute_hooks_with_priority(trigger: str, hook_names: list, context: dict = None):
    """Execute hooks using the priority system"""
    priority_system = setup_priority_system()
    
    # Calculate execution order
    execution_plan = priority_system.calculate_execution_order(
        trigger=trigger,
        hook_names=hook_names,
        context=context or {{}}
    )
    
    # Execute with priority and optimization
    result = priority_system.execute_with_priority(
        execution_plan,
        context=context or {{}}
    )
    
    return result

def optimize_system_performance():
    """Run system performance optimization"""
    priority_system = setup_priority_system()
    return priority_system.optimize_system_performance()

# Example usage
if __name__ == "__main__":
    # Initialize priority system
    priority_system = setup_priority_system()
    
    # Example: Execute hooks for user login
    result = execute_hooks_with_priority(
        trigger="user_login",
        hook_names=["auth_manager", "audit_logger", "session_manager"],
        context={{"time_sensitivity": "high", "enable_rollback": True}}
    )
    
    print(f"Execution result: {{result['overall_success']}}")
    print(f"Execution time: {{result['total_execution_time_ms']:.1f}}ms")
'''
        
        formatted_code = integration_code.format(
            config_dict=json.dumps(self.create_priority_system_config(), indent=4)
        )
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(formatted_code)
        
        return formatted_code
    
    def create_migration_guide(self) -> str:
        """Create migration guide for existing hook systems"""
        guide = '''# Hook Priority System Migration Guide

## Overview
This guide helps you migrate from basic hook execution to the sophisticated hook priority system.

## Step 1: Update Hook Metadata
Add priority system metadata to your existing hooks:

```python
# @priority: HIGH
# @triggers: user_login, api_request
# @depends: system_validation
# @provides: authentication
# @tags: auth, security, critical
# @phase: initialization
```

## Step 2: Configure Priority System
Create configuration file:

```bash
cp priority_system_config.json ~/.claude/hooks/
```

Edit configuration to match your needs:
- Adjust priority weights based on your system requirements
- Configure conflict resolution strategies per trigger
- Set resource thresholds appropriate for your environment

## Step 3: Replace Hook Execution
Replace direct hook calls:

```python
# OLD: Direct execution
for hook in hooks:
    hook.execute()

# NEW: Priority-based execution
execution_plan = priority_system.calculate_execution_order(
    trigger="your_trigger",
    hook_names=hook_names,
    context={"time_sensitivity": "normal"}
)

result = priority_system.execute_with_priority(execution_plan)
```

## Step 4: Add Error Handling and Rollback
Implement rollback support:

```python
result = priority_system.execute_with_priority(
    execution_plan,
    context={"enable_rollback": True}
)

if not result['overall_success'] and result['rollback_performed']:
    print("Execution failed, rollback completed")
```

## Step 5: Performance Monitoring
Enable performance optimization:

```python
# Run periodic optimization
optimization_result = priority_system.optimize_system_performance()
print(f"Optimizations applied: {optimization_result['actions_taken']}")
```

## Step 6: Testing and Validation
Test your migration:

```bash
python priority_system_demo.py
```

## Common Migration Patterns

### Pattern 1: Critical Path Hooks
```python
# Mark critical hooks with HIGH or CRITICAL priority
# Add dependencies to ensure execution order
# Enable rollback for critical operations
```

### Pattern 2: Background Processing
```python
# Use LOW or MAINTENANCE priority
# Group in cleanup or finalization phases
# Allow parallel execution where possible
```

### Pattern 3: Resource-Intensive Operations
```python
# Configure resource allocation requirements
# Use load-based conflict resolution
# Implement proper timeout handling
```

## Configuration Examples

### High-Performance Configuration
```json
{
  "max_workers": 16,
  "enable_parallel_optimization": true,
  "resource_threshold_cpu": 90.0,
  "enable_dynamic_priority_adjustment": true
}
```

### Reliability-Focused Configuration
```json
{
  "enable_rollback": true,
  "default_rollback_scope": "dependency_chain",
  "max_execution_time_ms": 60000,
  "enable_performance_tracing": true
}
```

### Resource-Constrained Configuration
```json
{
  "max_workers": 4,
  "resource_threshold_cpu": 70.0,
  "resource_threshold_memory": 80.0,
  "max_batch_size": 8
}
```
'''
        return guide


def create_default_config_file(config_path: str = None) -> str:
    """Create default configuration file"""
    if not config_path:
        config_path = Path.home() / ".claude" / "hooks" / "priority_system_config.json"
    
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    default_config = PrioritySystemConfig()
    
    with open(config_path, 'w') as f:
        json.dump(asdict(default_config), f, indent=2)
    
    return str(config_path)


def validate_system_configuration(config_file: str = None) -> Dict[str, Any]:
    """Validate system configuration and return validation report"""
    config_manager = ConfigurationManager(config_file)
    issues = config_manager.validate_configuration()
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'config_file': str(config_manager.config_file),
        'config': config_manager.get_config_dict()
    }


def main():
    """Main configuration utility"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hook Priority System Configuration Utility")
    parser.add_argument('--create-config', action='store_true', 
                       help='Create default configuration file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--integration-code', type=str,
                       help='Generate integration code file')
    parser.add_argument('--migration-guide', type=str,
                       help='Generate migration guide file')
    parser.add_argument('--config-file', type=str,
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    if args.create_config:
        config_path = create_default_config_file(args.config_file)
        print(f"✅ Default configuration created at: {config_path}")
    
    if args.validate:
        validation = validate_system_configuration(args.config_file)
        if validation['valid']:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues:")
            for issue in validation['issues']:
                print(f"  • {issue}")
    
    if args.integration_code:
        config_manager = ConfigurationManager(args.config_file)
        helper = IntegrationHelper(config_manager)
        code = helper.create_integration_code(args.integration_code)
        print(f"✅ Integration code generated: {args.integration_code}")
    
    if args.migration_guide:
        config_manager = ConfigurationManager(args.config_file)
        helper = IntegrationHelper(config_manager)
        guide = helper.create_migration_guide()
        
        with open(args.migration_guide, 'w') as f:
            f.write(guide)
        
        print(f"✅ Migration guide generated: {args.migration_guide}")


if __name__ == "__main__":
    main()