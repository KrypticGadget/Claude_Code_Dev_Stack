#!/usr/bin/env python3
"""
Audio Controller Hook - Manages all audio playback for Claude Code
Works with the master orchestrator to provide audio feedback
"""

import json
import re
import subprocess
import platform
import queue
import threading
import time
from pathlib import Path
from typing import Dict, Optional

class AudioController:
    """
    Manages audio playback with queue and cooldown
    """
    
    def __init__(self):
        self.audio_dir = Path(__file__).parent.parent / "audio"
        self.play_queue = queue.Queue()
        self.cooldown = {}
        self.min_interval = 2.0  # seconds between same sound
        self.enabled = True
        
        # Start player thread
        self.player_thread = threading.Thread(target=self._player_loop, daemon=True)
        self.player_thread.start()
        
        # Sound mappings for quick triggers
        self.quick_triggers = {
            # Common patterns to sounds
            'starting': 'project_created',
            'installing': 'dependencies_installed',
            'testing': 'unit_tests_pass',
            'building': 'build_started',
            'deploying': 'deploy_initiated',
            'complete': 'pipeline_complete',
            'success': 'milestone_complete',
            'waiting': 'awaiting_response',
            'error': 'clarification_needed',
            'ready': 'ready_for_input'
        }
    
    def process_text(self, text: str, context: str = 'general') -> Dict:
        """
        Process text and trigger appropriate audio
        """
        if not self.enabled:
            return {'audio_played': []}
        
        played = []
        text_lower = text.lower()
        
        # Check quick triggers
        for trigger, sound in self.quick_triggers.items():
            if trigger in text_lower:
                if self.play(sound):
                    played.append(sound)
                break  # Only play one quick trigger
        
        # Check for questions needing input
        if text.rstrip().endswith('?'):
            if 'yes' in text_lower and 'no' in text_lower:
                if self.play('yes_no_question'):
                    played.append('yes_no_question')
            elif any(word in text_lower for word in ['select', 'choose', 'pick', 'option']):
                if self.play('multiple_choice'):
                    played.append('multiple_choice')
            elif self.play('awaiting_response'):
                played.append('awaiting_response')
        
        # Check for completion patterns
        completion_patterns = [
            (r'successfully.*(?:created|installed|deployed)', 'milestone_complete'),
            (r'all.*tests.*pass', 'unit_tests_pass'),
            (r'build.*successful', 'build_successful'),
            (r'deployment.*complete', 'deploy_complete'),
            (r'environment.*ready', 'environment_ready'),
            (r'requirements.*complete', 'requirements_gathered'),
            (r'architecture.*designed', 'architecture_designed')
        ]
        
        for pattern, sound in completion_patterns:
            if re.search(pattern, text_lower):
                if self.play(sound):
                    played.append(sound)
                    break
        
        return {'audio_played': played}
    
    def play(self, sound_name: str) -> bool:
        """
        Queue sound for playback with cooldown check
        """
        # Check cooldown
        now = time.time()
        if sound_name in self.cooldown:
            if now - self.cooldown[sound_name] < self.min_interval:
                return False
        
        self.cooldown[sound_name] = now
        self.play_queue.put(sound_name)
        return True
    
    def _player_loop(self):
        """
        Background thread for playing sounds
        """
        while True:
            try:
                sound_name = self.play_queue.get(timeout=1)
                self._play_sound(sound_name)
            except queue.Empty:
                continue
            except Exception:
                pass  # Fail silently
    
    def _play_sound(self, sound_name: str):
        """
        Actually play the sound file
        """
        sound_file = self.audio_dir / f"{sound_name}.wav"
        
        # Check if file exists
        if not sound_file.exists():
            # Try to find partial match
            for file in self.audio_dir.glob("*.wav"):
                if sound_name in file.stem:
                    sound_file = file
                    break
            else:
                return  # No matching file found
        
        system = platform.system()
        try:
            if system == "Windows":
                # Windows: Use PowerShell
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{sound_file}').PlaySync()"],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
            elif system == "Darwin":
                # macOS: Use afplay
                subprocess.run(
                    ["afplay", str(sound_file)],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
            else:
                # Linux: Try paplay or aplay
                try:
                    subprocess.run(
                        ["paplay", str(sound_file)],
                        capture_output=True,
                        timeout=5,
                        check=False
                    )
                except FileNotFoundError:
                    subprocess.run(
                        ["aplay", str(sound_file)],
                        capture_output=True,
                        timeout=5,
                        check=False
                    )
        except Exception:
            pass  # Fail silently
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable audio
        """
        self.enabled = enabled
    
    def get_status(self) -> Dict:
        """
        Get audio system status
        """
        return {
            'enabled': self.enabled,
            'audio_dir': str(self.audio_dir),
            'sounds_available': len(list(self.audio_dir.glob("*.wav"))) if self.audio_dir.exists() else 0,
            'queue_size': self.play_queue.qsize(),
            'cooldowns_active': len(self.cooldown)
        }


# Global instance
audio_controller = None

def get_controller():
    """
    Get or create audio controller instance
    """
    global audio_controller
    if audio_controller is None:
        audio_controller = AudioController()
    return audio_controller


def process_hook(event_type: str, data: Dict) -> Dict:
    """
    Main hook entry point for audio processing
    """
    controller = get_controller()
    
    if event_type == 'claude_response':
        # Process Claude's response for audio triggers
        response = data.get('response', '')
        return controller.process_text(response, 'claude_response')
    
    elif event_type == 'user_message':
        # Process user message (might trigger ready sound)
        message = data.get('message', '')
        return controller.process_text(message, 'user_message')
    
    elif event_type == 'command':
        # Handle audio commands
        command = data.get('command', '')
        if command == 'audio_off':
            controller.set_enabled(False)
            return {'status': 'Audio disabled'}
        elif command == 'audio_on':
            controller.set_enabled(True)
            return {'status': 'Audio enabled'}
        elif command == 'audio_status':
            return controller.get_status()
    
    elif event_type == 'play_sound':
        # Direct sound playback request
        sound = data.get('sound', '')
        if controller.play(sound):
            return {'played': sound}
        else:
            return {'skipped': sound, 'reason': 'cooldown'}
    
    return {'processed': True}


# Export for hook system
__all__ = ['process_hook', 'AudioController']