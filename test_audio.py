#!/usr/bin/env python3
"""Test script to find the best audio playback method for Windows"""

import subprocess
import sys
from pathlib import Path

audio_dir = Path.home() / ".claude" / "audio"
test_file = audio_dir / "ready.mp3"

if not test_file.exists():
    print(f"ERROR: Audio file not found: {test_file}")
    sys.exit(1)

print(f"Testing audio playback for: {test_file}")
print("-" * 50)

# Test 1: pygame
print("Test 1: pygame...")
try:
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(str(test_file))
    pygame.mixer.music.play()
    print("✓ pygame works! (Best option - install with: pip install pygame)")
except ImportError:
    print("✗ pygame not installed")
except Exception as e:
    print(f"✗ pygame error: {e}")

# Test 2: Simple Windows start command
print("\nTest 2: Windows start command...")
try:
    # This should play without minimizing
    subprocess.run(
        f'start /b "" "{test_file}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("✓ Windows start command works!")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: VLC if installed
print("\nTest 3: VLC...")
vlc_paths = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
]
vlc_found = False
for vlc_path in vlc_paths:
    if Path(vlc_path).exists():
        try:
            subprocess.Popen(
                [vlc_path, "--intf", "dummy", "--play-and-exit", str(test_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✓ VLC works! Found at: {vlc_path}")
            vlc_found = True
            break
        except Exception as e:
            print(f"✗ VLC error: {e}")
if not vlc_found:
    print("✗ VLC not installed")

# Test 4: PowerShell with WMPlayer COM
print("\nTest 4: PowerShell WMPlayer COM...")
try:
    ps_script = f'''
    $wmp = New-Object -ComObject WMPlayer.OCX
    $wmp.URL = "{test_file}"
    $wmp.settings.volume = 100
    $wmp.controls.play()
    Start-Sleep -Seconds 3
    '''
    
    result = subprocess.run(
        ['powershell', '-NoProfile', '-Command', ps_script],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print("✓ PowerShell WMPlayer works!")
    else:
        print(f"✗ PowerShell error: {result.stderr}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)
print("RECOMMENDATION:")
print("1. Install pygame for best results: pip install pygame")
print("2. Otherwise, the 'start /b' command should work")
print("=" * 50)