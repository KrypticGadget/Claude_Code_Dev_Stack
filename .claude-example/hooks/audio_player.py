#!/usr/bin/env python3
"""
Audio player hook for Claude Code - plays audio notifications for various events.
Supports Windows, macOS, and Linux with MP3 files.
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
        
        # Map events to audio files
        self.audio_map = {
            "task_complete": "task_complete.mp3",
            "build_complete": "build_complete.mp3",
            "error_fixed": "error_fixed.mp3",
            "ready": "ready.mp3",
            "awaiting": "awaiting_instructions.mp3",
            # Aliases for events
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
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        
        # Check if file exists
        if not audio_path.exists():
            return False
        
        try:
            if self.system == "Windows":
                # Method 1: Try pygame first (if installed)
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(audio_path))
                    pygame.mixer.music.play()
                    return True
                except ImportError:
                    pass
                
                # Method 2: Use PowerShell with hidden window
                import subprocess
                ps_cmd = f'''
                $player = New-Object System.Media.SoundPlayer
                $player.SoundLocation = "{str(audio_path)}"
                $player.Play()
                '''
                
                # For MP3 files, use Windows Media Foundation
                if str(audio_path).lower().endswith('.mp3'):
                    ps_cmd = f'''
                    Add-Type -AssemblyName presentationCore
                    $player = New-Object System.Windows.Media.MediaPlayer
                    $player.Open([System.Uri]::new("{str(audio_path).replace(chr(92), '/')}", [System.UriKind]::Absolute))
                    $player.Play()
                    Start-Sleep -Seconds 3
                    '''
                
                # Run PowerShell completely detached without affecting parent window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                subprocess.Popen(
                    ['powershell', '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-Command', ps_cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    startupinfo=startupinfo,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )
                
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_path)], capture_output=True, timeout=2)
            else:  # Linux
                subprocess.run(["aplay", str(audio_path)], capture_output=True, timeout=2)
            return True
        except Exception:
            # Silently fail - don't break hook chain
            return False
    
    def determine_audio(self, input_data):
        """Determine which audio to play based on hook data"""
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        tool_response = input_data.get("tool_response", {})
        
        # SessionStart event
        if hook_event == "SessionStart":
            return self.audio_map.get("session_start")
        
        # Stop event (task complete)
        if hook_event == "Stop":
            return self.audio_map.get("task_complete")
        
        # Agent invocations
        if tool_name == "Task" or "@agent-" in input_data.get("prompt", ""):
            return self.audio_map.get("agent_start")
        
        # MCP services
        if tool_name and tool_name.startswith("mcp__"):
            return self.audio_map.get("mcp_activated")
        
        # Build/compile events
        if tool_name == "Bash":
            command = input_data.get("tool_input", {}).get("command", "")
            if any(build_cmd in command for build_cmd in ["npm run build", "make", "cargo build", "go build"]):
                if isinstance(tool_response, dict) and tool_response.get("exit_code") == 0:
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
        
        # File operations
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            return self.audio_map.get("success")
        
        # Awaiting input
        if hook_event == "UserInput" or "awaiting" in input_data.get("state", ""):
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
    
    # Play the audio if determined
    if audio_file:
        player.play_sound(audio_file)
    
    # Always exit successfully (audio is non-blocking)
    sys.exit(0)

if __name__ == "__main__":
    main()