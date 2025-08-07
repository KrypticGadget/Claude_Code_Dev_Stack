#!/usr/bin/env python3
"""Track model usage for cost optimization"""
import json
from pathlib import Path
from datetime import datetime, timedelta

STATE_DIR = Path(".claude/state")
COSTS = {
    "opus": 0.015,      # Hypothetical cost per call
    "haiku": 0.002,     # Much cheaper
    "default": 0.008    # Mid-range
}

def track_model_usage(agent, model="default"):
    """Track model usage and calculate costs"""
    usage_file = STATE_DIR / "model_usage.json"
    
    usage_data = {
        "daily": {},
        "total_cost": 0.0,
        "savings": 0.0
    }
    
    if usage_file.exists():
        with open(usage_file) as f:
            usage_data = json.load(f)
    
    # Track today's usage
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in usage_data["daily"]:
        usage_data["daily"][today] = {"opus": 0, "haiku": 0, "default": 0}
    
    usage_data["daily"][today][model] += 1
    
    # Calculate costs
    daily_cost = sum(
        COSTS[m] * count 
        for m, count in usage_data["daily"][today].items()
    )
    
    # Calculate savings (vs all Opus)
    opus_cost = sum(usage_data["daily"][today].values()) * COSTS["opus"]
    actual_cost = daily_cost
    usage_data["savings"] = opus_cost - actual_cost
    
    # Update total cost
    usage_data["total_cost"] = sum(
        sum(COSTS[m] * count for m, count in day_data.items())
        for day_data in usage_data["daily"].values()
    )
    
    # Save updated data
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(usage_file, 'w') as f:
        json.dump(usage_data, f, indent=2)
    
    # Create cost report if significant savings
    if usage_data["savings"] > 10:
        with open("COST_SAVINGS.md", 'w') as f:
            f.write(f"""# [COST SAVINGS] Model Usage Cost Savings

**Today's Savings**: ${usage_data['savings']:.2f}
**Total Cost**: ${usage_data['total_cost']:.2f}

## Today's Usage
- Opus 4: {usage_data['daily'][today]['opus']} calls
- Haiku 3.5: {usage_data['daily'][today]['haiku']} calls
- Default: {usage_data['daily'][today]['default']} calls

*Using Haiku for simple tasks saved ${usage_data['savings']:.2f} today!*
""")

if __name__ == "__main__":
    import sys
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        
        print("[SubagentStop] Recording agent metrics...")
        
        # Track subagent usage (simplified - you'd parse more details in production)
        metrics_file = STATE_DIR / "agent_metrics.json"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        metrics = {}
        if metrics_file.exists():
            with open(metrics_file) as f:
                metrics = json.load(f)
        
        # Update metrics
        timestamp = datetime.now().isoformat()
        if session_id not in metrics:
            metrics[session_id] = []
        
        metrics[session_id].append({
            "timestamp": timestamp,
            "event": "subagent_stop"
        })
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Track model usage for cost optimization
        # In production, you'd extract the actual agent and model from input_data
        track_model_usage("default-agent", "default")
        
        sys.exit(0)
    except Exception as e:
        print(f"Error in model tracker: {e}", file=sys.stderr)
        sys.exit(1)