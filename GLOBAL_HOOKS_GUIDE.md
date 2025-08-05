# 🌐 Global Hooks System - Claude Code Dev Stack v2.1

## Overview

The Global Hooks System enables Claude Code to work seamlessly with ANY project at ANY path, including paths with spaces and special characters. Install once at Claude Code root, and hooks work everywhere forever.

---

## 🏗️ Architecture

### Global Installation Structure
```
claude-code-root/
├── .claude-global/              # Global Claude configuration
│   ├── hooks/                   # Universal hook scripts
│   │   ├── base_hook.py         # Shared utilities
│   │   ├── agent_mention_parser.py
│   │   ├── session_loader.py
│   │   ├── session_saver.py
│   │   ├── quality_gate.py
│   │   ├── planning_trigger.py
│   │   ├── agent_orchestrator.py
│   │   ├── model_tracker.py
│   │   └── mcp_gateway.py
│   ├── config/                  # Global configurations
│   │   ├── hooks.json
│   │   ├── agents.json
│   │   └── models.json
│   ├── state/                   # Runtime state (auto-created)
│   └── logs/                    # Hook execution logs
└── settings.json                # Claude Code global settings
```

---

## 🚀 Installation

### One-Line Installation

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-hooks.ps1 | iex
```

**Ubuntu/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-hooks.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-hooks-mac.sh | bash
```

### What the Installer Does

1. **Detects Claude Code Root**: Finds Claude Code installation directory
2. **Sets Environment Variables**:
   - `CLAUDE_HOME`: Claude Code root directory
   - `CLAUDE_PYTHON`: Python executable path
   - `CLAUDE_HOOKS_DIR`: Global hooks directory
3. **Creates Global Structure**: `.claude-global` directory at root
4. **Downloads Hook Scripts**: All 9 Python hooks + base utilities
5. **Updates Global Settings**: Configures Claude Code to use hooks
6. **Tests Installation**: Verifies hooks work with spaces in paths

---

## 🔧 Environment Variables

### Core Variables
- **`CLAUDE_HOME`**: Claude Code installation root
- **`CLAUDE_PYTHON`**: Python executable (auto-detected)
- **`CLAUDE_PROJECT_DIR`**: Current project directory (dynamic)
- **`CLAUDE_SESSION_ID`**: Current session identifier
- **`CLAUDE_HOOKS_DIR`**: Global hooks directory

### Usage in Hooks
```python
import os
from pathlib import Path

# Get project directory (handles spaces automatically)
project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())).resolve()

# Access Claude home
claude_home = Path(os.environ.get('CLAUDE_HOME', '~/.claude')).expanduser()
```

---

## 📁 Path Handling

### Spaces and Special Characters
All hooks use Python's `pathlib.Path` for robust path handling:

```python
# Safe path joining
config_file = Path(project_dir) / ".claude" / "config.json"

# Handle Windows, macOS, Linux paths
normalized_path = Path(user_input).resolve()

# Quote paths for shell commands
quoted_path = shlex.quote(str(file_path))
```

### Cross-Platform Support
- **Windows**: `C:\Users\Test User\My Projects\Claude Project`
- **macOS**: `/Users/test user/Development/Claude Projects/My App`
- **Linux**: `/home/user/projects/claude apps/test project`
- **WSL**: `/mnt/c/Users/Test User/Projects/Claude Code Apps`

---

## 🪝 Hook Scripts

### 1. **base_hook.py**
Shared utilities for all hooks:
- Path resolution and normalization
- Environment variable management
- Logging configuration
- Error handling
- Cache management

### 2. **agent_mention_parser.py**
Parses @agent- mentions:
- Detects explicit mentions: `@agent-backend-services[haiku]`
- Implicit routing based on keywords
- Outputs routing decisions

### 3. **session_loader.py**
Restores context on startup:
- Loads previous session state
- Detects project type
- Provides continuation context

### 4. **session_saver.py**
Persists session state:
- Saves after each operation
- Tracks file changes
- Maintains agent history

### 5. **quality_gate.py**
Enforces code quality:
- Checks code standards
- Security vulnerability detection
- Provides improvement suggestions

### 6. **planning_trigger.py**
Detects planning needs:
- Analyzes task complexity
- Suggests appropriate agents
- Triggers planning mode

### 7. **agent_orchestrator.py**
Manages agent execution:
- Routes to appropriate agents
- Tracks execution flow
- Aggregates results

### 8. **model_tracker.py**
Tracks usage and costs:
- Monitors token usage
- Calculates costs
- Suggests optimizations

### 9. **mcp_gateway.py**
Manages MCP connections:
- Validates MCP requests
- Auto-starts servers
- Enforces security policies

---

