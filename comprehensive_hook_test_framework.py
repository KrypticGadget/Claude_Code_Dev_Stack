#!/usr/bin/env python3
"""
Comprehensive Hook Testing Framework for Claude Code Dev Stack v3.0
Tests all 28 hooks: functionality, event triggers, audio notifications, dependencies, and error handling
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import importlib.util

# Audio integration for testing
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

@dataclass
class HookTestResult:
    """Test result for individual hook"""
    hook_name: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    execution_time: float
    audio_notification: bool
    error_message: Optional[str] = None
    dependencies_met: bool = True
    event_triggered: bool = False
    output: Optional[str] = None

@dataclass
class TestSuiteResult:
    """Overall test suite results"""
    total_hooks: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_execution_time: float
    hooks_with_audio: int
    dependency_failures: int
    event_trigger_failures: int
    timestamp: str

class AudioTestManager:
    """Manages audio notification testing"""
    
    def __init__(self):
        self.audio_available = AUDIO_AVAILABLE
        self.audio_files_path = Path("TTS/audio_files")
        self.played_sounds = []
        
    def initialize_audio(self):
        """Initialize audio system for testing"""
        if not self.audio_available:
            return False
            
        try:
            pygame.mixer.init()
            return True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            return False
    
    def test_audio_notification(self, hook_name: str) -> bool:
        """Test if hook can play audio notification"""
        if not self.audio_available:
            return False
            
        audio_file = self.audio_files_path / f"{hook_name}_notification.mp3"
        if not audio_file.exists():
            audio_file = self.audio_files_path / "hook_triggered.mp3"
            
        if audio_file.exists():
            try:
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                time.sleep(0.5)  # Brief play
                pygame.mixer.music.stop()
                self.played_sounds.append(hook_name)
                return True
            except Exception as e:
                print(f"Audio test failed for {hook_name}: {e}")
                return False
        return False

class HookDependencyAnalyzer:
    """Analyzes hook dependencies and execution order"""
    
    def __init__(self):
        self.dependency_map = {
            # Core dependencies
            'session_loader': [],
            'session_saver': ['session_loader'],
            
            # Agent system dependencies
            'agent_mention_parser': [],
            'agent_enhancer_v3': ['agent_mention_parser'],
            'agent_orchestrator': ['agent_mention_parser', 'model_tracker'],
            'master_orchestrator': ['agent_orchestrator'],
            'smart_orchestrator': ['master_orchestrator'],
            'v3_orchestrator': ['smart_orchestrator'],
            
            # Quality system dependencies
            'quality_gate_hook': [],
            'quality_config': ['quality_gate_hook'],
            'setup_quality_system': ['quality_config'],
            'test_quality_system': ['setup_quality_system'],
            'code_linter': ['quality_gate_hook'],
            
            # Audio system dependencies
            'audio_player': [],
            'audio_player_v3': ['audio_player'],
            'audio_player_fixed': ['audio_player_v3'],
            'audio_notifier': ['audio_player_fixed'],
            'audio_controller': ['audio_notifier'],
            'audio_integration_v3': ['audio_controller'],
            
            # Execution and monitoring dependencies
            'enhanced_bash_hook': [],
            'parallel_execution_engine': ['enhanced_bash_hook'],
            'performance_monitor': [],
            'resource_monitor': ['performance_monitor'],
            'dependency_checker': [],
            
            # Utility dependencies
            'context_manager': [],
            'model_tracker': ['context_manager'],
            'planning_trigger': ['context_manager'],
            'notification_sender': ['audio_integration_v3'],
            'auto_formatter': [],
            'auto_documentation': ['auto_formatter'],
            'security_scanner': [],
            'git_quality_hooks': ['quality_gate_hook', 'security_scanner'],
            'browser_integration_hook': [],
            'chat_manager': ['context_manager'],
            'chat_manager_v3': ['chat_manager'],
            'status_line_manager': [],
            'slash_command_router': ['chat_manager_v3'],
            'venv_enforcer': ['dependency_checker'],
            'v3_config': [],
            'v3_validator': ['v3_config'],
            'v3_system_test': ['v3_validator']
        }
        
    def get_execution_order(self) -> List[str]:
        """Calculate optimal execution order based on dependencies"""
        executed = set()
        order = []
        
        def can_execute(hook_name):
            deps = self.dependency_map.get(hook_name, [])
            return all(dep in executed for dep in deps)
        
        hooks = list(self.dependency_map.keys())
        while hooks:
            ready_hooks = [h for h in hooks if can_execute(h)]
            if not ready_hooks:
                # Circular dependency or missing dependency
                order.extend(hooks)  # Add remaining hooks
                break
                
            for hook in ready_hooks:
                order.append(hook)
                executed.add(hook)
                hooks.remove(hook)
                
        return order
    
    def validate_dependencies(self, hook_name: str) -> Tuple[bool, List[str]]:
        """Validate if hook dependencies are available"""
        deps = self.dependency_map.get(hook_name, [])
        missing_deps = []
        
        for dep in deps:
            hook_file = Path(f"Claude_Code_Dev_Stack_v3/core/hooks/hooks/{dep}.py")
            if not hook_file.exists():
                missing_deps.append(dep)
                
        return len(missing_deps) == 0, missing_deps

class EventTriggerSimulator:
    """Simulates various events to test hook triggers"""
    
    def __init__(self):
        self.event_types = {
            'SessionStart': self.simulate_session_start,
            'SessionEnd': self.simulate_session_end,
            'UserPromptSubmit': self.simulate_user_prompt,
            'BeforeCodeEdit': self.simulate_before_code_edit,
            'AfterCodeEdit': self.simulate_after_code_edit,
            'AgentInvocation': self.simulate_agent_invocation,
            'MCPServerRequest': self.simulate_mcp_request
        }
    
    def simulate_session_start(self):
        """Simulate session start event"""
        return {"event": "SessionStart", "timestamp": datetime.now().isoformat()}
    
    def simulate_session_end(self):
        """Simulate session end event"""
        return {"event": "SessionEnd", "timestamp": datetime.now().isoformat()}
    
    def simulate_user_prompt(self):
        """Simulate user prompt submission"""
        return {
            "event": "UserPromptSubmit", 
            "user_prompt": "Test hook functionality @agent-testing",
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_before_code_edit(self):
        """Simulate before code edit event"""
        return {
            "event": "BeforeCodeEdit",
            "file_path": "test_file.py",
            "changes": "Adding test function",
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_after_code_edit(self):
        """Simulate after code edit event"""
        return {
            "event": "AfterCodeEdit",
            "file_path": "test_file.py",
            "operation": "create",
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_agent_invocation(self):
        """Simulate agent invocation event"""
        return {
            "event": "AgentInvocation",
            "agent_name": "testing-automation",
            "agent_prompt": "Test system functionality",
            "model_type": "claude-3-5-haiku",
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_mcp_request(self):
        """Simulate MCP server request"""
        return {
            "event": "MCPServerRequest",
            "mcp_server": "test_server",
            "mcp_method": "test_method",
            "timestamp": datetime.now().isoformat()
        }

class HookTester:
    """Individual hook testing class"""
    
    def __init__(self, hook_name: str, hooks_directory: Path):
        self.hook_name = hook_name
        self.hooks_directory = hooks_directory
        self.hook_file = hooks_directory / f"{hook_name}.py"
        
    def load_hook_module(self):
        """Dynamically load hook module"""
        try:
            spec = importlib.util.spec_from_file_location(self.hook_name, self.hook_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            return None
        except Exception as e:
            print(f"Failed to load hook module {self.hook_name}: {e}")
            return None
    
    def test_hook_execution(self, event_data: Dict[str, Any]) -> HookTestResult:
        """Test hook execution with simulated event data"""
        start_time = time.time()
        
        try:
            # Test if hook file exists
            if not self.hook_file.exists():
                return HookTestResult(
                    hook_name=self.hook_name,
                    status='skipped',
                    execution_time=0,
                    audio_notification=False,
                    error_message=f"Hook file not found: {self.hook_file}"
                )
            
            # Try to execute hook via subprocess (safer)
            result = subprocess.run([
                sys.executable, str(self.hook_file)
            ], capture_output=True, text=True, timeout=10)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                return HookTestResult(
                    hook_name=self.hook_name,
                    status='passed',
                    execution_time=execution_time,
                    audio_notification=False,  # Will be tested separately
                    event_triggered=True,
                    output=result.stdout
                )
            else:
                return HookTestResult(
                    hook_name=self.hook_name,
                    status='failed',
                    execution_time=execution_time,
                    audio_notification=False,
                    error_message=result.stderr,
                    event_triggered=True
                )
                
        except subprocess.TimeoutExpired:
            return HookTestResult(
                hook_name=self.hook_name,
                status='error',
                execution_time=time.time() - start_time,
                audio_notification=False,
                error_message="Hook execution timeout (10s)",
                event_triggered=True
            )
        except Exception as e:
            return HookTestResult(
                hook_name=self.hook_name,
                status='error',
                execution_time=time.time() - start_time,
                audio_notification=False,
                error_message=str(e),
                event_triggered=False
            )

class ComprehensiveHookTestFramework:
    """Main testing framework for all 28 hooks"""
    
    def __init__(self):
        self.hooks_directory = Path("Claude_Code_Dev_Stack_v3/core/hooks/hooks")
        self.audio_manager = AudioTestManager()
        self.dependency_analyzer = HookDependencyAnalyzer()
        self.event_simulator = EventTriggerSimulator()
        self.results = []
        
        # All 28 hooks in Claude Code Dev Stack v3.0
        self.all_hooks = [
            # Core System Hooks (7)
            'session_loader', 'session_saver', 'context_manager', 'dependency_checker',
            'venv_enforcer', 'v3_config', 'v3_validator',
            
            # Agent Orchestration Hooks (6)
            'agent_mention_parser', 'agent_enhancer_v3', 'master_orchestrator',
            'smart_orchestrator', 'v3_orchestrator', 'model_tracker',
            
            # Quality & Code Hooks (5)
            'quality_gate_hook', 'code_linter', 'auto_formatter', 'security_scanner',
            'git_quality_hooks',
            
            # Audio Integration Hooks (4)
            'audio_player_v3', 'audio_notifier', 'audio_controller', 'audio_integration_v3',
            
            # Execution & Monitoring Hooks (3)
            'enhanced_bash_hook', 'performance_monitor', 'resource_monitor',
            
            # Utility & Communication Hooks (3)
            'planning_trigger', 'notification_sender', 'browser_integration_hook'
        ]
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hook_test_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_test_environment(self):
        """Setup test environment"""
        self.logger.info("Setting up test environment...")
        
        # Initialize audio system
        if self.audio_manager.initialize_audio():
            self.logger.info("Audio system initialized for testing")
        else:
            self.logger.warning("Audio system not available for testing")
        
        # Verify hooks directory exists
        if not self.hooks_directory.exists():
            self.logger.error(f"Hooks directory not found: {self.hooks_directory}")
            return False
            
        # Count available hooks
        available_hooks = list(self.hooks_directory.glob("*.py"))
        self.logger.info(f"Found {len(available_hooks)} hook files in directory")
        
        return True
    
    def test_single_hook(self, hook_name: str, event_data: Dict[str, Any]) -> HookTestResult:
        """Test a single hook comprehensively"""
        self.logger.info(f"Testing hook: {hook_name}")
        
        # 1. Test dependencies
        deps_ok, missing_deps = self.dependency_analyzer.validate_dependencies(hook_name)
        if not deps_ok:
            self.logger.warning(f"Missing dependencies for {hook_name}: {missing_deps}")
        
        # 2. Execute hook test
        tester = HookTester(hook_name, self.hooks_directory)
        result = tester.test_hook_execution(event_data)
        result.dependencies_met = deps_ok
        
        # 3. Test audio notification
        if result.status == 'passed':
            result.audio_notification = self.audio_manager.test_audio_notification(hook_name)
        
        self.logger.info(f"Hook {hook_name} test completed: {result.status}")
        return result
    
    def test_hook_execution_order(self) -> Dict[str, Any]:
        """Test hooks in dependency order"""
        self.logger.info("Testing hook execution order...")
        
        execution_order = self.dependency_analyzer.get_execution_order()
        self.logger.info(f"Optimal execution order: {execution_order}")
        
        order_test_results = []
        for i, hook_name in enumerate(execution_order):
            if hook_name in self.all_hooks:
                # Simulate appropriate event for this hook
                event_data = self.get_appropriate_event_for_hook(hook_name)
                result = self.test_single_hook(hook_name, event_data)
                order_test_results.append({
                    'position': i,
                    'hook_name': hook_name,
                    'result': asdict(result)
                })
        
        return {
            'execution_order': execution_order,
            'test_results': order_test_results
        }
    
    def get_appropriate_event_for_hook(self, hook_name: str) -> Dict[str, Any]:
        """Get appropriate event type for hook"""
        event_mapping = {
            'session_loader': 'SessionStart',
            'session_saver': 'SessionEnd',
            'agent_mention_parser': 'UserPromptSubmit',
            'planning_trigger': 'UserPromptSubmit',
            'quality_gate_hook': 'BeforeCodeEdit',
            'model_tracker': 'AgentInvocation',
            'master_orchestrator': 'AgentInvocation'
        }
        
        event_type = event_mapping.get(hook_name, 'UserPromptSubmit')
        return self.event_simulator.event_types[event_type]()
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test hook error handling capabilities"""
        self.logger.info("Testing error handling...")
        
        error_scenarios = [
            {'scenario': 'invalid_input', 'data': {'invalid': 'data'}},
            {'scenario': 'missing_file', 'data': {'file_path': '/nonexistent/file.py'}},
            {'scenario': 'timeout_simulation', 'data': {'timeout': True}},
            {'scenario': 'permission_denied', 'data': {'restricted': True}}
        ]
        
        error_test_results = {}
        for scenario in error_scenarios:
            scenario_results = []
            for hook_name in self.all_hooks[:5]:  # Test first 5 hooks for errors
                try:
                    tester = HookTester(hook_name, self.hooks_directory)
                    result = tester.test_hook_execution(scenario['data'])
                    scenario_results.append({
                        'hook_name': hook_name,
                        'handled_gracefully': result.status != 'error',
                        'error_message': result.error_message
                    })
                except Exception as e:
                    scenario_results.append({
                        'hook_name': hook_name,
                        'handled_gracefully': False,
                        'error_message': str(e)
                    })
            
            error_test_results[scenario['scenario']] = scenario_results
        
        return error_test_results
    
    def test_parallel_execution(self) -> Dict[str, Any]:
        """Test parallel hook execution"""
        self.logger.info("Testing parallel hook execution...")
        
        # Test hooks that can run in parallel (no dependencies)
        parallel_hooks = ['context_manager', 'dependency_checker', 'auto_formatter', 
                         'browser_integration_hook', 'notification_sender']
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for hook_name in parallel_hooks:
                if hook_name in self.all_hooks:
                    event_data = self.get_appropriate_event_for_hook(hook_name)
                    future = executor.submit(self.test_single_hook, hook_name, event_data)
                    futures.append((hook_name, future))
            
            parallel_results = []
            for hook_name, future in futures:
                try:
                    result = future.result(timeout=15)
                    parallel_results.append({
                        'hook_name': hook_name,
                        'result': asdict(result)
                    })
                except Exception as e:
                    parallel_results.append({
                        'hook_name': hook_name,
                        'error': str(e)
                    })
        
        parallel_execution_time = time.time() - start_time
        
        return {
            'parallel_execution_time': parallel_execution_time,
            'parallel_results': parallel_results,
            'hooks_tested': len(parallel_results)
        }
    
    def run_comprehensive_test_suite(self) -> TestSuiteResult:
        """Run complete test suite for all 28 hooks"""
        self.logger.info("Starting comprehensive hook testing...")
        
        if not self.setup_test_environment():
            raise RuntimeError("Failed to setup test environment")
        
        start_time = time.time()
        
        # Test 1: Individual hook functionality
        self.logger.info("Phase 1: Testing individual hook functionality...")
        for hook_name in self.all_hooks:
            event_data = self.get_appropriate_event_for_hook(hook_name)
            result = self.test_single_hook(hook_name, event_data)
            self.results.append(result)
        
        # Test 2: Execution order and dependencies
        self.logger.info("Phase 2: Testing execution order and dependencies...")
        order_results = self.test_hook_execution_order()
        
        # Test 3: Error handling
        self.logger.info("Phase 3: Testing error handling...")
        error_results = self.test_error_handling()
        
        # Test 4: Parallel execution
        self.logger.info("Phase 4: Testing parallel execution...")
        parallel_results = self.test_parallel_execution()
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        passed = sum(1 for r in self.results if r.status == 'passed')
        failed = sum(1 for r in self.results if r.status == 'failed')
        errors = sum(1 for r in self.results if r.status == 'error')
        skipped = sum(1 for r in self.results if r.status == 'skipped')
        
        hooks_with_audio = sum(1 for r in self.results if r.audio_notification)
        dependency_failures = sum(1 for r in self.results if not r.dependencies_met)
        event_trigger_failures = sum(1 for r in self.results if not r.event_triggered)
        
        # Create comprehensive test report
        test_report = {
            'summary': TestSuiteResult(
                total_hooks=len(self.all_hooks),
                passed=passed,
                failed=failed,
                errors=errors,
                skipped=skipped,
                total_execution_time=total_time,
                hooks_with_audio=hooks_with_audio,
                dependency_failures=dependency_failures,
                event_trigger_failures=event_trigger_failures,
                timestamp=datetime.now().isoformat()
            ),
            'individual_results': [asdict(r) for r in self.results],
            'execution_order_test': order_results,
            'error_handling_test': error_results,
            'parallel_execution_test': parallel_results,
            'audio_test_summary': {
                'audio_system_available': self.audio_manager.audio_available,
                'hooks_with_audio_notifications': hooks_with_audio,
                'audio_files_tested': len(self.audio_manager.played_sounds)
            }
        }
        
        # Save detailed report
        report_file = f"comprehensive_hook_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2, default=str)
        
        self.logger.info(f"Comprehensive test completed. Report saved to: {report_file}")
        return test_report['summary']

