#!/usr/bin/env python3
"""
Simple conversion using simpleaudio to test and convert files
"""

import os
import sys
from pathlib import Path
import struct
import wave

def read_edge_tts_wav(file_path):
    """
    Read Edge-TTS WAV file and extract audio data
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        # Edge-TTS files might have a different structure
        # Let's try to find the audio data
        print(f"  File size: {len(data)} bytes")
        
        # Check if it starts with RIFF
        if data[:4] == b'RIFF':
            print("  Format: Standard RIFF WAV")
            return data
        else:
            print(f"  Format: Non-standard (starts with {data[:4]})")
            # File might still contain valid audio data
            return data
            
    except Exception as e:
        print(f"  Error reading file: {e}")
        return None

def test_with_simpleaudio(file_path):
    """
    Test if simpleaudio can play the file
    """
    try:
        import simpleaudio as sa
        wave_obj = sa.WaveObject.from_wave_file(str(file_path))
        print(f"  SimpleAudio can read: channels={wave_obj.num_channels}, rate={wave_obj.sample_rate}, width={wave_obj.bytes_per_sample}")
        return True
    except Exception as e:
        print(f"  SimpleAudio cannot read: {e}")
        return False

def convert_with_edge_tts_regenerate():
    """
    Alternative: regenerate files with different Edge-TTS settings
    """
    print("\nAlternative Solution:")
    print("-" * 40)
    print("The Edge-TTS files are in a format that Windows audio APIs cannot play.")
    print("We need to either:")
    print("1. Install ffmpeg and use it to convert the files")
    print("2. Use pygame for playback (pip install pygame)")
    print("3. Regenerate the files with different Edge-TTS settings")
    print("\nRecommended: Install pygame for playback")
    print("Run: pip install pygame")

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    sounds_dir = base_dir / "sounds"
    
    print("=" * 60)
    print("WAV File Analysis Tool")
    print("=" * 60)
    
    # Get all WAV files
    wav_files = list(sounds_dir.glob("*.wav"))
    print(f"\nFound {len(wav_files)} WAV files")
    
    # Analyze first few files
    print("\nAnalyzing files...")
    print("-" * 40)
    
    for i, wav_file in enumerate(wav_files[:3]):  # Just test first 3
        print(f"\n{i+1}. {wav_file.name}:")
        
        # Read raw data
        data = read_edge_tts_wav(wav_file)
        
        # Test with simpleaudio
        test_with_simpleaudio(wav_file)
        
        # Try to play with winsound
        try:
            import winsound
            winsound.PlaySound(str(wav_file), winsound.SND_FILENAME)
            print("  Winsound: Can play")
        except Exception as e:
            print(f"  Winsound: Cannot play - {type(e).__name__}")
    
    print("\n" + "-" * 40)
    convert_with_edge_tts_regenerate()
    
    # Create a test script for pygame
    print("\n" + "=" * 60)
    print("Creating pygame test script...")
    
    pygame_script = base_dir / "test_pygame_playback.py"
    with open(pygame_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Test pygame playback of Edge-TTS files"""
import pygame
from pathlib import Path

def play_wav_with_pygame(file_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(str(file_path))
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print(f"Successfully played: {file_path.name}")
        return True
    except Exception as e:
        print(f"Failed to play {file_path.name}: {e}")
        return False

if __name__ == "__main__":
    sounds_dir = Path(__file__).parent / "sounds"
    test_file = sounds_dir / "project_created.wav"
    
    if test_file.exists():
        print(f"Testing: {test_file}")
        if play_wav_with_pygame(test_file):
            print("SUCCESS: pygame can play Edge-TTS files!")
            print("Install pygame system-wide: pip install pygame")
    else:
        print(f"File not found: {test_file}")
''')
    
    print(f"Created: {pygame_script}")
    print("\nTo test pygame playback:")
    print("1. pip install pygame")
    print("2. python test_pygame_playback.py")

if __name__ == "__main__":
    main()