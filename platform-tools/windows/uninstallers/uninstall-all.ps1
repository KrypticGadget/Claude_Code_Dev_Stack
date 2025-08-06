#!/usr/bin/env pwsh
# Claude Code Dev Stack - Complete Uninstaller for Windows
# Removes all installed components with confirmation

Write-Host "`n=== Claude Code Dev Stack - Complete Uninstaller ===" -ForegroundColor Cyan

# Define paths
$basePath = "$HOME\.claude-code-dev-stack"
$commandsPath = "$HOME\.claude-commands"
$mcpConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Show what will be removed
Write-Host "`nThis will remove:" -ForegroundColor Yellow
Write-Host "  - Agent libraries at: $basePath"
Write-Host "  - Command utilities at: $commandsPath"
Write-Host "  - Git hooks configuration"
Write-Host "  - MCP server configurations"
Write-Host "  - PATH environment entries"

# Ask for confirmation
Write-Host "`nThis action cannot be undone!" -ForegroundColor Red
$confirmation = Read-Host "Are you sure you want to uninstall? (yes/no)"

if ($confirmation -ne 'yes') {
    Write-Host "`nUninstall cancelled." -ForegroundColor Yellow
    return
}

Write-Host "`nUninstalling..." -ForegroundColor Cyan

# Remove agent libraries
if (Test-Path $basePath) {
    Write-Host "Removing agent libraries..." -ForegroundColor Yellow
    Remove-Item -Path $basePath -Recurse -Force
    Write-Host "  Agent libraries removed" -ForegroundColor Green
}

# Remove commands
if (Test-Path $commandsPath) {
    Write-Host "Removing command utilities..." -ForegroundColor Yellow
    Remove-Item -Path $commandsPath -Recurse -Force
    Write-Host "  Commands removed" -ForegroundColor Green
}

# Clean Git configuration
Write-Host "Cleaning Git configuration..." -ForegroundColor Yellow
git config --global --unset core.hooksPath 2>$null
Write-Host "  Git configuration cleaned" -ForegroundColor Green

# Clean MCP configuration
if (Test-Path $mcpConfigPath) {
    Write-Host "Cleaning MCP configuration..." -ForegroundColor Yellow
    try {
        $config = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
        
        # Remove our MCP servers
        $servers = @("filesystem", "github", "git", "postgres", "sqlite")
        foreach ($server in $servers) {
            if ($config.mcpServers.PSObject.Properties[$server]) {
                $config.mcpServers.PSObject.Properties.Remove($server)
            }
        }
        
        $config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
        Write-Host "  MCP configuration cleaned" -ForegroundColor Green
    }
    catch {
        Write-Host "  Warning: Could not clean MCP configuration" -ForegroundColor Yellow
    }
}

# Remove from PATH
Write-Host "Cleaning PATH environment variable..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
$paths = $currentPath -split ';' | Where-Object { 
    $_ -ne $commandsPath -and $_ -ne $basePath 
}
$newPath = $paths -join ';'
[Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)
Write-Host "  PATH cleaned" -ForegroundColor Green

Write-Host "`n=== Uninstall Complete ===" -ForegroundColor Green
Write-Host "Please restart your terminal for all changes to take effect." -ForegroundColor Yellow
Write-Host "Thank you for using Claude Code Dev Stack!" -ForegroundColor Cyan