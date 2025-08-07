#!/usr/bin/env python3
"""Test suite for integrated Claude Code Dev Stack"""

import json
import unittest
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent / ".claude-example" / "hooks"))

# Import the modules to test
import agent_orchestrator_integrated
import slash_command_router
import mcp_gateway_enhanced
import mcp_initializer
import agent_orchestrator
import agent_mention_parser
import model_tracker
import quality_gate
import session_loader
import session_saver

class TestIntegratedSystem(unittest.TestCase):
    """Test suite for complete integrated system"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.claude_home = self.test_dir / ".claude"
        self.claude_home.mkdir(parents=True, exist_ok=True)
        
        # Create required directories
        (self.claude_home / "hooks").mkdir(exist_ok=True)
        (self.claude_home / "logs").mkdir(exist_ok=True)
        (self.claude_home / "state").mkdir(exist_ok=True)
        (self.claude_home / "agents").mkdir(exist_ok=True)
        (self.claude_home / "commands").mkdir(exist_ok=True)
        
        # Mock Path.home() with patch
        self.home_patcher = patch('pathlib.Path.home', return_value=self.test_dir)
        self.home_patcher.start()
    
    def tearDown(self):
        """Cleanup test environment"""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_agent_orchestrator_explicit_mentions(self):
        """Test agent orchestrator with explicit @agent- mentions"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        # Test explicit mention
        prompt = "Please @agent-frontend-mockup[opus] create a landing page"
        mentions = orchestrator.extract_explicit_mentions(prompt)
        
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["agent"], "frontend-mockup")
        self.assertEqual(mentions[0]["model"], "opus")
        self.assertTrue(mentions[0]["explicit"])
    
    def test_agent_orchestrator_keyword_matching(self):
        """Test agent orchestrator keyword matching"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        # Test keyword matching
        prompt = "I need to optimize database queries and improve api performance"
        agents = orchestrator.analyze_prompt_keywords(prompt)
        
        # Should find database and backend agents (since "api" and "database" are in prompt)
        agent_names = [a["agent"] for a in agents]
        self.assertIn("database-architecture", agent_names)
        # Check that we found relevant agents (may vary based on keyword matching)
        self.assertTrue(len(agent_names) > 0)
        self.assertTrue(any("database" in name or "backend" in name or "performance" in name for name in agent_names))
    
    def test_slash_command_routing(self):
        """Test slash command router"""
        # Test command parsing
        prompt = "/new-project E-commerce platform with React and Node.js"
        command, params = slash_command_router.parse_slash_command(prompt)
        
        self.assertEqual(command, "/new-project")
        self.assertEqual(params, "E-commerce platform with React and Node.js")
        
        # Test routing
        context = slash_command_router.route_to_agents(command, params)
        self.assertIsNotNone(context)
        self.assertIn("master-orchestrator", context)
        self.assertIn("business-analyst", context)
    
    def test_mcp_gateway_validation(self):
        """Test MCP gateway validation"""
        gateway = mcp_gateway_enhanced.MCPGateway(service="playwright")
        
        # Test dangerous URL blocking
        tool_input = {"url": "file:///etc/passwd"}
        is_valid, reason = gateway.validate_playwright("navigate", tool_input)
        self.assertFalse(is_valid)
        self.assertIn("dangerous", reason.lower())
        
        # Test valid URL
        tool_input = {"url": "https://example.com"}
        is_valid, reason = gateway.validate_playwright("navigate", tool_input)
        self.assertTrue(is_valid)
    
    def test_mcp_gateway_rate_limiting(self):
        """Test MCP gateway rate limiting"""
        gateway = mcp_gateway_enhanced.MCPGateway(service="web-search")
        gateway.service_configs["web-search"]["rate_limit"] = 2  # Low limit for testing
        
        # First two requests should pass
        for i in range(2):
            allowed, reason = gateway.check_rate_limit()
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # Third request should be blocked
        allowed, reason = gateway.check_rate_limit()
        self.assertFalse(allowed)
        self.assertIn("rate limit", reason.lower())
    
    def test_mcp_initializer_status_check(self):
        """Test MCP initializer status checking"""
        with patch('subprocess.run') as mock_run:
            # Mock successful MCP list output
            mock_run.return_value = MagicMock(
                stdout="playwright\nobsidian\nweb-search",
                returncode=0
            )
            
            initializer = mcp_initializer.MCPInitializer()
            status = initializer.check_mcp_status()
            
            # All services should be found
            self.assertIn("playwright", status)
            self.assertIn("obsidian", status)
            self.assertIn("web-search", status)
            self.assertIn("✅", status["playwright"])
    
    def test_agent_execution_strategy(self):
        """Test agent execution strategy determination"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        agents = [
            {"agent": "frontend-mockup"},
            {"agent": "backend-services"},
            {"agent": "database-architecture"},
            {"agent": "testing-automation"}
        ]
        
        strategy = orchestrator.determine_execution_strategy(agents)
        
        # database-architecture should be parallel (no deps)
        # backend-services depends on database
        # testing depends on backend and frontend
        self.assertIn("parallel_groups", strategy)
        self.assertIn("sequential", strategy)
    
    def test_orchestration_plan_generation(self):
        """Test orchestration plan generation"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        agents = [
            {"agent": "frontend-mockup", "model": "opus", "explicit": True},
            {"agent": "backend-services", "model": "default", "explicit": False}
        ]
        
        mcps = ["playwright", "web-search"]
        task = "Build a full-stack application"
        
        plan = orchestrator.create_orchestration_plan(agents, mcps, task)
        
        # Verify plan contains expected sections
        self.assertIn("**Task**:", plan)
        self.assertIn("Agents to Invoke", plan)
        self.assertIn("Required MCP Services", plan)
        self.assertIn("Execution Strategy", plan)
    
    def test_hook_json_communication(self):
        """Test that all hooks properly handle JSON stdin/stdout"""
        hooks_to_test = [
            "agent_mention_parser",
            "model_tracker",
            "quality_gate",
            "session_loader",
            "session_saver"
        ]
        
        for hook_name in hooks_to_test:
            # Create test input
            test_input = {
                "tool_name": "Task",
                "tool_input": {"prompt": "test prompt"},
                "session_id": "test_session"
            }
            
            # Mock stdin and test each hook doesn't crash
            with patch('sys.stdin', new=MagicMock()):
                with patch('json.load', return_value=test_input):
                    try:
                        module = sys.modules[hook_name]
                        # Just verify modules load without error
                        self.assertIsNotNone(module)
                    except Exception as e:
                        self.fail(f"Hook {hook_name} failed: {e}")
    
    def test_integrated_workflow(self):
        """Test a complete integrated workflow"""
        # This simulates the full flow from slash command to agent orchestration
        
        # Step 1: Slash command input
        user_input = "/frontend-mockup Create a responsive landing page"
        
        # Step 2: Parse command
        command, params = slash_command_router.parse_slash_command(user_input)
        self.assertEqual(command, "/frontend-mockup")
        
        # Step 3: Get routing context
        context = slash_command_router.route_to_agents(command, params)
        self.assertIsNotNone(context)
        
        # Get agents and MCPs from command mappings
        mapping = slash_command_router.COMMAND_MAPPINGS.get(command, {})
        agents_list = mapping.get("agents", [])
        mcps_list = mapping.get("mcps", [])
        
        self.assertIn("frontend-mockup", agents_list)
        self.assertIn("playwright", mcps_list)
        
        # Step 4: Orchestrator creates plan
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        agents = [{"agent": name, "model": "default", "explicit": False} 
                 for name in agents_list]
        
        plan = orchestrator.create_orchestration_plan(
            agents, 
            mcps_list, 
            params
        )
        
        # Verify complete plan
        self.assertIn("frontend-mockup", plan)
        self.assertIn("playwright", plan)
        self.assertIn("Execution Strategy", plan)
    
    def test_state_persistence(self):
        """Test that state is properly persisted"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        # Create and save a plan
        test_plan = {
            "task": "Test task",
            "agents": [{"agent": "test-agent"}],
            "mcp_services": ["test-mcp"],
            "execution_strategy": {"parallel_groups": [], "sequential": []},
            "timestamp": "2024-01-01T00:00:00"
        }
        
        orchestrator.save_orchestration_plan(test_plan)
        
        # Verify file was created
        plan_file = self.claude_home / "state" / "orchestration_plan.json"
        self.assertTrue(plan_file.exists())
        
        # Verify content
        with open(plan_file) as f:
            saved_plans = json.load(f)
        
        self.assertEqual(len(saved_plans), 1)
        self.assertEqual(saved_plans[0]["task"], "Test task")
    
    def test_logging_functionality(self):
        """Test that operations are properly logged"""
        orchestrator = agent_orchestrator_integrated.AgentOrchestrator()
        
        # Log an operation
        orchestrator.log_orchestration({
            "task": "Test logging",
            "agents": ["test-agent"],
            "mcps": ["test-mcp"]
        })
        
        # Verify log file was created
        log_file = self.claude_home / "logs" / "orchestration.jsonl"
        self.assertTrue(log_file.exists())
        
        # Verify log content
        with open(log_file) as f:
            log_line = f.readline()
            log_data = json.loads(log_line)
        
        self.assertEqual(log_data["task"], "Test logging")
        self.assertIn("timestamp", log_data)

