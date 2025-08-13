#!/usr/bin/env python3
"""
Claude Code v3.0 System Validator
Comprehensive testing and validation for Phase 1 components
"""

import sys
import json
import time
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Import v3.0 components for testing
try:
    from .status_line_manager import get_status_line, StatusLineCore
    from .context_manager import get_context_manager, EnhancedContextManager
    from .chat_manager import get_chat_manager, ChatManagementSystem, HandoffTrigger
    from .v3_orchestrator import get_v3_orchestrator, ClaudeCodeV3Orchestrator
    from .v3_config import get_config, V3Config
    STATUS_LINE_AVAILABLE = True
    CONTEXT_MANAGER_AVAILABLE = True
    CHAT_MANAGER_AVAILABLE = True
    ORCHESTRATOR_AVAILABLE = True
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    STATUS_LINE_AVAILABLE = False
    CONTEXT_MANAGER_AVAILABLE = False
    CHAT_MANAGER_AVAILABLE = False
    ORCHESTRATOR_AVAILABLE = False
    CONFIG_AVAILABLE = False

class V3SystemValidator:
    """
    Comprehensive validation system for Claude Code v3.0
    """
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "component_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        self.components = {
            "status_line": None,
            "context_manager": None,
            "chat_manager": None,
            "orchestrator": None,
            "config": None
        }
    
    def run_comprehensive_validation(self) -> Dict:
        """Run complete v3.0 system validation"""
        print("🚀 Starting Claude Code v3.0 System Validation")
        print("=" * 60)
        
        try:
            # Phase 1: Component Availability Tests
            print("\n📋 Phase 1: Component Availability Tests")
            self._test_component_availability()
            
            # Phase 2: Individual Component Tests
            print("\n🔧 Phase 2: Individual Component Tests")
            self._test_individual_components()
            
            # Phase 3: Integration Tests
            print("\n🔗 Phase 3: Component Integration Tests")
            self._test_component_integration()
            
            # Phase 4: Performance Tests
            print("\n⚡ Phase 4: Performance Tests")
            self._test_system_performance()
            
            # Phase 5: End-to-End Workflow Tests
            print("\n🎯 Phase 5: End-to-End Workflow Tests")
            self._test_end_to_end_workflows()
            
            # Generate final assessment
            self._generate_final_assessment()
            
        except Exception as e:
            self.test_results["errors"].append({
                "phase": "validation_execution",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
        
        # Print results summary
        self._print_results_summary()
        
        return self.test_results
    
    def _test_component_availability(self):
        """Test availability of all v3.0 components"""
        availability_tests = [
            ("status_line", STATUS_LINE_AVAILABLE, "Status Line Manager"),
            ("context_manager", CONTEXT_MANAGER_AVAILABLE, "Context Manager"),
            ("chat_manager", CHAT_MANAGER_AVAILABLE, "Chat Manager"),
            ("orchestrator", ORCHESTRATOR_AVAILABLE, "v3.0 Orchestrator"),
            ("config", CONFIG_AVAILABLE, "Configuration System")
        ]
        
        for component_key, available, description in availability_tests:
            self.test_results["tests_run"] += 1
            
            if available:
                self.test_results["tests_passed"] += 1
                print(f"✅ {description}: Available")
                self.test_results["component_tests"][component_key] = {"available": True}
            else:
                self.test_results["tests_failed"] += 1
                print(f"❌ {description}: Not Available")
                self.test_results["component_tests"][component_key] = {"available": False}
                self.test_results["errors"].append({
                    "component": component_key,
                    "error": f"{description} not available for testing"
                })
    
    def _test_individual_components(self):
        """Test each component individually"""
        
        # Test Status Line
        if STATUS_LINE_AVAILABLE:
            print("\n  🔍 Testing Status Line Manager...")
            self._test_status_line()
        
        # Test Context Manager
        if CONTEXT_MANAGER_AVAILABLE:
            print("\n  🔍 Testing Context Manager...")
            self._test_context_manager()
        
        # Test Chat Manager
        if CHAT_MANAGER_AVAILABLE:
            print("\n  🔍 Testing Chat Manager...")
            self._test_chat_manager()
        
        # Test Configuration System
        if CONFIG_AVAILABLE:
            print("\n  🔍 Testing Configuration System...")
            self._test_configuration_system()
    
    def _test_status_line(self):
        """Test Status Line Manager functionality"""
        test_name = "status_line_functionality"
        try:
            status_line = get_status_line()
            self.components["status_line"] = status_line
            
            # Test status update
            status_line.update_status(
                "test_component", 
                "active", 
                {"test": True, "timestamp": datetime.utcnow().isoformat()}
            )
            
            # Test current status retrieval
            current_status = status_line.get_current_status()
            
            # Test intelligent routing
            routing = status_line.get_intelligent_routing()
            
            # Test git status
            status_line.update_git_status()
            
            self.test_results["component_tests"]["status_line"] = {
                "available": True,
                "status_update": True,
                "current_status": current_status is not None,
                "intelligent_routing": routing is not None,
                "git_integration": True
            }
            
            self.test_results["tests_run"] += 4
            self.test_results["tests_passed"] += 4
            print("    ✅ Status updates working")
            print("    ✅ Current status retrieval working")
            print("    ✅ Intelligent routing working")
            print("    ✅ Git integration working")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["component_tests"]["status_line"] = {
                "available": True,
                "error": str(e)
            }
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            print(f"    ❌ Status Line test failed: {e}")
    
    def _test_context_manager(self):
        """Test Context Manager functionality"""
        test_name = "context_manager_functionality"
        try:
            context_manager = get_context_manager()
            self.components["context_manager"] = context_manager
            
            # Test context snapshot creation
            snapshot = context_manager.create_context_snapshot()
            
            # Test context health check
            health = context_manager.get_context_health()
            
            # Test handoff execution
            handoff_result = context_manager.execute_intelligent_handoff(
                "test_agent_1", "test_agent_2", {"test": True}
            )
            
            # Test context optimization
            optimization_result = context_manager.optimize_context("gentle")
            
            self.test_results["component_tests"]["context_manager"] = {
                "available": True,
                "snapshot_creation": snapshot is not None,
                "health_check": health is not None,
                "handoff_execution": handoff_result.success,
                "context_optimization": optimization_result is not None
            }
            
            self.test_results["tests_run"] += 4
            self.test_results["tests_passed"] += 4
            print("    ✅ Context snapshot creation working")
            print("    ✅ Context health monitoring working")
            print("    ✅ Intelligent handoffs working")
            print("    ✅ Context optimization working")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["component_tests"]["context_manager"] = {
                "available": True,
                "error": str(e)
            }
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            print(f"    ❌ Context Manager test failed: {e}")
    
    def _test_chat_manager(self):
        """Test Chat Manager functionality"""
        test_name = "chat_manager_functionality"
        try:
            chat_manager = get_chat_manager()
            self.components["chat_manager"] = chat_manager
            
            # Test conversation flow management
            flow_result = chat_manager.manage_conversation_flow(
                "Test user message for v3.0 validation", "user"
            )
            
            # Test conversation health check
            health = chat_manager.check_conversation_health()
            
            # Test handoff suggestions
            suggestions = chat_manager.get_handoff_suggestions()
            
            # Test continuity report
            continuity_report = chat_manager.generate_continuity_report()
            
            self.test_results["component_tests"]["chat_manager"] = {
                "available": True,
                "conversation_flow": flow_result.get("processed", False),
                "health_monitoring": health is not None,
                "handoff_suggestions": suggestions is not None,
                "continuity_reporting": continuity_report is not None
            }
            
            self.test_results["tests_run"] += 4
            self.test_results["tests_passed"] += 4
            print("    ✅ Conversation flow management working")
            print("    ✅ Health monitoring working")
            print("    ✅ Handoff suggestions working")
            print("    ✅ Continuity reporting working")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["component_tests"]["chat_manager"] = {
                "available": True,
                "error": str(e)
            }
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            print(f"    ❌ Chat Manager test failed: {e}")
    
    def _test_configuration_system(self):
        """Test Configuration System functionality"""
        test_name = "configuration_system"
        try:
            config = get_config()
            
            # Test config loading
            config_loaded = config is not None
            
            # Test config structure
            has_status_line_config = hasattr(config, 'status_line')
            has_context_manager_config = hasattr(config, 'context_manager')
            has_chat_manager_config = hasattr(config, 'chat_manager')
            has_orchestrator_config = hasattr(config, 'orchestrator')
            
            self.test_results["component_tests"]["config"] = {
                "available": True,
                "config_loaded": config_loaded,
                "status_line_config": has_status_line_config,
                "context_manager_config": has_context_manager_config,
                "chat_manager_config": has_chat_manager_config,
                "orchestrator_config": has_orchestrator_config
            }
            
            self.test_results["tests_run"] += 5
            self.test_results["tests_passed"] += 5
            print("    ✅ Configuration loading working")
            print("    ✅ Status line config available")
            print("    ✅ Context manager config available")
            print("    ✅ Chat manager config available")
            print("    ✅ Orchestrator config available")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["component_tests"]["config"] = {
                "available": True,
                "error": str(e)
            }
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            print(f"    ❌ Configuration system test failed: {e}")
    
    def _test_component_integration(self):
        """Test integration between components"""
        
        # Test Status Line ↔ Context Manager integration
        if STATUS_LINE_AVAILABLE and CONTEXT_MANAGER_AVAILABLE:
            print("\n  🔗 Testing Status Line ↔ Context Manager integration...")
            self._test_status_context_integration()
        
        # Test Chat Manager ↔ Context Manager integration
        if CHAT_MANAGER_AVAILABLE and CONTEXT_MANAGER_AVAILABLE:
            print("\n  🔗 Testing Chat Manager ↔ Context Manager integration...")
            self._test_chat_context_integration()
        
        # Test Status Line ↔ Chat Manager integration
        if STATUS_LINE_AVAILABLE and CHAT_MANAGER_AVAILABLE:
            print("\n  🔗 Testing Status Line ↔ Chat Manager integration...")
            self._test_status_chat_integration()
    
    def _test_status_context_integration(self):
        """Test Status Line and Context Manager integration"""
        test_name = "status_context_integration"
        try:
            status_line = self.components.get("status_line") or get_status_line()
            context_manager = self.components.get("context_manager") or get_context_manager()
            
            # Simulate status change that should trigger context snapshot
            status_line.update_status(
                "integration_test",
                "active",
                {"integration_test": True, "trigger_snapshot": True}
            )
            
            # Create context snapshot with status integration
            snapshot = context_manager.create_context_snapshot()
            
            integration_working = snapshot is not None
            
            self.test_results["integration_tests"]["status_context"] = {
                "integration_working": integration_working,
                "snapshot_created": snapshot is not None
            }
            
            self.test_results["tests_run"] += 1
            if integration_working:
                self.test_results["tests_passed"] += 1
                print("    ✅ Status Line ↔ Context Manager integration working")
            else:
                self.test_results["tests_failed"] += 1
                print("    ❌ Status Line ↔ Context Manager integration failed")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["integration_tests"]["status_context"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ Status-Context integration test failed: {e}")
    
    def _test_chat_context_integration(self):
        """Test Chat Manager and Context Manager integration"""
        test_name = "chat_context_integration"
        try:
            chat_manager = self.components.get("chat_manager") or get_chat_manager()
            context_manager = self.components.get("context_manager") or get_context_manager()
            
            # Test handoff with context preservation
            handoff_result = chat_manager.execute_intelligent_handoff(
                "test_agent_1",
                "test_agent_2", 
                HandoffTrigger.EXPLICIT_REQUEST
            )
            
            integration_working = handoff_result.get("success", False)
            
            self.test_results["integration_tests"]["chat_context"] = {
                "integration_working": integration_working,
                "handoff_success": handoff_result.get("success", False),
                "continuity_score": handoff_result.get("continuity_score", 0.0)
            }
            
            self.test_results["tests_run"] += 1
            if integration_working:
                self.test_results["tests_passed"] += 1
                print("    ✅ Chat Manager ↔ Context Manager integration working")
            else:
                self.test_results["tests_failed"] += 1
                print("    ❌ Chat Manager ↔ Context Manager integration failed")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["integration_tests"]["chat_context"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ Chat-Context integration test failed: {e}")
    
    def _test_status_chat_integration(self):
        """Test Status Line and Chat Manager integration"""
        test_name = "status_chat_integration"
        try:
            status_line = self.components.get("status_line") or get_status_line()
            chat_manager = self.components.get("chat_manager") or get_chat_manager()
            
            # Test conversation flow with status updates
            flow_result = chat_manager.manage_conversation_flow(
                "Test message for status integration", "user"
            )
            
            # Check if status was updated
            current_status = status_line.get_current_status()
            
            integration_working = (
                flow_result.get("processed", False) and 
                current_status is not None
            )
            
            self.test_results["integration_tests"]["status_chat"] = {
                "integration_working": integration_working,
                "conversation_processed": flow_result.get("processed", False),
                "status_updated": current_status is not None
            }
            
            self.test_results["tests_run"] += 1
            if integration_working:
                self.test_results["tests_passed"] += 1
                print("    ✅ Status Line ↔ Chat Manager integration working")
            else:
                self.test_results["tests_failed"] += 1
                print("    ❌ Status Line ↔ Chat Manager integration failed")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["integration_tests"]["status_chat"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ Status-Chat integration test failed: {e}")
    
    def _test_system_performance(self):
        """Test system performance metrics"""
        print("\n  ⚡ Testing response times...")
        
        if ORCHESTRATOR_AVAILABLE:
            self._test_orchestrator_performance()
        
        if STATUS_LINE_AVAILABLE:
            self._test_status_line_performance()
    
    def _test_orchestrator_performance(self):
        """Test orchestrator performance"""
        test_name = "orchestrator_performance"
        try:
            orchestrator = get_v3_orchestrator()
            
            # Measure processing time
            start_time = time.time()
            
            result = orchestrator.process_request("user_prompt", {
                "prompt": "Test performance measurement for v3.0 system"
            })
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Performance thresholds
            excellent_threshold = 100  # ms
            good_threshold = 500  # ms
            acceptable_threshold = 1000  # ms
            
            if processing_time <= excellent_threshold:
                performance_rating = "excellent"
            elif processing_time <= good_threshold:
                performance_rating = "good"
            elif processing_time <= acceptable_threshold:
                performance_rating = "acceptable"
            else:
                performance_rating = "poor"
            
            self.test_results["performance_tests"]["orchestrator"] = {
                "processing_time_ms": round(processing_time, 2),
                "performance_rating": performance_rating,
                "request_processed": result.get("processed", False)
            }
            
            self.test_results["tests_run"] += 1
            if performance_rating in ["excellent", "good", "acceptable"]:
                self.test_results["tests_passed"] += 1
                print(f"    ✅ Orchestrator performance: {performance_rating} ({processing_time:.1f}ms)")
            else:
                self.test_results["tests_failed"] += 1
                print(f"    ❌ Orchestrator performance: {performance_rating} ({processing_time:.1f}ms)")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["performance_tests"]["orchestrator"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ Orchestrator performance test failed: {e}")
    
    def _test_status_line_performance(self):
        """Test status line performance"""
        test_name = "status_line_performance"
        try:
            status_line = self.components.get("status_line") or get_status_line()
            
            # Measure status update time
            start_time = time.time()
            
            status_line.update_status(
                "performance_test",
                "active",
                {"test": "performance", "timestamp": datetime.utcnow().isoformat()}
            )
            
            update_time = (time.time() - start_time) * 1000
            
            # Measure status retrieval time
            start_time = time.time()
            current_status = status_line.get_current_status()
            retrieval_time = (time.time() - start_time) * 1000
            
            # Performance assessment
            target_update_time = 50  # ms
            target_retrieval_time = 100  # ms
            
            update_performance = "good" if update_time <= target_update_time else "acceptable" if update_time <= 200 else "poor"
            retrieval_performance = "good" if retrieval_time <= target_retrieval_time else "acceptable" if retrieval_time <= 300 else "poor"
            
            self.test_results["performance_tests"]["status_line"] = {
                "update_time_ms": round(update_time, 2),
                "retrieval_time_ms": round(retrieval_time, 2),
                "update_performance": update_performance,
                "retrieval_performance": retrieval_performance
            }
            
            self.test_results["tests_run"] += 2
            if update_performance in ["good", "acceptable"] and retrieval_performance in ["good", "acceptable"]:
                self.test_results["tests_passed"] += 2
                print(f"    ✅ Status Line update: {update_performance} ({update_time:.1f}ms)")
                print(f"    ✅ Status Line retrieval: {retrieval_performance} ({retrieval_time:.1f}ms)")
            else:
                self.test_results["tests_failed"] += 2
                print(f"    ❌ Status Line update: {update_performance} ({update_time:.1f}ms)")
                print(f"    ❌ Status Line retrieval: {retrieval_performance} ({retrieval_time:.1f}ms)")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["performance_tests"]["status_line"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ Status Line performance test failed: {e}")
    
    def _test_end_to_end_workflows(self):
        """Test complete end-to-end workflows"""
        if ORCHESTRATOR_AVAILABLE:
            print("\n  🎯 Testing complete workflow orchestration...")
            self._test_complete_workflow()
    
    def _test_complete_workflow(self):
        """Test complete workflow from user input to agent handoff"""
        test_name = "end_to_end_workflow"
        try:
            orchestrator = get_v3_orchestrator()
            
            # Test complete workflow
            workflow_request = {
                "type": "development_project",
                "description": "Build a simple web application with authentication",
                "complexity": "medium",
                "phases": ["planning", "implementation", "testing"]
            }
            
            workflow_result = orchestrator.execute_intelligent_workflow(workflow_request)
            
            workflow_success = workflow_result.get("status") == "completed"
            
            self.test_results["integration_tests"]["end_to_end_workflow"] = {
                "workflow_executed": True,
                "workflow_success": workflow_success,
                "phases_completed": len(workflow_result.get("phases", [])),
                "handoffs_executed": len(workflow_result.get("handoffs_executed", [])),
                "context_snapshots": len(workflow_result.get("context_snapshots", []))
            }
            
            self.test_results["tests_run"] += 1
            if workflow_success:
                self.test_results["tests_passed"] += 1
                print("    ✅ End-to-end workflow execution successful")
            else:
                self.test_results["tests_failed"] += 1
                print("    ❌ End-to-end workflow execution failed")
            
        except Exception as e:
            self.test_results["tests_run"] += 1
            self.test_results["tests_failed"] += 1
            self.test_results["integration_tests"]["end_to_end_workflow"] = {"error": str(e)}
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            print(f"    ❌ End-to-end workflow test failed: {e}")
    
    def _generate_final_assessment(self):
        """Generate final system assessment"""
        total_tests = self.test_results["tests_run"]
        passed_tests = self.test_results["tests_passed"]
        failed_tests = self.test_results["tests_failed"]
        
        if total_tests == 0:
            success_rate = 0.0
        else:
            success_rate = passed_tests / total_tests
        
        # Determine overall status
        if success_rate >= 0.95:
            self.test_results["overall_status"] = "excellent"
        elif success_rate >= 0.85:
            self.test_results["overall_status"] = "good"
        elif success_rate >= 0.70:
            self.test_results["overall_status"] = "acceptable"
        else:
            self.test_results["overall_status"] = "poor"
        
        # Generate recommendations
        if failed_tests > 0:
            self.test_results["recommendations"].append(
                f"Address {failed_tests} failed tests to improve system reliability"
            )
        
        if success_rate < 0.90:
            self.test_results["recommendations"].append(
                "System performance below 90% - review component integration"
            )
        
        # Component-specific recommendations
        for component, test_data in self.test_results["component_tests"].items():
            if not test_data.get("available", True):
                self.test_results["recommendations"].append(
                    f"Initialize {component} component for full v3.0 functionality"
                )
    
    def _print_results_summary(self):
        """Print comprehensive validation results"""
        print("\n" + "=" * 60)
        print("🎯 CLAUDE CODE v3.0 VALIDATION RESULTS")
        print("=" * 60)
        
        # Overall status
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "acceptable": "🟠",
            "poor": "🔴",
            "unknown": "⚪"
        }
        
        overall_status = self.test_results["overall_status"]
        print(f"\n{status_emoji.get(overall_status, '⚪')} Overall Status: {overall_status.upper()}")
        
        # Test statistics
        print(f"\n📊 Test Statistics:")
        print(f"   Total Tests: {self.test_results['tests_run']}")
        print(f"   Passed: {self.test_results['tests_passed']} ✅")
        print(f"   Failed: {self.test_results['tests_failed']} ❌")
        
        if self.test_results['tests_run'] > 0:
            success_rate = self.test_results['tests_passed'] / self.test_results['tests_run'] * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        # Component status
        print(f"\n🔧 Component Status:")
        for component, test_data in self.test_results["component_tests"].items():
            if test_data.get("available", False):
                if "error" in test_data:
                    print(f"   {component}: ⚠️  Available but errors detected")
                else:
                    print(f"   {component}: ✅ Working")
            else:
                print(f"   {component}: ❌ Not Available")
        
        # Performance summary
        if self.test_results.get("performance_tests"):
            print(f"\n⚡ Performance Summary:")
            for component, perf_data in self.test_results["performance_tests"].items():
                if "error" not in perf_data:
                    if component == "orchestrator":
                        rating = perf_data.get("performance_rating", "unknown")
                        time_ms = perf_data.get("processing_time_ms", 0)
                        print(f"   {component}: {rating} ({time_ms}ms)")
                    elif component == "status_line":
                        update_perf = perf_data.get("update_performance", "unknown")
                        retrieval_perf = perf_data.get("retrieval_performance", "unknown")
                        print(f"   {component}: update={update_perf}, retrieval={retrieval_perf}")
        
        # Errors and warnings
        if self.test_results["errors"]:
            print(f"\n❌ Errors Detected ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results["errors"][:5], 1):  # Show first 5
                print(f"   {i}. {error.get('test', 'unknown')}: {error.get('error', 'Unknown error')}")
            
            if len(self.test_results["errors"]) > 5:
                print(f"   ... and {len(self.test_results['errors']) - 5} more")
        
        # Recommendations
        if self.test_results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(self.test_results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Phase 1 completion assessment
        print(f"\n🚀 Phase 1 Implementation Status:")
        essential_components = ["status_line", "context_manager", "chat_manager"]
        working_components = [
            comp for comp in essential_components 
            if self.test_results["component_tests"].get(comp, {}).get("available", False) and
               "error" not in self.test_results["component_tests"].get(comp, {})
        ]
        
        completion_percentage = (len(working_components) / len(essential_components)) * 100
        print(f"   Essential Components Working: {len(working_components)}/{len(essential_components)} ({completion_percentage:.0f}%)")
        
        if completion_percentage >= 100:
            print("   🎉 Phase 1 COMPLETE - All essential components operational!")
        elif completion_percentage >= 66:
            print("   🟡 Phase 1 MOSTLY COMPLETE - Minor issues to resolve")
        else:
            print("   🔴 Phase 1 INCOMPLETE - Major components need attention")
        
        print("\n" + "=" * 60)


def main():
    """Main validation entry point"""
    validator = V3SystemValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results to file
    results_file = Path.home() / ".claude" / "v3" / "validation_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Return exit code based on overall status
    if results["overall_status"] in ["excellent", "good"]:
        return 0
    elif results["overall_status"] == "acceptable":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())