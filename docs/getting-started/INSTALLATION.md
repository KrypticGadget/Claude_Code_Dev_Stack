# Installation Guide - Claude Code Agent System

This guide walks you through installing and configuring the Claude Code Agent System with Claude Code.

## Prerequisites

Before installing the agent system, ensure you have:

1. **Claude Code CLI** installed and configured
   - Visit [claude.ai/code](https://claude.ai/code) to get started
   - Verify installation: `claude --version`

2. **Git** installed on your system
   - Verify with: `git --version`

3. **Text editor** for viewing/editing agent files

## Installation Methods

### Method 1: One-Line Installer (Recommended)

```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/install.sh | bash
```

This installer will:
- Backup your existing Claude Code configuration
- Download all 28 agent files
- Install agents in the correct location
- Verify the installation
- Provide next steps

### Method 2: Manual Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/claude-code-agent-system.git
cd claude-code-agent-system
```

#### Step 2: Locate Claude Code Agent Directory
Find where Claude Code stores agent configurations:

**macOS/Linux:**
```bash
~/.config/claude/agents/
```

**Windows:**
```bash
%APPDATA%\claude\agents\
```

#### Step 3: Copy Agent Files
Copy all `.md` files from the `agents/` directory to your Claude Code agent directory:

```bash
# macOS/Linux
cp agents/*.md ~/.config/claude/agents/

# Windows (PowerShell)
Copy-Item agents\*.md -Destination "$env:APPDATA\claude\agents\"
```

#### Step 4: Verify Installation
List installed agents:
```bash
claude agent list
```

You should see all 28 agents listed.

### Method 3: Selective Installation

To install only specific agents:

```bash
# Copy individual agent files
cp agents/master-orchestrator-agent.md ~/.config/claude/agents/
cp agents/business-analyst-agent.md ~/.config/claude/agents/
# ... etc
```

## Post-Installation Setup

### 1. Test the Installation

Test with a simple command:
```
> Use the master-orchestrator agent to help me plan a simple todo application
```

### 2. Configure Your Workspace

Create a CLAUDE.md file in your project root:
```markdown
# Project: [Your Project Name]

## Quick Commands
- Lint: `npm run lint`
- Test: `npm test`
- Build: `npm run build`

## Architecture Notes
[Add project-specific notes here]
```

### 3. Customize Agent Behavior (Optional)

Agents can be customized by editing their `.md` files:

1. Navigate to the agents directory
2. Open the agent file you want to customize
3. Modify the instructions while keeping the frontmatter intact
4. Save the file

## Updating Agents

### Automatic Updates

Use the update script:
```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/update.sh | bash
```

### Manual Updates

1. Pull the latest changes:
```bash
cd claude-code-agent-system
git pull origin main
```

2. Copy updated files:
```bash
cp agents/*.md ~/.config/claude/agents/
```

### Updating Individual Agents

To update a specific agent:
```bash
# Download the latest version
curl -o master-orchestrator-agent.md https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/agents/master-orchestrator-agent.md

# Copy to Claude Code directory
cp master-orchestrator-agent.md ~/.config/claude/agents/
```

## Troubleshooting

### Agents Not Appearing

1. Verify Claude Code is installed:
```bash
claude --version
```

2. Check agent directory exists:
```bash
ls ~/.config/claude/agents/  # macOS/Linux
dir %APPDATA%\claude\agents\  # Windows
```

3. Ensure files have `.md` extension and valid frontmatter

### Permission Issues

On macOS/Linux, ensure proper permissions:
```bash
chmod 644 ~/.config/claude/agents/*.md
```

### Agent Not Activating

Check the agent file has valid frontmatter:
```markdown
---
name: agent-name
description: Agent description with activation triggers
tools: Read, Write, Edit, Bash, Grep, Glob
---
```

### Conflicts with Existing Agents

If you have existing custom agents:
1. Backup your current agents first
2. Install the new agents
3. Merge any customizations

## Best Practices

1. **Regular Updates**: Check for updates monthly
2. **Backup Custom Agents**: Before updating, backup any customized agents
3. **Project-Specific Config**: Use CLAUDE.md files for project-specific settings
4. **Agent Combinations**: Learn which agents work well together
5. **Prompt Templates**: Use the master-prompts for consistency

## Getting Help

- **Documentation**: See `/docs/` directory
- **Examples**: Check `/examples/` directory  
- **Issues**: Report at [GitHub Issues](https://github.com/yourusername/claude-code-agent-system/issues)
- **Community**: Join discussions at [GitHub Discussions](https://github.com/yourusername/claude-code-agent-system/discussions)

## Next Steps

1. Read the [Quick Start Guide](../QUICK_START.md)
2. Explore [Master Prompts](../master-prompts/README.md)
3. Review [Agent Catalog](architecture/agent-catalog.md)
4. Try [Example Projects](../examples/README.md)

Congratulations! You now have access to 28 specialized AI agents ready to help with your development projects.