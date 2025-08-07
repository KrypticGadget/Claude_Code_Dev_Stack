#!/usr/bin/env python3
"""
audio_notifier.py - Audio notification system for Claude Code hooks
Plays appropriate sounds based on hook events and outcomes
"""

import json
import sys
import os
import platform
import subprocess
from pathlib import Path

class AudioNotifier:
    def __init__(self):
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        
        # Map events to audio files (supporting both wav and mp3)
        self.audio_map = {
            "success": "task_complete.mp3",
            "warning": "awaiting_instructions.mp3",
            "error": "error_fixed.mp3",
            "notify": "ready.mp3",
            "agent": "ready.mp3",
            "mcp": "ready.mp3",
            "session": "ready.mp3"
        }
        
    def play_sound(self, sound_type):
        """Play audio file based on event type"""
        audio_filename = self.audio_map.get(sound_type, "ready.mp3")
        if not audio_filename:
            return
            
        audio_file = self.audio_dir / audio_filename
        
        if not audio_file.exists():
            return  # Silently skip if audio file doesn't exist
        
        try:
            if self.system == "Windows":
                # Method 1: Try pygame first (silent playback)
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(audio_file))
                    pygame.mixer.music.play()
                    return
                except ImportError:
                    pass
                
                # Method 2: Try playsound module
                try:
                    from playsound import playsound
                    playsound(str(audio_file), False)  # False = don't block
                    return
                except ImportError:
                    pass
                
                # Method 3: Use mshta.exe with HTML5 audio (invisible, won't affect PowerShell)
                audio_url = audio_file.as_uri()
                mshta_script = f'''mshta "javascript:var a=new Audio('{audio_url}');a.play();setTimeout(function(){{close();}},5000);"'''
                
                subprocess.Popen(
                    mshta_script,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
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