#!/usr/bin/env python3
"""
V3.0 System Integration Test
Comprehensive test of all V3 components and features
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class V3SystemTest:
    """Complete V3 system testing"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0",
            "tests": {},
            "summary": {}
        }
        self.test_count = 0
        self.passed_count = 0
    
    def run_test(self, name: str, test_func) -> bool:
        """Run a single test"""
        self.test_count += 1
        print(f"\n[{self.test_count}] Testing {name}...")
        
        try:
            result = test_func()
            if result:
                self.passed_count += 1
                self.results["tests"][name] = "PASSED"
                print(f"    [PASS] {name}")
                return True
            else:
                self.results["tests"][name] = "FAILED"
                print(f"    [FAIL] {name}")
                return False
        except Exception as e:
            self.results["tests"][name] = f"ERROR: {str(e)}"
            print(f"    [ERROR] {name}: {e}")
            return False
    
    def test_status_line(self) -> bool:
        """Test Status Line Manager"""
        try:
            from status_line_manager import StatusLineManager
            manager = StatusLineManager()
            
            # Test all components
            status = manager.status
            assert "model" in status
            assert "git" in status
            assert "phase" in status
            assert "tokens" in status
            assert "performance" in status
            assert "chat_health" in status
            
            # Test status line generation
            line = manager.get_status_line()
            assert len(line) > 0
            
            # Test database logging
            manager.log_to_database()
            
            manager.shutdown()
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_context_manager(self) -> bool:
        """Test Context Manager"""
        try:
            from context_manager import ContextManager
            manager = ContextManager()
            
            # Test token management
            manager.update_token_count(50000)
            assert manager.get_token_percentage() == 50.0
            
            # Test depth tracking
            manager.increment_depth()
            assert manager.context["depth"] == 2
            
            # Test handoff template
            template = manager.generate_handoff_template()
            assert "session_id" in template
            assert "phase" in template
            
            # Test phase transition
            manager.transition_phase("design")
            assert manager.context["phase"] == "design"
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_chat_manager(self) -> bool:
        """Test Chat Manager"""
        try:
            from chat_manager_v3 import ChatManager
            manager = ChatManager()
            
            # Test message handling
            manager.add_message("user", "Test message")
            assert manager.chat_state["depth"] == 1
            
            # Test health assessment
            health = manager.get_chat_health()
            assert health["status"] in ["good", "warning", "critical"]
            
            # Test handoff documentation
            doc = manager.generate_handoff_documentation()
            assert "Chat Handoff Documentation" in doc
            
            # Test summary
            summary = manager.get_summary()
            assert "chat_id" in summary
            assert "phase" in summary
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_smart_orchestrator(self) -> bool:
        """Test Smart Orchestrator"""
        try:
            from smart_orchestrator import SmartOrchestrator
            orchestrator = SmartOrchestrator()
            
            # Test request analysis
            analysis = orchestrator.analyze_request("Build a React app with authentication")
            assert "intent" in analysis
            assert "domains" in analysis
            assert "complexity" in analysis
            
            # Test agent selection
            selected = orchestrator.select_agents(analysis, {"phase": "implementation"})
            assert len(selected) > 0
            
            # Test execution plan
            plan = orchestrator.create_execution_plan(selected, analysis)
            assert "agents" in plan
            assert "execution_groups" in plan
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_parallel_execution(self) -> bool:
        """Test Parallel Execution Engine"""
        try:
            from parallel_execution_engine import ParallelExecutionEngine
            engine = ParallelExecutionEngine()
            
            # Test execution plan creation
            agents = ["business-analyst", "technical-cto", "frontend-architecture"]
            plan = engine.create_execution_plan(agents)
            assert len(plan) > 0
            
            # Test parallel group execution
            results = engine.execute_parallel_group(agents[:2], {"test": True})
            assert len(results) == 2
            
            # Test execution status
            status = engine.get_execution_status()
            assert "max_workers" in status
            assert "resource_locks" in status
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_audio_v3(self) -> bool:
        """Test Audio Player V3"""
        try:
            from audio_player_v3 import AudioPlayerV3
            player = AudioPlayerV3()
            
            # Test configuration
            assert isinstance(player.config, dict)
            
            # Test context retrieval
            context = player.get_current_context()
            assert "phase" in context
            
            # Test sound selection (don't play)
            sound = player.select_sound("Task", context)
            # Sound may be None if no audio files exist
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_agent_enhancer(self) -> bool:
        """Test Agent Enhancer"""
        try:
            from agent_enhancer_v3 import AgentEnhancerV3
            enhancer = AgentEnhancerV3()
            
            # Test agent-specific enhancements
            enhancements = enhancer.get_specific_enhancements("master-orchestrator")
            assert len(enhancements) > 0
            
            # Test priority calculation
            priority = enhancer.get_agent_priority("prompt-engineer")
            assert priority == 1
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_slash_commands(self) -> bool:
        """Test V3 Slash Commands"""
        try:
            from slash_command_router import parse_slash_command, COMMAND_MAPPINGS
            
            # Test V3 command parsing
            command, params = parse_slash_command("/v3-status check all")
            assert command == "/v3-status"
            assert params == "check all"
            
            # Test V3 commands exist
            v3_commands = ["/v3-status", "/v3-handoff", "/v3-parallel", "/v3-smart-build", "/v3-test"]
            for cmd in v3_commands:
                assert cmd in COMMAND_MAPPINGS
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_settings_integration(self) -> bool:
        """Test Settings.json V3 Integration"""
        try:
            settings_file = Path.home() / ".claude" / "settings.json"
            if settings_file.exists():
                settings = json.loads(settings_file.read_text())
                
                # Check V3 features
                assert "v3Features" in settings
                assert "statusLine" in settings["v3Features"]
                assert "contextManager" in settings["v3Features"]
                assert "smartOrchestrator" in settings["v3Features"]
                
                return True
            else:
                print("      Settings file not found")
                return False
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_component_integration(self) -> bool:
        """Test Component Integration"""
        try:
            # Import all V3 components
            from status_line_manager import StatusLineManager
            from context_manager import ContextManager
            from chat_manager_v3 import ChatManager
            from smart_orchestrator import SmartOrchestrator
            from parallel_execution_engine import ParallelExecutionEngine
            
            # Create instances
            status_mgr = StatusLineManager()
            context_mgr = ContextManager()
            chat_mgr = ChatManager()
            orchestrator = SmartOrchestrator()
            engine = ParallelExecutionEngine()
            
            # Test data flow between components
            # Status -> Context
            status = status_mgr.status
            context_mgr.context["phase"] = status["phase"]
            
            # Context -> Chat
            chat_mgr.chat_state["tokens"] = context_mgr.context["tokens"]
            
            # Orchestrator -> Engine
            agents = ["business-analyst", "technical-cto"]
            orch_result = orchestrator.execute_orchestration("test request")
            engine_plan = engine.create_execution_plan(agents)
            
            # Verify integration
            assert len(engine_plan) > 0
            assert orch_result["success"]
            
            # Cleanup
            status_mgr.shutdown()
            
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test Performance Metrics"""
        try:
            import time
            from status_line_manager import StatusLineManager
            
            manager = StatusLineManager()
            
            # Test update speed
            start = time.time()
            for _ in range(10):
                manager.update_status()
            elapsed = time.time() - start
            
            # Should complete 10 updates in under 2 seconds
            assert elapsed < 2.0
            
            manager.shutdown()
            return True
        except Exception as e:
            print(f"      Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all V3 system tests"""
        print("=" * 70)
        print("CLAUDE CODE V3.0 - COMPREHENSIVE SYSTEM TEST")
        print("=" * 70)
        
        # Phase 1 Components
        print("\n## PHASE 1: Core Intelligence Components")
        self.run_test("Status Line Manager", self.test_status_line)
        self.run_test("Context Manager", self.test_context_manager)
        self.run_test("Chat Manager", self.test_chat_manager)
        self.run_test("Smart Orchestrator", self.test_smart_orchestrator)
        
        # Phase 2 Components
        print("\n## PHASE 2: Smart Orchestration")
        self.run_test("Parallel Execution Engine", self.test_parallel_execution)
        self.run_test("Agent Enhancer", self.test_agent_enhancer)
        
        # Phase 3 Components
        print("\n## PHASE 3: Enhanced User Experience")
        self.run_test("Audio Player V3", self.test_audio_v3)
        self.run_test("Slash Commands V3", self.test_slash_commands)
        
        # Integration Tests
        print("\n## INTEGRATION TESTS")
        self.run_test("Settings Integration", self.test_settings_integration)
        self.run_test("Component Integration", self.test_component_integration)
        self.run_test("Performance Metrics", self.test_performance)
        
        # Summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        percentage = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        
        self.results["summary"] = {
            "total_tests": self.test_count,
            "passed": self.passed_count,
            "failed": self.test_count - self.passed_count,
            "success_rate": percentage
        }
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_count}")
        print(f"Failed: {self.test_count - self.passed_count}")
        print(f"Success Rate: {percentage:.1f}%")
        
        if percentage == 100:
            print("\n[SUCCESS] V3.0 SYSTEM FULLY OPERATIONAL!")
            print("All components tested and verified.")
        elif percentage >= 80:
            print("\n[MOSTLY COMPLETE] V3.0 System is mostly operational")
            print("Some components need attention.")
        elif percentage >= 60:
            print("\n[PARTIAL] V3.0 System partially operational")
            print("Several components need fixes.")
        else:
            print("\n[NEEDS WORK] V3.0 System needs significant work")
            print("Many components are not functioning properly.")
        
        # Save results
        results_file = self.home_dir / "v3" / "system_test_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        results_file.write_text(json.dumps(self.results, indent=2))
        print(f"\nDetailed results saved to: {results_file}")

def main():
    """Main test execution"""
    tester = V3SystemTest()
    tester.run_all_tests()
    
    # Return exit code based on success rate
    if tester.results["summary"]["success_rate"] >= 80:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())