#!/usr/bin/env python3
"""
Audio File Consolidation Script
Merges old and new audio files, removes defunct ones, creates final audio directory
"""

import asyncio
import edge_tts
import os
import shutil
from pathlib import Path
import wave
import pygame

# Initialize pygame for audio conversion
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Define all audio files needed for the enhanced system
REQUIRED_FILES = {
    # Core System Files
    "project_created": "Project structure initialized successfully",
    "ready_for_input": "Ready for your input",
    "agent_activated": "Agent activated",
    "pipeline_complete": "Pipeline complete",
    "pipeline_initiated": "Pipeline initiated",
    
    # File Operation Files
    "confirm_required": "Confirmation required",
    "file_operation_pending": "File operation pending",
    "file_operation_complete": "File operation complete",
    
    # Command Execution Files
    "command_execution_pending": "Command awaiting approval",
    "command_successful": "Command executed successfully",
    
    # Planning Files
    "planning_complete": "Planning complete",
    
    # State Files
    "processing": "Processing",
    "analyzing": "Analyzing requirements",
    "working": "Working on your request",
    "awaiting_input": "Awaiting your input",
    
    # Completion Files
    "milestone_complete": "Milestone achieved",
    "operation_complete": "Operation completed successfully",
    "phase_complete": "Phase completed",
    
    # Decision Files
    "decision_required": "Decision required to proceed",
    
    # Fallback Files (keep existing)
    "awaiting_confirmation": "Awaiting confirmation",
    "permission_required": "Permission required",
    "build_successful": "Build successful"
}

# Files that already exist and should be kept as-is
EXISTING_KEEP = [
    "project_created",
    "ready_for_input", 
    "agent_activated",
    "pipeline_complete",
    "milestone_complete",
    "awaiting_confirmation",
    "permission_required",
    "build_successful"
]

async def generate_audio_file(filename, text, output_dir, voice="en-GB-RyanNeural"):
    """Generate a single audio file using Edge-TTS and convert to PCM WAV"""
    try:
        # Generate with Edge-TTS
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate="-5%",      # Slightly slower for clarity
            pitch="-5Hz"      # Slightly lower for authority
        )
        
        # Save as temp MP3
        temp_file = output_dir / f"_temp_{filename}.mp3"
        await communicate.save(str(temp_file))
        
        # Convert to WAV using pygame
        sound = pygame.mixer.Sound(str(temp_file))
        raw_data = sound.get_raw()
        
        # Save as PCM WAV
        output_file = output_dir / f"{filename}.wav"
        with wave.open(str(output_file), 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            wav_file.writeframes(raw_data)
        
        # Remove temp file
        if temp_file.exists():
            temp_file.unlink()
        
        return True
    except Exception as e:
        print(f"  [FAIL] {filename}.wav - Error: {e}")
        return False

async def consolidate_audio():
    """Main consolidation function"""
    print("Audio File Consolidation System")
    print("=" * 60)
    
    # Define directories
    original_dir = Path("TTS/sounds")
    final_dir = Path("TTS/audio_final")
    
    # Create final directory
    final_dir.mkdir(parents=True, exist_ok=True)
    
    # Voice selection
    voices = {
        'professional': "en-US-GuyNeural",      # Professional male
        'friendly': "en-US-AriaNeural",         # Friendly female  
        'jarvis': "en-GB-RyanNeural",          # British male (JARVIS-style)
        'alert': "en-US-JennyNeural"           # Clear female for alerts
    }
    
    print(f"\nTotal files needed: {len(REQUIRED_FILES)}")
    print(f"Existing files to keep: {len(EXISTING_KEEP)}")
    print(f"New files to generate: {len(REQUIRED_FILES) - len(EXISTING_KEEP)}")
    
    # Step 1: Copy existing files that we're keeping
    print("\n" + "-" * 40)
    print("Step 1: Copying existing files...")
    copied = 0
    for filename in EXISTING_KEEP:
        src = original_dir / f"{filename}.wav"
        dst = final_dir / f"{filename}.wav"
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  [COPY] {filename}.wav")
            copied += 1
        else:
            print(f"  [MISS] {filename}.wav - not found in original")
    
    # Step 2: Generate new files
    print("\n" + "-" * 40)
    print("Step 2: Generating new files...")
    generated = 0
    
    for filename, text in REQUIRED_FILES.items():
        # Skip if already copied
        if filename in EXISTING_KEEP and (final_dir / f"{filename}.wav").exists():
            continue
        
        # Choose voice based on content
        if "required" in text.lower() or "pending" in text.lower():
            voice = voices['alert']  # Alert voice for confirmations
        elif "complete" in text.lower() or "successful" in text.lower():
            voice = voices['friendly']  # Friendly for completions
        elif "analyzing" in text.lower() or "processing" in text.lower():
            voice = voices['jarvis']  # JARVIS for processing
        else:
            voice = voices['professional']  # Default professional
        
        if await generate_audio_file(filename, text, final_dir, voice):
            print(f"  [GEN] {filename}.wav - '{text}'")
            generated += 1
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    print("CONSOLIDATION COMPLETE")
    print(f"  Files copied: {copied}")
    print(f"  Files generated: {generated}")
    print(f"  Total files: {len(list(final_dir.glob('*.wav')))}")
    print(f"  Location: {final_dir.absolute()}")
    
    # Step 4: Test playback
    print("\nTesting audio playback...")
    try:
        import winsound
        test_file = final_dir / "ready_for_input.wav"
        if test_file.exists():
            winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
            print("[OK] Audio playback successful!")
            print("You should have heard: 'Ready for your input'")
    except Exception as e:
        print(f"[ERROR] Playback test failed: {e}")
    
    # Step 5: Instructions
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Copy final audio files to .claude-example/audio/:")
    print("   Copy-Item 'TTS\\audio_final\\*.wav' '.claude-example\\audio\\' -Force")
    print("")
    print("2. Then copy to your Claude directory:")
    print("   Copy-Item '.claude-example\\audio\\*.wav' 'C:\\Users\\Zach\\.claude\\audio\\' -Force")
    print("")
    print("3. Copy the enhanced hook:")
    print("   Copy-Item '.claude-example\\hooks\\audio_player.py' 'C:\\Users\\Zach\\.claude\\hooks\\' -Force")
    print("")
    print("4. Copy the settings:")
    print("   Copy-Item '.claude-example\\settings.json' 'C:\\Users\\Zach\\.claude\\settings.json' -Force")
    print("")
    print("5. Restart Claude Code")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(consolidate_audio())