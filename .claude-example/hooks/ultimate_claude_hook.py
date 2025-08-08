#!/usr/bin/env python3
"""
Ultimate Claude Code Hook - Simplified Integration
Combines orchestration, audio, agent routing, and meta-prompting
"""

import json
import re
import subprocess
import platform
import time
from pathlib import Path
from typing import Dict, List, Optional
import queue
import threading

# Global instances
_orchestrator = None
_audio_system = None

class SimpleAudioSystem:
    """Lightweight audio player"""
    
    def __init__(self):
        self.audio_dir = Path(__file__).parent.parent / "audio"
        self.queue = queue.Queue()
        self.cooldowns = {}
        self.min_interval = 2.0
        
        # Start player thread
        threading.Thread(target=self._player, daemon=True).start()
    
    def play(self, sound: str):
        """Queue a sound"""
        now = time.time()
        if sound in self.cooldowns and now - self.cooldowns[sound] < self.min_interval:
            return
        self.cooldowns[sound] = now
        self.queue.put(sound)
    
    def _player(self):
        """Background player"""
        while True:
            try:
                sound = self.queue.get(timeout=1)
                file = self.audio_dir / f"{sound}.wav"
                if file.exists():
                    if platform.system() == "Windows":
                        subprocess.run(
                            ["powershell", "-c", f"(New-Object Media.SoundPlayer '{file}').PlaySync()"],
                            capture_output=True, timeout=5
                        )
            except:
                pass

class UltimateOrchestrator:
    """Main orchestration logic"""
    
    def __init__(self):
        self.audio = SimpleAudioSystem()
        self.current_phase = None
        self.pending_input = None
        
        # Agent mappings
        self.agents = {
            'backend': ['backend', 'api', 'server', 'endpoint'],
            'frontend': ['frontend', 'ui', 'react', 'vue'],
            'database': ['database', 'schema', 'sql', 'query'],
            'security': ['security', 'auth', 'oauth', 'encryption'],
            'testing': ['test', 'qa', 'coverage'],
            'devops': ['deploy', 'docker', 'kubernetes', 'ci/cd'],
            'architect': ['architecture', 'design', 'system'],
            'prompt': ['prompt', 'meta', 'optimize']
        }
        
        # Phase patterns
        self.phases = {
            'project_created': r'project.*(?:created|initialized)',
            'dependencies_installed': r'dependencies.*installed',
            'backend_complete': r'backend.*(?:complete|ready)',
            'frontend_complete': r'frontend.*(?:complete|ready)',
            'tests_pass': r'tests.*pass',
            'build_successful': r'build.*successful',
            'deploy_complete': r'deploy.*complete'
        }
        
        # Input patterns
        self.inputs = {
            'yes_no_question': r'yes.*no|y\/n|\?$',
            'multiple_choice': r'\d\.\s+\w+|choose|select',
            'awaiting_confirmation': r'confirm|proceed\?',
            'awaiting_response': r'\?$'
        }
    
    def process_user_input(self, text: str) -> Dict:
        """Process user input"""
        result = {'agents': [], 'audio': [], 'transform': False}
        
        # Check if needs meta-prompting
        if self._needs_transform(text):
            self.audio.play('meta_prompt_transforming')
            result['transform'] = True
            result['audio'].append('meta_prompt_transforming')
        
        # Detect agents
        text_lower = text.lower()
        for agent, triggers in self.agents.items():
            if any(t in text_lower for t in triggers):
                result['agents'].append(agent)
        
        if result['agents']:
            self.audio.play('agent_activated')
            result['audio'].append('agent_activated')
        
        # Complex orchestration
        if len(result['agents']) > 2:
            self.audio.play('orchestrator_engaged')
            result['audio'].append('orchestrator_engaged')
        
        return result
    
    def process_claude_response(self, text: str) -> Dict:
        """Process Claude response"""
        result = {'phase': None, 'input': None, 'audio': []}
        text_lower = text.lower()
        
        # Check phases
        for phase, pattern in self.phases.items():
            if re.search(pattern, text_lower):
                if phase != self.current_phase:
                    self.current_phase = phase
                    self.audio.play(phase)
                    result['phase'] = phase
                    result['audio'].append(phase)
                break
        
        # Check input needs
        for input_type, pattern in self.inputs.items():
            if re.search(pattern, text_lower):
                if input_type != self.pending_input:
                    self.pending_input = input_type
                    self.audio.play(input_type)
                    result['input'] = input_type
                    result['audio'].append(input_type)
                break
        
        # Success detection
        if any(word in text_lower for word in ['complete', 'success', 'ready', 'done']):
            if 'pipeline_complete' not in result['audio']:
                self.audio.play('pipeline_complete')
                result['audio'].append('pipeline_complete')
        
        return result
    
    def _needs_transform(self, text: str) -> bool:
        """Check if needs meta-prompting"""
        # Vague indicators
        if len(text.split()) < 5 and '?' in text:
            return True
        
        # Missing specifics
        vague_starts = ['help', 'how', 'can you', 'build', 'create']
        return any(text.lower().startswith(v) for v in vague_starts) and '@' not in text

def process_message(message: str, is_user: bool = True) -> Dict:
    """Main processing function"""
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = UltimateOrchestrator()
    
    if is_user:
        return _orchestrator.process_user_input(message)
    else:
        return _orchestrator.process_claude_response(message)

def hook_handler(event: Dict) -> Dict:
    """Hook handler for Claude Code"""
    try:
        event_type = event.get('type', '')
        
        if event_type == 'user_message':
            return process_message(event.get('message', ''), is_user=True)
        elif event_type == 'claude_response':
            return process_message(event.get('response', ''), is_user=False)
        elif event_type == 'play_sound':
            if _orchestrator:
                _orchestrator.audio.play(event.get('sound', ''))
            return {'played': True}
        
        return {'processed': True}
    except:
        return {'processed': False}

# Export
__all__ = ['hook_handler', 'process_message']