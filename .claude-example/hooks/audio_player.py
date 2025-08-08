#!/usr/bin/env python3
"""
Audio player hook for Claude Code - plays audio notifications for various events.
Supports multiple playback methods for Windows compatibility.
"""

import json
import sys
import subprocess
import platform
from pathlib import Path

class AudioPlayer:
    def __init__(self):
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        
        # Essential event-to-audio mapping
        self.audio_map = {
            "session_start": "project_created.wav",
            "task_complete": "pipeline_complete.wav",
            "agent_start": "agent_activated.wav",
            "build_complete": "build_successful.wav",
            "error_fixed": "rollback_complete.wav",
            "success": "milestone_complete.wav",
            "ready": "ready_for_input.wav",
            "awaiting": "awaiting_response.wav"
        }
    
    def play_sound(self, audio_file):
        """Play audio file using appropriate system player"""
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        
        if not audio_path.exists():
            print(f"[AUDIO] File not found: {audio_path}", file=sys.stderr)
            return False
        
        if self.system == "Windows":
            # Try multiple methods for Windows
            
            # Method 1: Try pygame first (handles more formats)
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.play()
                # Wait for audio to finish (up to 2 seconds)
                import time
                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy() and time.time() < time.time() + 2:
                    clock.tick(10)
                print(f"[AUDIO] Played with pygame: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] pygame not available or failed: {e}", file=sys.stderr)
            
            # Method 2: Use PowerShell Media.SoundPlayer (more reliable for Edge-TTS WAVs)
            try:
                ps_command = f'''
                Add-Type -AssemblyName System.Media
                $player = New-Object System.Media.SoundPlayer("{str(audio_path).replace(chr(92), chr(92)*2)}")
                $player.PlaySync()
                '''
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_command],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                if result.returncode == 0:
                    print(f"[AUDIO] Played with PowerShell: {audio_file}", file=sys.stderr)
                    return True
                else:
                    print(f"[AUDIO] PowerShell error: {result.stderr}", file=sys.stderr)
            except Exception as e:
                print(f"[AUDIO] PowerShell failed: {e}", file=sys.stderr)
            
            # Method 3: Try winsound as last resort
            try:
                import winsound
                # Try async first to avoid blocking
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                print(f"[AUDIO] Played with winsound: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] winsound failed: {e}", file=sys.stderr)
                
        elif self.system == "Darwin":  # macOS
            try:
                subprocess.run(["afplay", str(audio_path)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] Error: {e}", file=sys.stderr)
                
        else:  # Linux
            try:
                subprocess.run(["aplay", str(audio_path)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] Error: {e}", file=sys.stderr)
        
        return False
    
    def determine_audio(self, input_data):
        """Determine which audio to play based on hook data"""
        event = input_data.get("hook_event_name", "")
        tool = input_data.get("tool_name", "")
        
        # Debug output
        print(f"[AUDIO] Event: {event}, Tool: {tool}", file=sys.stderr)
        
        # SessionStart event
        if event == "SessionStart":
            return self.audio_map.get("session_start")
        
        # Stop event (task complete)
        if event == "Stop":
            return self.audio_map.get("task_complete")
        
        # Agent invocations
        if tool == "Task":
            return self.audio_map.get("agent_start")
        
        # Build/compile events
        if tool == "Bash":
            command = input_data.get("tool_input", {}).get("command", "")
            if any(cmd in command for cmd in ["npm run build", "make", "cargo build", "go build"]):
                return self.audio_map.get("build_complete")
        
        # File operations
        if tool in ["Write", "Edit", "MultiEdit"]:
            return self.audio_map.get("success")
        
        return None

def main():
    """Main hook execution"""
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    player = AudioPlayer()
    audio_file = player.determine_audio(input_data)
    
    if audio_file:
        player.play_sound(audio_file)
    else:
        print(f"[AUDIO] No audio for this event", file=sys.stderr)
    
    # Always exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()