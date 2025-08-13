#!/usr/bin/env python3
"""
Chat Management System - V3.0 Intelligent Conversation Management
Handles chat flow, handoffs, and documentation generation
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

class ChatManager:
    """
    Manages chat conversations, suggests handoffs, and creates documentation
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.chat_dir = self.home_dir / "chats"
        self.config_file = self.home_dir / "chat_config.json"
        self.current_chat_file = self.home_dir / "current_chat.json"
        
        # Ensure directories exist
        self.home_dir.mkdir(parents=True, exist_ok=True)
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize chat state
        self.chat_state = self.load_chat_state()
        
        # Configuration
        self.config = self.load_config()
        
        # Thresholds for handoff suggestions
        self.HANDOFF_THRESHOLDS = {
            "token_percentage": 85,
            "conversation_depth": 20,
            "time_minutes": 45,
            "error_count": 5,
            "phase_transitions": 3
        }
        
        # Phase-specific handoff points
        self.NATURAL_HANDOFF_POINTS = {
            "exploration": ["requirements", "design"],
            "requirements": ["design", "implementation"],
            "design": ["implementation"],
            "implementation": ["testing", "deployment"],
            "testing": ["deployment", "production"],
            "deployment": ["production", "maintenance"]
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load chat configuration"""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                pass
        
        # Default configuration
        return {
            "auto_handoff": True,
            "auto_document": True,
            "preserve_context": True,
            "handoff_style": "comprehensive",  # minimal, standard, comprehensive
            "notification_enabled": True
        }
    
    def load_chat_state(self) -> Dict[str, Any]:
        """Load current chat state"""
        if self.current_chat_file.exists():
            try:
                return json.loads(self.current_chat_file.read_text())
            except:
                pass
        
        # Initialize new chat state
        return {
            "chat_id": self.generate_chat_id(),
            "started": datetime.now().isoformat(),
            "messages": [],
            "phase": "exploration",
            "depth": 0,
            "tokens": {"current": 0, "limit": 100000},
            "errors": [],
            "transitions": [],
            "key_points": [],
            "active_agents": [],
            "files_modified": [],
            "commands_executed": [],
            "handoff_suggested": False,
            "last_activity": datetime.now().isoformat()
        }
    
    def generate_chat_id(self) -> str:
        """Generate unique chat ID"""
        return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the chat"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content[:1000],  # Truncate long messages
            "metadata": metadata or {}
        }
        
        self.chat_state["messages"].append(message)
        self.chat_state["depth"] += 1
        self.chat_state["last_activity"] = datetime.now().isoformat()
        
        # Extract key information
        if role == "assistant":
            self.extract_key_information(content, metadata)
        
        self.save_chat_state()
        
        # Check if handoff needed
        if self.should_suggest_handoff():
            return self.create_handoff_suggestion()
        
        return None
    
    def extract_key_information(self, content: str, metadata: Dict):
        """Extract key information from assistant messages"""
        content_lower = content.lower()
        
        # Extract files modified
        if metadata.get("tool") in ["Write", "Edit", "MultiEdit"]:
            file_path = metadata.get("file_path")
            if file_path and file_path not in self.chat_state["files_modified"]:
                self.chat_state["files_modified"].append(file_path)
        
        # Extract commands executed
        if metadata.get("tool") == "Bash":
            command = metadata.get("command", "")
            if command:
                self.chat_state["commands_executed"].append({
                    "command": command[:200],
                    "timestamp": datetime.now().isoformat()
                })
        
        # Extract active agents
        if metadata.get("tool") == "Task":
            agent = metadata.get("subagent_type")
            if agent and agent not in self.chat_state["active_agents"]:
                self.chat_state["active_agents"].append(agent)
        
        # Detect key points
        key_indicators = [
            "created", "implemented", "fixed", "resolved",
            "completed", "finished", "deployed", "configured"
        ]
        
        for indicator in key_indicators:
            if indicator in content_lower:
                self.chat_state["key_points"].append({
                    "timestamp": datetime.now().isoformat(),
                    "point": content[:200]
                })
                break
        
        # Detect errors
        if "error" in content_lower or "failed" in content_lower:
            self.chat_state["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": content[:200]
            })
    
    def update_tokens(self, current: int, limit: int = 100000):
        """Update token count"""
        self.chat_state["tokens"]["current"] = current
        self.chat_state["tokens"]["limit"] = limit
        self.save_chat_state()
    
    def transition_phase(self, new_phase: str):
        """Record phase transition"""
        old_phase = self.chat_state["phase"]
        self.chat_state["phase"] = new_phase
        self.chat_state["transitions"].append({
            "from": old_phase,
            "to": new_phase,
            "timestamp": datetime.now().isoformat()
        })
        self.save_chat_state()
        
        # Check if natural handoff point
        if self.is_natural_handoff_point(old_phase, new_phase):
            return self.create_handoff_suggestion("phase_transition")
        
        return None
    
    def is_natural_handoff_point(self, from_phase: str, to_phase: str) -> bool:
        """Check if this is a natural handoff point"""
        natural_transitions = self.NATURAL_HANDOFF_POINTS.get(from_phase, [])
        return to_phase in natural_transitions
    
    def should_suggest_handoff(self) -> bool:
        """Determine if handoff should be suggested"""
        if self.chat_state["handoff_suggested"]:
            return False  # Don't suggest multiple times
        
        # Check token threshold
        token_pct = (self.chat_state["tokens"]["current"] / 
                    self.chat_state["tokens"]["limit"]) * 100
        if token_pct >= self.HANDOFF_THRESHOLDS["token_percentage"]:
            return True
        
        # Check conversation depth
        if self.chat_state["depth"] >= self.HANDOFF_THRESHOLDS["conversation_depth"]:
            return True
        
        # Check time duration
        started = datetime.fromisoformat(self.chat_state["started"])
        duration = datetime.now() - started
        if duration > timedelta(minutes=self.HANDOFF_THRESHOLDS["time_minutes"]):
            return True
        
        # Check error count
        if len(self.chat_state["errors"]) >= self.HANDOFF_THRESHOLDS["error_count"]:
            return True
        
        # Check phase transitions
        if len(self.chat_state["transitions"]) >= self.HANDOFF_THRESHOLDS["phase_transitions"]:
            return True
        
        return False
    
    def create_handoff_suggestion(self, reason: str = "threshold") -> Dict[str, Any]:
        """Create handoff suggestion"""
        self.chat_state["handoff_suggested"] = True
        self.save_chat_state()
        
        suggestion = {
            "type": "handoff_suggestion",
            "reason": reason,
            "chat_id": self.chat_state["chat_id"],
            "metrics": {
                "token_percentage": (self.chat_state["tokens"]["current"] / 
                                   self.chat_state["tokens"]["limit"]) * 100,
                "depth": self.chat_state["depth"],
                "duration_minutes": self.get_chat_duration_minutes(),
                "errors": len(self.chat_state["errors"]),
                "phase_transitions": len(self.chat_state["transitions"])
            },
            "recommendation": self.get_handoff_recommendation(reason),
            "documentation": self.generate_handoff_documentation()
        }
        
        # Save suggestion
        suggestion_file = self.chat_dir / f"handoff_suggestion_{self.chat_state['chat_id']}.json"
        suggestion_file.write_text(json.dumps(suggestion, indent=2))
        
        return suggestion
    
    def get_chat_duration_minutes(self) -> float:
        """Get chat duration in minutes"""
        started = datetime.fromisoformat(self.chat_state["started"])
        duration = datetime.now() - started
        return duration.total_seconds() / 60
    
    def get_handoff_recommendation(self, reason: str) -> str:
        """Get specific handoff recommendation"""
        recommendations = {
            "threshold": "Chat approaching limits. Generate handoff documentation and start new chat.",
            "phase_transition": "Natural transition point reached. Good time for handoff.",
            "errors": "Multiple errors encountered. Consider fresh start with context.",
            "time": "Long session detected. Recommend break and handoff.",
            "tokens": "Token limit approaching. Must handoff to continue.",
            "manual": "User-requested handoff."
        }
        return recommendations.get(reason, "Consider generating handoff documentation.")
    
    def generate_handoff_documentation(self) -> str:
        """Generate comprehensive handoff documentation"""
        doc = f"""# Chat Handoff Documentation
Generated: {datetime.now().isoformat()}
Chat ID: {self.chat_state['chat_id']}
Duration: {self.get_chat_duration_minutes():.1f} minutes

## Session Overview
- **Current Phase**: {self.chat_state['phase']}
- **Messages Exchanged**: {self.chat_state['depth']}
- **Token Usage**: {self.chat_state['tokens']['current']:,} / {self.chat_state['tokens']['limit']:,} ({(self.chat_state['tokens']['current'] / self.chat_state['tokens']['limit'] * 100):.1f}%)
- **Active Agents**: {', '.join(self.chat_state['active_agents']) if self.chat_state['active_agents'] else 'None'}

## Work Completed
"""
        
        # Add key points
        if self.chat_state["key_points"]:
            doc += "### Key Achievements\n"
            for point in self.chat_state["key_points"][-10:]:  # Last 10 points
                doc += f"- {point['point']}\n"
        
        # Add files modified
        if self.chat_state["files_modified"]:
            doc += "\n### Files Modified\n"
            for file_path in self.chat_state["files_modified"][-20:]:  # Last 20 files
                doc += f"- `{file_path}`\n"
        
        # Add commands executed
        if self.chat_state["commands_executed"]:
            doc += "\n### Key Commands Executed\n"
            for cmd in self.chat_state["commands_executed"][-10:]:  # Last 10 commands
                doc += f"- `{cmd['command']}`\n"
        
        # Add phase transitions
        if self.chat_state["transitions"]:
            doc += "\n### Phase Transitions\n"
            for transition in self.chat_state["transitions"]:
                doc += f"- {transition['from']} → {transition['to']}\n"
        
        # Add errors if any
        if self.chat_state["errors"]:
            doc += "\n### Errors Encountered\n"
            for error in self.chat_state["errors"][-5:]:  # Last 5 errors
                doc += f"- {error['error']}\n"
        
        # Add continuation instructions
        doc += f"""
## Continuation Instructions

### To Resume This Chat
```bash
claude --resume-from {self.chat_dir}/handoff_{self.chat_state['chat_id']}.md
```

### Current Context
The session is in the **{self.chat_state['phase']}** phase. 
"""
        
        # Add phase-specific instructions
        phase_instructions = {
            "exploration": "Continue exploring requirements and understanding the problem space.",
            "requirements": "Complete requirement gathering and create specifications.",
            "design": "Finalize system design and architecture decisions.",
            "implementation": "Continue implementing features according to design.",
            "testing": "Complete testing and ensure quality standards are met.",
            "deployment": "Prepare for deployment and production release.",
            "production": "Monitor and maintain the production system."
        }
        
        doc += phase_instructions.get(self.chat_state["phase"], "Continue with current objectives.")
        
        # Add recent messages for context
        doc += "\n\n### Recent Context (Last 5 Messages)\n"
        for msg in self.chat_state["messages"][-5:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            doc += f"\n**{role}**: {msg['content'][:200]}...\n"
        
        # Save documentation
        handoff_file = self.chat_dir / f"handoff_{self.chat_state['chat_id']}.md"
        handoff_file.write_text(doc)
        
        return doc
    
    def archive_chat(self):
        """Archive current chat and start fresh"""
        # Generate final documentation
        final_doc = self.generate_handoff_documentation()
        
        # Archive chat state
        archive_file = self.chat_dir / f"archived_{self.chat_state['chat_id']}.json"
        archive_file.write_text(json.dumps(self.chat_state, indent=2))
        
        # Reset for new chat
        self.chat_state = self.load_chat_state()
        self.chat_state["handoff_suggested"] = False
        self.save_chat_state()
        
        return {
            "archived": True,
            "chat_id": archive_file.stem,
            "documentation": final_doc
        }
    
    def get_chat_health(self) -> Dict[str, Any]:
        """Assess current chat health"""
        token_pct = (self.chat_state["tokens"]["current"] / 
                    self.chat_state["tokens"]["limit"]) * 100
        
        # Determine health status
        if token_pct >= 90 or self.chat_state["depth"] >= 25:
            health = "critical"
        elif token_pct >= 75 or self.chat_state["depth"] >= 20:
            health = "warning"
        else:
            health = "good"
        
        return {
            "status": health,
            "metrics": {
                "token_usage": f"{token_pct:.1f}%",
                "depth": self.chat_state["depth"],
                "duration_minutes": self.get_chat_duration_minutes(),
                "error_count": len(self.chat_state["errors"]),
                "phase": self.chat_state["phase"]
            },
            "recommendations": self.get_health_recommendations(health, token_pct)
        }
    
    def get_health_recommendations(self, health: str, token_pct: float) -> List[str]:
        """Get health-based recommendations"""
        recommendations = []
        
        if health == "critical":
            recommendations.append("Immediate handoff required - approaching limits")
        elif health == "warning":
            recommendations.append("Consider preparing handoff documentation")
        
        if token_pct > 70:
            recommendations.append("High token usage - use /compact if possible")
        
        if self.chat_state["depth"] > 15:
            recommendations.append("Deep conversation - consider phase transition")
        
        if len(self.chat_state["errors"]) > 3:
            recommendations.append("Multiple errors - review and address issues")
        
        return recommendations
    
    def save_chat_state(self):
        """Save current chat state"""
        self.current_chat_file.write_text(json.dumps(self.chat_state, indent=2))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get chat summary"""
        return {
            "chat_id": self.chat_state["chat_id"],
            "phase": self.chat_state["phase"],
            "depth": self.chat_state["depth"],
            "duration_minutes": self.get_chat_duration_minutes(),
            "token_usage": f"{(self.chat_state['tokens']['current'] / self.chat_state['tokens']['limit'] * 100):.1f}%",
            "files_modified": len(self.chat_state["files_modified"]),
            "commands_executed": len(self.chat_state["commands_executed"]),
            "active_agents": self.chat_state["active_agents"],
            "health": self.get_chat_health()["status"]
        }

def main():
    """Main entry point for chat management"""
    manager = ChatManager()
    
    if len(sys.argv) < 2:
        # Default: show status
        summary = manager.get_summary()
        print(json.dumps(summary, indent=2))
        return
    
    command = sys.argv[1]
    
    if command == "status":
        print(json.dumps(manager.get_summary(), indent=2))
    
    elif command == "health":
        print(json.dumps(manager.get_chat_health(), indent=2))
    
    elif command == "handoff":
        suggestion = manager.create_handoff_suggestion("manual")
        print(f"Handoff documentation generated: {manager.chat_dir}/handoff_{manager.chat_state['chat_id']}.md")
    
    elif command == "archive":
        result = manager.archive_chat()
        print(f"Chat archived: {result['chat_id']}")
    
    elif command == "add-message" and len(sys.argv) > 3:
        role = sys.argv[2]
        content = " ".join(sys.argv[3:])
        result = manager.add_message(role, content)
        if result:
            print("Handoff suggested:", result["recommendation"])
    
    elif command == "transition" and len(sys.argv) > 2:
        new_phase = sys.argv[2]
        result = manager.transition_phase(new_phase)
        if result:
            print("Handoff suggested at transition point")
    
    else:
        print("Usage: chat_manager.py [status|health|handoff|archive|add-message <role> <content>|transition <phase>]")

if __name__ == "__main__":
    main()