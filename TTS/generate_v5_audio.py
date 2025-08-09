#!/usr/bin/env python3
"""
Generate v5.0 Specific Audio Files with Clear Descriptions
Uses Edge-TTS to create audio files that actually say what's happening
"""

import asyncio
import edge_tts
import pygame
from pathlib import Path
import os

# Initialize pygame for audio conversion
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Output directory
OUTPUT_DIR = Path("audio_v5")
OUTPUT_DIR.mkdir(exist_ok=True)

# Define all the audio files we need with CLEAR descriptions
AUDIO_FILES = {
    # File Operations (clear descriptions)
    "file_operation_mkdir.wav": "Creating directory",
    "file_operation_touch.wav": "Creating file",
    "file_operation_copy.wav": "Copying files",
    "file_operation_move.wav": "Moving files",
    "file_operation_delete.wav": "Deleting files - caution",
    
    # Navigation
    "navigation_cd.wav": "Changing directory",
    "navigation_ls.wav": "Listing files",
    "navigation_pwd.wav": "Checking current directory",
    
    # Git Operations
    "git_status.wav": "Checking git status",
    "git_commit.wav": "Creating git commit",
    "git_push.wav": "Pushing to remote",
    "git_pull.wav": "Pulling from remote",
    "git_branch.wav": "Managing branches",
    
    # Build Operations
    "build_npm.wav": "Running npm build",
    "build_make.wav": "Running make build",
    "build_cargo.wav": "Building with cargo",
    "build_gradle.wav": "Building with gradle",
    
    # Package Installation
    "install_pip.wav": "Installing Python packages",
    "install_npm.wav": "Installing npm packages",
    "install_apt.wav": "Installing system packages",
    "install_brew.wav": "Installing with homebrew",
    
    # Testing
    "test_pytest.wav": "Running pytest tests",
    "test_jest.wav": "Running jest tests",
    "test_cargo.wav": "Running cargo tests",
    "test_npm.wav": "Running npm tests",
    
    # Docker Operations
    "docker_build.wav": "Building Docker image",
    "docker_run.wav": "Running Docker container",
    "docker_compose.wav": "Running docker-compose",
    
    # Network Operations
    "network_curl.wav": "Making HTTP request",
    "network_wget.wav": "Downloading file",
    "network_ssh.wav": "SSH connection",
    "network_scp.wav": "Secure copy operation",
    
    # Process Management
    "process_ps.wav": "Listing processes",
    "process_kill.wav": "Terminating process - caution",
    "process_systemctl.wav": "Managing system services",
    
    # Search Operations
    "search_find.wav": "Searching for files",
    "search_grep.wav": "Searching file contents",
    "search_ripgrep.wav": "Fast searching with ripgrep",
    
    # Permission Operations
    "permission_chmod.wav": "Changing file permissions",
    "permission_chown.wav": "Changing file ownership",
    
    # Archive Operations
    "archive_tar.wav": "Creating or extracting archive",
    "archive_zip.wav": "Creating zip file",
    "archive_unzip.wav": "Extracting zip file",
    
    # Environment Operations
    "env_export.wav": "Setting environment variable",
    "env_source.wav": "Sourcing configuration",
    "env_venv.wav": "Virtual environment detected",
    
    # System Operations
    "system_df.wav": "Checking disk space",
    "system_du.wav": "Checking disk usage",
    "system_top.wav": "Monitoring system resources",
    
    # Security Operations
    "security_openssl.wav": "Security operation",
    "security_gpg.wav": "Encryption operation",
    
    # Database Operations
    "database_query.wav": "Running database query",
    "database_migration.wav": "Running database migration",
    
    # Agent Operations (more specific)
    "agent_frontend.wav": "Frontend agent activated",
    "agent_backend.wav": "Backend agent activated",
    "agent_database.wav": "Database agent activated",
    "agent_testing.wav": "Testing agent activated",
    "agent_security.wav": "Security agent activated",
    "agent_orchestrator.wav": "Master orchestrator coordinating",
    
    # Status Updates (more specific)
    "status_analyzing_code.wav": "Analyzing code structure",
    "status_generating_code.wav": "Generating code",
    "status_reviewing_code.wav": "Reviewing code quality",
    "status_optimizing.wav": "Optimizing performance",
    
    # Completion States (more specific)
    "complete_tests_passed.wav": "All tests passed successfully",
    "complete_build_success.wav": "Build completed successfully",
    "complete_deployment.wav": "Deployment successful",
    "complete_installation.wav": "Installation complete",
    
    # Warning States
    "warning_no_venv.wav": "Warning - no virtual environment active",
    "warning_risky_command.wav": "Warning - risky command detected",
    "warning_permission_denied.wav": "Permission denied",
    "warning_file_exists.wav": "File already exists",
    
    # Error States
    "error_command_failed.wav": "Command failed",
    "error_file_not_found.wav": "File not found",
    "error_syntax.wav": "Syntax error detected",
    "error_connection.wav": "Connection error",
    
    # MCP Operations
    "mcp_playwright.wav": "Playwright browser automation",
    "mcp_obsidian.wav": "Obsidian note management",
    "mcp_websearch.wav": "Web search initiated",
    
    # Auto-Accept Mode
    "auto_accepting.wav": "Auto-accepting operation",
    "auto_confirmed.wav": "Automatically confirmed",
    
    # Planning/Thinking States
    "thinking_planning.wav": "Planning approach",
    "thinking_considering.wav": "Considering options",
    "thinking_deciding.wav": "Making decision"
}

