#!/usr/bin/env pwsh
# Claude Code Dev Stack - Installation Verifier for Windows
# Checks installation status

Write-Host "`n=== Claude Code Dev Stack - Installation Verifier ===" -ForegroundColor Cyan

# Define paths to check
$basePath = "$HOME\.claude-code-dev-stack"
$commandsPath = "$HOME\.claude-commands"
$mcpConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Check results
$results = @{
    AgentLibraries = $false
    Commands = $false
    GitHooks = $false
    MCPConfig = $false
    PathConfig = $false
}

Write-Host "`nChecking installation..." -ForegroundColor Yellow

# Check agent libraries
if (Test-Path "$basePath\agents") {
    $agentCount = (Get-ChildItem "$basePath\agents" -File -ErrorAction SilentlyContinue).Count
    if ($agentCount -gt 0) {
        Write-Host "  Agent libraries: Found ($agentCount files)" -ForegroundColor Green
        $results.AgentLibraries = $true
    }
    else {
        Write-Host "  Agent libraries: Empty directory" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  Agent libraries: Not installed" -ForegroundColor Red
}

# Check commands
if (Test-Path $commandsPath) {
    $cmdCount = (Get-ChildItem $commandsPath -File -ErrorAction SilentlyContinue).Count
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

# Check Git hooks
$gitHooksPath = git config --global --get core.hooksPath 2>$null
if ($gitHooksPath -and (Test-Path "$basePath\hooks")) {
    Write-Host "  Git hooks: Configured" -ForegroundColor Green
    $results.GitHooks = $true
}
else {
    Write-Host "  Git hooks: Not configured" -ForegroundColor Red
}

# Check MCP configuration
if (Test-Path $mcpConfigPath) {
    try {
        $config = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
        $mcpServers = @("filesystem", "github", "git", "postgres", "sqlite")
        $foundServers = @()
        
        foreach ($server in $mcpServers) {
            if ($config.mcpServers.PSObject.Properties[$server]) {
                $foundServers += $server
            }
        }
        
        if ($foundServers.Count -gt 0) {
            Write-Host "  MCP servers: Found ($($foundServers.Count) configured)" -ForegroundColor Green
            $results.MCPConfig = $true
        }
        else {
            Write-Host "  MCP servers: None configured" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  MCP servers: Error reading config" -ForegroundColor Red
    }
}
else {
    Write-Host "  MCP servers: Config file not found" -ForegroundColor Red
}

# Check PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
if ($currentPath -like "*$commandsPath*") {
    Write-Host "  PATH: Commands directory included" -ForegroundColor Green
    $results.PathConfig = $true
}
else {
    Write-Host "  PATH: Commands directory not in PATH" -ForegroundColor Red
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