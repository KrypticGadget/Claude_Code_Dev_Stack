# Simple Claude Code Agents Uninstaller for Windows
# Removes agents from ~/.claude/agents

Write-Host ""
Write-Host "Claude Code Agents Uninstaller" -ForegroundColor Red
Write-Host "===============================" -ForegroundColor Red
Write-Host ""

# Define path
$claudeDir = "$env:USERPROFILE\.claude"
$agentsDir = "$claudeDir\agents"

Write-Host "Looking for agents in: $agentsDir" -ForegroundColor Gray
Write-Host ""

# Check if agents exist
if (-not (Test-Path $agentsDir)) {
    Write-Host "No agents found to uninstall." -ForegroundColor Yellow
    return
}

# Count files
$agentFiles = Get-ChildItem $agentsDir -Filter "*.md" -File
$count = $agentFiles.Count

Write-Host "Found $count agent files to remove:" -ForegroundColor Yellow
Write-Host "  - $agentsDir" -ForegroundColor White
Write-Host ""
Write-Host "This action cannot be undone!" -ForegroundColor Red
Write-Host ""
$confirmation = Read-Host "Type 'yes' to confirm uninstallation"

if ($confirmation -ne 'yes') {
    Write-Host ""
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    return
}

Write-Host ""
Write-Host "Uninstalling agents..." -ForegroundColor Yellow

try {
    Remove-Item -Path $agentsDir -Recurse -Force -ErrorAction Stop
    Write-Host "  Removed: $count agent files" -ForegroundColor Green
    Write-Host ""
    Write-Host "Agents uninstalled successfully!" -ForegroundColor Green
} catch {
    Write-Host "  Failed to remove agents" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
return