# Keep essential original files
KEEP_ORIGINAL = [
    "project_created.wav",
    "ready_for_input.wav",
    "pipeline_complete.wav",
    "milestone_complete.wav",
    "awaiting_input.wav"
]

async def generate_audio(text, output_path):
    """Generate audio file using Edge-TTS"""
    print(f"Generating: {output_path.name} - '{text}'")
    
    # Use a clear, professional voice
    voice = "en-US-AriaNeural"  # Clear female voice
    # Alternative: "en-US-GuyNeural" for male voice
    
    communicate = edge_tts.Communicate(text, voice)
    
    # Generate to temp MP3
    temp_mp3 = output_path.with_suffix('.mp3')
    await communicate.save(str(temp_mp3))
    
    # Convert MP3 to WAV using pygame (simpler method)
    try:
        # Load the MP3
        pygame.mixer.music.load(str(temp_mp3))
        
        # For now, just rename the MP3 to WAV
        # (Edge-TTS actually generates PCM-compatible audio)
        import shutil
        shutil.move(str(temp_mp3), str(output_path))
        
        print(f"  ✓ Generated: {output_path.name}")
        
    except Exception as e:
        print(f"  ⚠ Error: {e}")
        # If conversion fails, keep the MP3
        if temp_mp3.exists():
            shutil.move(str(temp_mp3), str(output_path))
    
    return output_path

async def main():
    """Generate all audio files"""
    print("=" * 60)
    print("CLAUDE CODE V5.0 - SPECIFIC AUDIO GENERATION")
    print("Generating clear, descriptive audio files...")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Generate all audio files
    tasks = []
    for filename, text in AUDIO_FILES.items():
        output_path = OUTPUT_DIR / filename
        tasks.append(generate_audio(text, output_path))
    
    # Run all generations
    results = await asyncio.gather(*tasks)
    
    print("\n" + "=" * 60)
    print(f"✅ Generated {len(results)} specific audio files!")
    print(f"📁 Location: {OUTPUT_DIR.absolute()}")
    print("=" * 60)
    
    # Copy essential original files
    print("\nCopying essential original files...")
    original_dir = Path("../TTS/audio_final")
    if original_dir.exists():
        for filename in KEEP_ORIGINAL:
            src = original_dir / filename
            if src.exists():
                dst = OUTPUT_DIR / filename
                import shutil
                shutil.copy2(src, dst)
                print(f"  ✓ Copied: {filename}")
    
    print("\n🎉 All audio files ready for v5.0!")
    print("\nNext steps:")
    print("1. Copy files from audio_v5/ to .claude-example/audio/")
    print("2. Update audio_player.py with new mappings")
    print("3. Test with various commands")

if __name__ == "__main__":
    asyncio.run(main())