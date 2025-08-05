# 🔧 Hooks Implementation Guide - Claude Code Dev Stack v2.1

## Overview
Hooks are the **execution layer** that transforms intelligent agent decisions into guaranteed implementation. Version 2.1 adds support for @-mention routing, model selection, and microcompact awareness.

---

## 🎯 Core Concept

```
Without Hooks: Agent Decision → Hope it gets implemented → Manual verification
With Hooks:    @agent[model] → Hook Routes → Executes → Guaranteed + Verified
```

### 🆕 Version 2.1 Enhancements
- **@-mention Parser**: Routes deterministic agent calls
- **Model Selection**: Tracks Opus vs Haiku usage for cost optimization
- **Microcompact Awareness**: Preserves state before automatic context clearing
- **PDF Integration**: Logs PDF reading for agent context

---

## 📁 Enhanced Directory Structure

```
.claude/
├── hooks/
│   ├── session_loader.py          # Restores context on startup
│   ├── session_saver.py           # Persists context (microcompact-aware)
│   ├── quality_gate.py            # Enforces standards
│   ├── planning_trigger.py        # Detects planning needs
│   ├── agent_orchestrator.py      # Routes to agents
│   ├── agent_mention_parser.py    # 🆕 Parses @-mentions
│   ├── model_tracker.py           # 🆕 Tracks model usage/costs
│   ├── mcp_gateway.py             # Validates MCP usage
│   └── mcp_pipeline.py            # Manages MCP data
├── config/
│   ├── coding_standards.json      # Your standards
│   ├── agent_routing.json         # Agent selection rules
│   ├── agent_models.json          # 🆕 Model preferences
│   └── mcp_config.json            # MCP settings
└── state/
    ├── session_state.json         # Current session
    ├── agent_state.md             # Agent assignments
    ├── planning_phase.md          # Planning context
    ├── meta_prompt_state.json     # Meta-prompting state
    ├── microcompact_state.json    # 🆕 Microcompact tracking
    └── model_usage.json           # 🆕 Cost tracking
```

---

## 🆕 New Hook Implementations (v2.1)

### Agent Mention Parser
**File**: `.claude/hooks/agent_mention_parser.py`

```python
#!/usr/bin/env python3
"""Parse and track @-mention agent invocations"""
import json
import re
from pathlib import Path
from datetime import datetime

AGENT_PATTERN = r'@([a-z-]+)(?:\[(opus|haiku)\])?'
STATE_DIR = Path(".claude/state")

def parse_agent_mentions(content):
    """Extract @-mentions with optional model specifications"""
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
    """Update agent routing based on @-mentions"""
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
    if len(sys.argv) > 1:
        content = sys.argv[1]
        mentions = parse_agent_mentions(content)
        if mentions:
            update_agent_routing(mentions)
            print(f"📍 Routed to: {', '.join(m['agent'] for m in mentions)}")
```

### Model Usage Tracker
**File**: `.claude/hooks/model_tracker.py`

```python
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
            f.write(f"""# 💰 Model Usage Cost Savings

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
    if len(sys.argv) > 2:
        agent = sys.argv[1]
        model = sys.argv[2]
        track_model_usage(agent, model)
```

### Enhanced Session Saver (Microcompact-Aware)
**File**: `.claude/hooks/session_saver.py` (Updated)

```python
#!/usr/bin/env python3
"""Session state persistence hook with microcompact awareness"""
import json
import os
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
                r["agent"] for r in routing[-5:]
            ]
    
    # Save microcompact state
    with open(STATE_DIR / "microcompact_state.json", 'w') as f:
        json.dump(microcompact_state, f, indent=2)
    
    print("💾 Pre-microcompact state saved")

def save_session_state():
    """Persist all session state components"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check for impending microcompact
    if detect_microcompact_trigger():
        save_pre_microcompact_state()
    
    # Continue with normal session save...
    # [Previous session_saver.py code continues here]
```

### 1.1 Session Loader
**File**: `.claude/hooks/session_loader.py`

```python
#!/usr/bin/env python3
"""Session context restoration hook"""
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
    
    # 2. Agent assignments
    agent_state_file = STATE_DIR / "agent_state.md"
    if agent_state_file.exists():
        with open(agent_state_file) as f:
            context_parts.append("## Active Agent Assignments")
            context_parts.append(f.read())
            context_parts.append("")
    
    # 3. Planning phase
    planning_file = Path("PLANNING_PHASE.md")
    if planning_file.exists():
        with open(planning_file) as f:
            context_parts.append("## Current Planning Phase")
            context_parts.append(f.read())
            context_parts.append("")
    
    # 4. Recent decisions
    decisions_file = STATE_DIR / "recent_decisions.json"
    if decisions_file.exists():
        with open(decisions_file) as f:
            decisions = json.load(f)
            context_parts.append("## Recent Decisions")
            for decision in decisions[-5:]:  # Last 5 decisions
                context_parts.append(f"- {decision['timestamp']}: {decision['description']}")
            context_parts.append("")
    
    # Write context file
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(context_parts))
    
    print(f"✅ Session context restored to {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        load_session_state()
    except Exception as e:
        print(f"❌ Session restoration failed: {e}")
        sys.exit(1)
```

