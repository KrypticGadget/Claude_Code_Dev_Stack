# Claude Code Dev Stack v2.1 - Master Uninstaller
# Removes agents, commands, MCPs, and hooks with granular control

param(
    [switch]$Agents,
    [switch]$Commands,
    [switch]$MCPs,
    [switch]$Hooks,
    [switch]$All,
    [switch]$Force,
    [switch]$WhatIf,
    [switch]$Backup
)

$ErrorActionPreference = "Stop"
$script:exitCode = 0

# Colors
function Write-Header { param($Text) Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
function Write-Success { param($Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Warning { param($Text) Write-Host "⚠ $Text" -ForegroundColor Yellow }
function Write-Error { param($Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Info { param($Text) Write-Host "ℹ $Text" -ForegroundColor Blue }

# ASCII Art Banner
$banner = @"
╔═══════════════════════════════════════════════════════╗
║      Claude Code Dev Stack v2.1 - Uninstaller         ║
╚═══════════════════════════════════════════════════════╝
"@

Write-Host $banner -ForegroundColor Red

# Define paths
$projectClaudeDir = Join-Path $PWD ".claude"
$userClaudeDir = Join-Path $env:USERPROFILE ".claude"
$backupDir = Join-Path $env:USERPROFILE "claude-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Component arrays
$agentFiles = @(
    "agents/frontend-architect.md",
    "agents/backend-architect.md",
    "agents/database-architect.md",
    "agents/devops-architect.md",
    "agents/api-architect.md",
    "agents/security-architect.md",
    "agents/testing-architect.md",
    "agents/documentation-architect.md",
    "agents/ui-ux-designer.md",
    "agents/business-analyst.md",
    "agents/project-manager.md",
    "agents/quality-assurance.md",
    "agents/performance-engineer.md",
    "agents/data-scientist.md",
    "agents/mobile-developer.md",
    "agents/blockchain-developer.md",
    "agents/game-developer.md",
    "agents/embedded-systems.md",
    "agents/machine-learning.md",
    "agents/cloud-architect.md",
    "agents/solution-architect.md",
    "agents/integration-specialist.md",
    "agents/automation-engineer.md",
    "agents/compliance-officer.md",
    "agents/accessibility-specialist.md",
    "agents/localization-engineer.md",
    "agents/support-engineer.md",
    "agents/master-orchestrator.md"
)

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

$hookFiles = @(
    "hooks/pre-response.md",
    "hooks/post-response.md",
    "hooks/error-handler.md",
    "hooks/context-enhancer.md",
    "hooks/quality-checker.md"
)

$mcpNames = @(
    "playwright-mcp",
    "obsidian-mcp",
    "brave-search-mcp"
)

# Check if no parameters provided
if (-not ($Agents -or $Commands -or $MCPs -or $Hooks -or $All)) {
    Write-Header "Uninstall Menu"
    Write-Host "What would you like to uninstall?" -ForegroundColor Yellow
    Write-Host "[1] All components"
    Write-Host "[2] Agents only"
    Write-Host "[3] Commands only"
    Write-Host "[4] MCPs only"
    Write-Host "[5] Hooks only"
    Write-Host "[6] Custom selection"
    Write-Host "[0] Cancel"
    
    $choice = Read-Host "`nSelect option (0-6)"
    
    switch ($choice) {
        "0" { Write-Info "Uninstall cancelled"; exit 0 }
        "1" { $All = $true }
        "2" { $Agents = $true }
        "3" { $Commands = $true }
        "4" { $MCPs = $true }
        "5" { $Hooks = $true }
        "6" {
            Write-Host "`nSelect components to uninstall:" -ForegroundColor Yellow
            $Agents = (Read-Host "Remove Agents? (y/n)") -eq 'y'
            $Commands = (Read-Host "Remove Commands? (y/n)") -eq 'y'
            $MCPs = (Read-Host "Remove MCPs? (y/n)") -eq 'y'
            $Hooks = (Read-Host "Remove Hooks? (y/n)") -eq 'y'
        }
        default { Write-Error "Invalid option"; exit 2 }
    }
}

# If -All is specified, enable all components
if ($All) {
    $Agents = $Commands = $MCPs = $Hooks = $true
}

# Confirmation
if (-not $Force) {
    Write-Header "Components to Uninstall"
    if ($Agents) { Write-Host "• Agents (28 files)" -ForegroundColor Yellow }
    if ($Commands) { Write-Host "• Commands (10 files)" -ForegroundColor Yellow }
    if ($MCPs) { Write-Host "• MCPs (3 packages)" -ForegroundColor Yellow }
    if ($Hooks) { Write-Host "• Hooks (5 files)" -ForegroundColor Yellow }
    
    if ($Backup) {
        Write-Info "Backup will be created at: $backupDir"
    }
    
    $confirm = Read-Host "`nProceed with uninstall? (y/n)"
    if ($confirm -ne 'y') {
        Write-Info "Uninstall cancelled"
        exit 0
    }
}

# Create backup if requested
if ($Backup -and -not $WhatIf) {
    Write-Header "Creating Backup"
    try {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # Backup project .claude directory
        if (Test-Path $projectClaudeDir) {
            $projectBackup = Join-Path $backupDir "project-claude"
            Copy-Item -Path $projectClaudeDir -Destination $projectBackup -Recurse -Force
            Write-Success "Backed up project .claude directory"
        }
        
        # Backup user .claude directory
        if (Test-Path $userClaudeDir) {
            $userBackup = Join-Path $backupDir "user-claude"
            Copy-Item -Path $userClaudeDir -Destination $userBackup -Recurse -Force
            Write-Success "Backed up user .claude directory"
        }
        
        Write-Info "Backup location: $backupDir"
    }
    catch {
        Write-Error "Backup failed: $_"
        $script:exitCode = 1
    }
}

# Function to remove files
function Remove-ComponentFiles {
    param(
        [string]$ComponentType,
        [string[]]$Files
    )
    
    Write-Header "Removing $ComponentType"
    $removedCount = 0
    $failedCount = 0
    
    foreach ($file in $Files) {
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
                $script:exitCode = 1
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
                $script:exitCode = 1
            }
        }
    }
    
    Write-Info "Summary: $removedCount removed, $failedCount failed"
    return @{ Removed = $removedCount; Failed = $failedCount }
}

# Track overall results
$results = @{
    Agents = @{ Removed = 0; Failed = 0 }
    Commands = @{ Removed = 0; Failed = 0 }
    MCPs = @{ Removed = 0; Failed = 0 }
    Hooks = @{ Removed = 0; Failed = 0 }
}

# Remove Agents
if ($Agents) {
    $results.Agents = Remove-ComponentFiles -ComponentType "Agents" -Files $agentFiles
}

# Remove Commands
if ($Commands) {
    $results.Commands = Remove-ComponentFiles -ComponentType "Commands" -Files $commandFiles
}

# Remove Hooks
if ($Hooks) {
    $results.Hooks = Remove-ComponentFiles -ComponentType "Hooks" -Files $hookFiles
}

# Remove MCPs
if ($MCPs) {
    Write-Header "Removing MCPs"
    $mcpRemoved = 0
    $mcpFailed = 0
    
    # Check if claude CLI is available
    $claudeAvailable = Get-Command claude -ErrorAction SilentlyContinue
    
    if ($claudeAvailable) {
        # Get list of installed MCPs
        try {
            $installedMCPs = & claude mcp list 2>$null | Out-String
            
            foreach ($mcp in $mcpNames) {
                if ($installedMCPs -match $mcp) {
                    try {
                        if ($WhatIf) {
                            Write-Host "Would remove MCP: $mcp" -ForegroundColor DarkGray
                        } else {
                            & claude mcp remove $mcp 2>$null
                            Write-Success "Removed MCP: $mcp"
                        }
                        $mcpRemoved++
                    }
                    catch {
                        Write-Error "Failed to remove MCP: $mcp - $_"
                        $mcpFailed++
                        $script:exitCode = 1
                    }
                }
            }
        }
        catch {
            Write-Warning "Could not list MCPs. They may need to be removed manually."
            $script:exitCode = 1
        }
    } else {
        Write-Warning "Claude CLI not found. MCPs must be removed manually."
        $script:exitCode = 1
    }
    
    $results.MCPs = @{ Removed = $mcpRemoved; Failed = $mcpFailed }
    Write-Info "Summary: $mcpRemoved removed, $mcpFailed failed"
}

# Clean up empty directories
if (-not $WhatIf) {
    Write-Header "Cleaning Up Empty Directories"
    
    $dirsToCheck = @(
        (Join-Path $projectClaudeDir "agents"),
        (Join-Path $projectClaudeDir "commands"),
        (Join-Path $projectClaudeDir "hooks"),
        (Join-Path $userClaudeDir "agents"),
        (Join-Path $userClaudeDir "commands"),
        (Join-Path $userClaudeDir "hooks")
    )
    
    foreach ($dir in $dirsToCheck) {
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

# Final Summary
Write-Header "Uninstall Summary"
$totalRemoved = 0
$totalFailed = 0

foreach ($component in $results.Keys) {
    if ($results[$component].Removed -gt 0 -or $results[$component].Failed -gt 0) {
        $removed = $results[$component].Removed
        $failed = $results[$component].Failed
        $totalRemoved += $removed
        $totalFailed += $failed
        
        $status = if ($failed -eq 0) { "✓" } else { "⚠" }
        $color = if ($failed -eq 0) { "Green" } else { "Yellow" }
        
        Write-Host "$status $component`: $removed removed, $failed failed" -ForegroundColor $color
    }
}

Write-Host "`nTotal: $totalRemoved components removed, $totalFailed failed" -ForegroundColor Cyan

if ($WhatIf) {
    Write-Info "This was a dry run. No changes were made."
}

if ($Backup -and -not $WhatIf) {
    Write-Info "Backup saved to: $backupDir"
}

# Set exit code
if ($totalFailed -gt 0) {
    $exitCode = 1  # Partial success
} elseif ($totalRemoved -eq 0) {
    $exitCode = 2  # Nothing to remove
}

exit $exitCode