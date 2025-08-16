# Claude Code Dev Stack v3.0 - Complete Installation Guide

**Zero-Configuration Installation for All Components with Full Attribution**

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [One-Line Installation](#one-line-installation)
3. [Component-Specific Installation](#component-specific-installation)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Verification & Testing](#verification--testing)
6. [Attribution & Third-Party Setup](#attribution--third-party-setup)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup
- **Claude Code**: Latest version installed

### Required Dependencies
- **Node.js**: 18+ (for MCP servers)
- **Python**: 3.8+ (for hooks and audio system)
- **Git**: Latest version (for repository cloning)
- **PowerShell**: 5.1+ on Windows

### Optional Dependencies
- **Docker**: For containerized deployment
- **Visual Studio Code**: For enhanced development experience
- **Obsidian**: For knowledge management integration

---

## One-Line Installation

### 🚀 Complete System Installation

#### Windows (PowerShell)
```powershell
# Complete installation with all components
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1 | iex

# Alternative: Download and run with options
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1
.\install-all.ps1 -IncludeMobile -AudioEnabled -ObsidianApiKey "your_api_key"
```

#### macOS (Bash)
```bash
# Complete installation
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/install-all.sh | bash

# With options
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/install-all.sh
chmod +x install-all.sh
./install-all.sh --include-mobile --audio-enabled
```

#### Linux (Bash)
```bash
# Complete installation
wget -qO- https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/install-all.sh | bash

# With options
wget https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/install-all.sh
chmod +x install-all.sh
./install-all.sh --include-mobile --audio-enabled
```

### Installation Options
- `--include-mobile` / `-IncludeMobile`: Install mobile interface components
- `--audio-enabled` / `-AudioEnabled`: Enable audio notification system
- `--obsidian-api-key` / `-ObsidianApiKey`: Set Obsidian API key for MCP integration
- `--skip-verification` / `-SkipVerification`: Skip post-installation verification
- `--force` / `-Force`: Force reinstallation of existing components

---

## Component-Specific Installation

### 🤖 28 AI Agents Installation

#### Windows
```powershell
# Install all 28 agents
.\platform-tools\windows\installers\install-agents.ps1

# Verify installation
Get-ChildItem ~/.claude/agents/*.md | Measure-Object
# Expected result: Count = 28
```

#### macOS/Linux
```bash
# Install all 28 agents
./platform-tools/unix/installers/install-agents.sh

# Verify installation
ls ~/.claude/agents/*.md | wc -l
# Expected result: 28
```

**Agent Categories Installed:**
- 4 Orchestration & Strategy agents
- 4 Technical Leadership agents  
- 7 Architecture & Design agents
- 6 Development & Implementation agents
- 7 Operations & Quality agents

### 🔧 28 Automation Hooks Installation

#### Windows
```powershell
# Install all 28 hooks
.\platform-tools\windows\installers\install-hooks.ps1

# Verify hook configuration
Get-Content ~/.claude/settings.json | ConvertFrom-Json | Select-Object -ExpandProperty hooks
```

#### macOS/Linux
```bash
# Install all 28 hooks
./platform-tools/unix/installers/install-hooks.sh

# Verify hook configuration
cat ~/.claude/settings.json | jq '.hooks'
```

**Hook Categories Installed:**
- 4 Session Management hooks
- 6 Agent Orchestration hooks
- 5 Quality Control hooks
- 4 Project Lifecycle hooks
- 5 Integration & Monitoring hooks
- 4 Communication & Sync hooks

### ⚡ 18 Slash Commands Installation

#### Windows
```powershell
# Install all 18 slash commands
.\platform-tools\windows\installers\install-commands.ps1

# Test command availability
claude "Please list available slash commands"
```

#### macOS/Linux
```bash
# Install all 18 slash commands
./platform-tools/unix/installers/install-commands.sh

# Test command availability
claude "Please list available slash commands"
```

**Command Categories Installed:**
- 4 Project Management commands
- 3 Business & Analysis commands
- 3 Architecture & Design commands
- 4 Development commands
- 4 Quality & Deployment commands

### 🔌 3 MCP Servers Installation

#### Automated MCP Setup (Windows)
```powershell
# Install all 3 MCP servers
.\platform-tools\windows\installers\install-mcps.ps1

# Or install with specific configuration
.\platform-tools\windows\mcp\master-mcp-setup.ps1 -ObsidianApiKey "your_api_key_here"
```

#### Manual MCP Installation

**1. Playwright MCP**
```powershell
# Basic headless installation
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless

# Full-featured installation
claude mcp add playwright-full -- cmd /c npx '@playwright/mcp@latest' --caps=vision,pdf --save-session
```

**2. Obsidian MCP**
```powershell
# Prerequisites: Install UV
pip install uv

# Install Obsidian MCP
claude mcp add obsidian --env OBSIDIAN_API_KEY=your_api_key --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- cmd /c uvx mcp-obsidian
```

**3. Web-search MCP**
```powershell
# Clone and build
git clone https://github.com/pskill9/web-search.git "$env:USERPROFILE\mcp-servers\web-search"
cd "$env:USERPROFILE\mcp-servers\web-search"
npm install && npm run build

# Add to Claude Code
claude mcp add web-search -- cmd /c node "%USERPROFILE%\mcp-servers\web-search\build\index.js"
```

### 🔊 Audio System Installation

#### Windows Audio Setup
```powershell
# Install audio system
.\platform-tools\windows\installers\install-audio.ps1

# Test audio system
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py
```

#### macOS/Linux Audio Setup
```bash
# Install audio system
./platform-tools/unix/installers/install-audio.sh

# Test audio system (macOS)
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py
```

**Audio Components Installed:**
- 102+ contextual audio files
- Model-specific notification sounds
- Context-aware audio selection
- Cross-platform audio support

### 📱 Mobile Interface Installation

#### Windows Mobile Setup
```powershell
# Install mobile interface
.\platform-tools\windows\mobile\launch-mobile-remote.ps1

# Access mobile interface
Start-Process "http://localhost:8080"
```

#### Cross-Platform Mobile Setup
```bash
# Install mobile components
./platform-tools/unix/mobile/setup-mobile.sh

# Launch mobile interface
python ~/.claude/mobile/launch_mobile.py --port 8080
```

---

## Platform-Specific Instructions

### 🪟 Windows Installation Details

#### Prerequisites Installation
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies via Chocolatey
choco install nodejs python git -y

# Or install manually:
# Node.js: https://nodejs.org/
# Python: https://python.org/
# Git: https://git-scm.com/
```

#### Windows-Specific Configuration
```powershell
# Enable PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Windows-specific tools
npm install -g windows-build-tools

# Configure Windows audio support
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Media
```

### 🍎 macOS Installation Details

#### Prerequisites Installation
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies via Homebrew
brew install node python git

# Install additional tools
brew install ffmpeg  # For audio processing
```

#### macOS-Specific Configuration
```bash
# Configure audio permissions
sudo chmod +x /usr/bin/afplay

# Install Python dependencies
pip3 install --user pygame playsound

# Configure shell for Claude Code
echo 'export PATH="$HOME/.claude/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 🐧 Linux Installation Details

#### Ubuntu/Debian Installation
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install -y nodejs npm python3 python3-pip git

# Install audio support
sudo apt install -y alsa-utils pulseaudio

# Install additional tools
sudo apt install -y curl wget jq
```

#### CentOS/RHEL Installation
```bash
# Install EPEL repository
sudo dnf install -y epel-release

# Install dependencies
sudo dnf install -y nodejs npm python3 python3-pip git

# Install audio support
sudo dnf install -y alsa-utils pulseaudio
```

#### Linux-Specific Configuration
```bash
# Configure audio permissions
sudo usermod -a -G audio $USER

# Install Python audio dependencies
pip3 install --user playsound pygame

# Configure systemd service (optional)
sudo systemctl enable claude-code-stack
```

---

## Verification & Testing

### 🔍 Complete System Verification

#### Automated Verification
```powershell
# Windows verification
.\platform-tools\windows\verifiers\verify-installation.ps1 -Verbose

# Expected output:
# ✅ 28 Agents installed and functional
# ✅ 28 Hooks configured and active  
# ✅ 18 Slash Commands available
# ✅ 3 MCP Servers connected
# ✅ Audio System operational
# ✅ Mobile Interface accessible
```

```bash
# Unix verification
./platform-tools/unix/verifiers/verify-installation.sh --verbose

# Expected output:
# ✅ 28 Agents installed and functional
# ✅ 28 Hooks configured and active
# ✅ 18 Slash Commands available
# ✅ 3 MCP Servers connected
# ✅ Audio System operational
# ✅ Mobile Interface accessible
```

### Component-Specific Testing

#### Agent Testing
```powershell
# Test agent routing
claude "Use the @agent-master-orchestrator to test the system"

# Test agent collaboration
claude "Use the @agent-business-analyst to analyze a test market opportunity"
```

#### Hook Testing
```powershell
# Test hook execution
python ~/.claude/hooks/audio_player.py < test_hook_data.json

# Test hook chain
claude "Execute a test command to trigger the hook chain"
```

#### Slash Command Testing
```powershell
# Test basic command
claude "/project-status"

# Test complex command
claude "/new-project 'Test project for verification'"
```

#### MCP Testing
```powershell
# Test Playwright MCP
claude "Use playwright to navigate to https://example.com and tell me the page title"

# Test Obsidian MCP (requires Obsidian running)
claude "Use obsidian to list all files in the vault"

# Test Web-search MCP
claude "Use web-search to find information about Claude Code"
```

#### Audio Testing
```powershell
# Test audio playback
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py

# Test context-aware audio
echo '{"hook_event_name": "Stop", "context": {"model": "claude-3-opus"}}' | python ~/.claude/hooks/audio_player.py
```

#### Mobile Testing
```powershell
# Launch mobile interface
.\platform-tools\windows\mobile\launch-mobile-remote.ps1

# Test mobile connectivity
# Open browser to http://localhost:8080
# Verify real-time status updates
# Test command execution from mobile
```

### Performance Testing

#### System Performance Verification
```powershell
# Monitor system resources during operation
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Select-Object ProcessName, CPU, WS | Sort-Object WS -Descending

# Expected resource usage:
# Total CPU: <80%
# Total Memory: <4GB
# Response time: <2s for most operations
```

#### Load Testing
```powershell
# Test parallel agent execution
# Run multiple commands simultaneously
claude "/new-project 'Test Project 1'" &
claude "/business-analysis" &
claude "/technical-feasibility 'Test system'" &

# Monitor system stability
# Verify all commands complete successfully
```

---

## Attribution & Third-Party Setup

### 🏆 Third-Party Component Setup

The Claude Code Dev Stack v3.0 integrates several excellent open-source projects. Here's how to set up the attributed components:

#### Claude Code Browser (@zainhoda)
```bash
# Clone original repository
git clone https://github.com/zainhoda/claude-code-browser.git /tmp/claude-code-browser

# Copy to integration directory
cp -r /tmp/claude-code-browser/* ~/.claude/integrations/browser/

# Install dependencies
cd ~/.claude/integrations/browser
npm install

# Configure for Dev Stack integration
cp config/devstack-integration.json config/local.json
```

#### 9cat Mobile App (@9cat)
```bash
# Clone original mobile app
git clone https://github.com/9cat/claude-code-app.git /tmp/claude-code-app

# Copy mobile components
cp -r /tmp/claude-code-app/* ~/.claude/integrations/mobile/

# Install Flutter dependencies (if developing mobile app)
cd ~/.claude/integrations/mobile
flutter pub get
```

#### MCP Manager (@qdhenry)
```bash
# Clone MCP Manager
git clone https://github.com/qdhenry/Claude-Code-MCP-Manager.git /tmp/mcp-manager

# Copy to integration directory
cp -r /tmp/mcp-manager/* ~/.claude/integrations/mcp-manager/

# Setup PowerShell wrapper
./setup-mcp-manager-integration.ps1
```

#### Claude Powerline (@Owloops)
```bash
# Install globally via npm
npm install -g @owloops/claude-powerline

# Configure for Dev Stack integration
mkdir -p ~/.claude/powerline
cp config/powerline-devstack.json ~/.claude/powerline/config.json

# Test integration
npx @owloops/claude-powerline --config ~/.claude/powerline/config.json
```

### 📝 License Compliance Verification

#### Verify All Licenses Present
```powershell
# Check LICENSE-THIRD-PARTY directory
Get-ChildItem ./LICENSE-THIRD-PARTY/ | Select-Object Name

# Expected files:
# LICENSE-claude-code-browser (AGPL-3.0)
# LICENSE-9cat-mobile (MIT)
# LICENSE-mcp-manager (MIT)
# LICENSE-openapi-codegen (Apache-2.0)
# LICENSE-openapi-generator (MIT)
# LICENSE-claude-powerline (MIT)
# LICENSE-cc-statusline (MIT)
```

#### Attribution Verification
```powershell
# Verify CREDITS.md exists and is complete
Get-Content ./CREDITS.md | Select-String "Original Author"

# Verify README attribution
Get-Content ./README.md | Select-String "Built With"

# Check for attribution in source files
Get-ChildItem -Recurse -Include "*.py","*.js","*.md" | 
    Select-String "Original.*Author|@zainhoda|@9cat|@qdhenry|@Owloops|@chongdashu"
```

---

## Troubleshooting

### 🚨 Common Installation Issues

#### Issue: "claude" command not found
```powershell
# Solution: Verify Claude Code installation
# Download from: https://claude.ai/code
# Add to PATH: $env:PATH += ";C:\Program Files\Claude Code"

# Test Claude Code installation
claude --version
```

#### Issue: Agents not appearing after installation
```powershell
# Solution: Check agent directory and permissions
Get-ChildItem ~/.claude/agents/ | Measure-Object

# If count != 28, reinstall
.\platform-tools\windows\installers\install-agents.ps1 -Force

# Check file permissions
icacls ~/.claude/agents/*.md
```

#### Issue: Hooks not triggering
```powershell
# Solution: Verify settings.json configuration
Get-Content ~/.claude/settings.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Check hook file permissions
Get-ChildItem ~/.claude/hooks/*.py | ForEach-Object { python $_.FullName --test }

# Reinstall hooks if needed
.\platform-tools\windows\installers\install-hooks.ps1 -Force
```

#### Issue: MCP servers not connecting
```powershell
# Solution: Check MCP server status
claude mcp list

# Check individual server logs
Get-Content "$env:LOCALAPPDATA\Claude\logs\mcp-*.log" -Tail 20

# Test server connectivity
claude mcp status playwright
claude mcp status obsidian
claude mcp status web-search

# Reinstall problematic MCPs
claude mcp remove playwright
.\platform-tools\windows\installers\install-mcps.ps1 -Servers @("playwright")
```

#### Issue: Audio not playing
```powershell
# Solution: Test audio system components
# Check audio files exist
Get-ChildItem ~/.claude/audio/*.mp3 | Measure-Object

# Test audio player directly
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py

# Check Windows audio configuration
Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status

# Reinstall audio system
.\platform-tools\windows\installers\install-audio.ps1 -Force
```

#### Issue: Mobile interface not accessible
```powershell
# Solution: Check mobile server status
Test-NetConnection -ComputerName localhost -Port 8080

# Check firewall settings
Get-NetFirewallRule -DisplayName "*Claude*" | Select-Object DisplayName, Enabled

# Restart mobile interface
.\platform-tools\windows\mobile\launch-mobile-remote.ps1 -Force

# Check for port conflicts
netstat -ano | Select-String ":8080"
```

### 🔧 Advanced Troubleshooting

#### Complete System Reset
```powershell
# Backup current configuration
Copy-Item ~/.claude ~/.claude-backup-$(Get-Date -Format "yyyyMMdd-HHmm") -Recurse

# Complete uninstallation
.\platform-tools\windows\uninstallers\uninstall-all.ps1

# Clean installation
.\platform-tools\windows\installers\install-all.ps1

# Restore custom settings if needed
# Copy-Item ~/.claude-backup-*/custom-settings.json ~/.claude/
```

#### Diagnostic Information Collection
```powershell
# System information
Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory

# Claude Code version
claude --version

# Node.js and Python versions
node --version
python --version

# Disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, FreeSpace, Size

# Network connectivity
Test-NetConnection -ComputerName api.anthropic.com -Port 443

# Process information
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Select-Object ProcessName, CPU, WS, StartTime
```

#### Log Analysis
```powershell
# View all Claude Code logs
Get-ChildItem "$env:LOCALAPPDATA\Claude\logs\" | Sort-Object LastWriteTime -Descending

# Real-time log monitoring
Get-Content "$env:LOCALAPPDATA\Claude\logs\claude.log" -Wait -Tail 10

# Error pattern detection
Get-Content "$env:LOCALAPPDATA\Claude\logs\*.log" | 
    Select-String "ERROR|FATAL|Exception" | 
    Select-Object -Last 20
```

---

## Advanced Configuration

### 🔧 Custom Configuration Options

#### Settings.json Configuration
```json
{
  "version": "3.0.0",
  "agents": {
    "max_parallel": 5,
    "timeout": 300,
    "retry_count": 3,
    "performance_mode": "balanced"
  },
  "hooks": {
    "execution_timeout": 30,
    "chain_max_depth": 10,
    "error_handling": "graceful"
  },
  "audio": {
    "enabled": true,
    "volume": 0.8,
    "context_aware": true,
    "model_specific": true
  },
  "mobile": {
    "enabled": true,
    "port": 8080,
    "ssl": false,
    "max_devices": 10
  },
  "status_line": {
    "update_frequency": 100,
    "history_retention": 86400,
    "real_time": true
  }
}
```

#### Environment Variables
```powershell
# Set Claude Code Dev Stack environment variables
$env:CLAUDE_CODE_DEVSTACK_VERSION = "3.0.0"
$env:CLAUDE_CODE_DEVSTACK_HOME = "$env:USERPROFILE\.claude"
$env:CLAUDE_CODE_AGENTS_PATH = "$env:USERPROFILE\.claude\agents"
$env:CLAUDE_CODE_HOOKS_PATH = "$env:USERPROFILE\.claude\hooks"
$env:CLAUDE_CODE_AUDIO_PATH = "$env:USERPROFILE\.claude\audio"
$env:CLAUDE_CODE_MOBILE_PORT = "8080"

# Obsidian integration
$env:OBSIDIAN_API_KEY = "your_api_key_here"
$env:OBSIDIAN_HOST = "127.0.0.1"
$env:OBSIDIAN_PORT = "27124"
```

#### Performance Optimization
```powershell
# High-performance configuration
# Increase parallel agent limit
# Edit ~/.claude/settings.json
# Set "max_parallel": 10

# Optimize memory usage
# Set "memory_optimization": true

# Enable aggressive caching
# Set "cache_enabled": true
# Set "cache_size": "1GB"

# Configure SSD optimizations
# Set "storage_optimization": "ssd"
```

### 🎛️ Developer Customization

#### Custom Agent Development
```python
# Create custom agent template
# File: ~/.claude/agents/custom-agent-template.md
"""
---
name: agent-custom-template
description: Template for creating custom agents
tools: Read, Write, Edit, Bash, Grep, Glob
tier: 5
category: custom
---

# Custom Agent Template

This is a template for creating custom agents in the Claude Code Dev Stack.

## Capabilities
- Custom functionality
- Integration with existing agents
- Access to all development tools

## Usage Patterns
Invoke with: @agent-custom-template
"""
```

#### Custom Hook Development
```python
# Create custom hook
# File: ~/.claude/hooks/custom_hook.py

import json
import sys
from pathlib import Path

class CustomHook:
    def __init__(self):
        self.name = "custom_hook"
        self.version = "1.0.0"
        
    def execute(self, event_data):
        """Execute custom hook logic"""
        try:
            # Custom hook implementation
            result = self.process_event(event_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_event(self, event_data):
        # Implement custom logic here
        return f"Processed event: {event_data.get('hook_event_name')}"

if __name__ == "__main__":
    hook = CustomHook()
    event_data = json.loads(sys.stdin.read())
    result = hook.execute(event_data)
    print(json.dumps(result))
```

#### Custom Command Development
```markdown
<!-- File: ~/.claude/commands/custom-command.md -->
---
name: custom-command
description: Custom slash command for specialized workflows
category: custom
---

# /custom-command

Custom command for specialized development workflows.

## Usage
`/custom-command "parameters"`

## Implementation
This command triggers a custom workflow involving multiple agents and hooks.
```

### 📊 Monitoring & Analytics

#### Custom Metrics Collection
```python
# File: ~/.claude/monitoring/custom_metrics.py

import json
import time
from pathlib import Path

class MetricsCollector:
    def __init__(self):
        self.metrics_file = Path.home() / ".claude" / "metrics" / "custom.json"
        self.metrics_file.parent.mkdir(exist_ok=True)
        
    def collect_metrics(self):
        metrics = {
            "timestamp": time.time(),
            "agent_performance": self.get_agent_metrics(),
            "hook_performance": self.get_hook_metrics(),
            "system_health": self.get_system_metrics()
        }
        
        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
    
    def get_agent_metrics(self):
        # Collect agent performance metrics
        return {}
    
    def get_hook_metrics(self):
        # Collect hook performance metrics
        return {}
    
    def get_system_metrics(self):
        # Collect system performance metrics
        return {}
```

---

## 🎯 Installation Checklist

### Pre-Installation
- [ ] Verify Claude Code is installed and working
- [ ] Check system meets minimum requirements
- [ ] Ensure internet connectivity
- [ ] Backup existing Claude Code configuration

### Component Installation
- [ ] Install all 28 AI agents
- [ ] Configure 28 automation hooks
- [ ] Setup 18 slash commands
- [ ] Install 3 MCP servers (Playwright, Obsidian, Web-search)
- [ ] Configure audio system with 102+ sounds
- [ ] Setup mobile interface

### Third-Party Integration
- [ ] Clone and attribute Claude Code Browser (@zainhoda)
- [ ] Setup 9cat Mobile App components (@9cat)
- [ ] Configure MCP Manager (@qdhenry)
- [ ] Install Claude Powerline (@Owloops)
- [ ] Verify all attribution and licensing

### Testing & Verification
- [ ] Run complete system verification script
- [ ] Test agent routing and execution
- [ ] Verify hook triggering and chaining
- [ ] Test all slash commands
- [ ] Verify MCP server connectivity
- [ ] Test audio system functionality
- [ ] Verify mobile interface accessibility

### Post-Installation
- [ ] Configure custom settings if needed
- [ ] Set up monitoring and logging
- [ ] Create backup of working configuration
- [ ] Review documentation and usage guides

---

*Claude Code Dev Stack v3.0 Installation Guide - Complete Setup with Full Attribution*

**All third-party components properly credited to original authors:**
- @zainhoda (Claude Code Browser)
- @9cat (Mobile App)
- @qdhenry (MCP Manager)
- @Owloops (Claude Powerline)
- @chongdashu (CC-Statusline)

Last Updated: January 16, 2025