### 1.2 Session Saver
**File**: `.claude/hooks/session_saver.py`

```python
#!/usr/bin/env python3
"""Session state persistence hook"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path(".claude")
STATE_DIR = CLAUDE_DIR / "state"

def extract_agent_mentions(content):
    """Extract agent references from content"""
    agent_pattern = r'(?:agent|specialist|architect|engineer|analyst):\s*(\w+)'
    return re.findall(agent_pattern, content, re.IGNORECASE)

def save_session_state():
    """Persist all session state components"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Save timestamp
    session_meta = {
        "last_saved": datetime.now().isoformat(),
        "session_id": os.getenv("SESSION_ID", "default")
    }
    
    # 2. Scan for agent activities
    agent_activities = []
    for file in Path(".").rglob("*.md"):
        if file.stat().st_mtime > (datetime.now().timestamp() - 3600):  # Last hour
            with open(file) as f:
                content = f.read()
                agents = extract_agent_mentions(content)
                if agents:
                    agent_activities.extend(agents)
    
    # 3. Update agent state
    if agent_activities:
        agent_state = f"# Active Agents\n\n"
        agent_state += f"*As of {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        for agent in set(agent_activities):
            agent_state += f"- {agent}\n"
        
        with open(STATE_DIR / "agent_state.md", 'w') as f:
            f.write(agent_state)
    
    # 4. Save session metadata
    with open(STATE_DIR / "session_meta.json", 'w') as f:
        json.dump(session_meta, f, indent=2)
    
    print("✅ Session state saved successfully")

if __name__ == "__main__":
    try:
        save_session_state()
    except Exception as e:
        print(f"❌ Session save failed: {e}")
```

### 1.3 Quality Gate
**File**: `.claude/hooks/quality_gate.py`

```python
#!/usr/bin/env python3
"""Code quality enforcement hook"""
import json
import sys
import re
from pathlib import Path

CLAUDE_DIR = Path(".claude")
CONFIG_FILE = CLAUDE_DIR / "config" / "coding_standards.json"

def load_standards():
    """Load coding standards configuration"""
    if not CONFIG_FILE.exists():
        return {
            "naming": {
                "functions": "snake_case",
                "classes": "PascalCase",
                "constants": "UPPER_SNAKE_CASE"
            },
            "forbidden_patterns": [
                r"console\.log\(",  # No console.log in production
                r"TODO(?!:)",       # TODOs must have descriptions
                r"password\s*=\s*[\"']",  # No hardcoded passwords
            ],
            "required_patterns": {
                "functions": r"def .+\(.*\):\s*\n\s*\"\"\"",  # Docstrings required
            }
        }
    
    with open(CONFIG_FILE) as f:
        return json.load(f)

def check_file_quality(file_path, content):
    """Check file against quality standards"""
    issues = []
    standards = load_standards()
    
    # Check naming conventions
    if file_path.endswith('.py'):
        # Function names
        functions = re.findall(r'def (\w+)\(', content)
        for func in functions:
            if standards["naming"]["functions"] == "snake_case":
                if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                    issues.append(f"Function '{func}' doesn't follow snake_case")
        
        # Class names  
        classes = re.findall(r'class (\w+)[:\(]', content)
        for cls in classes:
            if standards["naming"]["classes"] == "PascalCase":
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls):
                    issues.append(f"Class '{cls}' doesn't follow PascalCase")
    
    # Check forbidden patterns
    for i, pattern in enumerate(standards.get("forbidden_patterns", [])):
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Forbidden pattern found: {pattern}")
    
    # Check required patterns
    for pattern_type, pattern in standards.get("required_patterns", {}).items():
        if pattern_type == "functions" and file_path.endswith('.py'):
            functions = re.findall(r'def \w+\(.*\):', content)
            for func in functions:
                func_with_next = content[content.find(func):content.find(func)+200]
                if not re.search(pattern, func_with_next):
                    issues.append(f"Function missing required docstring")
    
    return issues

def main():
    """Main quality gate execution"""
    # Get file being edited from environment or args
    file_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("EDITING_FILE", "")
    
    if not file_path or not Path(file_path).exists():
        print("⚠️  No file to check")
        return 0
    
    with open(file_path) as f:
        content = f.read()
    
    issues = check_file_quality(file_path, content)
    
    if issues:
        print(f"❌ Quality gate failed for {file_path}:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Create quality report
        report = {
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "issues": issues
        }
        
        report_file = CLAUDE_DIR / "state" / "quality_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return 1
    else:
        print(f"✅ Quality gate passed for {file_path}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📋 Hook Configuration

### settings.json Configuration
**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/session_loader.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command", 
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/session_saver.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/quality_gate.py ${EDITING_FILE}"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write.*\\.(md|txt|json)$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/planning_trigger.py ${EDITED_FILE}"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/agent_orchestrator.py '${USER_PROMPT}'"
          }
        ]
      }
    ]
  }
}
```

