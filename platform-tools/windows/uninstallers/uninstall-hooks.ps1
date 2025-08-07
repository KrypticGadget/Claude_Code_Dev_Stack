# Enhanced Claude Code Hooks Uninstaller v2.1
# Safely removes all hook components with backup

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║     Claude Code Enhanced Hooks Uninstaller v2.1 - FIXED       ║
║       Safely Removes All 19 Hooks with Complete Backup        ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Yellow

# Configuration
$claudeDir = "$env:USERPROFILE\.claude"
$hooksDir = "$claudeDir\hooks"
$audioDir = "$claudeDir\audio"
$logsDir = "$claudeDir\logs"
$stateDir = "$claudeDir\state"
$backupsDir = "$claudeDir\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Step 1: Check if hooks are installed
Write-Host "`n🔍 Checking installation..." -ForegroundColor Yellow

if (!(Test-Path $hooksDir)) {
    Write-Host "  ⚠ No hooks directory found at: $hooksDir" -ForegroundColor Yellow
    Write-Host "  Nothing to uninstall." -ForegroundColor Gray
    return 0
}

$installedHooks = Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue
$audioFiles = if (Test-Path $audioDir) { Get-ChildItem $audioDir -Filter "*.mp3" -ErrorAction SilentlyContinue } else { @() }

Write-Host "  Found: $($installedHooks.Count) hooks" -ForegroundColor Cyan
Write-Host "  Found: $($audioFiles.Count) audio files" -ForegroundColor Cyan

# Step 2: Confirm uninstallation
Write-Host "`n⚠ This will remove:" -ForegroundColor Yellow
Write-Host "  • All hook scripts in $hooksDir" -ForegroundColor White
Write-Host "  • All audio files in $audioDir" -ForegroundColor White
Write-Host "  • Hook-related logs in $logsDir" -ForegroundColor White
Write-Host "  • Session state in $stateDir" -ForegroundColor White

$confirm = Read-Host "`nDo you want to continue? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "`nUninstallation cancelled." -ForegroundColor Gray
    return 0
}

# Step 3: Create backup
Write-Host "`n💾 Creating backup..." -ForegroundColor Yellow

# Create backup directory
if (!(Test-Path $backupsDir)) {
    New-Item -ItemType Directory -Path $backupsDir -Force | Out-Null
}
$backupPath = "$backupsDir\uninstall_backup_$timestamp"
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Backup hooks
if ($installedHooks) {
    $hooksBackupDir = "$backupPath\hooks"
    New-Item -ItemType Directory -Path $hooksBackupDir -Force | Out-Null
    Copy-Item "$hooksDir\*.py" $hooksBackupDir -Force
    Write-Host "  ✓ Backed up $($installedHooks.Count) hooks" -ForegroundColor Green
}

# Backup audio files
if ($audioFiles.Count -gt 0) {
    $audioBackupDir = "$backupPath\audio"
    New-Item -ItemType Directory -Path $audioBackupDir -Force | Out-Null
    Copy-Item "$audioDir\*.mp3" $audioBackupDir -Force
    Write-Host "  ✓ Backed up $($audioFiles.Count) audio files" -ForegroundColor Green
}

# Backup .claude.json (COMPLETE VERSION)
$claudeJsonPath = "$env:USERPROFILE\.claude.json"
if (Test-Path $claudeJsonPath) {
    Copy-Item $claudeJsonPath "$backupPath\.claude.json" -Force
    Write-Host "  ✓ Backed up .claude.json (complete with hooks)" -ForegroundColor Green
    
    # Also check if it has hook configuration
    $settings = Get-Content $claudeJsonPath -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($settings.hooks) {
        Write-Host "    • Contains hook configuration" -ForegroundColor Gray
    }
}

# Backup state if exists
if (Test-Path $stateDir) {
    $stateFiles = Get-ChildItem $stateDir -File -ErrorAction SilentlyContinue
    if ($stateFiles) {
        $stateBackupDir = "$backupPath\state"
        New-Item -ItemType Directory -Path $stateBackupDir -Force | Out-Null
        Copy-Item "$stateDir\*" $stateBackupDir -Force -Recurse
        Write-Host "  ✓ Backed up state files" -ForegroundColor Green
    }
}

