#!/usr/bin/env powershell
# Claude Code Dev Stack v3.0 - One-liner Installer
# Installs all components with proper attribution

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                Claude Code Dev Stack v3.0                      ║
║                 One-Liner Installation                         ║
║                                                                ║
║  Integrating components from:                                  ║
║  • @zainhoda/claude-code-browser                               ║
║  • @9cat/claude-code-app                                       ║
║  • @qdhenry/mcp-manager                                        ║
║  • @Owloops/claude-powerline                                   ║
║  • @chongdashu/cc-statusline                                   ║
║  + Original 28-agent orchestration by Zach                    ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Prerequisites check
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "node" = "Node.js 18+"
    "python" = "Python 3.8+"
    "git" = "Git"
    "claude" = "Claude Code CLI"
}

foreach ($tool in $prerequisites.Keys) {
    try {
        $version = & $tool --version 2>$null
        Write-Host "✅ $($prerequisites[$tool]): Found" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($prerequisites[$tool]): Missing" -ForegroundColor Red
        exit 1
    }
}

# Install system
Write-Host "📦 Installing Claude Code Dev Stack v3.0..." -ForegroundColor Yellow

# Install Claude Powerline (@Owloops)
Write-Host "Installing statusline components..." -ForegroundColor Blue
npm install -g @owloops/claude-powerline

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Blue
npm install

# Setup statusline integration
Write-Host "Setting up ultimate statusline..." -ForegroundColor Blue
cd integrations/statusline
npm install
npm run build
cd ../..

# Setup mobile app
Write-Host "Setting up mobile app..." -ForegroundColor Blue
cd apps/mobile
npm install
cd ../..

# Setup web app
Write-Host "Setting up web app..." -ForegroundColor Blue
cd apps/web
npm install
cd ../..

# Create statusline configuration
Write-Host "Configuring statusline..." -ForegroundColor Blue
$claudeDir = "$env:USERPROFILE\.claude"
if (!(Test-Path $claudeDir)) { New-Item -Type Directory -Path $claudeDir }

$statuslineConfig = @{
    theme = "tokyo-night"
    display = @{
        lines = @(
            @{
                segments = @{
                    directory = @{ enabled = $true; showBasename = $false }
                    git = @{ enabled = $true; showSha = $true; showWorkingTree = $true }
                    model = @{ enabled = $true }
                    version = @{ enabled = $true }
                }
            },
            @{
                segments = @{
                    session = @{ enabled = $true; type = "breakdown" }
                    block = @{ enabled = $true; type = "cost"; burnType = "cost" }
                    today = @{ enabled = $true; type = "cost" }
                    context = @{ enabled = $true }
                }
            }
        )
    }
    budget = @{
        session = @{ amount = 10.0; warningThreshold = 80 }
        today = @{ amount = 25.0; warningThreshold = 80 }
    }
} | ConvertTo-Json -Depth 10

$statuslineConfig | Out-File "$claudeDir\powerline-config.json" -Encoding UTF8

# Launch system
Write-Host "🚀 Launching Claude Code Dev Stack v3.0..." -ForegroundColor Green

Start-Job -ScriptBlock { 
    cd $using:PWD
    cd apps/web
    npm run dev 
} -Name "WebApp"

Start-Job -ScriptBlock {
    cd $using:PWD  
    cd apps/mobile
    npm start
} -Name "MobileApp"

Write-Host @"

🎉 Installation Complete!

System URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Web App:      http://localhost:5173
📱 Mobile App:   http://localhost:8081 (Expo)
📊 Browser:      http://localhost:8080 (@zainhoda)
🔌 MCP Manager:  http://localhost:8085 (@qdhenry)
📈 Statusline:   Terminal (Powerline + Dev Stack)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Statusline Features:
• Line 1: Directory | Git | Model | Costs (@Owloops)
• Line 2: Agents (0/28) | Tasks | Hooks | Audio (Zach)
• Real-time updates: 100ms

Attribution: See CREDITS.md
Documentation: ./docs/
"@ -ForegroundColor Green

Write-Host "`n🔥 Ready to orchestrate AI development at scale!" -ForegroundColor Yellow