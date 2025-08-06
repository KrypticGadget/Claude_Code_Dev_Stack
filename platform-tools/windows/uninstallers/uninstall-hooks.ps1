# Simple Claude Code Hooks Uninstaller for Windows
# Removes hooks from ~/.claude/hooks

Write-Host ""
Write-Host "Claude Code Hooks Uninstaller" -ForegroundColor Red
Write-Host "==============================" -ForegroundColor Red
Write-Host ""

# Define path
$claudeDir = "$env:USERPROFILE\.claude"
$hooksDir = "$claudeDir\hooks"

Write-Host "Looking for hooks in: $hooksDir" -ForegroundColor Gray
Write-Host ""

# Check if hooks exist
if (-not (Test-Path $hooksDir)) {
    Write-Host "No hooks found to uninstall." -ForegroundColor Yellow
    return
}

# Count files
$hookFiles = Get-ChildItem $hooksDir -Filter "*.py" -File
$count = $hookFiles.Count

Write-Host "Found $count hook files to remove:" -ForegroundColor Yellow
Write-Host "  - $hooksDir" -ForegroundColor White
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
Write-Host "Uninstalling hooks..." -ForegroundColor Yellow

try {
    Remove-Item -Path $hooksDir -Recurse -Force -ErrorAction Stop
    Write-Host "  Removed: $count hook files" -ForegroundColor Green
    Write-Host ""
    Write-Host "Hooks uninstalled successfully!" -ForegroundColor Green
} catch {
    Write-Host "  Failed to remove hooks" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
return