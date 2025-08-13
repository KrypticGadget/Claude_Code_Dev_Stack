#!/usr/bin/env python3
"""
Test script for Claude Code V3.0 Phase 1 components
Validates status line, context manager, and smart orchestrator
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

def test_component(name, test_func):
    """Test a component and report results"""
    print(f"\nTesting {name}...")
    try:
        result = test_func()
        if result:
            print(f"[PASS] {name}: PASSED")
            return True
        else:
            print(f"[FAIL] {name}: FAILED")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: ERROR - {e}")
        return False

def test_status_line():
    """Test Status Line Manager"""
    try:
        from status_line_manager import StatusLineManager
        manager = StatusLineManager()
        
        # Test status line generation
        status_line = manager.get_status_line()
        assert len(status_line) > 0, "Empty status line"
        
        # Test status update
        manager.update_status()
        
        # Test JSON output
        status = manager.status
        assert "model" in status
        assert "git" in status
        assert "phase" in status
        
        manager.shutdown()
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_context_manager():
    """Test Context Manager"""
    try:
        from context_manager import ContextManager
        manager = ContextManager()
        
        # Test context loading
        context = manager.context
        assert "session_id" in context
        assert "phase" in context
        assert "tokens" in context
        
        # Test token management
        manager.update_token_count(50000)
        percentage = manager.get_token_percentage()
        assert percentage == 50.0, f"Expected 50%, got {percentage}%"
        
        # Test recommendations
        recommendations = manager.get_recommendations()
        assert isinstance(recommendations, list)
        
        # Test health assessment
        health = manager.assess_health()
        assert health in ["good", "warning", "critical"]
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_smart_orchestrator():
    """Test Smart Orchestrator"""
    try:
        from smart_orchestrator import SmartOrchestrator
        orchestrator = SmartOrchestrator()
        
        # Test simple request
        result = orchestrator.execute_orchestration("Create a simple Python script")
        assert result["success"] == True
        assert "selected_agents" in result
        assert "plan" in result
        
        # Test complex request
        result = orchestrator.execute_orchestration(
            "Build a full-stack application with React frontend, Node.js backend, and PostgreSQL database"
        )
        assert result["success"] == True
        assert len(result["selected_agents"]) > 2, "Complex request should select multiple agents"
        
        # Test pattern matching
        analysis = orchestrator.analyze_request("Create a new project with authentication")
        assert analysis["pattern_match"] == "new_project"
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_audio_v3():
    """Test Audio Player V3"""
    try:
        from audio_player_v3 import AudioPlayerV3
        player = AudioPlayerV3()
        
        # Test configuration loading
        assert player.config["enabled"] == True
        
        # Test context retrieval
        context = player.get_current_context()
        assert "model" in context
        assert "phase" in context
        
        # Test sound selection (without playing)
        sound = player.select_sound("Task", context)
        # Sound may be None if audio files don't exist, that's okay
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_integration():
    """Test component integration"""
    try:
        from status_line_manager import StatusLineManager
        from context_manager import ContextManager
        from smart_orchestrator import SmartOrchestrator
        
        # Create instances
        status_mgr = StatusLineManager()
        context_mgr = ContextManager()
        orchestrator = SmartOrchestrator()
        
        # Test data flow
        status = status_mgr.status
        context = orchestrator.get_current_context()
        
        # Verify shared data
        assert context["phase"] == status["phase"]
        
        # Cleanup
        status_mgr.shutdown()
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Run Phase 1 tests"""
    print("=" * 60)
    print("Claude Code V3.0 - Phase 1 Component Tests")
    print("=" * 60)
    
    tests = [
        ("Status Line Manager", test_status_line),
        ("Context Manager", test_context_manager),
        ("Smart Orchestrator", test_smart_orchestrator),
        ("Audio Player V3", test_audio_v3),
        ("Component Integration", test_integration)
    ]
    
    results = []
    for name, test_func in tests:
        results.append(test_component(name, test_func))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("\n[SUCCESS] PHASE 1 COMPLETE: All components operational!")
    elif percentage >= 80:
        print("\n[WARNING] PHASE 1 MOSTLY COMPLETE: Some components need attention")
    else:
        print("\n[FAILURE] PHASE 1 INCOMPLETE: Critical components failing")
    
    # Save results
    results_dir = Path.home() / ".claude" / "v3"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = results_dir / "phase1_test_results.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 1",
        "tests_passed": passed,
        "tests_total": total,
        "percentage": percentage,
        "components": {
            name: "passed" if result else "failed" 
            for (name, _), result in zip(tests, results)
        }
    }
    
    results_file.write_text(json.dumps(results_data, indent=2))
    print(f"\nResults saved to: {results_file}")
    
    return 0 if percentage >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())