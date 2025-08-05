# Claude Code Dev Stack v2.1 - Hooks Uninstaller
# Removes only hook files from project and user directories

param(
    [switch]$Force,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Header { param($Text) Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
function Write-Success { param($Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Warning { param($Text) Write-Host "⚠ $Text" -ForegroundColor Yellow }
function Write-Error { param($Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Info { param($Text) Write-Host "ℹ $Text" -ForegroundColor Blue }

Write-Host "`n🪝 Claude Code Hooks Uninstaller" -ForegroundColor Red

# Define paths
$projectClaudeDir = Join-Path $PWD ".claude"
$userClaudeDir = Join-Path $env:USERPROFILE ".claude"

# Hook files to remove
$hookFiles = @(
    "hooks/pre-response.md",
    "hooks/post-response.md",
    "hooks/error-handler.md",
    "hooks/context-enhancer.md",
    "hooks/quality-checker.md"
)

# Confirmation
if (-not $Force) {
    Write-Warning "This will remove 5 hook files from:"
    if (Test-Path $projectClaudeDir) { Write-Host "  • $projectClaudeDir" }
    if (Test-Path $userClaudeDir) { Write-Host "  • $userClaudeDir" }
    
    $confirm = Read-Host "`nProceed? (y/n)"
    if ($confirm -ne 'y') {
        Write-Info "Uninstall cancelled"
        exit 0
    }
}

Write-Header "Removing Hooks"
$removedCount = 0
$failedCount = 0

foreach ($file in $hookFiles) {
    # Check project directory
    $projectPath = Join-Path $projectClaudeDir $file
    if (Test-Path $projectPath) {
        try {
            if ($WhatIf) {
                Write-Host "Would remove: $projectPath" -ForegroundColor DarkGray
            } else {
                Remove-Item -Path $projectPath -Force
                Write-Success "Removed: $file (project)"
            }
            $removedCount++
        }
        catch {
            Write-Error "Failed to remove: $file (project) - $_"
            $failedCount++
        }
    }
    
    # Check user directory
    $userPath = Join-Path $userClaudeDir $file
    if (Test-Path $userPath) {
        try {
            if ($WhatIf) {
                Write-Host "Would remove: $userPath" -ForegroundColor DarkGray
            } else {
                Remove-Item -Path $userPath -Force
                Write-Success "Removed: $file (user)"
            }
            $removedCount++
        }
        catch {
            Write-Error "Failed to remove: $file (user) - $_"
            $failedCount++
        }
    }
}

# Clean up empty hooks directories
if (-not $WhatIf) {
    $hooksDirs = @(
        (Join-Path $projectClaudeDir "hooks"),
        (Join-Path $userClaudeDir "hooks")
    )
    
    foreach ($dir in $hooksDirs) {
        if ((Test-Path $dir) -and (Get-ChildItem $dir -Force).Count -eq 0) {
            try {
                Remove-Item -Path $dir -Force
                Write-Success "Removed empty directory: $dir"
            }
            catch {
                Write-Warning "Could not remove directory: $dir"
            }
        }
    }
}

# Summary
Write-Header "Summary"
Write-Host "Hooks removed: $removedCount" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "Failed: $failedCount" -ForegroundColor Red
    exit 1
}

if ($WhatIf) {
    Write-Info "This was a dry run. No changes were made."
}

exit 0