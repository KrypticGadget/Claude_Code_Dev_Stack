#!/usr/bin/env python3
"""
Audio player hook for Claude Code - plays audio notifications for various events.
Supports Windows, macOS, and Linux with WAV files for silent playback.
"""

import json
import sys
import subprocess
import platform
from pathlib import Path

class AudioPlayer:
    def __init__(self):
        # Audio directory under .claude
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        
        # Map events to audio files (using WAV for silent Windows playback)
        self.audio_map = {
            "task_complete": "task_complete.wav",
            "build_complete": "build_complete.wav",
            "error_fixed": "error_fixed.wav",
            "ready": "ready.wav",
            "awaiting": "awaiting_instructions.wav",
            # Aliases for events
            "agent_start": "ready.wav",
            "mcp_activated": "ready.wav",
            "success": "task_complete.wav",
            "build_success": "build_complete.wav",
            "error_resolved": "error_fixed.wav",
            "session_start": "ready.wav",
            "waiting": "awaiting_instructions.wav"
        }
    
    def play_sound(self, audio_file):
        """Play audio file using appropriate system player"""
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        
        # Check if file exists
        if not audio_path.exists():
            print(f"[AUDIO DEBUG] File not found: {audio_path}", file=sys.stderr)
            return False
        
        try:
            if self.system == "Windows":
                # Method 1: Try pygame first (if installed) - most reliable, no windows
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(audio_path))
                    pygame.mixer.music.play()
                    print(f"[AUDIO DEBUG] Playing with pygame: {audio_file}", file=sys.stderr)
                    return True
                except ImportError:
                    pass
                
                # Method 2: Use winsound for WAV files - built-in, no windows, no console issues
                try:
                    import winsound
                    # Verify file exists and is readable
                    if not audio_path.exists():
                        print(f"[AUDIO ERROR] File does not exist: {audio_path}", file=sys.stderr)
                        return False
                    
                    # Try synchronous first to ensure it works
                    print(f"[AUDIO DEBUG] Attempting winsound.PlaySound with: {str(audio_path)}", file=sys.stderr)
                    winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)
                    print(f"[AUDIO SUCCESS] Sound played successfully: {audio_file}", file=sys.stderr)
                    return True
                except ImportError as e:
                    print(f"[AUDIO ERROR] winsound module not available: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"[AUDIO ERROR] winsound playback failed: {e}", file=sys.stderr)
                    print(f"[AUDIO ERROR] File path was: {audio_path}", file=sys.stderr)
                    pass
                
                # Method 3: Fallback to simple Windows command
                try:
                    # Use Windows media player in background
                    cmd = f'powershell -WindowStyle Hidden -Command "(New-Object Media.SoundPlayer \'{str(audio_path)}\').PlaySync()"'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"[AUDIO DEBUG] Playing with PowerShell: {audio_file}", file=sys.stderr)
                    return True
                except:
                    pass
                    
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)], capture_output=True, timeout=2)
            else:  # Linux
                subprocess.run(["aplay", str(audio_path)], capture_output=True, timeout=2)
            return True
        except Exception as e:
            print(f"[AUDIO DEBUG] General error: {e}", file=sys.stderr)
            return False
    
    def determine_audio(self, input_data):
        """Determine which audio to play based on hook data"""
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        tool_response = input_data.get("tool_response", {})
        
        # Debug logging
        print(f"[AUDIO DEBUG] Hook event: {hook_event}, Tool: {tool_name}", file=sys.stderr)
        
        # SessionStart event
        if hook_event == "SessionStart":
            return self.audio_map.get("session_start")
        
        # Stop event (task complete)
        if hook_event == "Stop":
            return self.audio_map.get("task_complete")
        
        # Agent invocations - check multiple places for agent mentions
        if tool_name == "Task":
            return self.audio_map.get("agent_start")
        
        # Check for @agent- mentions in various fields
        prompt_str = str(input_data.get("prompt", ""))
        tool_input_str = str(input_data.get("tool_input", {}))
        
        if "@agent-" in prompt_str or "@agent-" in tool_input_str:
            return self.audio_map.get("agent_start")
        
        # Also check if Task tool has agent in description
        if tool_name == "Task" and "agent" in str(input_data).lower():
            return self.audio_map.get("agent_start")
        
        # MCP services
        if tool_name and tool_name.startswith("mcp__"):
            return self.audio_map.get("mcp_activated")
        
        # Build/compile events - play on any build completion (success or failure)
        if tool_name == "Bash":
            command = input_data.get("tool_input", {}).get("command", "")
            if any(build_cmd in command for build_cmd in ["npm run build", "make", "cargo build", "go build", "npm build", "yarn build"]):
                # Play build complete sound regardless of exit code to notify completion
                return self.audio_map.get("build_complete")
        
        # Error resolution
        if hook_event == "PostToolUse":
            if isinstance(tool_response, dict):
                # Check if an error was fixed
                if "error" in str(tool_response).lower() and tool_response.get("success"):
                    return self.audio_map.get("error_fixed")
                # Check for successful completion
                elif tool_response.get("success") or tool_response.get("exit_code") == 0:
                    return self.audio_map.get("success")
        
        # File operations - check if we're fixing errors
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            # Check if we're fixing code errors based on context
            prompt_lower = str(input_data.get("prompt", "")).lower()
            tool_input_str = str(input_data.get("tool_input", {})).lower()
            
            if any(word in prompt_lower or word in tool_input_str for word in ["fix", "error", "syntax", "bug", "issue", "problem", "correct"]):
                return self.audio_map.get("error_fixed")
            else:
                return self.audio_map.get("success")
        
        # Awaiting input - check for help commands and waiting states
        prompt_str = str(input_data.get("prompt", ""))
        if hook_event == "UserInput" or "awaiting" in input_data.get("state", ""):
            return self.audio_map.get("awaiting")
        
        # Check if user is asking for help
        if any(help_cmd in prompt_str.lower() for help_cmd in ["/help", "help me", "need help", "??"]):
            return self.audio_map.get("awaiting")
        
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
    
    # Debug output
    print(f"[AUDIO DEBUG] Event triggered, file to play: {audio_file}", file=sys.stderr)
    
    # Play the audio if determined
    if audio_file:
        player.play_sound(audio_file)
    
    # Always exit successfully (audio is non-blocking)
    sys.exit(0)

if __name__ == "__main__":
    main()