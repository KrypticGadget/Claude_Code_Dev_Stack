#!/usr/bin/env python3
"""
Fixed Audio Player Hook for Claude Code v5.0
Prioritizes winsound for Windows + proper error handling
"""

import json
import sys
import subprocess
import platform
from pathlib import Path
import os
import time

class AudioPlayer:
    def __init__(self):
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        # Check for auto-accept mode
        self.auto_accept = os.environ.get('CLAUDE_AUTO_ACCEPT', '').lower() in ['1', 'true', 'yes']
        # Debug mode
        self.debug = os.environ.get('CLAUDE_DEBUG', '').lower() in ['1', 'true', 'yes']
        
        # Comprehensive event-to-audio mapping with SPECIFIC descriptive audio
        self.audio_map = {
            # File Operations - SPECIFIC
            "file_mkdir": "mkdir_operation.wav",
            "file_touch": "touch_operation.wav",
            "file_copy": "copy_operation.wav",
            "file_move": "move_operation.wav",
            "file_delete": "delete_operation.wav",
            
            # Git Operations - SPECIFIC
            "git_status": "git_status.wav",
            "git_commit": "git_commit.wav",
            "git_push": "git_push.wav",
            "git_pull": "git_pull.wav",
            
            # Build Operations - SPECIFIC
            "build_npm": "npm_build.wav",
            "build_make": "make_build.wav",
            "build_cargo": "cargo_build.wav",
            
            # Package Management - SPECIFIC
            "install_pip": "pip_install.wav",
            "install_npm": "npm_install.wav",
            "install_packages": "installing_packages.wav",
            
            # Testing - SPECIFIC
            "test_running": "running_tests.wav",
            "test_passed": "tests_passed.wav",
            "test_failed": "tests_failed.wav",
            
            # Docker - SPECIFIC
            "docker_build": "docker_building.wav",
            "docker_run": "docker_running.wav",
            
            # Navigation/Search - SPECIFIC
            "nav_cd": "changing_directory.wav",
            "nav_ls": "checking_files.wav",
            "search_files": "searching_files.wav",
            
            # Network - SPECIFIC
            "net_http": "http_request.wav",
            "net_download": "downloading_file.wav",
            "net_ssh": "ssh_connection.wav",
            
            # Virtual Environment - SPECIFIC
            "venv_required": "venv_required.wav",
            "venv_activated": "venv_activated.wav",
            "venv_warning": "no_venv_warning.wav",
            
            # Agent Operations - SPECIFIC
            "agent_frontend": "frontend_agent.wav",
            "agent_backend": "backend_agent.wav",
            "agent_database": "database_agent.wav",
            "agent_orchestrator": "master_orchestrator.wav",
            
            # Status Updates - SPECIFIC
            "analyzing_code": "analyzing_code.wav",
            "generating_code": "generating_code.wav",
            "reviewing_changes": "reviewing_changes.wav",
            "optimizing": "optimizing_performance.wav",
            
            # Warnings - SPECIFIC
            "risky_command": "risky_command.wav",
            "permission_denied": "permission_denied.wav",
            "file_exists": "file_exists.wav",
            
            # Errors - SPECIFIC
            "command_failed": "command_failed.wav",
            "file_not_found": "file_not_found.wav",
            "connection_error": "connection_error.wav",
            
            # MCP Services - SPECIFIC
            "mcp_playwright": "playwright_automation.wav",
            "mcp_obsidian": "obsidian_notes.wav",
            "mcp_websearch": "web_search.wav",
            
            # Auto-accept Mode - SPECIFIC
            "auto_accepting": "auto_accepting.wav",
            "auto_mode": "auto_mode_active.wav",
            
            # Legacy mappings (fallback compatibility)
            "session_start": "project_created.wav",
            "session_stop": "ready_for_input.wav",
            "agent_start": "agent_activated.wav",
            "task_complete": "pipeline_complete.wav",
            "file_confirm": "confirm_required.wav",
            "file_pending": "file_operation_pending.wav",
            "file_complete": "file_operation_complete.wav",
            "command_success": "command_successful.wav",
            "planning_exit": "planning_complete.wav",
            "planning_active": "analyzing.wav",
            "success": "milestone_complete.wav",
            "operation_done": "operation_complete.wav",
            "phase_done": "phase_complete.wav",
            "ready": "ready_for_input.wav",
            "awaiting": "awaiting_input.wav",
            "decision": "decision_required.wav",
            "working": "working.wav",
            "processing": "processing.wav",
            "analyzing": "analyzing.wav",
            "pipeline_start": "pipeline_initiated.wav",
            "pipeline_end": "pipeline_complete.wav"
        }
    
    def play_sound(self, sound_key):
        """Play audio file based on sound key - FIXED VERSION"""
        audio_file = self.audio_map.get(sound_key)
        if not audio_file:
            if self.debug:
                print(f"[AUDIO] No mapping for key: {sound_key}", file=sys.stderr)
            return False
            
        audio_path = self.audio_dir / audio_file
        
        if not audio_path.exists():
            if self.debug:
                print(f"[AUDIO] File not found: {audio_path}", file=sys.stderr)
            return False
        
        if self.debug:
            print(f"[AUDIO] Playing: {audio_file} for event: {sound_key}", file=sys.stderr)
        
        if self.system == "Windows":
            # Method 1: winsound (MOST RELIABLE for Windows WAV files)
            try:
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True
            except Exception as e:
                if self.debug:
                    print(f"[AUDIO] winsound failed: {e}", file=sys.stderr)
            
            # Method 2: pygame (backup)
            try:
                import pygame
                # Initialize if not already
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                
                # Use Sound object for async playback
                sound = pygame.mixer.Sound(str(audio_path))
                sound.play()
                return True
            except Exception as e:
                if self.debug:
                    print(f"[AUDIO] pygame failed: {e}", file=sys.stderr)
            
            # Method 3: PowerShell (last resort)
            try:
                # Use Start-Process for async playback
                subprocess.Popen([
                    "powershell", "-WindowStyle", "Hidden", "-c",
                    f"(New-Object Media.SoundPlayer '{audio_path}').Play()"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception as e:
                if self.debug:
                    print(f"[AUDIO] PowerShell failed: {e}", file=sys.stderr)
        
        elif self.system == "Darwin":  # macOS
            try:
                subprocess.Popen(["afplay", str(audio_path)], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                return True
            except:
                pass
        
        elif self.system == "Linux":
            # Try various Linux audio players
            for player in ["aplay", "paplay", "ffplay", "mpg123"]:
                try:
                    subprocess.Popen([player, str(audio_path)],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return True
                except:
                    continue
        
        return False
    
    def determine_audio(self, hook_data):
        """Determine which audio to play based on hook event data"""
        event = hook_data.get("hook_event_name", "")
        tool = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})
        tool_response = hook_data.get("tool_response", {})
        
        # SessionStart event - ALWAYS PLAY
        if event == "SessionStart":
            if self.auto_accept:
                return "auto_mode"
            return "session_start"  # This should play project_created.wav
        
        # Stop event - Claude finished
        if event == "Stop":
            return "ready"
        
        # PreToolUse events - BEFORE operations
        if event == "PreToolUse":
            if tool in ["Write", "Edit", "MultiEdit"]:
                if self.auto_accept:
                    return "auto_accepting"
                return "file_confirm"
            
            elif tool == "Bash":
                # Categorize Bash commands for SPECIFIC audio
                command = tool_input.get("command", "").lower()
                
                # Check for auto-accept mode first
                if self.auto_accept:
                    return "auto_accepting"
                
                # File Operations - SPECIFIC
                if "mkdir" in command:
                    return "file_mkdir"
                elif "touch" in command:
                    return "file_touch"
                elif any(x in command for x in ["cp ", "copy"]):
                    return "file_copy"
                elif any(x in command for x in ["mv ", "move"]):
                    return "file_move"
                elif any(x in command for x in ["rm ", "del ", "rmdir"]):
                    return "file_delete"
                
                # Navigation - SPECIFIC
                elif "cd " in command:
                    return "nav_cd"
                elif any(x in command for x in ["ls", "dir"]):
                    return "nav_ls"
                
                # Git Operations - SPECIFIC
                elif "git status" in command:
                    return "git_status"
                elif "git commit" in command:
                    return "git_commit"
                elif "git push" in command:
                    return "git_push"
                elif "git pull" in command:
                    return "git_pull"
                
                # Build Operations - SPECIFIC
                elif any(x in command for x in ["npm run", "npm build"]):
                    return "build_npm"
                elif "make" in command:
                    return "build_make"
                elif "cargo build" in command:
                    return "build_cargo"
                
                # Package Installation - SPECIFIC
                elif any(x in command for x in ["pip install", "pip3 install"]):
                    return "install_pip"
                elif any(x in command for x in ["npm install", "npm i"]):
                    return "install_npm"
                
                # Testing - SPECIFIC
                elif any(x in command for x in ["pytest", "jest", "cargo test", "npm test"]):
                    return "test_running"
                
                # Docker - SPECIFIC
                elif "docker build" in command:
                    return "docker_build"
                elif any(x in command for x in ["docker run", "docker-compose up"]):
                    return "docker_run"
                
                # Default
                return "processing"
            
            elif tool == "Task":
                # Agent being invoked
                agent_type = tool_input.get("subagent_type", "").lower()
                if "frontend" in agent_type:
                    return "agent_frontend"
                elif "backend" in agent_type:
                    return "agent_backend"
                elif "database" in agent_type:
                    return "agent_database"
                elif "orchestrator" in agent_type:
                    return "agent_orchestrator"
                return "agent_start"
        
        # PostToolUse events - AFTER operations complete
        if event == "PostToolUse":
            if tool == "Task":
                return "pipeline_complete"
            
            elif tool in ["Write", "Edit", "MultiEdit"]:
                if tool_response and tool_response.get("success"):
                    return "file_complete"
            
            elif tool == "Bash":
                exit_code = tool_response.get("exit_code", -1)
                if exit_code == 0:
                    command = tool_input.get("command", "").lower()
                    if any(x in command for x in ["pytest", "jest", "npm test"]):
                        return "test_passed"
                    return "command_success"
                elif exit_code > 0:
                    return "command_failed"
        
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
        success = player.play_sound(sound_key)
        if player.debug and success:
            print(f"[AUDIO] Successfully played audio for: {sound_key}", file=sys.stderr)
    elif player.debug:
        event = input_data.get('hook_event_name', 'unknown')
        print(f"[AUDIO] No audio for event: {event}", file=sys.stderr)
    
    # Always exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()