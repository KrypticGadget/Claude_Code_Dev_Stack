#!/usr/bin/env python3
"""
Migration script to integrate V3 audio system with existing V2 audio player
Creates a bridge between the two systems for smooth transition
"""

import sys
import json
import os
from pathlib import Path

# Try to import both audio players
try:
    from audio_player import AudioPlayer as AudioPlayerV2
except ImportError:
    AudioPlayerV2 = None

try:
    from audio_player_v3 import AudioPlayerV3
except ImportError:
    AudioPlayerV3 = None

class AudioBridge:
    """Bridge between V2 and V3 audio systems"""
    
    def __init__(self):
        self.use_v3 = os.environ.get("AUDIO_V3", "false").lower() in ["true", "1", "yes"]
        self.v2_player = AudioPlayerV2() if AudioPlayerV2 else None
        self.v3_player = AudioPlayerV3() if AudioPlayerV3 else None
        
    def play(self, hook_data):
        """Route to appropriate audio player"""
        if self.use_v3 and self.v3_player:
            # Use V3 player
            event_type = hook_data.get("tool_name") or hook_data.get("hook_event_name", "")
            self.v3_player.handle_event(event_type)
        elif self.v2_player:
            # Use V2 player
            sound_key = self.v2_player.determine_audio(hook_data)
            if sound_key:
                self.v2_player.play_sound(sound_key)

def main():
    """Main entry point"""
    try:
        # Read hook data
        input_data = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except:
        input_data = {}
    
    # Use bridge to play audio
    bridge = AudioBridge()
    bridge.play(input_data)
    
    sys.exit(0)

if __name__ == "__main__":
    main()