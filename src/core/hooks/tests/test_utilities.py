#!/usr/bin/env python3
"""
Hook Test Utilities - V3.6.9
Provides utility functions and classes for hook testing including:
- Mock data generators
- Test environment setup helpers
- Performance measurement tools
- Test data validation
- Hook execution helpers
"""

import json
import os
import time
import tempfile
import shutil
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Generator
from contextlib import contextmanager
import psutil
import logging

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Generates comprehensive test data for different hook types"""
    
    @staticmethod
    def generate_user_prompt_data() -> Dict[str, Any]:
        """Generate test data for user prompt scenarios"""
        return {
            "user_input": "Create a React component for user authentication",
            "context": {
                "project_type": "web_application",
                "framework": "react",
                "language": "typescript",
                "current_file": "src/components/Auth.tsx"
            },
            "session_data": {
                "session_id": str(uuid.uuid4()),
                "user_id": "test_user_123",
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {
                "request_type": "code_generation",
                "complexity": "medium",
                "estimated_tokens": 1500
            }
        }
    
    @staticmethod
    def generate_claude_response_data() -> Dict[str, Any]:
        """Generate test data for Claude response scenarios"""
        return {
            "response_text": "Here's a React authentication component...",
            "response_metadata": {
                "model": "claude-3-sonnet-20240229",
                "tokens_used": 1247,
                "response_time_ms": 2341,
                "completion_reason": "stop"
            },
            "context": {
                "conversation_id": str(uuid.uuid4()),
                "message_count": 5,
                "user_satisfaction": None
            },
            "processing_data": {
                "hooks_triggered": ["code_formatter", "documentation_generator"],
                "execution_time": 0.234,
                "success": True
            }
        }
    
    @staticmethod
    def generate_agent_activation_data() -> Dict[str, Any]:
        """Generate test data for agent activation scenarios"""
        return {
            "agent_mention": "@agent-frontend-architecture",
            "agent_context": {
                "requested_agent": "frontend-architecture", 
                "requesting_user": "test_user",
                "project_context": {
                    "name": "E-commerce Platform",
                    "type": "full_stack_web",
                    "phase": "development"
                }
            },
            "delegation_data": {
                "task_description": "Design scalable frontend architecture",
                "priority": "high",
                "estimated_duration": "2-3 hours",
                "dependencies": ["backend-services", "database-architecture"]
            },
            "workflow_data": {
                "current_step": 3,
                "total_steps": 8,
                "workflow_id": str(uuid.uuid4())
            }
        }
    
    @staticmethod
    def generate_file_change_data() -> Dict[str, Any]:
        """Generate test data for file change scenarios"""
        return {
            "file_path": "/project/src/components/UserProfile.tsx",
            "change_type": "modified",
            "file_info": {
                "size_bytes": 2847,
                "last_modified": datetime.now().isoformat(),
                "file_type": "typescript",
                "line_count": 89
            },
            "change_details": {
                "lines_added": 12,
                "lines_deleted": 3,
                "lines_modified": 7,
                "change_summary": "Added user avatar upload functionality"
            },
            "git_info": {
                "branch": "feature/user-profiles",
                "commit_hash": None,  # Not committed yet
                "author": "test_developer",
                "staged": False
            }
        }
    
    @staticmethod
    def generate_mcp_request_data() -> Dict[str, Any]:
        """Generate test data for MCP request scenarios"""
        return {
            "mcp_method": "tools/call",
            "mcp_params": {
                "name": "code_analyzer",
                "arguments": {
                    "file_path": "/project/src/utils/api.ts",
                    "analysis_type": "security_check"
                }
            },
            "request_metadata": {
                "request_id": str(uuid.uuid4()),
                "client_id": "claude_code_agent",
                "timestamp": datetime.now().isoformat(),
                "timeout": 30.0
            },
            "context": {
                "project_root": "/project",
                "active_files": ["src/utils/api.ts", "src/types/api.ts"],
                "language_server": "typescript"
            }
        }
    
    @staticmethod
    def generate_system_event_data() -> Dict[str, Any]:
        """Generate test data for system event scenarios"""
        return {
            "event_type": "resource_threshold_exceeded",
            "event_data": {
                "resource_type": "memory",
                "current_usage": 87.3,
                "threshold": 85.0,
                "trend": "increasing"
            },
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0.5, 0.6, 0.7]
            },
            "timestamp": datetime.now().isoformat(),
            "severity": "warning",
            "recommended_action": "optimize_memory_usage"
        }
    
    @staticmethod
    def generate_performance_data() -> Dict[str, Any]:
        """Generate test data for performance monitoring"""
        return {
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_io_read": 1234567,
                "disk_io_write": 987654,
                "network_io_sent": 2345678,
                "network_io_recv": 3456789
            },
            "hook_performance": {
                "execution_time_ms": 234.5,
                "memory_delta": 1024 * 1024,  # 1MB
                "cpu_time_ms": 156.7,
                "io_operations": 12
            },
            "thresholds": {
                "max_execution_time": 5000,
                "max_memory_usage": 100 * 1024 * 1024,  # 100MB
                "max_cpu_usage": 80.0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_error_scenario_data(error_type: str) -> Dict[str, Any]:
        """Generate test data for error scenarios"""
        base_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": str(uuid.uuid4()),
            "error_context": {
                "hook_name": "test_hook",
                "trigger": "test_trigger",
                "execution_id": str(uuid.uuid4())
            }
        }
        
        error_scenarios = {
            "timeout": {
                **base_data,
                "operation": "long_running_task",
                "timeout_seconds": 5.0,
                "expected_duration": 30.0,
                "resource_usage": "high"
            },
            "memory_exhaustion": {
                **base_data,
                "operation": "memory_intensive_task",
                "memory_limit": 50 * 1024 * 1024,  # 50MB
                "current_usage": 48 * 1024 * 1024,  # 48MB
                "allocation_size": 10 * 1024 * 1024  # 10MB (would exceed limit)
            },
            "file_not_found": {
                **base_data,
                "operation": "file_access",
                "file_path": "/nonexistent/path/file.txt",
                "access_type": "read",
                "permissions_required": "read"
            },
            "permission_denied": {
                **base_data,
                "operation": "file_write",
                "file_path": "/restricted/system/file.txt",
                "access_type": "write",
                "current_permissions": "read-only"
            },
            "network_failure": {
                **base_data,
                "operation": "api_request",
                "endpoint": "https://api.example.com/data",
                "method": "GET",
                "error_type": "connection_timeout"
            },
            "dependency_failure": {
                **base_data,
                "operation": "hook_execution",
                "dependency_hook": "required_dependency",
                "dependency_status": "failed",
                "failure_reason": "initialization_error"
            }
        }
        
        return error_scenarios.get(error_type, base_data)


class TestEnvironmentManager:
    """Manages test environment setup and cleanup"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.temp_dir = None
        self.created_files = []
        self.spawned_processes = []
        self.temp_configs = []
        
    def __enter__(self):
        self.setup()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def setup(self):
        """Setup test environment"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"hook_test_{self.test_name}_")
        logger.debug(f"Created test environment at: {self.temp_dir}")
        
        # Create standard test directories
        test_dirs = ['config', 'data', 'logs', 'temp']
        for dir_name in test_dirs:
            os.makedirs(os.path.join(self.temp_dir, dir_name), exist_ok=True)
            
    def cleanup(self):
        """Cleanup test environment"""
        # Terminate spawned processes
        for process in self.spawned_processes:
            try:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=5)
                    if process.is_alive():
                        process.kill()
            except Exception as e:
                logger.warning(f"Failed to terminate process: {e}")
        
        # Remove created files
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")
                
        # Remove temporary configurations
        for config_file in self.temp_configs:
            try:
                if os.path.exists(config_file):
                    os.remove(config_file)
            except Exception as e:
                logger.warning(f"Failed to remove config {config_file}: {e}")
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up test environment: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory {self.temp_dir}: {e}")
                
    def create_test_file(self, file_name: str, content: str = "") -> str:
        """Create a test file and track it for cleanup"""
        file_path = os.path.join(self.temp_dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        self.created_files.append(file_path)
        return file_path
        
    def create_test_config(self, config_data: Dict[str, Any], file_name: str = "test_config.json") -> str:
        """Create a test configuration file"""
        config_path = os.path.join(self.temp_dir, 'config', file_name)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
            
        self.temp_configs.append(config_path)
        return config_path
        
    def get_temp_path(self, relative_path: str = "") -> str:
        """Get path within temporary directory"""
        return os.path.join(self.temp_dir, relative_path)


class PerformanceProfiler:
    """Profiles hook performance and resource usage"""
    
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.start_cpu_time = None
        self.end_cpu_time = None
        self.process = psutil.Process()
        
    def __enter__(self):
        self.start_profiling()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_profiling()
        
    def start_profiling(self):
        """Start performance profiling"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        self.start_cpu_time = self.process.cpu_times().user + self.process.cpu_times().system
        
    def stop_profiling(self):
        """Stop performance profiling"""
        self.end_time = time.time()
        self.end_memory = self.process.memory_info().rss
        self.end_cpu_time = self.process.cpu_times().user + self.process.cpu_times().system
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not (self.start_time and self.end_time):
            raise ValueError("Profiling not completed")
            
        return {
            "hook_name": self.hook_name,
            "execution_time_ms": (self.end_time - self.start_time) * 1000,
            "memory_usage_bytes": self.end_memory - self.start_memory,
            "cpu_time_ms": (self.end_cpu_time - self.start_cpu_time) * 1000,
            "peak_memory_bytes": self.process.memory_info().peak_wset if hasattr(self.process.memory_info(), 'peak_wset') else None,
            "timestamp": datetime.now().isoformat()
        }


