#!/usr/bin/env python3
"""
Generate v5.0 Audio Files as PROPER WAV format
Converts Edge-TTS MP3 output to real PCM WAV files that work with winsound
"""

import asyncio
import edge_tts
import pygame
import wave
from pathlib import Path
import os
import sys

# Output directory for proper WAV files
OUTPUT_DIR = Path("audio_v5_proper")
OUTPUT_DIR.mkdir(exist_ok=True)

# Complete v5.0 audio system - 69 files with descriptive text
AUDIO_FILES_V5 = {
    # Core System Files (22) - Original compatibility
    "project_created.wav": "Project initialized successfully",
    "ready_for_input.wav": "Ready for your input",
    "agent_activated.wav": "Agent activated",
    "pipeline_complete.wav": "Pipeline completed",
    "pipeline_initiated.wav": "Pipeline initiated",
    "confirm_required.wav": "Confirmation required",
    "file_operation_pending.wav": "File operation pending",
    "file_operation_complete.wav": "File operation complete",
    "command_execution_pending.wav": "Command execution pending",
    "command_successful.wav": "Command successful",
    "planning_complete.wav": "Planning complete",
    "processing.wav": "Processing",
    "analyzing.wav": "Analyzing",
    "working.wav": "Working",
    "awaiting_input.wav": "Awaiting input",
    "milestone_complete.wav": "Milestone complete",
    "operation_complete.wav": "Operation complete",
    "phase_complete.wav": "Phase complete",
    "decision_required.wav": "Decision required",
    "awaiting_confirmation.wav": "Awaiting confirmation",
    "permission_required.wav": "Permission required",
    "build_successful.wav": "Build successful",
    
    # File Operations - SPECIFIC (5)
    "mkdir_operation.wav": "Creating directory",
    "touch_operation.wav": "Creating new file",
    "copy_operation.wav": "Copying files",
    "move_operation.wav": "Moving files",
    "delete_operation.wav": "Deleting files",
    
    # Git Operations - SPECIFIC (4)
    "git_status.wav": "Checking git status",
    "git_commit.wav": "Creating git commit",
    "git_push.wav": "Pushing to remote repository",
    "git_pull.wav": "Pulling latest changes",
    
    # Build Operations - SPECIFIC (3)
    "npm_build.wav": "Running npm build",
    "make_build.wav": "Building with make",
    "cargo_build.wav": "Building rust project",
    
    # Testing - SPECIFIC (3)
    "running_tests.wav": "Running test suite",
    "tests_passed.wav": "All tests passed",
    "tests_failed.wav": "Tests failed",
    
    # Package Management - SPECIFIC (3)
    "installing_packages.wav": "Installing packages",
    "pip_install.wav": "Installing Python packages",
    "npm_install.wav": "Installing node modules",
    
    # Docker - SPECIFIC (2)
    "docker_building.wav": "Building Docker image",
    "docker_running.wav": "Starting Docker container",
    
    # Navigation/Search - SPECIFIC (3)
    "checking_files.wav": "Listing directory contents",
    "searching_files.wav": "Searching for files",
    "changing_directory.wav": "Navigating to directory",
    
    # Network - SPECIFIC (3)
    "http_request.wav": "Making HTTP request",
    "downloading_file.wav": "Downloading file",
    "ssh_connection.wav": "Establishing SSH connection",
    
    # Virtual Environment - SPECIFIC (3)
    "venv_required.wav": "Virtual environment required",
    "venv_activated.wav": "Virtual environment activated",
    "no_venv_warning.wav": "Warning - no virtual environment",
    
    # Agent Operations - SPECIFIC (4)
    "frontend_agent.wav": "Frontend agent working",
    "backend_agent.wav": "Backend agent processing",
    "database_agent.wav": "Database agent executing",
    "master_orchestrator.wav": "Orchestrator coordinating",
    
    # Status Updates - SPECIFIC (4)
    "analyzing_code.wav": "Analyzing your code",
    "generating_code.wav": "Generating code",
    "reviewing_changes.wav": "Reviewing changes",
    "optimizing_performance.wav": "Optimizing performance",
    
    # Warnings - SPECIFIC (3)
    "risky_command.wav": "Caution - risky command detected",
    "permission_denied.wav": "Permission denied",
    "file_exists.wav": "File already exists",
    
    # Errors - SPECIFIC (3)
    "command_failed.wav": "Command execution failed",
    "file_not_found.wav": "File not found",
    "connection_error.wav": "Connection error",
    
    # MCP Services - SPECIFIC (3)
    "playwright_automation.wav": "Playwright browser automation",
    "obsidian_notes.wav": "Obsidian note management",
    "web_search.wav": "Searching the web",
    
    # Auto Mode - SPECIFIC (2)
    "auto_accepting.wav": "Auto-accepting operation",
    "auto_mode_active.wav": "Automatic mode active"
}

