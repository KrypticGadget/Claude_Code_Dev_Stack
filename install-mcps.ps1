# Tier 1 MCP Installer for Windows PowerShell
# Installs: Playwright MCP, Obsidian MCP, and Brave Search MCP

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== Tier 1 MCP Installer for Claude Code ===" -ForegroundColor Cyan
Write-Host "Installing: Playwright, Obsidian, and Brave Search MCPs" -ForegroundColor Yellow
Write-Host ""

# Check for Node.js and npm
Write-Host "[1/5] Checking Node.js/npm installation..." -ForegroundColor Green
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
Write-Host "[2/5] Detecting Claude Code installation..." -ForegroundColor Green
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

# Create MCP directory
$mcpDir = Join-Path $claudeCodePath "mcp"
if (-not (Test-Path $mcpDir)) {
    New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null
}

# Install Tier 1 MCPs
Write-Host ""
Write-Host "[3/5] Installing Tier 1 MCPs..." -ForegroundColor Green

$mcps = @(
    @{name="@modelcontextprotocol/server-playwright"; display="Playwright MCP"},
    @{name="@kreateworld/mcp-obsidian"; display="Obsidian MCP"},
    @{name="@modelcontextprotocol/server-brave-search"; display="Brave Search MCP"}
)

foreach ($mcp in $mcps) {
    Write-Host "  Installing $($mcp.display)..." -ForegroundColor Yellow
    try {
        $output = npm install -g $mcp.name 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $($mcp.display) installed successfully" -ForegroundColor DarkGray
        } else {
            throw "Installation failed: $output"
        }
    } catch {
        Write-Host "  ✗ Failed to install $($mcp.display): $_" -ForegroundColor Red
        # Continue with other installations
    }
}

# Download tier1-universal.json configuration
Write-Host ""
Write-Host "[4/5] Downloading MCP configuration..." -ForegroundColor Green
$configUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/mcp-configs/tier1-universal.json"
$configPath = Join-Path $mcpDir "tier1-universal.json"

try {
    Invoke-WebRequest -Uri $configUrl -OutFile $configPath -UseBasicParsing
    Write-Host "  ✓ Configuration downloaded successfully" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Failed to download configuration: $_" -ForegroundColor Red
    exit 1
}

# Update Claude Code settings
Write-Host ""
Write-Host "[5/5] Updating Claude Code settings..." -ForegroundColor Green

try {
    # Read existing settings
    $settings = @{}
    if (Test-Path $settingsPath) {
        $content = Get-Content $settingsPath -Raw
        if ($content) {
            $settings = $content | ConvertFrom-Json -AsHashtable
        }
    }
    
    # Ensure mcpServers section exists
    if (-not $settings.ContainsKey("mcpServers")) {
        $settings["mcpServers"] = @{}
    }
    
    # Load tier1 configuration
    $tier1Config = Get-Content $configPath -Raw | ConvertFrom-Json -AsHashtable
    
    # Merge MCP configurations
    if ($tier1Config.ContainsKey("mcpServers")) {
        foreach ($key in $tier1Config["mcpServers"].Keys) {
            $settings["mcpServers"][$key] = $tier1Config["mcpServers"][$key]
        }
    }
    
    # Write updated settings
    $json = $settings | ConvertTo-Json -Depth 10
    Set-Content -Path $settingsPath -Value $json -Encoding UTF8
    
    Write-Host "  ✓ Claude Code settings updated successfully" -ForegroundColor DarkGray
} catch {
    Write-Host "  ✗ Failed to update settings: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Tier 1 MCPs installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Installed MCPs:" -ForegroundColor Cyan
Write-Host "  • Playwright MCP - Web automation and testing" -ForegroundColor White
Write-Host "  • Obsidian MCP - Note-taking integration" -ForegroundColor White
Write-Host "  • Brave Search MCP - Web search capabilities" -ForegroundColor White
Write-Host ""
Write-Host "Please restart Claude Code to activate the MCPs." -ForegroundColor Yellow