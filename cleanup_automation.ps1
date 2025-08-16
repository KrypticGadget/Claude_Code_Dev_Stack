# Claude Code Dev Stack - Cleanup Automation (PowerShell)
# Comprehensive archive and cleanup automation for legacy files and test results
# Generated: August 16, 2025
# Version: 1.0

param(
    [string]$ProjectRoot = ".",
    [switch]$DryRun,
    [string[]]$Categories = @(),
    [switch]$Verbose
)

# Set up logging
$LogFile = "cleanup_automation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$ErrorActionPreference = "Continue"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Get-DirectorySize {
    param([string]$Path)
    try {
        $Size = (Get-ChildItem -Path $Path -Recurse -File | Measure-Object -Property Length -Sum).Sum
        return [math]::Max($Size, 0)
    }
    catch {
        return 0
    }
}

function Test-PathSafely {
    param([string]$Path)
    try {
        return Test-Path -Path $Path
    }
    catch {
        return $false
    }
}

# Initialize cleanup report
$CleanupReport = @{
    ExecutionDate = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    DryRun = $DryRun.IsPresent
    FilesProcessed = 0
    FilesArchived = 0
    FilesDeleted = 0
    SpaceRecovered = 0
    Errors = @()
    Operations = @()
}

# Define cleanup patterns
$CleanupPatterns = @{
    "test_results" = @{
        Patterns = @("*test*results*.json", "*_test_*.json", "validation_results.json", "final_demo_results.json", "hook_test_report*.json")
        ArchivePath = "test-results"
        Action = "archive"
        Description = "Test result JSON files"
    }
    "log_files" = @{
        Patterns = @("*.log")
        ArchivePath = "logs"
        Action = "archive_if_not_empty"
        Description = "Log files"
    }
    "cache_dirs" = @{
        Patterns = @("__pycache__")
        ArchivePath = $null
        Action = "delete"
        Description = "Python cache directories"
    }
    "legacy_scripts" = @{
        Patterns = @(
            "launch_mobile.bat", "launch_mobile.sh", "LAUNCH_MOBILE_NOW.ps1",
            "setup_ngrok.ps1", "cleanup_audio.ps1", "remove_duplicates.ps1"
        )
        ArchivePath = "legacy-scripts"
        Action = "archive"
        Description = "Legacy launcher and setup scripts"
    }
    "development_tests" = @{
        Patterns = @(
            "test_agents_simple.py", "test_all_agents_v3.py", "test_agent_routing.py",
            "test_audio_system.py", "test_error_handling.py", 
            "comprehensive_hook_test_framework.py", "test-installer.ps1"
        )
        ArchivePath = "development-tests"
        Action = "archive"
        Description = "Development and testing scripts"
    }
    "validation_scripts" = @{
        Patterns = @(
            "platform_validator.py", "validate_audio_system.py", 
            "validate_system_demo.py", "final_demo.py",
            "final_security_assessment.py", "validate-installers.sh"
        )
        ArchivePath = "validation-scripts"
        Action = "archive"
        Description = "System validation and demo scripts"
    }
    "legacy_docs" = @{
        Patterns = @(
            "test_orchestration_command.md", "V3_TEST_PROMPTS.md",
            "V3_COMPLETE_SYSTEM_TEST.md", "COMPLETE_TODO_LIST_V3_PHASES_3-10.md"
        )
        ArchivePath = "documentation/development-notes"
        Action = "archive"
        Description = "Legacy development documentation"
    }
}

function Initialize-ArchiveStructure {
    param([string]$ArchiveRoot)
    
    $ArchiveDirs = @(
        "test-results",
        "logs", 
        "legacy-scripts",
        "development-tests/agent-testing",
        "development-tests/system-validation",
        "validation-scripts",
        "documentation/development-notes",
        "documentation/v2-era",
        "documentation/completed-todos"
    )
    
    foreach ($Dir in $ArchiveDirs) {
        $FullPath = Join-Path $ArchiveRoot $Dir
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would create directory: $FullPath"
        }
        else {
            if (-not (Test-PathSafely $FullPath)) {
                try {
                    New-Item -Path $FullPath -ItemType Directory -Force | Out-Null
                    Write-Log "Created archive directory: $FullPath"
                }
                catch {
                    Write-Log "Failed to create directory $FullPath : $($_.Exception.Message)" "ERROR"
                    return $false
                }
            }
        }
    }
    return $true
}