---

## 🚀 Phase 2: Agent Integration Hooks

### 2.1 Planning Trigger
**File**: `.claude/hooks/planning_trigger.py`

```python
#!/usr/bin/env python3
"""Detect when planning phase should be triggered"""
import json
import sys
from pathlib import Path
from datetime import datetime

TRIGGER_FILES = [
    "requirements.txt",
    "package.json", 
    "REQUIREMENTS.md",
    "FEATURE_REQUEST.md",
    "ARCHITECTURE.md",
    "USER_STORIES.md"
]

def should_trigger_planning(file_path):
    """Check if file change should trigger planning"""
    file_name = Path(file_path).name
    return any(trigger in file_name.upper() for trigger in 
               [t.upper() for t in TRIGGER_FILES])

def create_planning_trigger(file_path):
    """Create planning trigger notification"""
    trigger_data = {
        "trigger_type": "file_change",
        "file": file_path,
        "timestamp": datetime.now().isoformat(),
        "suggested_agents": [
            "requirements-analyst",
            "system-architect", 
            "technical-feasibility-analyst"
        ],
        "action": "Review changes and update project plan"
    }
    
    trigger_file = Path(".claude/state/PLANNING_TRIGGER.json")
    trigger_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(trigger_file, 'w') as f:
        json.dump(trigger_data, f, indent=2)
    
    # Also create visible notification
    with open("PLANNING_NEEDED.md", 'w') as f:
        f.write(f"""# Planning Phase Triggered

**Trigger**: {file_path} was modified
**Time**: {trigger_data['timestamp']}

## Suggested Actions

1. Run `/technical-feasibility` to assess changes
2. Update `/project-plan` if needed
3. Review with agents: {', '.join(trigger_data['suggested_agents'])}

This file will be automatically removed once planning is complete.
""")
    
    print(f"🎯 Planning phase triggered by {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if should_trigger_planning(file_path):
            create_planning_trigger(file_path)
```

### 2.2 Agent Orchestrator
**File**: `.claude/hooks/agent_orchestrator.py`

```python
#!/usr/bin/env python3
"""Route prompts to appropriate agents based on content"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

AGENT_KEYWORDS = {
    "system-architect": ["architecture", "system design", "scalability", "infrastructure"],
    "backend-engineer": ["api", "backend", "server", "endpoint", "database connection"],
    "frontend-architect": ["ui", "frontend", "react", "vue", "user interface"],
    "database-architect": ["schema", "database", "table", "query", "index"],
    "security-architect": ["security", "authentication", "authorization", "encryption"],
    "devops-specialist": ["deploy", "ci/cd", "pipeline", "docker", "kubernetes"],
    "testing-engineer": ["test", "qa", "quality", "coverage", "validation"],
    "business-analyst": ["roi", "business case", "market", "competitor"]
}

def analyze_prompt(prompt):
    """Analyze prompt to determine relevant agents"""
    prompt_lower = prompt.lower()
    relevant_agents = []
    confidence_scores = {}
    
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in prompt_lower)
        if score > 0:
            relevant_agents.append(agent)
            confidence_scores[agent] = score
    
    # Sort by confidence
    relevant_agents.sort(key=lambda a: confidence_scores[a], reverse=True)
    
    return relevant_agents[:3]  # Top 3 agents

def create_routing_suggestion(prompt, agents):
    """Create agent routing suggestion"""
    routing_data = {
        "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "timestamp": datetime.now().isoformat(),
        "suggested_agents": agents,
        "routing_confidence": "high" if len(agents) > 0 else "low"
    }
    
    # Save routing data
    routing_file = Path(".claude/state/agent_routing.json")
    routing_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing routings
    existing = []
    if routing_file.exists():
        with open(routing_file) as f:
            existing = json.load(f)
    
    # Add new routing (keep last 10)
    existing.append(routing_data)
    existing = existing[-10:]
    
    with open(routing_file, 'w') as f:
        json.dump(existing, f, indent=2)
    
    # Create visible suggestion if agents found
    if agents:
        with open("AGENT_SUGGESTION.md", 'w') as f:
            f.write(f"""# Agent Routing Suggestion

## Your Request
{prompt[:500]}...

## Suggested Agents
{chr(10).join(f"- **{agent}** - Primary match" if i == 0 else f"- {agent}" 
              for i, agent in enumerate(agents))}

## Quick Commands
- Use `--agent {agents[0]}` to target the primary agent
- Use `/new-project` to engage full orchestration

*This suggestion is based on keyword analysis*
""")
        
        print(f"🤖 Suggested agents: {', '.join(agents)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        agents = analyze_prompt(prompt)
        create_routing_suggestion(prompt, agents)
```

