# Claude Code Dev Stack V3

[![npm version](https://badge.fury.io/js/%40claude-code%2Fdev-stack.svg)](https://badge.fury.io/js/%40claude-code%2Fdev-stack)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org)

> AI-powered development environment with 28 specialized agents, 37 intelligent hooks, and unified tooling

## ✨ Features

- 🤖 **28 Specialized AI Agents** - Expert agents for every aspect of development
- 🪝 **37 Intelligent Hooks** - Automated workflows and smart triggers  
- 🔊 **90+ Audio Feedback Files** - Rich audio notifications for all system events
- 🎨 **Unified React PWA** - Beautiful dashboard for visual management
- ⚡ **Smart Orchestration** - Intelligent agent coordination and task routing
- 📊 **Performance Monitoring** - Real-time system metrics and optimization
- 🔒 **Security Scanning** - Built-in security validation and vulnerability detection
- 📚 **Auto-Documentation** - Automatic documentation generation and updates

## 🚀 Quick Start

### Installation

```bash
# Install globally
npm install -g @claude-code/dev-stack

# Initialize the system
claude-code-setup

# Or run interactive setup
claude-code-setup --interactive
```

### Basic Usage

```bash
# List available agents
claude-code-agents list

# Install all agents
claude-code-agents install --all

# List available hooks
claude-code-hooks list

# Install all hooks
claude-code-hooks install --all

# Start the UI dashboard
npm run dev
```

## 📦 What's Included

### 🤖 Specialized Agents (28 Total)

**Architecture & Design**
- `backend-services` - Backend Services Architecture Specialist
- `frontend-architecture` - Frontend Architecture Specialist
- `database-architecture` - Database Architecture Specialist
- `security-architecture` - Security Architecture Specialist
- `technical-specifications` - Technical Specifications Specialist

**Development & Engineering**
- `api-integration-specialist` - API Integration Specialist
- `middleware-specialist` - Middleware Development Specialist
- `mobile-development` - Mobile Development Specialist
- `performance-optimization` - Performance Optimization Specialist
- `production-frontend` - Production Frontend Specialist

**DevOps & Infrastructure**
- `devops-engineering` - DevOps Engineering Specialist
- `integration-setup` - Integration Setup Specialist
- `script-automation` - Script Automation Specialist
- `testing-automation` - Testing Automation Specialist

**Quality & Management**
- `quality-assurance` - Quality Assurance Specialist
- `project-manager` - Project Management Specialist
- `master-orchestrator` - Master Orchestrator Agent
- `business-analyst` - Business Analysis Specialist

**Leadership & Strategy**
- `ceo-strategy` - CEO Strategy Specialist
- `technical-cto` - Technical CTO Specialist
- `business-tech-alignment` - Business-Tech Alignment Specialist
- `financial-analyst` - Financial Analysis Specialist

**User Experience & Design**
- `ui-ux-design` - UI/UX Design Specialist
- `frontend-mockup` - Frontend Mockup Specialist
- `prompt-engineer` - Prompt Engineering Specialist
- `usage-guide` - Usage Guide Specialist
- `development-prompt` - Development Prompt Specialist

### 🪝 Intelligent Hooks (37 Total)

**Core Orchestration**
- `master_orchestrator` - Master orchestration and workflow management
- `smart_orchestrator` - Intelligent agent routing and task distribution
- `v3_orchestrator` - Version 3 orchestration engine
- `orchestration_enhancer` - Enhanced orchestration capabilities
- `agent_enhancer_v3` - Agent enhancement and optimization

**Audio & Feedback**
- `audio_controller` - Audio feedback control system
- `audio_notifier` - Smart audio notification system
- `audio_player` - Core audio playback functionality
- `audio_player_v3` - Version 3 audio player
- `audio_player_fixed` - Fixed audio player implementation

**Quality & Security**
- `quality_gate_hook` - Quality gate enforcement
- `security_scanner` - Security vulnerability scanning
- `code_linter` - Code quality linting
- `git_quality_hooks` - Git workflow quality checks
- `v3_validator` - Version 3 validation system

**Performance & Monitoring**
- `performance_monitor` - System performance monitoring
- `resource_monitor` - Resource usage tracking
- `status_line_manager` - Status line management
- `model_tracker` - Model usage tracking
- `context_manager` - Context and session management

**And 17+ more hooks for communication, documentation, and development tools!**

### 🔊 Audio System (90+ Files)

Rich audio feedback for every system event:
- System events (startup, processing, completion)
- Agent activations and delegations
- File operations and Git workflows
- Build processes and deployments
- Quality checks and security scans
- Error handling and warnings

## 🛠️ CLI Commands

### Main Setup
```bash
claude-code-setup [options]

Options:
  -i, --interactive     Run interactive setup wizard
  -a, --agents-only     Install only agents  
  -h, --hooks-only      Install only hooks
  -u, --audio-only      Setup only audio system
  -p, --path <path>     Custom installation path
  -y, --yes             Skip confirmations (use defaults)
  --skip-validation     Skip system validation
  --dev-mode            Enable development mode features
```

### Agent Management
```bash
claude-code-agents <command> [options]

Commands:
  list                  List all available agents
  install [agent]       Install agent(s) 
  info <agent>          Show detailed agent information
  validate              Validate all installed agents
  help-examples         Show usage examples

Options:
  -a, --all            Install/list all agents
  -p, --path <path>    Installation path
  -f, --force          Force reinstall
  --json               Output as JSON
```

### Hook Management  
```bash
claude-code-hooks <command> [options]

Commands:
  list                  List all available hooks
  install [hook]        Install hook(s)
  info <hook>           Show detailed hook information
  test [hook]           Test hook functionality
  toggle <hook>         Enable/disable a hook
  categories            List all hook categories
  help-examples         Show usage examples

Options:
  -a, --all            Install/list all hooks
  -c, --category <cat> Filter by category  
  -p, --path <path>    Installation path
  -f, --force          Force reinstall
  --json               Output as JSON
```

## 📖 Programmatic Usage

```javascript
import { 
  ClaudeCodeDevStack,
  agentInstaller,
  hookInstaller, 
  audioSetup,
  configHelpers 
} from '@claude-code/dev-stack';

// Initialize the complete stack
const stack = new ClaudeCodeDevStack();
await stack.initialize();

// Install specific components
await agentInstaller.installAll();
await hookInstaller.installAll(); 
await audioSetup.setupAll();

// Generate configuration
await configHelpers.generateConfig({
  devMode: true,
  path: '/custom/path'
});

// Start the UI
await stack.startUI({ port: 3000 });

// Run orchestration
await stack.orchestrate({
  name: 'deploy-app',
  agents: ['backend-services', 'devops-engineering']
});
```

## 🏗️ Architecture

```
@claude-code/dev-stack/
├── bin/                    # CLI executables
│   ├── claude-code-setup.js
│   ├── claude-code-agents.js  
│   └── claude-code-hooks.js
├── lib/                    # Core libraries
│   ├── agents/            # Agent management
│   ├── hooks/             # Hook management  
│   ├── audio/             # Audio system
│   ├── config/            # Configuration
│   ├── orchestration/     # Orchestration engine
│   └── ui/                # UI management
├── core/                   # Core assets
│   ├── agents/agents/     # 28 agent files (.md)
│   ├── hooks/hooks/       # 37 hook files (.py)
│   └── audio/audio/       # 90+ audio files (.wav)
├── ui/react-pwa/          # Unified PWA dashboard
├── scripts/               # Build and utility scripts
└── index.js               # Main entry point
```

## 🔧 Configuration

After installation, Claude Code creates a configuration structure:

```
~/.claude/
├── claude-code.config.json    # Main configuration
├── agents.config.json         # Agent routing and delegation  
├── hooks.config.json          # Hook triggers and execution
├── agents/                    # Installed agent files
├── hooks/                     # Installed hook files
├── audio/                     # Audio system files
│   └── audio-config.json     # Audio configuration
├── ui/                        # PWA dashboard files  
├── logs/                      # System logs
└── cache/                     # Performance cache
```

## 🚀 Development

```bash
# Clone the repository
git clone https://github.com/claude-code/dev-stack.git
cd dev-stack

# Install dependencies
npm install

# Run tests
npm test

# Validate package
npm run validate

# Start development UI
npm run dev
```

## 📊 System Requirements

- **Node.js**: >= 18.0.0
- **npm**: >= 8.0.0  
- **Git**: >= 2.20.0
- **Python**: >= 3.8.0 (for hooks)
- **Operating System**: Windows, macOS, Linux

## 🔄 Migration from V2

```bash
# Backup existing configuration
cp -r ~/.claude ~/.claude.v2.backup

# Install V3
npm install -g @claude-code/dev-stack

# Run migration (preserves existing settings)
claude-code-setup --migrate-from-v2
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/claude-code/dev-stack/blob/main/CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/claude-code/dev-stack.git
cd dev-stack
npm install
npm run test
```

## 📄 License

MIT © [Claude Code Team](https://claude-code.dev)

## 🆘 Support

- 📚 [Documentation](https://claude-code.dev/docs)
- 🐛 [Issue Tracker](https://github.com/claude-code/dev-stack/issues)
- 💬 [Discord Community](https://discord.gg/claude-code)
- 📧 [Email Support](mailto:support@claude-code.dev)

## 📈 Roadmap

### V3.1 (Coming Soon)
- [ ] VS Code Extension
- [ ] Docker Container Support  
- [ ] Cloud Deployment Templates
- [ ] Advanced Analytics Dashboard

### V3.2
- [ ] Custom Agent Builder
- [ ] Plugin Marketplace
- [ ] Team Collaboration Features
- [ ] Enterprise SSO Integration

---

<div align="center">
  <b>Made with ❤️ by the Claude Code Team</b><br>
  <sub>Empowering developers with AI-driven workflows</sub>
</div>