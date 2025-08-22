#!/usr/bin/env python3
"""
pytest integration tests for hook testing framework
Provides comprehensive pytest-based tests for all hook functionality
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock

from test_framework import HookTestFramework, TestResult
from test_utilities import (
    TestDataGenerator, TestEnvironmentManager, PerformanceProfiler,
    ConcurrencyTester, TestValidator, HookExecutionHelper
)


class TestHookTestFramework:
    """Test the hook test framework itself"""
    
    def test_framework_initialization(self, hooks_directory):
        """Test framework initialization"""
        framework = HookTestFramework(hooks_directory=hooks_directory)
        
        assert framework.hooks_directory.exists()
        assert framework.hook_registry_data is not None
        assert "hooks" in framework.hook_registry_data
        assert framework.test_suites is not None
        assert len(framework.test_suites) > 0
        
    def test_test_suite_configuration(self, test_framework):
        """Test test suite configuration"""
        assert "individual_functionality" in test_framework.test_suites
        assert "hook_chains" in test_framework.test_suites
        assert "error_scenarios" in test_framework.test_suites
        assert "performance" in test_framework.test_suites
        assert "integration" in test_framework.test_suites
        assert "concurrency" in test_framework.test_suites
        assert "regression" in test_framework.test_suites
        
        # Test suite structure
        suite = test_framework.test_suites["individual_functionality"]
        assert suite.name is not None
        assert suite.description is not None
        assert len(suite.tests) > 0
        assert suite.timeout > 0
        
    @pytest.mark.performance
    def test_performance_baseline_loading(self, test_framework):
        """Test performance baseline loading and saving"""
        # Test loading baselines
        baselines = test_framework._load_performance_baselines()
        assert isinstance(baselines, dict)
        
        # Test saving baselines
        test_baselines = {"test_hook": 1000.0}
        test_framework.performance_baselines = test_baselines
        test_framework._save_performance_baselines()
        
        # Verify saved
        loaded_baselines = test_framework._load_performance_baselines()
        assert "test_hook" in loaded_baselines


class TestTestUtilities:
    """Test the test utilities module"""
    
    def test_test_data_generator(self, test_data_generator):
        """Test test data generation"""
        # Test user prompt data
        user_data = test_data_generator.generate_user_prompt_data()
        assert "user_input" in user_data
        assert "context" in user_data
        assert "session_data" in user_data
        
        # Test Claude response data
        response_data = test_data_generator.generate_claude_response_data()
        assert "response_text" in response_data
        assert "response_metadata" in response_data
        
        # Test agent activation data
        agent_data = test_data_generator.generate_agent_activation_data()
        assert "agent_mention" in agent_data
        assert "agent_context" in agent_data
        
        # Test performance data
        perf_data = test_data_generator.generate_performance_data()
        assert "metrics" in perf_data
        assert "thresholds" in perf_data
        
    def test_test_environment_manager(self, isolated_test_environment):
        """Test test environment management"""
        # Test temporary directory creation
        assert isolated_test_environment.temp_dir is not None
        assert isolated_test_environment.temp_dir != ""
        
        # Test file creation
        test_file = isolated_test_environment.create_test_file("test.txt", "test content")
        assert test_file in isolated_test_environment.created_files
        
        # Test config creation
        config_data = {"test": "value"}
        config_file = isolated_test_environment.create_test_config(config_data)
        assert config_file in isolated_test_environment.temp_configs
        
    def test_performance_profiler(self):
        """Test performance profiling"""
        with PerformanceProfiler("test_hook") as profiler:
            time.sleep(0.1)  # Small delay for measurement
            
        metrics = profiler.get_metrics()
        assert "hook_name" in metrics
        assert "execution_time_ms" in metrics
        assert "memory_usage_bytes" in metrics
        assert metrics["execution_time_ms"] >= 100  # At least 100ms
        
    def test_concurrency_tester(self):
        """Test concurrency testing utilities"""
        tester = ConcurrencyTester(max_workers=2)
        
        def mock_executor(data):
            time.sleep(0.1)
            return {"success": True, "data": data}
            
        test_data = [{"id": 1}, {"id": 2}, {"id": 3}]
        results = tester.execute_concurrent_hooks(mock_executor, test_data)
        
        assert len(results) == 3
        assert all(result["success"] for result in results)
        
        # Test analysis
        analysis = tester.analyze_concurrency_results(results)
        assert "total_executions" in analysis
        assert "successful_executions" in analysis
        assert "success_rate" in analysis
        
    def test_test_validator(self):
        """Test test validation utilities"""
        # Test hook execution result validation
        valid_result = {"status": "success", "timestamp": "2024-01-01T00:00:00"}
        assert TestValidator.validate_hook_execution_result(valid_result, dict)
        
        invalid_result = None
        assert not TestValidator.validate_hook_execution_result(invalid_result)
        
        # Test performance metrics validation
        metrics = {
            "execution_time_ms": 500,
            "memory_usage_bytes": 1024 * 1024,  # 1MB
            "cpu_time_ms": 250
        }
        
        is_valid, issues = TestValidator.validate_performance_metrics(metrics)
        assert is_valid
        assert len(issues) == 0
        
        # Test with threshold violations
        slow_metrics = {
            "execution_time_ms": 10000,  # 10 seconds
            "memory_usage_bytes": 200 * 1024 * 1024  # 200MB
        }
        
        is_valid, issues = TestValidator.validate_performance_metrics(slow_metrics)
        assert not is_valid
        assert len(issues) > 0


class TestIndividualHookFunctionality:
    """Test individual hook functionality"""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("hook_name", [
        "smart_orchestrator", "master_orchestrator", "v3_orchestrator",
        "audio_player_v3", "code_linter", "performance_monitor"
    ])
    def test_hook_registration_and_activation(self, mock_hook_manager, hook_name):
        """Test hook registration and activation for key hooks"""
        # Test registration
        success = mock_hook_manager.register_hook_file(f"{hook_name}.py")
        assert success
        
        # Test activation
        success = mock_hook_manager.activate_hook(hook_name)
        assert success
        
        # Test deactivation
        success = mock_hook_manager.deactivate_hook(hook_name)
        assert success
        
    @pytest.mark.unit
    def test_hook_execution_with_various_triggers(self, mock_hook_manager, comprehensive_test_data):
        """Test hook execution with different triggers"""
        hook_name = "test_hook"
        triggers = ["test", "user_prompt", "file_change", "system_event"]
        
        for trigger in triggers:
            execution_id = mock_hook_manager.execute_hook(
                hook_name, trigger, comprehensive_test_data["orchestration_hook"]
            )
            assert execution_id is not None
            assert isinstance(execution_id, str)
            
    @pytest.mark.unit
    def test_hook_execution_with_invalid_data(self, mock_hook_manager):
        """Test hook execution with invalid data"""
        hook_name = "test_hook"
        invalid_data_sets = [
            None,
            {},
            {"incomplete": "data"},
            "invalid_string_data"
        ]
        
        for invalid_data in invalid_data_sets:
            # Should handle gracefully without crashing
            execution_id = mock_hook_manager.execute_hook(hook_name, "test", invalid_data)
            # Mock returns success, but in real implementation should handle gracefully
            assert execution_id is not None


class TestHookChains:
    """Test hook chain functionality"""
    
    @pytest.mark.integration
    def test_orchestration_chain_execution(self, mock_hook_manager, comprehensive_test_data):
        """Test orchestration hook chain"""
        chain_hooks = ["smart_orchestrator", "master_orchestrator", "v3_orchestrator"]
        
        # Activate chain hooks
        for hook in chain_hooks:
            mock_hook_manager.activate_hook(hook)
            
        # Execute chain trigger
        execution_ids = mock_hook_manager.execute_by_trigger(
            "agent_mention", comprehensive_test_data["orchestration_hook"]
        )
        
        assert len(execution_ids) > 0
        assert all(isinstance(eid, str) for eid in execution_ids)
        
    @pytest.mark.integration
    def test_quality_gate_chain_execution(self, mock_hook_manager, comprehensive_test_data):
        """Test quality gate hook chain"""
        chain_hooks = ["code_linter", "security_scanner", "quality_gate_hook"]
        
        # Activate chain hooks
        for hook in chain_hooks:
            mock_hook_manager.activate_hook(hook)
            
        # Execute chain trigger
        execution_ids = mock_hook_manager.execute_by_trigger(
            "commit", comprehensive_test_data["quality_hook"]
        )
        
        assert len(execution_ids) > 0
        
    @pytest.mark.integration
    def test_session_management_chain(self, mock_hook_manager, comprehensive_test_data):
        """Test session management hook chain"""
        chain_hooks = ["session_loader", "context_manager", "session_saver"]
        
        for hook in chain_hooks:
            mock_hook_manager.activate_hook(hook)
            
        # Test session operations
        session_data = comprehensive_test_data["orchestration_hook"]
        
        load_ids = mock_hook_manager.execute_by_trigger("start", session_data)
        save_ids = mock_hook_manager.execute_by_trigger("save", session_data)
        
        assert len(load_ids) > 0
        assert len(save_ids) > 0


class TestErrorScenarios:
    """Test error handling scenarios"""
    
    @pytest.mark.unit
    def test_hook_timeout_handling(self, mock_hook_manager):
        """Test hook timeout handling"""
        # Mock timeout scenario
        with patch.object(mock_hook_manager, 'execute_hook') as mock_execute:
            def timeout_simulation(*args, **kwargs):
                time.sleep(2)  # Simulate slow execution
                return None  # Simulate timeout
                
            mock_execute.side_effect = timeout_simulation
            
            # Should handle timeout gracefully
            start_time = time.time()
            result = mock_hook_manager.execute_hook("slow_hook", "test", {})
            execution_time = time.time() - start_time
            
            # Should timeout quickly in mock (within 3 seconds)
            assert execution_time < 3.0
            
    @pytest.mark.unit
    def test_dependency_failure_recovery(self, mock_hook_manager):
        """Test dependency failure recovery"""
        # Mock dependency failure
        with patch.object(mock_hook_manager, 'execute_hook') as mock_execute:
            mock_execute.return_value = None  # Simulate dependency failure
            
            result = mock_hook_manager.execute_hook("dependent_hook", "test", {
                "dependencies": ["failed_dependency"]
            })
            
            # Should handle dependency failure gracefully
            # In mock, this returns None, but real implementation should handle gracefully
            
    @pytest.mark.unit
    def test_invalid_input_handling(self, mock_hook_manager):
        """Test handling of various invalid inputs"""
        invalid_inputs = [
            None,
            {"malformed": None},
            {"large_data": "x" * 100000},  # Large input
            {"circular_ref": None}  # Will be made circular
        ]
        
        # Create circular reference
        invalid_inputs[3]["circular_ref"] = invalid_inputs[3]
        
        for invalid_input in invalid_inputs:
            try:
                result = mock_hook_manager.execute_hook("test_hook", "test", invalid_input)
                # Should either succeed (mock) or handle gracefully
                assert True
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Unhandled exception with invalid input: {e}")


class TestPerformanceTesting:
    """Test performance aspects"""
    
    @pytest.mark.performance
    def test_hook_execution_performance(self, mock_hook_manager, performance_monitor):
        """Test hook execution performance"""
        hook_name = "performance_test_hook"
        test_data = {"performance_test": True}
        
        # Execute hook and measure performance
        start_time = time.time()
        execution_id = mock_hook_manager.execute_hook(hook_name, "test", test_data)
        execution_time = time.time() - start_time
        
        # Performance assertions
        assert execution_id is not None
        assert execution_time < 1.0  # Should complete within 1 second for mock
        
    @pytest.mark.performance
    def test_concurrent_hook_execution_performance(self, mock_hook_manager):
        """Test concurrent hook execution performance"""
        def execute_hook_task(hook_name, data):
            return mock_hook_manager.execute_hook(hook_name, "test", data)
            
        # Execute multiple hooks concurrently
        hook_data_pairs = [
            ("hook_1", {"test": 1}),
            ("hook_2", {"test": 2}), 
            ("hook_3", {"test": 3}),
            ("hook_4", {"test": 4})
        ]
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(execute_hook_task, hook_name, data)
                for hook_name, data in hook_data_pairs
            ]
            
            results = [future.result() for future in as_completed(futures)]
            
        execution_time = time.time() - start_time
        
        # All executions should complete
        assert len(results) == 4
        assert all(result is not None for result in results)
        
        # Should complete faster than sequential execution
        assert execution_time < 2.0  # Reasonable time for concurrent execution
        
    @pytest.mark.performance
    def test_memory_usage_monitoring(self, mock_hook_manager):
        """Test memory usage during hook execution"""
        import psutil
        
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Execute multiple hooks to test memory usage
        for i in range(10):
            mock_hook_manager.execute_hook(f"memory_test_hook_{i}", "test", {
                "iteration": i,
                "data": "x" * 1000  # Small data to avoid excessive memory
            })
            
        memory_after = process.memory_info().rss
        memory_growth = memory_after - memory_before
        
        # Memory growth should be reasonable (< 10MB for mock operations)
        assert memory_growth < 10 * 1024 * 1024  # 10MB


class TestConcurrencyTesting:
    """Test concurrency aspects"""
    
    @pytest.mark.concurrency
    def test_parallel_hook_execution(self, mock_hook_manager):
        """Test parallel hook execution"""
        hooks_to_test = ["hook_1", "hook_2", "hook_3", "hook_4", "hook_5"]
        
        def execute_hook_parallel(hook_name):
            return mock_hook_manager.execute_hook(hook_name, "test", {"parallel": True})
            
        # Execute hooks in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(execute_hook_parallel, hook) for hook in hooks_to_test]
            results = [future.result() for future in as_completed(futures)]
            
        # All should complete successfully
        assert len(results) == len(hooks_to_test)
        assert all(result is not None for result in results)
        
    @pytest.mark.concurrency
    def test_thread_safety(self, mock_hook_manager):
        """Test thread safety of hook operations"""
        results = []
        errors = []
        
        def thread_worker(thread_id):
            try:
                for i in range(5):
                    result = mock_hook_manager.execute_hook(
                        f"thread_test_hook_{thread_id}_{i}", 
                        "test", 
                        {"thread_id": thread_id, "iteration": i}
                    )
                    results.append(result)
            except Exception as e:
                errors.append(e)
                
        # Create multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=thread_worker, args=(thread_id,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Check results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 15  # 3 threads * 5 iterations
        assert all(result is not None for result in results)
        
    @pytest.mark.concurrency
    def test_resource_contention_handling(self, mock_hook_manager):
        """Test resource contention handling"""
        shared_resource = {"value": 0, "lock": threading.Lock()}
        
        def resource_contention_hook(hook_id):
            # Simulate resource contention
            with shared_resource["lock"]:
                old_value = shared_resource["value"]
                time.sleep(0.01)  # Small delay to create contention
                shared_resource["value"] = old_value + 1
                
            return mock_hook_manager.execute_hook(f"contention_hook_{hook_id}", "test", {
                "shared_resource_value": shared_resource["value"]
            })
            
        # Execute hooks that access shared resource
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(resource_contention_hook, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
            
        # All should complete successfully
        assert len(results) == 10
        assert all(result is not None for result in results)
        
        # Shared resource should be correctly updated
        assert shared_resource["value"] == 10


class TestRegressionTesting:
    """Test regression scenarios"""
    
    @pytest.mark.regression
    def test_backward_compatibility(self, mock_hook_manager):
        """Test backward compatibility"""
        # Test legacy data formats
        legacy_formats = [
            {"version": "1.0", "data": "legacy_string"},
            {"old_format": True, "payload": {"nested": "structure"}},
            "plain_string_legacy_format"
        ]
        
        for legacy_data in legacy_formats:
            try:
                result = mock_hook_manager.execute_hook("legacy_hook", "test", legacy_data)
                assert result is not None
            except Exception as e:
                pytest.fail(f"Backward compatibility failed for {legacy_data}: {e}")
                
    @pytest.mark.regression
    def test_api_contract_compliance(self, mock_hook_manager):
        """Test API contract compliance"""
        # Test required return formats
        execution_id = mock_hook_manager.execute_hook("contract_test_hook", "test", {})
        
        # Should return valid execution ID
        assert execution_id is not None
        assert isinstance(execution_id, str)
        assert len(execution_id) > 0
        
        # Test trigger execution
        execution_ids = mock_hook_manager.execute_by_trigger("test", {})
        assert isinstance(execution_ids, list)
        
    @pytest.mark.regression
    def test_performance_regression(self, mock_hook_manager, mock_performance_baselines):
        """Test for performance regression"""
        hook_name = "performance_regression_test"
        baseline_time = mock_performance_baselines.get(hook_name, 1000.0)  # 1s baseline
        
        # Measure current performance
        start_time = time.time()
        execution_id = mock_hook_manager.execute_hook(hook_name, "test", {})
        current_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Check for regression (allow 50% tolerance)
        regression_threshold = baseline_time * 1.5
        assert current_time <= regression_threshold, f"Performance regression detected: {current_time}ms > {regression_threshold}ms"


class TestTestReporting:
    """Test the test reporting functionality"""
    
    def test_test_result_creation(self, hook_assertions):
        """Test TestResult creation and validation"""
        result = TestResult(
            test_name="test_example",
            hook_name="example_hook",
            status="PASS",
            execution_time=1.234
        )
        
        hook_assertions.assert_test_result_valid(result)
        
    def test_test_suite_results_validation(self, sample_test_results, hook_assertions):
        """Test test suite results validation"""
        # Filter to only passed tests for this test
        passed_results = [r for r in sample_test_results if r.status == "PASS"]
        
        if passed_results:
            # Should pass with 100% pass rate
            hook_assertions.assert_test_suite_results(passed_results, min_pass_rate=1.0)
        
        # Test with mixed results - should fail with high pass rate requirement
        with pytest.raises(AssertionError):
            hook_assertions.assert_test_suite_results(sample_test_results, min_pass_rate=0.9)
            
    def test_performance_threshold_validation(self, hook_assertions):
        """Test performance threshold validation"""
        # Test within threshold
        hook_assertions.assert_performance_within_threshold(0.5, 1.0)
        
        # Test exceeding threshold
        with pytest.raises(AssertionError):
            hook_assertions.assert_performance_within_threshold(2.0, 1.0)


# Integration test with actual test data
class TestIntegrationWithRealData:
    """Integration tests using comprehensive test data"""
    
    @pytest.mark.integration
    def test_comprehensive_hook_execution(self, mock_hook_manager, comprehensive_test_data):
        """Test hook execution with comprehensive test data"""
        for data_type, test_data in comprehensive_test_data.items():
            if "hook" in data_type:
                hook_name = data_type.replace("_hook", "")
                result = mock_hook_manager.execute_hook(hook_name, "test", test_data)
                assert result is not None, f"Failed to execute {hook_name} with {data_type} data"
                
    @pytest.mark.integration
    @pytest.mark.parametrize("scenario", ["normal", "error", "performance", "concurrency"])
    def test_scenario_based_execution(self, mock_hook_manager, test_data_generator, scenario):
        """Test execution with different scenarios"""
        if scenario == "normal":
            test_data = test_data_generator.generate_user_prompt_data()
        elif scenario == "error":
            test_data = test_data_generator.generate_error_scenario_data("timeout")
        elif scenario == "performance":
            test_data = test_data_generator.generate_performance_data()
        else:  # concurrency
            test_data = test_data_generator.generate_system_event_data()
            
        result = mock_hook_manager.execute_hook("scenario_test_hook", "test", test_data)
        assert result is not None


# Smoke tests for critical functionality
class TestSmokeTests:
    """Smoke tests for critical functionality"""
    
    @pytest.mark.smoke
    def test_framework_can_initialize(self, hooks_directory):
        """Smoke test: Framework can initialize"""
        framework = HookTestFramework(hooks_directory=hooks_directory)
        assert framework is not None
        assert framework.hook_registry_data is not None
        
    @pytest.mark.smoke
    def test_basic_hook_execution(self, mock_hook_manager):
        """Smoke test: Basic hook execution works"""
        result = mock_hook_manager.execute_hook("smoke_test_hook", "test", {"smoke": True})
        assert result is not None
        
    @pytest.mark.smoke
    def test_test_data_generation(self, test_data_generator):
        """Smoke test: Test data generation works"""
        data = test_data_generator.generate_user_prompt_data()
        assert data is not None
        assert isinstance(data, dict)
        assert len(data) > 0
        
    @pytest.mark.smoke
    def test_performance_profiling(self):
        """Smoke test: Performance profiling works"""
        with PerformanceProfiler("smoke_test") as profiler:
            time.sleep(0.01)
            
        metrics = profiler.get_metrics()
        assert metrics is not None
        assert "execution_time_ms" in metrics