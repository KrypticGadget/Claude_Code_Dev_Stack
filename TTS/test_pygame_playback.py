#!/usr/bin/env python3
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
