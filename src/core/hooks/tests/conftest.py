#!/usr/bin/env python3
"""
pytest configuration and fixtures for hook testing
Provides comprehensive test fixtures and utilities for pytest integration
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Generator
from unittest.mock import Mock, patch

# Add the hooks directory to the path
hooks_dir = Path(__file__).parent.parent
sys.path.insert(0, str(hooks_dir))

from test_framework import HookTestFramework, TestResult
from test_utilities import (
    TestDataGenerator, TestEnvironmentManager, PerformanceProfiler,
    create_comprehensive_test_data
)
from hook_manager import HookManager


@pytest.fixture(scope="session")
def hooks_directory():
    """Fixture providing the hooks directory path"""
    return str(Path(__file__).parent.parent)


@pytest.fixture(scope="session")
def hook_registry_data(hooks_directory):
    """Fixture providing hook registry data"""
    registry_file = Path(hooks_directory) / "hook-registry.json"
    if registry_file.exists():
        with open(registry_file, 'r') as f:
            return json.load(f)
    else:
        # Return mock registry data for testing
        return {
            "version": "3.6.9",
            "total_hooks": 2,
            "hooks": {
                "test_hook_1": {
                    "source": "test_hook_1.py",
                    "group": "testing",
                    "priority": 1,
                    "triggers": ["test"],
                    "phase": "testing"
                },
                "test_hook_2": {
                    "source": "test_hook_2.py", 
                    "group": "testing",
                    "priority": 2,
                    "triggers": ["test"],
                    "phase": "testing"
                }
            },
            "groups": {
                "testing": ["test_hook_1", "test_hook_2"]
            }
        }


@pytest.fixture(scope="session")
def test_framework(hooks_directory):
    """Fixture providing initialized test framework"""
    framework = HookTestFramework(hooks_directory=hooks_directory)
    yield framework
    # Cleanup after all tests
    if hasattr(framework, 'test_manager') and framework.test_manager:
        framework.teardown_test_environment()


@pytest.fixture(scope="function")
def isolated_test_environment():
    """Fixture providing isolated test environment for each test"""
    env_manager = TestEnvironmentManager("pytest_test")
    env_manager.setup()
    yield env_manager
    env_manager.cleanup()


@pytest.fixture(scope="function")
def mock_hook_manager():
    """Fixture providing mock hook manager"""
    manager = Mock(spec=HookManager)
    manager.hooks_directory = Path(__file__).parent.parent
    manager.initialized = True
    manager.running = True
    manager.registry = Mock()
    manager.config_manager = Mock()
    
    # Mock registry data
    manager.registry.hooks = {}
    manager.registry.active_executions = {}
    manager.registry.execution_queue = Mock()
    manager.registry.execution_queue.qsize.return_value = 0
    
    # Mock common methods
    manager.register_hook_file.return_value = True
    manager.activate_hook.return_value = True
    manager.deactivate_hook.return_value = True
    manager.execute_hook.return_value = "test_execution_id_123"
    manager.execute_by_trigger.return_value = ["test_execution_id_123"]
    
    return manager


@pytest.fixture(scope="function")
def test_data_generator():
    """Fixture providing test data generator"""
    return TestDataGenerator()


@pytest.fixture(scope="function")
def performance_profiler():
    """Fixture providing performance profiler"""
    profiler = PerformanceProfiler("test_hook")
    yield profiler


@pytest.fixture(scope="function", params=[
    "user_prompt", "claude_response", "agent_activation", 
    "file_change", "mcp_request", "system_event"
])
def test_scenario_data(request, test_data_generator):
    """Fixture providing different test scenario data"""
    scenario_generators = {
        "user_prompt": test_data_generator.generate_user_prompt_data,
        "claude_response": test_data_generator.generate_claude_response_data,
        "agent_activation": test_data_generator.generate_agent_activation_data,
        "file_change": test_data_generator.generate_file_change_data,
        "mcp_request": test_data_generator.generate_mcp_request_data,
        "system_event": test_data_generator.generate_system_event_data
    }
    
    generator = scenario_generators.get(request.param, test_data_generator.generate_user_prompt_data)
    return generator()


@pytest.fixture(scope="function")
def temp_hook_file(isolated_test_environment):
    """Fixture providing temporary hook file for testing"""
    hook_content = '''#!/usr/bin/env python3
"""
Test Hook for Testing Framework
"""

def execute(trigger, data, context=None):
    """Test hook execution function"""
    return {
        "status": "success",
        "message": "Test hook executed successfully",
        "data": data,
        "trigger": trigger
    }

# Hook metadata
__hook_metadata__ = {
    "name": "test_hook",
    "version": "1.0.0",
    "description": "Test hook for testing framework",
    "author": "Test Framework",
    "triggers": ["test", "pytest"],
    "dependencies": [],
    "provides": ["test_functionality"],
    "tags": ["testing", "pytest"]
}
'''
    
    hook_file = isolated_test_environment.create_test_file("test_hook.py", hook_content)
    return hook_file


@pytest.fixture(scope="function")
def mock_registry_data():
    """Fixture providing mock registry data for testing"""
    return {
        "version": "3.6.9",
        "total_hooks": 3,
        "hooks": {
            "mock_hook_1": {
                "source": "mock_hook_1.py",
                "group": "testing",
                "priority": 1,
                "triggers": ["test", "mock"],
                "phase": "testing"
            },
            "mock_hook_2": {
                "source": "mock_hook_2.py",
                "group": "testing",
                "priority": 2,
                "triggers": ["test"],
                "phase": "testing"
            },
            "mock_hook_3": {
                "source": "mock_hook_3.py",
                "group": "performance",
                "priority": 1,
                "triggers": ["performance"],
                "phase": "testing"
            }
        },
        "groups": {
            "testing": ["mock_hook_1", "mock_hook_2"],
            "performance": ["mock_hook_3"]
        }
    }


@pytest.fixture(scope="function")
def mock_performance_baselines():
    """Fixture providing mock performance baselines"""
    return {
        "mock_hook_1": 500.0,  # 500ms baseline
        "mock_hook_2": 750.0,  # 750ms baseline
        "mock_hook_3": 1000.0  # 1s baseline
    }


@pytest.fixture(scope="function")
def sample_test_results():
    """Fixture providing sample test results for testing"""
    return [
        TestResult(
            test_name="test_mock_hook_1",
            hook_name="mock_hook_1",
            status="PASS",
            execution_time=0.456,
            details={"trigger": "test"}
        ),
        TestResult(
            test_name="test_mock_hook_2",
            hook_name="mock_hook_2",
            status="FAIL",
            execution_time=1.234,
            error_message="Mock failure for testing"
        ),
        TestResult(
            test_name="test_mock_hook_3",
            hook_name="mock_hook_3",
            status="ERROR",
            execution_time=0.789,
            error_message="Mock error for testing"
        ),
        TestResult(
            test_name="test_mock_hook_4",
            hook_name="mock_hook_4",
            status="SKIP",
            execution_time=0.001,
            error_message="Mock skip for testing"
        )
    ]


@pytest.fixture(scope="function")
def comprehensive_test_data():
    """Fixture providing comprehensive test data for all hook types"""
    return {
        "orchestration_hook": create_comprehensive_test_data("smart_orchestrator", "normal"),
        "routing_hook": create_comprehensive_test_data("agent_mention_parser", "normal"),
        "feedback_hook": create_comprehensive_test_data("audio_player_v3", "normal"),
        "quality_hook": create_comprehensive_test_data("code_linter", "normal"),
        "monitoring_hook": create_comprehensive_test_data("performance_monitor", "normal"),
        "error_scenario": create_comprehensive_test_data("test_hook", "error"),
        "performance_scenario": create_comprehensive_test_data("test_hook", "performance"),
        "concurrency_scenario": create_comprehensive_test_data("test_hook", "concurrency")
    }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.concurrency = pytest.mark.concurrency
pytest.mark.regression = pytest.mark.regression
pytest.mark.smoke = pytest.mark.smoke


# Custom pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and organize tests"""
    
    # Add markers based on test names and file paths
    for item in items:
        # Add unit test marker
        if "unit" in item.nodeid or "test_individual" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            
        # Add integration test marker
        if "integration" in item.nodeid or "test_chain" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            
        # Add performance test marker
        if "performance" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.performance)
            
        # Add concurrency test marker
        if "concurrency" in item.nodeid or "parallel" in item.nodeid:
            item.add_marker(pytest.mark.concurrency)
            
        # Add regression test marker
        if "regression" in item.nodeid or "backward_compatibility" in item.nodeid:
            item.add_marker(pytest.mark.regression)
            
        # Add smoke test marker for critical tests
        if any(keyword in item.nodeid for keyword in ["smoke", "critical", "basic"]):
            item.add_marker(pytest.mark.smoke)


