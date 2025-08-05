# Tier 1 MCP Installer for Windows PowerShell
# Installs: Playwright MCP, Obsidian MCP, and Brave Search MCP
# Global installation at Claude Code root level

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== Tier 1 MCP Global Installer for Claude Code ===" -ForegroundColor Cyan
Write-Host "Installing: Playwright, Obsidian, and Brave Search MCPs" -ForegroundColor Yellow
Write-Host "Installation Type: GLOBAL (Available in all projects)" -ForegroundColor Green
Write-Host ""

# Check for Claude CLI
Write-Host "[1/6] Checking Claude CLI installation..." -ForegroundColor Green
try {
    $claudeVersion = claude --version 2>$null
    if (-not $claudeVersion) {
        throw "Claude CLI not found"
    }
    Write-Host "  ✓ Claude CLI detected: $claudeVersion" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Claude CLI not found. Please install Claude Code first." -ForegroundColor Red
    Write-Host "  Download from: https://claude.ai/download" -ForegroundColor Yellow
    exit 1
}

# Check for Node.js and npm
Write-Host ""
Write-Host "[2/6] Checking Node.js/npm installation..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    if (-not $nodeVersion -or -not $npmVersion) {
        throw "Node.js/npm not found"
    }
    Write-Host "  ✓ Node.js $nodeVersion detected" -ForegroundColor DarkGray
    Write-Host "  ✓ npm v$npmVersion detected" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Node.js/npm not found. Please install Node.js first." -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Detect Claude Code installation path
Write-Host ""
Write-Host "[3/6] Detecting Claude Code installation..." -ForegroundColor Green
$claudeCodePaths = @(
    "$env:APPDATA\Claude",
    "$env:LOCALAPPDATA\Claude",
    "$env:USERPROFILE\AppData\Roaming\Claude",
    "$env:USERPROFILE\AppData\Local\Claude"
)

$claudeCodePath = $null
$settingsPath = $null

foreach ($path in $claudeCodePaths) {
    $testSettingsPath = Join-Path $path "claude_desktop_config.json"
    if (Test-Path $testSettingsPath) {
        $claudeCodePath = $path
        $settingsPath = $testSettingsPath
        break
    }
}

if (-not $claudeCodePath) {
    Write-Host "  ✗ Claude Code installation not found" -ForegroundColor Red
    Write-Host "  Please ensure Claude Code is installed" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ Found Claude Code at: $claudeCodePath" -ForegroundColor DarkGray

# Create global MCP directory at Claude Code root
$mcpDir = Join-Path $claudeCodePath "mcp"
if (-not (Test-Path $mcpDir)) {
    New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null
    Write-Host "  ✓ Created global MCP directory: $mcpDir" -ForegroundColor DarkGray
}

# Install Tier 1 MCPs using Claude CLI
Write-Host ""
Write-Host "[4/6] Installing Tier 1 MCPs globally..." -ForegroundColor Green

$mcps = @(
    @{
        name="playwright"
        command="claude mcp add playwright npx @playwright/mcp@latest"
        display="Playwright MCP"
        description="Browser testing and UI automation"
    },
    @{
        name="obsidian"
        command="claude mcp add obsidian npx @kreateworld/mcp-obsidian@latest"
        display="Obsidian MCP"
        description="Knowledge management and documentation"
    },
    @{
        name="brave-search"
        command="claude mcp add brave-search npx @modelcontextprotocol/server-brave-search@latest"
        display="Brave Search MCP"
        description="Web research and market analysis"
    }
)

$installedCount = 0
foreach ($mcp in $mcps) {
    Write-Host ""
    Write-Host "  Installing $($mcp.display)..." -ForegroundColor Yellow
    Write-Host "  Purpose: $($mcp.description)" -ForegroundColor DarkGray
    try {
        # Execute Claude MCP add command
        $output = & cmd /c $mcp.command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $($mcp.display) installed globally" -ForegroundColor Green
            $installedCount++
            
            # Create subdirectory for this MCP
            $mcpSubDir = Join-Path $mcpDir $mcp.name
            if (-not (Test-Path $mcpSubDir)) {
                New-Item -ItemType Directory -Path $mcpSubDir -Force | Out-Null
            }
        } else {
            throw "Installation failed: $output"
        }
    } catch {
        Write-Host "  ✗ Failed to install $($mcp.display): $_" -ForegroundColor Red
        Write-Host "  You can manually install with: $($mcp.command)" -ForegroundColor Yellow
    }
}

