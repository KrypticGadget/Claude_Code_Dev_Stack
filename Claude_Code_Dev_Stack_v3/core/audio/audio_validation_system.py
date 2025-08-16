#!/usr/bin/env python3
"""
Audio Notification Validation System for Phase-Aware Development
Complete validation, testing, and cross-platform compatibility system for 102 audio files
"""

import os
import sys
import json
import time
import platform
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Cross-platform audio imports
try:
    if platform.system() == "Windows":
        import winsound
    elif platform.system() == "Darwin":
        # macOS - using subprocess for afplay
        pass
    else:
        # Linux - using subprocess for various players
        pass
except ImportError as e:
    print(f"Warning: Audio system import failed: {e}")

class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"

class ValidationLevel(Enum):
    BASIC = "basic"
    FULL = "full"
    STRESS = "stress"

@dataclass
class AudioFile:
    name: str
    path: Path
    format: AudioFormat
    size_bytes: int
    duration_ms: Optional[int] = None
    sample_rate: Optional[int] = None
    is_valid: bool = False
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

@dataclass
class PhaseContext:
    phase_name: str
    active_agents: List[str]
    current_operation: str
    platform: str
    session_id: str
    timestamp: float

class AudioValidationSystem:
    """
    Comprehensive audio validation and testing system for Claude Code Dev Stack
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.audio_dir = self.base_dir / "audio"
        self.validation_dir = self.base_dir / "validation"
        self.logs_dir = self.validation_dir / "logs"
        self.reports_dir = self.validation_dir / "reports"
        
        # Create directories
        for dir_path in [self.validation_dir, self.logs_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load audio configuration
        self.config = self._load_audio_config()
        
        # Platform detection
        self.platform = platform.system()
        self.platform_config = self._get_platform_config()
        
        # Validation results
        self.validation_results = {}
        self.test_results = {}
        
        # Expected audio files based on audio_config.json
        self.expected_files = self._get_expected_files()
        
        print(f"Audio Validation System initialized for {self.platform}")
        print(f"Expected audio files: {len(self.expected_files)}")
    
    def _load_audio_config(self) -> Dict[str, Any]:
        """Load the main audio configuration"""
        config_path = self.base_dir.parent.parent / "TTS" / "audio_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading audio config: {e}")
        
        # Fallback configuration
        return {
            "audio_files": {},
            "voice_settings": {},
            "categories": {}
        }
    
    def _get_expected_files(self) -> List[str]:
        """Get list of expected audio files from configuration"""
        expected = []
        
        # From audio_config.json
        if "audio_files" in self.config:
            expected.extend(self.config["audio_files"].keys())
        
        # Additional phase-aware files
        phase_files = [
            "quality_gate_passed.wav",
            "file_not_found.wav",
            "permission_denied.wav",
            "phase_testing.wav",
            "milestone_complete.wav",
            "working.wav",
            "v3_feature_activated.wav"
        ]
        
        for file in phase_files:
            if file not in expected:
                expected.append(file)
        
        return expected
    
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific audio configuration"""
        configs = {
            "Windows": {
                "audio_players": ["winsound"],
                "supported_formats": [".wav", ".mp3"],
                "test_command": None,
                "volume_control": "system"
            },
            "Darwin": {  # macOS
                "audio_players": ["afplay"],
                "supported_formats": [".wav", ".mp3", ".aiff", ".m4a"],
                "test_command": ["afplay", "--help"],
                "volume_control": "afplay"
            },
            "Linux": {
                "audio_players": ["aplay", "paplay", "play", "mpg123"],
                "supported_formats": [".wav", ".mp3", ".ogg"],
                "test_command": ["which", "aplay"],
                "volume_control": "alsa"
            }
        }
        
        return configs.get(self.platform, configs["Linux"])
    
    def validate_audio_environment(self) -> Dict[str, Any]:
        """Validate the audio environment and capabilities"""
        print("Validating audio environment...")
        
        results = {
            "platform": self.platform,
            "audio_system_available": False,
            "supported_formats": [],
            "available_players": [],
            "volume_control": False,
            "errors": []
        }
        
        try:
            # Test platform-specific audio system
            if self.platform == "Windows":
                results["audio_system_available"] = self._test_windows_audio()
            elif self.platform == "Darwin":
                results["audio_system_available"] = self._test_macos_audio()
            else:
                results["audio_system_available"] = self._test_linux_audio()
            
            # Test supported formats
            results["supported_formats"] = self.platform_config["supported_formats"]
            
            # Test available players
            results["available_players"] = self._test_audio_players()
            
            # Test volume control
            results["volume_control"] = self._test_volume_control()
            
        except Exception as e:
            results["errors"].append(f"Environment validation error: {str(e)}")
        
        return results
    
    def _test_windows_audio(self) -> bool:
        """Test Windows audio system"""
        try:
            import winsound
            # Test basic functionality
            winsound.Beep(1000, 100)
            return True
        except Exception:
            return False
    
    def _test_macos_audio(self) -> bool:
        """Test macOS audio system"""
        try:
            result = subprocess.run(
                ["afplay", "--help"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _test_linux_audio(self) -> bool:
        """Test Linux audio system"""
        for player in self.platform_config["audio_players"]:
            try:
                result = subprocess.run(
                    ["which", player], 
                    capture_output=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False
    
    def _test_audio_players(self) -> List[str]:
        """Test available audio players"""
        available = []
        
        for player in self.platform_config["audio_players"]:
            try:
                if self.platform == "Windows" and player == "winsound":
                    import winsound
                    available.append(player)
                else:
                    result = subprocess.run(
                        ["which", player] if self.platform != "Windows" else [player, "--help"], 
                        capture_output=True, 
                        timeout=5
                    )
                    if result.returncode == 0:
                        available.append(player)
            except Exception:
                continue
        
        return available
    
    def _test_volume_control(self) -> bool:
        """Test volume control capabilities"""
        try:
            if self.platform == "Windows":
                # Windows has system volume control
                return True
            elif self.platform == "Darwin":
                # macOS afplay supports volume control
                return True
            else:
                # Linux - test ALSA mixer
                result = subprocess.run(
                    ["which", "amixer"], 
                    capture_output=True, 
                    timeout=5
                )
                return result.returncode == 0
        except Exception:
            return False
    
    def scan_audio_files(self) -> List[AudioFile]:
        """Scan and catalog all audio files"""
        print(f"Scanning audio files in {self.audio_dir}...")
        
        audio_files = []
        
        if not self.audio_dir.exists():
            print(f"Warning: Audio directory {self.audio_dir} does not exist")
            return audio_files
        
        # Scan for audio files
        for file_path in self.audio_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.wav', '.mp3', '.ogg', '.flac']:
                try:
                    audio_file = AudioFile(
                        name=file_path.name,
                        path=file_path,
                        format=AudioFormat(file_path.suffix[1:].lower()),
                        size_bytes=file_path.stat().st_size
                    )
                    audio_files.append(audio_file)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Found {len(audio_files)} audio files")
        return audio_files
    
    def validate_audio_file(self, audio_file: AudioFile, level: ValidationLevel = ValidationLevel.BASIC) -> AudioFile:
        """Validate a single audio file"""
        
        # Basic validation
        try:
            # Check file exists and is readable
            if not audio_file.path.exists():
                audio_file.validation_errors.append("File does not exist")
                return audio_file
            
            if audio_file.size_bytes == 0:
                audio_file.validation_errors.append("File is empty")
                return audio_file
            
            # Check minimum size (at least 1KB for a valid audio file)
            if audio_file.size_bytes < 1024:
                audio_file.validation_errors.append("File too small to be valid audio")
                return audio_file
            
            # Platform-specific validation
            if level in [ValidationLevel.FULL, ValidationLevel.STRESS]:
                self._detailed_audio_validation(audio_file)
            
            # Mark as valid if no errors
            if not audio_file.validation_errors:
                audio_file.is_valid = True
            
        except Exception as e:
            audio_file.validation_errors.append(f"Validation error: {str(e)}")
        
        return audio_file
    
    def _detailed_audio_validation(self, audio_file: AudioFile):
        """Perform detailed audio file validation"""
        try:
            # Try to get audio metadata if available
            if audio_file.format == AudioFormat.WAV:
                self._validate_wav_file(audio_file)
            elif audio_file.format == AudioFormat.MP3:
                self._validate_mp3_file(audio_file)
            
        except Exception as e:
            audio_file.validation_errors.append(f"Detailed validation error: {str(e)}")
    
    def _validate_wav_file(self, audio_file: AudioFile):
        """Validate WAV file format"""
        try:
            with open(audio_file.path, 'rb') as f:
                # Check RIFF header
                header = f.read(12)
                if len(header) < 12:
                    audio_file.validation_errors.append("WAV file too short")
                    return
                
                if header[:4] != b'RIFF':
                    audio_file.validation_errors.append("Invalid WAV RIFF header")
                    return
                
                if header[8:12] != b'WAVE':
                    audio_file.validation_errors.append("Invalid WAV format")
                    return
                
                # Basic WAV validation passed
                
        except Exception as e:
            audio_file.validation_errors.append(f"WAV validation error: {str(e)}")
    
    def _validate_mp3_file(self, audio_file: AudioFile):
        """Validate MP3 file format"""
        try:
            with open(audio_file.path, 'rb') as f:
                # Check for MP3 sync word
                header = f.read(10)
                if len(header) < 10:
                    audio_file.validation_errors.append("MP3 file too short")
                    return
                
                # Look for MP3 frame sync (0xFF followed by 0xE0-0xFF)
                found_sync = False
                for i in range(len(header) - 1):
                    if header[i] == 0xFF and (header[i + 1] & 0xE0) == 0xE0:
                        found_sync = True
                        break
                
                if not found_sync:
                    audio_file.validation_errors.append("No valid MP3 sync found")
                    return
                
        except Exception as e:
            audio_file.validation_errors.append(f"MP3 validation error: {str(e)}")
    
    def test_audio_playback(self, audio_file: AudioFile, timeout: float = 5.0) -> Dict[str, Any]:
        """Test audio file playback"""
        result = {
            "success": False,
            "player_used": None,
            "duration_ms": None,
            "error": None
        }
        
        try:
            if self.platform == "Windows":
                result.update(self._test_windows_playback(audio_file, timeout))
            elif self.platform == "Darwin":
                result.update(self._test_macos_playback(audio_file, timeout))
            else:
                result.update(self._test_linux_playback(audio_file, timeout))
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _test_windows_playback(self, audio_file: AudioFile, timeout: float) -> Dict[str, Any]:
        """Test audio playback on Windows"""
        try:
            import winsound
            start_time = time.time()
            winsound.PlaySound(str(audio_file.path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            # Give it a moment to start
            time.sleep(0.1)
            duration_ms = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "player_used": "winsound",
                "duration_ms": duration_ms
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_macos_playback(self, audio_file: AudioFile, timeout: float) -> Dict[str, Any]:
        """Test audio playback on macOS"""
        try:
            start_time = time.time()
            process = subprocess.Popen(
                ["afplay", str(audio_file.path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a short time to see if it starts successfully
            time.sleep(0.1)
            if process.poll() is None:  # Still running
                process.terminate()
                duration_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "player_used": "afplay",
                    "duration_ms": duration_ms
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "error": f"afplay failed: {stderr.decode()}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _test_linux_playback(self, audio_file: AudioFile, timeout: float) -> Dict[str, Any]:
        """Test audio playback on Linux"""
        for player in self.platform_config["audio_players"]:
            try:
                start_time = time.time()
                process = subprocess.Popen(
                    [player, str(audio_file.path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait a short time to see if it starts successfully
                time.sleep(0.1)
                if process.poll() is None:  # Still running
                    process.terminate()
                    duration_ms = int((time.time() - start_time) * 1000)
                    return {
                        "success": True,
                        "player_used": player,
                        "duration_ms": duration_ms
                    }
            except Exception:
                continue
        
        return {
            "success": False,
            "error": "No working audio player found"
        }
    
    def validate_complete_system(self, level: ValidationLevel = ValidationLevel.FULL) -> Dict[str, Any]:
        """Perform complete system validation"""
        print(f"Starting complete system validation (level: {level.value})...")
        
        start_time = time.time()
        
        results = {
            "timestamp": start_time,
            "validation_level": level.value,
            "environment": self.validate_audio_environment(),
            "files": {
                "scanned": 0,
                "valid": 0,
                "invalid": 0,
                "missing": 0,
                "details": []
            },
            "playback_tests": {
                "attempted": 0,
                "successful": 0,
                "failed": 0,
                "details": []
            },
            "coverage": {
                "expected_files": len(self.expected_files),
                "found_files": 0,
                "missing_files": []
            },
            "performance": {
                "total_duration_seconds": 0,
                "average_file_validation_ms": 0
            }
        }
        
        # Scan audio files
        audio_files = self.scan_audio_files()
        results["files"]["scanned"] = len(audio_files)
        
        # Validate each file
        for audio_file in audio_files:
            file_start = time.time()
            validated_file = self.validate_audio_file(audio_file, level)
            
            if validated_file.is_valid:
                results["files"]["valid"] += 1
            else:
                results["files"]["invalid"] += 1
            
            results["files"]["details"].append({
                "name": validated_file.name,
                "valid": validated_file.is_valid,
                "errors": validated_file.validation_errors,
                "size_bytes": validated_file.size_bytes
            })
            
            # Test playback for valid files
            if validated_file.is_valid and level in [ValidationLevel.FULL, ValidationLevel.STRESS]:
                playback_result = self.test_audio_playback(validated_file)
                results["playback_tests"]["attempted"] += 1
                
                if playback_result["success"]:
                    results["playback_tests"]["successful"] += 1
                else:
                    results["playback_tests"]["failed"] += 1
                
                results["playback_tests"]["details"].append({
                    "file": validated_file.name,
                    "result": playback_result
                })
        
        # Check coverage
        found_names = [f.name for f in audio_files]
        results["coverage"]["found_files"] = len(found_names)
        
        for expected in self.expected_files:
            if expected not in found_names:
                results["coverage"]["missing_files"].append(expected)
        
        results["files"]["missing"] = len(results["coverage"]["missing_files"])
        
        # Performance metrics
        total_duration = time.time() - start_time
        results["performance"]["total_duration_seconds"] = total_duration
        if audio_files:
            results["performance"]["average_file_validation_ms"] = (total_duration * 1000) / len(audio_files)
        
        # Save results
        self._save_validation_results(results)
        
        print(f"Validation complete in {total_duration:.2f}s")
        print(f"Files: {results['files']['valid']}/{results['files']['scanned']} valid")
        print(f"Missing: {results['files']['missing']} files")
        
        return results
    
    def _save_validation_results(self, results: Dict[str, Any]):
        """Save validation results to file"""
        timestamp = int(time.time())
        results_file = self.reports_dir / f"validation_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {results_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def generate_missing_files(self, dry_run: bool = True) -> List[str]:
        """Generate missing audio files using TTS"""
        print("Identifying missing audio files...")
        
        audio_files = self.scan_audio_files()
        found_names = [f.name for f in audio_files]
        missing_files = [f for f in self.expected_files if f not in found_names]
        
        if not missing_files:
            print("No missing files found!")
            return []
        
        print(f"Found {len(missing_files)} missing files:")
        for file in missing_files:
            print(f"  - {file}")
        
        if dry_run:
            print("Dry run - no files generated")
            return missing_files
        
        # Generate missing files
        tts_script = self.base_dir.parent.parent / "TTS" / "generator" / "generate_new_audio.py"
        if tts_script.exists():
            try:
                # Create temporary config for missing files
                missing_config = {}
                for file in missing_files:
                    # Extract description from config or generate one
                    description = self.config.get("audio_files", {}).get(file, f"Audio notification for {file.replace('.wav', '').replace('_', ' ')}")
                    missing_config[file] = description
                
                config_file = self.validation_dir / "missing_files_config.json"
                with open(config_file, 'w') as f:
                    json.dump({"audio_files": missing_config}, f, indent=2)
                
                print(f"Generating {len(missing_files)} missing audio files...")
                result = subprocess.run([
                    sys.executable, str(tts_script), "--config", str(config_file)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Audio generation completed successfully")
                else:
                    print(f"Audio generation failed: {result.stderr}")
                
            except Exception as e:
                print(f"Error generating missing files: {e}")
        
        return missing_files
    
    def run_stress_test(self, iterations: int = 10, concurrent: bool = True) -> Dict[str, Any]:
        """Run stress test on audio system"""
        print(f"Running stress test: {iterations} iterations, concurrent={concurrent}")
        
        start_time = time.time()
        results = {
            "iterations": iterations,
            "concurrent": concurrent,
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "average_response_time_ms": 0,
            "errors": []
        }
        
        audio_files = [f for f in self.scan_audio_files() if f.is_valid]
        if not audio_files:
            results["errors"].append("No valid audio files found for stress testing")
            return results
        
        test_times = []
        
        def run_test_iteration(iteration: int, audio_file: AudioFile):
            try:
                test_start = time.time()
                playback_result = self.test_audio_playback(audio_file, timeout=2.0)
                test_duration = (time.time() - test_start) * 1000
                
                test_times.append(test_duration)
                results["total_tests"] += 1
                
                if playback_result["success"]:
                    results["successful_tests"] += 1
                else:
                    results["failed_tests"] += 1
                    results["errors"].append(f"Iteration {iteration}: {playback_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                results["failed_tests"] += 1
                results["errors"].append(f"Iteration {iteration}: {str(e)}")
        
        if concurrent:
            threads = []
            for i in range(iterations):
                audio_file = audio_files[i % len(audio_files)]
                thread = threading.Thread(target=run_test_iteration, args=(i, audio_file))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
        else:
            for i in range(iterations):
                audio_file = audio_files[i % len(audio_files)]
                run_test_iteration(i, audio_file)
        
        if test_times:
            results["average_response_time_ms"] = sum(test_times) / len(test_times)
        
        total_duration = time.time() - start_time
        print(f"Stress test completed in {total_duration:.2f}s")
        print(f"Success rate: {results['successful_tests']}/{results['total_tests']} ({results['successful_tests']/max(1, results['total_tests'])*100:.1f}%)")
        
        return results

def main():
    """Main validation entry point"""
    system = AudioValidationSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "validate":
            level = ValidationLevel.FULL
            if len(sys.argv) > 2:
                level = ValidationLevel(sys.argv[2].lower())
            results = system.validate_complete_system(level)
            
        elif command == "scan":
            files = system.scan_audio_files()
            print(f"Found {len(files)} audio files")
            
        elif command == "missing":
            dry_run = "--generate" not in sys.argv
            missing = system.generate_missing_files(dry_run)
            print(f"Missing files: {len(missing)}")
            
        elif command == "stress":
            iterations = 10
            if len(sys.argv) > 2:
                iterations = int(sys.argv[2])
            results = system.run_stress_test(iterations)
            
        elif command == "environment":
            env_results = system.validate_audio_environment()
            print(json.dumps(env_results, indent=2))
            
        else:
            print("Unknown command. Use: validate, scan, missing, stress, environment")
    else:
        # Default full validation
        results = system.validate_complete_system(ValidationLevel.FULL)

if __name__ == "__main__":
    main()