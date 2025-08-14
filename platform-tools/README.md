# Platform Tools

OS-specific installers, uninstallers, and mobile access tools for Claude Code Dev Stack V3.0+ with Complete Automation & Mobile Monitoring.

## 📁 Structure

```
platform-tools/
├── windows/          # PowerShell scripts (.ps1)
│   ├── installers/   # Component installers
│   ├── uninstallers/ # Component removers
│   ├── verifiers/    # Installation checkers
│   ├── mobile/       # 📱 Mobile access launchers
│   └── mcp/          # MCP server setup
├── linux/            # Bash scripts for Linux/WSL
│   ├── installers/   # Component installers
│   ├── uninstallers/ # Component removers
│   ├── verifiers/    # Installation checkers
│   └── mobile/       # 📱 Mobile access launchers
└── macos/            # macOS-specific scripts
    ├── installers/   # Component installers
    ├── uninstallers/ # Component removers
    ├── verifiers/    # Installation checkers
    └── mobile/       # 📱 Mobile access launchers
```

## 🌟 What's New in V3.0+

- **📱 Mobile Access**: One-liner Samsung Galaxy S25 Edge dashboard access
- **🤖 28 V3+ Enhanced Agents**: Smart orchestration with 4x parallel execution
- **🔧 28 Advanced Hooks**: Complete automation with quality tools & notifications
- **🔊 102 Audio Files**: Phase-aware notifications with mobile push integration
- **🔐 Enterprise Security**: Token authentication, tunnels, session management
- **📊 Real-Time Dashboard**: Mobile-optimized monitoring with QR code access
- **🚇 Auto-Fallback Tunnels**: ngrok/Cloudflare with intelligent provider selection
- **⚡ Performance Optimized**: <750 lines per agent, 80% token reduction
- **🛡️ Quality Tools**: Multi-language linting, security scanning, git hooks

---

# 🪟 Windows PowerShell

## 🚀 **Installers**

### Complete Installation (All V3+ Components)
```powershell
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1" -UseBasicParsing | iex
```

### 📱 Mobile Access (Samsung Galaxy S25 Edge)
```powershell
# One-liner mobile dashboard access with secure tunnels
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mobile/launch-mobile-remote.ps1" -UseBasicParsing | iex
```

### Individual Components
```powershell
# 28 V3+ Enhanced AI Agents
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-agents.ps1" -UseBasicParsing | iex

# 20+ Slash Commands
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-commands.ps1" -UseBasicParsing | iex

# 28 Advanced Hooks + Quality Tools + V3+ Settings
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-hooks.ps1" -UseBasicParsing | iex

# MCP Configurations + Playwright + Web Search
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-mcps.ps1" -UseBasicParsing | iex
```

## 🗑️ **Uninstallers**

### Complete Uninstall (All Components)
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-all.ps1 | iex
```

### Individual Components
```powershell
# Remove Agents
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-agents.ps1 | iex

# Remove Commands
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-commands.ps1 | iex

# Remove Hooks
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-hooks.ps1 | iex

# Remove MCP Configs
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-mcps.ps1 | iex
```

## ✅ **Verifier**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/verifiers/verify-installation.ps1 | iex
```

## 🔧 **Special Tools**

### MCP Master Setup
```powershell
# Complete MCP server installation
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mcp/master-mcp-setup.ps1 | iex

# Or download and run with options:
./master-mcp-setup.ps1 -ObsidianApiKey "your-api-key" -Test
```

---

# 🐧 Linux/WSL

## 🚀 **Installers**

### Complete Installation (All V3+ Components)
```bash
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash
```

### 📱 Mobile Access (Samsung Galaxy S25 Edge)
```bash
# One-liner mobile dashboard access with secure tunnels
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/mobile/launch-mobile-remote.sh | bash
```

### Individual Components
```bash
# 28 V3+ Enhanced AI Agents
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-agents.sh | bash

# 20+ Slash Commands
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-commands.sh | bash

# 28 Advanced Hooks + Quality Tools + V3+ Settings
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-hooks.sh | bash

# MCP Configurations + Playwright + Web Search
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-mcps.sh | bash
```

## 🗑️ **Uninstallers**

### Complete Uninstall (All Components)
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-all.sh | bash
```

### Individual Components
```bash
# Remove Agents
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-agents.sh | bash

# Remove Commands
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-commands.sh | bash

# Remove Hooks
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-hooks.sh | bash

# Remove MCP Configs
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-mcps.sh | bash
```

## ✅ **Verifier**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/verifiers/verify-installation.sh | bash
```

---

# 🍎 macOS

## 🚀 **Installers**

### Complete Installation (All V3+ Components)
```bash
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all.sh | bash
```

### 📱 Mobile Access (Samsung Galaxy S25 Edge)
```bash
# One-liner mobile dashboard access with secure tunnels
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/mobile/launch-mobile-remote.sh | bash
```

### Individual Components
```bash
# 28 V3+ Enhanced AI Agents
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-agents.sh | bash

# 20+ Slash Commands
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-commands.sh | bash

# 28 Advanced Hooks + Quality Tools + V3+ Settings
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-hooks.sh | bash

# MCP Configurations + Playwright + Web Search
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-mcps.sh | bash
```

## 🗑️ **Uninstallers**

### Complete Uninstall (All Components)
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-all.sh | bash
```

### Individual Components
```bash
# Remove Agents
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-agents.sh | bash

