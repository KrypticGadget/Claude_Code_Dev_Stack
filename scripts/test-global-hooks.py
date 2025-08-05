#!/usr/bin/env python3
"""
Test Global Hooks System
Tests that hooks work correctly with paths containing spaces and special characters
"""

import os
import sys
import json
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import platform

class HooksTestSuite:
    def __init__(self):
        self.claude_home = Path(os.environ.get('CLAUDE_HOME', '~/.claude')).expanduser()
        self.hooks_dir = self.claude_home / '.claude-global' / 'hooks'
        self.test_results = []
        self.platform = platform.system()
        
    def run_all_tests(self) -> bool:
        """Run all test scenarios"""
        print("🧪 Claude Code Global Hooks Test Suite v2.1")
        print("=" * 60)
        
        # Check environment
        if not self.check_environment():
            return False
            
        # Test scenarios
        test_paths = self.get_test_paths()
        
        for test_name, test_path in test_paths:
            print(f"\n📁 Testing: {test_name}")
            print(f"   Path: {test_path}")
            
            # Create test directory
            test_dir = Path(tempfile.gettempdir()) / test_path
            try:
                test_dir.mkdir(parents=True, exist_ok=True)
                
                # Run tests in this directory
                results = self.run_path_tests(test_dir)
                self.test_results.append((test_name, test_path, results))
                
            except Exception as e:
                print(f"   ❌ Failed to create test directory: {e}")
                self.test_results.append((test_name, test_path, {"error": str(e)}))
            finally:
                # Cleanup
                if test_dir.exists():
                    shutil.rmtree(test_dir, ignore_errors=True)
        
        # Print summary
        self.print_summary()
        return self.all_tests_passed()
    
    def check_environment(self) -> bool:
        """Check if environment is properly configured"""
        print("🔍 Checking Environment...")
        
        checks = {
            "CLAUDE_HOME": os.environ.get('CLAUDE_HOME'),
            "CLAUDE_PYTHON": os.environ.get('CLAUDE_PYTHON'),
            "Hooks Directory": self.hooks_dir.exists(),
            "Python Version": sys.version.split()[0]
        }
        
        all_good = True
        for check, value in checks.items():
            if value and (isinstance(value, bool) or value):
                print(f"   ✅ {check}: {value}")
            else:
                print(f"   ❌ {check}: Not found")
                all_good = False
                
        return all_good
    
    def get_test_paths(self) -> List[Tuple[str, str]]:
        """Get platform-specific test paths with spaces and special characters"""
        
        if self.platform == "Windows":
            return [
                ("Simple Spaces", "Test Project"),
                ("Multiple Spaces", "My Test  Project"),
                ("Special Chars", "Project & Tests"),
                ("Parentheses", "Claude (Beta) Project"),
                ("Unicode", "Projet été 2024"),
                ("Deep Path", "Deep Path\\With Spaces\\Claude Project\\Test App"),
                ("Mixed Chars", "Test_Project-v2.1 (Beta)")
            ]
        else:  # macOS and Linux
            return [
                ("Simple Spaces", "Test Project"),
                ("Multiple Spaces", "My Test  Project"),
                ("Special Chars", "Project & Tests"),
                ("Parentheses", "Claude (Beta) Project"),
                ("Unicode", "Projet été 2024"),
                ("Quotes", "Project 'Test' App"),
                ("Deep Path", "Deep Path/With Spaces/Claude Project/Test App"),
                ("Mixed Chars", "Test_Project-v2.1 (Beta)")
            ]
    
    def run_path_tests(self, test_dir: Path) -> Dict[str, bool]:
        """Run hook tests in a specific directory"""
        results = {}
        
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Set environment for tests
            os.environ['CLAUDE_PROJECT_DIR'] = str(test_dir)
            
            # Test each hook
            hooks_to_test = [
                'session_loader.py',
                'agent_mention_parser.py',
                'planning_trigger.py',
                'quality_gate.py',
                'model_tracker.py'
            ]
            
            for hook in hooks_to_test:
                hook_path = self.hooks_dir / hook
                if hook_path.exists():
                    results[hook] = self.test_hook(hook_path, test_dir)
                else:
                    results[hook] = False
                    print(f"   ⚠️  {hook}: Not found")
            
        finally:
            os.chdir(original_dir)
            
        return results
    
    def test_hook(self, hook_path: Path, test_dir: Path) -> bool:
        """Test a specific hook with the test directory"""
        try:
            # Prepare test input based on hook
            if 'agent_mention_parser' in hook_path.name:
                test_input = "@agent-backend-services create API"
            elif 'planning_trigger' in hook_path.name:
                test_input = "Build a complex e-commerce platform"
            else:
                test_input = ""
            
            # Run hook
            python_cmd = os.environ.get('CLAUDE_PYTHON', 'python3')
            cmd = [python_cmd, str(hook_path)]
            
            # Add input if needed
            process_input = test_input.encode() if test_input else None
            
            result = subprocess.run(
                cmd,
                input=process_input,
                capture_output=True,
                text=True,
                timeout=5,
                env=os.environ.copy()
            )
            
            # Check result
            if result.returncode == 0:
                print(f"   ✅ {hook_path.name}: Success")
                return True
            else:
                print(f"   ❌ {hook_path.name}: Exit code {result.returncode}")
                if result.stderr:
                    print(f"      Error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  {hook_path.name}: Timeout")
            return False
        except Exception as e:
            print(f"   ❌ {hook_path.name}: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        total_scenarios = len(self.test_results)
        passed_scenarios = 0
        
        for test_name, test_path, results in self.test_results:
            if isinstance(results, dict) and "error" not in results:
                passed_hooks = sum(1 for v in results.values() if v)
                total_hooks = len(results)
                scenario_passed = passed_hooks == total_hooks
                
                if scenario_passed:
                    passed_scenarios += 1
                    status = "✅ PASSED"
                else:
                    status = f"⚠️  PARTIAL ({passed_hooks}/{total_hooks})"
            else:
                status = "❌ FAILED"
                
            print(f"{status} - {test_name}")
        
        print(f"\nOverall: {passed_scenarios}/{total_scenarios} scenarios passed")
        
        # Platform-specific notes
        print("\n📝 Platform Notes:")
        if self.platform == "Windows":
            print("   - Windows paths tested with backslashes")
            print("   - PowerShell execution policy may need bypass")
        elif self.platform == "Darwin":
            print("   - macOS paths tested with forward slashes")
            print("   - Check Security & Privacy settings if blocked")
        else:
            print("   - Linux paths tested with forward slashes")
            print("   - WSL paths may need Windows path translation")
    
    def all_tests_passed(self) -> bool:
        """Check if all tests passed"""
        for _, _, results in self.test_results:
            if isinstance(results, dict) and "error" not in results:
                if not all(results.values()):
                    return False
            else:
                return False
        return True


def main():
    """Run the test suite"""
    # Check if running in correct environment
    if not shutil.which('python3') and not shutil.which('python'):
        print("❌ Python not found in PATH")
        return 1
    
    # Create and run test suite
    test_suite = HooksTestSuite()
    
    if test_suite.run_all_tests():
        print("\n🎉 All tests passed! Hooks work correctly with spaces in paths.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the summary above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())