def pytest_configure(config):
    """Configure pytest with custom settings"""
    
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "concurrency: mark test as concurrency test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    
    # Set up test environment variables
    os.environ["PYTEST_RUNNING"] = "1"
    os.environ["TEST_ENVIRONMENT"] = "pytest"


def pytest_unconfigure(config):
    """Cleanup after pytest run"""
    # Clean up environment variables
    os.environ.pop("PYTEST_RUNNING", None)
    os.environ.pop("TEST_ENVIRONMENT", None)


# Custom assertion helpers
class HookTestAssertions:
    """Custom assertion helpers for hook testing"""
    
    @staticmethod
    def assert_test_result_valid(result: TestResult):
        """Assert that a test result is valid"""
        assert isinstance(result, TestResult)
        assert result.test_name is not None
        assert result.hook_name is not None
        assert result.status in ["PASS", "FAIL", "ERROR", "SKIP"]
        assert isinstance(result.execution_time, (int, float))
        assert result.execution_time >= 0
        
    @staticmethod
    def assert_hook_execution_successful(execution_id: str):
        """Assert that hook execution was successful"""
        assert execution_id is not None
        assert isinstance(execution_id, str)
        assert len(execution_id) > 0
        
    @staticmethod
    def assert_performance_within_threshold(execution_time: float, threshold: float):
        """Assert that execution time is within performance threshold"""
        assert isinstance(execution_time, (int, float))
        assert execution_time <= threshold, f"Execution time {execution_time}s exceeds threshold {threshold}s"
        
    @staticmethod
    def assert_test_suite_results(results: List[TestResult], min_pass_rate: float = 0.8):
        """Assert that test suite results meet minimum pass rate"""
        assert len(results) > 0, "No test results found"
        
        passed_tests = sum(1 for result in results if result.status == "PASS")
        pass_rate = passed_tests / len(results)
        
        assert pass_rate >= min_pass_rate, f"Pass rate {pass_rate:.2%} is below minimum {min_pass_rate:.2%}"