---

## 🚀 Phase 3: MCP Integration Hooks

### 3.1 MCP Gateway
**File**: `.claude/hooks/mcp_gateway.py`

```python
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
    if len(sys.argv) > 1:
        mcp_tool = sys.argv[1].replace("mcp__", "")
        if validate_mcp_usage(mcp_tool):
            print(f"✅ MCP '{mcp_tool}' validated")
            sys.exit(0)
        else:
            sys.exit(1)
```

---

## 🚀 Installation Scripts

### Windows PowerShell Installer
**File**: `install-hooks.ps1`

```powershell
# Claude Code Hooks Installation Script
Write-Host "🔧 Installing Claude Code Hooks System..." -ForegroundColor Cyan

# Create directory structure
$claudeDir = ".claude"
$directories = @(
    "$claudeDir/hooks",
    "$claudeDir/config", 
    "$claudeDir/state"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Download hook files from repository
$hookFiles = @{
    "session_loader.py" = "$claudeDir/hooks/session_loader.py"
    "session_saver.py" = "$claudeDir/hooks/session_saver.py"
    "quality_gate.py" = "$claudeDir/hooks/quality_gate.py"
    "planning_trigger.py" = "$claudeDir/hooks/planning_trigger.py"
    "agent_orchestrator.py" = "$claudeDir/hooks/agent_orchestrator.py"
    "mcp_gateway.py" = "$claudeDir/hooks/mcp_gateway.py"
}

$repoBase = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

foreach ($file in $hookFiles.GetEnumerator()) {
    $url = "$repoBase/hooks/$($file.Key)"
    $dest = $file.Value
    
    Write-Host "Downloading $($file.Key)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}

# Create default configurations
$codingStandards = @{
    naming = @{
        functions = "snake_case"
        classes = "PascalCase"
        constants = "UPPER_SNAKE_CASE"
    }
    forbidden_patterns = @(
        "console\.log\("
        "TODO(?!:)"
        "password\s*=\s*[""']"
    )
}

$codingStandards | ConvertTo-Json -Depth 3 | Out-File "$claudeDir/config/coding_standards.json"

# Create settings.json
$settings = @{
    hooks = @{
        SessionStart = @(@{
            hooks = @(@{
                type = "command"
                command = "python3 `$CLAUDE_PROJECT_DIR/.claude/hooks/session_loader.py"
            })
        })
        Stop = @(@{
            hooks = @(@{
                type = "command"
                command = "python3 `$CLAUDE_PROJECT_DIR/.claude/hooks/session_saver.py"
            })
        })
    }
}

$settings | ConvertTo-Json -Depth 5 | Out-File "$claudeDir/settings.json"

Write-Host "✅ Hooks installation complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy .claude/settings.json to your Claude Code settings" -ForegroundColor White
Write-Host "  2. Restart Claude Code to activate hooks" -ForegroundColor White
Write-Host "  3. Hooks will now manage your session state automatically" -ForegroundColor White
```

---

## 🎯 Testing & Validation

### Test Session Continuity
```bash
# Start Claude Code
# Create some agent state
echo "# Test Agent State" > .claude/state/agent_state.md
echo "- system-architect: Active" >> .claude/state/agent_state.md

# Exit Claude Code
# Restart Claude Code
# Check if SESSION_CONTEXT.md was created with your state
```

### Test Quality Gates
```python
# Create a file with bad naming
def BadlyNamedFunction():  # Should fail PascalCase check
    pass

# Try to save - quality gate should report issue
```

### Test Planning Triggers
```bash
# Modify requirements.txt
echo "new-package==1.0" >> requirements.txt
# Check if PLANNING_NEEDED.md appears
```

---

## 📊 Success Metrics

1. **Zero Context Loss**: Sessions continue seamlessly
2. **Automated Quality**: Standards enforced without manual review
3. **Smart Routing**: Prompts go to right agents automatically
4. **MCP Control**: Never exceed 5 tools
5. **Planning Triggers**: Requirements changes detected

---

## 🚀 Next Steps

1. Install Phase 1 hooks first (session + quality)
2. Test thoroughly before adding more hooks
3. Customize standards to your preferences
4. Add Phase 2/3 hooks as needed
5. Monitor `.claude/state/` for insights

Remember: **Hooks make your agents' intelligence executable!**