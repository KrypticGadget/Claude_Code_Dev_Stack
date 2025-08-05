# 🔧 Hooks Implementation Guide - Claude Code Dev Stack v2.1

## Overview
Hooks are the **execution layer** that transforms intelligent agent decisions into guaranteed implementation. Version 2.1 adds support for @agent- mention routing, model selection, and microcompact awareness.

---

## 🎯 Core Concept

```
Without Hooks: Agent Decision → Hope it gets implemented → Manual verification
With Hooks:    @agent-[model] → Hook Routes → Executes → Guaranteed + Verified
```

### 🆕 Version 2.1 Enhancements
- **@agent- mention Parser**: Routes deterministic agent calls
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
│   ├── agent_mention_parser.py    # 🆕 Parses @agent- mentions
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

**Purpose**: Parse and track @agent- mention invocations for deterministic routing

**Key Features**:
- Extracts @agent- mentions with optional model specifications
- Updates agent routing based on mentions
- Maintains history of agent invocations
- Supports model override syntax: `@agent-name[opus]` or `@agent-name[haiku]`

**Usage Pattern**:
```python
# Parses: @agent-backend-services[haiku] create API
# Result: Routes to backend-services agent with Haiku model
```

### Model Usage Tracker
**File**: `.claude/hooks/model_tracker.py`

**Purpose**: Track model usage for cost optimization

**Key Features**:
- Tracks daily usage by model type
- Calculates cost savings vs all-Opus usage
- Generates cost reports when savings exceed threshold
- Maintains historical usage data

**Cost Tracking**:
- Opus: $0.015 per call (hypothetical)
- Haiku: $0.002 per call
- Default: $0.008 per call

### Enhanced Session Saver (Microcompact-Aware)
**File**: `.claude/hooks/session_saver.py` (Updated)

**New Features**:
- Detects approaching microcompact threshold
- Saves critical state before context clearing
- Preserves active agents and recent decisions
- Tracks v2.1 feature usage

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
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/agent_mention_parser.py '${USER_PROMPT}'"
          },
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

## 🚀 Phase 1: Core Hooks

### 1.1 Session Loader
**Purpose**: Restore all context when Claude Code starts

**Restores**:
- Meta-prompting state
- Active agent assignments with @agent- mentions
- Model usage statistics
- Recent routing history
- Planning phase context
- Microcompact state

**Output**: Creates SESSION_CONTEXT.md with full context

### 1.2 Session Saver
**Purpose**: Persist state when Claude Code stops

**Saves**:
- Current timestamp and session ID
- Active @agent- mentions found in recent files
- Model usage for cost tracking
- Pre-microcompact state if threshold approached
- v2.1 feature flags

### 1.3 Quality Gate
**Purpose**: Enforce coding standards automatically

**Checks**:
- Naming conventions (snake_case, PascalCase, etc.)
- Forbidden patterns (hardcoded passwords, console.log)
- Required patterns (docstrings for functions)
- File-specific requirements

**Action**: Blocks file save if standards violated

---

## 🚀 Phase 2: Agent Integration Hooks

### 2.1 Planning Trigger
**Purpose**: Detect when planning phase should be triggered

**Triggers On**:
- requirements.txt changes
- REQUIREMENTS.md modifications
- ARCHITECTURE.md updates
- New feature requests

**Creates**: PLANNING_NEEDED.md with suggested actions

### 2.2 Agent Orchestrator
**Purpose**: Route prompts to appropriate agents

**v2.1 Features**:
- Prioritizes explicit @agent- mentions
- Falls back to keyword analysis
- Tracks routing confidence
- Creates AGENT_SUGGESTION.md

**Routing Priority**:
1. Explicit @agent- mentions (always honored)
2. Keyword matching (if no explicit mentions)
3. Context-based suggestions

---

## 🚀 Phase 3: MCP Integration Hooks

### 3.1 MCP Gateway
**Purpose**: Validate and track MCP tool usage

