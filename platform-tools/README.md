# Platform Tools

OS-specific installers, uninstallers, and verification scripts for Claude Code Dev Stack v2.1.

## 📁 Structure

```
platform-tools/
├── windows/          # PowerShell scripts
├── linux/           # Bash scripts for Linux/WSL
└── macos/           # macOS-specific scripts
```

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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-agents-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-commands-mac.sh | bash
```

#### 3️⃣ Hooks Only (13 Automation Hooks)

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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-hooks-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-mcps-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/verifiers/verify-installation-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-all-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-agents-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-commands-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-hooks-mac.sh | bash
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
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-mcps-mac.sh | bash
```

## 📦 Tool Categories

### Installers
- `install-all` - Complete stack installation (28 agents + 18 commands + 13 hooks + MCP configs)
- `install-agents` - 28 AI agents only
- `install-commands` - 18 slash commands only
- `install-hooks` - 13 automation hooks only (requires Python)
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

## 🔗 Related Documentation
- [Installation Guide](../docs/getting-started/INSTALLATION.md)
- [Component Reference](../docs/reference/)
- [Main README](../README.md)