Write-Host "  Backup location: $backupPath" -ForegroundColor Cyan

# Step 4: Remove hook scripts
Write-Host "`n🗑️ Removing hooks..." -ForegroundColor Yellow

# List of all possible enhanced hooks (including test hook)
$allHooks = @(
    # Core integration hooks
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py",
    "slash_command_router.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    
    # Audio and notification
    "audio_player.py",
    "audio_notifier.py",
    
    # Session management
    "session_loader.py",
    "session_saver.py",
    
    # Quality and tracking
    "quality_gate.py",
    "model_tracker.py",
    "planning_trigger.py",
    
    # Pre/Post hooks
    "pre_command.py",
    "post_command.py",
    "pre_project.py",
    "post_project.py",
    
    # Base utilities
    "base_hook.py",
    
    # Debug hook
    "test_hook.py"
)

$removedCount = 0
foreach ($hook in $allHooks) {
    $hookPath = "$hooksDir\$hook"
    if (Test-Path $hookPath) {
        Remove-Item $hookPath -Force
        Write-Host "  ✓ Removed: $hook" -ForegroundColor Green
        $removedCount++
    }
}

Write-Host "  Removed: $removedCount hooks" -ForegroundColor Cyan

# Step 5: Remove audio files
Write-Host "`n🎵 Removing audio files..." -ForegroundColor Yellow

$audioCount = 0
if (Test-Path $audioDir) {
    Get-ChildItem $audioDir -Filter "*.mp3" | ForEach-Object {
        Remove-Item $_.FullName -Force
        $audioCount++
    }
    Write-Host "  ✓ Removed: $audioCount audio files" -ForegroundColor Green
    
    # Remove audio directory if empty
    if ((Get-ChildItem $audioDir -ErrorAction SilentlyContinue).Count -eq 0) {
        Remove-Item $audioDir -Force
        Write-Host "  ✓ Removed empty audio directory" -ForegroundColor Green
    }
}

# Step 6: Clean up logs
Write-Host "`n📝 Cleaning logs..." -ForegroundColor Yellow

$logsRemoved = 0
if (Test-Path $logsDir) {
    # Remove hook-related logs
    $logPatterns = @(
        "orchestration.jsonl",
        "mcp_operations.jsonl",
        "agent_routing.jsonl",
        "slash_commands.jsonl",
        "model_usage.jsonl",
        "test_hook.log",  # Added test hook log
        "audio_player.log",
        "session_*.log"
    )
    
    foreach ($pattern in $logPatterns) {
        $logFile = "$logsDir\$pattern"
        if (Test-Path $logFile) {
            Remove-Item $logFile -Force
            $logsRemoved++
        }
    }
    
    Write-Host "  ✓ Removed: $logsRemoved log files" -ForegroundColor Green
}

# Step 7: Clean up state
Write-Host "`n💾 Cleaning state..." -ForegroundColor Yellow

$stateRemoved = 0
if (Test-Path $stateDir) {
    # Remove hook-related state files
    $statePatterns = @(
        "agent_routing.json",
        "active_agents.json",
        "orchestration_plan.json",
        "mcp_state.json",
        "session_state.json"
    )
    
    foreach ($pattern in $statePatterns) {
        $stateFile = "$stateDir\$pattern"
        if (Test-Path $stateFile) {
            Remove-Item $stateFile -Force
            $stateRemoved++
        }
    }
    
    Write-Host "  ✓ Removed: $stateRemoved state files" -ForegroundColor Green
    
    # Remove state directory if empty
    if ((Get-ChildItem $stateDir -ErrorAction SilentlyContinue).Count -eq 0) {
        Remove-Item $stateDir -Force
        Write-Host "  ✓ Removed empty state directory" -ForegroundColor Green
    }
}