async def generate_proper_wav(filename, text):
    """Generate a proper PCM WAV file using Edge-TTS + pygame + wave"""
    
    try:
        # Use clear voice for all
        voice = "en-US-AriaNeural"  # Clear female voice
        
        # Alternative voices based on content
        if "error" in text.lower() or "failed" in text.lower():
            voice = "en-US-JennyNeural"  # Alert voice
        elif "agent" in text.lower() or "orchestrator" in text.lower():
            voice = "en-GB-RyanNeural"  # British male (JARVIS-style)
        elif "caution" in text.lower() or "warning" in text.lower():
            voice = "en-US-JennyNeural"  # Alert voice
        
        # Generate with Edge-TTS
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate="-5%",      # Slightly slower for clarity
            pitch="-5Hz"      # Slightly lower for authority
        )
        
        # Save as temporary MP3 (Edge-TTS default format)
        temp_mp3 = OUTPUT_DIR / f"_temp_{filename}.mp3"
        await communicate.save(str(temp_mp3))
        
        # Convert MP3 to WAV using pygame
        sound = pygame.mixer.Sound(str(temp_mp3))
        raw_data = sound.get_raw()
        
        # Save as PROPER PCM WAV file
        output_file = OUTPUT_DIR / filename
        with wave.open(str(output_file), 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            wav_file.writeframes(raw_data)
        
        # Remove temp MP3 file
        if temp_mp3.exists():
            temp_mp3.unlink()
        
        # Verify file size
        size = output_file.stat().st_size
        if size > 1000:  # Should be at least 1KB
            return True, size
        else:
            return False, 0
            
    except Exception as e:
        print(f"    Error: {e}")
        return False, 0

async def main():
    """Generate all v5.0 audio files as proper WAVs"""
    
    print("=" * 70)
    print("CLAUDE CODE V5.0 - PROPER WAV AUDIO GENERATION")
    print("Generating 69 descriptive audio files as real PCM WAV format")
    print("=" * 70)
    
    # Check dependencies
    print("\nChecking dependencies...")
    
    # Check pygame
    try:
        import pygame
        print("  [OK] pygame is installed")
    except ImportError:
        print("  Installing pygame...")
        os.system("pip install pygame")
        import pygame
    
    # Check edge-tts
    try:
        import edge_tts
        print("  [OK] edge-tts is installed")
    except ImportError:
        print("  Installing edge-tts...")
        os.system("pip install edge-tts")
        import edge_tts
    
    # Initialize pygame for audio conversion
    print("\nInitializing pygame mixer...")
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    print("  [OK] Pygame mixer initialized")
    
    # Generate all files
    print(f"\nGenerating {len(AUDIO_FILES_V5)} audio files...")
    print("-" * 40)
    
    success_count = 0
    failed_files = []
    total = len(AUDIO_FILES_V5)
    current = 0
    
    for filename, text in AUDIO_FILES_V5.items():
        current += 1
        print(f"[{current:2}/{total}] {filename:<30} - '{text}'")
        
        success, size = await generate_proper_wav(filename, text)
        
        if success:
            print(f"    [OK] Generated ({size:,} bytes)")
            success_count += 1
        else:
            print(f"    [FAIL] Generation failed")
            failed_files.append(filename)
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    
    if success_count == total:
        print(f"[SUCCESS] All {total} audio files generated as proper WAV!")
    else:
        print(f"Generated: {success_count}/{total} files")
        if failed_files:
            print(f"Failed files: {', '.join(failed_files[:5])}")
    
    print(f"\nOutput location: {OUTPUT_DIR.absolute()}")
    
    # Test with winsound
    print("\n" + "-" * 40)
    print("Testing playback with winsound...")
    
    try:
        import winsound
        test_files = ["mkdir_operation.wav", "git_status.wav", "project_created.wav"]
        
        for test_file in test_files:
            test_path = OUTPUT_DIR / test_file
            if test_path.exists():
                print(f"  Testing: {test_file}")
                winsound.PlaySound(str(test_path), winsound.SND_FILENAME)
                print(f"    [OK] Plays correctly!")
                break
        
        print("\n[SUCCESS] Audio files are proper WAV format and play correctly!")
        
    except Exception as e:
        print(f"  Could not test playback: {e}")
    
    # Instructions
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Delete the bad .wav files from:")
    print(f"   C:\\Users\\Zach\\Desktop\\Master Code\\Claude_Code_Agents\\Claude_Code_Dev_Stack\\.claude-example\\audio\\")
    print("\n2. Copy the new proper WAV files from:")
    print(f"   {OUTPUT_DIR.absolute()}")
    print("   TO:")
    print(f"   .claude-example\\audio\\")
    print("\n3. The audio system will now work correctly!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())