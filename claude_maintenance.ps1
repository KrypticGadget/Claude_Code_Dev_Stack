# Claude Code Maintenance Script - Prevents performance degradation
# Run this weekly or when Claude Code starts feeling slow
# Usage: .\claude_maintenance.ps1

Write-Host ""
Write-Host "Claude Code Maintenance Tool" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta
Write-Host ""

$totalCleaned = 0
$issues = @()

# 1. Check and fix .claude.json bloat
Write-Host "1. Checking .claude.json size..." -ForegroundColor Yellow
$jsonPath = "$env:USERPROFILE\.claude.json"
if (Test-Path $jsonPath) {
    $jsonSize = (Get-Item $jsonPath).Length / 1MB
    Write-Host "   Current size: $([Math]::Round($jsonSize, 2))MB" -ForegroundColor $(if($jsonSize -gt 5){"Red"}else{"Green"})
    
    if ($jsonSize -gt 5) {
        Write-Host "   WARNING: File too large! Creating backup and resetting..." -ForegroundColor Red
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$env:USERPROFILE\.claude.json.backup_$timestamp"
        Move-Item $jsonPath $backupPath -Force
        Write-Host "   Backup saved to: $backupPath" -ForegroundColor Gray
        Write-Host "   ✓ .claude.json reset - Claude will create fresh one" -ForegroundColor Green
        $totalCleaned += $jsonSize
        $issues += "Large .claude.json reset"
    }
} else {
    Write-Host "   No .claude.json found (will be created on next run)" -ForegroundColor Gray
}

# 2. Clean old state files
Write-Host ""
Write-Host "2. Cleaning old state files..." -ForegroundColor Yellow
$stateDir = "$env:USERPROFILE\.claude\state"
if (Test-Path $stateDir) {
    $oldFiles = Get-ChildItem $stateDir -Filter "*.json" -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
    
    if ($oldFiles.Count -gt 0) {
        $oldFiles | Remove-Item -Force
        Write-Host "   ✓ Removed $($oldFiles.Count) old state files" -ForegroundColor Green
        $issues += "$($oldFiles.Count) old state files"
    } else {
        Write-Host "   No old state files found" -ForegroundColor Gray
    }
}

# 3. Clean temp files
Write-Host ""
Write-Host "3. Cleaning temp files..." -ForegroundColor Yellow
$tempPatterns = @(
    "$env:USERPROFILE\*.tmp.*",
    "$env:USERPROFILE\.claude.json.tmp.*",
    "$env:USERPROFILE\.claude\*.tmp.*",
    "$env:TEMP\claude*"
)

$tempCount = 0
foreach ($pattern in $tempPatterns) {
    $temps = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    if ($temps) {
        $tempCount += $temps.Count
        $temps | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

if ($tempCount -gt 0) {
    Write-Host "   ✓ Removed $tempCount temp files" -ForegroundColor Green
    $issues += "$tempCount temp files"
} else {
    Write-Host "   No temp files found" -ForegroundColor Gray
}

# 4. Clean old todo files
Write-Host ""
Write-Host "4. Cleaning old todo files..." -ForegroundColor Yellow
$todoDir = "$env:USERPROFILE\.claude\todos"
if (Test-Path $todoDir) {
    $oldTodos = Get-ChildItem $todoDir -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) }
    
    if ($oldTodos.Count -gt 0) {
        $oldTodos | Remove-Item -Force
        Write-Host "   ✓ Removed $($oldTodos.Count) old todo files" -ForegroundColor Green
        $issues += "$($oldTodos.Count) old todos"
    } else {
        Write-Host "   No old todo files found" -ForegroundColor Gray
    }
}

# 5. Clean old logs
Write-Host ""
Write-Host "5. Cleaning old logs..." -ForegroundColor Yellow
$logsDir = "$env:USERPROFILE\.claude\logs"
if (Test-Path $logsDir) {
    $oldLogs = Get-ChildItem $logsDir -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) }
    
    if ($oldLogs.Count -gt 0) {
        $sizeMB = ($oldLogs | Measure-Object -Property Length -Sum).Sum / 1MB
        $oldLogs | Remove-Item -Force
        Write-Host "   ✓ Removed $($oldLogs.Count) old log files ($([Math]::Round($sizeMB, 2))MB)" -ForegroundColor Green
        $totalCleaned += $sizeMB
        $issues += "$($oldLogs.Count) old logs"
    } else {
        Write-Host "   No old log files found" -ForegroundColor Gray
    }
}

# 6. Check hook health
Write-Host ""
Write-Host "6. Checking hook health..." -ForegroundColor Yellow
$hooksDir = "$env:USERPROFILE\.claude\hooks"
if (Test-Path $hooksDir) {
    $problematicHooks = @("session_saver.py", "session_loader.py", "model_tracker.py")
    $foundProblematic = @()
    
    foreach ($hook in $problematicHooks) {
        $hookPath = "$hooksDir\$hook"
        if (Test-Path $hookPath) {
            # Check if it's the minimal version
            $content = Get-Content $hookPath -Raw
            if ($content -notmatch "Ultra-lightweight|minimal") {
                $foundProblematic += $hook
            }
        }
    }
    
    if ($foundProblematic.Count -gt 0) {
        Write-Host "   ⚠ Found non-minimal problematic hooks:" -ForegroundColor Yellow
        $foundProblematic | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
        Write-Host "   Run: .\manage_hooks.ps1 -Action minimal" -ForegroundColor Yellow
        $issues += "Problematic hooks detected"
    } else {
        Write-Host "   ✓ All hooks are optimized" -ForegroundColor Green
    }
}

# 7. Clean shell snapshots
Write-Host ""
Write-Host "7. Cleaning shell snapshots..." -ForegroundColor Yellow
$snapshotDir = "$env:USERPROFILE\.claude\shell-snapshots"
if (Test-Path $snapshotDir) {
    $snapshots = Get-ChildItem $snapshotDir -ErrorAction SilentlyContinue
    if ($snapshots.Count -gt 10) {
        # Keep only last 10 snapshots
        $toDelete = $snapshots | Sort-Object LastWriteTime | Select-Object -First ($snapshots.Count - 10)
        $toDelete | Remove-Item -Force
        Write-Host "   ✓ Removed $($toDelete.Count) old snapshots" -ForegroundColor Green
        $issues += "$($toDelete.Count) old snapshots"
    } else {
        Write-Host "   Snapshot count OK ($($snapshots.Count))" -ForegroundColor Gray
    }
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host "MAINTENANCE COMPLETE" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""

if ($issues.Count -gt 0) {
    Write-Host "Issues Fixed:" -ForegroundColor Green
    $issues | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }
    Write-Host ""
    Write-Host "Total space recovered: $([Math]::Round($totalCleaned, 2))MB" -ForegroundColor Cyan
} else {
    Write-Host "✓ System is clean and optimized!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Yellow
Write-Host "  • Run this script weekly" -ForegroundColor White
Write-Host "  • Use '.\manage_hooks.ps1 -Action minimal' for best performance" -ForegroundColor White
Write-Host "  • Exit debug mode when not needed (use 'claude' not 'claude --debug')" -ForegroundColor White
Write-Host ""

# Check if Claude Code is running
$claudeProcess = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($claudeProcess) {
    Write-Host "NOTE: Claude Code is currently running" -ForegroundColor Yellow
    Write-Host "  Restart Claude Code for changes to take full effect" -ForegroundColor Yellow
}

Write-Host ""