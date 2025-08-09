#!/usr/bin/env python3
"""
Audio Playback Diagnostic Tool
Tests different audio playback methods to identify what works
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def test_file_format(audio_path):
    """Check if file is proper WAV format"""
    print(f"\n[1] Testing file format: {audio_path}")
    
    if not audio_path.exists():
        print(f"   [FAIL] File does not exist!")
        return False
    
    # Check file header
    with open(audio_path, 'rb') as f:
        header = f.read(4)
    
    size = audio_path.stat().st_size
    print(f"   File size: {size:,} bytes")
    print(f"   Header: {header[:4]}")
    
    if header[:4] == b'RIFF':
        print(f"   [OK] File is proper WAV format")
        return True
    elif header[:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
        print(f"   [FAIL] File is MP3 format (not WAV)")
        return False
    else:
        print(f"   [UNKNOWN] Unknown format")
        return False

def test_winsound(audio_path):
    """Test winsound (most reliable for Windows WAV files)"""
    print(f"\n[2] Testing winsound playback...")
    
    try:
        import winsound
        print(f"   Playing with winsound...")
        winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)
        print(f"   [OK] winsound playback successful!")
        return True
    except Exception as e:
        print(f"   [FAIL] winsound error: {e}")
        return False

def test_pygame(audio_path):
    """Test pygame playback"""
    print(f"\n[3] Testing pygame playback...")
    
    try:
        import pygame
        print(f"   Initializing pygame mixer...")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        print(f"   Loading sound...")
        pygame.mixer.music.load(str(audio_path))
        
        print(f"   Playing...")
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()
        print(f"   [OK] pygame playback successful!")
        return True
    except Exception as e:
        print(f"   [FAIL] pygame error: {e}")
        try:
            pygame.mixer.quit()
        except:
            pass
        return False

def test_powershell(audio_path):
    """Test PowerShell Media.SoundPlayer"""
    print(f"\n[4] Testing PowerShell Media.SoundPlayer...")
    
    try:
        cmd = [
            "powershell", "-c",
            f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync()"
        ]
        print(f"   Running PowerShell command...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f"   [OK] PowerShell playback successful!")
            return True
        else:
            print(f"   [FAIL] PowerShell error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   [FAIL] PowerShell error: {e}")
        return False

def test_windows_media(audio_path):
    """Test Windows Media Player via COM"""
    print(f"\n[5] Testing Windows Media Player COM...")
    
    try:
        import win32com.client
        wmp = win32com.client.Dispatch("WMPlayer.OCX")
        media = wmp.newMedia(str(audio_path))
        wmp.currentMedia = media
        wmp.controls.play()
        time.sleep(1)  # Let it play
        print(f"   [OK] Windows Media Player playback successful!")
        return True
    except ImportError:
        print(f"   [SKIP] pywin32 not installed")
        return False
    except Exception as e:
        print(f"   [FAIL] Windows Media Player error: {e}")
        return False

def main():
    """Run all audio tests"""
    print("=" * 60)
    print("AUDIO PLAYBACK DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Test file to use
    audio_dir = Path.home() / ".claude" / "audio"
    test_files = ["project_created.wav", "mkdir_operation.wav", "git_status.wav"]
    
    audio_path = None
    for test_file in test_files:
        test_path = audio_dir / test_file
        if test_path.exists():
            audio_path = test_path
            break
    
    if not audio_path:
        print(f"\n[ERROR] No test audio files found in {audio_dir}")
        print(f"Looking for: {test_files}")
        return
    
    print(f"\nUsing test file: {audio_path}")
    print("=" * 60)
    
    # Run tests
    results = {}
    
    # Check format first
    is_wav = test_file_format(audio_path)
    results['format'] = is_wav
    
    if not is_wav:
        print("\n" + "=" * 60)
        print("[CRITICAL] File is not proper WAV format!")
        print("You need to copy the proper WAV files from:")
        print("  TTS/audio_v5_proper/")
        print("To:")
        print(f"  {audio_dir}")
        print("=" * 60)
        return
    
    # Test playback methods
    results['winsound'] = test_winsound(audio_path)
    results['pygame'] = test_pygame(audio_path)
    results['powershell'] = test_powershell(audio_path)
    results['wmp'] = test_windows_media(audio_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    working_methods = []
    for method, success in results.items():
        if success:
            print(f"  [OK] {method}")
            if method != 'format':
                working_methods.append(method)
        else:
            print(f"  [FAIL] {method}")
    
    print("\n" + "=" * 60)
    if working_methods:
        print(f"WORKING METHODS: {', '.join(working_methods)}")
        print(f"\nRECOMMENDATION: Use {working_methods[0]} as primary method")
    else:
        print("NO WORKING PLAYBACK METHODS FOUND!")
        print("\nTroubleshooting steps:")
        print("1. Ensure proper WAV files are in ~/.claude/audio/")
        print("2. Check Windows audio settings")
        print("3. Try running as administrator")
    print("=" * 60)

if __name__ == "__main__":
    main()