# Remove Commands
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-commands.sh | bash

# Remove Hooks
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-hooks.sh | bash

# Remove MCP Configs
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-mcps.sh | bash
```

## ✅ **Verifier**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/verifiers/verify-installation.sh | bash
```

---

## 📦 Component Details

### **What Gets Installed**

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 28 | V3+ Enhanced AI specialists with smart orchestration |
| **Commands** | 20+ | Advanced slash commands for instant workflows |
| **Hooks** | 28 | Complete automation with quality tools & mobile integration |
| **MCPs** | 4 | Playwright, Web-search, GitHub, Obsidian configurations |
| **Audio** | 102 | Phase-aware notifications with mobile push sync |
| **Mobile** | 3 | Cross-platform mobile access launchers |
| **Dashboard** | 1 | Real-time web monitoring with Samsung Galaxy S25 Edge optimization |
| **Tunnels** | 2 | Secure remote access with auto-fallback (ngrok/Cloudflare) |
| **Settings** | 1 | Complete V3+ integrated configuration |

### **Installation Locations**
- **Windows**: `C:\Users\[Username]\.claude\`
- **Linux/WSL**: `~/.claude/`
- **macOS**: `~/.claude/`

### **Requirements**
- **Python 3.7+**: Required for hooks, mobile access, dashboard, quality tools
- **Node.js 16+**: Required for MCP servers (Playwright, Web-search, GitHub)
- **Internet Connection**: Required for GitHub downloads and tunnel setup
- **Mobile Device**: Samsung Galaxy S25 Edge optimized (works on any modern smartphone)
- **Audio System**: Optional but recommended for phase-aware notifications

---

## 🔧 Troubleshooting

### 🤖 V3+ System Not Working?
1. **Python Check**: `python --version` (requires 3.7+)
2. **Installation Verification**: Run platform verifier script
3. **Settings Validation**: Check `~/.claude/settings.json` exists
4. **Restart Claude Code**: Reload after installation

### 📱 Mobile Access Issues?
1. **Network Check**: Ensure internet connectivity
2. **Python Dependencies**: `pip install flask flask-socketio qrcode[pil] requests psutil`
3. **Tunnel Setup**: Check ngrok or Cloudflare tokens
4. **QR Code**: Try manual URL if QR scan fails

### 🔧 Quality Tools Not Working?
1. **Linter Installation**: `pip install black flake8 mypy pylint`
2. **Node.js Tools**: `npm install -g eslint prettier`
3. **Git Hooks**: Run `python ~/.claude/hooks/git_quality_hooks.py install`
4. **Permissions**: Ensure write access to project directories

### 🎵 Audio Issues?
1. **Audio System**: Test with `python ~/.claude/audio/test_audio.py`
2. **Volume**: Adjust with `python ~/.claude/audio/calibrate_volume.py`
3. **Dependencies**: Install pygame, sounddevice
4. **Mobile Sync**: Check notification service tokens

### 🚇 Tunnel Failures?
1. **Provider Status**: Check ngrok/Cloudflare service status
2. **Authentication**: Verify API tokens in environment variables
3. **Firewall**: Ensure port 8080 is accessible
4. **Fallback**: System auto-tries multiple providers

### 🔐 Permission Errors?
- **Windows**: Run PowerShell as Administrator
- **Linux/macOS**: Use `sudo` if needed, check file permissions
- **Mobile**: Ensure notification permissions enabled

### 📡 Download Failures?
- **Internet**: Check connectivity and DNS resolution
- **GitHub**: Verify repository availability
- **Rate Limits**: Wait and retry if GitHub rate limited
- **Individual Components**: Try installing components separately

---

## 🔗 Related Documentation

### **📚 Component Documentation**
- [🤖 Agents Guide](../.claude-example/agents/README.md) - 28 V3+ Enhanced AI Agents
- [🔧 Hooks Guide](../.claude-example/hooks/README.md) - 28 Advanced Automation Hooks
- [📊 Dashboard Guide](../.claude-example/dashboard/README.md) - Mobile-Optimized Monitoring
- [🚇 Tunnels Guide](../.claude-example/tunnels/README.md) - Secure Remote Access
- [🔊 Audio Guide](../.claude-example/audio/README.md) - 102 Phase-Aware Notifications
- [📱 Mobile Guide](../.claude-example/mobile/README.md) - Samsung Galaxy S25 Edge Access

### **🔧 Technical Documentation**
- [📋 Installation Guide](../docs/INSTALLATION.md) - Complete V3+ Setup
- [⚙️ Configuration Guide](../docs/CONFIGURATION.md) - Settings & Customization
- [🔒 Security Guide](../docs/SECURITY.md) - Authentication & Best Practices
- [📈 Performance Guide](../docs/PERFORMANCE.md) - Optimization & Monitoring
- [🛠️ Troubleshooting](../docs/TROUBLESHOOTING.md) - Common Issues & Solutions

### **🚀 Getting Started**
- [🏠 Main README](../README.md) - Complete V3+ Overview
- [⚡ Quick Start](../docs/QUICK_START.md) - 5-Minute Setup
- [📱 Mobile Setup](../docs/MOBILE_SETUP.md) - Samsung Galaxy S25 Edge Guide
- [🎯 Use Cases](../docs/USE_CASES.md) - Real-World Examples