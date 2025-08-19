# Claude Code MCP Server Installer - Enhanced Edition with Docker Support
# Auto-fixes browser locks, sets environment variables, works from any directory
# Version: 3.1 - Now includes Docker MCP for container management
# Last Updated: 2025-01-19

param(
    [switch]$SkipBrowserFix = $false,
    [switch]$Minimal = $false,
    [switch]$IncludeDocker = $true
)

Write-Host ""
Write-Host "Claude Code MCP Server Installer v3.1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing: Playwright, Web Search, GitHub, Obsidian, Docker" -ForegroundColor Cyan
Write-Host ""

# Function to clean browser processes and cache
function Clear-BrowserLocks {
    Write-Host "Cleaning browser locks and cache..." -ForegroundColor Yellow
    
    # Kill ONLY Edge processes (leave Chrome alone for user browsing)
    $processes = @("msedge", "msedgewebview2")
    $totalKilled = 0
    foreach ($proc in $processes) {
        $count = (Get-Process -Name $proc -ErrorAction SilentlyContinue).Count
        if ($count -gt 0) {
            Stop-Process -Name $proc -Force -ErrorAction SilentlyContinue
            $totalKilled += $count
        }
    }
    
    if ($totalKilled -gt 0) {
        Write-Host "  ✓ Terminated $totalKilled browser process(es)" -ForegroundColor Green
    }
    
    # Clear Playwright cache (Edge specific)
    $cachePaths = @(
        "$env:LOCALAPPDATA\ms-playwright\mcp-edge",
        "$env:LOCALAPPDATA\ms-playwright\msedge-*",
        "$env:TEMP\playwright-edge-*",
        "$env:TEMP\playwright-*"
    )
    
    foreach ($path in $cachePaths) {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "  ✓ Cleared Playwright cache" -ForegroundColor Green
    Start-Sleep -Milliseconds 500
}

# Function to set permanent environment variables
function Set-PlaywrightEnvironment {
    Write-Host "Setting environment variables..." -ForegroundColor Yellow
    
    # Set user environment variables permanently
    [Environment]::SetEnvironmentVariable('PLAYWRIGHT_HEADLESS', 'false', 'User')
    [Environment]::SetEnvironmentVariable('PLAYWRIGHT_BROWSERS_PATH', "$env:LOCALAPPDATA\ms-playwright", 'User')
    
    # Also set for current session
    $env:PLAYWRIGHT_HEADLESS = "false"
    $env:PLAYWRIGHT_BROWSERS_PATH = "$env:LOCALAPPDATA\ms-playwright"
    
    Write-Host "  ✓ Environment variables configured for headed mode" -ForegroundColor Green
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Claude Code CLI
$hasClaudeCode = $false
try {
    $claudeVersion = claude --version 2>$null
    if ($claudeVersion) {
        Write-Host "  ✓ Claude Code detected" -ForegroundColor Green
        $hasClaudeCode = $true
    }
} catch {
    Write-Host "  ✗ Claude Code CLI not found!" -ForegroundColor Red
    Write-Host "    Install from: https://claude.ai/download" -ForegroundColor Yellow
    if (-not $Minimal) {
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check Node.js
$hasNode = $false
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "  ✓ Node.js detected: $nodeVersion" -ForegroundColor Green
        $hasNode = $true
    }
} catch {
    Write-Host "  ✗ Node.js not found!" -ForegroundColor Red
    Write-Host "    Install from: https://nodejs.org" -ForegroundColor Yellow
    if (-not $Minimal) {
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Always clean browser locks unless skipped
if (-not $SkipBrowserFix) {
    Clear-BrowserLocks
    Write-Host ""
}

# Set environment variables
Set-PlaywrightEnvironment
Write-Host ""

# Install MCP Servers
Write-Host "Installing MCP servers..." -ForegroundColor Cyan
Write-Host ""

# 1. Install Playwright MCP with headed mode and all fixes
Write-Host "1. Installing Playwright MCP (headed mode)..." -ForegroundColor Yellow

# Remove existing Playwright MCP
try {
    $output = claude mcp remove playwright 2>&1
    if ($output -notlike "*not found*") {
        Write-Host "   Removed existing Playwright configuration" -ForegroundColor Gray
    }
} catch {}

# Install with proper configuration
$playwrightInstalled = $false
$retryCount = 0
$maxRetries = 3

while (-not $playwrightInstalled -and $retryCount -lt $maxRetries) {
    try {
        # Clear any lingering locks before each attempt
        if ($retryCount -gt 0) {
            Write-Host "   Retry attempt $($retryCount)..." -ForegroundColor Yellow
            Clear-BrowserLocks
            Start-Sleep -Seconds 2
        }
        
        # Install Playwright MCP with Edge browser configuration
        $installCmd = @"
claude mcp add playwright ``
    --env PLAYWRIGHT_HEADLESS=false ``
    --env PLAYWRIGHT_BROWSER=msedge ``
    --env PLAYWRIGHT_BROWSERS_PATH="$env:LOCALAPPDATA\ms-playwright" ``
    --env PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-blink-features=AutomationControlled" ``
    -- cmd /c npx '@playwright/mcp@latest'
"@
        
        Invoke-Expression $installCmd 2>&1 | Out-Null
        $playwrightInstalled = $true
        Write-Host "   ✓ Playwright MCP installed (browser UI will be visible)" -ForegroundColor Green
    }
    catch {
        $retryCount++
        if ($retryCount -ge $maxRetries) {
            Write-Host "   ✗ Failed to install Playwright after $maxRetries attempts" -ForegroundColor Red
            Write-Host "   Try running this command manually:" -ForegroundColor Yellow
            Write-Host "   $installCmd" -ForegroundColor Gray
        }
    }
}

# 2. Check for Python (needed for Obsidian)
Write-Host ""
Write-Host "2. Checking Obsidian MCP prerequisites..." -ForegroundColor Yellow

$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "   ✓ Python detected: $pythonVersion" -ForegroundColor Green
        $pythonInstalled = $true
    }
} catch {
    Write-Host "   ⚠ Python not found (required for Obsidian MCP)" -ForegroundColor Yellow
    Write-Host "     Install from: https://python.org" -ForegroundColor Gray
}

if ($pythonInstalled -and -not $Minimal) {
    Write-Host "   Installing Obsidian MCP..." -ForegroundColor Yellow
    
    # Install mcp-obsidian package
    try {
        pip install mcp-obsidian --upgrade --quiet 2>$null
        Write-Host "   ✓ mcp-obsidian package installed" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "   Obsidian REST API Plugin required:" -ForegroundColor Yellow
        Write-Host "   1. Open Obsidian → Settings → Community Plugins" -ForegroundColor Gray
        Write-Host "   2. Search for 'Local REST API'" -ForegroundColor Gray
        Write-Host "   3. Install and enable the plugin" -ForegroundColor Gray
        Write-Host "   4. Copy the API key from plugin settings" -ForegroundColor Gray
        Write-Host ""
        
        $apiKey = Read-Host "   Enter Obsidian API key (or press Enter to skip)"
        
        if ($apiKey) {
            try {
                claude mcp remove obsidian 2>$null | Out-Null
            } catch {}
            
            claude mcp add obsidian --env OBSIDIAN_API_KEY=$apiKey --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- python -m mcp_obsidian
            Write-Host "   ✓ Obsidian MCP installed" -ForegroundColor Green
        } else {
            Write-Host "   ⚠ Skipping Obsidian MCP (no API key)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ✗ Failed to install mcp-obsidian package" -ForegroundColor Red
    }
}

# 3. Install Web-search MCP
if (-not $Minimal) {
    Write-Host ""
    Write-Host "3. Installing Web-search MCP..." -ForegroundColor Yellow
    
    $webSearchDir = "$env:USERPROFILE\mcp-servers\web-search"
    
    # Check for Git
    $hasGit = $false
    try {
        git --version 2>$null | Out-Null
        $hasGit = $true
    } catch {}
    
    if ($hasGit) {
        Write-Host "   Cloning repository..." -ForegroundColor Gray
        if (Test-Path $webSearchDir) {
            Remove-Item -Path $webSearchDir -Recurse -Force 2>$null
        }
        git clone https://github.com/pskill9/web-search.git $webSearchDir 2>$null
    } else {
        Write-Host "   Downloading repository..." -ForegroundColor Gray
        $zipUrl = "https://github.com/pskill9/web-search/archive/refs/heads/main.zip"
        $zipPath = "$env:TEMP\web-search.zip"
        
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        
        if (Test-Path $webSearchDir) {
            Remove-Item -Path $webSearchDir -Recurse -Force
        }
        
        Expand-Archive -Path $zipPath -DestinationPath "$env:USERPROFILE\mcp-servers" -Force
        Move-Item "$env:USERPROFILE\mcp-servers\web-search-main" $webSearchDir -Force
        Remove-Item $zipPath
    }
    
    Write-Host "   Building server..." -ForegroundColor Gray
    Push-Location $webSearchDir
    npm install --silent 2>$null
    npm run build --silent 2>$null
    Pop-Location
    
    try {
        claude mcp remove web-search 2>$null | Out-Null
    } catch {}
    
    $indexPath = "$webSearchDir\build\index.js"
    if (Test-Path $indexPath) {
        claude mcp add web-search -- cmd /c node "$indexPath"
        Write-Host "   ✓ Web-search MCP installed" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Failed to build Web-search MCP" -ForegroundColor Red
    }
}

# 4. Install GitHub MCP Server
if (-not $Minimal) {
    Write-Host ""
    Write-Host "4. Installing GitHub MCP Server..." -ForegroundColor Yellow
    
    # Check if Docker is available for GitHub MCP
    $hasDocker = $false
    try {
        docker --version 2>$null | Out-Null
        $hasDocker = $true
        Write-Host "   ✓ Docker detected" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠ Docker not found - will use remote GitHub MCP server" -ForegroundColor Yellow
    }
    
    if ($hasDocker) {
        Write-Host "   Installing GitHub MCP with Docker..." -ForegroundColor Gray
        
        # Prompt for GitHub token
        Write-Host ""
        Write-Host "   GitHub Personal Access Token required:" -ForegroundColor Yellow
        Write-Host "   1. Go to https://github.com/settings/tokens" -ForegroundColor Gray
        Write-Host "   2. Generate new token (classic or fine-grained)" -ForegroundColor Gray
        Write-Host "   3. Enable repository, issues, pull requests permissions" -ForegroundColor Gray
        Write-Host ""
        
        $githubToken = Read-Host "   Enter GitHub token (or press Enter to skip)"
        
        if ($githubToken) {
            try {
                # Remove existing GitHub MCP if present
                claude mcp remove github 2>$null | Out-Null
                
                # Add GitHub MCP with Docker
                claude mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN=$githubToken -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
                Write-Host "   ✓ GitHub MCP installed with Docker" -ForegroundColor Green
            } catch {
                Write-Host "   ✗ Failed to install GitHub MCP with Docker" -ForegroundColor Red
                Write-Host "   Falling back to remote GitHub MCP..." -ForegroundColor Yellow
                
                # Fallback to remote MCP
                try {
                    claude mcp add github-remote --type http --url "https://api.githubcopilot.com/mcp/" --header "Authorization=Bearer $githubToken"
                    Write-Host "   ✓ GitHub remote MCP installed" -ForegroundColor Green
                } catch {
                    Write-Host "   ✗ Failed to install GitHub remote MCP" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "   ⚠ Skipping GitHub MCP (no token provided)" -ForegroundColor Yellow
            Write-Host "   You can install it later with your GitHub token" -ForegroundColor Gray
        }
    } else {
        # No Docker - try remote MCP server
        Write-Host "   Installing remote GitHub MCP..." -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "   GitHub Personal Access Token required:" -ForegroundColor Yellow
        Write-Host "   1. Go to https://github.com/settings/tokens" -ForegroundColor Gray
        Write-Host "   2. Generate new token (classic or fine-grained)" -ForegroundColor Gray
        Write-Host "   3. Enable repository, issues, pull requests permissions" -ForegroundColor Gray
        Write-Host ""
        
        $githubToken = Read-Host "   Enter GitHub token (or press Enter to skip)"
        
        if ($githubToken) {
            try {
                # Remove existing GitHub MCP if present
                claude mcp remove github 2>$null | Out-Null
                claude mcp remove github-remote 2>$null | Out-Null
                
                # Add remote GitHub MCP
                claude mcp add github --type http --url "https://api.githubcopilot.com/mcp/" --header "Authorization=Bearer $githubToken"
                Write-Host "   ✓ GitHub remote MCP installed" -ForegroundColor Green
            } catch {
                Write-Host "   ✗ Failed to install GitHub remote MCP" -ForegroundColor Red
            }
        } else {
            Write-Host "   ⚠ Skipping GitHub MCP (no token provided)" -ForegroundColor Yellow
        }
    }
}

# 5. Install Docker MCP Server (NEW)
if ($hasDocker -and -not $Minimal) {
    Write-Host ""
    Write-Host "5. Installing Docker MCP Server..." -ForegroundColor Yellow
    Write-Host "   This enables Docker container management from Claude" -ForegroundColor Gray
    
    # Check if QuantGeekDev/docker-mcp is available
    $dockerMcpInstalled = $false
    
    Write-Host "   Setting up Docker MCP..." -ForegroundColor Gray
    
    # Option 1: Try the QuantGeekDev docker-mcp
    try {
        # Clone or download the docker-mcp repository
        $dockerMcpDir = "$env:USERPROFILE\mcp-servers\docker-mcp"
        
        if (Test-Path $dockerMcpDir) {
            Remove-Item -Path $dockerMcpDir -Recurse -Force 2>$null
        }
        
        # Clone the repository
        if ($hasGit) {
            git clone https://github.com/QuantGeekDev/docker-mcp.git $dockerMcpDir 2>$null
        } else {
            # Download as zip
            $zipUrl = "https://github.com/QuantGeekDev/docker-mcp/archive/refs/heads/main.zip"
            $zipPath = "$env:TEMP\docker-mcp.zip"
            
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
            Expand-Archive -Path $zipPath -DestinationPath "$env:USERPROFILE\mcp-servers" -Force
            Move-Item "$env:USERPROFILE\mcp-servers\docker-mcp-main" $dockerMcpDir -Force
            Remove-Item $zipPath
        }
        
        # Build the Docker MCP server
        Push-Location $dockerMcpDir
        npm install --silent 2>$null
        npm run build --silent 2>$null
        Pop-Location
        
        # Remove existing Docker MCP if present
        try {
            claude mcp remove docker 2>$null | Out-Null
        } catch {}
        
        # Add Docker MCP
        $dockerMcpPath = "$dockerMcpDir\build\index.js"
        if (Test-Path $dockerMcpPath) {
            claude mcp add docker -- cmd /c node "$dockerMcpPath"
            Write-Host "   ✓ Docker MCP installed (container management enabled)" -ForegroundColor Green
            $dockerMcpInstalled = $true
        }
    } catch {
        Write-Host "   ⚠ Could not install QuantGeekDev docker-mcp" -ForegroundColor Yellow
    }
    
    # Option 2: Install Docker Code Sandbox MCP
    if (-not $dockerMcpInstalled) {
        Write-Host "   Installing Docker Code Sandbox MCP..." -ForegroundColor Gray
        
        try {
            # Install the npm package first
            Write-Host "   Installing code-sandbox npm package..." -ForegroundColor Gray
            npm install -g @modelcontextprotocol/code-sandbox-mcp --silent 2>$null
            
            # Remove existing code-sandbox MCP if present
            try {
                claude mcp remove code-sandbox 2>$null | Out-Null
            } catch {}
            
            # Add code sandbox MCP using npx (works best on Windows)
            $sandboxInstallCmd = @"
claude mcp add code-sandbox -- npx @modelcontextprotocol/code-sandbox-mcp
"@
            
            Invoke-Expression $sandboxInstallCmd 2>&1 | Out-Null
            Write-Host "   ✓ Docker Code Sandbox MCP installed" -ForegroundColor Green
            $dockerMcpInstalled = $true
        } catch {
            Write-Host "   ⚠ Failed to install Docker Code Sandbox MCP" -ForegroundColor Yellow
            Write-Host "   Try running manually:" -ForegroundColor Yellow
            Write-Host "   docker pull ghcr.io/modelcontextprotocol/code-sandbox:latest" -ForegroundColor Gray
        }
    }
    
    if ($dockerMcpInstalled) {
        Write-Host ""
        Write-Host "   Docker MCP capabilities:" -ForegroundColor Cyan
        Write-Host "   • Manage containers, images, volumes, networks" -ForegroundColor Gray
        Write-Host "   • Execute code in isolated Docker containers" -ForegroundColor Gray
        Write-Host "   • Run tests in containerized environments" -ForegroundColor Gray
        Write-Host "   • Deploy applications with Docker Compose" -ForegroundColor Gray
    }
}

# Create helper scripts
Write-Host ""
Write-Host "Creating helper scripts..." -ForegroundColor Yellow

# Create a quick fix script in user's home directory
$quickFixScript = @'
# Quick Playwright Fix (Edge Only - Preserves Chrome)
param([switch]$Silent)
if (-not $Silent) { Write-Host "Fixing Playwright Edge browser locks..." -ForegroundColor Yellow }
Stop-Process -Name msedge,msedgewebview2 -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\ms-playwright\mcp-edge" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\ms-playwright\msedge-*" -Recurse -Force -ErrorAction SilentlyContinue
if (-not $Silent) { Write-Host "✓ Edge browser locks cleared (Chrome untouched)" -ForegroundColor Green }
'@

$quickFixPath = "$env:USERPROFILE\fix-playwright.ps1"
$quickFixScript | Out-File -FilePath $quickFixPath -Encoding UTF8
Write-Host "  ✓ Created quick fix script: $quickFixPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " MCP Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# List installed servers
Write-Host "Installed MCP servers:" -ForegroundColor Green
claude mcp list 2>$null | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
Write-Host "✅ Playwright is configured for HEADED MODE (browser visible)" -ForegroundColor Green
Write-Host ""

# Test commands
Write-Host "Test your setup:" -ForegroundColor Yellow
Write-Host '  claude "Use playwright to go to example.com"' -ForegroundColor Gray
if (-not $Minimal) {
    Write-Host '  claude "Use web-search to find news about AI"' -ForegroundColor Gray
    Write-Host '  claude "Use github to list my repositories"' -ForegroundColor Gray
    if ($hasDocker) {
        Write-Host '  claude "Use docker to list running containers"' -ForegroundColor Gray
        Write-Host '  claude "Use docker to create a test container"' -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Quick fixes if browser locks occur:" -ForegroundColor Yellow
Write-Host "  fix-playwright" -ForegroundColor Gray
Write-Host "  OR" -ForegroundColor Gray
Write-Host "  powershell -File `"$quickFixPath`"" -ForegroundColor Gray

Write-Host ""
Write-Host "For detailed documentation:" -ForegroundColor Cyan
Write-Host "  https://github.com/KrypticGadget/Claude_Code_Dev_Stack" -ForegroundColor White
Write-Host ""

# Return success
exit 0