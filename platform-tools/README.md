# Platform Tools

OS-specific installers, uninstallers, and verification scripts for Claude Code Dev Stack v2.1 with Enhanced Hook System.

## 📁 Structure

```
platform-tools/
├── windows/          # PowerShell scripts (.ps1)
│   ├── installers/   # Component installers
│   ├── uninstallers/ # Component removers
│   ├── verifiers/    # Installation checkers
│   └── mcp/          # MCP server setup
├── linux/            # Bash scripts for Linux/WSL
│   ├── installers/   # Component installers
│   ├── uninstallers/ # Component removers
│   └── verifiers/    # Installation checkers
└── macos/            # macOS-specific scripts
    ├── installers/   # Component installers
    ├── uninstallers/ # Component removers
    └── verifiers/    # Installation checkers
```

## 🆕 What's New in v2.1

- **Enhanced Hook System**: 19 hooks with complete settings.json configuration
- **Audio Notifications**: Context-aware sound feedback
- **MCP Integration**: Playwright, Obsidian, and Web-search servers
- **Session Persistence**: Full state preservation between sessions
- **Complete Settings**: Hooks + Agents + Commands in unified configuration

---

# 🪟 Windows PowerShell

## 🚀 **Installers**

### Complete Installation (All Components)
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1 | iex
```

### Individual Components
```powershell
# 28 AI Agents
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-agents.ps1 | iex

# 18 Slash Commands
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-commands.ps1 | iex

# 19 Enhanced Hooks + Complete Settings
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-hooks.ps1 | iex

# MCP Configurations
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-mcps.ps1 | iex
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

### Complete Installation (All Components)
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash
```

### Individual Components
```bash
# 28 AI Agents
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-agents.sh | bash

# 18 Slash Commands
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-commands.sh | bash

# 19 Enhanced Hooks + Complete Settings
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-hooks.sh | bash

# MCP Configurations
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-mcps.sh | bash
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

### Complete Installation (All Components)
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all.sh | bash
```

### Individual Components
```bash
# 28 AI Agents
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-agents.sh | bash

# 18 Slash Commands
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-commands.sh | bash

# 19 Enhanced Hooks + Complete Settings
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-hooks.sh | bash

# MCP Configurations
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-mcps.sh | bash
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
| **Agents** | 28 | AI specialists for every development task |
| **Commands** | 18 | Slash commands for instant workflows |
| **Hooks** | 19 | Automation hooks with complete settings.json |
| **MCPs** | 3 | Playwright, Obsidian, Web-search configurations |
| **Audio** | 5 | Notification sounds for task completion |
| **Settings** | 1 | Complete integrated configuration file |

### **Installation Locations**
- **Windows**: `C:\Users\[Username]\.claude\`
- **Linux/WSL**: `~/.claude/`
- **macOS**: `~/.claude/`

### **Requirements**
- **Hooks**: Python 3.x required (hooks won't work without Python)
- **MCPs**: Node.js required for server functionality
- **Audio**: Optional (placeholders created if files not found)

---

## 🔧 Troubleshooting

### Hooks Not Working?
1. Verify Python is installed: `python --version` or `python3 --version`
2. Check settings.json has hook configuration
3. Run verifier script to check installation
4. Restart Claude Code after installation

### Permission Errors?
- **Windows**: Run PowerShell as Administrator
- **Linux/macOS**: Use `sudo` if needed

### Download Failures?
- Check internet connection
- Try downloading individual components
- Check GitHub repository availability

---

## 🔗 Related Documentation
- [Installation Guide](../docs/getting-started/INSTALLATION.md)
- [Component Reference](../docs/reference/)
- [Hooks Guide](../docs/reference/HOOKS_GUIDE.md)
- [Main README](../README.md)