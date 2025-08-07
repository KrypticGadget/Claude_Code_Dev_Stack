#!/usr/bin/env pwsh
# Master MCP Setup Script for Claude Code Dev Stack
# Installs and configures Playwright, Obsidian, and Web-search MCP servers

param(
    [string]$ObsidianApiKey = "",
    [switch]$SkipPlaywright,
    [switch]$SkipObsidian,
    [switch]$SkipWebSearch,
    [switch]$Uninstall,
    [switch]$Test
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " Claude Code MCP Server Setup v2.1" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    $issues = @()
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Host "  ✓ Node.js installed: $nodeVersion" -ForegroundColor Green
        }
    } catch {
        $issues += "Node.js not found. Install from https://nodejs.org"
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        if ($npmVersion) {
            Write-Host "  ✓ npm installed: $npmVersion" -ForegroundColor Green
        }
    } catch {
        $issues += "npm not found"
    }
    
    # Check Claude Code
    try {
        $claudeVersion = claude --version 2>$null
        if ($claudeVersion) {
            Write-Host "  ✓ Claude Code installed" -ForegroundColor Green
        }
    } catch {
        $issues += "Claude Code CLI not found. Install from https://claude.ai/download"
    }
    
    # Check Python (for Obsidian)
    if (-not $SkipObsidian) {
        try {
            $pythonVersion = python --version 2>$null
            if ($pythonVersion) {
                Write-Host "  ✓ Python installed: $pythonVersion" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠ Python not found (required for Obsidian MCP)" -ForegroundColor Yellow
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-Host "Prerequisites missing:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  - $issue" -ForegroundColor Red
        }
        Write-Host ""
        return $false
    }
    
    Write-Host ""
    return $true
}

