#!/usr/bin/env python3
"""
Enhanced Audio Player Hook for Claude Code
Provides intelligent audio notifications for various events and states
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
        
        # Comprehensive event-to-audio mapping
        self.audio_map = {
            # Session events
            "session_start": "project_created.wav",
            "session_stop": "ready_for_input.wav",
            
            # Agent/Task events
            "agent_start": "agent_activated.wav",
            "task_complete": "pipeline_complete.wav",
            
            # File operation events (Pre and Post)
            "file_confirm": "confirm_required.wav",
            "file_pending": "file_operation_pending.wav",
            "file_complete": "file_operation_complete.wav",
            
            # Command execution events
            "command_risky": "command_execution_pending.wav", 
            "command_normal": "processing.wav",
            "command_success": "command_successful.wav",
            
            # Planning events
            "planning_exit": "planning_complete.wav",
            "planning_active": "analyzing.wav",
            
            # Completion states
            "success": "milestone_complete.wav",
            "operation_done": "operation_complete.wav",
            "phase_done": "phase_complete.wav",
            
            # Waiting states
            "ready": "ready_for_input.wav",
            "awaiting": "awaiting_input.wav",
            "decision": "decision_required.wav",
            
            # Status updates
            "working": "working.wav",
            "processing": "processing.wav",
            "analyzing": "analyzing.wav",
            
            # Pipeline states
            "pipeline_start": "pipeline_initiated.wav",
            "pipeline_end": "pipeline_complete.wav"
        }
    
    def play_sound(self, sound_key):
        """Play audio file based on sound key"""
        audio_file = self.audio_map.get(sound_key)
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        
        if not audio_path.exists():
            print(f"[AUDIO] File not found: {audio_path}", file=sys.stderr)
            # Try fallback sounds for missing new files
            if sound_key in ["file_pending", "file_complete", "command_risky", "command_success", "planning_exit"]:
                # Use existing similar sounds as fallback
                fallback_map = {
                    "file_pending": "awaiting_confirmation.wav",
                    "file_complete": "milestone_complete.wav", 
                    "command_risky": "permission_required.wav",
                    "command_success": "build_successful.wav",
                    "planning_exit": "pipeline_complete.wav"
                }
                fallback_file = fallback_map.get(sound_key)
                if fallback_file:
                    audio_path = self.audio_dir / fallback_file
                    if audio_path.exists():
                        print(f"[AUDIO] Using fallback: {fallback_file}", file=sys.stderr)
            
            if not audio_path.exists():
                return False
        
        if self.system == "Windows":
            # Try multiple methods for Windows
            
            # Method 1: Try pygame first (handles more formats)
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.play()
                # Wait for audio to finish (up to 2 seconds for shorter sounds)
                import time
                clock = pygame.time.Clock()
                start_time = time.time()
                while pygame.mixer.music.get_busy() and time.time() - start_time < 2:
                    clock.tick(10)
                print(f"[AUDIO] Played with pygame: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] pygame failed: {e}", file=sys.stderr)
            
            # Method 2: Use PowerShell Media.SoundPlayer
            try:
                ps_command = f'''
                Add-Type -AssemblyName PresentationCore
                $player = New-Object System.Windows.Media.MediaPlayer
                $player.Open([Uri]"file:///{str(audio_path).replace(chr(92), '/')}")
                $player.Play()
                Start-Sleep -Seconds 2
                $player.Close()
                '''
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_command],
                    capture_output=True,
                    timeout=3
                )
                print(f"[AUDIO] Played with PowerShell: {audio_file}", file=sys.stderr)
                return True
            except Exception as e:
                print(f"[AUDIO] PowerShell failed: {e}", file=sys.stderr)
            
            # Method 3: Try winsound as last resort
            try:
                import winsound
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
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        
        # Debug output
        print(f"[AUDIO] Event: {event}, Tool: {tool}", file=sys.stderr)
        
        # SessionStart event
        if event == "SessionStart":
            return "session_start"
        
        # Stop event - Claude finished, user's turn
        if event == "Stop":
            return "ready"
        
        # PreToolUse events - BEFORE confirmation prompts
        if event == "PreToolUse":
            if tool in ["Write", "Edit", "MultiEdit"]:
                # File operations will need confirmation
                return "file_confirm"
            
            elif tool == "Bash":
                # Check if command is risky
                command = tool_input.get("command", "")
                risky_commands = ["rm ", "del ", "delete", "git push", "git reset", 
                                  "DROP", "DELETE FROM", "format", "kill", "shutdown"]
                if any(risky in command for risky in risky_commands):
                    return "command_risky"
                else:
                    return "confirm_required"
            
            elif tool == "ExitPlanMode":
                # Planning phase complete
                return "planning_exit"
            
            elif tool == "Task":
                # Agent being invoked
                return "agent_start"
        
        # PostToolUse events - AFTER operations complete
        if event == "PostToolUse":
            if tool == "Task":
                # Agent completed
                return "pipeline_complete"
            
            elif tool in ["Write", "Edit", "MultiEdit"]:
                # File operation completed
                if tool_response.get("success") or "written" in str(tool_response):
                    return "file_complete"
                return None
            
            elif tool == "Bash":
                # Command completed
                exit_code = tool_response.get("exit_code", -1)
                if exit_code == 0:
                    return "command_success"
                elif exit_code > 0:
                    return None  # Don't play sound for errors
                else:
                    return "operation_done"
            
            elif tool in ["Read", "Glob", "Grep", "LS"]:
                # Don't play sounds for read operations
                return None
            
            else:
                # Generic completion
                if tool_response.get("success"):
                    return "success"
        
        # SubagentStop - agent finished
        if event == "SubagentStop":
            return None  # Avoid double sounds with PostToolUse:Task
        
        return None

def main():
    """Main hook execution"""
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    player = AudioPlayer()
    sound_key = player.determine_audio(input_data)
    
    if sound_key:
        player.play_sound(sound_key)
    else:
        print(f"[AUDIO] No audio for this event", file=sys.stderr)
    
    # Always exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()