function New-FileMetadata {
    param([string]$FilePath, [string]$Category)
    
    try {
        $FileInfo = Get-Item $FilePath
        $RelativePath = Resolve-Path $FilePath -Relative
        
        $Metadata = @{
            archive_date = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            original_location = $RelativePath
            category = $Category
            file_info = @{
                size_bytes = $FileInfo.Length
                modified_date = $FileInfo.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ss")
                format = $FileInfo.Extension.TrimStart('.').ToUpper()
            }
            preservation_reason = $CleanupPatterns[$Category].Description
        }
        
        return $Metadata
    }
    catch {
        Write-Log "Failed to generate metadata for $FilePath : $($_.Exception.Message)" "ERROR"
        return @{}
    }
}

function Move-FileToArchive {
    param([string]$FilePath, [string]$Category)
    
    try {
        $Config = $CleanupPatterns[$Category]
        $ArchiveSubdir = $Config.ArchivePath
        
        if (-not $ArchiveSubdir) {
            return $false
        }
        
        $ArchiveDir = Join-Path $ArchiveRoot $ArchiveSubdir
        
        # Add date subdirectory for test results
        if ($Category -eq "test_results") {
            $DateStr = Get-Date -Format "yyyy-MM-dd"
            $ArchiveDir = Join-Path $ArchiveDir $DateStr
        }
        
        $FileName = Split-Path $FilePath -Leaf
        $TargetPath = Join-Path $ArchiveDir $FileName
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would archive: $FilePath -> $TargetPath"
        }
        else {
            # Ensure directory exists
            if (-not (Test-PathSafely $ArchiveDir)) {
                New-Item -Path $ArchiveDir -ItemType Directory -Force | Out-Null
            }
            
            # Move file
            Move-Item -Path $FilePath -Destination $TargetPath -Force
            
            # Generate and save metadata
            $Metadata = New-FileMetadata -FilePath $TargetPath -Category $Category
            $MetadataPath = "$TargetPath.metadata.json"
            $Metadata | ConvertTo-Json -Depth 10 | Set-Content -Path $MetadataPath
            
            Write-Log "Archived: $FilePath -> $TargetPath"
        }
        
        $CleanupReport.FilesArchived++
        $CleanupReport.Operations += @{
            action = "archive"
            source = $FilePath
            target = if ($DryRun) { "DRY_RUN" } else { $TargetPath }
            category = $Category
        }
        
        return $true
    }
    catch {
        $ErrorMsg = "Failed to archive $FilePath : $($_.Exception.Message)"
        Write-Log $ErrorMsg "ERROR"
        $CleanupReport.Errors += $ErrorMsg
        return $false
    }
}

function Remove-FileOrDirectory {
    param([string]$Path, [string]$Category)
    
    try {
        $Size = 0
        if (Test-PathSafely $Path) {
            if ((Get-Item $Path).PSIsContainer) {
                $Size = Get-DirectorySize -Path $Path
            }
            else {
                $Size = (Get-Item $Path).Length
            }
        }
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would delete: $Path"
        }
        else {
            Remove-Item -Path $Path -Recurse -Force
            Write-Log "Deleted: $Path"
        }
        
        $CleanupReport.FilesDeleted++
        $CleanupReport.SpaceRecovered += $Size
        $CleanupReport.Operations += @{
            action = "delete"
            target = $Path
            category = $Category
            size_recovered = $Size
        }
        
        return $true
    }
    catch {
        $ErrorMsg = "Failed to delete $Path : $($_.Exception.Message)"
        Write-Log $ErrorMsg "ERROR"
        $CleanupReport.Errors += $ErrorMsg
        return $false
    }
}