class ConcurrencyTester:
    """Tests hook behavior under concurrent execution"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.execution_results = []
        self.lock = threading.Lock()
        
    def execute_concurrent_hooks(self, hook_executor: Callable, test_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple hooks concurrently"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_data = {}
            for i, data in enumerate(test_data):
                future = executor.submit(self._execute_with_profiling, hook_executor, data, i)
                future_to_data[future] = data
                
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(future_to_data):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "data": future_to_data[future]
                    })
                    
        return results
        
    def _execute_with_profiling(self, hook_executor: Callable, data: Dict[str, Any], execution_id: int) -> Dict[str, Any]:
        """Execute hook with performance profiling"""
        start_time = time.time()
        
        try:
            with PerformanceProfiler(f"concurrent_execution_{execution_id}") as profiler:
                result = hook_executor(data)
                
            metrics = profiler.get_metrics()
            
            return {
                "success": True,
                "execution_id": execution_id,
                "result": result,
                "metrics": metrics,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
            
    def analyze_concurrency_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze concurrency test results"""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        if successful:
            execution_times = [r["execution_time"] for r in successful]
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
        else:
            avg_execution_time = max_execution_time = min_execution_time = 0
            
        return {
            "total_executions": len(results),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "avg_execution_time": avg_execution_time,
            "max_execution_time": max_execution_time,
            "min_execution_time": min_execution_time,
            "concurrency_efficiency": self._calculate_efficiency(results)
        }
        
    def _calculate_efficiency(self, results: List[Dict[str, Any]]) -> float:
        """Calculate concurrency efficiency"""
        successful = [r for r in results if r.get("success", False)]
        if len(successful) < 2:
            return 0.0
            
        # Compare concurrent execution time vs sequential
        concurrent_time = max(r["execution_time"] for r in successful)
        sequential_time = sum(r["execution_time"] for r in successful)
        
        # Efficiency = Sequential Time / (Concurrent Time * Number of Workers)
        efficiency = sequential_time / (concurrent_time * min(self.max_workers, len(successful)))
        return min(1.0, efficiency)  # Cap at 100% efficiency


