#!/usr/bin/env python3
"""
audio_notifier.py - Audio notification system for Claude Code hooks
Plays appropriate sounds based on hook events and outcomes
"""

import json
import sys
import os
import platform
from pathlib import Path

class AudioNotifier:
    def __init__(self):
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        
        # Map events to audio files
        self.audio_map = {
            "success": "success.wav",
            "warning": "warning.wav",
            "error": "error.wav",
            "notify": "notify.wav",
            "agent": "agent.wav",
            "mcp": "mcp.wav",
            "session": "session.wav"
        }
        
    def play_sound(self, sound_type):
        """Play audio file based on event type"""
        audio_file = self.audio_dir / self.audio_map.get(sound_type, "notify.wav")
        
        if not audio_file.exists():
            return  # Silently skip if audio file doesn't exist
        
        try:
            if self.system == "Windows":
                import winsound
                winsound.PlaySound(str(audio_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif self.system == "Darwin":  # macOS
                os.system(f'afplay "{audio_file}" &')
            else:  # Linux
                os.system(f'aplay "{audio_file}" &')
        except:
            pass  # Don't let audio errors break the hook chain
    
    def determine_sound(self, input_data):
        """Determine which sound to play based on hook data"""
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        
        # Agent invocations
        if "agent" in tool_name.lower() or "@agent-" in input_data.get("prompt", ""):
            return "agent"
        
        # MCP services
        if tool_name.startswith("mcp__"):
            return "mcp"
        
        # Session events
        if hook_event in ["SessionStart", "Stop"]:
            return "session"
        
        # Check for errors in tool response
        if "tool_response" in input_data:
            response = input_data["tool_response"]
            if isinstance(response, dict):
                if response.get("success") == False or response.get("error"):
                    return "error"
                elif response.get("success") == True:
                    return "success"
        
        # Default notification
        return "notify"

def main():
    """Main hook execution with audio notification"""
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    # Initialize notifier
    notifier = AudioNotifier()
    
    # Determine and play appropriate sound
    sound_type = notifier.determine_sound(input_data)
    notifier.play_sound(sound_type)
    
    # Always exit successfully (audio is non-blocking)
    sys.exit(0)

if __name__ == "__main__":
    main()