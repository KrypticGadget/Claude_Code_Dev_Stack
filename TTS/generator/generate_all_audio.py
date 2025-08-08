#!/usr/bin/env python3
"""
Ultimate Claude Code Dev Stack - Audio Generation System
Generates all 50 audio notifications as real WAV files using Edge-TTS
Fixed to output proper PCM WAV format compatible with Windows audio APIs
"""

import asyncio
import edge_tts
import os
import sys
from pathlib import Path
import wave

# Complete audio system - 50 sounds
COMPLETE_AUDIO_SYSTEM = {
    # Development Phases (23)
    "project_created": "Project structure initialized successfully",
    "dependencies_installed": "All dependencies have been installed",
    "environment_ready": "Development environment is ready",
    "requirements_gathered": "Requirements analysis complete",
    "architecture_designed": "System architecture has been designed",
    "database_modeled": "Database schema design complete",
    "backend_complete": "Backend services implementation complete",
    "frontend_complete": "Frontend components ready",
    "api_integrated": "API integration successful",
    "auth_implemented": "Authentication system implemented",
    "unit_tests_pass": "All unit tests passing",
    "integration_tests_pass": "Integration tests successful",
    "e2e_tests_complete": "End-to-end testing complete",
    "coverage_achieved": "Code coverage target achieved",
    "build_started": "Build process initiated",
    "build_progress": "Build in progress, please wait",
    "build_successful": "Build completed successfully",
    "build_optimized": "Production build optimized",
    "deploy_initiated": "Deployment sequence initiated",
    "deploy_validation": "Deployment validation in progress",
    "deploy_complete": "Application deployed successfully",
    "rollback_complete": "Rollback completed successfully",
    "milestone_complete": "Development milestone achieved",
    
    # Input Detection (15)
    "awaiting_response": "Awaiting your response",
    "awaiting_confirmation": "Please confirm to proceed",
    "awaiting_selection": "Please make a selection",
    "awaiting_details": "Additional details required",
    "awaiting_code_review": "Ready for your code review",
    "yes_no_question": "Please respond with yes or no",
    "multiple_choice": "Please select from the options provided",
    "clarification_needed": "Clarification needed to continue",
    "permission_required": "Your permission is required to proceed",
    "ready_for_input": "Ready for your next instruction",
    "processing_complete": "Processing complete, what's next?",
    "task_paused": "Task paused, awaiting guidance",
    "decision_point": "Decision point reached",
    "gentle_reminder": "Reminder: waiting for your input",
    "still_waiting": "Still awaiting your response",
    
    # Agent Orchestration (12)
    "agent_activated": "Agent activated",
    "agent_team_suggested": "Team collaboration recommended",
    "meta_prompt_transforming": "Optimizing prompt for execution",
    "orchestrator_engaged": "Master orchestrator engaged",
    "mcp_service_starting": "MCP service initializing",
    "parallel_execution": "Executing tasks in parallel",
    "sequential_execution": "Processing tasks sequentially",
    "handoff_occurring": "Agent handoff in progress",
    "optimization_applied": "Performance optimization applied",
    "context_switching": "Switching execution context",
    "pipeline_complete": "Pipeline execution complete",
    "coordination_active": "Multi-agent coordination active"
}

