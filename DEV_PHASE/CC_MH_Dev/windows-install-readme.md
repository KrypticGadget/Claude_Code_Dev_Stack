# 🪟 Windows PowerShell Installation Guide

Since Claude Code now runs natively on Windows, here's how to install the Claude Code Dev Stack using PowerShell.

## ⚡ Quick Install (One Command)

```powershell
# Run this in PowerShell (as regular user, not admin)
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-all.ps1 | iex
```

## 📋 Step-by-Step Installation

### 1. Install Agents Only
```powershell
# Download and run the agents installer
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install.ps1" -OutFile "$env:TEMP\install.ps1"
& "$env:TEMP\install.ps1"
```

### 2. Install Slash Commands Only
```powershell
# Download and run the commands installer
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/install-commands.ps1" -OutFile "$env:TEMP\install-commands.ps1"
& "$env:TEMP\install-commands.ps1"
```

## 📁 Installation Locations

After installation, your files will be located at:
- **Agents**: `%USERPROFILE%\.claude-code\agents\`
- **Commands**: `%USERPROFILE%\.claude-code\commands\`
- **Prompts**: `%USERPROFILE%\.claude-code\master-prompts\`
- **Config**: `%USERPROFILE%\.claude-code\config.ini`

## 🚀 Using Claude Code with Agents

### Basic Usage
```powershell
# Set your API key (first time only)
claude-code set-key

# Start a new project
claude-code "/new-project E-commerce platform with inventory management"

# Use specific agents
claude-code --agent backend "Design a REST API for user authentication"
claude-code --agent frontend "Create a responsive dashboard"
```

### Using Slash Commands
```powershell
# Quick commands for common tasks
claude-code "/backend-service REST API with JWT authentication"
claude-code "/database-design multi-tenant SaaS schema"
claude-code "/frontend-mockup landing page with hero section"
claude-code "/documentation API reference guide"
```

## ⚡ PowerShell Aliases (Optional)

Add these aliases to your PowerShell profile for even quicker access:

```powershell
# Add to your $PROFILE
. "$env:USERPROFILE\.claude-code\commands\claude-code-aliases.ps1"

# Then use shortcuts like:
ccnew "SaaS platform idea"          # Same as: claude-code "/new-project ..."
ccbackend "REST API design"         # Same as: claude-code "/backend-service ..."
ccfrontend "dashboard mockup"       # Same as: claude-code "/frontend-mockup ..."
```

To edit your PowerShell profile:
```powershell
notepad $PROFILE
```

## 🔧 Troubleshooting

### Claude Code not found
```powershell
# Make sure Claude Code is installed
npm install -g @anthropic-ai/claude-code

# Verify installation
claude-code --version
```

### Permission Issues
```powershell
# If you get execution policy errors
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Network Issues
```powershell
# If downloads fail, try with TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

## 📚 What's Included

- **28 Specialized AI Agents**
  - Backend, Frontend, Database, DevOps, Security, and more
- **18 Slash Commands**
  - Quick access to common development tasks
- **Master Prompts**
  - Templates for project initialization, workflows, optimization
- **Configuration Files**
  - Customizable agent behaviors and aliases

## 🎯 Next Steps

1. **Start a Project**: `claude-code "/new-project Your awesome idea"`
2. **Read Quick Reference**: `notepad $env:USERPROFILE\.claude-code\QUICK_REFERENCE.txt`
3. **Explore Agents**: Check `$env:USERPROFILE\.claude-code\agents\` directory
4. **Customize**: Edit agent files to match your workflow

## 📄 Update Your Repository

To add these PowerShell scripts to your repository:

1. Save `install.ps1` to your repo root
2. Save `install-commands.ps1` to your repo root
3. Update README.md with Windows instructions
4. Consider creating a `windows/` directory for Windows-specific files

---

**Note**: These scripts are designed for Windows PowerShell 5.1+ and PowerShell Core 7+. They do not require WSL or Git Bash.