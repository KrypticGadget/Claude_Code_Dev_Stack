#!/usr/bin/env python3
"""
Optimized audio player hook for Claude Code - fast & reliable audio notifications.
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
        
        # Minimal event-to-audio mapping (only essential sounds)
        self.audio_map = {
            "session_start": "project_created.wav",
            "task_complete": "pipeline_complete.wav",
            "agent_start": "agent_activated.wav",
            "build_complete": "build_successful.wav",
            "error_fixed": "rollback_complete.wav",
            "success": "milestone_complete.wav"
        }
    
    def play_sound(self, audio_file):
        """Fast, non-blocking audio playback"""
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        if not audio_path.exists():
            return False
        
        try:
            if self.system == "Windows":
                # Use winsound for fastest Windows playback
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True
            elif self.system == "Darwin":
                subprocess.Popen(["afplay", str(audio_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            else:  # Linux
                subprocess.Popen(["aplay", str(audio_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
        except:
            return False
    
    def determine_audio(self, input_data):
        """Quick event-to-audio mapping"""
        event = input_data.get("hook_event_name", "")
        tool = input_data.get("tool_name", "")
        
        # Direct event mapping
        if event == "SessionStart":
            return self.audio_map.get("session_start")
        elif event == "Stop":
            return self.audio_map.get("task_complete")
        elif tool == "Task":
            return self.audio_map.get("agent_start")
        elif tool == "Bash":
            cmd = input_data.get("tool_input", {}).get("command", "")
            if any(x in cmd for x in ["build", "make", "compile"]):
                return self.audio_map.get("build_complete")
        elif tool in ["Write", "Edit", "MultiEdit"]:
            return self.audio_map.get("success")
        
        return None

def main():
    """Main hook execution - optimized for speed"""
    try:
        input_data = json.load(sys.stdin)
    except:
        sys.exit(0)
    
    player = AudioPlayer()
    audio_file = player.determine_audio(input_data)
    
    if audio_file:
        player.play_sound(audio_file)
    
    sys.exit(0)

if __name__ == "__main__":
    main()