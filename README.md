# Claude Code Dev Stack V3.7.12

AI-powered development environment with 28 specialized agents, intelligent hooks, unified tooling, and real-time statusline.

## 🚀 Quick Install

### From npm (Latest v3.7.12)
```bash
npm install -g claude-code-dev-stack@latest
```

### From GitHub (Development)
```bash
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#main
```

### One-line Installers
**Linux/Mac:**
```bash
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/feature/v3-dev/install.sh | bash
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/feature/v3-dev/install.ps1 | iex
```

## ✨ What Gets Installed

- ✅ **28 Specialized AI Agents** - Architecture, development, DevOps, QA, and more
- ✅ **37 Intelligent Hooks** - Automated workflows and orchestration
- ✅ **90+ Audio Files** - Rich audio feedback system
- ✅ **Real-time Statusline** - Live context awareness (v3.7.12)
- ✅ **Unified React PWA** - Beautiful dashboard interface
- ✅ **MCP Servers** - code-sandbox, GitHub, Playwright integration
- ✅ **Claude Code Integration** - Seamless hooks and agent routing

## 🛠️ Commands

After installation, you'll have access to:

```bash
# Main setup command (includes statusline configuration)
ccds-setup

# List and manage agents
ccds-agents list

# List and manage hooks  
ccds-hooks list

# Test statusline
python ~/.claude/hooks/test_statusline.py

# Start the PWA dashboard
cd ~/.claude/ui && npm run dev
```

## 🎯 Quick Start

1. **Install the stack:**
   ```bash
   npm install -g claude-code-dev-stack@latest
   ```

2. **Run setup (configures statusline and hooks):**
   ```bash
   ccds-setup
   ```

3. **Test the statusline:**
   ```bash
   python ~/.claude/hooks/test_statusline.py
   ```

4. **View your setup:**
   ```bash
   ccds-agents list
   ccds-hooks list
   ```

5. **The statusline will appear automatically when you launch Claude Code!**

## 🏗️ Architecture

```
Claude Code Dev Stack V3/
├── 🤖 28 AI Agents          # Specialized development agents
├── 🪝 37 Smart Hooks        # Automated workflow triggers
├── 🔊 90+ Audio Files       # Rich feedback system
├── 🎨 Unified PWA           # React dashboard interface
├── 🔌 MCP Integration       # External tool connections
└── ⚙️  Claude Code Config   # Seamless integration
```

## 📊 Features

- **Real-time Statusline** (v3.7.12) - Live display of model, git, phase, agents, tokens
- **Agent Orchestration** - Smart routing and task delegation
- **Audio Feedback** - Rich audio notifications for all actions
- **Performance Monitoring** - Real-time metrics and optimization
- **Security Scanning** - Automated security checks and validation
- **Auto-Documentation** - Intelligent documentation generation
- **Quality Gates** - Automated quality control and validation

## 🔧 Requirements

- Node.js 18+
- npm 8+
- Claude Code (for full integration)

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Agent Reference](docs/agents.md)
- [Hook Reference](docs/hooks.md)
- [PWA Guide](docs/pwa.md)

## 🐛 Issues & Support

- [GitHub Issues](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues)
- [Discussions](https://github.com/KrypticGadget/Claude_Code_Dev_Stack/discussions)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the Claude Code Community**