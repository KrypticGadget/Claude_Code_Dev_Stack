#!/usr/bin/env python3
"""
Enhanced audio player hook for Claude Code Dev Stack
Plays context-aware audio notifications based on events
"""

import json
import sys
import os
import platform
import subprocess
from pathlib import Path

class AudioPlayer:
    def __init__(self):
        # Audio directory relative to hooks
        self.audio_dir = Path(__file__).parent.parent / "audio"
        self.system = platform.system()
        
        # Map events to audio files (using your actual MP3 files)
        self.audio_map = {
            "task_complete": "task_complete.mp3",
            "build_complete": "build_complete.mp3",
            "error_fixed": "error_fixed.mp3",
            "ready": "ready.mp3",
            "awaiting": "awaiting_instructions.mp3",
            # Additional mappings for hook events
            "agent_start": "ready.mp3",
            "mcp_activated": "ready.mp3",
            "success": "task_complete.mp3",
            "build_success": "build_complete.mp3",
            "error_resolved": "error_fixed.mp3",
            "session_start": "ready.mp3",
            "waiting": "awaiting_instructions.mp3"
        }
    
    def play_sound(self, audio_file):
        """Play audio file using appropriate system player"""
        audio_path = self.audio_dir / audio_file
        
        if not audio_path.exists():
            # Silently skip if file doesn't exist
            return False
        
        try:
            if self.system == "Windows":
                # Windows: Use PowerShell to play sound
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync()"],
                    capture_output=True,
                    timeout=2
                )
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)], capture_output=True, timeout=2)
            else:  # Linux
                subprocess.run(["aplay", str(audio_path)], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def determine_audio(self, input_data):
        """Determine which audio to play based on hook data"""
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        tool_response = input_data.get("tool_response", {})
        
        # SessionStart event
        if hook_event == "SessionStart":
            return self.audio_map["session_start"]
        
        # Stop event (task complete)
        if hook_event == "Stop":
            return self.audio_map["task_complete"]
        
        # Agent invocations
        if tool_name == "Task" or "@agent-" in input_data.get("prompt", ""):
            return self.audio_map["agent_start"]
        
        # MCP services
        if tool_name and tool_name.startswith("mcp__"):
            return self.audio_map["mcp_activated"]
        
        # Build/compile events
        if tool_name == "Bash":
            command = input_data.get("tool_input", {}).get("command", "")
            if any(build_cmd in command for build_cmd in ["npm run build", "make", "cargo build", "go build"]):
                if isinstance(tool_response, dict) and tool_response.get("exit_code") == 0:
                    return self.audio_map["build_complete"]
        
        # Error resolution
        if hook_event == "PostToolUse":
            if isinstance(tool_response, dict):
                # Check if an error was fixed
                if "fixed" in str(tool_response).lower() or "resolved" in str(tool_response).lower():
                    return self.audio_map["error_fixed"]
                # Check for successful completion
                elif tool_response.get("success") or tool_response.get("exit_code") == 0:
                    return self.audio_map["success"]
        
        # UserPromptSubmit - waiting for instructions
        if hook_event == "UserPromptSubmit" and not input_data.get("prompt"):
            return self.audio_map["awaiting"]
        
        return None  # No audio for this event

def main():
    """Main hook execution"""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    # Create player instance
    player = AudioPlayer()
    
    # Determine which audio to play
    audio_file = player.determine_audio(input_data)
    
    # Play the audio if determined
    if audio_file:
        player.play_sound(audio_file)
    
    # Always exit successfully (audio is non-blocking)
    sys.exit(0)

if __name__ == "__main__":
    main()