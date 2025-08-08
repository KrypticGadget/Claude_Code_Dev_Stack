#!/usr/bin/env python3
"""
Convert Edge-TTS MP3 files (mislabeled as .wav) to real PCM WAV files
"""

import os
import sys
from pathlib import Path

def check_file_format(file_path):
    """Check the actual format of the file"""
    with open(file_path, 'rb') as f:
        header = f.read(4)
    
    if header[:2] == b'\xff\xfb' or header[:2] == b'\xff\xf3':
        return "MP3"
    elif header == b'RIFF':
        return "WAV"
    else:
        return "Unknown"

def convert_mp3_to_wav_with_pygame():
    """
    Use pygame to convert MP3 to WAV
    Pygame can read MP3 and we can save as WAV
    """
    try:
        import pygame
        print("Using pygame for conversion...")
        return True
    except ImportError:
        print("pygame not installed. Installing...")
        os.system("pip install pygame")
        return False

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    sounds_dir = base_dir / "sounds"
    clean_dir = base_dir / "sounds_clean"
    
    # Create output directory
    clean_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("MP3 to WAV Converter")
    print("Converting Edge-TTS MP3 files to real WAV files")
    print("=" * 60)
    
    # Check file formats
    wav_files = list(sounds_dir.glob("*.wav"))
    print(f"\nChecking {len(wav_files)} files...")
    
    mp3_count = 0
    for wav_file in wav_files[:5]:  # Check first 5
        format_type = check_file_format(wav_file)
        if format_type == "MP3":
            mp3_count += 1
        print(f"  {wav_file.name}: {format_type}")
    
    if mp3_count > 0:
        print(f"\nFound MP3 files with .wav extension!")
        print("These files need to be properly converted.")
    
    # Try pygame conversion
    print("\n" + "-" * 40)
    print("Installing pygame for conversion...")
    os.system("pip install pygame")
    
    print("\nTesting pygame conversion...")
    test_script = base_dir / "pygame_converter.py"
    
    with open(test_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Convert MP3 files to WAV using pygame"""
import pygame
from pathlib import Path
import wave
import struct

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def convert_file(input_file, output_file):
    """Convert MP3 to WAV using pygame"""
    try:
        # Load the MP3 file
        sound = pygame.mixer.Sound(str(input_file))
        
        # Get the raw audio data
        raw_data = sound.get_raw()
        
        # Save as WAV file
        with wave.open(str(output_file), 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            wav_file.writeframes(raw_data)
        
        print(f"Converted: {input_file.name} -> {output_file.name}")
        return True
        
    except Exception as e:
        print(f"Failed: {input_file.name} - {e}")
        return False

if __name__ == "__main__":
    sounds_dir = Path(__file__).parent / "sounds"
    clean_dir = Path(__file__).parent / "sounds_clean"
    clean_dir.mkdir(exist_ok=True)
    
    files = list(sounds_dir.glob("*.wav"))
    success = 0
    
    for file in files:
        output = clean_dir / file.name
        if convert_file(file, output):
            success += 1
    
    print(f"\\nConverted {success}/{len(files)} files")
    print(f"Clean files saved to: {clean_dir}")
    
    # Test with winsound
    print("\\nTesting with winsound...")
    try:
        import winsound
        test_file = clean_dir / "project_created.wav"
        if test_file.exists():
            winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
            print("SUCCESS: File plays correctly!")
    except Exception as e:
        print(f"Test failed: {e}")
''')
    
    print(f"Created converter script: {test_script}")
    print("\nRun the converter:")
    print(f"  python {test_script.name}")
    
    # Alternative solution
    print("\n" + "=" * 60)
    print("IMPORTANT DISCOVERY:")
    print("The Edge-TTS files are actually MP3 format, not WAV!")
    print("They have .wav extension but contain MP3 data.")
    print("\nSolutions:")
    print("1. Run: python pygame_converter.py (after installing pygame)")
    print("2. Use ffmpeg to convert: ffmpeg -i input.wav output_real.wav")
    print("3. Regenerate with Edge-TTS using --codec pcm option")
    print("=" * 60)

if __name__ == "__main__":
    main()