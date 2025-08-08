#!/usr/bin/env python3
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
    
    print(f"\nConverted {success}/{len(files)} files")
    print(f"Clean files saved to: {clean_dir}")
    
    # Test with winsound
    print("\nTesting with winsound...")
    try:
        import winsound
        test_file = clean_dir / "project_created.wav"
        if test_file.exists():
            winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
            print("SUCCESS: File plays correctly!")
    except Exception as e:
        print(f"Test failed: {e}")
