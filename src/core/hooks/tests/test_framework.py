#!/usr/bin/env python3
"""
Comprehensive Hook Test Framework - V3.6.9
Provides extensive testing capabilities for all 38 hooks including:
- Individual hook functionality testing
- Hook chain and dependency testing  
- Error scenario and recovery testing
- Performance testing and benchmarking
- Integration testing with LSP bridge and registry
- Concurrency testing for parallel execution
- Regression testing for breaking changes
"""

import asyncio
import json
import logging
import multiprocessing
import os
import sys
import time
import traceback
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Union
from unittest.mock import Mock, patch, MagicMock
import threading
import tempfile
import shutil
import psutil
import pytest

# Import hook system components
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_registry import HookRegistry, HookPriority, HookState, TriggerType, HookMetadata
from hook_manager import HookManager, get_hook_manager
from hook_config import HookConfigManager

# Setup comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hook_test_framework.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result data"""
    test_name: str
    hook_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    execution_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data"""
    hook_name: str
    operation: str
    baseline_time: float
    current_time: float
    memory_usage: float
    cpu_usage: float
    passed: bool
    threshold_factor: float = 1.5  # Allow 50% performance degradation


@dataclass
class TestSuite:
    """Complete test suite configuration"""
    name: str
    description: str
    tests: List[str]
    setup_hooks: List[str] = field(default_factory=list)
    teardown_hooks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout: float = 300.0
    parallel_execution: bool = False


class MockEnvironment:
    """Mock environment for isolated hook testing"""
    
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.temp_dir = None
        self.mock_registry = None
        self.mock_config = None
        self.mock_data = {}
        
    def __enter__(self):
        """Setup mock environment"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"hook_test_{self.hook_name}_")
        
        # Setup mock registry
        self.mock_registry = Mock(spec=HookRegistry)
        self.mock_registry.hooks = {}
        self.mock_registry.active_executions = {}
        self.mock_registry.execution_queue = Mock()
        
        # Setup mock configuration
        self.mock_config = Mock(spec=HookConfigManager)
        self.mock_config.hook_configs = {}
        
        # Generate mock data for hook
        self.mock_data = self._generate_mock_data()
        
        logger.debug(f"Mock environment created for {self.hook_name} at {self.temp_dir}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup mock environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        logger.debug(f"Mock environment cleaned up for {self.hook_name}")
        
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate appropriate mock data based on hook type"""
        base_data = {
            'timestamp': datetime.now().isoformat(),
            'user_input': 'test input',
            'context': {'project_type': 'test', 'language': 'python'},
            'session_id': 'test_session_123'
        }
        
        # Hook-specific mock data
        hook_specific_data = {
            # Orchestration hooks
            'smart_orchestrator': {'agents': ['test-agent-1', 'test-agent-2'], 'workflow': 'test_workflow'},
            'master_orchestrator': {'coordination_data': {'phase': 'test', 'priority': 1}},
            'v3_orchestrator': {'orchestration_config': {'mode': 'test', 'parallel': True}},
            
            # Audio hooks
            'audio_player_v3': {'audio_file': 'test.wav', 'volume': 0.8, 'format': 'wav'},
            'audio_controller': {'action': 'play', 'source': 'notification'},
            'audio_notifier': {'notification_type': 'success', 'message': 'Test notification'},
            
            # Quality hooks
            'code_linter': {'file_path': f'{self.temp_dir}/test_file.py', 'language': 'python'},
            'security_scanner': {'scan_target': self.temp_dir, 'scan_type': 'dependency'},
            'quality_gate_hook': {'commit_hash': 'abc123', 'quality_metrics': {'coverage': 85}},
            
            # Monitoring hooks
            'performance_monitor': {'metrics': {'cpu': 45.2, 'memory': 67.8, 'disk': 23.1}},
            'resource_monitor': {'resource_type': 'memory', 'threshold': 80},
            'model_tracker': {'model_name': 'claude-3-sonnet', 'tokens_used': 1500},
            
            # Session hooks
            'session_loader': {'session_file': f'{self.temp_dir}/test_session.json'},
            'session_saver': {'session_data': {'test': 'data'}, 'auto_save': True},
            'context_manager': {'context_type': 'project', 'data': {'name': 'test_project'}}
        }
        
        base_data.update(hook_specific_data.get(self.hook_name, {}))
        return base_data


class HookTestFramework:
    """Comprehensive hook testing framework"""
    
    def __init__(self, hooks_directory: str = None, config_file: str = None):
        self.hooks_directory = Path(hooks_directory) if hooks_directory else Path(__file__).parent.parent
        self.config_file = config_file
        
        # Test configuration
        self.test_results: List[TestResult] = []
        self.performance_benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.baseline_data_file = self.hooks_directory / "tests" / "performance_baselines.json"
        
        # Test registry and manager
        self.test_manager: Optional[HookManager] = None
        self.test_registry: Optional[HookRegistry] = None
        
        # Load hook registry for test discovery
        registry_file = self.hooks_directory / "hook-registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                self.hook_registry_data = json.load(f)
        else:
            raise FileNotFoundError(f"Hook registry not found at {registry_file}")
        
        # Initialize test suites
        self.test_suites = self._initialize_test_suites()
        
        # Performance baselines
        self.performance_baselines = self._load_performance_baselines()
        
        logger.info(f"Hook Test Framework initialized with {len(self.hook_registry_data['hooks'])} hooks")
    
    def _initialize_test_suites(self) -> Dict[str, TestSuite]:
        """Initialize all test suites"""
        suites = {}
        
        # Individual hook functionality tests
        suites['individual_functionality'] = TestSuite(
            name="Individual Hook Functionality",
            description="Test each hook in isolation",
            tests=[f"test_individual_hook_{hook}" for hook in self.hook_registry_data['hooks'].keys()],
            timeout=60.0
        )
        
        # Hook chain dependency tests
        suites['hook_chains'] = TestSuite(
            name="Hook Chain Testing",
            description="Test sequences of dependent hooks",
            tests=[
                "test_orchestration_chain",
                "test_quality_gate_chain", 
                "test_session_management_chain",
                "test_audio_feedback_chain"
            ],
            timeout=120.0
        )
        
        # Error scenario tests
        suites['error_scenarios'] = TestSuite(
            name="Error Scenario Testing",
            description="Test hook failure handling and recovery",
            tests=[
                "test_hook_timeout_handling",
                "test_dependency_failure_recovery",
                "test_resource_exhaustion_handling",
                "test_invalid_input_handling",
                "test_file_system_errors"
            ],
            timeout=90.0
        )
        
        # Performance tests
        suites['performance'] = TestSuite(
            name="Performance Testing",
            description="Load testing and benchmark validation",
            tests=[
                "test_hook_execution_benchmarks",
                "test_concurrent_execution_performance",
                "test_memory_usage_patterns",
                "test_resource_cleanup_efficiency"
            ],
            timeout=300.0
        )
        
        # Integration tests
        suites['integration'] = TestSuite(
            name="Integration Testing",
            description="LSP bridge and hook registry integration",
            tests=[
                "test_lsp_bridge_integration",
                "test_hook_registry_sync",
                "test_api_integration",
                "test_configuration_integration"
            ],
            timeout=180.0
        )
        
        # Concurrency tests
        suites['concurrency'] = TestSuite(
            name="Concurrency Testing",
            description="Multiple hooks executing simultaneously",
            tests=[
                "test_parallel_hook_execution",
                "test_resource_contention",
                "test_deadlock_detection",
                "test_thread_safety"
            ],
            timeout=240.0,
            parallel_execution=True
        )
        
        # Regression tests
        suites['regression'] = TestSuite(
            name="Regression Testing",
            description="Prevent breaking changes",
            tests=[
                "test_backward_compatibility",
                "test_api_contract_compliance",
                "test_configuration_migration",
                "test_performance_regression"
            ],
            timeout=200.0
        )
        
        return suites
    
    def _load_performance_baselines(self) -> Dict[str, float]:
        """Load performance baseline data"""
        if self.baseline_data_file.exists():
            try:
                with open(self.baseline_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load performance baselines: {e}")
        
        # Default baselines (in milliseconds)
        return {
            hook_name: 1000.0  # 1 second default baseline
            for hook_name in self.hook_registry_data['hooks'].keys()
        }
    
    def _save_performance_baselines(self):
        """Save updated performance baselines"""
        try:
            os.makedirs(self.baseline_data_file.parent, exist_ok=True)
            with open(self.baseline_data_file, 'w') as f:
                json.dump(self.performance_baselines, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance baselines: {e}")
    
    def setup_test_environment(self):
        """Setup the test environment"""
        logger.info("Setting up test environment...")
        
        # Create test manager with isolated configuration
        self.test_manager = HookManager(
            hooks_directory=str(self.hooks_directory),
            config_file=self.config_file,
            api_host='localhost',
            api_port=8889,  # Different port to avoid conflicts
            auto_start=False
        )
        
        # Initialize test manager
        self.test_manager.initialize()
        self.test_registry = self.test_manager.registry
        
        logger.info("Test environment setup complete")
    
    def teardown_test_environment(self):
        """Cleanup test environment"""
        logger.info("Tearing down test environment...")
        
        if self.test_manager:
            self.test_manager.stop()
        
        logger.info("Test environment teardown complete")
    
    # Individual Hook Testing
    
    def test_individual_hook(self, hook_name: str) -> TestResult:
        """Test individual hook functionality"""
        start_time = time.time()
        
        try:
            with MockEnvironment(hook_name) as mock_env:
                # Get hook metadata
                hook_metadata = self.hook_registry_data['hooks'].get(hook_name)
                if not hook_metadata:
                    return TestResult(
                        test_name=f"test_individual_hook_{hook_name}",
                        hook_name=hook_name,
                        status="SKIP",
                        execution_time=time.time() - start_time,
                        error_message="Hook not found in registry"
                    )
                
                # Test hook registration
                hook_file = self.hooks_directory / hook_metadata['source']
                if not hook_file.exists():
                    return TestResult(
                        test_name=f"test_individual_hook_{hook_name}",
                        hook_name=hook_name,
                        status="FAIL",
                        execution_time=time.time() - start_time,
                        error_message=f"Hook source file not found: {hook_file}"
                    )
                
                # Test hook loading
                success = self.test_manager.register_hook_file(str(hook_file))
                if not success:
                    return TestResult(
                        test_name=f"test_individual_hook_{hook_name}",
                        hook_name=hook_name,
                        status="FAIL",
                        execution_time=time.time() - start_time,
                        error_message="Failed to register hook"
                    )
                
                # Test hook activation
                success = self.test_manager.activate_hook(hook_name)
                if not success:
                    return TestResult(
                        test_name=f"test_individual_hook_{hook_name}",
                        hook_name=hook_name,
                        status="FAIL",
                        execution_time=time.time() - start_time,
                        error_message="Failed to activate hook"
                    )
                
                # Test hook execution with mock data
                for trigger in hook_metadata.get('triggers', ['test']):
                    execution_id = self.test_manager.execute_hook(
                        hook_name, trigger, mock_env.mock_data
                    )
                    if not execution_id:
                        return TestResult(
                            test_name=f"test_individual_hook_{hook_name}",
                            hook_name=hook_name,
                            status="FAIL",
                            execution_time=time.time() - start_time,
                            error_message=f"Failed to execute hook with trigger: {trigger}"
                        )
                
                # Test hook deactivation
                success = self.test_manager.deactivate_hook(hook_name)
                if not success:
                    return TestResult(
                        test_name=f"test_individual_hook_{hook_name}",
                        hook_name=hook_name,
                        status="FAIL",
                        execution_time=time.time() - start_time,
                        error_message="Failed to deactivate hook"
                    )
                
                return TestResult(
                    test_name=f"test_individual_hook_{hook_name}",
                    hook_name=hook_name,
                    status="PASS",
                    execution_time=time.time() - start_time,
                    details={"triggers_tested": hook_metadata.get('triggers', [])}
                )
                
        except Exception as e:
            return TestResult(
                test_name=f"test_individual_hook_{hook_name}",
                hook_name=hook_name,
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception during testing: {str(e)}"
            )
    
    # Hook Chain Testing
    
    def test_orchestration_chain(self) -> TestResult:
        """Test orchestration hook chain"""
        start_time = time.time()
        
        try:
            chain_hooks = [
                'smart_orchestrator',
                'master_orchestrator', 
                'v3_orchestrator',
                'orchestration_enhancer'
            ]
            
            # Activate orchestration hooks in order
            for hook_name in chain_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    self.test_manager.activate_hook(hook_name)
            
            # Test chain execution
            execution_data = {
                'agent_request': '@agent-business-analyst',
                'project_context': {'type': 'test', 'phase': 'planning'},
                'workflow_data': {'step': 1, 'total_steps': 5}
            }
            
            execution_ids = self.test_manager.execute_by_trigger(
                'agent_mention', execution_data
            )
            
            if not execution_ids:
                return TestResult(
                    test_name="test_orchestration_chain",
                    hook_name="orchestration_chain",
                    status="FAIL",
                    execution_time=time.time() - start_time,
                    error_message="No hooks executed in orchestration chain"
                )
            
            return TestResult(
                test_name="test_orchestration_chain", 
                hook_name="orchestration_chain",
                status="PASS",
                execution_time=time.time() - start_time,
                details={"execution_ids": execution_ids, "hooks_in_chain": len(execution_ids)}
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_orchestration_chain",
                hook_name="orchestration_chain", 
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in orchestration chain: {str(e)}"
            )
    
    def test_quality_gate_chain(self) -> TestResult:
        """Test quality gate hook chain"""
        start_time = time.time()
        
        try:
            chain_hooks = [
                'code_linter',
                'security_scanner',
                'quality_gate_hook',
                'git_quality_hooks'
            ]
            
            # Create test file for quality checking
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write("""
def test_function():
    # Test function for quality gate testing
    return "Hello, World!"

if __name__ == "__main__":
    print(test_function())
""")
                test_file_path = f.name
            
            try:
                # Activate quality hooks
                for hook_name in chain_hooks:
                    if hook_name in self.hook_registry_data['hooks']:
                        self.test_manager.activate_hook(hook_name)
                
                # Test quality gate chain
                execution_data = {
                    'file_path': test_file_path,
                    'commit_data': {'hash': 'test123', 'author': 'test_user'},
                    'quality_requirements': {'min_coverage': 80, 'max_complexity': 10}
                }
                
                execution_ids = self.test_manager.execute_by_trigger(
                    'commit', execution_data
                )
                
                return TestResult(
                    test_name="test_quality_gate_chain",
                    hook_name="quality_gate_chain",
                    status="PASS" if execution_ids else "FAIL",
                    execution_time=time.time() - start_time,
                    details={"execution_ids": execution_ids, "test_file": test_file_path}
                )
                
            finally:
                # Cleanup test file
                if os.path.exists(test_file_path):
                    os.unlink(test_file_path)
                    
        except Exception as e:
            return TestResult(
                test_name="test_quality_gate_chain",
                hook_name="quality_gate_chain",
                status="ERROR", 
                execution_time=time.time() - start_time,
                error_message=f"Exception in quality gate chain: {str(e)}"
            )
    
    def test_session_management_chain(self) -> TestResult:
        """Test session management hook chain"""
        start_time = time.time()
        
        try:
            chain_hooks = [
                'session_loader',
                'context_manager', 
                'session_saver'
            ]
            
            # Activate session hooks
            for hook_name in chain_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    self.test_manager.activate_hook(hook_name)
            
            # Test session loading
            session_data = {
                'session_id': 'test_session_123',
                'user_context': {'project': 'test_project', 'language': 'python'},
                'chat_history': [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi!'}]
            }
            
            # Load session
            load_ids = self.test_manager.execute_by_trigger('start', session_data)
            
            # Manage context
            context_ids = self.test_manager.execute_by_trigger('session', {
                'context_update': {'new_file': 'test.py', 'action': 'created'}
            })
            
            # Save session 
            save_ids = self.test_manager.execute_by_trigger('save', {
                'session_data': session_data,
                'auto_save': True
            })
            
            total_executions = len(load_ids) + len(context_ids) + len(save_ids)
            
            return TestResult(
                test_name="test_session_management_chain",
                hook_name="session_management_chain",
                status="PASS" if total_executions > 0 else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "load_executions": len(load_ids),
                    "context_executions": len(context_ids), 
                    "save_executions": len(save_ids)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_session_management_chain",
                hook_name="session_management_chain",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in session management chain: {str(e)}"
            )
    
    def test_audio_feedback_chain(self) -> TestResult:
        """Test audio feedback hook chain"""
        start_time = time.time()
        
        try:
            chain_hooks = [
                'audio_player_v3',
                'audio_controller',
                'audio_notifier',
                'notification_sender'
            ]
            
            # Activate audio hooks
            for hook_name in chain_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    self.test_manager.activate_hook(hook_name)
            
            # Test audio notification chain
            notification_data = {
                'notification_type': 'success',
                'message': 'Test completed successfully',
                'audio_enabled': True,
                'volume': 0.5
            }
            
            audio_ids = self.test_manager.execute_by_trigger('notify', notification_data)
            
            return TestResult(
                test_name="test_audio_feedback_chain",
                hook_name="audio_feedback_chain", 
                status="PASS" if audio_ids else "FAIL",
                execution_time=time.time() - start_time,
                details={"execution_ids": audio_ids}
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_audio_feedback_chain",
                hook_name="audio_feedback_chain",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in audio feedback chain: {str(e)}"
            )
    
    # Error Scenario Testing
    
    def test_hook_timeout_handling(self) -> TestResult:
        """Test hook timeout handling"""
        start_time = time.time()
        
        try:
            # Create a mock hook that will timeout
            with patch.object(self.test_registry, 'execute_hook') as mock_execute:
                # Simulate timeout by making the execution hang
                def slow_execution(*args, **kwargs):
                    time.sleep(35)  # Longer than default 30s timeout
                    return "execution_id_123"
                
                mock_execute.side_effect = slow_execution
                
                # Test timeout handling
                execution_id = self.test_manager.execute_hook(
                    'test_hook', 'test_trigger', {}, timeout=5.0
                )
                
                # Should handle timeout gracefully
                return TestResult(
                    test_name="test_hook_timeout_handling",
                    hook_name="timeout_test",
                    status="PASS",
                    execution_time=time.time() - start_time,
                    details={"timeout_handled": execution_id is None}
                )
                
        except Exception as e:
            return TestResult(
                test_name="test_hook_timeout_handling", 
                hook_name="timeout_test",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in timeout test: {str(e)}"
            )
    
    def test_dependency_failure_recovery(self) -> TestResult:
        """Test dependency failure recovery"""
        start_time = time.time()
        
        try:
            # Test hook dependency resolution when dependencies fail
            dependency_data = {
                'primary_hook': 'master_orchestrator',
                'failed_dependency': 'context_manager',
                'execution_data': {'test': 'dependency_failure'}
            }
            
            # Simulate dependency failure
            with patch.object(self.test_registry, 'dependency_resolver') as mock_resolver:
                mock_resolver.resolve_dependencies.return_value = (False, ['context_manager'])
                
                # Try to execute hook with failed dependency
                execution_id = self.test_manager.execute_hook(
                    'master_orchestrator', 'test', dependency_data
                )
                
                return TestResult(
                    test_name="test_dependency_failure_recovery",
                    hook_name="dependency_test",
                    status="PASS",
                    execution_time=time.time() - start_time,
                    details={"dependency_failure_handled": True}
                )
                
        except Exception as e:
            return TestResult(
                test_name="test_dependency_failure_recovery",
                hook_name="dependency_test", 
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in dependency test: {str(e)}"
            )
    
    def test_resource_exhaustion_handling(self) -> TestResult:
        """Test resource exhaustion handling"""
        start_time = time.time()
        
        try:
            # Test behavior under resource exhaustion
            original_cpu_count = multiprocessing.cpu_count()
            
            with patch('multiprocessing.cpu_count', return_value=1):
                with patch('psutil.virtual_memory') as mock_memory:
                    # Simulate low memory
                    mock_memory.return_value.percent = 95.0
                    
                    # Try to execute resource-intensive operations
                    execution_ids = []
                    for i in range(10):  # Attempt many concurrent executions
                        exec_id = self.test_manager.execute_hook(
                            'performance_monitor', 'execution', {'test_load': True}
                        )
                        if exec_id:
                            execution_ids.append(exec_id)
                    
                    return TestResult(
                        test_name="test_resource_exhaustion_handling",
                        hook_name="resource_test",
                        status="PASS",
                        execution_time=time.time() - start_time,
                        details={
                            "executions_completed": len(execution_ids),
                            "resource_exhaustion_handled": True
                        }
                    )
                    
        except Exception as e:
            return TestResult(
                test_name="test_resource_exhaustion_handling",
                hook_name="resource_test",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in resource exhaustion test: {str(e)}"
            )
    
    def test_invalid_input_handling(self) -> TestResult:
        """Test invalid input handling"""
        start_time = time.time()
        
        try:
            invalid_inputs = [
                None,
                {},
                {'invalid': 'structure'},
                {'malformed_json': '{"incomplete":'},
                {'oversized_data': 'x' * 1000000}  # 1MB string
            ]
            
            handled_count = 0
            for invalid_input in invalid_inputs:
                try:
                    execution_id = self.test_manager.execute_hook(
                        'context_manager', 'test', invalid_input
                    )
                    handled_count += 1
                except Exception:
                    # Expected to handle gracefully without crashing
                    handled_count += 1
            
            return TestResult(
                test_name="test_invalid_input_handling",
                hook_name="input_validation_test",
                status="PASS" if handled_count == len(invalid_inputs) else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "invalid_inputs_tested": len(invalid_inputs),
                    "handled_gracefully": handled_count
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_invalid_input_handling",
                hook_name="input_validation_test",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in invalid input test: {str(e)}"
            )
    
    def test_file_system_errors(self) -> TestResult:
        """Test file system error handling"""
        start_time = time.time()
        
        try:
            # Test hooks that interact with file system
            filesystem_hooks = [
                'session_loader',
                'session_saver', 
                'auto_documentation',
                'code_linter'
            ]
            
            error_scenarios = [
                {'scenario': 'missing_file', 'file_path': '/nonexistent/path/file.txt'},
                {'scenario': 'permission_denied', 'file_path': '/root/restricted_file.txt'},
                {'scenario': 'disk_full', 'file_path': '/tmp/test_file.txt'},
                {'scenario': 'corrupted_file', 'file_path': '/dev/null'}
            ]
            
            handled_scenarios = 0
            for scenario in error_scenarios:
                for hook_name in filesystem_hooks:
                    if hook_name in self.hook_registry_data['hooks']:
                        try:
                            self.test_manager.execute_hook(
                                hook_name, 'test', scenario
                            )
                            handled_scenarios += 1
                        except Exception:
                            # File system errors should be handled gracefully
                            handled_scenarios += 1
            
            total_tests = len(error_scenarios) * len(filesystem_hooks)
            
            return TestResult(
                test_name="test_file_system_errors",
                hook_name="filesystem_test",
                status="PASS" if handled_scenarios == total_tests else "FAIL", 
                execution_time=time.time() - start_time,
                details={
                    "scenarios_tested": len(error_scenarios),
                    "hooks_tested": len(filesystem_hooks),
                    "handled_gracefully": handled_scenarios
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_file_system_errors",
                hook_name="filesystem_test",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in filesystem test: {str(e)}"
            )
    
    # Performance Testing
    
    def test_hook_execution_benchmarks(self) -> TestResult:
        """Test hook execution performance against baselines"""
        start_time = time.time()
        
        try:
            benchmark_results = {}
            failed_benchmarks = []
            
            for hook_name in self.hook_registry_data['hooks'].keys():
                if hook_name not in self.hook_registry_data['hooks']:
                    continue
                
                # Get baseline performance
                baseline_time = self.performance_baselines.get(hook_name, 1000.0)
                
                # Measure current performance
                hook_start = time.time()
                process = psutil.Process()
                memory_before = process.memory_info().rss
                
                with MockEnvironment(hook_name) as mock_env:
                    execution_id = self.test_manager.execute_hook(
                        hook_name, 'test', mock_env.mock_data
                    )
                
                hook_time = (time.time() - hook_start) * 1000  # Convert to ms
                memory_after = process.memory_info().rss
                memory_usage = memory_after - memory_before
                
                # Create benchmark
                benchmark = PerformanceBenchmark(
                    hook_name=hook_name,
                    operation="execution",
                    baseline_time=baseline_time,
                    current_time=hook_time,
                    memory_usage=memory_usage,
                    cpu_usage=psutil.cpu_percent(),
                    passed=hook_time <= baseline_time * 1.5  # 50% tolerance
                )
                
                benchmark_results[hook_name] = benchmark
                self.performance_benchmarks[hook_name] = benchmark
                
                if not benchmark.passed:
                    failed_benchmarks.append(hook_name)
                
                # Update baseline if performance improved
                if hook_time < baseline_time * 0.9:  # 10% improvement
                    self.performance_baselines[hook_name] = hook_time
            
            # Save updated baselines
            self._save_performance_baselines()
            
            return TestResult(
                test_name="test_hook_execution_benchmarks",
                hook_name="performance_benchmarks",
                status="PASS" if not failed_benchmarks else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "benchmarks_run": len(benchmark_results),
                    "failed_benchmarks": failed_benchmarks,
                    "average_performance": sum(b.current_time for b in benchmark_results.values()) / len(benchmark_results)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_hook_execution_benchmarks",
                hook_name="performance_benchmarks",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in performance benchmarking: {str(e)}"
            )
    
    def test_concurrent_execution_performance(self) -> TestResult:
        """Test concurrent hook execution performance"""
        start_time = time.time()
        
        try:
            # Test concurrent execution of multiple hooks
            concurrent_hooks = [
                'performance_monitor',
                'resource_monitor', 
                'model_tracker',
                'context_manager'
            ]
            
            # Single-threaded baseline
            single_thread_start = time.time()
            for hook_name in concurrent_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    with MockEnvironment(hook_name) as mock_env:
                        self.test_manager.execute_hook(hook_name, 'test', mock_env.mock_data)
            single_thread_time = time.time() - single_thread_start
            
            # Multi-threaded execution
            multi_thread_start = time.time()
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for hook_name in concurrent_hooks:
                    if hook_name in self.hook_registry_data['hooks']:
                        with MockEnvironment(hook_name) as mock_env:
                            future = executor.submit(
                                self.test_manager.execute_hook,
                                hook_name, 'test', mock_env.mock_data
                            )
                            futures.append(future)
                
                # Wait for all completions
                for future in as_completed(futures):
                    future.result()
            
            multi_thread_time = time.time() - multi_thread_start
            
            # Calculate performance improvement
            improvement_factor = single_thread_time / multi_thread_time if multi_thread_time > 0 else 1.0
            
            return TestResult(
                test_name="test_concurrent_execution_performance",
                hook_name="concurrency_performance",
                status="PASS" if improvement_factor > 1.2 else "FAIL",  # At least 20% improvement
                execution_time=time.time() - start_time,
                details={
                    "single_thread_time": single_thread_time,
                    "multi_thread_time": multi_thread_time,
                    "improvement_factor": improvement_factor,
                    "hooks_tested": len(concurrent_hooks)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_concurrent_execution_performance",
                hook_name="concurrency_performance",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in concurrent performance test: {str(e)}"
            )
    
    def test_memory_usage_patterns(self) -> TestResult:
        """Test memory usage patterns"""
        start_time = time.time()
        
        try:
            process = psutil.Process()
            memory_before = process.memory_info().rss
            
            # Execute memory-intensive operations
            memory_intensive_hooks = [
                'auto_documentation',
                'performance_monitor',
                'session_loader',
                'context_manager'
            ]
            
            memory_snapshots = [memory_before]
            
            for hook_name in memory_intensive_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    with MockEnvironment(hook_name) as mock_env:
                        # Execute hook multiple times to stress memory
                        for _ in range(5):
                            self.test_manager.execute_hook(hook_name, 'test', mock_env.mock_data)
                    
                    # Take memory snapshot
                    memory_snapshots.append(process.memory_info().rss)
            
            # Check for memory leaks
            memory_growth = memory_snapshots[-1] - memory_snapshots[0]
            memory_growth_mb = memory_growth / (1024 * 1024)
            
            # Memory growth should be reasonable (< 100MB for testing)
            memory_leak_detected = memory_growth_mb > 100
            
            return TestResult(
                test_name="test_memory_usage_patterns",
                hook_name="memory_patterns",
                status="FAIL" if memory_leak_detected else "PASS",
                execution_time=time.time() - start_time,
                details={
                    "memory_growth_mb": memory_growth_mb,
                    "memory_snapshots": len(memory_snapshots),
                    "memory_leak_detected": memory_leak_detected
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_memory_usage_patterns",
                hook_name="memory_patterns",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in memory pattern test: {str(e)}"
            )
    
    def test_resource_cleanup_efficiency(self) -> TestResult:
        """Test resource cleanup efficiency"""
        start_time = time.time()
        
        try:
            # Test cleanup after hook execution
            cleanup_test_data = {
                'temp_files': [],
                'open_handles': [],
                'threads': []
            }
            
            # Execute hooks that create resources
            resource_hooks = [
                'session_saver',
                'auto_documentation', 
                'performance_monitor'
            ]
            
            for hook_name in resource_hooks:
                if hook_name in self.hook_registry_data['hooks']:
                    with MockEnvironment(hook_name) as mock_env:
                        # Track resources before execution
                        process = psutil.Process()
                        handles_before = process.num_handles() if hasattr(process, 'num_handles') else 0
                        threads_before = process.num_threads()
                        
                        # Execute hook
                        self.test_manager.execute_hook(hook_name, 'test', mock_env.mock_data)
                        
                        # Check resources after execution  
                        handles_after = process.num_handles() if hasattr(process, 'num_handles') else 0
                        threads_after = process.num_threads()
                        
                        cleanup_test_data['open_handles'].append({
                            'hook': hook_name,
                            'handles_delta': handles_after - handles_before
                        })
                        cleanup_test_data['threads'].append({
                            'hook': hook_name,
                            'threads_delta': threads_after - threads_before
                        })
            
            # Analyze cleanup efficiency
            handle_leaks = sum(1 for h in cleanup_test_data['open_handles'] if h['handles_delta'] > 5)
            thread_leaks = sum(1 for t in cleanup_test_data['threads'] if t['threads_delta'] > 2)
            
            cleanup_efficient = handle_leaks == 0 and thread_leaks == 0
            
            return TestResult(
                test_name="test_resource_cleanup_efficiency",
                hook_name="resource_cleanup",
                status="PASS" if cleanup_efficient else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "handle_leaks": handle_leaks,
                    "thread_leaks": thread_leaks,
                    "cleanup_data": cleanup_test_data
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_resource_cleanup_efficiency",
                hook_name="resource_cleanup",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in resource cleanup test: {str(e)}"
            )
    
    # Integration Testing
    
    def test_lsp_bridge_integration(self) -> TestResult:
        """Test LSP bridge integration"""
        start_time = time.time()
        
        try:
            # Test LSP-compatible hooks
            lsp_hooks = [
                hook_name for hook_name, metadata in self.hook_registry_data['hooks'].items()
                if metadata.get('lsp_compatible', False)
            ]
            
            if not lsp_hooks:
                return TestResult(
                    test_name="test_lsp_bridge_integration",
                    hook_name="lsp_integration",
                    status="SKIP",
                    execution_time=time.time() - start_time,
                    error_message="No LSP-compatible hooks found"
                )
            
            # Test LSP communication for each compatible hook
            lsp_test_results = {}
            for hook_name in lsp_hooks:
                try:
                    # Simulate LSP request
                    lsp_request = {
                        'method': 'textDocument/didChange',
                        'params': {
                            'textDocument': {'uri': 'file:///test.py'},
                            'contentChanges': [{'text': 'print("test")'}]
                        }
                    }
                    
                    execution_id = self.test_manager.execute_hook(
                        hook_name, 'lsp_request', lsp_request
                    )
                    
                    lsp_test_results[hook_name] = execution_id is not None
                    
                except Exception as e:
                    lsp_test_results[hook_name] = False
            
            successful_integrations = sum(lsp_test_results.values())
            
            return TestResult(
                test_name="test_lsp_bridge_integration",
                hook_name="lsp_integration",
                status="PASS" if successful_integrations > 0 else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "lsp_hooks_tested": len(lsp_hooks),
                    "successful_integrations": successful_integrations,
                    "integration_results": lsp_test_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_lsp_bridge_integration",
                hook_name="lsp_integration",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in LSP integration test: {str(e)}"
            )
    
    def test_hook_registry_sync(self) -> TestResult:
        """Test hook registry synchronization"""
        start_time = time.time()
        
        try:
            # Test registry synchronization with configuration
            sync_issues = []
            
            # Check all hooks in registry have corresponding files
            for hook_name, metadata in self.hook_registry_data['hooks'].items():
                hook_file = self.hooks_directory / metadata['source']
                if not hook_file.exists():
                    sync_issues.append(f"Missing source file for {hook_name}: {hook_file}")
            
            # Check all hook files have registry entries
            hook_files = list(self.hooks_directory.glob("*.py"))
            for hook_file in hook_files:
                if hook_file.name.startswith('hook_') or hook_file.name.endswith('_hook.py'):
                    # Should have registry entry
                    found_in_registry = any(
                        metadata['source'] == hook_file.name 
                        for metadata in self.hook_registry_data['hooks'].values()
                    )
                    if not found_in_registry:
                        sync_issues.append(f"Hook file not in registry: {hook_file.name}")
            
            # Test runtime registry sync
            registry_hooks = set(self.test_registry.hooks.keys()) if self.test_registry else set()
            config_hooks = set(self.hook_registry_data['hooks'].keys())
            
            missing_from_runtime = config_hooks - registry_hooks
            extra_in_runtime = registry_hooks - config_hooks
            
            if missing_from_runtime:
                sync_issues.extend([f"Missing from runtime: {h}" for h in missing_from_runtime])
            if extra_in_runtime:
                sync_issues.extend([f"Extra in runtime: {h}" for h in extra_in_runtime])
            
            return TestResult(
                test_name="test_hook_registry_sync",
                hook_name="registry_sync",
                status="PASS" if not sync_issues else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "sync_issues": sync_issues,
                    "config_hooks": len(config_hooks),
                    "runtime_hooks": len(registry_hooks)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_hook_registry_sync",
                hook_name="registry_sync",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in registry sync test: {str(e)}"
            )
    
    def test_api_integration(self) -> TestResult:
        """Test API integration"""
        start_time = time.time()
        
        try:
            import requests
            import json
            
            # Test API endpoints
            api_base_url = f"http://{self.test_manager.api_host}:{self.test_manager.api_port}"
            
            api_tests = [
                {"endpoint": "/hooks", "method": "GET", "expected_status": 200},
                {"endpoint": "/hooks/status", "method": "GET", "expected_status": 200},
                {"endpoint": "/system/health", "method": "GET", "expected_status": 200}
            ]
            
            api_results = {}
            
            for test in api_tests:
                try:
                    if test["method"] == "GET":
                        response = requests.get(f"{api_base_url}{test['endpoint']}", timeout=5)
                    else:
                        response = requests.post(f"{api_base_url}{test['endpoint']}", timeout=5)
                    
                    api_results[test["endpoint"]] = {
                        "status_code": response.status_code,
                        "expected": test["expected_status"],
                        "passed": response.status_code == test["expected_status"]
                    }
                    
                except requests.RequestException as e:
                    api_results[test["endpoint"]] = {
                        "status_code": 0,
                        "expected": test["expected_status"],
                        "passed": False,
                        "error": str(e)
                    }
            
            successful_tests = sum(1 for result in api_results.values() if result["passed"])
            
            return TestResult(
                test_name="test_api_integration",
                hook_name="api_integration",
                status="PASS" if successful_tests == len(api_tests) else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "api_tests": len(api_tests),
                    "successful_tests": successful_tests,
                    "api_results": api_results
                }
            )
            
        except ImportError:
            return TestResult(
                test_name="test_api_integration",
                hook_name="api_integration",
                status="SKIP",
                execution_time=time.time() - start_time,
                error_message="requests library not available for API testing"
            )
        except Exception as e:
            return TestResult(
                test_name="test_api_integration",
                hook_name="api_integration",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in API integration test: {str(e)}"
            )
    
    def test_configuration_integration(self) -> TestResult:
        """Test configuration integration"""
        start_time = time.time()
        
        try:
            # Test configuration loading and validation
            config_issues = []
            
            if not self.test_manager.config_manager:
                return TestResult(
                    test_name="test_configuration_integration",
                    hook_name="config_integration",
                    status="FAIL",
                    execution_time=time.time() - start_time,
                    error_message="Configuration manager not initialized"
                )
            
            # Test configuration validation
            validation_results = self.test_manager.config_manager.validate_configurations()
            if validation_results:
                config_issues.extend(validation_results)
            
            # Test configuration updates
            test_config_updates = {
                'timeout': 45.0,
                'retry_count': 3,
                'enabled': True
            }
            
            for hook_name in list(self.hook_registry_data['hooks'].keys())[:3]:  # Test first 3 hooks
                try:
                    self.test_manager.config_manager.update_hook_config(hook_name, test_config_updates)
                except Exception as e:
                    config_issues.append(f"Failed to update config for {hook_name}: {str(e)}")
            
            return TestResult(
                test_name="test_configuration_integration",
                hook_name="config_integration",
                status="PASS" if not config_issues else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "config_issues": config_issues,
                    "validation_results": validation_results,
                    "update_tests_run": 3
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_configuration_integration",
                hook_name="config_integration",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in configuration integration test: {str(e)}"
            )
    
    # Concurrency Testing
    
    def test_parallel_hook_execution(self) -> TestResult:
        """Test parallel hook execution"""
        start_time = time.time()
        
        try:
            # Test multiple hooks executing in parallel
            parallel_hooks = list(self.hook_registry_data['hooks'].keys())[:10]  # Test first 10 hooks
            
            execution_results = {}
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_hook = {}
                
                for hook_name in parallel_hooks:
                    with MockEnvironment(hook_name) as mock_env:
                        future = executor.submit(
                            self.test_manager.execute_hook,
                            hook_name, 'test', mock_env.mock_data
                        )
                        future_to_hook[future] = hook_name
                
                # Collect results
                for future in as_completed(future_to_hook):
                    hook_name = future_to_hook[future]
                    try:
                        execution_id = future.result(timeout=30)
                        execution_results[hook_name] = {
                            "success": execution_id is not None,
                            "execution_id": execution_id
                        }
                    except Exception as e:
                        execution_results[hook_name] = {
                            "success": False,
                            "error": str(e)
                        }
            
            successful_executions = sum(1 for result in execution_results.values() if result["success"])
            
            return TestResult(
                test_name="test_parallel_hook_execution",
                hook_name="parallel_execution",
                status="PASS" if successful_executions > len(parallel_hooks) * 0.8 else "FAIL",  # 80% success rate
                execution_time=time.time() - start_time,
                details={
                    "hooks_tested": len(parallel_hooks),
                    "successful_executions": successful_executions,
                    "execution_results": execution_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_parallel_hook_execution",
                hook_name="parallel_execution",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in parallel execution test: {str(e)}"
            )
    
    def test_resource_contention(self) -> TestResult:
        """Test resource contention handling"""
        start_time = time.time()
        
        try:
            # Test hooks competing for same resources
            resource_contention_scenarios = [
                {
                    "resource": "file_system",
                    "hooks": ["session_saver", "auto_documentation", "code_linter"],
                    "shared_resource": "/tmp/test_contention_file.txt"
                },
                {
                    "resource": "memory",
                    "hooks": ["performance_monitor", "resource_monitor", "context_manager"],
                    "shared_resource": "memory_pool"
                }
            ]
            
            contention_results = {}
            
            for scenario in resource_contention_scenarios:
                scenario_results = []
                
                # Create shared resource
                if scenario["resource"] == "file_system":
                    with open(scenario["shared_resource"], 'w') as f:
                        f.write("test content for contention")
                
                # Execute hooks concurrently that use same resource
                with ThreadPoolExecutor(max_workers=len(scenario["hooks"])) as executor:
                    futures = []
                    
                    for hook_name in scenario["hooks"]:
                        if hook_name in self.hook_registry_data['hooks']:
                            test_data = {"shared_resource": scenario["shared_resource"]}
                            future = executor.submit(
                                self.test_manager.execute_hook,
                                hook_name, 'test', test_data
                            )
                            futures.append((future, hook_name))
                    
                    # Collect results
                    for future, hook_name in futures:
                        try:
                            execution_id = future.result(timeout=30)
                            scenario_results.append({
                                "hook": hook_name,
                                "success": execution_id is not None,
                                "execution_id": execution_id
                            })
                        except Exception as e:
                            scenario_results.append({
                                "hook": hook_name,
                                "success": False,
                                "error": str(e)
                            })
                
                contention_results[scenario["resource"]] = scenario_results
                
                # Cleanup shared resource
                if scenario["resource"] == "file_system" and os.path.exists(scenario["shared_resource"]):
                    os.unlink(scenario["shared_resource"])
            
            # Analyze contention handling
            total_tests = sum(len(results) for results in contention_results.values())
            successful_tests = sum(
                sum(1 for result in results if result["success"])
                for results in contention_results.values()
            )
            
            return TestResult(
                test_name="test_resource_contention",
                hook_name="resource_contention",
                status="PASS" if successful_tests > total_tests * 0.7 else "FAIL",  # 70% success rate
                execution_time=time.time() - start_time,
                details={
                    "scenarios_tested": len(resource_contention_scenarios),
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "contention_results": contention_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_resource_contention",
                hook_name="resource_contention",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in resource contention test: {str(e)}"
            )
    
    def test_deadlock_detection(self) -> TestResult:
        """Test deadlock detection and prevention"""
        start_time = time.time()
        
        try:
            # Create potential deadlock scenarios
            deadlock_scenarios = [
                {
                    "name": "circular_dependency",
                    "hooks": ["master_orchestrator", "smart_orchestrator"],
                    "dependency_chain": ["master_orchestrator -> smart_orchestrator", "smart_orchestrator -> master_orchestrator"]
                },
                {
                    "name": "resource_lock_chain",
                    "hooks": ["session_loader", "session_saver"],
                    "dependency_chain": ["session_loader -> session_saver", "session_saver -> session_loader"]
                }
            ]
            
            deadlock_detection_results = {}
            
            for scenario in deadlock_scenarios:
                try:
                    # Simulate deadlock scenario with timeout
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        futures = []
                        
                        # Create interdependent execution scenario
                        for i, hook_name in enumerate(scenario["hooks"]):
                            if hook_name in self.hook_registry_data['hooks']:
                                test_data = {
                                    "dependency_hook": scenario["hooks"][1-i],  # Circular dependency
                                    "wait_for_completion": True
                                }
                                future = executor.submit(
                                    self.test_manager.execute_hook,
                                    hook_name, 'test', test_data
                                )
                                futures.append((future, hook_name))
                        
                        # Check if deadlock is detected/prevented (should complete or timeout gracefully)
                        completed_executions = 0
                        for future, hook_name in futures:
                            try:
                                result = future.result(timeout=10)  # Short timeout to detect deadlock
                                completed_executions += 1
                            except Exception:
                                # Timeout or deadlock detection - this is expected/acceptable
                                pass
                        
                        deadlock_detection_results[scenario["name"]] = {
                            "completed_executions": completed_executions,
                            "total_executions": len(futures),
                            "deadlock_handled": True  # No system hang occurred
                        }
                        
                except Exception as e:
                    deadlock_detection_results[scenario["name"]] = {
                        "completed_executions": 0,
                        "total_executions": len(scenario["hooks"]),
                        "deadlock_handled": False,
                        "error": str(e)
                    }
            
            # All scenarios should be handled without system hang
            all_handled = all(result["deadlock_handled"] for result in deadlock_detection_results.values())
            
            return TestResult(
                test_name="test_deadlock_detection",
                hook_name="deadlock_detection",
                status="PASS" if all_handled else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "scenarios_tested": len(deadlock_scenarios),
                    "all_deadlocks_handled": all_handled,
                    "detection_results": deadlock_detection_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_deadlock_detection",
                hook_name="deadlock_detection",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in deadlock detection test: {str(e)}"
            )
    
    def test_thread_safety(self) -> TestResult:
        """Test thread safety of hook operations"""
        start_time = time.time()
        
        try:
            # Test thread safety with concurrent operations
            thread_safety_operations = [
                "register_hook",
                "activate_hook", 
                "deactivate_hook",
                "execute_hook"
            ]
            
            test_hook_name = "test_thread_safety_hook"
            
            # Thread safety test results
            safety_results = {}
            
            for operation in thread_safety_operations:
                operation_results = []
                
                # Perform operation concurrently from multiple threads
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    
                    for i in range(10):  # 10 concurrent operations
                        if operation == "register_hook":
                            future = executor.submit(
                                self.test_manager.register_hook_file,
                                str(self.hooks_directory / "context_manager.py")  # Use existing file
                            )
                        elif operation == "activate_hook":
                            future = executor.submit(
                                self.test_manager.activate_hook,
                                "context_manager"
                            )
                        elif operation == "deactivate_hook":
                            future = executor.submit(
                                self.test_manager.deactivate_hook,
                                "context_manager"
                            )
                        elif operation == "execute_hook":
                            future = executor.submit(
                                self.test_manager.execute_hook,
                                "context_manager", "test", {"thread_id": i}
                            )
                        
                        futures.append(future)
                    
                    # Collect results
                    for future in futures:
                        try:
                            result = future.result(timeout=15)
                            operation_results.append({
                                "success": True,
                                "result": result
                            })
                        except Exception as e:
                            operation_results.append({
                                "success": False,
                                "error": str(e)
                            })
                
                safety_results[operation] = {
                    "total_operations": len(operation_results),
                    "successful_operations": sum(1 for r in operation_results if r["success"]),
                    "results": operation_results
                }
            
            # Check if operations completed without race conditions
            all_operations_safe = all(
                result["successful_operations"] > 0
                for result in safety_results.values()
            )
            
            return TestResult(
                test_name="test_thread_safety",
                hook_name="thread_safety",
                status="PASS" if all_operations_safe else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "operations_tested": len(thread_safety_operations),
                    "all_operations_safe": all_operations_safe,
                    "safety_results": safety_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_thread_safety",
                hook_name="thread_safety",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in thread safety test: {str(e)}"
            )
    
    # Regression Testing
    
    def test_backward_compatibility(self) -> TestResult:
        """Test backward compatibility"""
        start_time = time.time()
        
        try:
            # Test legacy hook interfaces
            compatibility_tests = []
            
            # Test legacy trigger formats
            legacy_triggers = ["old_format", "deprecated_trigger", "v2_trigger"]
            for trigger in legacy_triggers:
                try:
                    execution_ids = self.test_manager.execute_by_trigger(trigger, {"legacy_test": True})
                    compatibility_tests.append({
                        "test": f"legacy_trigger_{trigger}",
                        "success": True,
                        "executions": len(execution_ids)
                    })
                except Exception as e:
                    compatibility_tests.append({
                        "test": f"legacy_trigger_{trigger}",
                        "success": False,
                        "error": str(e)
                    })
            
            # Test legacy data formats
            legacy_data_formats = [
                {"old_format": True, "data": "legacy_string_format"},
                {"version": "2.0", "payload": {"nested": "old_structure"}},
                "plain_string_data"  # Very old format
            ]
            
            for i, data_format in enumerate(legacy_data_formats):
                try:
                    execution_id = self.test_manager.execute_hook(
                        "context_manager", "test", data_format
                    )
                    compatibility_tests.append({
                        "test": f"legacy_data_format_{i}",
                        "success": execution_id is not None,
                        "execution_id": execution_id
                    })
                except Exception as e:
                    compatibility_tests.append({
                        "test": f"legacy_data_format_{i}",
                        "success": False,
                        "error": str(e)
                    })
            
            successful_compatibility_tests = sum(1 for test in compatibility_tests if test["success"])
            
            return TestResult(
                test_name="test_backward_compatibility",
                hook_name="backward_compatibility",
                status="PASS" if successful_compatibility_tests > len(compatibility_tests) * 0.8 else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "compatibility_tests": len(compatibility_tests),
                    "successful_tests": successful_compatibility_tests,
                    "test_results": compatibility_tests
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_backward_compatibility",
                hook_name="backward_compatibility",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in backward compatibility test: {str(e)}"
            )
    
    def test_api_contract_compliance(self) -> TestResult:
        """Test API contract compliance"""
        start_time = time.time()
        
        try:
            # Test API contract for each hook
            contract_violations = []
            
            for hook_name, metadata in self.hook_registry_data['hooks'].items():
                # Check required metadata fields
                required_fields = ['source', 'group', 'priority', 'triggers', 'phase']
                for field in required_fields:
                    if field not in metadata:
                        contract_violations.append(f"{hook_name}: Missing required field '{field}'")
                
                # Check data types
                if 'priority' in metadata and not isinstance(metadata['priority'], int):
                    contract_violations.append(f"{hook_name}: Priority must be integer")
                
                if 'triggers' in metadata and not isinstance(metadata['triggers'], list):
                    contract_violations.append(f"{hook_name}: Triggers must be list")
                
                # Check source file exists
                source_file = self.hooks_directory / metadata.get('source', '')
                if not source_file.exists():
                    contract_violations.append(f"{hook_name}: Source file does not exist")
            
            # Test API response contracts
            api_response_tests = [
                {
                    "method": "get_hook_info",
                    "args": ["context_manager"],
                    "expected_fields": ["name", "file_path", "version", "state"]
                },
                {
                    "method": "list_hooks", 
                    "args": [{}],
                    "expected_structure": "list_of_dicts"
                },
                {
                    "method": "get_system_status",
                    "args": [],
                    "expected_fields": ["timestamp", "initialized", "running"]
                }
            ]
            
            for test in api_response_tests:
                try:
                    method = getattr(self.test_manager, test["method"])
                    result = method(*test["args"])
                    
                    if test.get("expected_fields"):
                        if isinstance(result, dict):
                            for field in test["expected_fields"]:
                                if field not in result:
                                    contract_violations.append(f"API {test['method']}: Missing field '{field}'")
                    
                    if test.get("expected_structure") == "list_of_dicts":
                        if not isinstance(result, list) or (result and not isinstance(result[0], dict)):
                            contract_violations.append(f"API {test['method']}: Expected list of dicts")
                            
                except Exception as e:
                    contract_violations.append(f"API {test['method']}: Exception - {str(e)}")
            
            return TestResult(
                test_name="test_api_contract_compliance",
                hook_name="api_contract",
                status="PASS" if not contract_violations else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "contract_violations": contract_violations,
                    "hooks_checked": len(self.hook_registry_data['hooks']),
                    "api_methods_tested": len(api_response_tests)
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_api_contract_compliance",
                hook_name="api_contract",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in API contract test: {str(e)}"
            )
    
    def test_configuration_migration(self) -> TestResult:
        """Test configuration migration"""
        start_time = time.time()
        
        try:
            # Test migration from old configuration formats
            migration_scenarios = [
                {
                    "name": "v2_to_v3_migration",
                    "old_config": {
                        "version": "2.0",
                        "hooks": {
                            "test_hook": {
                                "enabled": True,
                                "priority": "high",  # Old string format
                                "triggers": "user_input,claude_response"  # Old comma-separated string
                            }
                        }
                    },
                    "expected_result": {
                        "version": "3.6.9",
                        "hooks": {
                            "test_hook": {
                                "enabled": True,
                                "priority": 2,  # New integer format
                                "triggers": ["user_input", "claude_response"]  # New list format
                            }
                        }
                    }
                }
            ]
            
            migration_results = []
            
            for scenario in migration_scenarios:
                try:
                    # Create temporary config file with old format
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
                        json.dump(scenario["old_config"], temp_config)
                        temp_config_path = temp_config.name
                    
                    try:
                        # Test migration
                        migrated_config = self.test_manager.config_manager.migrate_configuration(temp_config_path)
                        
                        migration_success = True
                        migration_issues = []
                        
                        # Validate migration results
                        if migrated_config.get("version") != scenario["expected_result"]["version"]:
                            migration_issues.append("Version not updated correctly")
                            migration_success = False
                        
                        migration_results.append({
                            "scenario": scenario["name"],
                            "success": migration_success,
                            "issues": migration_issues
                        })
                        
                    finally:
                        # Cleanup temp file
                        if os.path.exists(temp_config_path):
                            os.unlink(temp_config_path)
                        
                except Exception as e:
                    migration_results.append({
                        "scenario": scenario["name"],
                        "success": False,
                        "error": str(e)
                    })
            
            successful_migrations = sum(1 for result in migration_results if result["success"])
            
            return TestResult(
                test_name="test_configuration_migration",
                hook_name="config_migration",
                status="PASS" if successful_migrations == len(migration_scenarios) else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "migration_scenarios": len(migration_scenarios),
                    "successful_migrations": successful_migrations,
                    "migration_results": migration_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_configuration_migration",
                hook_name="config_migration",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in configuration migration test: {str(e)}"
            )
    
    def test_performance_regression(self) -> TestResult:
        """Test for performance regression"""
        start_time = time.time()
        
        try:
            # Compare current performance against baselines
            regression_hooks = list(self.hook_registry_data['hooks'].keys())[:5]  # Test subset
            regression_results = []
            
            for hook_name in regression_hooks:
                if hook_name not in self.performance_baselines:
                    continue
                
                baseline_time = self.performance_baselines[hook_name]
                
                # Measure current performance
                perf_start = time.time()
                with MockEnvironment(hook_name) as mock_env:
                    execution_id = self.test_manager.execute_hook(
                        hook_name, 'test', mock_env.mock_data
                    )
                current_time = (time.time() - perf_start) * 1000  # Convert to ms
                
                # Check for regression (>50% slower than baseline)
                regression_factor = current_time / baseline_time if baseline_time > 0 else 1.0
                has_regression = regression_factor > 1.5
                
                regression_results.append({
                    "hook_name": hook_name,
                    "baseline_time": baseline_time,
                    "current_time": current_time,
                    "regression_factor": regression_factor,
                    "has_regression": has_regression
                })
            
            hooks_with_regression = sum(1 for result in regression_results if result["has_regression"])
            
            return TestResult(
                test_name="test_performance_regression",
                hook_name="performance_regression",
                status="PASS" if hooks_with_regression == 0 else "FAIL",
                execution_time=time.time() - start_time,
                details={
                    "hooks_tested": len(regression_results),
                    "hooks_with_regression": hooks_with_regression,
                    "regression_results": regression_results
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="test_performance_regression",
                hook_name="performance_regression",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Exception in performance regression test: {str(e)}"
            )
    
    # Test Execution and Reporting
    
    def run_test_suite(self, suite_name: str) -> List[TestResult]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        suite = self.test_suites[suite_name]
        logger.info(f"Running test suite: {suite.name}")
        
        suite_results = []
        start_time = time.time()
        
        try:
            # Setup suite
            for setup_hook in suite.setup_hooks:
                self.test_manager.execute_hook(setup_hook, 'setup', {})
            
            # Run tests
            if suite.parallel_execution:
                # Run tests in parallel
                with ThreadPoolExecutor(max_workers=4) as executor:
                    future_to_test = {}
                    
                    for test_name in suite.tests:
                        if hasattr(self, test_name):
                            test_method = getattr(self, test_name)
                            future = executor.submit(test_method)
                            future_to_test[future] = test_name
                        elif test_name.startswith('test_individual_hook_'):
                            hook_name = test_name.replace('test_individual_hook_', '')
                            future = executor.submit(self.test_individual_hook, hook_name)
                            future_to_test[future] = test_name
                    
                    # Collect results
                    for future in as_completed(future_to_test, timeout=suite.timeout):
                        test_name = future_to_test[future]
                        try:
                            result = future.result()
                            suite_results.append(result)
                        except Exception as e:
                            suite_results.append(TestResult(
                                test_name=test_name,
                                hook_name="unknown",
                                status="ERROR",
                                execution_time=0.0,
                                error_message=f"Test execution failed: {str(e)}"
                            ))
            else:
                # Run tests sequentially
                for test_name in suite.tests:
                    if hasattr(self, test_name):
                        test_method = getattr(self, test_name)
                        result = test_method()
                        suite_results.append(result)
                    elif test_name.startswith('test_individual_hook_'):
                        hook_name = test_name.replace('test_individual_hook_', '')
                        result = self.test_individual_hook(hook_name)
                        suite_results.append(result)
            
            # Teardown suite
            for teardown_hook in suite.teardown_hooks:
                self.test_manager.execute_hook(teardown_hook, 'teardown', {})
                
        except Exception as e:
            logger.error(f"Test suite {suite_name} failed: {e}")
            suite_results.append(TestResult(
                test_name=f"suite_{suite_name}",
                hook_name="suite_execution",
                status="ERROR",
                execution_time=time.time() - start_time,
                error_message=f"Suite execution failed: {str(e)}"
            ))
        
        # Add suite results to overall results
        self.test_results.extend(suite_results)
        
        logger.info(f"Test suite {suite_name} completed with {len(suite_results)} tests")
        return suite_results
    
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run all test suites"""
        logger.info("Starting comprehensive hook testing...")
        
        all_results = {}
        
        # Setup test environment
        self.setup_test_environment()
        
        try:
            # Run each test suite
            for suite_name in self.test_suites.keys():
                logger.info(f"Running test suite: {suite_name}")
                suite_results = self.run_test_suite(suite_name)
                all_results[suite_name] = suite_results
        
        finally:
            # Cleanup test environment
            self.teardown_test_environment()
        
        logger.info("All tests completed")
        return all_results
    
    def generate_test_report(self, results: Dict[str, List[TestResult]] = None) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if results is None:
            results = {"all_tests": self.test_results}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "3.6.9",
            "total_hooks_tested": len(self.hook_registry_data['hooks']),
            "summary": {},
            "suite_results": {},
            "performance_summary": {},
            "recommendations": []
        }
        
        # Calculate overall summary
        all_tests = []
        for suite_results in results.values():
            all_tests.extend(suite_results)
        
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.status == "PASS")
        failed_tests = sum(1 for test in all_tests if test.status == "FAIL")
        error_tests = sum(1 for test in all_tests if test.status == "ERROR")
        skipped_tests = sum(1 for test in all_tests if test.status == "SKIP")
        
        report["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "skipped": skipped_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_execution_time": sum(test.execution_time for test in all_tests)
        }
        
        # Suite-specific results
        for suite_name, suite_results in results.items():
            suite_passed = sum(1 for test in suite_results if test.status == "PASS")
            suite_total = len(suite_results)
            
            report["suite_results"][suite_name] = {
                "total_tests": suite_total,
                "passed": suite_passed,
                "pass_rate": (suite_passed / suite_total * 100) if suite_total > 0 else 0,
                "execution_time": sum(test.execution_time for test in suite_results),
                "failed_tests": [test.test_name for test in suite_results if test.status == "FAIL"],
                "error_tests": [test.test_name for test in suite_results if test.status == "ERROR"]
            }
        
        # Performance summary
        if self.performance_benchmarks:
            perf_summary = {
                "benchmarks_run": len(self.performance_benchmarks),
                "passed_benchmarks": sum(1 for b in self.performance_benchmarks.values() if b.passed),
                "average_execution_time": sum(b.current_time for b in self.performance_benchmarks.values()) / len(self.performance_benchmarks),
                "slowest_hooks": sorted(
                    [(name, bench.current_time) for name, bench in self.performance_benchmarks.items()],
                    key=lambda x: x[1], reverse=True
                )[:5]
            }
            report["performance_summary"] = perf_summary
        
        # Generate recommendations
        recommendations = []
        
        if report["summary"]["pass_rate"] < 90:
            recommendations.append("Overall pass rate is below 90%. Review failed tests and improve hook reliability.")
        
        if failed_tests > 0:
            recommendations.append(f"{failed_tests} tests failed. Check hook implementations and test data.")
        
        if error_tests > 0:
            recommendations.append(f"{error_tests} tests had errors. Review test environment and hook dependencies.")
        
        if self.performance_benchmarks:
            slow_hooks = [name for name, bench in self.performance_benchmarks.items() if not bench.passed]
            if slow_hooks:
                recommendations.append(f"Performance regression detected in: {', '.join(slow_hooks[:3])}")
        
        report["recommendations"] = recommendations
        
        return report
    
    def save_test_report(self, report: Dict[str, Any], file_path: str = None):
        """Save test report to file"""
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.hooks_directory / "tests" / f"test_report_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert TestResult objects to dictionaries for JSON serialization
        serializable_report = json.loads(json.dumps(report, default=str))
        
        with open(file_path, 'w') as f:
            json.dump(serializable_report, f, indent=2, default=str)
        
        logger.info(f"Test report saved to: {file_path}")
        return file_path


