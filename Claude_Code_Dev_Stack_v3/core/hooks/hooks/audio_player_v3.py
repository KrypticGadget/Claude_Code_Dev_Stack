#!/usr/bin/env python3
"""
Audio Player V3.0 - Enhanced Audio Feedback System
Model, git, and agent-specific sounds with dynamic selection
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Windows-specific audio support
if sys.platform == "win32":
    import winsound

class AudioPlayerV3:
    """
    Enhanced audio player with context-aware sound selection
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.audio_dir = self.home_dir / "audio"
        self.config_file = self.home_dir / "audio_config.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Sound categories
        self.SOUND_CATEGORIES = {
            "model": {
                "opus": ["opus_start.wav", "opus_think.wav", "opus_complete.wav"],
                "sonnet": ["sonnet_start.wav", "sonnet_process.wav", "sonnet_done.wav"],
                "haiku": ["haiku_quick.wav", "haiku_simple.wav", "haiku_fast.wav"]
            },
            "git": {
                "commit": ["git_commit.wav", "version_save.wav"],
                "push": ["git_push.wav", "upload.wav"],
                "pull": ["git_pull.wav", "download.wav"],
                "merge": ["git_merge.wav", "combine.wav"],
                "branch": ["git_branch.wav", "fork.wav"]
            },
            "agent": {
                "orchestrator": ["orchestrate.wav", "coordinate.wav"],
                "analyst": ["analyze.wav", "evaluate.wav"],
                "developer": ["code.wav", "build.wav"],
                "tester": ["test.wav", "validate.wav"],
                "designer": ["design.wav", "create.wav"]
            },
            "phase": {
                "exploration": ["explore.wav", "discover.wav"],
                "requirements": ["requirements.wav", "planning.wav"],
                "design": ["blueprint.wav", "architect.wav"],
                "implementation": ["implement.wav", "develop.wav"],
                "testing": ["testing.wav", "quality.wav"],
                "deployment": ["deploy.wav", "launch.wav"]
            },
            "action": {
                "start": ["start.wav", "begin.wav", "initiate.wav"],
                "complete": ["complete.wav", "done.wav", "success.wav"],
                "error": ["error.wav", "fail.wav", "problem.wav"],
                "warning": ["warning.wav", "caution.wav", "alert.wav"],
                "think": ["thinking.wav", "processing.wav", "analyzing.wav"]
            }
        }
        
        # Default sounds for common events
        self.DEFAULT_SOUNDS = {
            "Task": "orchestrate.wav",
            "Write": "write.wav",
            "Edit": "edit.wav",
            "MultiEdit": "multi_edit.wav",
            "Bash": "terminal.wav",
            "Read": "read.wav",
            "ExitPlanMode": "plan_complete.wav"
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load audio configuration"""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                pass
        
        # Default configuration
        return {
            "enabled": True,
            "volume": 0.7,
            "model_specific": True,
            "git_sounds": True,
            "agent_sounds": True,
            "phase_sounds": True,
            "random_variation": True
        }
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current system context for sound selection"""
        context = {}
        
        # Get model
        model_file = self.home_dir / "current_model"
        if model_file.exists():
            model = model_file.read_text().strip()
            if "opus" in model.lower():
                context["model"] = "opus"
            elif "sonnet" in model.lower():
                context["model"] = "sonnet"
            elif "haiku" in model.lower():
                context["model"] = "haiku"
            else:
                context["model"] = "default"
        
        # Get git context
        try:
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=1
            ).stdout.strip()
            context["git_branch"] = branch
        except:
            context["git_branch"] = None
        
        # Get phase
        phase_file = self.home_dir / "current_phase"
        if phase_file.exists():
            context["phase"] = phase_file.read_text().strip()
        else:
            context["phase"] = "exploration"
        
        # Get active agent
        agents_file = self.home_dir / "active_agents.json"
        if agents_file.exists():
            try:
                agents = json.loads(agents_file.read_text())
                context["agents"] = agents
            except:
                context["agents"] = []
        
        return context
    
    def select_sound(self, event_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Select appropriate sound based on event and context"""
        if not self.config["enabled"]:
            return None
        
        possible_sounds = []
        
        # Check for event-specific default sound
        if event_type in self.DEFAULT_SOUNDS:
            default_sound = self.DEFAULT_SOUNDS[event_type]
            sound_path = self.audio_dir / default_sound
            if sound_path.exists():
                possible_sounds.append(str(sound_path))
        
        # Add model-specific sounds
        if self.config["model_specific"] and "model" in context:
            model = context["model"]
            if model in self.SOUND_CATEGORIES["model"]:
                for sound in self.SOUND_CATEGORIES["model"][model]:
                    sound_path = self.audio_dir / sound
                    if sound_path.exists():
                        possible_sounds.append(str(sound_path))
        
        # Add git-specific sounds
        if self.config["git_sounds"] and event_type == "Bash":
            # Check if it's a git command
            git_actions = {
                "commit": ["commit"],
                "push": ["push"],
                "pull": ["pull", "fetch"],
                "merge": ["merge", "rebase"],
                "branch": ["branch", "checkout"]
            }
            
            for action, keywords in git_actions.items():
                if any(kw in str(sys.argv) for kw in keywords):
                    if action in self.SOUND_CATEGORIES["git"]:
                        for sound in self.SOUND_CATEGORIES["git"][action]:
                            sound_path = self.audio_dir / sound
                            if sound_path.exists():
                                possible_sounds.append(str(sound_path))
        
        # Add agent-specific sounds
        if self.config["agent_sounds"] and context.get("agents"):
            agent_types = {
                "orchestrator": ["orchestrator"],
                "analyst": ["analyst", "business", "financial"],
                "developer": ["backend", "frontend", "mobile"],
                "tester": ["test", "qa", "automation"],
                "designer": ["ui", "ux", "design"]
            }
            
            for agent in context["agents"]:
                for agent_type, keywords in agent_types.items():
                    if any(kw in agent.lower() for kw in keywords):
                        if agent_type in self.SOUND_CATEGORIES["agent"]:
                            for sound in self.SOUND_CATEGORIES["agent"][agent_type]:
                                sound_path = self.audio_dir / sound
                                if sound_path.exists():
                                    possible_sounds.append(str(sound_path))
        
        # Add phase-specific sounds
        if self.config["phase_sounds"] and "phase" in context:
            phase = context["phase"]
            if phase in self.SOUND_CATEGORIES["phase"]:
                for sound in self.SOUND_CATEGORIES["phase"][phase]:
                    sound_path = self.audio_dir / sound
                    if sound_path.exists():
                        possible_sounds.append(str(sound_path))
        
        # Select sound
        if possible_sounds:
            if self.config["random_variation"] and len(possible_sounds) > 1:
                return random.choice(possible_sounds)
            else:
                return possible_sounds[0]
        
        # Fallback to generic action sounds
        action = "start" if "start" in event_type.lower() else "complete"
        if action in self.SOUND_CATEGORIES["action"]:
            for sound in self.SOUND_CATEGORIES["action"][action]:
                sound_path = self.audio_dir / sound
                if sound_path.exists():
                    return str(sound_path)
        
        return None
    
    def play_sound(self, sound_path: str):
        """Play the selected sound"""
        try:
            if sys.platform == "win32":
                # Use synchronous playback to ensure sound plays completely
                winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                if os.environ.get("CLAUDE_DEBUG"):
                    print(f"[AudioV3] Played: {Path(sound_path).name}", file=sys.stderr)
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["afplay", sound_path], check=False)
            else:
                # Linux - try multiple players
                for player in ["aplay", "paplay", "play"]:
                    try:
                        subprocess.run([player, sound_path], check=True)
                        break
                    except:
                        continue
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG"):
                print(f"[AudioV3] Error playing sound: {e}", file=sys.stderr)
    
    def handle_event(self, event_type: str):
        """Handle an audio event"""
        # Get context
        context = self.get_current_context()
        
        # Select sound
        sound_path = self.select_sound(event_type, context)
        
        # Play sound
        if sound_path:
            self.play_sound(sound_path)
        elif os.environ.get("CLAUDE_DEBUG"):
            print(f"[AudioV3] No sound found for event: {event_type}", file=sys.stderr)
    
    def create_sound_profile(self, profile_name: str, sounds: Dict[str, str]):
        """Create a custom sound profile"""
        profiles_dir = self.home_dir / "sound_profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        
        profile_file = profiles_dir / f"{profile_name}.json"
        profile_file.write_text(json.dumps(sounds, indent=2))
    
    def load_sound_profile(self, profile_name: str):
        """Load a custom sound profile"""
        profile_file = self.home_dir / "sound_profiles" / f"{profile_name}.json"
        if profile_file.exists():
            try:
                profile = json.loads(profile_file.read_text())
                # Update DEFAULT_SOUNDS with profile
                self.DEFAULT_SOUNDS.update(profile)
                return True
            except:
                pass
        return False

def main():
    """Main entry point for audio player"""
    player = AudioPlayerV3()
    
    # Get event type from environment or arguments
    event_type = os.environ.get("CLAUDE_TOOL_NAME")
    
    if not event_type and len(sys.argv) > 1:
        event_type = sys.argv[1]
    
    if event_type:
        player.handle_event(event_type)
    else:
        # Play default sound
        player.handle_event("start")

if __name__ == "__main__":
    main()