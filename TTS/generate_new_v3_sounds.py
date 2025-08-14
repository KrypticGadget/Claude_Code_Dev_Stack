#!/usr/bin/env python3
"""
Generate only the new V3+ audio files
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_audio_from_json import AudioGenerator

async def main():
    """Generate only new V3+ sounds"""
    
    # List of new sounds to generate
    new_sounds = [
        "linting_started.wav",
        "linting_complete.wav", 
        "linting_issues.wav",
        "formatting_code.wav",
        "dependency_installing.wav",
        "dependency_missing.wav",
        "performance_warning.wav",
        "resource_warning.wav",
        "notification_sent.wav",
        "tunnel_connected.wav",
        "tunnel_disconnected.wav",
        "dashboard_started.wav",
        "security_scanning.wav",
        "documentation_generating.wav",
        "quality_gate_passed.wav"
    ]
    
    print("=" * 60)
    print("Generating 15 New V3+ Audio Files")
    print("=" * 60)
    
    # Initialize generator
    generator = AudioGenerator("audio_config.json", "../.claude-example/audio")
    
    # Generate each new sound
    success_count = 0
    for i, filename in enumerate(new_sounds, 1):
        if filename in generator.audio_files:
            text = generator.audio_files[filename]
            print(f"[{i:2}/15] {filename:<35} - '{text}'")
            
            success, size = await generator.generate_wav(filename, text)
            if success:
                print(f"    [OK] Generated ({size:,} bytes)")
                success_count += 1
            else:
                print(f"    [FAIL] Failed")
        else:
            print(f"[{i:2}/15] {filename:<35} - NOT FOUND in config")
    
    print("\n" + "=" * 60)
    print(f"Generated {success_count}/15 new V3+ audio files")
    print("Files saved to: ../.claude-example/audio/")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())