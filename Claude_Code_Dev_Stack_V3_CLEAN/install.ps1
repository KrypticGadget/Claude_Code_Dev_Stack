# Claude Code Dev Stack V3 - One-Line Installer for Windows
# Usage: irm https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/feature/v3-dev/install.ps1 | iex

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████  ██          █████   ██    ██ ██████   ███████     ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ██        ██         ███████  ██    ██ ██   ██  █████       ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ████████  ███████    ██   ██   ██████   ██████   ███████     ║
║                                                               ║
║                    CODE DEV STACK V3                         ║
║                One-Command Installation                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check for Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is required but not installed." -ForegroundColor Red
    Write-Host "   Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check for npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm is required but not installed." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing Claude Code Dev Stack V3..." -ForegroundColor Green
Write-Host ""

# Install from GitHub
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev

Write-Host ""
Write-Host "✨ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Yellow
Write-Host "  1. List agents:  claude-code-agents list"
Write-Host "  2. List hooks:   claude-code-hooks list"
Write-Host "  3. Start PWA:    cd ~/.claude/ui && npm run dev"
Write-Host "  4. Test Claude:  claude `"@master-orchestrator help`""
Write-Host ""
Write-Host "📚 Documentation: https://claude-code.dev/docs" -ForegroundColor Blue
Write-Host ""