class TestValidator:
    """Validates test results and data integrity"""
    
    @staticmethod
    def validate_hook_execution_result(result: Any, expected_type: type = None) -> bool:
        """Validate hook execution result"""
        if result is None:
            return False
            
        if expected_type and not isinstance(result, expected_type):
            return False
            
        # Check for common result patterns
        if isinstance(result, dict):
            required_fields = ["status", "timestamp"]
            if not all(field in result for field in required_fields):
                return False
                
        return True
        
    @staticmethod
    def validate_performance_metrics(metrics: Dict[str, Any], thresholds: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """Validate performance metrics against thresholds"""
        issues = []
        
        # Default thresholds
        default_thresholds = {
            "execution_time_ms": 5000,  # 5 seconds
            "memory_usage_bytes": 100 * 1024 * 1024,  # 100MB
            "cpu_time_ms": 10000  # 10 seconds
        }
        
        thresholds = thresholds or default_thresholds
        
        # Check execution time
        if "execution_time_ms" in metrics:
            if metrics["execution_time_ms"] > thresholds.get("execution_time_ms", default_thresholds["execution_time_ms"]):
                issues.append(f"Execution time {metrics['execution_time_ms']:.2f}ms exceeds threshold")
                
        # Check memory usage
        if "memory_usage_bytes" in metrics:
            if metrics["memory_usage_bytes"] > thresholds.get("memory_usage_bytes", default_thresholds["memory_usage_bytes"]):
                issues.append(f"Memory usage {metrics['memory_usage_bytes']} bytes exceeds threshold")
                
        # Check CPU time
        if "cpu_time_ms" in metrics:
            if metrics["cpu_time_ms"] > thresholds.get("cpu_time_ms", default_thresholds["cpu_time_ms"]):
                issues.append(f"CPU time {metrics['cpu_time_ms']:.2f}ms exceeds threshold")
                
        return len(issues) == 0, issues
        
    @staticmethod
    def validate_test_data_integrity(data: Dict[str, Any], schema: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """Validate test data integrity"""
        issues = []
        
        # Check for required fields
        required_fields = ["timestamp", "session_id"] if not schema else schema.get("required", [])
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
                
        # Check data types
        if schema and "types" in schema:
            for field, expected_type in schema["types"].items():
                if field in data and not isinstance(data[field], expected_type):
                    issues.append(f"Field '{field}' has incorrect type. Expected {expected_type.__name__}, got {type(data[field]).__name__}")
                    
        # Check for null/empty values in critical fields
        critical_fields = ["session_id", "timestamp", "context"]
        for field in critical_fields:
            if field in data and (data[field] is None or data[field] == ""):
                issues.append(f"Critical field '{field}' is null or empty")
                
        return len(issues) == 0, issues


class HookExecutionHelper:
    """Helper for executing hooks with various scenarios"""
    
    def __init__(self, hook_manager):
        self.hook_manager = hook_manager
        self.execution_history = []
        
    def execute_with_timeout(self, hook_name: str, trigger: str, data: Dict[str, Any], timeout: float = 30.0) -> Optional[str]:
        """Execute hook with timeout handling"""
        start_time = time.time()
        
        try:
            execution_id = self.hook_manager.execute_hook(hook_name, trigger, data, timeout=timeout)
            
            # Record execution
            self.execution_history.append({
                "hook_name": hook_name,
                "trigger": trigger,
                "execution_id": execution_id,
                "execution_time": time.time() - start_time,
                "success": execution_id is not None,
                "timestamp": datetime.now().isoformat()
            })
            
            return execution_id
            
        except Exception as e:
            self.execution_history.append({
                "hook_name": hook_name,
                "trigger": trigger,
                "execution_id": None,
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
            
    def execute_with_retry(self, hook_name: str, trigger: str, data: Dict[str, Any], max_retries: int = 3, retry_delay: float = 1.0) -> Optional[str]:
        """Execute hook with retry logic"""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                execution_id = self.execute_with_timeout(hook_name, trigger, data)
                if execution_id:
                    return execution_id
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        # All retries failed
        if last_error:
            raise last_error
        return None
        
    def execute_batch(self, executions: List[Dict[str, Any]], parallel: bool = False) -> List[Dict[str, Any]]:
        """Execute batch of hooks"""
        results = []
        
        if parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for execution in executions:
                    future = executor.submit(
                        self.execute_with_timeout,
                        execution["hook_name"],
                        execution["trigger"],
                        execution["data"]
                    )
                    futures.append((future, execution))
                    
                for future, execution in futures:
                    try:
                        execution_id = future.result(timeout=30)
                        results.append({
                            "execution": execution,
                            "execution_id": execution_id,
                            "success": execution_id is not None
                        })
                    except Exception as e:
                        results.append({
                            "execution": execution,
                            "execution_id": None,
                            "success": False,
                            "error": str(e)
                        })
        else:
            for execution in executions:
                try:
                    execution_id = self.execute_with_timeout(
                        execution["hook_name"],
                        execution["trigger"],
                        execution["data"]
                    )
                    results.append({
                        "execution": execution,
                        "execution_id": execution_id,
                        "success": execution_id is not None
                    })
                except Exception as e:
                    results.append({
                        "execution": execution,
                        "execution_id": None,
                        "success": False,
                        "error": str(e)
                    })
                    
        return results
        
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {}
            
        successful = [e for e in self.execution_history if e["success"]]
        failed = [e for e in self.execution_history if not e["success"]]
        
        execution_times = [e["execution_time"] for e in self.execution_history]
        
        return {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": len(successful) / len(self.execution_history) * 100,
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "unique_hooks_tested": len(set(e["hook_name"] for e in self.execution_history))
        }


@contextmanager
def isolated_test_environment(test_name: str):
    """Context manager for isolated test environment"""
    env_manager = TestEnvironmentManager(test_name)
    try:
        env_manager.setup()
        yield env_manager
    finally:
        env_manager.cleanup()


@contextmanager
def performance_monitoring(hook_name: str):
    """Context manager for performance monitoring"""
    profiler = PerformanceProfiler(hook_name)
    try:
        profiler.start_profiling()
        yield profiler
    finally:
        profiler.stop_profiling()


def create_comprehensive_test_data(hook_name: str, scenario: str = "normal") -> Dict[str, Any]:
    """Create comprehensive test data for any hook"""
    generator = TestDataGenerator()
    
    # Base data
    base_data = {
        "hook_name": hook_name,
        "test_scenario": scenario,
        "timestamp": datetime.now().isoformat(),
        "test_id": str(uuid.uuid4())
    }
    
    # Hook-specific data based on hook group
    hook_groups = {
        "orchestration": generator.generate_agent_activation_data,
        "routing": generator.generate_user_prompt_data,
        "feedback": generator.generate_claude_response_data,
        "ui": generator.generate_system_event_data,
        "automation": generator.generate_file_change_data,
        "quality": generator.generate_file_change_data,
        "monitoring": generator.generate_performance_data,
        "state": generator.generate_user_prompt_data,
        "config": generator.generate_system_event_data,
        "workflow": generator.generate_agent_activation_data,
        "execution": generator.generate_mcp_request_data,
        "special": generator.generate_user_prompt_data,
        "migration": generator.generate_system_event_data
    }
    
    # Try to determine hook group from name patterns
    for group, data_generator in hook_groups.items():
        if group in hook_name.lower():
            specific_data = data_generator()
            base_data.update(specific_data)
            break
    else:
        # Default to user prompt data
        specific_data = generator.generate_user_prompt_data()
        base_data.update(specific_data)
    
    # Add scenario-specific modifications
    if scenario == "error":
        error_data = generator.generate_error_scenario_data("timeout")
        base_data.update(error_data)
    elif scenario == "performance":
        perf_data = generator.generate_performance_data()
        base_data.update(perf_data)
    elif scenario == "concurrency":
        base_data["concurrent_id"] = threading.get_ident()
        base_data["thread_count"] = threading.active_count()
    
    return base_data


# Export utility functions
__all__ = [
    'TestDataGenerator',
    'TestEnvironmentManager', 
    'PerformanceProfiler',
    'ConcurrencyTester',
    'TestValidator',
    'HookExecutionHelper',
    'isolated_test_environment',
    'performance_monitoring',
    'create_comprehensive_test_data'
]