#!/usr/bin/env python3
"""
Generate new audio files for enhanced Claude Code audio system
These are the missing/new audio files needed for the improved hook system
"""

import asyncio
import edge_tts
import os
from pathlib import Path
import wave

# New audio files needed for enhanced system
NEW_AUDIO_FILES = {
    # Pre-confirmation alerts (3)
    "confirm_required": "Confirmation required",
    "command_execution_pending": "Command awaiting approval", 
    "file_operation_pending": "File operation pending",
    
    # Completion sounds (4)
    "file_operation_complete": "File operation complete",
    "command_successful": "Command executed successfully",
    "planning_complete": "Planning complete",
    "ready_for_input": "Ready for your input",
    
    # Status updates (3)
    "processing": "Processing",
    "working": "Working on your request",
    "analyzing": "Analyzing requirements",
    
    # Enhanced states (5)
    "phase_complete": "Phase completed",
    "pipeline_initiated": "Pipeline initiated", 
    "awaiting_input": "Awaiting your input",
    "operation_complete": "Operation completed successfully",
    "decision_required": "Decision required to proceed"
}

async def generate_audio_files():
    """Generate the new audio files"""
    
    print("Enhanced Audio System - New File Generation")
    print("=" * 60)
    print(f"Generating {len(NEW_AUDIO_FILES)} new audio files...")
    print()
    
    # Check pygame is installed for conversion
    try:
        import pygame
        print("[OK] pygame is installed for WAV conversion")
    except ImportError:
        print("Installing pygame...")
        os.system("pip install pygame")
        import pygame
    
    # Initialize pygame for conversion
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    # Output directory
    output_dir = Path(__file__).parent.parent / "sounds_new"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Voice selection
    voices = {
        'professional': "en-US-GuyNeural",      # Professional male
        'friendly': "en-US-AriaNeural",         # Friendly female  
        'jarvis': "en-GB-RyanNeural",          # British male (JARVIS-style)
        'alert': "en-US-JennyNeural"           # Clear female for alerts
    }
    
    success_count = 0
    
    print("Generating files...")
    print("-" * 40)
    
    for filename, text in NEW_AUDIO_FILES.items():
        try:
            # Choose voice based on content type
            if "required" in text.lower() or "pending" in text.lower():
                voice = voices['alert']  # Alert voice for confirmations
            elif "complete" in text.lower() or "successful" in text.lower():
                voice = voices['friendly']  # Friendly for completions
            elif "analyzing" in text.lower() or "processing" in text.lower():
                voice = voices['jarvis']  # JARVIS for processing
            else:
                voice = voices['professional']  # Default professional
            
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
            
            print(f"  [OK] {filename}.wav - '{text}'")
            success_count += 1
            
        except Exception as e:
            print(f"  [FAIL] {filename}.wav - Error: {e}")
    
    print("-" * 40)
    print(f"\nGenerated {success_count}/{len(NEW_AUDIO_FILES)} files")
    print(f"Location: {output_dir}")
    
    # Test playback
    if success_count > 0:
        print("\nTesting playback...")
        try:
            import winsound
            test_file = output_dir / "ready_for_input.wav"
            if test_file.exists():
                winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
                print("[OK] Audio playback successful!")
                print("You should have heard: 'Ready for your input'")
        except Exception as e:
            print(f"[ERROR] Playback test failed: {e}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Copy new files to C:\\Users\\Zach\\.claude\\audio\\")
    print("   Copy-Item 'TTS\\sounds_new\\*.wav' 'C:\\Users\\Zach\\.claude\\audio\\' -Force")
    print("2. Update your hooks:")
    print("   Copy-Item '.claude-example\\hooks\\audio_player.py' 'C:\\Users\\Zach\\.claude\\hooks\\' -Force")
    print("   Copy-Item '.claude-example\\settings.json' 'C:\\Users\\Zach\\.claude\\settings.json' -Force")
    print("3. Restart Claude Code")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(generate_audio_files())