#!/usr/bin/env python3
"""Parse and track @agent- mention invocations for deterministic routing"""
import json
import re
from pathlib import Path
from datetime import datetime

# Updated pattern for @agent- mentions
AGENT_PATTERN = r'@agent-([a-z-]+)(?:\[(opus|haiku)\])?'
STATE_DIR = Path(".claude/state")

def parse_agent_mentions(content):
    """Extract @agent- mentions with optional model specifications"""
    mentions = []
    for match in re.finditer(AGENT_PATTERN, content):
        agent_name = match.group(1)
        model = match.group(2) or "default"
        mentions.append({
            "agent": agent_name,
            "model": model,
            "timestamp": datetime.now().isoformat()
        })
    return mentions

def update_agent_routing(mentions):
    """Update agent routing based on @agent- mentions"""
    routing_file = STATE_DIR / "agent_routing.json"
    
    current_routing = []
    if routing_file.exists():
        with open(routing_file) as f:
            current_routing = json.load(f)
    
    # Add new mentions
    for mention in mentions:
        current_routing.append(mention)
    
    # Keep last 50 mentions for analysis
    current_routing = current_routing[-50:]
    
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(routing_file, 'w') as f:
        json.dump(current_routing, f, indent=2)
    
    # Update active agents file
    active_agents = {}
    for mention in mentions:
        active_agents[mention["agent"]] = mention["model"]
    
    with open(STATE_DIR / "active_agents.json", 'w') as f:
        json.dump(active_agents, f, indent=2)

if __name__ == "__main__":
    import sys
    try:
        # Read input from Claude Code via stdin or use test data
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
            prompt = input_data.get("prompt", "")
        else:
            # Test mode - use sample data
            prompt = "Test @agent-testing and @agent-master-orchestrator functionality"
            print("[INFO] Running in test mode", file=sys.stderr)
        
        mentions = parse_agent_mentions(prompt)
        if mentions:
            update_agent_routing(mentions)
            print(f"[UserPromptSubmit] Detected agents: {', '.join(m['agent'] for m in mentions)}", file=sys.stderr)
            
            # Add context about detected agents
            context = f"Routing to agents: {', '.join(m['agent'] for m in mentions)}"
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context
                }
            }
            print(json.dumps(output))
        else:
            print("[INFO] No agent mentions detected", file=sys.stderr)
        
        sys.exit(0)
    except Exception as e:
        print(f"Error in agent parser: {e}", file=sys.stderr)
        sys.exit(1)