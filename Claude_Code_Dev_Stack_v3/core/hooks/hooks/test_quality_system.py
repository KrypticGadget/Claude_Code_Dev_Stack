#!/usr/bin/env python3
"""
Test script for the updated quality system
Tests linting with different strictness levels and audio notifications
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def create_test_file_with_issues():
    """Create a test Python file with various linting issues"""
    test_content = '''#!/usr/bin/env python3
# Test file with various linting issues

import unused_module
import os
import sys

def very_long_function_name_that_exceeds_normal_conventions():
    password = "hardcoded_secret_123"  # Security issue
    x=1+2+3+4+5  # Style issue - no spaces
    if True:
        if True:
            if True:
                if True:
                    print("Too much nesting")  # Complexity issue
    
    # Line too long - this line is intentionally very long to trigger the line length warning from linters like flake8
    return x

def another_function():
    # Missing docstring
    pass

class TestClass:
    def method_with_issues(self):
        # Unused variable
        unused_var = "test"
        print("Hello World")   # Trailing whitespace issue
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        return f.name

def test_linter_with_strictness(test_file_path, strictness_level):
    """Test the linter with different strictness levels"""
    print(f"\n[TEST] Testing strictness level: {strictness_level}")
    print("=" * 50)
    
    # Set strictness level
    quality_config_path = Path(__file__).parent / 'quality_config.py'
    subprocess.run([
        sys.executable, str(quality_config_path), 'strictness', strictness_level
    ], capture_output=True)
    
    # Run the linter
    linter_path = Path(__file__).parent / 'code_linter.py'
    result = subprocess.run([
        sys.executable, str(linter_path), 'post-write', test_file_path
    ], capture_output=True, text=True)
    
    print(f"Return code: {result.returncode}")
    print(f"Success: {'[OK] Commit allowed' if result.returncode == 0 else '[BLOCKED] Commit blocked'}")
    
    if result.stderr:
        print("\nLinter output:")
        print(result.stderr)
    
    return result.returncode == 0

def test_audio_notifications():
    """Test audio notification functionality"""
    print("\n[AUDIO] Testing audio notifications...")
    
    # Check if audio files exist
    audio_dir = Path.home() / '.claude' / 'audio'
    audio_files = [
        'linting_started.wav',
        'linting_complete.wav', 
        'linting_issues.wav',
        'formatting_code.wav'
    ]
    
    for audio_file in audio_files:
        audio_path = audio_dir / audio_file
        if audio_path.exists():
            print(f"[OK] {audio_file} found")
        else:
            print(f"[WARN] {audio_file} not found (audio notifications may not work)")

def main():
    """Main test function"""
    print("[TEST] Claude Code Quality System Test")
    print("=" * 60)
    
    # Create test file
    test_file = create_test_file_with_issues()
    print(f"Created test file: {test_file}")
    
    try:
        # Test audio notifications
        test_audio_notifications()
        
        # Test different strictness levels
        strictness_levels = ['suggestion', 'warning', 'strict']
        results = {}
        
        for level in strictness_levels:
            results[level] = test_linter_with_strictness(test_file, level)
        
        # Summary
        print("\n[RESULTS] Test Results Summary:")
        print("=" * 30)
        for level, success in results.items():
            status = "[OK] Allows commit" if success else "[BLOCKED] Blocks commit"
            print(f"{level:12}: {status}")
        
        print(f"\n[RECOMMENDATIONS] Recommendations:")
        print(f"  * Use 'suggestion' level for development (shows issues, allows commits)")
        print(f"  * Use 'warning' level for team environments (blocks only on errors)")
        print(f"  * Use 'strict' level for production branches (blocks on any issue)")
        
        print(f"\n[COMMANDS] Configuration commands:")
        print(f"  python quality_config.py strictness suggestion")
        print(f"  python quality_config.py show")
        print(f"  python quality_config.py autoformat on")
        
    finally:
        # Cleanup
        os.unlink(test_file)
        print(f"\nCleaned up test file: {test_file}")

if __name__ == '__main__':
    main()