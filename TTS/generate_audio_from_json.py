#!/usr/bin/env python3
"""
Agnostic Audio Generator for Claude Code V3.0
Reads audio configuration from JSON and generates proper WAV files
Uses Edge-TTS + pygame for consistent PCM WAV format
"""

import asyncio
import json
import edge_tts
import pygame
import wave
from pathlib import Path
import os
import sys
import argparse

class AudioGenerator:
    def __init__(self, config_file="audio_config.json", output_dir="audio_v3_final"):
        """Initialize the audio generator with configuration"""
        self.config_file = Path(config_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load configuration
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        self.audio_files = self.config['audio_files']
        self.voice_settings = self.config.get('voice_settings', {})
        self.categories = self.config.get('categories', {})
        
        # Initialize pygame mixer for audio conversion
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
    def get_voice_settings(self, text, filename):
        """Determine voice settings based on text content and filename"""
        # Check for specific patterns
        if any(word in text.lower() for word in ['error', 'failed', 'denied']):
            return self.voice_settings.get('error', self.voice_settings['default'])
        elif any(word in text.lower() for word in ['warning', 'caution', 'risky']):
            return self.voice_settings.get('warning', self.voice_settings['default'])
        elif any(word in text.lower() for word in ['agent', 'orchestrator', 'jarvis']):
            return self.voice_settings.get('jarvis', self.voice_settings['default'])
        else:
            return self.voice_settings['default']
    
    async def generate_wav(self, filename, text):
        """Generate a proper PCM WAV file using Edge-TTS"""
        try:
            # Get voice settings
            settings = self.get_voice_settings(text, filename)
            
            # Generate with Edge-TTS
            communicate = edge_tts.Communicate(
                text,
                settings['voice'],
                rate=settings['rate'],
                pitch=settings['pitch']
            )
            
            # Save as temporary MP3
            temp_mp3 = self.output_dir / f"_temp_{filename}.mp3"
            await communicate.save(str(temp_mp3))
            
            # Convert MP3 to proper PCM WAV using pygame
            sound = pygame.mixer.Sound(str(temp_mp3))
            raw_data = sound.get_raw()
            
            # Save as proper WAV file
            output_file = self.output_dir / filename
            with wave.open(str(output_file), 'wb') as wav_file:
                wav_file.setnchannels(2)  # Stereo
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 44.1kHz
                wav_file.writeframes(raw_data)
            
            # Clean up temp file
            if temp_mp3.exists():
                temp_mp3.unlink()
            
            # Verify file
            size = output_file.stat().st_size
            return size > 1000, size  # Should be at least 1KB
            
        except Exception as e:
            print(f"    Error generating {filename}: {e}")
            return False, 0
    
    async def generate_all(self, filter_category=None):
        """Generate all audio files or filtered by category"""
        # Filter files if category specified
        if filter_category:
            if filter_category in self.categories:
                files_to_generate = {
                    f"{name}.wav" if not name.endswith('.wav') else name: self.audio_files[f"{name}.wav" if not name.endswith('.wav') else name]
                    for name in self.categories[filter_category]
                    if (f"{name}.wav" if not name.endswith('.wav') else name) in self.audio_files
                }
                print(f"Generating {len(files_to_generate)} files in category '{filter_category}'")
            else:
                print(f"Category '{filter_category}' not found. Available: {', '.join(self.categories.keys())}")
                return
        else:
            files_to_generate = self.audio_files
            print(f"Generating all {len(files_to_generate)} audio files")
        
        print("-" * 60)
        
        success_count = 0
        failed_files = []
        total = len(files_to_generate)
        current = 0
        
        for filename, text in files_to_generate.items():
            current += 1
            print(f"[{current:3}/{total}] {filename:<35} - '{text}'")
            
            success, size = await self.generate_wav(filename, text)
            
            if success:
                print(f"    [OK] Generated ({size:,} bytes)")
                success_count += 1
            else:
                print(f"    [FAIL] Failed")
                failed_files.append(filename)
        
        return success_count, failed_files, total
    
    def test_playback(self):
        """Test generated audio files with winsound"""
        try:
            import winsound
            
            # Find a test file
            test_files = ["startup.wav", "agent_activated.wav", "project_created.wav"]
            for test_file in test_files:
                test_path = self.output_dir / test_file
                if test_path.exists():
                    print(f"Testing playback: {test_file}")
                    winsound.PlaySound(str(test_path), winsound.SND_FILENAME)
                    print("  [OK] Playback successful!")
                    return True
            
            print("  No test files found")
            return False
            
        except Exception as e:
            print(f"  Could not test playback: {e}")
            return False

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate Claude Code V3.0 Audio Files")
    parser.add_argument('-c', '--config', default='audio_config.json', help='JSON config file')
    parser.add_argument('-o', '--output', default='audio_v3_final', help='Output directory')
    parser.add_argument('-f', '--filter', help='Filter by category (e.g., agents, git, v3)')
    parser.add_argument('-l', '--list', action='store_true', help='List categories only')
    parser.add_argument('-t', '--test', action='store_true', help='Test playback after generation')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CLAUDE CODE V3.0 - JSON-BASED AUDIO GENERATOR")
    print("=" * 70)
    
    # Check dependencies
    print("\nChecking dependencies...")
    
    try:
        import pygame
        print("  [OK] pygame installed")
    except ImportError:
        print("  Installing pygame...")
        os.system(f"{sys.executable} -m pip install pygame")
        import pygame
    
    try:
        import edge_tts
        print("  [OK] edge-tts installed")
    except ImportError:
        print("  Installing edge-tts...")
        os.system(f"{sys.executable} -m pip install edge-tts")
        import edge_tts
    
    # Initialize generator
    print(f"\nLoading configuration from: {args.config}")
    generator = AudioGenerator(args.config, args.output)
    
    # List categories if requested
    if args.list:
        print("\nAvailable categories:")
        for category, files in generator.categories.items():
            print(f"  - {category:<15} ({len(files)} files)")
        return
    
    # Generate audio files
    print(f"Output directory: {generator.output_dir.absolute()}\n")
    
    success, failed, total = await generator.generate_all(args.filter)
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    
    if success == total:
        print(f"[SUCCESS] All {total} audio files generated!")
    else:
        print(f"Generated: {success}/{total} files")
        if failed:
            print(f"Failed: {', '.join(failed[:5])}")
            if len(failed) > 5:
                print(f"  ... and {len(failed)-5} more")
    
    # Test playback if requested
    if args.test:
        print("\n" + "-" * 40)
        print("Testing playback...")
        if generator.test_playback():
            print("\n[SUCCESS] Audio files are proper WAV format!")
    
    # Instructions
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the generated WAV files from:")
    print(f"   {generator.output_dir.absolute()}")
    print("   TO:")
    print(f"   .claude-example\\audio\\")
    print("\n2. The V3.0 audio system will work correctly!")
    print("\nUsage examples:")
    print("  python generate_audio_from_json.py              # Generate all")
    print("  python generate_audio_from_json.py -f v3        # V3 sounds only")
    print("  python generate_audio_from_json.py -f agents    # Agent sounds only")
    print("  python generate_audio_from_json.py -l           # List categories")
    print("  python generate_audio_from_json.py -t           # Test playback")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())