# Claude Code Dev Stack v3 Consolidation Script (PowerShell)
# ============================================================
# Windows PowerShell version of the consolidation script

param(
    [string]$RootDir = (Get-Location).Path,
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script configuration
$V3Dir = Join-Path $RootDir "Claude_Code_Dev_Stack_v3"
$BackupDir = Join-Path $RootDir "BACKUP_v3_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$LogFile = Join-Path $RootDir "consolidation_log.txt"

# Initialize log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $Timestamp = Get-Date -Format "HH:mm:ss"
    $LogEntry = "[$Timestamp] $Level`: $Message"
    
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-ConsolidationPrerequisites {
    Write-Log "Checking consolidation prerequisites..."
    
    # Check if v3 directory exists
    if (!(Test-Path $V3Dir)) {
        Write-Log "v3 directory not found: $V3Dir" "ERROR"
        return $false
    }
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log "PowerShell 5.0 or higher required" "ERROR"
        return $false
    }
    
    # Check disk space (rough estimate)
    $Drive = (Get-Item $RootDir).PSDrive
    $FreeSpace = $Drive.Free / 1GB
    if ($FreeSpace -lt 2) {
        Write-Log "Insufficient disk space. At least 2GB required" "WARNING"
    }
    
    Write-Log "Prerequisites check completed"
    return $true
}

