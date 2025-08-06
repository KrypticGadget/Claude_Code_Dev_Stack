# Claude Code Dev Stack v2.1 - MCPs Uninstaller
# Removes Tier 1 Model Context Protocol packages

param(
    [switch]$Force,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Header { param($Text) Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
function Write-Success { param($Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Warning { param($Text) Write-Host "⚠ $Text" -ForegroundColor Yellow }
function Write-Error { param($Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Info { param($Text) Write-Host "ℹ $Text" -ForegroundColor Blue }

Write-Host "`n🔌 Claude Code MCPs Uninstaller" -ForegroundColor Red

# Tier 1 MCPs to remove
$mcpNames = @(
    "playwright-mcp",
    "obsidian-mcp",
    "brave-search-mcp"
)

# Check if claude CLI is available
$claudeAvailable = Get-Command claude -ErrorAction SilentlyContinue

if (-not $claudeAvailable) {
    Write-Error "Claude CLI not found. Please install Claude Desktop first."
    Write-Info "MCPs can only be managed through the Claude CLI."
    exit 2
}

# Get list of installed MCPs
Write-Header "Checking Installed MCPs"
try {
    $installedMCPs = & claude mcp list 2>$null | Out-String
    $foundMCPs = @()
    
    foreach ($mcp in $mcpNames) {
        if ($installedMCPs -match $mcp) {
            $foundMCPs += $mcp
            Write-Info "Found: $mcp"
        }
    }
    
    if ($foundMCPs.Count -eq 0) {
        Write-Warning "No Tier 1 MCPs found to uninstall"
        exit 0
    }
}
catch {
    Write-Error "Failed to list MCPs: $_"
    exit 2
}

# Confirmation
if (-not $Force) {
    Write-Warning "This will remove the following MCPs:"
    foreach ($mcp in $foundMCPs) {
        Write-Host "  • $mcp" -ForegroundColor Yellow
    }
    
    $confirm = Read-Host "`nProceed? (y/n)"
    if ($confirm -ne 'y') {
        Write-Info "Uninstall cancelled"
        exit 0
    }
}

Write-Header "Removing MCPs"
$removedCount = 0
$failedCount = 0

foreach ($mcp in $foundMCPs) {
    try {
        if ($WhatIf) {
            Write-Host "Would remove MCP: $mcp" -ForegroundColor DarkGray
            $removedCount++
        } else {
            Write-Host "Removing $mcp..." -NoNewline
            $output = & claude mcp remove $mcp 2>&1
            
            # Check if removal was successful
            $checkList = & claude mcp list 2>$null | Out-String
            if ($checkList -notmatch $mcp) {
                Write-Host " Done" -ForegroundColor Green
                Write-Success "Removed: $mcp"
                $removedCount++
            } else {
                Write-Host " Failed" -ForegroundColor Red
                Write-Error "Failed to remove: $mcp"
                $failedCount++
            }
        }
    }
    catch {
        Write-Error "Failed to remove $mcp`: $_"
        $failedCount++
    }
}

# Additional cleanup for MCP configurations
if (-not $WhatIf -and $removedCount -gt 0) {
    Write-Header "Cleaning MCP Configurations"
    
    $configPaths = @(
        "$env:APPDATA\Claude\mcp-configs",
        "$env:LOCALAPPDATA\Claude\mcp-data"
    )
    
    foreach ($path in $configPaths) {
        if (Test-Path $path) {
            foreach ($mcp in $foundMCPs) {
                $mcpConfig = Join-Path $path $mcp
                if (Test-Path $mcpConfig) {
                    try {
                        Remove-Item -Path $mcpConfig -Recurse -Force
                        Write-Success "Cleaned config: $mcp"
                    }
                    catch {
                        Write-Warning "Could not clean config for: $mcp"
                    }
                }
            }
        }
    }
}

# Summary
Write-Header "Summary"
Write-Host "MCPs removed: $removedCount" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "Failed: $failedCount" -ForegroundColor Red
    exit 1
}

if ($WhatIf) {
    Write-Info "This was a dry run. No changes were made."
}

# Restart recommendation
if ($removedCount -gt 0 -and -not $WhatIf) {
    Write-Info "Please restart Claude Desktop to complete the uninstall."
}

exit 0