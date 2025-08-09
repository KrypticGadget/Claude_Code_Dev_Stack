#!/usr/bin/env python3
"""
Direct test of audio playback to debug why hooks aren't playing
"""

import sys
import os
from pathlib import Path

# Add debug output
print("[TEST] Starting direct audio test", file=sys.stderr)
print(f"[TEST] Python version: {sys.version}", file=sys.stderr)
print(f"[TEST] Working directory: {os.getcwd()}", file=sys.stderr)

# Check audio file exists
audio_dir = Path.home() / ".claude" / "audio"
test_file = audio_dir / "project_created.wav"

print(f"[TEST] Audio directory: {audio_dir}", file=sys.stderr)
print(f"[TEST] Test file: {test_file}", file=sys.stderr)
print(f"[TEST] File exists: {test_file.exists()}", file=sys.stderr)

if test_file.exists():
    print(f"[TEST] File size: {test_file.stat().st_size} bytes", file=sys.stderr)
    
    # Test 1: winsound (most reliable)
    print("[TEST] Trying winsound...", file=sys.stderr)
    try:
        import winsound
        # Try both sync and async
        print("[TEST] Playing with SND_FILENAME | SND_ASYNC", file=sys.stderr)
        winsound.PlaySound(str(test_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
        print("[TEST] winsound async call completed", file=sys.stderr)
        
        # Try sync to ensure it plays
        import time
        time.sleep(0.5)
        print("[TEST] Playing with SND_FILENAME sync", file=sys.stderr)
        winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
        print("[TEST] winsound SUCCESS!", file=sys.stderr)
    except Exception as e:
        print(f"[TEST] winsound failed: {e}", file=sys.stderr)
    
    # Test 2: pygame
    print("[TEST] Trying pygame...", file=sys.stderr)
    try:
        import pygame
        print("[TEST] pygame imported", file=sys.stderr)
        
        # Initialize mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print("[TEST] pygame mixer initialized", file=sys.stderr)
        
        # Load and play
        sound = pygame.mixer.Sound(str(test_file))
        print(f"[TEST] Sound loaded, length: {sound.get_length()}s", file=sys.stderr)
        
        channel = sound.play()
        print(f"[TEST] Playing on channel: {channel}", file=sys.stderr)
        
        # Wait for completion
        import time
        while channel and channel.get_busy():
            time.sleep(0.1)
        
        print("[TEST] pygame SUCCESS!", file=sys.stderr)
        pygame.mixer.quit()
    except Exception as e:
        print(f"[TEST] pygame failed: {e}", file=sys.stderr)
    
    # Test 3: subprocess with start command
    print("[TEST] Trying Windows start command...", file=sys.stderr)
    try:
        import subprocess
        # Use Windows 'start' command to play in default player
        subprocess.run(["cmd", "/c", "start", "/min", "", str(test_file)], 
                      shell=False, capture_output=True)
        print("[TEST] Windows start command executed", file=sys.stderr)
    except Exception as e:
        print(f"[TEST] start command failed: {e}", file=sys.stderr)
    
else:
    print(f"[TEST] ERROR: Test file does not exist!", file=sys.stderr)
    print(f"[TEST] Looking for files in {audio_dir}:", file=sys.stderr)
    if audio_dir.exists():
        wav_files = list(audio_dir.glob("*.wav"))
        print(f"[TEST] Found {len(wav_files)} .wav files", file=sys.stderr)
        for f in wav_files[:5]:
            print(f"[TEST]   - {f.name} ({f.stat().st_size} bytes)", file=sys.stderr)

print("[TEST] Direct audio test complete", file=sys.stderr)