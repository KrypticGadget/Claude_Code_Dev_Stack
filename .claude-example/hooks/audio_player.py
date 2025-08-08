#!/usr/bin/env python3
"""
Audio player hook for Claude Code - plays audio notifications for various events.
Minimal debug output for troubleshooting.
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
        
        try:
            if self.system == "Windows":
                # Use winsound for Windows - synchronous playback
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)
                print(f"[AUDIO] Played: {audio_file}", file=sys.stderr)
                return True
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_file}", file=sys.stderr)
                return True
            else:  # Linux
                subprocess.run(["aplay", str(audio_path)], capture_output=True, timeout=2)
                print(f"[AUDIO] Played: {audio_file}", file=sys.stderr)
                return True
        except Exception as e:
            print(f"[AUDIO] Error playing {audio_file}: {e}", file=sys.stderr)
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