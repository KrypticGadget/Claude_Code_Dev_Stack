#!/usr/bin/env python3
"""Session context restoration hook with v2.1 enhancements"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
CLAUDE_DIR = Path(".claude")
STATE_DIR = CLAUDE_DIR / "state"
OUTPUT_FILE = Path("SESSION_CONTEXT.md")

def load_session_state():
    """Load all session state components"""
    context_parts = []
    
    # Header with timestamp
    context_parts.append(f"# Session Context Restored\n")
    context_parts.append(f"*Restored at: {datetime.now().isoformat()}*\n")
    
    # 1. Meta-prompting state
    meta_state_file = STATE_DIR / "meta_prompt_state.json"
    if meta_state_file.exists():
        with open(meta_state_file) as f:
            meta_state = json.load(f)
            context_parts.append("## Meta-Prompting State")
            context_parts.append("```json")
            context_parts.append(json.dumps(meta_state, indent=2))
            context_parts.append("```\n")
    
    # 2. Agent assignments with @agent- routing
    agent_state_file = STATE_DIR / "agent_state.md"
    if agent_state_file.exists():
        with open(agent_state_file) as f:
            context_parts.append("## Active Agent Assignments")
            context_parts.append(f.read())
            context_parts.append("")
    
    # 3. Agent routing history
    routing_file = STATE_DIR / "agent_routing.json"
    if routing_file.exists():
        with open(routing_file) as f:
            routing = json.load(f)
            if routing:
                context_parts.append("## Recent @agent- Routing")
                for route in routing[-10:]:  # Last 10
                    context_parts.append(f"- {route['timestamp']}: @agent-{route['agent']}[{route['model']}]")
                context_parts.append("")
    
    # 4. Model usage tracking
    usage_file = STATE_DIR / "model_usage.json"
    if usage_file.exists():
        with open(usage_file) as f:
            usage = json.load(f)
            context_parts.append("## Model Usage & Cost Tracking")
            context_parts.append(f"- Today's Savings: ${usage.get('savings', 0):.2f}")
            context_parts.append(f"- Total Cost: ${usage.get('total_cost', 0):.2f}")
            context_parts.append("")
    
    # 5. Planning phase
    planning_file = Path("PLANNING_PHASE.md")
    if planning_file.exists():
        with open(planning_file) as f:
            context_parts.append("## Current Planning Phase")
            context_parts.append(f.read())
            context_parts.append("")
    
    # 6. Recent decisions
    decisions_file = STATE_DIR / "recent_decisions.json"
    if decisions_file.exists():
        with open(decisions_file) as f:
            decisions = json.load(f)
            context_parts.append("## Recent Decisions")
            for decision in decisions[-5:]:  # Last 5 decisions
                context_parts.append(f"- {decision['timestamp']}: {decision['description']}")
            context_parts.append("")
    
    # 7. Microcompact state
    microcompact_file = STATE_DIR / "microcompact_state.json"
    if microcompact_file.exists():
        with open(microcompact_file) as f:
            mc_state = json.load(f)
            context_parts.append("## Microcompact State")
            context_parts.append(f"- Last trigger: {mc_state.get('timestamp', 'Never')}")
            context_parts.append(f"- Active agents preserved: {', '.join(mc_state.get('active_agents', []))}")
            context_parts.append("")
    
    # Write context file
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(context_parts))
    
    print(f"[OK] Session context restored to {OUTPUT_FILE}")
    print(f"[INFO] Model tracking enabled for cost optimization")
    print(f"[INFO] @agent- deterministic routing active")

if __name__ == "__main__":
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        hook_event = input_data.get("hook_event_name", "")
        source = input_data.get("source", "startup")
        
        print(f"[SessionStart] Loading session (source: {source})...")
        
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        load_session_state()
        
        # Output additional context for Claude
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Session context restored from {OUTPUT_FILE}"
            }
        }
        print(json.dumps(output))
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Session restoration failed: {e}", file=sys.stderr)
        sys.exit(1)