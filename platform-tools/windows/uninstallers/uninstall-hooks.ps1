#!/usr/bin/env pwsh
# Claude Code Dev Stack - Git Hooks Uninstaller for Windows
# Removes Git hooks configuration

Write-Host "`n=== Claude Code Dev Stack - Git Hooks Uninstaller ===" -ForegroundColor Cyan

# Define path
$hooksPath = "$HOME\.claude-code-dev-stack\hooks"

# Show what will be removed
Write-Host "`nThis will remove:" -ForegroundColor Yellow
Write-Host "  - Git hooks directory at: $hooksPath"
Write-Host "  - Git global hooks configuration"

# Ask for confirmation
Write-Host "`nThis action cannot be undone!" -ForegroundColor Red
$confirmation = Read-Host "Are you sure you want to uninstall Git hooks? (yes/no)"

if ($confirmation -ne 'yes') {
    Write-Host "`nUninstall cancelled." -ForegroundColor Yellow
    return
}

Write-Host "`nUninstalling..." -ForegroundColor Cyan

# Remove hooks directory
if (Test-Path $hooksPath) {
    Write-Host "Removing hooks directory..." -ForegroundColor Yellow
    try {
        Remove-Item -Path $hooksPath -Recurse -Force
        Write-Host "  Hooks directory removed" -ForegroundColor Green
    }
    catch {
        Write-Host "  Error removing hooks: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "  Hooks directory not found" -ForegroundColor Yellow
}

# Clean Git configuration
Write-Host "Cleaning Git configuration..." -ForegroundColor Yellow
git config --global --unset core.hooksPath 2>$null
Write-Host "  Git configuration cleaned" -ForegroundColor Green

Write-Host "`n=== Git Hooks Uninstall Complete ===" -ForegroundColor Green