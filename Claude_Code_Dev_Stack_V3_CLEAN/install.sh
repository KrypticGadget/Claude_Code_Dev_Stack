#!/bin/bash

# Claude Code Dev Stack V3 - One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/feature/v3-dev/install.sh | bash

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ████████  ██          █████   ██    ██ ██████   ███████     ║"
echo "║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║"
echo "║   ██        ██         ███████  ██    ██ ██   ██  █████       ║"
echo "║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║"
echo "║   ████████  ███████    ██   ██   ██████   ██████   ███████     ║"
echo "║                                                               ║"
echo "║                    CODE DEV STACK V3                         ║"
echo "║                One-Command Installation                       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "📦 Installing Claude Code Dev Stack V3..."
echo ""

# Install from GitHub
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev

echo ""
echo "✨ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "  1. List agents:  claude-code-agents list"
echo "  2. List hooks:   claude-code-hooks list"
echo "  3. Start PWA:    cd ~/.claude/ui && npm run dev"
echo "  4. Test Claude:  claude \"@master-orchestrator help\""
echo ""
echo "📚 Documentation: https://claude-code.dev/docs"
echo ""