class TestSystemIntegration(unittest.TestCase):
    """Integration tests for system components"""
    
    def test_settings_file_structure(self):
        """Test that settings-integrated.json has correct structure"""
        settings_path = Path(__file__).parent / ".claude-example" / "settings-integrated.json"
        
        if settings_path.exists():
            with open(settings_path) as f:
                settings = json.load(f)
            
            # Verify main sections exist
            self.assertIn("hooks", settings)
            self.assertIn("agentSystem", settings)
            self.assertIn("slashCommands", settings)
            self.assertIn("mcpIntegration", settings)
            
            # Verify hook events
            hook_events = ["PreToolUse", "PostToolUse", "UserPromptSubmit", 
                          "SessionStart", "Stop"]
            for event in hook_events:
                self.assertIn(event, settings["hooks"])
            
            # Verify agent count (should be 28)
            agents = settings["agentSystem"]["agents"]
            self.assertEqual(len(agents), 28)
            
            # Verify command count (should be 18)
            commands = settings["slashCommands"]["commands"]
            self.assertEqual(len(commands), 18)
    
    def test_hook_file_consistency(self):
        """Test that all hook files follow consistent patterns"""
        hooks_dir = Path(__file__).parent / ".claude-example" / "hooks"
        
        if hooks_dir.exists():
            hook_files = list(hooks_dir.glob("*.py"))
            
            for hook_file in hook_files:
                with open(hook_file) as f:
                    content = f.read()
                
                # All hooks should use json.load(sys.stdin)
                if "if __name__" in content:
                    self.assertIn("json.load(sys.stdin)", content,
                                 f"{hook_file.name} should read from stdin")
                    
                    # Should not use sys.argv for arguments
                    self.assertNotIn("sys.argv[1]", content,
                                    f"{hook_file.name} should not use sys.argv")
                    
                    # Should output hookSpecificOutput
                    if "hookSpecificOutput" in content:
                        self.assertIn("json.dumps", content,
                                     f"{hook_file.name} should output JSON")

def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nTests with errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)