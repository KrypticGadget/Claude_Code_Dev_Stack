#!/usr/bin/env python3
"""
Convert Edge-TTS WAV files to standard PCM format compatible with Windows audio APIs
"""

import os
import sys
from pathlib import Path
from pydub import AudioSegment
import wave

def convert_wav_to_pcm(input_file, output_file):
    """
    Convert WAV file to standard PCM format
    16-bit, 44100 Hz, stereo/mono
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_wav(input_file)
        
        # Convert to standard PCM format
        # 16-bit depth, 44100 Hz sample rate
        audio = audio.set_frame_rate(44100)
        audio = audio.set_sample_width(2)  # 2 bytes = 16 bits
        
        # Export as WAV with PCM codec
        audio.export(
            output_file,
            format="wav",
            parameters=["-acodec", "pcm_s16le"]  # PCM 16-bit little-endian
        )
        
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {e}")
        return False

def test_wav_file(file_path):
    """
    Test if WAV file is in proper format for winsound
    """
    try:
        with wave.open(str(file_path), 'rb') as wav_file:
            params = wav_file.getparams()
            print(f"  Channels: {params.nchannels}")
            print(f"  Sample width: {params.sampwidth} bytes")
            print(f"  Frame rate: {params.framerate} Hz")
            print(f"  Frames: {params.nframes}")
            print(f"  Compression: {params.comptype} ({params.compname})")
            
            # Check if it's PCM (uncompressed)
            if params.comptype == 'NONE':
                print("  ✓ File is in PCM format (compatible)")
                return True
            else:
                print("  ✗ File is compressed (may not be compatible)")
                return False
    except Exception as e:
        print(f"  Error reading file: {e}")
        return False

def main():
    # Setup paths
    base_dir = Path(__file__).parent
    sounds_dir = base_dir / "sounds"
    clean_dir = base_dir / "sounds_clean"
    
    # Create output directory
    clean_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("WAV File Conversion Tool")
    print("Converting Edge-TTS files to PCM format")
    print("=" * 60)
    
    # Get all WAV files
    wav_files = list(sounds_dir.glob("*.wav"))
    print(f"\nFound {len(wav_files)} WAV files to convert")
    
    # Test original format of first file
    if wav_files:
        print(f"\nTesting original format of {wav_files[0].name}:")
        test_wav_file(wav_files[0])
    
    # Convert each file
    print("\nConverting files...")
    print("-" * 40)
    
    success_count = 0
    for wav_file in wav_files:
        output_file = clean_dir / wav_file.name
        print(f"Converting: {wav_file.name}... ", end="")
        
        if convert_wav_to_pcm(wav_file, output_file):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print("-" * 40)
    print(f"Conversion complete: {success_count}/{len(wav_files)} successful")
    
    # Test converted format
    if success_count > 0:
        converted_files = list(clean_dir.glob("*.wav"))
        if converted_files:
            print(f"\nTesting converted format of {converted_files[0].name}:")
            test_wav_file(converted_files[0])
    
    # Test with winsound
    print("\nTesting playback with winsound...")
    try:
        import winsound
        test_file = clean_dir / "project_created.wav"
        if test_file.exists():
            print(f"Playing: {test_file.name}")
            winsound.PlaySound(str(test_file), winsound.SND_FILENAME)
            print("✓ Playback successful!")
        else:
            print("✗ Test file not found")
    except Exception as e:
        print(f"✗ Playback failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Clean files saved to: {clean_dir}")
    print("You can now copy these files to C:\\Users\\Zach\\.claude\\audio\\")
    print("=" * 60)

if __name__ == "__main__":
    main()