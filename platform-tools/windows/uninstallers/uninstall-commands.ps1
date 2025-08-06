#!/usr/bin/env pwsh
# Claude Code Dev Stack - Commands Uninstaller for Windows
# Removes command utilities

Write-Host "`n=== Claude Code Dev Stack - Commands Uninstaller ===" -ForegroundColor Cyan

# Define path
$commandsPath = "$HOME\.claude-commands"

# Check if commands exist
if (-not (Test-Path $commandsPath)) {
    Write-Host "`nCommands directory not found." -ForegroundColor Yellow
    Write-Host "Nothing to uninstall." -ForegroundColor Green
    return
}

# Show what will be removed
Write-Host "`nThis will remove:" -ForegroundColor Yellow
Write-Host "  - All command utilities at: $commandsPath"

# Ask for confirmation
Write-Host "`nThis action cannot be undone!" -ForegroundColor Red
$confirmation = Read-Host "Are you sure you want to uninstall commands? (yes/no)"

if ($confirmation -ne 'yes') {
    Write-Host "`nUninstall cancelled." -ForegroundColor Yellow
    return
}

# Remove commands
Write-Host "`nRemoving commands..." -ForegroundColor Cyan
try {
    Remove-Item -Path $commandsPath -Recurse -Force
    Write-Host "Commands removed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error removing commands: $_" -ForegroundColor Red
    return
}

# Clean PATH
Write-Host "Cleaning PATH environment variable..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
$paths = $currentPath -split ';' | Where-Object { $_ -ne $commandsPath }
$newPath = $paths -join ';'
[Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)
Write-Host "  PATH cleaned" -ForegroundColor Green

Write-Host "`n=== Commands Uninstall Complete ===" -ForegroundColor Green
Write-Host "Please restart your terminal for PATH changes to take effect." -ForegroundColor Yellow