#!/usr/bin/env python3
"""
Enhanced Audio Player Hook for Claude Code v5.0
Provides SPECIFIC descriptive audio notifications for all operations
"""

import json
import sys
import subprocess
import platform
from pathlib import Path
import os

class AudioPlayer:
    def __init__(self):
        self.audio_dir = Path.home() / ".claude" / "audio"
        self.system = platform.system()
        # Check for auto-accept mode
        self.auto_accept = os.environ.get('CLAUDE_AUTO_ACCEPT', '').lower() in ['1', 'true', 'yes']
        
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
        """Play audio file based on sound key"""
        audio_file = self.audio_map.get(sound_key)
        if not audio_file:
            return False
            
        audio_path = self.audio_dir / audio_file
        
        if not audio_path.exists():
            print(f"[AUDIO] File not found: {audio_path}", file=sys.stderr)
            return False
        
        if self.system == "Windows":
            # Try multiple methods for Windows
            
            # Method 1: winsound (built-in, SYNCHRONOUS for reliability)
            try:
                import winsound
                if os.environ.get('CLAUDE_DEBUG'):
                    print(f"[AUDIO] winsound attempting: {audio_path.name}", file=sys.stderr)
                # Use SYNCHRONOUS playback - no SND_ASYNC flag
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME)
                if os.environ.get('CLAUDE_DEBUG'):
                    print(f"[AUDIO] winsound SUCCESS: {audio_path.name}", file=sys.stderr)
                return True
            except Exception as e:
                if os.environ.get('CLAUDE_DEBUG'):
                    print(f"[AUDIO] winsound failed: {e}", file=sys.stderr)
            
            # Method 2: pygame (backup, also synchronous)
            try:
                import pygame
                # Initialize if not already
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                
                # Load and play synchronously
                sound = pygame.mixer.Sound(str(audio_path))
                channel = sound.play()
                
                # Wait for sound to finish
                if channel:
                    import time
                    while channel.get_busy():
                        time.sleep(0.01)
                return True
            except:
                pass
            
            # Method 3: PowerShell (last resort, also synchronous)
            try:
                subprocess.run([
                    "powershell", "-WindowStyle", "Hidden", "-c",
                    f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync()"
                ], check=True, capture_output=True, timeout=3)
                return True
            except:
                pass
            
        elif self.system == "Darwin":  # macOS
            try:
                subprocess.run(["afplay", str(audio_path)], check=True, capture_output=True)
                return True
            except:
                pass
        
        elif self.system == "Linux":
            # Try various Linux audio players
            for player in ["aplay", "paplay", "ffplay -nodisp -autoexit", "mpg123"]:
                try:
                    subprocess.run(player.split() + [str(audio_path)], check=True, capture_output=True)
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
        
        # SessionStart event
        if event == "SessionStart":
            if self.auto_accept:
                return "auto_mode"
            return "session_start"
        
        # Stop event - Claude finished, user's turn
        if event == "Stop":
            return "ready"
        
        # PreToolUse events - BEFORE confirmation prompts
        if event == "PreToolUse":
            if tool in ["Write", "Edit", "MultiEdit"]:
                # File operations - be specific if possible
                if self.auto_accept:
                    return "auto_accepting"
                    
                # Try to determine file operation type from context
                file_path = tool_input.get("file_path", "").lower()
                if tool == "Write" and not Path(file_path).exists() if file_path else False:
                    return "file_touch"  # Creating new file
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
                elif any(x in command for x in ["apt", "brew", "yarn add"]):
                    return "install_packages"
                
                # Testing - SPECIFIC
                elif any(x in command for x in ["pytest", "jest", "cargo test", "npm test"]):
                    return "test_running"
                
                # Docker - SPECIFIC
                elif "docker build" in command:
                    return "docker_build"
                elif any(x in command for x in ["docker run", "docker-compose up"]):
                    return "docker_run"
                
                # Network Operations - SPECIFIC
                elif any(x in command for x in ["curl", "http"]):
                    return "net_http"
                elif any(x in command for x in ["wget", "download"]):
                    return "net_download"
                elif "ssh" in command:
                    return "net_ssh"
                
                # Search Operations - SPECIFIC
                elif any(x in command for x in ["find", "grep", "rg ", "fd "]):
                    return "search_files"
                
                # Virtual Environment Check
                elif any(x in command for x in ["venv", "virtualenv", "activate"]):
                    return "venv_activated"
                
                # Check for risky commands
                risky_commands = ["rm -rf", "del /f", "git push --force", "git reset --hard", 
                                  "DROP", "DELETE FROM", "format", "kill -9", "shutdown"]
                if any(risky in command for risky in risky_commands):
                    return "risky_command"
                
                # Default for other commands
                return "processing"
            
            elif tool == "ExitPlanMode":
                # Planning phase complete
                return "planning_exit"
            
            elif tool == "Task":
                # Agent being invoked - try to be specific
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
                # Agent completed
                return "pipeline_complete"
            
            elif tool in ["Write", "Edit", "MultiEdit"]:
                # File operation completed
                response_str = str(tool_response).lower()
                if (tool_response.get("success") or 
                    any(x in response_str for x in ["written", "updated", "created"]) or
                    tool_response is not None):
                    return "file_complete"
                elif "exists" in response_str:
                    return "file_exists"
                elif "permission" in response_str:
                    return "permission_denied"
                return None
            
            elif tool == "Bash":
                # Command completed - check result
                exit_code = tool_response.get("exit_code", -1)
                command = tool_input.get("command", "").lower()
                output = str(tool_response).lower()
                
                if exit_code == 0:
                    # Success - play specific completion sounds
                    if any(x in command for x in ["pytest", "jest", "npm test", "cargo test"]):
                        # Check if tests actually passed
                        if "passed" in output or "success" in output:
                            return "test_passed"
                        elif "failed" in output:
                            return "test_failed"
                    elif any(x in command for x in ["git commit", "git push"]):
                        return "success"
                    elif any(x in command for x in ["npm run", "make", "cargo build"]):
                        return "operation_done"
                    elif any(x in command for x in ["mkdir", "touch", "cp ", "mv "]):
                        return "file_complete"
                    else:
                        return "command_success"
                
                elif exit_code > 0:
                    # Error occurred - play specific error sounds
                    if any(x in command for x in ["pytest", "jest", "npm test"]):
                        return "test_failed"
                    elif "permission denied" in output:
                        return "permission_denied"
                    elif "not found" in output or "no such" in output:
                        return "file_not_found"
                    elif "connection" in output or "network" in output:
                        return "connection_error"
                    else:
                        return "command_failed"
                
                return "operation_done"
            
            elif tool in ["Read", "Glob", "Grep", "LS"]:
                # Don't play sounds for read operations
                return None
            
            elif tool == "WebSearch":
                return "mcp_websearch"
            
            elif tool == "WebFetch":
                return "net_http"
            
            else:
                # Generic completion
                if tool_response.get("success"):
                    return "success"
        
        # UserPromptSubmit - check for special commands
        if event == "UserPromptSubmit":
            prompt = hook_data.get("prompt", "").lower()
            if "/playwright" in prompt:
                return "mcp_playwright"
            elif "/obsidian" in prompt:
                return "mcp_obsidian"
            elif "optimize" in prompt or "performance" in prompt:
                return "optimizing"
            elif "analyze" in prompt or "review" in prompt:
                return "analyzing_code"
            elif "generate" in prompt or "create" in prompt:
                return "generating_code"
        
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
        success = player.play_sound(sound_key)
        if os.environ.get('CLAUDE_DEBUG'):
            event = input_data.get('hook_event_name', 'unknown')
            tool = input_data.get('tool_name', 'none')
            print(f"[AUDIO] Event:{event} Tool:{tool} Key:{sound_key} Success:{success}", file=sys.stderr)
    else:
        # Don't log for every event, only debug mode
        if os.environ.get('CLAUDE_DEBUG'):
            event = input_data.get('hook_event_name', 'unknown')
            tool = input_data.get('tool_name', 'none')
            print(f"[AUDIO] No audio - Event:{event} Tool:{tool}", file=sys.stderr)
    
    # Always exit successfully
    sys.exit(0)

if __name__ == "__main__":
    main()