async def generate_all_audio():
    """Generate all audio files as real WAV files"""
    
    print("ULTIMATE Claude Code Dev Stack - Audio Generation (FIXED)")
    print("=" * 60)
    print(f"Generating {len(COMPLETE_AUDIO_SYSTEM)} audio files as real WAV...")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    
    # Install pygame if needed
    try:
        import pygame
        print("  [OK] pygame is installed")
    except ImportError:
        print("  Installing pygame for WAV conversion...")
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
    
    print()
    
    # Initialize pygame for audio conversion
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    # Create output directory - TTS/sounds folder
    output_dir = Path(__file__).parent.parent / "sounds"  # Goes to TTS/sounds/
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Best voices for different types
    voices = {
        'jarvis': "en-GB-RyanNeural",       # British male (JARVIS-style)
        'professional': "en-US-GuyNeural",   # Professional male
        'friendly': "en-US-AriaNeural",      # Friendly female
        'alert': "en-US-JennyNeural"         # Clear female
    }
    
    # Track progress
    total = len(COMPLETE_AUDIO_SYSTEM)
    current = 0
    success = 0
    failed = 0
    
    # Categories for organization
    categories = {
        'development': [],
        'input': [],
        'orchestration': []
    }
    
    # Categorize sounds
    for filename, text in COMPLETE_AUDIO_SYSTEM.items():
        if any(keyword in filename for keyword in ['project', 'build', 'deploy', 'test', 'backend', 'frontend', 'api', 'auth', 'database', 'requirements', 'architecture', 'environment', 'dependencies', 'coverage', 'rollback', 'milestone']):
            categories['development'].append((filename, text))
        elif any(keyword in filename for keyword in ['awaiting', 'question', 'choice', 'clarification', 'permission', 'input', 'reminder', 'waiting', 'decision']):
            categories['input'].append((filename, text))
        else:
            categories['orchestration'].append((filename, text))
    
    # Generate by category
    for category, items in categories.items():
        print(f"\n{category.upper()} ({len(items)} files)")
        print("-" * 40)
        
        for filename, text in items:
            current += 1
            
            try:
                # Choose voice based on category
                if category == 'input':
                    voice = voices['friendly']
                elif category == 'orchestration':
                    voice = voices['jarvis']
                else:
                    voice = voices['professional']
                
                # Generate audio with optimized settings
                communicate = edge_tts.Communicate(
                    text,
                    voice,
                    rate="-5%",      # Slightly slower for clarity
                    pitch="-5Hz"      # Slightly lower for authority
                )
                
                # First save as temporary MP3 (Edge-TTS default format)
                temp_file = output_dir / f"_temp_{filename}.mp3"
                await communicate.save(str(temp_file))
                
                # Convert MP3 to WAV using pygame
                sound = pygame.mixer.Sound(str(temp_file))
                raw_data = sound.get_raw()
                
                # Save as real PCM WAV file
                output_file = output_dir / f"{filename}.wav"
                with wave.open(str(output_file), 'wb') as wav_file:
                    wav_file.setnchannels(2)  # Stereo
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(44100)  # 44.1kHz
                    wav_file.writeframes(raw_data)
                
                # Remove temp MP3 file
                if temp_file.exists():
                    temp_file.unlink()
                
                # Progress indicator
                print(f"  [{current}/{total}] [OK] {filename}.wav")
                success += 1
                
            except Exception as e:
                print(f"  [{current}/{total}] [FAIL] {filename}.wav - Error: {e}")
                failed += 1
    
    print()
    print("=" * 60)
    
    if success == total:
        print(f"[OK] SUCCESS! All {total} audio files generated as real WAV!")
    else:
        print(f"Generated {success}/{total} files ({failed} failed)")
    
    print(f"\nLocation: {output_dir}")
    print("\nAudio System Ready:")
    print(f"  [OK] {len(categories['development'])} Development phase sounds")
    print(f"  [OK] {len(categories['input'])} Input detection sounds")
    print(f"  [OK] {len(categories['orchestration'])} Orchestration sounds")
    print("\n[OK] All files are in PCM WAV format compatible with winsound!")
    
    # Test with winsound
    print("\nTesting playback with winsound...")
    try:
        import winsound
        test_file = output_dir / "project_created.wav"
        if test_file.exists():
            print(f"  Playing: {test_file.name}")
            winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
            print("  [OK] SUCCESS! Audio plays correctly with winsound!")
            print("\nYou should have heard: 'Project structure initialized successfully'")
        else:
            print("  [FAIL] Test file not found")
    except Exception as e:
        print(f"  [FAIL] Playback test failed: {e}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Copy these files to C:\\Users\\Zach\\.claude\\audio\\")
    print("   Copy-Item '.claude-example\\audio\\*.wav' 'C:\\Users\\Zach\\.claude\\audio\\' -Force")
    print("2. Restart Claude Code")
    print("3. You should hear audio notifications!")
    print("=" * 60)

async def test_audio(filename):
    """Test a single audio file"""
    import subprocess
    import platform
    
    output_dir = Path(__file__).parent.parent
    audio_file = output_dir / f"{filename}.wav"
    
    if not audio_file.exists():
        print(f"File not found: {audio_file}")
        return
    
    print(f"Testing: {audio_file}")
    
    system = platform.system()
    if system == "Windows":
        import winsound
        winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
        print("[OK] Playback complete!")
    elif system == "Darwin":
        subprocess.run(["afplay", str(audio_file)])
    else:
        subprocess.run(["aplay", str(audio_file)])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode
        if len(sys.argv) > 2:
            asyncio.run(test_audio(sys.argv[2]))
        else:
            asyncio.run(test_audio("project_created"))
    else:
        # Generate all audio
        asyncio.run(generate_all_audio())