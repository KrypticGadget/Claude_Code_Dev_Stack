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

- **Enhanced Hook System**: 19 hooks with full agent orchestration
- **Audio Notifications**: Context-aware sound feedback
- **MCP Integration**: Playwright, Obsidian, and Web-search servers
- **Session Persistence**: Full state preservation between sessions
- **Backup System**: Automatic backups before uninstallation

## ⚡ One-Liner Commands

### 🚀 Complete Installation (All Components)

#### Windows PowerShell
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1 | iex
```

#### Linux/WSL
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash
```

#### macOS
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all.sh | bash
```

### 📦 Individual Component Installation

#### 1️⃣ Agents Only (28 AI Agents)

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-agents.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-agents.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-agents.sh | bash
```

#### 2️⃣ Commands Only (18 Slash Commands)

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-commands.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-commands.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-commands.sh | bash
```

#### 3️⃣ Hooks Only (19 Enhanced Hooks + Audio)

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-hooks.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-hooks.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-hooks.sh | bash
```

#### 4️⃣ MCP Configs Only (Model Context Protocol)

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-mcps.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-mcps.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-mcps.sh | bash
```

### ✅ Verification

#### Windows PowerShell
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/verifiers/verify-installation.ps1 | iex
```

#### Linux/WSL
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/verifiers/verify-installation.sh | bash
```

#### macOS
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/verifiers/verify-installation.sh | bash
```

### 🗑️ Complete Uninstallation (All Components)

#### Windows PowerShell
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-all.ps1 | iex
```

#### Linux/WSL
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-all.sh | bash
```

#### macOS
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-all.sh | bash
```

### 🧹 Individual Component Uninstallation

#### 1️⃣ Uninstall Agents Only

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-agents.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-agents.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-agents.sh | bash
```

#### 2️⃣ Uninstall Commands Only

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-commands.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-commands.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-commands.sh | bash
```

#### 3️⃣ Uninstall Hooks Only

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-hooks.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-hooks.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-hooks.sh | bash
```

#### 4️⃣ Uninstall MCP Configs Only

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-mcps.ps1 | iex
```

**Linux/WSL:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-mcps.sh | bash
```

**macOS:**
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-mcps.sh | bash
```

## 📦 Tool Categories

### Installers
- `install-all` - Complete stack installation (28 agents + 18 commands + 19 enhanced hooks + MCP configs)
- `install-agents` - 28 AI agents only
- `install-commands` - 18 slash commands only
- `install-hooks` - 19 enhanced hooks with audio notifications (requires Python)
- `install-mcps` - MCP configuration files only

### Uninstallers
- `uninstall-all` - Remove everything (with confirmation)
- `uninstall-agents` - Remove agents only
- `uninstall-commands` - Remove commands only
- `uninstall-hooks` - Remove hooks only
- `uninstall-mcps` - Remove MCP configs only

### Verifiers
- `verify-installation` - Check installation status
- Reports on all 4 stack components
- Shows file counts and missing elements
- Checks Python availability for hooks
- Tests hook functionality

### Special Tools

#### Windows MCP Master Setup
For complete MCP server installation and configuration:
```powershell
# Install and configure all MCP servers
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mcp/master-mcp-setup.ps1 | iex

# Or download and run with options:
./master-mcp-setup.ps1 -ObsidianApiKey "your-api-key" -Test
```

## 🔗 Related Documentation
- [Installation Guide](../docs/getting-started/INSTALLATION.md)
- [Component Reference](../docs/reference/)
- [Main README](../README.md)