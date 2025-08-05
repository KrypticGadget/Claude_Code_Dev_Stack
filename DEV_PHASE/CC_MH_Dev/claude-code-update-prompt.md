# 🚀 Claude Code Prompt for Repository Updates

Copy and paste this entire prompt into Claude Code on your other machine:

---

## Project: Update Claude Code Dev Stack Repository

I need to update my GitHub repository at https://github.com/KrypticGadget/Claude_Code_Dev_Stack with Windows PowerShell support and meta-prompting methodology.

### Current State
- Repository has bash scripts for Linux/WSL installation
- 28 AI agents in Config_Files/
- 18 slash commands in slash-commands/
- Works in WSL but not native Windows PowerShell

### Required Updates

#### 1. Add Windows PowerShell Scripts
Create these files in the repository root:

**install.ps1** - Main agent installer for Windows:
- Download all 28 agents from Config_Files/
- Install to `$env:USERPROFILE\.claude-code\agents\`
- Create configuration file
- Generate quick reference

**install-commands.ps1** - Slash commands installer:
- Download all slash commands
- Install to `$env:USERPROFILE\.claude-code\commands\`
- Create command registry
- Generate PowerShell aliases

**install-all.ps1** - Complete installation:
- Run both installers
- One-line execution support

#### 2. Create Master Prompting Guide
Create **MASTER_PROMPTING_GUIDE.md** with:
- Meta-prompting methodology (AIMS structure)
- Slash command reference table
- Agent specialization matrix
- MCP tool integration (Tier 1: file-system, git, database, api-test, env-config)
- Master prompt templates
- Workflow examples

#### 3. Update Documentation
- Add Windows section to README.md
- Create WINDOWS_INSTALL.md
- Update installation instructions for both platforms

#### 4. Create Directory Structure
```
/windows/
  - README.md
  - claude-code-aliases.ps1
  - setup-hooks.ps1
  - admin-tools.ps1

/mcp-integration/
  - README.md
  - tier1-tools.json
  - tool-prompts/
    - file-system.md
    - git-integration.md
    - database-access.md
    - api-testing.md

/hooks/
  - pre-commit.ps1
  - post-update.ps1
  - test-runner.ps1
  - diff-logger.ps1
```

### PowerShell Script Requirements
- Use `Invoke-WebRequest` for downloads
- Support progress indicators
- Handle errors gracefully
- Create all necessary directories
- Generate configuration files
- Check for Claude Code installation

### One-Line Installation Commands
Windows PowerShell:
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.ps1 | iex
```

Linux/macOS/WSL (keep existing):
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install.sh | bash
```

### Git Workflow
1. Create new branch: `feature/windows-powershell-support`
2. Add all new files
3. Update existing files
4. Commit with message: "Add Windows PowerShell support and meta-prompting methodology"
5. Push and create PR

### Testing Requirements
- Scripts work on Windows PowerShell 5.1+
- Scripts work on PowerShell Core 7+
- One-line installers execute successfully
- All agents and commands accessible after installation
- No dependency on WSL or Git Bash

### MCP Integration Notes
Focus on Tier 1 priority tools:
- @file-system - Read/write project files
- @git - Version control operations  
- @database - Direct database queries
- @api-test - Endpoint validation
- @env-config - Environment variable management

Each agent should have MCP tool recommendations in their prompts.

### Deliverables
1. All PowerShell scripts tested and working
2. Complete documentation updates
3. Meta-prompting guide that can be given to any Claude instance
4. Git repository updated and pushed
5. Release notes for v2.0.0

Please start by creating the PowerShell installation scripts, then the master prompting guide, then update all documentation.

---

## Additional Context for Follow-up

After the initial updates, we'll need to:
1. Create hooks for testing protocols
2. Add diff logging capabilities
3. Enhance administrative tools
4. Integrate MCP tools more deeply

The goal is a unified system where any Claude instance can generate perfectly integrated prompts using agents, slash commands, and MCP tools.