function Find-FilesByPatterns {
    param([string[]]$Patterns, [string]$SearchDir = $ProjectRoot)
    
    $FoundFiles = @()
    
    foreach ($Pattern in $Patterns) {
        try {
            $Matches = Get-ChildItem -Path $SearchDir -Filter $Pattern -File -ErrorAction SilentlyContinue
            $FoundFiles += $Matches
        }
        catch {
            Write-Log "Error searching for pattern $Pattern : $($_.Exception.Message)" "WARNING"
        }
    }
    
    return $FoundFiles
}

function Find-DirectoriesByPatterns {
    param([string[]]$Patterns, [string]$SearchDir = $ProjectRoot)
    
    $FoundDirs = @()
    
    foreach ($Pattern in $Patterns) {
        try {
            $Matches = Get-ChildItem -Path $SearchDir -Filter $Pattern -Directory -Recurse -ErrorAction SilentlyContinue
            $FoundDirs += $Matches
        }
        catch {
            Write-Log "Error searching for directory pattern $Pattern : $($_.Exception.Message)" "WARNING"
        }
    }
    
    return $FoundDirs
}

function Invoke-CategoryProcessing {
    param([string]$Category, [hashtable]$Config)
    
    Write-Log "Processing category: $Category"
    
    # Find files or directories based on category
    if ($Category -eq "cache_dirs") {
        $Items = Find-DirectoriesByPatterns -Patterns $Config.Patterns
    }
    else {
        $Items = Find-FilesByPatterns -Patterns $Config.Patterns
    }
    
    Write-Log "Found $($Items.Count) items for $Category"
    
    foreach ($Item in $Items) {
        $CleanupReport.FilesProcessed++
        $ItemPath = $Item.FullName
        
        switch ($Config.Action) {
            "archive" {
                Move-FileToArchive -FilePath $ItemPath -Category $Category
            }
            "delete" {
                Remove-FileOrDirectory -Path $ItemPath -Category $Category
            }
            "archive_if_not_empty" {
                if ($Item.Length -gt 0) {
                    Move-FileToArchive -FilePath $ItemPath -Category $Category
                }
                else {
                    Remove-FileOrDirectory -Path $ItemPath -Category $Category
                }
            }
            "skip" {
                Write-Log "Skipping $ItemPath (requires manual handling)"
            }
            default {
                Write-Log "Unknown action for $ItemPath : $($Config.Action)" "WARNING"
            }
        }
    }
}

function New-ReadmeFiles {
    param([string]$ArchiveRoot)
    
    $ReadmeContent = @{
        "test-results" = @"
# Test Results Archive

This directory contains archived test results from Claude Code Dev Stack development.

## Organization
- Files are organized by date of execution
- Each test result file has accompanying metadata
- Results are preserved for debugging and regression analysis

## File Types
- `*test*results*.json`: Comprehensive test execution results
- `*.metadata.json`: File metadata and context information

## Usage
To reference historical test results:
1. Check the date-based subdirectories
2. Review metadata files for context
3. Use results for debugging or comparison with current tests
"@
        "legacy-scripts" = @"
# Legacy Scripts Archive

This directory contains deprecated scripts and tools that have been replaced or are no longer actively used.

## Categories
- Mobile launchers: Old mobile app launch scripts
- Setup tools: Development environment setup utilities
- Cleanup scripts: File management and cleanup tools

## Important Notes
- These scripts are preserved for reference only
- Check DEPRECATION_NOTES.md for replacement information
- Do not use these scripts in current development
"@
        "development-tests" = @"
# Development Tests Archive

This directory contains test scripts and frameworks used during development phases.

## Categories
- agent-testing/: Agent functionality testing scripts
- system-validation/: System-wide validation and testing
- platform-validation/: Cross-platform compatibility tests

## Usage Notes
- These scripts may be useful for reference when creating new tests
- Check metadata for dependencies and requirements
- Some scripts may need updates to work with current system
"@
        "documentation" = @"
# Documentation Archive

This directory contains historical documentation and development notes.

## Organization
- development-notes/: Notes from development phases
- v2-era/: Documentation from V2 system
- completed-todos/: Archived TODO lists and task tracking

## Preservation Purpose
- Historical context for system evolution
- Reference for design decisions
- Debugging and troubleshooting context
"@
    }
    
    foreach ($DirName in $ReadmeContent.Keys) {
        $ReadmePath = Join-Path $ArchiveRoot "$DirName/README.md"
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would create README: $ReadmePath"
        }
        else {
            $ReadmeDir = Split-Path $ReadmePath -Parent
            if (-not (Test-PathSafely $ReadmeDir)) {
                New-Item -Path $ReadmeDir -ItemType Directory -Force | Out-Null
            }
            
            Set-Content -Path $ReadmePath -Value $ReadmeContent[$DirName]
            Write-Log "Created README: $ReadmePath"
        }
    }
}