**Enforces**:
- Maximum 5 MCPs total
- Approved tools only
- Usage tracking
- Tier compliance

**Approved MCPs**:
- Tier 1: playwright, obsidian, brave-search
- Tier 2 Database: mongodb, postgresql, supabase
- Tier 2 Deploy: gcp, vercel, netlify, aws

---

## 🚀 Installation

### Windows PowerShell
```powershell
# One-line installer
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.ps1 | iex
```

### Linux/WSL
```bash
# One-line installer
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.sh | bash
```

### macOS
```bash
# One-line installer
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all-mac.sh | bash
```

### Manual Installation
1. Create `.claude` directory structure
2. Copy all hook files to `.claude/hooks/`
3. Copy configuration files to `.claude/config/`
4. Copy settings.json to `.claude/`
5. Make Python files executable: `chmod +x .claude/hooks/*.py`

---

## 🎯 Testing & Validation

### Test Session Continuity
```bash
# Start Claude Code
# Create some agent state
echo "# Test Agent State" > .claude/state/agent_state.md
echo "- @agent-backend-services: Active" >> .claude/state/agent_state.md

# Exit Claude Code
# Restart Claude Code
# Check if SESSION_CONTEXT.md was created with your state
```

### Test @agent- mention Routing
```bash
# Submit a prompt with explicit mention
"@agent-frontend-architecture[opus] design a dashboard"

# Check .claude/state/agent_routing.json for routing record
```

### Test Model Tracking
```bash
# Use agents with different models
"@agent-business-analyst[opus] analyze market"
"@agent-testing-automation[haiku] write tests"

# Check .claude/state/model_usage.json for usage tracking
# Look for COST_SAVINGS.md if savings > $10
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
6. **Cost Visibility**: Model usage tracked and optimized

---

## 🔧 Customization

### Coding Standards
Edit `.claude/config/coding_standards.json`:
```json
{
  "naming": {
    "functions": "camelCase",  // or snake_case
    "classes": "PascalCase",
    "constants": "UPPER_SNAKE_CASE"
  },
  "forbidden_patterns": [
    // Add your patterns
  ]
}
```

### Agent Model Preferences
Edit `.claude/config/agent_models.json`:
```json
{
  "model_preferences": {
    "opus": {
      "agents": ["your-complex-agents"]
    },
    "haiku": {
      "agents": ["your-simple-agents"]
    }
  }
}
```

### MCP Configuration
Edit `.claude/config/mcp_config.json`:
```json
{
  "max_tools": 5,
  "approved_tools": ["your-tools"]
}
```

---

## 🚨 Troubleshooting

### Hooks Not Running
1. Check Claude Code settings include `.claude/settings.json`
2. Verify Python 3 is installed: `python3 --version`
3. Check hook file permissions: `ls -la .claude/hooks/`
4. Look for errors in Claude Code logs

### Session Not Restoring
1. Check `.claude/state/` directory exists
2. Verify session_loader.py has execute permissions
3. Look for SESSION_CONTEXT.md after restart
4. Check for error messages on startup

### @agent- mentions Not Working
1. Verify agent_mention_parser.py is in UserPromptSubmit hooks
2. Check `.claude/state/agent_routing.json` for records
3. Ensure @agent- syntax is correct (with hyphen)
4. Look for routing messages in output

### Cost Tracking Issues
1. Check model_tracker.py is executable
2. Verify `.claude/state/model_usage.json` exists
3. Look for COST_SAVINGS.md when savings > $10
4. Check daily usage is being recorded

---

## 🚀 Next Steps

1. **Install Hooks**: Use one-line installer for your OS
2. **Configure Standards**: Customize coding standards
3. **Set Model Preferences**: Configure which agents use which models
4. **Test Everything**: Run through all test scenarios
5. **Monitor Usage**: Check cost savings regularly
6. **Iterate**: Adjust configurations based on your workflow

Remember: **Hooks make your agents' intelligence executable!**

---

*Hooks Implementation Guide v2.1 | Compatible with Claude Code @agent- mentions*