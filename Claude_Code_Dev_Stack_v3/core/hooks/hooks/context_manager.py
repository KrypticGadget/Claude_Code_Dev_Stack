#!/usr/bin/env python3
"""
Context Manager - V3.0 Intelligent Context Management
Handles handoffs, compaction suggestions, and phase transitions
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class ContextManager:
    """
    Manages conversation context, handoffs, and documentation
    Provides intelligent suggestions for context optimization
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.context_file = self.home_dir / "context_state.json"
        self.handoff_dir = self.home_dir / "handoffs"
        
        # Ensure directories exist
        self.home_dir.mkdir(parents=True, exist_ok=True)
        self.handoff_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize context
        self.context = self.load_context()
        
        # Thresholds and limits
        self.TOKEN_WARNING = 0.8  # 80% threshold
        self.TOKEN_CRITICAL = 0.9  # 90% threshold
        self.DEPTH_WARNING = 15
        self.DEPTH_CRITICAL = 20
        
        # Phase transition points
        self.PHASE_TRANSITIONS = {
            "exploration": ["requirements", "design"],
            "requirements": ["design", "implementation"],
            "design": ["implementation", "testing"],
            "implementation": ["testing", "debugging"],
            "testing": ["deployment", "debugging"],
            "debugging": ["testing", "implementation"],
            "deployment": ["production", "maintenance"]
        }
    
    def load_context(self) -> Dict[str, Any]:
        """Load current context state"""
        if self.context_file.exists():
            try:
                return json.loads(self.context_file.read_text())
            except:
                pass
        
        # Initialize new context
        return {
            "session_id": self.generate_session_id(),
            "started": datetime.now().isoformat(),
            "phase": "exploration",
            "tokens": {"current": 0, "limit": 100000},
            "depth": 1,
            "key_decisions": [],
            "active_files": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "handoff_count": 0
        }
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def update_token_count(self, tokens: int):
        """Update current token count"""
        self.context["tokens"]["current"] = tokens
        self.save_context()
        
        # Check if action needed
        percentage = self.get_token_percentage()
        if percentage >= self.TOKEN_CRITICAL:
            return self.trigger_critical_action()
        elif percentage >= self.TOKEN_WARNING:
            return self.suggest_compaction()
        return None
    
    def get_token_percentage(self) -> float:
        """Calculate token usage percentage"""
        tokens = self.context["tokens"]
        return (tokens["current"] / tokens["limit"]) * 100
    
    def increment_depth(self):
        """Increment conversation depth"""
        self.context["depth"] += 1
        self.save_context()
        
        # Check if handoff needed
        if self.context["depth"] >= self.DEPTH_CRITICAL:
            return self.suggest_handoff("deep_conversation")
        elif self.context["depth"] >= self.DEPTH_WARNING:
            return self.suggest_phase_transition()
        return None
    
    def add_key_decision(self, decision: str):
        """Record a key decision"""
        self.context["key_decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        })
        self.save_context()
    
    def add_active_file(self, filepath: str):
        """Track an active file"""
        if filepath not in self.context["active_files"]:
            self.context["active_files"].append(filepath)
            self.save_context()
    
    def complete_task(self, task: str):
        """Mark a task as completed"""
        self.context["completed_tasks"].append({
            "timestamp": datetime.now().isoformat(),
            "task": task
        })
        
        # Remove from pending if exists
        self.context["pending_tasks"] = [
            t for t in self.context["pending_tasks"] if t != task
        ]
        self.save_context()
    
    def add_pending_task(self, task: str):
        """Add a pending task"""
        if task not in self.context["pending_tasks"]:
            self.context["pending_tasks"].append(task)
            self.save_context()
    
    def suggest_compaction(self) -> Dict[str, Any]:
        """Suggest context compaction"""
        return {
            "action": "suggest_compact",
            "reason": f"Token usage at {self.get_token_percentage():.1f}%",
            "recommendation": "Use /compact command to optimize context",
            "compactable": self.identify_compactable_sections()
        }
    
    def identify_compactable_sections(self) -> List[str]:
        """Identify what can be compacted"""
        sections = []
        
        # Check for repetitive content
        if len(self.context["completed_tasks"]) > 10:
            sections.append("Completed tasks history")
        
        # Check for old decisions
        if len(self.context["key_decisions"]) > 20:
            sections.append("Older key decisions")
        
        # Check for inactive files
        if len(self.context["active_files"]) > 15:
            sections.append("Inactive file references")
        
        return sections
    
    def suggest_handoff(self, reason: str) -> Dict[str, Any]:
        """Suggest documentation handoff"""
        return {
            "action": "suggest_handoff",
            "reason": reason,
            "recommendation": "Generate handoff documentation and start new chat",
            "handoff_template": self.generate_handoff_template()
        }
    
    def suggest_phase_transition(self) -> Dict[str, Any]:
        """Suggest moving to next phase"""
        current_phase = self.context["phase"]
        next_phases = self.PHASE_TRANSITIONS.get(current_phase, [])
        
        if not next_phases:
            return None
        
        return {
            "action": "suggest_phase_transition",
            "current_phase": current_phase,
            "suggested_phases": next_phases,
            "recommendation": f"Consider transitioning from {current_phase} to {next_phases[0]}"
        }
    
    def trigger_critical_action(self) -> Dict[str, Any]:
        """Trigger critical context action"""
        return {
            "action": "critical_handoff_required",
            "reason": f"Token usage critical at {self.get_token_percentage():.1f}%",
            "requirement": "Must generate handoff documentation immediately",
            "handoff_document": self.generate_handoff_document()
        }
    
    def generate_handoff_template(self) -> Dict[str, Any]:
        """Generate handoff documentation template"""
        return {
            "session_id": self.context["session_id"],
            "phase": self.context["phase"],
            "summary": "## Work Completed\n[Summary of achievements]\n",
            "current_state": {
                "active_files": self.context["active_files"],
                "pending_tasks": self.context["pending_tasks"],
                "key_decisions": self.context["key_decisions"][-5:]  # Last 5 decisions
            },
            "next_steps": "## Next Phase Directives\n[Clear instructions for continuation]\n",
            "technical_context": "## Technical Context\n[Critical technical details]\n"
        }
    
    def generate_handoff_document(self) -> str:
        """Generate complete handoff documentation"""
        template = self.generate_handoff_template()
        
        doc = f"""# Handoff Documentation
**Session**: {template['session_id']}
**Phase**: {template['phase']}
**Generated**: {datetime.now().isoformat()}

## Work Completed
- Completed {len(self.context['completed_tasks'])} tasks
- Made {len(self.context['key_decisions'])} key decisions
- Modified {len(self.context['active_files'])} files

### Key Decisions
"""
        
        # Add recent decisions
        for decision in self.context["key_decisions"][-5:]:
            doc += f"- {decision['decision']}\n"
        
        doc += f"""

## Current State
### Active Files
"""
        for file in self.context["active_files"][-10:]:
            doc += f"- {file}\n"
        
        doc += f"""

### Pending Tasks
"""
        for task in self.context["pending_tasks"]:
            doc += f"- [ ] {task}\n"
        
        doc += """

## Next Phase Directives
1. Review pending tasks above
2. Continue with current phase objectives
3. Maintain established patterns and decisions

## Technical Context Preserved
- Development phase: {phase}
- Token usage: {tokens:.1f}%
- Conversation depth: {depth}
- Session duration: Active since {started}

## Continuation Command
```
claude --resume-from {handoff_file}
```
""".format(
            phase=self.context["phase"],
            tokens=self.get_token_percentage(),
            depth=self.context["depth"],
            started=self.context["started"],
            handoff_file=f"handoff_{self.context['session_id']}.md"
        )
        
        # Save handoff document
        handoff_path = self.handoff_dir / f"handoff_{self.context['session_id']}.md"
        handoff_path.write_text(doc)
        
        # Increment handoff count
        self.context["handoff_count"] += 1
        self.save_context()
        
        return doc
    
    def transition_phase(self, new_phase: str):
        """Transition to a new development phase"""
        old_phase = self.context["phase"]
        self.context["phase"] = new_phase
        
        # Record transition
        self.add_key_decision(f"Transitioned from {old_phase} to {new_phase}")
        
        # Generate phase transition document
        self.generate_phase_transition_doc(old_phase, new_phase)
        
        self.save_context()
    
    def generate_phase_transition_doc(self, old_phase: str, new_phase: str):
        """Generate phase transition documentation"""
        doc = f"""# Phase Transition Documentation
**From**: {old_phase}
**To**: {new_phase}
**Timestamp**: {datetime.now().isoformat()}

## {old_phase.title()} Phase Summary
- Completed tasks: {len(self.context['completed_tasks'])}
- Key decisions: {len(self.context['key_decisions'])}
- Files modified: {len(self.context['active_files'])}

## {new_phase.title()} Phase Objectives
"""
        
        # Add phase-specific objectives
        objectives = {
            "requirements": ["Gather all requirements", "Define acceptance criteria", "Create specifications"],
            "design": ["Create architecture", "Design interfaces", "Plan implementation"],
            "implementation": ["Write code", "Implement features", "Create tests"],
            "testing": ["Run tests", "Fix bugs", "Validate requirements"],
            "deployment": ["Prepare deployment", "Update documentation", "Release"]
        }
        
        for obj in objectives.get(new_phase, ["Continue with phase objectives"]):
            doc += f"- [ ] {obj}\n"
        
        # Save transition document
        transition_path = self.handoff_dir / f"transition_{old_phase}_to_{new_phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        transition_path.write_text(doc)
    
    def save_context(self):
        """Save current context state"""
        self.context_file.write_text(json.dumps(self.context, indent=2))
    
    def get_status(self) -> Dict[str, Any]:
        """Get current context status"""
        return {
            "session_id": self.context["session_id"],
            "phase": self.context["phase"],
            "token_percentage": self.get_token_percentage(),
            "depth": self.context["depth"],
            "health": self.assess_health(),
            "recommendations": self.get_recommendations()
        }
    
    def assess_health(self) -> str:
        """Assess context health"""
        token_pct = self.get_token_percentage()
        depth = self.context["depth"]
        
        if token_pct >= self.TOKEN_CRITICAL or depth >= self.DEPTH_CRITICAL:
            return "critical"
        elif token_pct >= self.TOKEN_WARNING or depth >= self.DEPTH_WARNING:
            return "warning"
        return "good"
    
    def get_recommendations(self) -> List[str]:
        """Get current recommendations"""
        recommendations = []
        
        token_pct = self.get_token_percentage()
        if token_pct >= self.TOKEN_CRITICAL:
            recommendations.append("Immediate handoff required")
        elif token_pct >= self.TOKEN_WARNING:
            recommendations.append("Consider using /compact")
        
        depth = self.context["depth"]
        if depth >= self.DEPTH_CRITICAL:
            recommendations.append("Start new chat with handoff")
        elif depth >= self.DEPTH_WARNING:
            recommendations.append("Consider phase transition")
        
        return recommendations

def main():
    """Main entry point for context management"""
    manager = ContextManager()
    
    # Parse command
    if len(sys.argv) < 2:
        print(json.dumps(manager.get_status(), indent=2))
        return
    
    command = sys.argv[1]
    
    if command == "status":
        print(json.dumps(manager.get_status(), indent=2))
    
    elif command == "handoff":
        doc = manager.generate_handoff_document()
        print(f"Handoff document generated: {manager.handoff_dir}/handoff_{manager.context['session_id']}.md")
    
    elif command == "compact":
        suggestion = manager.suggest_compaction()
        print(json.dumps(suggestion, indent=2))
    
    elif command == "transition" and len(sys.argv) > 2:
        new_phase = sys.argv[2]
        manager.transition_phase(new_phase)
        print(f"Transitioned to {new_phase} phase")
    
    elif command == "add-decision" and len(sys.argv) > 2:
        decision = " ".join(sys.argv[2:])
        manager.add_key_decision(decision)
        print(f"Decision recorded: {decision}")
    
    elif command == "complete-task" and len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        manager.complete_task(task)
        print(f"Task completed: {task}")
    
    else:
        print("Usage: context_manager.py [status|handoff|compact|transition <phase>|add-decision <text>|complete-task <text>]")

if __name__ == "__main__":
    main()