function New-CleanupReport {
    $ReportPath = "cleanup_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    
    # Add summary statistics
    $CleanupReport.Summary = @{
        total_files_processed = $CleanupReport.FilesProcessed
        files_archived = $CleanupReport.FilesArchived
        files_deleted = $CleanupReport.FilesDeleted
        space_recovered_mb = [math]::Round($CleanupReport.SpaceRecovered / 1MB, 2)
        errors_count = $CleanupReport.Errors.Count
        success_rate = if ($CleanupReport.FilesProcessed -gt 0) {
            [math]::Round(($CleanupReport.FilesProcessed - $CleanupReport.Errors.Count) / $CleanupReport.FilesProcessed * 100, 2)
        } else { 100 }
    }
    
    if ($DryRun) {
        Write-Log "[DRY RUN] Would save report: $ReportPath"
    }
    else {
        $CleanupReport | ConvertTo-Json -Depth 10 | Set-Content -Path $ReportPath
        Write-Log "Cleanup report saved: $ReportPath"
    }
    
    return $ReportPath
}

# Main execution
Write-Log "Starting Claude Code Dev Stack cleanup automation"
Write-Log "Project root: $(Resolve-Path $ProjectRoot)"
Write-Log "Dry run mode: $($DryRun.IsPresent)"

# Resolve paths
$ProjectRoot = Resolve-Path $ProjectRoot
$ArchiveRoot = Join-Path $ProjectRoot "ARCHIVE"

try {
    # Ensure archive structure exists
    if (-not (Initialize-ArchiveStructure -ArchiveRoot $ArchiveRoot)) {
        throw "Failed to initialize archive structure"
    }
    
    # Create README files
    New-ReadmeFiles -ArchiveRoot $ArchiveRoot
    
    # Determine categories to process
    if ($Categories.Count -eq 0) {
        $CategoriesToProcess = $CleanupPatterns.Keys
    }
    else {
        $CategoriesToProcess = $Categories
    }
    
    # Process each category
    foreach ($Category in $CategoriesToProcess) {
        if ($CleanupPatterns.ContainsKey($Category)) {
            Invoke-CategoryProcessing -Category $Category -Config $CleanupPatterns[$Category]
        }
        else {
            Write-Log "Unknown category: $Category" "WARNING"
        }
    }
    
    # Generate cleanup report
    $ReportPath = New-CleanupReport
    
    # Summary
    Write-Log "Cleanup automation completed successfully"
    Write-Log "Files processed: $($CleanupReport.FilesProcessed)"
    Write-Log "Files archived: $($CleanupReport.FilesArchived)"
    Write-Log "Files deleted: $($CleanupReport.FilesDeleted)"
    Write-Log "Space recovered: $([math]::Round($CleanupReport.SpaceRecovered / 1MB, 2)) MB"
    Write-Log "Errors: $($CleanupReport.Errors.Count)"
    
    if ($DryRun) {
        Write-Host "`nThis was a dry run - no files were actually moved or deleted." -ForegroundColor Yellow
        Write-Host "Run without -DryRun to execute the cleanup." -ForegroundColor Yellow
    }
    
    Write-Host "`nCleanup automation completed successfully!" -ForegroundColor Green
}
catch {
    Write-Log "Cleanup automation failed: $($_.Exception.Message)" "ERROR"
    Write-Host "Cleanup automation failed. Check logs for details." -ForegroundColor Red
    exit 1
}