#!/usr/bin/env pwsh
# Claude Code Dev Stack - MCP Uninstaller for Windows
# Removes MCP server configurations

Write-Host "`n=== Claude Code Dev Stack - MCP Uninstaller ===" -ForegroundColor Cyan

# Define MCP config path
$mcpConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Check if config exists
if (-not (Test-Path $mcpConfigPath)) {
    Write-Host "`nMCP configuration file not found." -ForegroundColor Yellow
    Write-Host "Nothing to uninstall." -ForegroundColor Green
    return
}

# Show what will be removed
Write-Host "`nThis will remove MCP server configurations for:" -ForegroundColor Yellow
Write-Host "  - filesystem"
Write-Host "  - github"
Write-Host "  - git"
Write-Host "  - postgres"
Write-Host "  - sqlite"

# Ask for confirmation
Write-Host "`nThis action cannot be undone!" -ForegroundColor Red
$confirmation = Read-Host "Are you sure you want to uninstall MCP configurations? (yes/no)"

if ($confirmation -ne 'yes') {
    Write-Host "`nUninstall cancelled." -ForegroundColor Yellow
    return
}

# Clean MCP configuration
Write-Host "`nCleaning MCP configuration..." -ForegroundColor Cyan
try {
    $config = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
    
    # Remove our MCP servers
    $servers = @("filesystem", "github", "git", "postgres", "sqlite")
    $removedCount = 0
    
    foreach ($server in $servers) {
        if ($config.mcpServers.PSObject.Properties[$server]) {
            $config.mcpServers.PSObject.Properties.Remove($server)
            Write-Host "  Removed: $server" -ForegroundColor Green
            $removedCount++
        }
    }
    
    if ($removedCount -gt 0) {
        $config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
        Write-Host "`nMCP configurations cleaned successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "`nNo MCP configurations found to remove." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error cleaning MCP configuration: $_" -ForegroundColor Red
    return
}

Write-Host "`n=== MCP Uninstall Complete ===" -ForegroundColor Green