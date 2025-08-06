#!/usr/bin/env python3
"""Validate and track MCP tool usage"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Approved MCP tools and their limits
MCP_CONFIG = {
    "tier1": ["playwright", "obsidian", "brave-search"],
    "tier2_database": ["mongodb", "postgresql", "supabase"],
    "tier2_deploy": ["gcp", "vercel", "netlify", "aws"],
    "max_tools": 5,
    "usage_tracking": True
}

def load_active_mcps():
    """Load currently active MCPs"""
    mcp_file = Path(".claude/state/active_mcps.json")
    if mcp_file.exists():
        with open(mcp_file) as f:
            return json.load(f)
    return {"tools": [], "count": 0}

def validate_mcp_usage(mcp_tool):
    """Validate MCP tool usage"""
    active = load_active_mcps()
    
    # Check if already at limit
    if active["count"] >= MCP_CONFIG["max_tools"]:
        print(f"⚠️  MCP limit reached ({MCP_CONFIG['max_tools']} tools)")
        return False
    
    # Check if tool is approved
    all_approved = (MCP_CONFIG["tier1"] + 
                   MCP_CONFIG["tier2_database"] + 
                   MCP_CONFIG["tier2_deploy"])
    
    if mcp_tool not in all_approved:
        print(f"❌ MCP '{mcp_tool}' not in approved list")
        return False
    
    # Track usage
    if MCP_CONFIG["usage_tracking"]:
        usage_file = Path(".claude/state/mcp_usage.json")
        usage_data = []
        if usage_file.exists():
            with open(usage_file) as f:
                usage_data = json.load(f)
        
        usage_data.append({
            "tool": mcp_tool,
            "timestamp": datetime.now().isoformat(),
            "action": "invoked"
        })
        
        usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(usage_file, 'w') as f:
            json.dump(usage_data[-100:], f, indent=2)  # Keep last 100
    
    return True

if __name__ == "__main__":
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        
        # Check if this is an MCP tool
        if tool_name.startswith("mcp__"):
            mcp_tool = tool_name.replace("mcp__", "")
            
            if validate_mcp_usage(mcp_tool):
                print(f"[PreToolUse] MCP '{mcp_tool}' validated")
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": f"MCP tool '{mcp_tool}' is approved"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
            else:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"MCP tool '{mcp_tool}' not approved or limit reached"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
        
        # Not an MCP tool, allow it
        sys.exit(0)
    except Exception as e:
        print(f"Error in MCP gateway: {e}", file=sys.stderr)
        sys.exit(1)