# Uninstall function
function Uninstall-MCPServers {
    Write-Host "Uninstalling MCP servers..." -ForegroundColor Yellow
    
    $servers = @("playwright", "playwright-headed", "playwright-mobile", "obsidian", "web-search")
    
    foreach ($server in $servers) {
        try {
            claude mcp remove $server 2>$null
            Write-Host "  ✓ Removed $server" -ForegroundColor Green
        } catch {
            Write-Host "  - $server not installed" -ForegroundColor Gray
        }
    }
    
    # Clean up web-search directory
    $webSearchDir = "$env:USERPROFILE\mcp-servers\web-search"
    if (Test-Path $webSearchDir) {
        Remove-Item -Path $webSearchDir -Recurse -Force
        Write-Host "  ✓ Removed web-search directory" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "MCP servers uninstalled successfully!" -ForegroundColor Green
}

# Install Playwright MCP
function Install-PlaywrightMCP {
    Write-Host "Installing Playwright MCP..." -ForegroundColor Cyan
    Write-Host ""
    
    # Remove existing if present
    try {
        claude mcp remove playwright 2>$null
    } catch {}
    
    # Install headless version (default)
    Write-Host "  Installing headless version..." -ForegroundColor Yellow
    $cmd = "claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless"
    Invoke-Expression $cmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Playwright MCP installed (headless)" -ForegroundColor Green
        
        # Option to install additional variants
        Write-Host ""
        $response = Read-Host "Install additional Playwright variants? (headed/mobile) [y/N]"
        if ($response -eq 'y' -or $response -eq 'Y') {
            # Headed version
            try {
                claude mcp remove playwright-headed 2>$null
            } catch {}
            claude mcp add playwright-headed -- cmd /c npx '@playwright/mcp@latest'
            Write-Host "  ✓ Playwright MCP headed variant installed" -ForegroundColor Green
            
            # Mobile version
            try {
                claude mcp remove playwright-mobile 2>$null
            } catch {}
            claude mcp add playwright-mobile -- cmd /c npx '@playwright/mcp@latest' --device='iPhone 15'
            Write-Host "  ✓ Playwright MCP mobile variant installed" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✗ Failed to install Playwright MCP" -ForegroundColor Red
        return $false
    }
    
    Write-Host ""
    return $true
}

# Install Obsidian MCP
function Install-ObsidianMCP {
    Write-Host "Installing Obsidian MCP..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check for Python and UV
    $hasUV = $false
    try {
        $uvVersion = uvx --version 2>$null
        if ($uvVersion) {
            $hasUV = $true
            Write-Host "  ✓ UV package manager found" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Installing UV package manager..." -ForegroundColor Yellow
        pip install --user uv
        $hasUV = $true
    }
    
    if (-not $hasUV) {
        Write-Host "  ✗ Could not install UV package manager" -ForegroundColor Red
        Write-Host "    Install manually: pip install uv" -ForegroundColor Yellow
        return $false
    }
    
    # Get Obsidian API key
    if (-not $ObsidianApiKey) {
        Write-Host ""
        Write-Host "  Obsidian REST API Plugin required:" -ForegroundColor Yellow
        Write-Host "  1. Open Obsidian → Settings → Community Plugins" -ForegroundColor Gray
        Write-Host "  2. Search for 'Local REST API'" -ForegroundColor Gray
        Write-Host "  3. Install and enable the plugin" -ForegroundColor Gray
        Write-Host "  4. Copy the API key from plugin settings" -ForegroundColor Gray
        Write-Host ""
        $ObsidianApiKey = Read-Host "Enter your Obsidian API key (or press Enter to skip)"
    }
    
    if ($ObsidianApiKey) {
        # Remove existing if present
        try {
            claude mcp remove obsidian 2>$null
        } catch {}
        
        # Find uvx path
        $uvxPath = (Get-Command uvx -ErrorAction SilentlyContinue).Source
        if (-not $uvxPath) {
            $uvxPath = "uvx"  # Try default
        }
        
        # Install with API key
        $cmd = "claude mcp add obsidian --env OBSIDIAN_API_KEY=$ObsidianApiKey --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- cmd /c `"$uvxPath`" mcp-obsidian"
        Invoke-Expression $cmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Obsidian MCP installed" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to install Obsidian MCP" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "  ⚠ Skipping Obsidian MCP (no API key provided)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    return $true
}

# Install Web-search MCP
function Install-WebSearchMCP {
    Write-Host "Installing Web-search MCP..." -ForegroundColor Cyan
    Write-Host ""
    
    $installDir = "$env:USERPROFILE\mcp-servers\web-search"
    
    # Check if Git is available
    $hasGit = $false
    try {
        git --version 2>$null | Out-Null
        $hasGit = $true
    } catch {}
    
    if ($hasGit) {
        # Clone with Git
        Write-Host "  Cloning repository..." -ForegroundColor Yellow
        if (Test-Path $installDir) {
            Remove-Item -Path $installDir -Recurse -Force
        }
        git clone https://github.com/pskill9/web-search.git $installDir 2>$null
    } else {
        # Download as ZIP
        Write-Host "  Downloading repository (Git not found)..." -ForegroundColor Yellow
        $zipUrl = "https://github.com/pskill9/web-search/archive/refs/heads/main.zip"
        $zipPath = "$env:TEMP\web-search.zip"
        
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        
        if (Test-Path $installDir) {
            Remove-Item -Path $installDir -Recurse -Force
        }
        
        Expand-Archive -Path $zipPath -DestinationPath "$env:USERPROFILE\mcp-servers" -Force
        Move-Item "$env:USERPROFILE\mcp-servers\web-search-main" $installDir -Force
        Remove-Item $zipPath
    }
    
    # Build the server
    Write-Host "  Building server..." -ForegroundColor Yellow
    Push-Location $installDir
    npm install --silent 2>$null
    npm run build --silent 2>$null
    Pop-Location
    
    # Add to Claude Code
    try {
        claude mcp remove web-search 2>$null
    } catch {}
    
    $indexPath = "$installDir\build\index.js"
    if (Test-Path $indexPath) {
        claude mcp add web-search -- cmd /c node "$indexPath"
        Write-Host "  ✓ Web-search MCP installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to build Web-search MCP" -ForegroundColor Red
        return $false
    }
    
    Write-Host ""
    return $true
}

# Test MCP servers
function Test-MCPServers {
    Write-Host "Testing MCP servers..." -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Run these commands in Claude Code to test:" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $SkipPlaywright) {
        Write-Host "  Playwright test:" -ForegroundColor Cyan
        Write-Host '  claude "Use playwright to navigate to https://example.com and get the page title"' -ForegroundColor White
        Write-Host ""
    }
    
    if (-not $SkipObsidian -and $ObsidianApiKey) {
        Write-Host "  Obsidian test:" -ForegroundColor Cyan
        Write-Host '  claude "Use obsidian to list all files in the vault"' -ForegroundColor White
        Write-Host ""
    }
    
    if (-not $SkipWebSearch) {
        Write-Host "  Web-search test:" -ForegroundColor Cyan
        Write-Host '  claude "Use web-search to find information about Claude AI"' -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "Combined workflow test:" -ForegroundColor Cyan
    Write-Host '  claude "Use web-search to find articles about AI, then use playwright to visit the first result"' -ForegroundColor White
    Write-Host ""
}

# Main execution
if ($Uninstall) {
    Uninstall-MCPServers
    return
}

if ($Test) {
    Test-MCPServers
    return
}

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-Host "Please install missing prerequisites and run again." -ForegroundColor Red
    return
}

Write-Host "Starting MCP server installation..." -ForegroundColor Green
Write-Host ""

$success = $true

# Install servers
if (-not $SkipPlaywright) {
    if (-not (Install-PlaywrightMCP)) {
        $success = $false
    }
}

if (-not $SkipObsidian) {
    if (-not (Install-ObsidianMCP)) {
        $success = $false
    }
}

if (-not $SkipWebSearch) {
    if (-not (Install-WebSearchMCP)) {
        $success = $false
    }
}

# Final summary
Write-Host "==================================" -ForegroundColor Cyan
Write-Host " Installation Complete" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# List installed servers
Write-Host "Installed MCP servers:" -ForegroundColor Green
claude mcp list

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Claude Code if it's running" -ForegroundColor Gray
Write-Host "  2. Test the servers with: .\master-mcp-setup.ps1 -Test" -ForegroundColor Gray
Write-Host "  3. Check the documentation for usage examples" -ForegroundColor Gray
Write-Host ""

if ($success) {
    Write-Host "✅ MCP setup completed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠ MCP setup completed with some issues" -ForegroundColor Yellow
    Write-Host "  Check the errors above and try again" -ForegroundColor Yellow
}

return