# Step 8: Update .claude.json
Write-Host "`n⚙️ Updating .claude.json configuration..." -ForegroundColor Yellow

$claudeJsonPath = "$env:USERPROFILE\.claude.json"
if (Test-Path $claudeJsonPath) {
    try {
        $settings = Get-Content $claudeJsonPath -Raw | ConvertFrom-Json
        
        # Check what's in settings before removing
        $hadHooks = $false
        $hadAgentSystem = $false
        $hadSlashCommands = $false
        
        if ($settings.PSObject.Properties["hooks"]) {
            $hadHooks = $true
        }
        if ($settings.PSObject.Properties["agentSystem"]) {
            $hadAgentSystem = $true
        }
        if ($settings.PSObject.Properties["slashCommands"]) {
            $hadSlashCommands = $true
        }
        
        # Remove all hook-related configurations
        if ($hadHooks) {
            $settings.PSObject.Properties.Remove("hooks")
            Write-Host "  ✓ Removed hooks configuration" -ForegroundColor Green
        }
        if ($hadAgentSystem) {
            $settings.PSObject.Properties.Remove("agentSystem")
            Write-Host "  ✓ Removed agent system configuration" -ForegroundColor Green
        }
        if ($hadSlashCommands) {
            $settings.PSObject.Properties.Remove("slashCommands")
            Write-Host "  ✓ Removed slash commands configuration" -ForegroundColor Green
        }
        
        # Save updated .claude.json without BOM
        $jsonContent = $settings | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText($claudeJsonPath, $jsonContent, [System.Text.UTF8Encoding]::new($false))
        
        if (!$hadHooks -and !$hadAgentSystem -and !$hadSlashCommands) {
            Write-Host "  • No hook configurations found in settings" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠ Could not update .claude.json: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  • No .claude.json found" -ForegroundColor Gray
}

# Step 9: Remove hooks directory if empty
if ((Get-ChildItem $hooksDir -ErrorAction SilentlyContinue).Count -eq 0) {
    Remove-Item $hooksDir -Force
    Write-Host "`n✓ Removed empty hooks directory" -ForegroundColor Green
}

# Step 10: Display summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  UNINSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Removal Summary:" -ForegroundColor Cyan
Write-Host "  • Hooks removed: $removedCount/20" -ForegroundColor White
Write-Host "  • Audio files removed: $audioCount" -ForegroundColor White
Write-Host "  • Logs cleaned: $logsRemoved" -ForegroundColor White
Write-Host "  • State files cleaned: $stateRemoved" -ForegroundColor White
Write-Host "  • Settings cleaned: $(if ($settings.PSObject.Properties["hooks"]) { "Yes" } else { "N/A" })" -ForegroundColor White

Write-Host "`n💾 Backup Information:" -ForegroundColor Yellow
Write-Host "  Location: $backupPath" -ForegroundColor White
Write-Host "  Contains: Hooks, audio, settings, and state" -ForegroundColor White

Write-Host "`n🔄 To Restore:" -ForegroundColor Cyan
Write-Host "  Option 1: Restore from backup" -ForegroundColor White
Write-Host "    • Copy files from: $backupPath" -ForegroundColor Gray
Write-Host "  Option 2: Fresh installation (RECOMMENDED)" -ForegroundColor White
Write-Host "    • Run: .\platform-tools\windows\installers\install-hooks.ps1" -ForegroundColor Gray
Write-Host "  Option 3: Use fix script for complete setup" -ForegroundColor White
Write-Host "    • Run: .\INSTALL_HOOKS_FIX.ps1" -ForegroundColor Gray

Write-Host "`n⚠️ Important Notes:" -ForegroundColor Yellow
Write-Host "  • Your backup is preserved at: $backupPath" -ForegroundColor White
Write-Host "  • Restart Claude Code after reinstalling hooks" -ForegroundColor White
Write-Host "  • Use --debug flag to verify hook operations" -ForegroundColor White

Write-Host "`n✅ Enhanced hooks have been safely removed with complete backup." -ForegroundColor Green

# Return success
return 0