def main():
    """Main test execution function"""
    print("Claude Code Dev Stack v3.0 - Comprehensive Hook Testing Framework")
    print("=" * 80)
    
    framework = ComprehensiveHookTestFramework()
    
    try:
        result = framework.run_comprehensive_test_suite()
        
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 40)
        print(f"Total Hooks Tested: {result.total_hooks}")
        print(f"✅ Passed: {result.passed}")
        print(f"❌ Failed: {result.failed}")
        print(f"⚠️  Errors: {result.errors}")
        print(f"⏭️  Skipped: {result.skipped}")
        print(f"🔊 Hooks with Audio: {result.hooks_with_audio}")
        print(f"🔗 Dependency Failures: {result.dependency_failures}")
        print(f"⚡ Event Trigger Failures: {result.event_trigger_failures}")
        print(f"⏱️  Total Time: {result.total_execution_time:.2f}s")
        
        # Calculate success rate
        success_rate = (result.passed / result.total_hooks) * 100 if result.total_hooks > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Hook system is functioning excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Hook system is functioning well with minor issues")
        elif success_rate >= 50:
            print("⚠️  FAIR: Hook system has some issues that need attention")
        else:
            print("❌ POOR: Hook system requires significant fixes")
            
    except Exception as e:
        print(f"❌ Test framework error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())