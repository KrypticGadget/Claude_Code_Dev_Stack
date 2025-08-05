# 📋 Claude Code Dev Stack - Repository Update Plan

## 🎯 Objectives
1. Add Windows PowerShell native support
2. Integrate MCP tools into the agent system
3. Create meta-prompting methodology
4. Prepare for hooks and administrative enhancements

## 📁 New Files to Add

### Root Directory
```
/
├── install.ps1                    # Windows native installer
├── install-commands.ps1           # Slash commands installer
├── install-all.ps1               # Complete installation
├── WINDOWS_INSTALL.md            # Windows-specific guide
└── MASTER_PROMPTING_GUIDE.md     # The meta-prompting guide
```

### Windows Directory (New)
```
/windows/
├── README.md                     # Windows-specific documentation
├── claude-code-aliases.ps1       # PowerShell aliases
├── setup-hooks.ps1              # Git hooks setup
└── admin-tools.ps1              # Administrative utilities
```

### MCP Integration Directory (New)
```
/mcp-integration/
├── README.md                    # MCP integration guide
├── tier1-tools.json            # Priority MCP tools config
├── tool-prompts/               # MCP-specific prompt templates
│   ├── file-system.md
│   ├── git-integration.md
│   ├── database-access.md
│   └── api-testing.md
└── install-mcp.ps1             # MCP setup script
```

### Hooks Directory (New)
```
/hooks/
├── pre-commit.ps1              # Pre-commit validation
├── post-update.ps1             # Post-update actions
├── test-runner.ps1             # Automated testing
└── diff-logger.ps1             # Change tracking
```

## 📝 Updated README.md Sections

### New Installation Section
```markdown
## ⚡ Quick Install

### Windows PowerShell (Native)
```powershell
# One-line installation
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.ps1 | iex
```

### Linux/macOS/WSL
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install.sh | bash
```

### With MCP Tools (Advanced)
```powershell
# Install with MCP integration
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/mcp-integration/install-mcp.ps1 | iex
```
```

### New Meta-Prompting Section
```markdown
## 🧠 Meta-Prompting Methodology

Give the [Master Prompting Guide](MASTER_PROMPTING_GUIDE.md) to any Claude instance along with your project details to receive perfectly integrated prompts.

### Quick Example
Tell Claude: "Using the Master Prompting Guide, create prompts for building a SaaS platform with user authentication, payment processing, and admin dashboard."

Claude will generate integrated prompts using:
- Appropriate slash commands
- Correct agent routing
- MCP tool integration
- Proper execution sequence
```

## 🔧 Git Commands to Execute

```bash
# On your other machine with Claude Code

# 1. Clone the repo
git clone https://github.com/KrypticGadget/Claude_Code_Dev_Stack.git
cd Claude_Code_Dev_Stack

# 2. Create new directories
mkdir windows
mkdir mcp-integration
mkdir hooks

# 3. Add the PowerShell scripts
# Copy the content from the artifacts above into these files:
# - install.ps1
# - install-commands.ps1
# - install-all.ps1
# - WINDOWS_INSTALL.md
# - MASTER_PROMPTING_GUIDE.md

# 4. Update existing files
# Update README.md with new installation instructions

# 5. Stage and commit
git add .
git commit -m "Add Windows PowerShell support and meta-prompting methodology"

# 6. Push to repository
git push origin main
```

## 🎨 Claude Code Prompts for Updates

### Update 1: Create Windows Support
```
/new-project "Windows PowerShell support for Claude Code Dev Stack"
Context: Existing repo needs Windows native installation
Requirements:
- PowerShell scripts to replace bash scripts
- One-line installation commands
- Windows-specific documentation
MCP Tools: @file-system for script creation, @git for commits
```

### Update 2: Add MCP Integration
```
/backend-service "MCP tool integration layer"
Context: Add Model Context Protocol support to agent system
Requirements:
- Tier 1 tools: file-system, git, database, api-test, env-config
- Integration points in each agent
- Tool-specific prompt templates
MCP Tools: @file-system for config files
```

### Update 3: Create Hooks System
```
/devops "Git hooks and administrative tools"
Context: Enhance reliability with automated checks
Requirements:
- Pre-commit: code review, testing
- Post-update: documentation sync
- Diff logging for change tracking
- PowerShell-based for Windows
MCP Tools: @git for hook installation, @file-system for scripts
```

## 🚀 Testing Protocol

### 1. Windows Installation Test
```powershell
# Remove existing installation
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude-code"

# Test one-line installer
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.ps1 | iex

# Verify installation
Test-Path "$env:USERPROFILE\.claude-code\agents"
Test-Path "$env:USERPROFILE\.claude-code\commands"

# Test command execution
claude-code "/new-project Test installation"
```

### 2. MCP Integration Test
```powershell
# Test MCP tool access
claude-code "Read all files in current directory using @file-system"
claude-code "Show git status using @git"
```

### 3. Meta-Prompting Test
```
# Give MASTER_PROMPTING_GUIDE.md to a fresh Claude instance
# Ask it to generate prompts for various scenarios
# Verify the prompts work correctly in Claude Code
```

## 📊 Success Metrics

- ✅ Windows users can install with one PowerShell command
- ✅ All 28 agents accessible on Windows
- ✅ All 18 slash commands work correctly
- ✅ MCP tools integrate seamlessly
- ✅ Meta-prompting guide produces valid prompts
- ✅ Hooks enhance development workflow
- ✅ Documentation is comprehensive

## 🔄 Next Steps After Repository Update

1. **Release Notes**: Create release notes for Windows support
2. **Version Tag**: Tag as v2.0.0 with Windows + MCP support
3. **Community Announcement**: Share the update
4. **Gather Feedback**: Monitor issues for Windows-specific problems
5. **Iterate**: Enhance based on user feedback