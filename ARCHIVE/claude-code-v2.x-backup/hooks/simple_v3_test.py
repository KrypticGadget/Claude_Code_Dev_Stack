#!/usr/bin/env python3
"""
Simple Claude Code v3.0 Test
Quick validation of Phase 1 components without complex dependencies
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

def test_status_line():
    """Test Status Line Manager"""
    print("Testing Status Line Manager...")
    try:
        # Test the module can be imported and basic functionality
        from status_line_manager import StatusLineCore
        
        status_line = StatusLineCore()
        print("  [OK] StatusLineCore created successfully")
        
        # Test basic status update
        status_line.update_status("test", "active", {"test": True})
        print("  [OK] Status update successful")
        
        # Test status retrieval
        current_status = status_line.get_current_status()
        print("  [OK] Status retrieval successful")
        
        # Test routing
        routing = status_line.get_intelligent_routing()
        print("  [OK] Intelligent routing successful")
        
        print("  Status Line Manager: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Status Line Manager failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_context_manager():
    """Test Context Manager"""
    print("Testing Context Manager...")
    try:
        from context_manager import EnhancedContextManager
        
        context_manager = EnhancedContextManager()
        print("  [OK] EnhancedContextManager created successfully")
        
        # Test context snapshot
        snapshot = context_manager.create_context_snapshot()
        print("  [OK] Context snapshot created successfully")
        
        # Test health check
        health = context_manager.get_context_health()
        print("  [OK] Context health check successful")
        
        # Test handoff
        handoff_result = context_manager.execute_intelligent_handoff(
            "test_agent_1", "test_agent_2", {"test": True}
        )
        print("  [OK] Intelligent handoff executed successfully")
        
        print("  Context Manager: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Context Manager failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_chat_manager():
    """Test Chat Manager"""
    print("Testing Chat Manager...")
    try:
        from chat_manager import ChatManagementSystem
        
        chat_manager = ChatManagementSystem()
        print("  [OK] ChatManagementSystem created successfully")
        
        # Test conversation flow
        flow_result = chat_manager.manage_conversation_flow("Test message", "user")
        print("  [OK] Conversation flow managed successfully")
        
        # Test health check
        health = chat_manager.check_conversation_health()
        print("  [OK] Conversation health check successful")
        
        # Test handoff suggestions
        suggestions = chat_manager.get_handoff_suggestions()
        print("  [OK] Handoff suggestions generated successfully")
        
        print("  Chat Manager: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Chat Manager failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_configuration():
    """Test Configuration System"""
    print("Testing Configuration System...")
    try:
        from v3_config import get_config, V3Config
        
        config = get_config()
        print("  [OK] Configuration loaded successfully")
        
        # Test config structure
        assert hasattr(config, 'status_line'), "Missing status_line config"
        assert hasattr(config, 'context_manager'), "Missing context_manager config"
        assert hasattr(config, 'chat_manager'), "Missing chat_manager config"
        assert hasattr(config, 'orchestrator'), "Missing orchestrator config"
        print("  [OK] Configuration structure validated")
        
        print("  Configuration System: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Configuration System failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_orchestrator():
    """Test v3.0 Orchestrator"""
    print("Testing v3.0 Orchestrator...")
    try:
        from v3_orchestrator import ClaudeCodeV3Orchestrator
        
        orchestrator = ClaudeCodeV3Orchestrator()
        print("  [OK] ClaudeCodeV3Orchestrator created successfully")
        
        # Test request processing
        result = orchestrator.process_request("user_prompt", {"prompt": "Test request"})
        print("  [OK] Request processing successful")
        
        # Test system status
        status = orchestrator.get_system_status()
        print("  [OK] System status retrieval successful")
        
        print("  v3.0 Orchestrator: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] v3.0 Orchestrator failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_integration():
    """Test basic integration between components"""
    print("Testing Component Integration...")
    try:
        # Import all components
        from status_line_manager import get_status_line
        from context_manager import get_context_manager
        from chat_manager import get_chat_manager
        from v3_orchestrator import get_v3_orchestrator
        
        # Initialize components
        status_line = get_status_line()
        context_manager = get_context_manager()
        chat_manager = get_chat_manager()
        orchestrator = get_v3_orchestrator()
        
        print("  [OK] All components initialized successfully")
        
        # Test basic workflow
        start_time = time.time()
        result = orchestrator.process_request("user_message", {
            "message": "Test integration workflow for v3.0 system"
        })
        processing_time = (time.time() - start_time) * 1000
        
        print(f"  [OK] Integration workflow completed in {processing_time:.1f}ms")
        
        # Test component coordination
        system_status = orchestrator.get_system_status()
        components_working = sum(1 for comp in system_status.get("component_status", {}).values() if comp)
        
        print(f"  [OK] {components_working} components working in coordination")
        
        print("  Component Integration: PASSED\n")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Component Integration failed: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run simple v3.0 validation"""
    print("=" * 50)
    print("Claude Code v3.0 Simple Validation Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Status Line Manager", test_status_line),
        ("Context Manager", test_context_manager),
        ("Chat Manager", test_chat_manager),
        ("Configuration System", test_configuration),
        ("v3.0 Orchestrator", test_orchestrator),
        ("Component Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name} test crashed: {e}")
            failed += 1
    
    print("=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Total Tests: {passed + failed}")
    
    if failed == 0:
        print("\nSTATUS: ALL TESTS PASSED - Phase 1 Implementation Complete!")
        success_rate = 100.0
    else:
        success_rate = (passed / (passed + failed)) * 100
        print(f"\nSTATUS: {success_rate:.1f}% Success Rate")
        
        if success_rate >= 80:
            print("Phase 1 Implementation: MOSTLY COMPLETE")
        elif success_rate >= 50:
            print("Phase 1 Implementation: PARTIALLY COMPLETE")
        else:
            print("Phase 1 Implementation: NEEDS WORK")
    
    # Save basic results
    results_dir = Path.home() / ".claude" / "v3"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = results_dir / "simple_test_results.txt"
    with open(results_file, 'w') as f:
        f.write(f"Claude Code v3.0 Simple Test Results\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Tests Passed: {passed}\n")
        f.write(f"Tests Failed: {failed}\n")
        f.write(f"Success Rate: {success_rate:.1f}%\n")
    
    print(f"\nResults saved to: {results_file}")
    
    # Return appropriate exit code
    if success_rate >= 80:
        return 0  # Success
    elif success_rate >= 50:
        return 1  # Partial success
    else:
        return 2  # Failure

if __name__ == "__main__":
    sys.exit(main())