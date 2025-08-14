# Claude Code Dev Stack V3.0+
## The Ultimate AI Development Platform with Remote Monitoring & Quality Tools

<div align="center">

![Version](https://img.shields.io/badge/version-3.0%2B-blue)
![Agents](https://img.shields.io/badge/agents-28-green)
![Audio](https://img.shields.io/badge/audio-102_files-orange)
![Hooks](https://img.shields.io/badge/hooks-28-purple)
![MCP](https://img.shields.io/badge/MCP-integrated-red)

</div>

---

## 🚀 **QUICK START - ONE-LINE INSTALLATION**

### **Windows**
```powershell
# INSTALL EVERYTHING (V3.0+ Complete System)
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1" -UseBasicParsing | iex

# UNINSTALL EVERYTHING
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-all.ps1" -UseBasicParsing | iex
```

### **Linux**
```bash
# INSTALL EVERYTHING (V3.0+ Complete System)
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash

# UNINSTALL EVERYTHING
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-all.sh | bash
```

### **macOS**
```bash
# INSTALL EVERYTHING (V3.0+ Complete System)
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-all.sh | bash

# UNINSTALL EVERYTHING
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-all.sh | bash
```

---

## ✨ **What You Get With V3.0+**

### **Core Features**
- 🤖 **28 V3-Enhanced AI Agents** with automatic orchestration & delegation
- 🔊 **102 Phase-Aware Audio Notifications** (includes 15 new V3+ sounds)
- 📱 **Remote Android/iOS Monitoring** via Pushover & Telegram
- 🎯 **Real-Time Status Line** with 100ms updates
- ⚡ **Parallel Execution Engine** (4x faster operations)
- 🔧 **Code Quality Tools** (multi-language linting & formatting)
- 📊 **Web Monitoring Dashboard** with performance metrics
- 🌐 **MCP Integration** (Browser, Search, GitHub, Obsidian)
- 💾 **Smart Resource Management** (prevents file bloat)
- 📋 **Automatic Documentation** generation

### **V3.0+ Extended Features (NEW)**
- 🔔 **Remote Notifications** - Get alerts on your phone anywhere
- 🛠️ **Quality Gates** - Automatic code linting & formatting
- 📈 **Performance Monitoring** - Track agent execution & token usage
- 🔒 **Security Scanning** - Vulnerability detection
- 🚇 **Tunnel Support** - Remote access via ngrok/Cloudflare
- 📦 **Dependency Management** - Auto-install missing packages
- 🗑️ **Resource Cleanup** - Automatic log rotation & compression
- 📝 **Git Hooks** - Pre-commit quality checks
- 🎨 **Multi-Language Support** - Python, JS, TS, Go, Rust, Java, Ruby, PHP, C++

---

## 🎯 **Quick Test After Installation**

```bash
# Test agent system
@agent-master-orchestrator Build me a full-stack web application

# Test slash commands
/orchestrate-demo

# Test notification system (set tokens first)
export PUSHOVER_TOKEN="your_token"
export PUSHOVER_USER="your_user"
python ~/.claude/hooks/notification_sender.py test

# Test quality tools
python ~/.claude/hooks/code_linter.py project .
```

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                   USER INPUT                             │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│               HOOKS LAYER (28 Hooks)                     │
│  • Status Line  • Context Manager  • Smart Orchestrator  │
│  • Notifications • Linting • Performance • Resources     │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AGENT SYSTEM (28 Agents)                    │
│  Tier 1: Prompt Engineer → Master Orchestrator          │
│  Tier 2: Strategic (Business, Technical, Financial)     │
│  Tier 3: Architecture (Frontend, Backend, Database)     │
│  Tier 4: Implementation (Development, Testing)          │
│  Tier 5: Quality (Security, Performance, DevOps)        │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│               MCP SERVERS (External)                     │
│  • Playwright (Browser)  • Web Search  • GitHub         │
│  • Obsidian (Notes)      • Custom APIs                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 **Remote Monitoring Setup**

### **1. Install Notification Services**
```bash
# Pushover (recommended - $5 one-time)
# 1. Install Pushover app on Android/iOS
# 2. Get API token from pushover.net

# Telegram (free)
# 1. Create bot via @BotFather
# 2. Get bot token and chat ID

# Set environment variables
export PUSHOVER_TOKEN="your_pushover_token"
export PUSHOVER_USER="your_pushover_user"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### **2. Setup Remote Access Tunnel**
```bash
# Option A: ngrok (easiest)
ngrok http 8080

# Option B: Cloudflare Tunnel (free)
cloudflared tunnel create claude-code
cloudflared tunnel run claude-code
```

### **3. Start Dashboard**
```bash
python ~/.claude/dashboard/dashboard_server.py
# Access at: http://localhost:8080 (or via tunnel URL)
```

---

## 🛠️ **Component Installation (Individual)**

### **Windows Components**
```powershell
# Individual installers
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-agents.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-hooks.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-commands.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-mcps.ps1" -UseBasicParsing | iex

# Individual uninstallers
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-agents.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-hooks.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-commands.ps1" -UseBasicParsing | iex
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/uninstallers/uninstall-mcps.ps1" -UseBasicParsing | iex
```

### **Linux Components**
```bash
# Individual installers
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-agents.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-hooks.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-commands.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-mcps.sh | bash

# Individual uninstallers
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-agents.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-hooks.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-commands.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/uninstallers/uninstall-mcps.sh | bash
```

### **macOS Components**
```bash
# Individual installers
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-agents.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-hooks.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-commands.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers/install-mcps.sh | bash

# Individual uninstallers
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-agents.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-hooks.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-commands.sh | bash
curl -sSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/uninstallers/uninstall-mcps.sh | bash
```

---

## 💡 **Slash Commands**

```bash
/orchestrate-demo         # Full V3 orchestration demonstration
/new-project             # Start project with complete orchestration
/business-analysis       # Comprehensive business viability assessment
/technical-feasibility   # Technical architecture evaluation
/full-stack-app         # Build complete application
/test-suite             # Generate comprehensive tests
/security-audit         # Security vulnerability scanning
/performance-optimization # Performance tuning
/mcp-search            # Web search via MCP
/mcp-playwright        # Browser automation
/mcp-github           # GitHub operations
/mcp-obsidian         # Note management
```

---

## 🎨 **Quality Tools Configuration**

### **Supported Languages**
- **Python**: black, flake8, mypy, pylint, bandit
- **JavaScript/TypeScript**: eslint, prettier, tslint
- **Go**: gofmt, golint, go vet
- **Rust**: rustfmt, clippy
- **Java**: checkstyle, google-java-format
- **Ruby**: rubocop
- **PHP**: phpcs, php-cs-fixer
- **C/C++**: clang-format, cpplint

### **Auto-Setup Quality Tools**
```bash
# Install all linters and formatters
pip install black flake8 mypy isort pylint bandit
npm install -g eslint prettier tslint @typescript-eslint/parser
go install golang.org/x/lint/golint@latest
rustup component add rustfmt clippy
gem install rubocop
composer global require friendsofphp/php-cs-fixer
```

---

## 📊 **Performance Metrics**

- **Execution Speed**: 4x faster with parallel agents
- **Token Efficiency**: 80% reduction via context compression
- **Audio Files**: 102 WAV files (~50MB total)
- **System Hooks**: 28 hooks for complete control
- **Agent Count**: 28 specialized agents
- **Languages**: 9+ supported for linting
- **Response Time**: <100ms status updates
- **Resource Usage**: <200MB RAM (with pooling)

---

## 🔧 **Configuration**

### **Settings Location**
```
~/.claude/settings.json
```

### **Key Settings**
```json
{
  "v3Features": {
    "statusLine": { "enabled": true, "updateInterval": 100 },
    "contextManager": { "tokenWarning": 0.8, "tokenCritical": 0.9 },
    "parallelExecution": { "maxWorkers": 4 }
  },
  "v3ExtendedFeatures": {
    "notifications": { "enabled": true },
    "qualityTools": { "autoFormat": true, "lintOnSave": true },
    "monitoring": { "dashboard": true, "port": 8080 }
  }
}
```

---

## 📚 **Documentation**

- [Installation Guide](docs/INSTALLATION.md)
- [V3 Extended Features](V3_EXTENDED_FEATURES.md)
- [Remote Access Setup](docs/REMOTE_ACCESS_SETUP.md)
- [Android Setup Guide](docs/ANDROID_SETUP.md)
- [Quality Tools Guide](docs/QUALITY_TOOLS.md)
- [API Documentation](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🐛 **Troubleshooting**

### **Common Issues**

**Audio not playing?**
```bash
# Test audio system
powershell ~/.claude/audio/test_audio.ps1
```

**Notifications not working?**
```bash
# Test notifications
python ~/.claude/hooks/notification_sender.py test
```

**Playwright browser locked?**
```bash
# Fix browser locks
powershell ~/fix-playwright.ps1
```

**High resource usage?**
```bash
# Run resource cleanup
python ~/.claude/hooks/resource_monitor.py cleanup
```

**Linting not working?**
```bash
# Check linter installation
python ~/.claude/hooks/code_linter.py check
```

---

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Areas for Contribution**
- New agent templates
- Additional language support for linting
- MCP server integrations
- Dashboard UI improvements
- Mobile app development

---

## 📈 **Version History**

- **V3.0+** (Current) - Remote monitoring, quality tools, 102 audio files, 28 hooks
- **V3.0** - Smart orchestration, parallel execution, 87 audio files
- **V2.1** - Enhanced agents, MCP integration
- **V2.0** - Multi-agent system
- **V1.0** - Initial release

---

## 🎯 **Component Summary**

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 28 | Specialized AI agents with V3 orchestration |
| **Hooks** | 28 | System automation & monitoring (was 19, +9 new) |
| **Audio Files** | 102 | Phase-aware notifications (was 87, +15 new) |
| **Slash Commands** | 20+ | Quick access commands |
| **MCP Servers** | 4 | External integrations |
| **Languages** | 9+ | Supported for quality tools |
| **Notification Channels** | 3 | Pushover, Telegram, Webhook |

---

## 📄 **License**

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- Anthropic for Claude AI
- Microsoft for Edge-TTS
- All open-source contributors

---

<div align="center">

**Built with ❤️ for the AI Development Community**

[Report Issues](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues) | 
[Request Features](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues) | 
[Star on GitHub](https://github.com/KrypticGadget/Claude_Code_Dev_Stack)

</div>