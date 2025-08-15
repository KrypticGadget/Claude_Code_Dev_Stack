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
        
        # Map events to audio files (using actual generated files)
        self.audio_map = {
            "success": "pipeline_complete.wav",
            "warning": "awaiting_response.wav",
            "error": "clarification_needed.wav",
            "notify": "ready_for_input.wav",
            "agent": "agent_activated.wav",
            "mcp": "mcp_service_starting.wav",
            "session": "processing_complete.wav"
        }
        
    def play_sound(self, sound_type):
        """Play audio file based on event type"""
        audio_filename = self.audio_map.get(sound_type, "ready_for_input.wav")
        if not audio_filename:
            return
            
        audio_file = self.audio_dir / audio_filename
        
        if not audio_file.exists():
            return  # Silently skip if audio file doesn't exist
        
        try:
            if self.system == "Windows":
                # Method 1: Try pygame first (handles more formats)
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(audio_file))
                    pygame.mixer.music.play()
                    # Wait for audio to finish (up to 2 seconds)
                    import time
                    clock = pygame.time.Clock()
                    while pygame.mixer.music.get_busy() and time.time() < time.time() + 2:
                        clock.tick(10)
                    print(f"[AUDIO] Played with pygame: {audio_filename}", file=sys.stderr)
                    return
                except Exception as e:
                    print(f"[AUDIO] pygame not available: {e}", file=sys.stderr)
                
                # Method 2: Use PowerShell Media.SoundPlayer (more reliable for Edge-TTS WAVs)
                try:
                    ps_command = f'''
                    Add-Type -AssemblyName System.Media
                    $player = New-Object System.Media.SoundPlayer("{str(audio_file).replace(chr(92), chr(92)*2)}")
                    $player.PlaySync()
                    '''
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", ps_command],
                        capture_output=True,
                        timeout=3,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"[AUDIO] Played with PowerShell: {audio_filename}", file=sys.stderr)
                        return
                    else:
                        print(f"[AUDIO] PowerShell error: {result.stderr}", file=sys.stderr)
                except Exception as e:
                    print(f"[AUDIO] PowerShell failed: {e}", file=sys.stderr)
                
                # Method 3: Try winsound as last resort
                try:
                    import winsound
                    winsound.PlaySound(str(audio_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
                    print(f"[AUDIO] Played with winsound: {audio_filename}", file=sys.stderr)
                    return
                except Exception as e:
                    print(f"[AUDIO] winsound failed: {e}", file=sys.stderr)
                
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_file)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_filename}", file=sys.stderr)
            else:  # Linux
                subprocess.run(["aplay", str(audio_file)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_filename}", file=sys.stderr)
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
                elif response.get("warning"):
                    return "warning"
                elif response.get("success"):
                    return "success"
        
        # Default notification
        return "notify"

def main():
    """Main hook execution"""
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    notifier = AudioNotifier()
    sound_type = notifier.determine_sound(input_data)
    notifier.play_sound(sound_type)
    
    # Always exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()