# Create global MCP configuration
Write-Host ""
Write-Host "[5/6] Creating global MCP configuration..." -ForegroundColor Green

# Create mcp-config.json
$mcpConfig = @{
    "version" = "1.0"
    "global" = $true
    "mcps" = @{
        "playwright" = @{
            "name" = "playwright"
            "command" = "npx"
            "args" = @("@playwright/mcp@latest")
            "description" = "Browser testing and UI automation"
            "enabled" = $true
        }
        "obsidian" = @{
            "name" = "obsidian"
            "command" = "npx"
            "args" = @("@kreateworld/mcp-obsidian@latest")
            "description" = "Knowledge management and documentation"
            "enabled" = $true
        }
        "brave-search" = @{
            "name" = "brave-search"
            "command" = "npx"
            "args" = @("@modelcontextprotocol/server-brave-search@latest")
            "description" = "Web research and market analysis"
            "enabled" = $true
        }
    }
    "installation_date" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    "installed_count" = $installedCount
}

$mcpConfigPath = Join-Path $claudeCodePath "mcp-config.json"
try {
    $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $mcpConfigPath -Encoding UTF8
    Write-Host "  ✓ Created global MCP configuration: $mcpConfigPath" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Failed to create MCP configuration: $_" -ForegroundColor Red
}

# Update Claude Code settings
Write-Host ""
Write-Host "[6/6] Updating Claude Code global settings..." -ForegroundColor Green

try {
    # Read existing settings
    $settings = @{}
    if (Test-Path $settingsPath) {
        $content = Get-Content $settingsPath -Raw
        if ($content) {
            $settings = $content | ConvertFrom-Json -AsHashtable
        }
    }
    
    # Update global MCP settings
    if (-not $settings.ContainsKey("globalSettings")) {
        $settings["globalSettings"] = @{}
    }
    
    $settings["globalSettings"]["mcpEnabled"] = $true
    $settings["globalSettings"]["mcpDirectory"] = $mcpDir
    $settings["globalSettings"]["mcpConfigPath"] = $mcpConfigPath
    $settings["globalSettings"]["mcpToolLimit"] = 5
    
    # Note: MCPs are now managed globally by Claude CLI
    if (-not $settings.ContainsKey("mcpServers")) {
        $settings["mcpServers"] = @{
            "_comment" = "MCPs are now managed globally via 'claude mcp' commands"
        }
    }
    
    # Write updated settings
    $json = $settings | ConvertTo-Json -Depth 10
    Set-Content -Path $settingsPath -Value $json -Encoding UTF8
    
    Write-Host "  ✓ Claude Code global settings updated successfully" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Failed to update settings: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Tier 1 MCPs global installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Installed $installedCount/3 MCPs globally:" -ForegroundColor Cyan
Write-Host "  • Playwright MCP - Browser testing and UI automation" -ForegroundColor White
Write-Host "  • Obsidian MCP - Knowledge management and documentation" -ForegroundColor White
Write-Host "  • Brave Search MCP - Web research and market analysis" -ForegroundColor White
Write-Host ""
Write-Host "Global MCP Directory: $mcpDir" -ForegroundColor Yellow
Write-Host "Global Configuration: $mcpConfigPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚡ MCPs are now available in ALL projects!" -ForegroundColor Green
Write-Host "Please restart Claude Code to activate the MCPs." -ForegroundColor Yellow