function Backup-CurrentStructure {
    Write-Log "Creating backup of current structure..."
    
    try {
        # Create backup directory
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        
        # Backup root structure (excluding v3 and existing backups)
        $RootBackup = Join-Path $BackupDir "root_structure"
        New-Item -ItemType Directory -Path $RootBackup -Force | Out-Null
        
        Get-ChildItem -Path $RootDir | Where-Object {
            $_.Name -ne "Claude_Code_Dev_Stack_v3" -and 
            !$_.Name.StartsWith("BACKUP_") -and
            $_.Name -ne "consolidation_log.txt"
        } | ForEach-Object {
            $DestPath = Join-Path $RootBackup $_.Name
            if ($_.PSIsContainer) {
                Copy-Item -Path $_.FullName -Destination $DestPath -Recurse -Force
            } else {
                Copy-Item -Path $_.FullName -Destination $DestPath -Force
            }
        }
        
        # Backup v3 structure
        $V3Backup = Join-Path $BackupDir "v3_structure"
        Copy-Item -Path $V3Dir -Destination $V3Backup -Recurse -Force
        
        Write-Log "Backup created successfully at: $BackupDir"
        return $true
        
    } catch {
        Write-Log "Backup failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Get-ConsolidationPlan {
    Write-Log "Creating consolidation plan..."
    
    $Plan = @(
        @{
            Source = "core\agents"
            Target = "agents"
            Action = "MergeWithExisting"
            Priority = 1
        },
        @{
            Source = "core\commands"
            Target = "commands" 
            Action = "MergeWithExisting"
            Priority = 1
        },
        @{
            Source = "core\hooks"
            Target = "hooks"
            Action = "ReplaceAndBackup"
            Priority = 2
        },
        @{
            Source = "core\audio"
            Target = "audio"
            Action = "MoveNew"
            Priority = 3
        },
        @{
            Source = "core\orchestration"
            Target = "orchestration"
            Action = "MoveNew"
            Priority = 3
        },
        @{
            Source = "core\integrations"
            Target = "integrations"
            Action = "MergeWithExisting"
            Priority = 4
        },
        @{
            Source = "core\testing"
            Target = "testing"
            Action = "MoveNew"
            Priority = 4
        },
        @{
            Source = "apps"
            Target = "apps"
            Action = "MoveNew"
            Priority = 5
        },
        @{
            Source = "MASTER_SPEC_V3.md"
            Target = "MASTER_SPEC_V3.md"
            Action = "MoveNew"
            Priority = 1
        },
        @{
            Source = "requirements.txt"
            Target = "requirements_v3.txt"
            Action = "MoveRename"
            Priority = 2
        },
        @{
            Source = "setup_environment.py"
            Target = "setup_environment_v3.py"
            Action = "MoveRename"
            Priority = 2
        }
    )
    
    return $Plan | Sort-Object Priority
}

function Invoke-MigrationStep {
    param(
        [hashtable]$Step,
        [string]$V3Path,
        [string]$RootPath
    )
    
    $SourcePath = Join-Path $V3Path $Step.Source
    $TargetPath = Join-Path $RootPath $Step.Target
    
    Write-Log "Migrating: $($Step.Source) -> $($Step.Target) ($($Step.Action))"
    
    if (!(Test-Path $SourcePath)) {
        Write-Log "Source path not found: $SourcePath" "WARNING"
        return
    }
    
    switch ($Step.Action) {
        "MergeWithExisting" {
            Merge-Directories -Source $SourcePath -Target $TargetPath
        }
        "ReplaceAndBackup" {
            Replace-WithBackup -Source $SourcePath -Target $TargetPath
        }
        "MoveNew" {
            Move-IfNew -Source $SourcePath -Target $TargetPath
        }
        "MoveRename" {
            Copy-Item -Path $SourcePath -Destination $TargetPath -Force
        }
    }
}

function Merge-Directories {
    param([string]$Source, [string]$Target)
    
    if (!(Test-Path $Target)) {
        New-Item -ItemType Directory -Path $Target -Force | Out-Null
    }
    
    Get-ChildItem -Path $Source -Recurse | ForEach-Object {
        $RelativePath = $_.FullName.Substring($Source.Length + 1)
        $TargetItem = Join-Path $Target $RelativePath
        
        if ($_.PSIsContainer) {
            if (!(Test-Path $TargetItem)) {
                New-Item -ItemType Directory -Path $TargetItem -Force | Out-Null
            }
        } else {
            $TargetDir = Split-Path $TargetItem -Parent
            if (!(Test-Path $TargetDir)) {
                New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
            }
            
            if (Test-Path $TargetItem) {
                $BackupName = "$($_.Name).backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                $BackupPath = Join-Path (Split-Path $TargetItem -Parent) $BackupName
                Move-Item -Path $TargetItem -Destination $BackupPath -Force
            }
            
            Copy-Item -Path $_.FullName -Destination $TargetItem -Force
        }
    }
}

function Replace-WithBackup {
    param([string]$Source, [string]$Target)
    
    if (Test-Path $Target) {
        $BackupName = "$(Split-Path $Target -Leaf)_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        $BackupPath = Join-Path (Split-Path $Target -Parent) $BackupName
        Move-Item -Path $Target -Destination $BackupPath -Force
    }
    
    if (Test-Path $Source) {
        Copy-Item -Path $Source -Destination $Target -Recurse -Force
    }
}

function Move-IfNew {
    param([string]$Source, [string]$Target)
    
    if ((Test-Path $Source) -and !(Test-Path $Target)) {
        if ((Get-Item $Source).PSIsContainer) {
            Copy-Item -Path $Source -Destination $Target -Recurse -Force
        } else {
            Copy-Item -Path $Source -Destination $Target -Force
        }
    }
}

function Update-PathReferences {
    Write-Log "Updating path references..."
    
    $FileExtensions = @("*.py", "*.md", "*.json", "*.yaml", "*.yml", "*.sh", "*.bat", "*.ps1")
    
    foreach ($Extension in $FileExtensions) {
        Get-ChildItem -Path $RootDir -Filter $Extension -Recurse | Where-Object {
            $_.FullName -notlike "*Claude_Code_Dev_Stack_v3*" -and
            $_.FullName -notlike "*BACKUP_*" -and
            $_.FullName -notlike "*node_modules*" -and
            $_.FullName -notlike "*venv*" -and
            $_.FullName -notlike "*.git*"
        } | ForEach-Object {
            Update-FileReferences -FilePath $_.FullName
        }
    }
}

function Update-FileReferences {
    param([string]$FilePath)
    
    try {
        $Content = Get-Content -Path $FilePath -Raw -ErrorAction SilentlyContinue
        if (!$Content) { return }
        
        $OriginalContent = $Content
        
        # Path replacement patterns
        $Patterns = @{
            'Claude_Code_Dev_Stack_v3/core/agents' = 'agents'
            'Claude_Code_Dev_Stack_v3/core/commands' = 'commands'
            'Claude_Code_Dev_Stack_v3/core/hooks' = 'hooks'
            'Claude_Code_Dev_Stack_v3/core/' = ''
            'Claude_Code_Dev_Stack_v3/' = ''
            '../Claude_Code_Dev_Stack_v3/' = '../'
            './Claude_Code_Dev_Stack_v3/' = './'
        }
        
        foreach ($Pattern in $Patterns.GetEnumerator()) {
            $Content = $Content -replace [regex]::Escape($Pattern.Key), $Pattern.Value
        }
        
        if ($Content -ne $OriginalContent) {
            Set-Content -Path $FilePath -Value $Content -NoNewline
            Write-Log "Updated references in: $FilePath"
        }
        
    } catch {
        Write-Log "Failed to update $FilePath`: $($_.Exception.Message)" "WARNING"
    }
}

function New-ValidationScript {
    Write-Log "Creating validation script..."
    
    $ScriptsDir = Join-Path $RootDir "scripts"
    if (!(Test-Path $ScriptsDir)) {
        New-Item -ItemType Directory -Path $ScriptsDir -Force | Out-Null
    }
    
    $ValidationScript = Join-Path $ScriptsDir "validate_consolidation.ps1"
    
    $ValidationContent = @'
# Post-Consolidation Validation Script
param([string]$RootDir = (Get-Location).Path)

function Test-ConsolidatedStructure {
    $Results = @{}
    $RequiredDirs = @("agents", "commands", "hooks", "audio", "orchestration", "integrations", "testing", "apps")
    
    foreach ($Dir in $RequiredDirs) {
        $DirPath = Join-Path $RootDir $Dir
        $Results[$Dir] = @{
            Exists = Test-Path $DirPath
            FileCount = if (Test-Path $DirPath) { (Get-ChildItem -Path $DirPath -Recurse).Count } else { 0 }
        }
    }
    
    return $Results
}

function Test-AgentFiles {
    $AgentsDir = Join-Path $RootDir "agents"
    if (!(Test-Path $AgentsDir)) {
        return @{ Status = "Missing" }
    }
    
    $AgentFiles = Get-ChildItem -Path $AgentsDir -Filter "*.md" -Recurse
    return @{
        Status = "Found"
        Count = $AgentFiles.Count
        Files = $AgentFiles | ForEach-Object { $_.Name }
    }
}

function Test-CommandFiles {
    $CommandsDir = Join-Path $RootDir "commands"
    if (!(Test-Path $CommandsDir)) {
        return @{ Status = "Missing" }
    }
    
    $CommandFiles = Get-ChildItem -Path $CommandsDir -Filter "*.md" -Recurse
    return @{
        Status = "Found"
        Count = $CommandFiles.Count
        Files = $CommandFiles | ForEach-Object { $_.Name }
    }
}

function Test-HookFiles {
    $HooksDir = Join-Path $RootDir "hooks"
    if (!(Test-Path $HooksDir)) {
        return @{ Status = "Missing" }
    }
    
    $HookFiles = Get-ChildItem -Path $HooksDir -Filter "*.py" -Recurse
    return @{
        Status = "Found"
        Count = $HookFiles.Count
        Files = $HookFiles | ForEach-Object { $_.Name }
    }
}

# Run validation
Write-Host "Consolidation Validation Results:" -ForegroundColor Green
Write-Host "=" * 40

$StructureResults = Test-ConsolidatedStructure
Write-Host "Structure Check:" -ForegroundColor Yellow
$StructureResults | Format-Table -AutoSize

$AgentResults = Test-AgentFiles
Write-Host "Agent Files Check:" -ForegroundColor Yellow
$AgentResults | Format-List

$CommandResults = Test-CommandFiles
Write-Host "Command Files Check:" -ForegroundColor Yellow
$CommandResults | Format-List

$HookResults = Test-HookFiles
Write-Host "Hook Files Check:" -ForegroundColor Yellow
$HookResults | Format-List

Write-Host "Validation completed!" -ForegroundColor Green
'@
    
    Set-Content -Path $ValidationScript -Value $ValidationContent
    Write-Log "Validation script created: $ValidationScript"
}

function New-ConsolidationReport {
    Write-Log "Generating consolidation report..."
    
    $ReportPath = Join-Path $RootDir "CONSOLIDATION_REPORT.md"
    $LogContent = Get-Content -Path $LogFile -Raw
    
    $ReportContent = @"
# Claude Code Dev Stack v3 Consolidation Report

## Migration Summary
- **Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Backup Location**: $BackupDir
- **Status**: Completed

## Migration Log
``````
$LogContent
``````

## Validation
Run the validation script to verify consolidation:
``````powershell
.\scripts\validate_consolidation.ps1
``````

## Rollback Instructions
If issues are found, restore from backup:
``````powershell
# Remove consolidated files
Remove-Item -Path agents,commands,hooks,audio,orchestration,integrations,testing,apps -Recurse -Force -ErrorAction SilentlyContinue

# Restore from backup
Copy-Item -Path "$BackupDir\root_structure\*" -Destination . -Recurse -Force
Copy-Item -Path "$BackupDir\v3_structure" -Destination "Claude_Code_Dev_Stack_v3" -Recurse -Force
``````

## Next Steps
1. Run validation script
2. Test all functionality  
3. Update documentation
4. Remove backup after verification (optional)
"@
    
    Set-Content -Path $ReportPath -Value $ReportContent
    Write-Log "Consolidation report generated: $ReportPath"
}

# Main consolidation process
function Start-Consolidation {
    Write-Log "Starting Claude Code Dev Stack v3 Consolidation"
    Write-Log "Root Directory: $RootDir"
    Write-Log "v3 Directory: $V3Dir"
    
    if ($DryRun) {
        Write-Log "DRY RUN MODE - No actual changes will be made" "WARNING"
    }
    
    # Prerequisites check
    if (!(Test-ConsolidationPrerequisites)) {
        Write-Log "Prerequisites check failed" "ERROR"
        return $false
    }
    
    # Confirmation prompt
    if (!$Force -and !$DryRun) {
        $Confirmation = Read-Host "This will consolidate v3 structure into root level. Continue? (y/N)"
        if ($Confirmation -ne 'y' -and $Confirmation -ne 'Y') {
            Write-Log "Consolidation cancelled by user"
            return $false
        }
    }
    
    if (!$DryRun) {
        # Create backup
        if (!(Backup-CurrentStructure)) {
            Write-Log "Failed to create backup" "ERROR"
            return $false
        }
        
        # Execute migration
        $Plan = Get-ConsolidationPlan
        foreach ($Step in $Plan) {
            try {
                Invoke-MigrationStep -Step $Step -V3Path $V3Dir -RootPath $RootDir
            } catch {
                Write-Log "Migration step failed: $($Step.Source) - $($_.Exception.Message)" "ERROR"
                return $false
            }
        }
        
        # Update path references
        Update-PathReferences
        
        # Create validation script
        New-ValidationScript
        
        # Generate report
        New-ConsolidationReport
        
        Write-Log "Consolidation completed successfully!" "SUCCESS"
        
        Write-Host "`n" + "="*50 -ForegroundColor Green
        Write-Host "CONSOLIDATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
        Write-Host "="*50 -ForegroundColor Green
        Write-Host "Backup created at: $BackupDir" -ForegroundColor Yellow
        Write-Host "Run .\scripts\validate_consolidation.ps1 to verify" -ForegroundColor Yellow
        
    } else {
        # Dry run - just show plan
        Write-Log "DRY RUN - Migration plan:"
        $Plan = Get-ConsolidationPlan
        foreach ($Step in $Plan) {
            Write-Log "WOULD MIGRATE: $($Step.Source) -> $($Step.Target) ($($Step.Action))"
        }
    }
    
    return $true
}

# Execute consolidation
try {
    $Success = Start-Consolidation
    if ($Success) {
        exit 0
    } else {
        exit 1
    }
} catch {
    Write-Log "Unexpected error: $($_.Exception.Message)" "ERROR"
    exit 1
}