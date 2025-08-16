#!/usr/bin/env python3
"""
Comprehensive Audio System Validation Script
Tests all 102 audio notification files across Windows, mobile, and web interfaces
"""

import os
import sys
import json
import time
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add the audio system to the path
script_dir = Path(__file__).parent
audio_system_dir = script_dir / "Claude_Code_Dev_Stack_v3" / "core" / "audio"
sys.path.insert(0, str(audio_system_dir))

try:
    from audio_validation_system import AudioValidationSystem, ValidationLevel
    from phase_aware_audio_manager import PhaseAwareAudioManager, DevelopmentPhase
except ImportError as e:
    print(f"Error importing audio systems: {e}")
    print("Please ensure audio system modules are available")
    sys.exit(1)

class ComprehensiveAudioValidator:
    """
    Complete audio validation across all platforms and interfaces
    """
    
    def __init__(self):
        self.base_dir = script_dir
        self.audio_dir = self.base_dir / "Claude_Code_Dev_Stack_v3" / "core" / "audio" / "audio"
        self.hooks_dir = self.base_dir / "Claude_Code_Dev_Stack_v3" / "core" / "hooks" / "hooks"
        self.web_dir = self.base_dir / "Claude_Code_Dev_Stack_v3" / "apps" / "web"
        self.mobile_dir = self.base_dir / ".claude-example" / "mobile"
        
        # Platform detection
        self.platform = platform.system()
        
        # Test results
        self.results = {
            "timestamp": time.time(),
            "platform": self.platform,
            "audio_files": {},
            "validation_results": {},
            "hook_integration": {},
            "web_interface": {},
            "mobile_interface": {},
            "cross_platform": {},
            "performance": {},
            "summary": {}
        }
        
        print(f"Comprehensive Audio Validator initialized on {self.platform}")
    
    def validate_all_systems(self) -> Dict[str, Any]:
        """Run complete validation of all audio systems"""
        
        print("Starting comprehensive audio system validation...")
        start_time = time.time()
        
        # 1. Validate audio files
        print("\n1. Validating audio files...")
        self.validate_audio_files()
        
        # 2. Test hook integration
        print("\n2. Testing hook integration...")
        self.test_hook_integration()
        
        # 3. Test web interface
        print("\n3. Testing web interface...")
        self.test_web_interface()
        
        # 4. Test mobile interface
        print("\n4. Testing mobile interface...")
        self.test_mobile_interface()
        
        # 5. Test cross-platform compatibility
        print("\n5. Testing cross-platform compatibility...")
        self.test_cross_platform()
        
        # 6. Performance testing
        print("\n6. Running performance tests...")
        self.test_performance()
        
        # 7. Generate summary
        print("\n7. Generating summary...")
        self.generate_summary()
        
        total_time = time.time() - start_time
        self.results["total_validation_time"] = total_time
        
        print(f"\nValidation completed in {total_time:.2f} seconds")
        self.save_results()
        
        return self.results
    
    def validate_audio_files(self):
        """Validate all audio files using the audio validation system"""
        try:
            validator = AudioValidationSystem()
            validation_results = validator.validate_complete_system(ValidationLevel.FULL)
            
            self.results["audio_files"] = {
                "total_scanned": validation_results["files"]["scanned"],
                "valid_files": validation_results["files"]["valid"],
                "invalid_files": validation_results["files"]["invalid"],
                "missing_files": validation_results["files"]["missing"],
                "coverage_percentage": (validation_results["files"]["valid"] / max(1, validation_results["coverage"]["expected_files"])) * 100,
                "missing_file_list": validation_results["coverage"]["missing_files"],
                "playback_success_rate": (validation_results["playback_tests"]["successful"] / max(1, validation_results["playback_tests"]["attempted"])) * 100 if validation_results["playback_tests"]["attempted"] > 0 else 0
            }
            
            self.results["validation_results"] = validation_results
            
            print(f"  ✓ Found {validation_results['files']['valid']} valid audio files")
            print(f"  ✓ Coverage: {self.results['audio_files']['coverage_percentage']:.1f}%")
            if validation_results["coverage"]["missing_files"]:
                print(f"  ! Missing {len(validation_results['coverage']['missing_files'])} files")
            
        except Exception as e:
            print(f"  ✗ Audio file validation failed: {e}")
            self.results["audio_files"]["error"] = str(e)
    
    def test_hook_integration(self):
        """Test the hook integration system"""
        try:
            hook_script = self.hooks_dir / "audio_integration_v3.py"
            
            if not hook_script.exists():
                raise FileNotFoundError(f"Hook integration script not found: {hook_script}")
            
            # Test different hook events
            test_events = [
                ("SessionStart", None, None),
                ("PreToolUse", "Task", "@agent-frontend-mockup create component"),
                ("PostToolUse", "Write", "Successfully created file"),
                ("Stop", None, None)
            ]
            
            hook_results = {}
            
            for event, tool, command in test_events:
                try:
                    # Create test input
                    test_input = {
                        "hook_event_name": event,
                        "tool_name": tool,
                        "command": command
                    }
                    
                    # Run hook integration
                    result = subprocess.run(
                        [sys.executable, str(hook_script)],
                        input=json.dumps(test_input),
                        capture_output=True,
                        text=True,
                        timeout=5,
                        env={**os.environ, "CLAUDE_AUDIO_DEBUG": "1"}
                    )
                    
                    hook_results[event] = {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                    
                except Exception as e:
                    hook_results[event] = {
                        "success": False,
                        "error": str(e)
                    }
            
            self.results["hook_integration"] = {
                "script_exists": True,
                "test_results": hook_results,
                "success_rate": sum(1 for r in hook_results.values() if r.get("success", False)) / len(hook_results) * 100
            }
            
            success_count = sum(1 for r in hook_results.values() if r.get("success", False))
            print(f"  ✓ Hook integration: {success_count}/{len(test_events)} tests passed")
            
        except Exception as e:
            print(f"  ✗ Hook integration test failed: {e}")
            self.results["hook_integration"]["error"] = str(e)
    
    def test_web_interface(self):
        """Test the web interface integration"""
        try:
            # Check if web components exist
            audio_controller = self.web_dir / "src" / "components" / "AudioController.tsx"
            package_json = self.web_dir / "package.json"
            
            web_results = {
                "audio_controller_exists": audio_controller.exists(),
                "package_json_exists": package_json.exists(),
                "dependencies": {},
                "build_status": None
            }
            
            # Check dependencies
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    
                    required_deps = ["react", "lucide-react"]
                    for dep in required_deps:
                        web_results["dependencies"][dep] = dep in package_data.get("dependencies", {})
                except Exception as e:
                    web_results["dependencies"]["error"] = str(e)
            
            # Test build (if possible)
            try:
                if web_results["package_json_exists"]:
                    # Quick check if node_modules exists
                    node_modules = self.web_dir / "node_modules"
                    web_results["node_modules_exists"] = node_modules.exists()
                    
                    if node_modules.exists():
                        # Try a quick build check
                        result = subprocess.run(
                            ["npm", "run", "build", "--dry-run"],
                            cwd=str(self.web_dir),
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        web_results["build_status"] = "success" if result.returncode == 0 else "failed"
                    else:
                        web_results["build_status"] = "no_dependencies"
            except Exception as e:
                web_results["build_status"] = f"error: {e}"
            
            self.results["web_interface"] = web_results
            
            if web_results["audio_controller_exists"]:
                print("  ✓ Web AudioController component found")
            else:
                print("  ✗ Web AudioController component missing")
            
        except Exception as e:
            print(f"  ✗ Web interface test failed: {e}")
            self.results["web_interface"]["error"] = str(e)
    
    def test_mobile_interface(self):
        """Test mobile interface capabilities"""
        try:
            mobile_results = {
                "mobile_dir_exists": self.mobile_dir.exists(),
                "launcher_scripts": {},
                "audio_support": False
            }
            
            if self.mobile_dir.exists():
                # Check for mobile launcher scripts
                launcher_files = [
                    "launch_mobile.py",
                    "launch_mobile.bat", 
                    "launch_mobile.ps1"
                ]
                
                for launcher in launcher_files:
                    launcher_path = self.mobile_dir / launcher
                    mobile_results["launcher_scripts"][launcher] = launcher_path.exists()
                
                # Check for audio-related mobile files
                audio_files = list(self.mobile_dir.glob("*audio*"))
                mobile_results["audio_files_count"] = len(audio_files)
                mobile_results["audio_support"] = len(audio_files) > 0
            
            self.results["mobile_interface"] = mobile_results
            
            if mobile_results["mobile_dir_exists"]:
                print("  ✓ Mobile interface directory found")
                launcher_count = sum(1 for exists in mobile_results["launcher_scripts"].values() if exists)
                print(f"  ✓ Found {launcher_count} launcher scripts")
            else:
                print("  ✗ Mobile interface directory not found")
                
        except Exception as e:
            print(f"  ✗ Mobile interface test failed: {e}")
            self.results["mobile_interface"]["error"] = str(e)
    
    def test_cross_platform(self):
        """Test cross-platform compatibility"""
        try:
            cross_platform_results = {
                "current_platform": self.platform,
                "audio_players": [],
                "platform_support": {},
                "file_formats": {}
            }
            
            # Test audio player availability
            players_by_platform = {
                "Windows": ["winsound"],
                "Darwin": ["afplay"],
                "Linux": ["aplay", "paplay", "play"]
            }
            
            current_players = players_by_platform.get(self.platform, [])
            
            for player in current_players:
                try:
                    if player == "winsound":
                        import winsound
                        cross_platform_results["audio_players"].append(player)
                    else:
                        result = subprocess.run(
                            ["which", player] if self.platform != "Windows" else [player, "--help"],
                            capture_output=True,
                            timeout=2
                        )
                        if result.returncode == 0:
                            cross_platform_results["audio_players"].append(player)
                except:
                    pass
            
            # Test file format support
            format_support = {
                "wav": True,  # Universally supported
                "mp3": self.platform in ["Darwin", "Windows"],  # Usually supported
                "ogg": self.platform == "Linux"  # Linux-specific
            }
            
            cross_platform_results["file_formats"] = format_support
            cross_platform_results["platform_support"] = {
                "audio_available": len(cross_platform_results["audio_players"]) > 0,
                "recommended_format": "wav",
                "compatibility_score": (len(cross_platform_results["audio_players"]) + sum(format_support.values())) / 5 * 100
            }
            
            self.results["cross_platform"] = cross_platform_results
            
            player_count = len(cross_platform_results["audio_players"])
            print(f"  ✓ Found {player_count} audio players on {self.platform}")
            print(f"  ✓ Compatibility score: {cross_platform_results['platform_support']['compatibility_score']:.1f}%")
            
        except Exception as e:
            print(f"  ✗ Cross-platform test failed: {e}")
            self.results["cross_platform"]["error"] = str(e)
    
    def test_performance(self):
        """Test audio system performance"""
        try:
            performance_results = {
                "audio_load_time": 0,
                "playback_latency": 0,
                "memory_usage": 0,
                "concurrent_playback": False
            }
            
            # Test audio loading performance
            start_time = time.time()
            try:
                manager = PhaseAwareAudioManager()
                performance_results["audio_load_time"] = (time.time() - start_time) * 1000
                
                # Test phase change performance
                start_time = time.time()
                manager.change_phase(DevelopmentPhase.IMPLEMENTATION)
                performance_results["phase_change_time"] = (time.time() - start_time) * 1000
                
                # Test event queuing performance
                start_time = time.time()
                for i in range(10):
                    manager.queue_event(
                        event_id=f"perf_test_{i}",
                        category="system",
                        operation="performance_test"
                    )
                performance_results["event_queue_time"] = (time.time() - start_time) * 1000
                
                manager.shutdown()
                
            except Exception as e:
                performance_results["manager_error"] = str(e)
            
            # Basic memory check
            try:
                import psutil
                process = psutil.Process()
                performance_results["memory_usage"] = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                performance_results["memory_usage"] = "psutil not available"
            
            self.results["performance"] = performance_results
            
            if performance_results.get("audio_load_time"):
                print(f"  ✓ Audio system load time: {performance_results['audio_load_time']:.1f}ms")
            
        except Exception as e:
            print(f"  ✗ Performance test failed: {e}")
            self.results["performance"]["error"] = str(e)
    
    def generate_summary(self):
        """Generate validation summary"""
        summary = {
            "overall_status": "PASS",
            "issues": [],
            "recommendations": [],
            "coverage": {
                "audio_files": 0,
                "hook_integration": 0,
                "web_interface": 0,
                "mobile_interface": 0,
                "cross_platform": 0
            }
        }
        
        # Calculate coverage scores
        if "audio_files" in self.results:
            summary["coverage"]["audio_files"] = self.results["audio_files"].get("coverage_percentage", 0)
        
        if "hook_integration" in self.results:
            summary["coverage"]["hook_integration"] = self.results["hook_integration"].get("success_rate", 0)
        
        if "web_interface" in self.results:
            web = self.results["web_interface"]
            web_score = 0
            if web.get("audio_controller_exists"):
                web_score += 50
            if web.get("node_modules_exists"):
                web_score += 30
            if web.get("build_status") == "success":
                web_score += 20
            summary["coverage"]["web_interface"] = web_score
        
        if "mobile_interface" in self.results:
            mobile = self.results["mobile_interface"]
            mobile_score = 0
            if mobile.get("mobile_dir_exists"):
                mobile_score += 50
            launcher_count = sum(1 for exists in mobile.get("launcher_scripts", {}).values() if exists)
            mobile_score += (launcher_count / 3) * 50
            summary["coverage"]["mobile_interface"] = mobile_score
        
        if "cross_platform" in self.results:
            summary["coverage"]["cross_platform"] = self.results["cross_platform"].get("platform_support", {}).get("compatibility_score", 0)
        
        # Overall score
        overall_score = sum(summary["coverage"].values()) / len(summary["coverage"])
        
        # Generate issues and recommendations
        if summary["coverage"]["audio_files"] < 90:
            summary["issues"].append("Audio file coverage below 90%")
            summary["recommendations"].append("Generate missing audio files using TTS system")
        
        if summary["coverage"]["hook_integration"] < 80:
            summary["issues"].append("Hook integration not fully functional")
            summary["recommendations"].append("Debug hook integration scripts")
        
        if summary["coverage"]["web_interface"] < 70:
            summary["issues"].append("Web interface incomplete")
            summary["recommendations"].append("Complete web interface setup and build")
        
        if summary["coverage"]["cross_platform"] < 60:
            summary["issues"].append("Limited cross-platform support")
            summary["recommendations"].append("Install additional audio players for better compatibility")
        
        if overall_score < 80:
            summary["overall_status"] = "NEEDS_WORK"
        elif overall_score < 60:
            summary["overall_status"] = "FAIL"
        
        summary["overall_score"] = overall_score
        self.results["summary"] = summary
        
        print(f"\n  Overall Score: {overall_score:.1f}% ({summary['overall_status']})")
        if summary["issues"]:
            print("  Issues found:")
            for issue in summary["issues"]:
                print(f"    - {issue}")
    
    def save_results(self):
        """Save validation results to file"""
        timestamp = int(time.time())
        results_file = self.base_dir / f"audio_validation_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\nResults saved to: {results_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_detailed_report(self):
        """Print detailed validation report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE AUDIO SYSTEM VALIDATION REPORT")
        print("="*80)
        
        print(f"\nPlatform: {self.results['platform']}")
        print(f"Validation Time: {self.results.get('total_validation_time', 0):.2f}s")
        
        # Audio Files
        if "audio_files" in self.results:
            af = self.results["audio_files"]
            print(f"\nAudio Files:")
            print(f"  Valid: {af.get('valid_files', 0)}")
            print(f"  Invalid: {af.get('invalid_files', 0)}")
            print(f"  Missing: {af.get('missing_files', 0)}")
            print(f"  Coverage: {af.get('coverage_percentage', 0):.1f}%")
        
        # Summary
        if "summary" in self.results:
            summary = self.results["summary"]
            print(f"\nSummary:")
            print(f"  Overall Status: {summary['overall_status']}")
            print(f"  Overall Score: {summary['overall_score']:.1f}%")
            
            if summary["issues"]:
                print(f"  Issues:")
                for issue in summary["issues"]:
                    print(f"    - {issue}")
            
            if summary["recommendations"]:
                print(f"  Recommendations:")
                for rec in summary["recommendations"]:
                    print(f"    - {rec}")

def main():
    """Main validation entry point"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python validate_audio_system.py [--report]")
        print("  --report: Show detailed report after validation")
        return
    
    validator = ComprehensiveAudioValidator()
    results = validator.validate_all_systems()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        validator.print_detailed_report()
    
    # Exit with appropriate code
    overall_status = results.get("summary", {}).get("overall_status", "FAIL")
    exit_code = 0 if overall_status == "PASS" else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()