# Claude Code Dev Stack v3.0
## The Ultimate Unified AI Development Environment

### 🚀 Built With

This project integrates and extends these excellent open-source projects:

- [**Claude Code Browser**](https://github.com/zainhoda/claude-code-browser) by @zainhoda - Session monitoring and automation
- [**Claude Code App**](https://github.com/9cat/claude-code-app) by @9cat - Mobile interface
- [**MCP Manager**](https://github.com/qdhenry/Claude-Code-MCP-Manager) by @qdhenry - MCP configuration
- [**OpenAPI MCP Codegen**](https://github.com/cnoe-io/openapi-mcp-codegen) by CNOE.io - Python MCP generation
- [**OpenAPI MCP Generator**](https://github.com/harsha-iiiv/openapi-mcp-generator) by @harsha-iiiv - Node.js MCP generation
- [**Claude Powerline**](https://github.com/Owloops/claude-powerline) by @Owloops - Advanced statusline
- [**CC-Statusline**](https://github.com/chongdashu/cc-statusline) by @chongdashu - Setup patterns

See [CREDITS.md](CREDITS.md) for detailed attribution and [LICENSE-THIRD-PARTY](LICENSE-THIRD-PARTY/) for all licenses.

## Features

### 🤖 AI Agent Orchestration
- **28 Custom AI Agents** for comprehensive development automation
- **28 Automation Hooks** for event-driven workflows
- **18 Slash Commands** for quick actions
- **102 Audio Notifications** for phase-aware feedback

### 📱 Multi-Platform Support
- **React PWA** - Progressive Web App for desktop and mobile browsers
- **React Native** - Native mobile apps for iOS and Android
- **Voice Control** - Natural language commands across all platforms
- **Real-time Sync** - Seamless experience across devices

### 📊 Ultimate Statusline
Combining the best of both worlds:
- **Claude Powerline** (@Owloops): Cost tracking, git integration, themes
- **Dev Stack Monitoring**: Agent status, task progress, hook activity
- **100ms Real-time Updates**: Lightning-fast status refresh

### 🔌 MCP Integration Hub
- **MCP Manager** for service orchestration
- **OpenAPI to MCP** generators (Python & TypeScript)
- **Playwright Testing** automation
- **GitHub Integration** for version control

### 🎯 Performance
- Repository size < 200MB
- 100ms statusline updates
- 70% code sharing between platforms
- Optimized audio assets

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git
- Claude Code CLI

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Claude_Code_Dev_Stack_v3.git
cd Claude_Code_Dev_Stack_v3

# Install dependencies
npm install
pip install -r requirements.txt

# Setup statusline
npm install -g @owloops/claude-powerline
bash ./scripts/setup-statusline.sh

# Launch the system
npm run dev
```

### Mobile Setup

```bash
# React Native setup
cd apps/mobile
npm install
npx expo start
```

## Architecture

```
Claude_Code_Dev_Stack_v3/
├── apps/
│   ├── web/          # React PWA
│   ├── mobile/       # React Native
│   └── shared/       # Shared components
├── core/
│   ├── agents/       # 28 AI agents
│   ├── hooks/        # 28 automation hooks
│   ├── commands/     # 18 slash commands
│   └── audio/        # 102 audio files
├── integrations/     # 7 integrated projects
└── docs/            # Documentation
```

## Development

### Running Tests

```bash
# Run all tests
npm test

# Run with MCP Playwright
npm run test:playwright

# Test specific components
npm run test:agents
npm run test:statusline
```

### Building for Production

```bash
# Build PWA
npm run build:pwa

# Build mobile apps
npm run build:mobile

# Create distribution
npm run dist
```

## Contributing

We welcome contributions! Please ensure:
- Proper attribution for any integrated code
- License compatibility verification
- Repository size constraints (<200MB)
- Test coverage for new features

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under AGPL-3.0 (due to Claude Code Browser integration).
Individual components maintain their original licenses - see [LICENSE-THIRD-PARTY](LICENSE-THIRD-PARTY/).

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/Claude_Code_Dev_Stack_v3/issues)
- 💬 [Discussions](https://github.com/yourusername/Claude_Code_Dev_Stack_v3/discussions)

## Acknowledgments

Special thanks to all the original authors and the open-source community.
See [CREDITS.md](CREDITS.md) for full attribution.

---

**Claude Code Dev Stack v3.0** - Orchestrating AI Development at Scale