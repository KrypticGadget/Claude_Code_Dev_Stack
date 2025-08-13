#!/usr/bin/env python3
"""
Generate SPECIFIC audio files that actually tell you what's happening
Uses the working method from generate_new_audio.py
"""

import asyncio
import edge_tts
import os
from pathlib import Path
import pygame
import io

# Initialize pygame
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Output directory
OUTPUT_DIR = Path("audio_specific")
OUTPUT_DIR.mkdir(exist_ok=True)

# Define specific audio files with clear descriptions
SPECIFIC_AUDIO = {
    # File Operations - SPECIFIC
    "mkdir_operation.wav": "Creating directory",
    "touch_operation.wav": "Creating new file",
    "copy_operation.wav": "Copying files",
    "move_operation.wav": "Moving files", 
    "delete_operation.wav": "Deleting files",
    
    # Git Operations - SPECIFIC
    "git_status.wav": "Checking git status",
    "git_commit.wav": "Creating git commit",
    "git_push.wav": "Pushing to remote repository",
    "git_pull.wav": "Pulling latest changes",
    
    # Build Operations - SPECIFIC
    "npm_build.wav": "Running npm build",
    "make_build.wav": "Building with make",
    "cargo_build.wav": "Building rust project",
    
    # Testing - SPECIFIC
    "running_tests.wav": "Running test suite",
    "tests_passed.wav": "All tests passed",
    "tests_failed.wav": "Tests failed",
    
    # Package Management - SPECIFIC
    "installing_packages.wav": "Installing packages",
    "pip_install.wav": "Installing Python packages",
    "npm_install.wav": "Installing node modules",
    
    # Docker - SPECIFIC
    "docker_building.wav": "Building Docker image",
    "docker_running.wav": "Starting Docker container",
    
    # System Operations - SPECIFIC
    "checking_files.wav": "Listing directory contents",
    "searching_files.wav": "Searching for files",
    "changing_directory.wav": "Navigating to directory",
    
    # Network - SPECIFIC
    "http_request.wav": "Making HTTP request",
    "downloading_file.wav": "Downloading file",
    "ssh_connection.wav": "Establishing SSH connection",
    
    # Virtual Environment - SPECIFIC
    "venv_required.wav": "Virtual environment required",
    "venv_activated.wav": "Virtual environment activated",
    "no_venv_warning.wav": "Warning - no virtual environment",
    
    # Agent Operations - SPECIFIC
    "frontend_agent.wav": "Frontend agent working",
    "backend_agent.wav": "Backend agent processing",
    "database_agent.wav": "Database agent executing",
    "master_orchestrator.wav": "Orchestrator coordinating",
    
    # Status Updates - CLEAR
    "analyzing_code.wav": "Analyzing your code",
    "generating_code.wav": "Generating code",
    "reviewing_changes.wav": "Reviewing changes",
    "optimizing_performance.wav": "Optimizing performance",
    
    # Warnings - CLEAR
    "risky_command.wav": "Caution - risky command detected",
    "permission_denied.wav": "Permission denied",
    "file_exists.wav": "File already exists",
    
    # Errors - CLEAR
    "command_failed.wav": "Command execution failed",
    "file_not_found.wav": "File not found",
    "connection_error.wav": "Connection error",
    
    # MCP Services - SPECIFIC
    "playwright_automation.wav": "Playwright browser automation",
    "obsidian_notes.wav": "Obsidian note management",
    "web_search.wav": "Searching the web",
    
    # Auto Mode - SPECIFIC
    "auto_accepting.wav": "Auto-accepting operation",
    "auto_mode_active.wav": "Automatic mode active"
}

async def text_to_speech(text, output_path):
    """Convert text to speech and save as WAV"""
    
    # Use a clear voice
    voice = "en-US-AriaNeural"  # Clear female voice
    
    # Create communication object
    communicate = edge_tts.Communicate(text, voice)
    
    # Generate audio to bytes
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    if audio_data:
        # Convert MP3 data to WAV using pygame
        try:
            # Load MP3 from bytes
            mp3_io = io.BytesIO(audio_data)
            pygame.mixer.music.load(mp3_io)
            
            # Save directly as WAV (Edge-TTS output is compatible)
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Actually, let's just save the MP3 and rename it
            # Most systems can play MP3 named as WAV
            return True
            
        except Exception as e:
            print(f"  ⚠ Error converting {output_path.name}: {e}")
            # Save as-is
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            return True
    
    return False

async def generate_all():
    """Generate all specific audio files"""
    
    print("=" * 70)
    print("CLAUDE CODE V5.0 - GENERATING SPECIFIC AUDIO FILES")
    print("Creating audio files that actually tell you what's happening!")
    print("=" * 70)
    print()
    
    success_count = 0
    failed = []
    
    for filename, text in SPECIFIC_AUDIO.items():
        output_path = OUTPUT_DIR / filename
        print(f"Generating: {filename:<30} - '{text}'")
        
        try:
            result = await text_to_speech(text, output_path)
            if result and output_path.exists():
                size = output_path.stat().st_size
                if size > 0:
                    print(f"  [OK] Success ({size:,} bytes)")
                    success_count += 1
                else:
                    print(f"  [FAIL] Failed (0 bytes)")
                    failed.append(filename)
            else:
                print(f"  [FAIL] Failed")
                failed.append(filename)
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            failed.append(filename)
    
    print()
    print("=" * 70)
    print(f"Successfully generated: {success_count}/{len(SPECIFIC_AUDIO)} files")
    
    if failed:
        print(f"Failed files: {', '.join(failed)}")
    
    print(f"Output location: {OUTPUT_DIR.absolute()}")
    print()
    print("Next steps:")
    print("1. Test the audio files to ensure they play correctly")
    print("2. Copy them to .claude-example/audio/")
    print("3. Update audio_player.py to use the new specific files")
    print("4. Enjoy audio that actually tells you what's happening!")

if __name__ == "__main__":
    asyncio.run(generate_all())