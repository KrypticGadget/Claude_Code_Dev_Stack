# Platform Tools

OS-specific installers, uninstallers, and verification scripts for Claude Code Dev Stack v2.1.

## 📁 Structure

```
platform-tools/
├── windows/          # PowerShell scripts
├── linux/           # Bash scripts for Linux/WSL
└── macos/           # macOS-specific scripts
```

## ⚡ Quick Installation

### Windows PowerShell
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1 | iex
```

### Linux/WSL
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash
```

### macOS
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all-mac.sh | bash
```

## 📦 Tool Categories

### Installers
- `install-all` - Complete stack installation
- `install-agents` - 28 AI agents only
- `install-commands` - 18 slash commands only
- `install-hooks` - 13 automation hooks only
- `install-mcps` - 3 MCP tools only

### Uninstallers
- `uninstall-all` - Remove everything
- Component-specific uninstallers with same pattern

### Verifiers
- `verify-installation` - Check installation status
- Reports on all 4 stack components
- Identifies missing elements

## 🔗 Related Documentation
- [Installation Guide](../docs/getting-started/INSTALLATION.md)
- [Component Reference](../docs/reference/)
- [Main README](../README.md)