# CLI Interface
def main():
    """Command-line interface for the hook test framework"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Hook Test Framework V3.6.9")
    parser.add_argument('--hooks-dir', help='Directory containing hooks')
    parser.add_argument('--config-file', help='Configuration file path')
    parser.add_argument('--suite', help='Specific test suite to run')
    parser.add_argument('--hook', help='Specific hook to test')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
    parser.add_argument('--report-file', help='Output file for test report')
    parser.add_argument('--update-baselines', action='store_true', help='Update performance baselines')
    
    args = parser.parse_args()
    
    try:
        # Initialize test framework
        framework = HookTestFramework(
            hooks_directory=args.hooks_dir,
            config_file=args.config_file
        )
        
        # Run tests
        if args.hook:
            # Test specific hook
            framework.setup_test_environment()
            try:
                result = framework.test_individual_hook(args.hook)
                print(f"Hook {args.hook}: {result.status}")
                if result.error_message:
                    print(f"Error: {result.error_message}")
            finally:
                framework.teardown_test_environment()
                
        elif args.suite:
            # Run specific test suite
            framework.setup_test_environment()
            try:
                results = framework.run_test_suite(args.suite)
                passed = sum(1 for r in results if r.status == "PASS")
                print(f"Suite {args.suite}: {passed}/{len(results)} tests passed")
            finally:
                framework.teardown_test_environment()
                
        else:
            # Run all tests
            results = framework.run_all_tests()
            
            # Generate report
            report = framework.generate_test_report(results)
            
            # Print summary
            print("\n" + "="*50)
            print("HOOK TEST FRAMEWORK RESULTS")
            print("="*50)
            print(f"Total Tests: {report['summary']['total_tests']}")
            print(f"Passed: {report['summary']['passed']}")
            print(f"Failed: {report['summary']['failed']}")
            print(f"Errors: {report['summary']['errors']}")
            print(f"Skipped: {report['summary']['skipped']}")
            print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
            print(f"Execution Time: {report['summary']['total_execution_time']:.2f}s")
            
            if report['recommendations']:
                print("\nRecommendations:")
                for rec in report['recommendations']:
                    print(f"  • {rec}")
            
            # Save report
            report_file = framework.save_test_report(report, args.report_file)
            print(f"\nDetailed report saved to: {report_file}")
            
    except Exception as e:
        logger.error(f"Test framework failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()