## ⚙️ Configuration

### Global Settings (settings.json)
```json
{
  "hooks": {
    "enabled": true,
    "global_path": "${env:CLAUDE_HOME}/.claude-global",
    "hooks_command": "\"${env:CLAUDE_PYTHON:-python3}\" \"${env:CLAUDE_HOME}/.claude-global/hooks/{hook_name}.py\"",
    "environment": {
      "CLAUDE_HOME": "${env:CLAUDE_HOME}",
      "CLAUDE_PYTHON": "${env:CLAUDE_PYTHON:-python3}",
      "CLAUDE_PROJECT_DIR": "${env:PWD}"
    }
  }
}
```

### Hook Configuration (hooks.json)
```json
{
  "session_management": {
    "auto_save": true,
    "save_interval": 300,
    "max_session_age": 86400
  },
  "quality_gates": {
    "enabled": true,
    "block_on_critical": false,
    "checks": ["security", "complexity", "naming"]
  },
  "agent_routing": {
    "confidence_threshold": 0.7,
    "allow_multiple_agents": true,
    "default_model": "default"
  }
}
```

---

## 🧪 Testing with Spaces

### Test Projects
Create test projects with challenging paths:

```bash
# Windows
mkdir "C:\Users\Test User\My Projects\Claude Test App"
cd "C:\Users\Test User\My Projects\Claude Test App"
claude-code .

# macOS/Linux
mkdir -p ~/Development/"Project & Tests"/"Claude App (Beta)"
cd ~/Development/"Project & Tests"/"Claude App (Beta)"
claude-code .
```

### Verify Hooks Work
1. Open Claude Code in a project with spaces
2. Type: `@agent-backend-services create API`
3. Check `.claude-global/logs/` for execution logs
4. Verify no "operation blocked by hook" errors

---

## 🔍 Troubleshooting

### Common Issues

**1. Environment Variables Not Set**
```bash
# Check variables
echo $CLAUDE_HOME
echo $CLAUDE_PYTHON

# Reload shell
source ~/.bashrc  # Linux/WSL
source ~/.zshrc   # macOS
```

**2. Python Not Found**
```bash
# Set CLAUDE_PYTHON manually
export CLAUDE_PYTHON=$(which python3)
```

**3. Hooks Not Running**
- Check Claude Code settings.json has hooks enabled
- Verify `.claude-global/hooks/` contains all scripts
- Check logs in `.claude-global/logs/`

**4. Path Issues**
- Ensure all paths use proper quoting
- Check environment variable expansion
- Verify no hardcoded paths in hooks

---

## 📊 Monitoring

### Hook Logs
```bash
# View recent hook executions
tail -f ~/.claude-global/logs/hooks.log

# Check specific hook
grep "agent_mention_parser" ~/.claude-global/logs/hooks.log
```

### Usage Statistics
```bash
# View model usage
cat ~/.claude-global/state/model_usage.json

# Check agent invocations
cat ~/.claude-global/state/agent_history.json
```

---

## 🛡️ Security

### Hook Security Features
- Command validation before execution
- Restricted file access to allowed directories
- No execution of arbitrary code
- Sanitized user inputs
- Secure environment variable handling

### Best Practices
1. Keep Python updated
2. Review hook logs regularly
3. Don't modify hook scripts directly
4. Use installer for updates
5. Report suspicious activity

---

## 🔄 Updates

### Updating Hooks
Re-run the installer to update:
```bash
# Updates all hooks to latest version
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-hooks.sh | bash
```

### Backup Before Update
```bash
# Backup current hooks
cp -r ~/.claude-global ~/.claude-global.backup
```

---

## 🎯 Benefits

1. **One-Time Installation**: Install once, works forever
2. **Universal Compatibility**: Works with any project path
3. **Zero Configuration**: No per-project setup needed
4. **Automatic Updates**: Hooks update themselves
5. **Cross-Platform**: Same behavior on all OS
6. **Space-Safe**: Handles paths with spaces perfectly
7. **Error Resilient**: Never blocks Claude Code operations

---

## 📝 Example Usage

After installation, hooks work automatically:

```bash
# Open any project (with spaces!)
cd "/home/user/My Projects/Claude App (v2.1)"
claude-code .

# Use @agent- mentions
"@agent-backend-services[haiku] create user authentication API"

# Hooks automatically:
# - Parse the agent mention
# - Route to backend-services agent
# - Use Haiku model for cost savings
# - Track usage and costs
# - Save session state
```

---

## 🤝 Contributing

To contribute to the hooks system:
1. Fork the repository
2. Create feature branch
3. Test with various path scenarios
4. Submit pull request

---

## 📄 License

MIT License - See LICENSE file for details