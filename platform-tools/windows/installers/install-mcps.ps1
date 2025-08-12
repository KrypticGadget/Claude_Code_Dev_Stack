# Claude Code MCP Server Installer
# Installs and configures Playwright, Obsidian, and Web-search MCP servers

Write-Host ""
Write-Host "Claude Code MCP Server Installer" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Claude Code is installed
try {
    $claudeVersion = claude --version 2>$null
    if ($claudeVersion) {
        Write-Host "✓ Claude Code detected" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Claude Code CLI not found!" -ForegroundColor Red
    Write-Host "  Install from: https://claude.ai/download" -ForegroundColor Yellow
    Write-Host ""
    return 1
}

# Check for Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "✓ Node.js detected: $nodeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Node.js not found!" -ForegroundColor Red
    Write-Host "  Install from: https://nodejs.org" -ForegroundColor Yellow
    Write-Host ""
    return 1
}

Write-Host ""
Write-Host "Installing MCP servers..." -ForegroundColor Yellow
Write-Host ""

# Install Playwright MCP (headed mode - browser UI visible)
Write-Host "1. Installing Playwright MCP..." -ForegroundColor Cyan
try {
    # Remove if exists
    claude mcp remove playwright 2>$null | Out-Null
} catch {}

try {
    claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest'
    Write-Host "   ✓ Playwright MCP installed (headed mode - browser UI visible)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to install Playwright MCP" -ForegroundColor Red
}

# Check for Python (needed for Obsidian)
Write-Host ""
Write-Host "2. Checking Obsidian MCP prerequisites..." -ForegroundColor Cyan

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

if ($pythonInstalled) {
    Write-Host "   Installing Obsidian MCP..." -ForegroundColor Cyan
    
    # Install mcp-obsidian package directly with pip
    Write-Host "   Installing mcp-obsidian package..." -ForegroundColor Yellow
    try {
        pip install mcp-obsidian --upgrade --quiet 2>$null
        Write-Host "   ✓ mcp-obsidian package installed" -ForegroundColor Green
        $mcpInstalled = $true
    } catch {
        Write-Host "   ✗ Failed to install mcp-obsidian package" -ForegroundColor Red
        $mcpInstalled = $false
    }
    
    if ($mcpInstalled) {
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
            
            # Use python -m to run the installed package (note: underscore not hyphen for module name)
            claude mcp add obsidian --env OBSIDIAN_API_KEY=$apiKey --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- python -m mcp_obsidian
            Write-Host "   ✓ Obsidian MCP installed" -ForegroundColor Green
        } else {
            Write-Host "   ⚠ Skipping Obsidian MCP (no API key)" -ForegroundColor Yellow
        }
    }
}

# Install Web-search MCP
Write-Host ""
Write-Host "3. Installing Web-search MCP..." -ForegroundColor Cyan

$webSearchDir = "$env:USERPROFILE\mcp-servers\web-search"

# Check for Git
$hasGit = $false
try {
    git --version 2>$null | Out-Null
    $hasGit = $true
} catch {}

if ($hasGit) {
    Write-Host "   Cloning repository..." -ForegroundColor Yellow
    if (Test-Path $webSearchDir) {
        Remove-Item -Path $webSearchDir -Recurse -Force 2>$null
    }
    git clone https://github.com/pskill9/web-search.git $webSearchDir 2>$null
} else {
    Write-Host "   Downloading repository..." -ForegroundColor Yellow
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

Write-Host "   Building server..." -ForegroundColor Yellow
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

# Download configuration files
Write-Host ""
Write-Host "4. Installing configuration files..." -ForegroundColor Cyan

$claudeDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}

$configs = @(
    @{Name="settings.json"; Url="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/settings.json"},
    @{Name=".mcp.json"; Url="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/.mcp.json"}
)

foreach ($config in $configs) {
    $dest = "$claudeDir\$($config.Name)"
    
    if (Test-Path $dest) {
        Write-Host "   • $($config.Name) exists (skipped)" -ForegroundColor Yellow
    } else {
        try {
            $webClient = New-Object System.Net.WebClient
            $bytes = $webClient.DownloadData($config.Url)
            [System.IO.File]::WriteAllBytes($dest, $bytes)
            $webClient.Dispose()
            Write-Host "   ✓ $($config.Name) installed" -ForegroundColor Green
        } catch {
            Write-Host "   ✗ Failed to download $($config.Name)" -ForegroundColor Red
        }
    }
}

# Summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host " MCP Installation Complete" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installed MCP servers:" -ForegroundColor Green
claude mcp list 2>$null

Write-Host ""
Write-Host "Test your MCP servers:" -ForegroundColor Yellow
Write-Host '  claude "Use playwright to go to example.com"' -ForegroundColor Gray
Write-Host '  claude "Use web-search to find news about AI"' -ForegroundColor Gray
if ($apiKey) {
    Write-Host '  claude "Use obsidian to list files in vault"' -ForegroundColor Gray
}

Write-Host ""
Write-Host "For detailed setup and troubleshooting:" -ForegroundColor Cyan
Write-Host "  https://github.com/KrypticGadget/Claude_Code_Dev_Stack/docs/MCP_COMPLETE_GUIDE.md" -ForegroundColor White
Write-Host ""

return 0