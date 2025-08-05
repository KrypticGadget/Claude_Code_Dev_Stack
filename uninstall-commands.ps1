# Claude Code Dev Stack v2.1 - Commands Uninstaller
# Removes only command files from project and user directories

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

Write-Host "`n⚡ Claude Code Commands Uninstaller" -ForegroundColor Red

# Define paths
$projectClaudeDir = Join-Path $PWD ".claude"
$userClaudeDir = Join-Path $env:USERPROFILE ".claude"

# Command files to remove
$commandFiles = @(
    "commands/build-frontend.md",
    "commands/build-backend.md",
    "commands/setup-database.md",
    "commands/deploy-app.md",
    "commands/run-tests.md",
    "commands/generate-docs.md",
    "commands/analyze-security.md",
    "commands/optimize-performance.md",
    "commands/create-api.md",
    "commands/design-ui.md"
)

# Confirmation
if (-not $Force) {
    Write-Warning "This will remove 10 command files from:"
    if (Test-Path $projectClaudeDir) { Write-Host "  • $projectClaudeDir" }
    if (Test-Path $userClaudeDir) { Write-Host "  • $userClaudeDir" }
    
    $confirm = Read-Host "`nProceed? (y/n)"
    if ($confirm -ne 'y') {
        Write-Info "Uninstall cancelled"
        exit 0
    }
}

Write-Header "Removing Commands"
$removedCount = 0
$failedCount = 0

foreach ($file in $commandFiles) {
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

# Clean up empty commands directories
if (-not $WhatIf) {
    $commandsDirs = @(
        (Join-Path $projectClaudeDir "commands"),
        (Join-Path $userClaudeDir "commands")
    )
    
    foreach ($dir in $commandsDirs) {
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
Write-Host "Commands removed: $removedCount" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "Failed: $failedCount" -ForegroundColor Red
    exit 1
}

if ($WhatIf) {
    Write-Info "This was a dry run. No changes were made."
}

exit 0