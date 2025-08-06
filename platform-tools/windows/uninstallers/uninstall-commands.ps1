# Simple Claude Code Commands Uninstaller for Windows
# Removes commands from ~/.claude/commands

Write-Host ""
Write-Host "Claude Code Commands Uninstaller" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red
Write-Host ""

# Define path
$claudeDir = "$env:USERPROFILE\.claude"
$commandsDir = "$claudeDir\commands"

Write-Host "Looking for commands in: $commandsDir" -ForegroundColor Gray
Write-Host ""

# Check if commands exist
if (-not (Test-Path $commandsDir)) {
    Write-Host "No commands found to uninstall." -ForegroundColor Yellow
    return
}

# Count files
$commandFiles = Get-ChildItem $commandsDir -Filter "*.md" -File
$count = $commandFiles.Count

Write-Host "Found $count command files to remove:" -ForegroundColor Yellow
Write-Host "  - $commandsDir" -ForegroundColor White
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
Write-Host "Uninstalling commands..." -ForegroundColor Yellow

try {
    Remove-Item -Path $commandsDir -Recurse -Force -ErrorAction Stop
    Write-Host "  Removed: $count command files" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commands uninstalled successfully!" -ForegroundColor Green
} catch {
    Write-Host "  Failed to remove commands" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
return