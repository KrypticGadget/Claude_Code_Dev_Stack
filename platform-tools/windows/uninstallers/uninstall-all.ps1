# Simple Claude Code Dev Stack Uninstaller for Windows
# Removes all components from ~/.claude

Write-Host ""
Write-Host "Claude Code Dev Stack - Complete Uninstaller" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

# Define what will be removed
$claudeDir = "$env:USERPROFILE\.claude"
Write-Host "Looking for files in: $claudeDir" -ForegroundColor Gray
$componentsToRemove = @(
    "$claudeDir\agents",
    "$claudeDir\commands",
    "$claudeDir\hooks",
    "$claudeDir\settings.json",
    "$claudeDir\.mcp.json"
)

# Check if anything is installed
$foundSomething = $false
foreach ($component in $componentsToRemove) {
    if (Test-Path $component) {
        $foundSomething = $true
        break
    }
}

if (-not $foundSomething) {
    Write-Host "Nothing to uninstall - no components found." -ForegroundColor Yellow
    return
}

# Show what will be removed
Write-Host "This will remove:" -ForegroundColor Yellow
foreach ($component in $componentsToRemove) {
    if (Test-Path $component) {
        if (Test-Path -Path $component -PathType Container) {
            $count = (Get-ChildItem $component -Recurse -File).Count
            Write-Host "  - $component ($count files)" -ForegroundColor White
        } else {
            Write-Host "  - $component" -ForegroundColor White
        }
    }
}

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
Write-Host "Uninstalling..." -ForegroundColor Yellow

# Remove components
$removed = 0
$failed = 0

foreach ($component in $componentsToRemove) {
    if (Test-Path $component) {
        try {
            Remove-Item -Path $component -Recurse -Force -ErrorAction Stop
            Write-Host "  Removed: $(Split-Path $component -Leaf)" -ForegroundColor Green
            $removed++
        } catch {
            Write-Host "  Failed to remove: $(Split-Path $component -Leaf)" -ForegroundColor Red
            Write-Host "    Error: $_" -ForegroundColor Red
            $failed++
        }
    }
}

# Clean up empty .claude directory if it exists
if (Test-Path $claudeDir) {
    $remaining = Get-ChildItem $claudeDir -Force
    if ($remaining.Count -eq 0) {
        try {
            Remove-Item -Path $claudeDir -Force
            Write-Host "  Removed empty .claude directory" -ForegroundColor Green
        } catch {
            Write-Host "  Could not remove .claude directory (may have other files)" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "Note: .claude directory still contains other files and was preserved" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Uninstall Summary:" -ForegroundColor Green
Write-Host "  Components removed: $removed" -ForegroundColor White
if ($failed -gt 0) {
    Write-Host "  Components failed: $failed" -ForegroundColor Red
}
Write-Host ""
Write-Host "Claude Code Dev Stack has been uninstalled." -ForegroundColor Green
Write-Host ""

# Return instead of exit
return