@pytest.fixture
def hook_assertions():
    """Fixture providing custom assertion helpers"""
    return HookTestAssertions()


# Performance monitoring fixtures
@pytest.fixture(scope="function")
def performance_monitor():
    """Fixture for monitoring test performance"""
    import time
    import psutil
    
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss
    
    yield
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    execution_time = end_time - start_time
    memory_delta = end_memory - start_memory
    
    # Log performance metrics if test is slow or memory-intensive
    if execution_time > 5.0:  # > 5 seconds
        pytest.current_test_slow = True
        print(f"\nSlow test detected: {execution_time:.2f}s")
        
    if memory_delta > 50 * 1024 * 1024:  # > 50MB
        pytest.current_test_memory_intensive = True
        print(f"\nMemory-intensive test detected: {memory_delta / 1024 / 1024:.2f}MB")


# Test data validation fixtures
@pytest.fixture(scope="function")
def test_data_validator():
    """Fixture providing test data validation"""
    def validate_test_data(data: Dict[str, Any], required_fields: List[str] = None) -> bool:
        """Validate test data structure"""
        if not isinstance(data, dict):
            return False
            
        default_required_fields = ["timestamp", "test_id"]
        required_fields = required_fields or default_required_fields
        
        for field in required_fields:
            if field not in data:
                return False
                
        return True
    
    return validate_test_data


# Environment setup hooks
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Setup logging for test session"""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.WARNING,  # Reduce log noise during tests
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress verbose logging from test dependencies
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


@pytest.fixture(scope="function", autouse=True)
def isolate_tests():
    """Isolate tests from each other"""
    # Patch global state that might interfere between tests
    with patch.dict(os.environ, {}, clear=False):
        yield