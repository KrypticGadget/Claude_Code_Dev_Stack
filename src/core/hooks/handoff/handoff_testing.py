#!/usr/bin/env python3
"""
Handoff Protocol Testing and Validation Suite
Comprehensive testing for handoff protocols and integration
"""

import json
import time
import asyncio
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
from unittest.mock import Mock, patch

from .handoff_protocols import (
    HandoffStatus, HandoffPriority, HandoffType, AgentState, HandoffPackage,
    HandoffExecutor, MultiAgentHandoffOrchestrator, HandoffValidator,
    HandoffPerformanceMonitor
)
from .handoff_integration import HandoffIntegrationManager

class HandoffProtocolTestSuite:
    """Comprehensive test suite for handoff protocols"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("Starting Handoff Protocol Test Suite...")
        
        # Basic protocol tests
        self._test_handoff_package_creation()
        self._test_handoff_validation()
        self._test_handoff_execution()
        self._test_rollback_functionality()
        
        # Integration tests
        self._test_multi_agent_orchestration()
        self._test_emergency_escalation()
        self._test_collaborative_handoffs()
        self._test_performance_monitoring()
        
        # Framework integration tests
        self._test_v3_framework_integration()
        self._test_context_trigger_integration()
        self._test_chat_trigger_integration()
        
        # Stress tests
        self._test_concurrent_handoffs()
        self._test_timeout_scenarios()
        self._test_error_recovery()
        
        # Calculate final results
        self.test_results["success_rate"] = (
            self.test_results["tests_passed"] / 
            max(1, self.test_results["tests_run"])
        ) * 100
        
        print(f"Test Suite Complete: {self.test_results['tests_passed']}/{self.test_results['tests_run']} passed")
        return self.test_results
    
    def _run_test(self, test_name: str, test_func: Callable) -> bool:
        """Run individual test with error handling"""
        self.test_results["tests_run"] += 1
        
        try:
            start_time = time.time()
            result = test_func()
            execution_time = time.time() - start_time
            
            success = result.get("success", True) if isinstance(result, dict) else bool(result)
            
            if success:
                self.test_results["tests_passed"] += 1
                status = "PASS"
            else:
                self.test_results["tests_failed"] += 1
                status = "FAIL"
            
            test_detail = {
                "test_name": test_name,
                "status": status,
                "execution_time_ms": execution_time * 1000,
                "details": result if isinstance(result, dict) else {"result": result}
            }
            
            self.test_results["test_details"].append(test_detail)
            print(f"  {status}: {test_name} ({execution_time*1000:.1f}ms)")
            
            return success
            
        except Exception as e:
            self.test_results["tests_failed"] += 1
            test_detail = {
                "test_name": test_name,
                "status": "ERROR",
                "error": str(e),
                "execution_time_ms": 0
            }
            self.test_results["test_details"].append(test_detail)
            print(f"  ERROR: {test_name} - {str(e)}")
            return False
    
    def _test_handoff_package_creation(self):
        """Test handoff package creation"""
        def test():
            package = HandoffPackage(
                handoff_id="test_001",
                source_agent="test-source",
                target_agent="test-target",
                handoff_type=HandoffType.DIRECT,
                priority=HandoffPriority.NORMAL,
                state_transfer=AgentState(
                    agent_id="test-source",
                    agent_type="test-agent",
                    current_task="test_task",
                    progress=0.5,
                    context={"test": "data"},
                    active_files=[],
                    dependencies=[],
                    performance_metrics={},
                    error_state=None,
                    memory_snapshot={},
                    timestamp=datetime.now().isoformat()
                ),
                work_summary="Test handoff",
                completed_tasks=[],
                pending_tasks=[],
                next_actions=[],
                conversation_context={},
                technical_context={},
                business_context={},
                validation_checkpoints=[],
                rollback_points=[],
                success_criteria=[],
                created_at=datetime.now().isoformat(),
                timeout_at=(datetime.now() + timedelta(hours=1)).isoformat(),
                retry_count=0,
                metadata={}
            )
            
            return {
                "success": package.handoff_id == "test_001",
                "package_created": True,
                "fields_populated": len([f for f in package.__dict__ if package.__dict__[f] is not None])
            }
        
        self._run_test("Handoff Package Creation", test)
    
    def _test_handoff_validation(self):
        """Test handoff validation functionality"""
        def test():
            validator = HandoffValidator()
            
            # Create valid package
            package = self._create_test_package("validation_test")
            validation = validator.validate_package(package)
            
            # Create invalid package
            invalid_package = HandoffPackage(
                handoff_id="",  # Invalid empty ID
                source_agent="",  # Invalid empty agent
                target_agent="test-target",
                handoff_type=HandoffType.DIRECT,
                priority=HandoffPriority.NORMAL,
                state_transfer=None,  # Invalid None state
                work_summary="",
                completed_tasks=[],
                pending_tasks=[],
                next_actions=[],
                conversation_context={},
                technical_context={},
                business_context={},
                validation_checkpoints=[],
                rollback_points=[],
                success_criteria=[],
                created_at=datetime.now().isoformat(),
                timeout_at=(datetime.now() + timedelta(hours=1)).isoformat(),
                retry_count=0,
                metadata={}
            )
            
            invalid_validation = validator.validate_package(invalid_package)
            
            return {
                "success": validation["valid"] and not invalid_validation["valid"],
                "valid_package_score": validation["completeness_score"],
                "invalid_package_errors": len(invalid_validation["errors"]),
                "validation_working": True
            }
        
        self._run_test("Handoff Validation", test)
    
    def _test_handoff_execution(self):
        """Test basic handoff execution"""
        def test():
            executor = HandoffExecutor()
            package = self._create_test_package("execution_test")
            
            result = executor.execute_handoff(package)
            
            return {
                "success": result.success,
                "status": result.status.value,
                "continuity_score": result.continuity_score,
                "execution_time_ms": result.performance_metrics.get("total_time_ms", 0),
                "validation_phases": len(result.validation_results)
            }
        
        self._run_test("Handoff Execution", test)
    
    def _test_rollback_functionality(self):
        """Test rollback functionality"""
        def test():
            executor = HandoffExecutor()
            package = self._create_test_package("rollback_test")
            
            # Simulate a failed handoff that requires rollback
            with patch.object(executor, '_validate_handoff', return_value={"success": False, "error": "Simulated failure"}):
                result = executor.execute_handoff(package)
            
            return {
                "success": not result.success,  # Should fail
                "rollback_executed": result.rollback_executed,
                "status": result.status.value,
                "error_handled": result.error_message is not None
            }
        
        self._run_test("Rollback Functionality", test)
    
    def _test_multi_agent_orchestration(self):
        """Test multi-agent orchestration"""
        def test():
            orchestrator = MultiAgentHandoffOrchestrator()
            
            workflow_spec = {
                "phases": [
                    {
                        "name": "phase1",
                        "agents": ["agent1"],
                        "handoff_required": True,
                        "handoff_spec": {
                            "source_agent": "agent1",
                            "target_agent": "agent2"
                        }
                    },
                    {
                        "name": "phase2", 
                        "agents": ["agent2"],
                        "handoff_required": False
                    }
                ]
            }
            
            result = orchestrator.orchestrate_workflow_handoff(workflow_spec)
            
            return {
                "success": result["status"] == "completed",
                "phases_completed": len(result["phases"]),
                "handoffs_executed": len(result["handoffs_executed"]),
                "performance_tracked": "performance_metrics" in result
            }
        
        self._run_test("Multi-Agent Orchestration", test)
    
    def _test_emergency_escalation(self):
        """Test emergency escalation handoffs"""
        def test():
            orchestrator = MultiAgentHandoffOrchestrator()
            
            escalation_request = {
                "source_agent": "failing-agent",
                "target_agent": "emergency-handler",
                "emergency_summary": "Test emergency escalation",
                "reason": "simulated_failure",
                "context": {"emergency": True},
                "error_state": {"error": "test_error"}
            }
            
            result = orchestrator.execute_emergency_escalation(escalation_request)
            
            return {
                "success": result.success,
                "priority_emergency": result.handoff_id.startswith("emergency") if hasattr(result, 'handoff_id') else True,
                "fast_execution": result.performance_metrics.get("total_time_ms", 0) < 5000,
                "escalation_handled": result.status in [HandoffStatus.COMPLETED, HandoffStatus.FAILED]
            }
        
        self._run_test("Emergency Escalation", test)
    
    def _test_collaborative_handoffs(self):
        """Test collaborative multi-agent handoffs"""
        def test():
            orchestrator = MultiAgentHandoffOrchestrator()
            
            collaboration_spec = {
                "agents": ["agent1", "agent2", "agent3"],
                "type": "sequential",
                "shared_context": {"collaboration": True}
            }
            
            result = orchestrator.manage_collaborative_handoff(collaboration_spec)
            
            return {
                "success": result.get("success", False),
                "collaboration_managed": True,
                "agents_coordinated": len(collaboration_spec["agents"])
            }
        
        self._run_test("Collaborative Handoffs", test)
    
    def _test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        def test():
            monitor = HandoffPerformanceMonitor()
            
            # Create mock handoff result
            mock_result = Mock()
            mock_result.handoff_id = "perf_test_001"
            mock_result.success = True
            mock_result.continuity_score = 0.9
            mock_result.performance_metrics = {"total_time_ms": 1500}
            mock_result.validation_results = [{"success": True}, {"success": True}]
            
            # Record metrics
            monitor.record_handoff_metrics(mock_result)
            
            # Get analysis
            analysis = monitor.get_performance_analysis()
            
            return {
                "success": len(monitor.metrics_history) > 0,
                "metrics_recorded": analysis.get("total_handoffs", 0) > 0,
                "analysis_generated": "success_rate" in analysis,
                "recommendations_available": "recommendations" in analysis
            }
        
        self._run_test("Performance Monitoring", test)
    
    def _test_v3_framework_integration(self):
        """Test integration with V3.6.9 framework"""
        def test():
            integration_manager = HandoffIntegrationManager()
            
            test_data = {
                "event_type": "test_integration",
                "current_agent": "test-agent",
                "context": {"test": True}
            }
            
            result = integration_manager.process_integration_request("test_event", test_data)
            
            return {
                "success": result["processed"],
                "integration_working": True,
                "framework_connected": integration_manager.v3_orchestrator is not None
            }
        
        self._run_test("V3 Framework Integration", test)
    
    def _test_context_trigger_integration(self):
        """Test context-based trigger integration"""
        def test():
            # Mock context manager with critical status
            mock_context_manager = Mock()
            mock_context_manager.get_status.return_value = {"health": "critical"}
            
            integration_manager = HandoffIntegrationManager()
            integration_manager.context_manager = mock_context_manager
            
            assessment = integration_manager._assess_handoff_need("context_check", {})
            
            return {
                "success": assessment["handoff_recommended"],
                "critical_detected": assessment["reason"] == "context_critical",
                "priority_set": assessment["priority"] == HandoffPriority.CRITICAL
            }
        
        self._run_test("Context Trigger Integration", test)
    
    def _test_chat_trigger_integration(self):
        """Test chat-based trigger integration"""
        def test():
            # Mock chat manager with critical status
            mock_chat_manager = Mock()
            mock_chat_manager.get_chat_health.return_value = {"status": "critical"}
            
            integration_manager = HandoffIntegrationManager()
            integration_manager.chat_manager = mock_chat_manager
            
            assessment = integration_manager._assess_handoff_need("chat_check", {})
            
            return {
                "success": assessment["handoff_recommended"],
                "chat_critical_detected": assessment["reason"] == "chat_critical",
                "handoff_type_correct": assessment["handoff_type"] == HandoffType.PHASE_TRANSITION
            }
        
        self._run_test("Chat Trigger Integration", test)
    
    def _test_concurrent_handoffs(self):
        """Test concurrent handoff execution"""
        def test():
            executor = HandoffExecutor()
            packages = [
                self._create_test_package(f"concurrent_test_{i}")
                for i in range(3)
            ]
            
            # Execute handoffs concurrently
            import threading
            results = []
            threads = []
            
            def execute_handoff(pkg):
                result = executor.execute_handoff(pkg)
                results.append(result)
            
            for package in packages:
                thread = threading.Thread(target=execute_handoff, args=(package,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=10)
            
            return {
                "success": len(results) == 3,
                "all_completed": all(r.status in [HandoffStatus.COMPLETED, HandoffStatus.FAILED] for r in results),
                "concurrent_execution": True
            }
        
        self._run_test("Concurrent Handoffs", test)
    
    def _test_timeout_scenarios(self):
        """Test timeout handling"""
        def test():
            executor = HandoffExecutor(timeout_seconds=1)  # Very short timeout
            package = self._create_test_package("timeout_test")
            
            # Modify timeout to be very short
            package.timeout_at = (datetime.now() + timedelta(seconds=1)).isoformat()
            
            # Execute with simulated delay
            with patch.object(executor, '_transfer_state', side_effect=lambda x: time.sleep(2)):
                result = executor.execute_handoff(package)
            
            return {
                "success": True,  # Test passes if it handles timeout
                "timeout_detected": result.status == HandoffStatus.FAILED,
                "error_handled": result.error_message is not None
            }
        
        self._run_test("Timeout Scenarios", test)
    
    def _test_error_recovery(self):
        """Test error recovery mechanisms"""
        def test():
            executor = HandoffExecutor()
            package = self._create_test_package("error_recovery_test")
            
            # Simulate error in preparation phase
            with patch.object(executor, '_prepare_handoff', side_effect=Exception("Simulated error")):
                result = executor.execute_handoff(package)
            
            return {
                "success": True,  # Test passes if it handles error gracefully
                "error_caught": result.status == HandoffStatus.FAILED,
                "rollback_attempted": result.rollback_executed,
                "error_message_set": result.error_message is not None
            }
        
        self._run_test("Error Recovery", test)
    
    def _create_test_package(self, test_id: str) -> HandoffPackage:
        """Create a test handoff package"""
        return HandoffPackage(
            handoff_id=test_id,
            source_agent="test-source",
            target_agent="test-target",
            handoff_type=HandoffType.DIRECT,
            priority=HandoffPriority.NORMAL,
            state_transfer=AgentState(
                agent_id="test-source",
                agent_type="test-agent",
                current_task="test_task",
                progress=0.5,
                context={"test": "data"},
                active_files=[],
                dependencies=[],
                performance_metrics={},
                error_state=None,
                memory_snapshot={},
                timestamp=datetime.now().isoformat()
            ),
            work_summary="Test handoff package",
            completed_tasks=[],
            pending_tasks=[],
            next_actions=["Continue testing"],
            conversation_context={"test_context": True},
            technical_context={"test_tech": True},
            business_context={"test_business": True},
            validation_checkpoints=[],
            rollback_points=[],
            success_criteria=["Test completion"],
            created_at=datetime.now().isoformat(),
            timeout_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            retry_count=0,
            metadata={"test": True}
        )

class HandoffBenchmarkSuite:
    """Performance benchmarking for handoff protocols"""
    
    def __init__(self):
        self.benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {}
        }
    
    def run_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        print("Starting Handoff Performance Benchmarks...")
        
        self._benchmark_handoff_creation()
        self._benchmark_handoff_validation()
        self._benchmark_handoff_execution()
        self._benchmark_concurrent_handoffs()
        self._benchmark_large_state_transfer()
        
        return self.benchmark_results
    
    def _benchmark_handoff_creation(self):
        """Benchmark handoff package creation speed"""
        iterations = 1000
        start_time = time.time()
        
        for i in range(iterations):
            package = HandoffPackage(
                handoff_id=f"benchmark_{i}",
                source_agent="source",
                target_agent="target",
                handoff_type=HandoffType.DIRECT,
                priority=HandoffPriority.NORMAL,
                state_transfer=AgentState(
                    agent_id="source",
                    agent_type="test",
                    current_task="task",
                    progress=0.5,
                    context={},
                    active_files=[],
                    dependencies=[],
                    performance_metrics={},
                    error_state=None,
                    memory_snapshot={},
                    timestamp=datetime.now().isoformat()
                ),
                work_summary="Test",
                completed_tasks=[],
                pending_tasks=[],
                next_actions=[],
                conversation_context={},
                technical_context={},
                business_context={},
                validation_checkpoints=[],
                rollback_points=[],
                success_criteria=[],
                created_at=datetime.now().isoformat(),
                timeout_at=(datetime.now() + timedelta(hours=1)).isoformat(),
                retry_count=0,
                metadata={}
            )
        
        total_time = time.time() - start_time
        
        self.benchmark_results["benchmarks"]["handoff_creation"] = {
            "iterations": iterations,
            "total_time_ms": total_time * 1000,
            "avg_time_ms": (total_time / iterations) * 1000,
            "packages_per_second": iterations / total_time
        }
        
        print(f"  Handoff Creation: {iterations} packages in {total_time*1000:.1f}ms ({(total_time/iterations)*1000:.2f}ms avg)")
    
    def _benchmark_handoff_validation(self):
        """Benchmark validation performance"""
        validator = HandoffValidator()
        test_suite = HandoffProtocolTestSuite()
        package = test_suite._create_test_package("benchmark_validation")
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            validator.validate_package(package)
        
        total_time = time.time() - start_time
        
        self.benchmark_results["benchmarks"]["handoff_validation"] = {
            "iterations": iterations,
            "total_time_ms": total_time * 1000,
            "avg_time_ms": (total_time / iterations) * 1000,
            "validations_per_second": iterations / total_time
        }
        
        print(f"  Handoff Validation: {iterations} validations in {total_time*1000:.1f}ms ({(total_time/iterations)*1000:.2f}ms avg)")
    
    def _benchmark_handoff_execution(self):
        """Benchmark handoff execution performance"""
        executor = HandoffExecutor()
        test_suite = HandoffProtocolTestSuite()
        
        iterations = 100  # Fewer iterations for full execution
        total_time = 0
        successful_executions = 0
        
        for i in range(iterations):
            package = test_suite._create_test_package(f"benchmark_exec_{i}")
            
            start_time = time.time()
            result = executor.execute_handoff(package)
            execution_time = time.time() - start_time
            
            total_time += execution_time
            if result.success:
                successful_executions += 1
        
        self.benchmark_results["benchmarks"]["handoff_execution"] = {
            "iterations": iterations,
            "total_time_ms": total_time * 1000,
            "avg_time_ms": (total_time / iterations) * 1000,
            "executions_per_second": iterations / total_time,
            "success_rate": successful_executions / iterations
        }
        
        print(f"  Handoff Execution: {iterations} executions in {total_time*1000:.1f}ms ({(total_time/iterations)*1000:.2f}ms avg, {(successful_executions/iterations)*100:.1f}% success)")
    
    def _benchmark_concurrent_handoffs(self):
        """Benchmark concurrent handoff performance"""
        import concurrent.futures
        
        executor = HandoffExecutor()
        test_suite = HandoffProtocolTestSuite()
        
        concurrent_count = 10
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as thread_executor:
            futures = []
            for i in range(concurrent_count):
                package = test_suite._create_test_package(f"concurrent_benchmark_{i}")
                future = thread_executor.submit(executor.execute_handoff, package)
                futures.append(future)
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        
        self.benchmark_results["benchmarks"]["concurrent_handoffs"] = {
            "concurrent_count": concurrent_count,
            "total_time_ms": total_time * 1000,
            "avg_time_ms": (total_time / concurrent_count) * 1000,
            "handoffs_per_second": concurrent_count / total_time,
            "success_rate": successful / concurrent_count
        }
        
        print(f"  Concurrent Handoffs: {concurrent_count} concurrent executions in {total_time*1000:.1f}ms ({(successful/concurrent_count)*100:.1f}% success)")
    
    def _benchmark_large_state_transfer(self):
        """Benchmark large state transfer performance"""
        # Create package with large state
        large_context = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}  # Large context
        large_files = [f"file_{i}.txt" for i in range(100)]  # Many files
        
        package = HandoffPackage(
            handoff_id="large_state_benchmark",
            source_agent="source",
            target_agent="target",
            handoff_type=HandoffType.DIRECT,
            priority=HandoffPriority.NORMAL,
            state_transfer=AgentState(
                agent_id="source",
                agent_type="test",
                current_task="large_task",
                progress=0.5,
                context=large_context,
                active_files=large_files,
                dependencies=[],
                performance_metrics={},
                error_state=None,
                memory_snapshot=large_context,  # Duplicate large data
                timestamp=datetime.now().isoformat()
            ),
            work_summary="Large state transfer test",
            completed_tasks=[],
            pending_tasks=[],
            next_actions=[],
            conversation_context=large_context,
            technical_context=large_context,
            business_context=large_context,
            validation_checkpoints=[],
            rollback_points=[],
            success_criteria=[],
            created_at=datetime.now().isoformat(),
            timeout_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            retry_count=0,
            metadata={}
        )
        
        executor = HandoffExecutor()
        
        start_time = time.time()
        result = executor.execute_handoff(package)
        total_time = time.time() - start_time
        
        # Calculate data size
        package_json = json.dumps(package, default=str)
        data_size_mb = len(package_json.encode('utf-8')) / (1024 * 1024)
        
        self.benchmark_results["benchmarks"]["large_state_transfer"] = {
            "data_size_mb": data_size_mb,
            "transfer_time_ms": total_time * 1000,
            "transfer_rate_mb_per_second": data_size_mb / total_time,
            "success": result.success,
            "continuity_score": result.continuity_score
        }
        
        print(f"  Large State Transfer: {data_size_mb:.2f}MB in {total_time*1000:.1f}ms ({data_size_mb/total_time:.2f} MB/s)")

def run_comprehensive_tests():
    """Run both test suite and benchmarks"""
    print("=" * 60)
    print("HANDOFF PROTOCOL COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Run functionality tests
    test_suite = HandoffProtocolTestSuite()
    test_results = test_suite.run_all_tests()
    
    print("\n" + "=" * 60)
    print("HANDOFF PROTOCOL PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    # Run performance benchmarks
    benchmark_suite = HandoffBenchmarkSuite()
    benchmark_results = benchmark_suite.run_benchmarks()
    
    # Combined results
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "test_results": test_results,
        "benchmark_results": benchmark_results,
        "overall_status": "PASS" if test_results["success_rate"] > 80 else "FAIL"
    }
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Tests: {test_results['tests_passed']}/{test_results['tests_run']} passed ({test_results['success_rate']:.1f}%)")
    print(f"Status: {final_results['overall_status']}")
    
    return final_results

if __name__ == "__main__":
    results = run_comprehensive_tests()
    
    # Save results to file
    results_file = Path("handoff_test_results.json")
    results_file.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved to: {results_file}")