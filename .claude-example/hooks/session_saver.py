#!/usr/bin/env python3
"""Session state persistence hook with microcompact awareness"""
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path(".claude")
STATE_DIR = CLAUDE_DIR / "state"

def detect_microcompact_trigger():
    """Check if we're approaching microcompact threshold"""
    # This is a simplified check - actual implementation would
    # monitor token usage or context size
    context_file = Path("SESSION_CONTEXT.md")
    if context_file.exists():
        size_kb = context_file.stat().st_size / 1024
        return size_kb > 50  # Trigger if context > 50KB
    return False

def save_pre_microcompact_state():
    """Save critical state before microcompact"""
    microcompact_state = {
        "timestamp": datetime.now().isoformat(),
        "critical_context": [],
        "active_agents": [],
        "recent_decisions": []
    }
    
    # Extract critical information
    if (STATE_DIR / "agent_routing.json").exists():
        with open(STATE_DIR / "agent_routing.json") as f:
            routing = json.load(f)
            microcompact_state["active_agents"] = [
                f"@agent-{r['agent']}" for r in routing[-5:]
            ]
    
    # Save microcompact state
    with open(STATE_DIR / "microcompact_state.json", 'w') as f:
        json.dump(microcompact_state, f, indent=2)
    
    print("💾 Pre-microcompact state saved")

def extract_agent_mentions(content):
    """Extract @agent- references from content"""
    agent_pattern = r'@agent-([a-z-]+)(?:\[(opus|haiku)\])?'
    mentions = []
    for match in re.finditer(agent_pattern, content):
        mentions.append({
            "agent": match.group(1),
            "model": match.group(2) or "default"
        })
    return mentions

def save_session_state():
    """Persist all session state components"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check for impending microcompact
    if detect_microcompact_trigger():
        save_pre_microcompact_state()
    
    # 1. Save timestamp
    session_meta = {
        "last_saved": datetime.now().isoformat(),
        "session_id": os.getenv("SESSION_ID", "default"),
        "v2_1_features": {
            "deterministic_routing": True,
            "model_selection": True,
            "microcompact_aware": True,
            "pdf_support": True
        }
    }
    
    # 2. Scan for agent activities
    agent_activities = []
    for file in Path(".").rglob("*.md"):
        try:
            if file.stat().st_mtime > (datetime.now().timestamp() - 3600):  # Last hour
                with open(file) as f:
                    content = f.read()
                    mentions = extract_agent_mentions(content)
                    agent_activities.extend(mentions)
        except:
            pass  # Skip files we can't read
    
    # 3. Update agent state
    if agent_activities:
        agent_state = f"# Active Agents\n\n"
        agent_state += f"*As of {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        seen = set()
        for activity in agent_activities:
            agent_key = f"{activity['agent']}[{activity['model']}]"
            if agent_key not in seen:
                agent_state += f"- @agent-{activity['agent']}[{activity['model']}]\n"
                seen.add(agent_key)
        
        with open(STATE_DIR / "agent_state.md", 'w') as f:
            f.write(agent_state)
    
    # 4. Save session metadata
    with open(STATE_DIR / "session_meta.json", 'w') as f:
        json.dump(session_meta, f, indent=2)
    
    # 5. Check model usage
    usage_file = STATE_DIR / "model_usage.json"
    if usage_file.exists():
        with open(usage_file) as f:
            usage = json.load(f)
            if usage.get("savings", 0) > 0:
                print(f"💰 Cost savings today: ${usage['savings']:.2f}")
    
    print("✅ Session state saved successfully")
    print("🎯 @agent- routing preserved")
    print("📊 Model usage tracked")

if __name__ == "__main__":
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        transcript_path = input_data.get("transcript_path", "")
        stop_hook_active = input_data.get("stop_hook_active", False)
        
        # Don't save if already in a stop hook loop
        if stop_hook_active:
            sys.exit(0)
        
        print("[Stop] Saving session state...")
        
        # Set session ID in environment for save_session_state
        os.environ["SESSION_ID"] = session_id
        
        save_session_state()
        
        # Save session data for next session
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "transcript": transcript_path,
            "status": "completed"
        }
        
        session_file = STATE_DIR / "session.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"Session saved: {session_id}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Session save failed: {e}", file=sys.stderr)
        sys.exit(1)