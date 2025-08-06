# Installers Directory

One-line installation commands for all platforms.

## 🚀 Quick Install Commands

### All-in-One Installers
- **Windows**: `iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-all.ps1 | iex`
- **Linux**: `curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-all.sh | bash`
- **macOS**: `curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/macos/install-all-mac.sh | bash`

## 📦 Component Installers

Each platform has individual installers:
- `install-agents` - 28 AI agents
- `install-commands` - 18 slash commands
- `install-hooks` - Automation layer
- `install-mcps` - External tools

## 📁 Structure

```
installers/
├── windows/      # PowerShell installers (.ps1)
├── linux/        # Bash installers (.sh)
└── macos/        # macOS-specific installers (.sh)
```

## 🛠️ Features

- **30-second installation** - Optimized for speed
- **Network timeouts** - No more hanging
- **Progress indicators** - See what's happening
- **Error handling** - Clear failure messages
- **Parallel downloads** - Faster installation

## 📝 Individual Component Installation

### Windows
```powershell
# Agents only
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-agents.ps1 | iex

# Commands only
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-commands.ps1 | iex

# Hooks only
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-hooks.ps1 | iex

# MCPs only
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-mcps.ps1 | iex
```

### Linux/WSL
```bash
# Agents only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-agents.sh | bash

# Commands only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-commands.sh | bash

# Hooks only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-hooks.sh | bash

# MCPs only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-mcps.sh | bash
```

### macOS
```bash
# Agents only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/macos/install-agents-mac.sh | bash

# Commands only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/macos/install-commands-mac.sh | bash

# Hooks only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/macos/install-hooks-mac.sh | bash

# MCPs only
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/macos/install-mcps-mac.sh | bash
```

## 🔍 Verification

After installation, verify with:
- **Windows**: Run `verification\verify-installation.ps1`
- **Linux**: Run `verification/verify-installation.sh`
- **macOS**: Run `verification/verify-installation-mac.sh`

## ⚠️ Troubleshooting

If installation fails:
1. Check your internet connection
2. Ensure you have proper permissions
3. Try installing individual components
4. Check the [main documentation](../docs/)