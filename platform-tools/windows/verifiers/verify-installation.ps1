#!/usr/bin/env pwsh
# Claude Code Dev Stack - Installation Verifier for Windows
# Checks installation status

Write-Host "`n=== Claude Code Dev Stack - Installation Verifier ===" -ForegroundColor Cyan

# Define paths to check
$claudeDir = "$env:USERPROFILE\.claude"
$agentsPath = "$claudeDir\agents"
$commandsPath = "$claudeDir\commands"
$hooksPath = "$claudeDir\hooks"
$settingsPath = "$claudeDir\settings.json"
$mcpPath = "$claudeDir\.mcp.json"

# Check results
$results = @{
    Agents = $false
    Commands = $false
    Hooks = $false
    Settings = $false
    MCPConfig = $false
}

Write-Host "`nChecking installation..." -ForegroundColor Yellow

# Check agents
if (Test-Path $agentsPath) {
    $agentCount = (Get-ChildItem $agentsPath -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
    if ($agentCount -gt 0) {
        Write-Host "  Agents: Found ($agentCount files)" -ForegroundColor Green
        $results.Agents = $true
    }
    else {
        Write-Host "  Agents: Empty directory" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  Agents: Not installed" -ForegroundColor Red
}

# Check commands
if (Test-Path $commandsPath) {
    $cmdCount = (Get-ChildItem $commandsPath -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
    if ($cmdCount -gt 0) {
        Write-Host "  Commands: Found ($cmdCount files)" -ForegroundColor Green
        $results.Commands = $true
    }
    else {
        Write-Host "  Commands: Empty directory" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  Commands: Not installed" -ForegroundColor Red
}

# Check hooks
if (Test-Path $hooksPath) {
    $hookCount = (Get-ChildItem $hooksPath -Filter "*.py" -File -ErrorAction SilentlyContinue).Count
    if ($hookCount -gt 0) {
        Write-Host "  Hooks: Found ($hookCount files)" -ForegroundColor Green
        $results.Hooks = $true
    }
    else {
        Write-Host "  Hooks: Empty directory" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  Hooks: Not installed" -ForegroundColor Red
}

# Check settings.json
if (Test-Path $settingsPath) {
    Write-Host "  Settings: Found" -ForegroundColor Green
    $results.Settings = $true
}
else {
    Write-Host "  Settings: Not installed" -ForegroundColor Red
}

# Check MCP configuration
if (Test-Path $mcpPath) {
    Write-Host "  MCP Config: Found" -ForegroundColor Green
    $results.MCPConfig = $true
}
else {
    Write-Host "  MCP Config: Not installed" -ForegroundColor Red
}

# Summary
Write-Host "`n=== Installation Summary ===" -ForegroundColor Cyan

$installed = ($results.Values | Where-Object { $_ -eq $true }).Count
$total = $results.Count

if ($installed -eq $total) {
    Write-Host "Status: Fully installed ($installed/$total components)" -ForegroundColor Green
    Write-Host "`nClaude Code Dev Stack is ready to use!" -ForegroundColor Green
}
elseif ($installed -gt 0) {
    Write-Host "Status: Partially installed ($installed/$total components)" -ForegroundColor Yellow
    Write-Host "`nRun install scripts to complete installation." -ForegroundColor Yellow
}
else {
    Write-Host "Status: Not installed" -ForegroundColor Red
    Write-Host "`nRun install-all.ps1 to install Claude Code Dev Stack." -ForegroundColor Yellow
}

# Return status code
if ($installed -eq $total) {
    return 0  # Fully installed
}
elseif ($installed -gt 0) {
    return 1  # Partially installed
}
else {
    return 2  # Not installed
}