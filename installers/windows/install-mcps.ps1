# Claude Code MCP Installer for Windows
# Version: 2.1 - Fixed Edition
# Installs Model Context Protocol servers using claude mcp add commands

$ErrorActionPreference = "Continue"  # Continue on errors
$ProgressPreference = 'SilentlyContinue'

Write-Host "`nClaude Code MCP Installer v2.1" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "Installing Model Context Protocol servers" -ForegroundColor Yellow

# Start timer
$startTime = Get-Date

# Check for Claude CLI
Write-Host "`n[1/5] Checking Claude CLI installation..." -ForegroundColor Green
try {
    $claudeVersion = claude --version 2>$null
    if (-not $claudeVersion) {
        throw "Claude CLI not found"
    }
    Write-Host "  ✓ Claude CLI detected: $claudeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Claude CLI not found. Please install Claude Desktop first." -ForegroundColor Red
    Write-Host "  Download from: https://claude.ai/download" -ForegroundColor Yellow
    exit 1
}

# Check for Node.js and npm
Write-Host "`n[2/5] Checking Node.js/npm installation..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    if (-not $nodeVersion -or -not $npmVersion) {
        throw "Node.js/npm not found"
    }
    Write-Host "  ✓ Node.js $nodeVersion detected" -ForegroundColor Green
    Write-Host "  ✓ npm v$npmVersion detected" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js/npm not found. Please install Node.js first." -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Define MCP servers to install
Write-Host "`n[3/5] Preparing MCP server list..." -ForegroundColor Green

$mcpServers = @(
    @{
        name = "filesystem"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-filesystem", "~/Documents")
        display = "Filesystem MCP"
        description = "Access and manage local files"
    },
    @{
        name = "github"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-github")
        display = "GitHub MCP"
        description = "Interact with GitHub repositories"
        env = @{
            "GITHUB_PERSONAL_ACCESS_TOKEN" = "`${GITHUB_TOKEN}"
        }
    },
    @{
        name = "google-drive"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-gdrive")
        display = "Google Drive MCP"
        description = "Access Google Drive files"
    },
    @{
        name = "postgres"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-postgres")
        display = "PostgreSQL MCP"
        description = "Connect to PostgreSQL databases"
        env = @{
            "DATABASE_URL" = "`${DATABASE_URL}"
        }
    },
    @{
        name = "memory"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-memory")
        display = "Memory MCP"
        description = "Persistent memory across conversations"
    },
    @{
        name = "puppeteer"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-puppeteer")
        display = "Puppeteer MCP"
        description = "Browser automation and web scraping"
    },
    @{
        name = "brave-search"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-brave-search")
        display = "Brave Search MCP"
        description = "Web search capabilities"
        env = @{
            "BRAVE_API_KEY" = "`${BRAVE_API_KEY}"
        }
    },
    @{
        name = "fetch"
        command = "npx"
        args = @("-y", "@modelcontextprotocol/server-fetch")
        display = "Fetch MCP"
        description = "Make HTTP requests"
    }
)

Write-Host "  Found $($mcpServers.Count) MCP servers to install" -ForegroundColor Green

# Install MCPs using claude mcp add command
Write-Host "`n[4/5] Installing MCP servers..." -ForegroundColor Green

$installedCount = 0
$failedServers = @()

foreach ($mcp in $mcpServers) {
    Write-Host "`n  Installing $($mcp.display)..." -ForegroundColor Cyan
    Write-Host "    Description: $($mcp.description)" -ForegroundColor DarkGray
    
    try {
        # Build the claude mcp add command
        $argsString = $mcp.args -join " "
        $fullCommand = "claude mcp add $($mcp.name) $($mcp.command) $argsString"
        
        # Add environment variables if needed
        if ($mcp.env) {
            $envString = ""
            foreach ($key in $mcp.env.Keys) {
                $envString += " --env $key=$($mcp.env[$key])"
            }
            $fullCommand += $envString
        }
        
        Write-Host "    Command: $fullCommand" -ForegroundColor DarkGray
        
        # Execute the command
        $result = Invoke-Expression $fullCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✓ Successfully installed $($mcp.display)" -ForegroundColor Green
            $installedCount++
        } else {
            throw "Installation failed with exit code $LASTEXITCODE"
        }
        
    } catch {
        Write-Host "    ✗ Failed to install $($mcp.display): $_" -ForegroundColor Red
        $failedServers += $mcp.name
        
        # Provide manual installation command
        Write-Host "    Manual install: $fullCommand" -ForegroundColor Yellow
    }
    
    # Small delay between installations
    Start-Sleep -Milliseconds 500
}

# Verify installation
Write-Host "`n[5/5] Verifying MCP installation..." -ForegroundColor Green

try {
    # List installed MCPs
    $installedList = claude mcp list 2>&1
    
    if ($installedList) {
        Write-Host "  Installed MCPs:" -ForegroundColor Green
        Write-Host $installedList -ForegroundColor DarkGray
    }
} catch {
    Write-Host "  Could not verify MCP installation" -ForegroundColor Yellow
}

# Calculate elapsed time
$endTime = Get-Date
$elapsed = $endTime - $startTime
$elapsedSeconds = [math]::Round($elapsed.TotalSeconds, 1)

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Installation Complete! (Time: $elapsedSeconds seconds)" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Total MCP servers: $($mcpServers.Count)" -ForegroundColor White
Write-Host "Successfully installed: $installedCount" -ForegroundColor Green

if ($failedServers.Count -gt 0) {
    Write-Host "Failed: $($failedServers.Count)" -ForegroundColor Red
    Write-Host "`nFailed servers:" -ForegroundColor Red
    $failedServers | ForEach-Object { 
        Write-Host "  - $_" -ForegroundColor Red 
    }
}

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "MCP Server Capabilities:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✓ Filesystem   - Read/write local files" -ForegroundColor White
Write-Host "✓ GitHub       - Manage repositories (set GITHUB_TOKEN)" -ForegroundColor White
Write-Host "✓ Google Drive - Access cloud documents" -ForegroundColor White
Write-Host "✓ PostgreSQL   - Database operations (set DATABASE_URL)" -ForegroundColor White
Write-Host "✓ Memory       - Persistent conversation memory" -ForegroundColor White
Write-Host "✓ Puppeteer    - Web automation and scraping" -ForegroundColor White
Write-Host "✓ Brave Search - Web search (set BRAVE_API_KEY)" -ForegroundColor White
Write-Host "✓ Fetch        - HTTP requests and APIs" -ForegroundColor White

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Environment Variables:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Some MCPs require environment variables:" -ForegroundColor Yellow
Write-Host "  GITHUB_TOKEN    - For GitHub MCP" -ForegroundColor White
Write-Host "  DATABASE_URL    - For PostgreSQL MCP" -ForegroundColor White
Write-Host "  BRAVE_API_KEY   - For Brave Search MCP" -ForegroundColor White
Write-Host "`nSet these in your system environment variables." -ForegroundColor Yellow

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "1. Restart Claude Desktop" -ForegroundColor White
Write-Host "2. MCPs will be available in all conversations" -ForegroundColor White
Write-Host "3. Use 'claude mcp list' to see installed MCPs" -ForegroundColor White
Write-Host "4. Use 'claude mcp remove <name>' to uninstall" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan

# Clean up and exit
if ($failedServers.Count -eq 0) {
    Write-Host "`n✅ All MCP servers installed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠ Installation completed with some failures" -ForegroundColor Yellow
    exit 0
}