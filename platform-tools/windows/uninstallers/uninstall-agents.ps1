#!/usr/bin/env pwsh
# Claude Code Dev Stack - Agents Uninstaller for Windows
# Removes agent libraries

Write-Host "`n=== Claude Code Dev Stack - Agents Uninstaller ===" -ForegroundColor Cyan

# Define path
$agentsPath = "$HOME\.claude-code-dev-stack\agents"

# Check if agents exist
if (-not (Test-Path $agentsPath)) {
    Write-Host "`nAgents directory not found." -ForegroundColor Yellow
    Write-Host "Nothing to uninstall." -ForegroundColor Green
    return
}

# Show what will be removed
Write-Host "`nThis will remove:" -ForegroundColor Yellow
Write-Host "  - All agent libraries at: $agentsPath"

# Ask for confirmation
Write-Host "`nThis action cannot be undone!" -ForegroundColor Red
$confirmation = Read-Host "Are you sure you want to uninstall agents? (yes/no)"

if ($confirmation -ne 'yes') {
    Write-Host "`nUninstall cancelled." -ForegroundColor Yellow
    return
}

# Remove agents
Write-Host "`nRemoving agents..." -ForegroundColor Cyan
try {
    Remove-Item -Path $agentsPath -Recurse -Force
    Write-Host "Agents removed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error removing agents: $_" -ForegroundColor Red
    return
}

Write-Host "`n=== Agents Uninstall Complete ===" -ForegroundColor Green