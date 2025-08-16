# Emergency Recovery Script for Claude Code Dev Stack
# This script provides emergency recovery from the safety backup branch

param(
    [switch]$Force,
    [switch]$Validate,
    [string]$RestorePoint = "safety/pre-reorganization-backup"
)

Write-Host "🚨 CLAUDE CODE DEV STACK - EMERGENCY RECOVERY" -ForegroundColor Red -BackgroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow

# Function to check Git status
function Test-GitRepository {
    if (-not (Test-Path ".git")) {
        Write-Error "❌ Not in a Git repository. Please run from repository root."
        exit 1
    }
    
    Write-Host "✅ Git repository detected" -ForegroundColor Green
}

# Function to validate backup branch
function Test-BackupBranch {
    param($BranchName)
    
    $branchExists = git show-ref --verify --quiet "refs/heads/$BranchName"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Safety branch '$BranchName' not found!"
        Write-Host "Available branches:" -ForegroundColor Yellow
        git branch -a
        exit 1
    }
    
    Write-Host "✅ Safety branch '$BranchName' verified" -ForegroundColor Green
}

# Function to validate key files in backup
function Test-BackupIntegrity {
    param($BranchName)
    
    Write-Host "🔍 Validating backup integrity..." -ForegroundColor Cyan
    
    $keyFiles = @(
        "Claude_Code_Dev_Stack_v3/apps/web/package.json",
        ".claude-example/settings.json",
        "install.ps1",
        "docs/README_V3.md",
        "Claude_Code_Dev_Stack_v3/core/hooks/hooks/__init__.py"
    )
    
    $missingFiles = @()
    
    foreach ($file in $keyFiles) {
        $exists = git cat-file -e "${BranchName}:$file" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $file" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file" -ForegroundColor Red
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "❌ Critical files missing from backup:"
        $missingFiles | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
        exit 1
    }
    
    Write-Host "✅ Backup integrity verified" -ForegroundColor Green
}

# Function to create recovery branch
function New-RecoveryBranch {
    param($RestorePoint)
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $recoveryBranch = "emergency-recovery-$timestamp"
    
    Write-Host "🔄 Creating recovery branch: $recoveryBranch" -ForegroundColor Cyan
    
    # Switch to restore point
    git checkout $RestorePoint
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to checkout $RestorePoint"
        exit 1
    }
    
    # Create new recovery branch
    git checkout -b $recoveryBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to create recovery branch"
        exit 1
    }
    
    Write-Host "✅ Recovery branch created: $recoveryBranch" -ForegroundColor Green
    return $recoveryBranch
}

# Function to show recovery status
function Show-RecoveryStatus {
    Write-Host "📊 RECOVERY STATUS" -ForegroundColor Yellow
    Write-Host "==================" -ForegroundColor Yellow
    
    Write-Host "Current branch: " -NoNewline
    git branch --show-current
    
    Write-Host "Last 5 commits:" -ForegroundColor Cyan
    git log --oneline -5
    
    Write-Host "`n📁 Key directories status:" -ForegroundColor Cyan
    $keyDirs = @(
        "Claude_Code_Dev_Stack_v3",
        ".claude-example",
        ".github/workflows",
        "docs"
    )
    
    foreach ($dir in $keyDirs) {
        if (Test-Path $dir) {
            $fileCount = (Get-ChildItem $dir -Recurse -File).Count
            Write-Host "  ✅ $dir ($fileCount files)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $dir (missing)" -ForegroundColor Red
        }
    }
}

# Main execution
try {
    Test-GitRepository
    
    if ($Validate) {
        Write-Host "🔍 VALIDATION MODE - Testing backup without recovery" -ForegroundColor Cyan
        Test-BackupBranch $RestorePoint
        Test-BackupIntegrity $RestorePoint
        Write-Host "✅ Validation complete - backup is ready for emergency recovery" -ForegroundColor Green
        exit 0
    }
    
    # Check for uncommitted changes
    $status = git status --porcelain
    if ($status -and -not $Force) {
        Write-Warning "⚠️  Uncommitted changes detected:"
        git status --short
        Write-Host "`nUse -Force to proceed anyway, or commit/stash changes first." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "🚨 EMERGENCY RECOVERY INITIATED" -ForegroundColor Red
    Write-Host "This will restore repository to: $RestorePoint" -ForegroundColor Yellow
    
    if (-not $Force) {
        $confirm = Read-Host "Continue? (type 'RECOVER' to confirm)"
        if ($confirm -ne "RECOVER") {
            Write-Host "❌ Recovery cancelled" -ForegroundColor Yellow
            exit 0
        }
    }
    
    Test-BackupBranch $RestorePoint
    Test-BackupIntegrity $RestorePoint
    
    $recoveryBranch = New-RecoveryBranch $RestorePoint
    
    Show-RecoveryStatus
    
    Write-Host "`n🎉 EMERGENCY RECOVERY COMPLETE!" -ForegroundColor Green -BackgroundColor Black
    Write-Host "You are now on branch: $recoveryBranch" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Verify system functionality"
    Write-Host "2. Run validation scripts"
    Write-Host "3. If recovery is successful, merge to main branch"
    Write-Host "4. If issues persist, check REPOSITORY_SAFETY_BACKUP_STRATEGY.md"
    
} catch {
    Write-Error "❌ Recovery failed: $($_.Exception.Message)"
    Write-Host "📖 Check REPOSITORY_SAFETY_BACKUP_STRATEGY.md for manual recovery procedures" -ForegroundColor Yellow
    exit 1
}