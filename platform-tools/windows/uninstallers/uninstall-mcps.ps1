# Simple Claude Code MCP Config Uninstaller for Windows
# Removes MCP configuration files from ~/.claude

Write-Host ""
Write-Host "Claude Code MCP Config Uninstaller" -ForegroundColor Red
Write-Host "===================================" -ForegroundColor Red
Write-Host ""

# Define paths
$claudeDir = "$env:USERPROFILE\.claude"
$settingsFile = "$claudeDir\settings.json"
$mcpFile = "$claudeDir\.mcp.json"

Write-Host "Looking for MCP configs in: $claudeDir" -ForegroundColor Gray
Write-Host ""

# Check what exists
$foundSomething = $false
$toRemove = @()

if (Test-Path $settingsFile) {
    $foundSomething = $true
    $toRemove += $settingsFile
}

if (Test-Path $mcpFile) {
    $foundSomething = $true
    $toRemove += $mcpFile
}

if (-not $foundSomething) {
    Write-Host "No MCP configuration files found to uninstall." -ForegroundColor Yellow
    return
}

Write-Host "Found configuration files to remove:" -ForegroundColor Yellow
foreach ($file in $toRemove) {
    Write-Host "  - $(Split-Path $file -Leaf)" -ForegroundColor White
}

Write-Host ""
Write-Host "This action cannot be undone!" -ForegroundColor Red
Write-Host "Note: This only removes config files. MCPs must be removed with 'claude mcp remove'" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'yes' to confirm uninstallation"

if ($confirmation -ne 'yes') {
    Write-Host ""
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    return
}

Write-Host ""
Write-Host "Uninstalling MCP configs..." -ForegroundColor Yellow

$removed = 0
$failed = 0

foreach ($file in $toRemove) {
    try {
        Remove-Item -Path $file -Force -ErrorAction Stop
        Write-Host "  Removed: $(Split-Path $file -Leaf)" -ForegroundColor Green
        $removed++
    } catch {
        Write-Host "  Failed to remove: $(Split-Path $file -Leaf)" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
if ($failed -eq 0) {
    Write-Host "MCP configs uninstalled successfully!" -ForegroundColor Green
} else {
    Write-Host "Completed with $failed errors." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Removing registered MCP servers..." -ForegroundColor Yellow

# Remove MCP servers from Claude Code
$mcpsToRemove = @("playwright", "obsidian", "web-search")
foreach ($mcp in $mcpsToRemove) {
    try {
        claude mcp remove $mcp 2>$null | Out-Null
        Write-Host "  Removed: $mcp" -ForegroundColor Green
    } catch {
        # Silently continue if MCP not found
    }
}

Write-Host ""
Write-Host "To reinstall MCPs, use:" -ForegroundColor Cyan
Write-Host "  .\platform-tools\windows\installers\install-mcps.ps1" -ForegroundColor White

Write-Host ""
return