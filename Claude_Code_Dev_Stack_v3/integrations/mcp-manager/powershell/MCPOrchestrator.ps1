# MCP Orchestrator - Master PowerShell orchestration system
# Complete lifecycle management for MCP Manager services on Windows
# 
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

#Requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Deploy", "Start", "Stop", "Restart", "Status", "Monitor", "Health", "Configure", "Backup", "Update", "Clean", "Logs", "Dashboard", "Reset")]
    [string]$Action = "Status",
    
    [ValidateSet("development", "staging", "production", "testing")]
    [string]$Environment = "development",
    
    [string]$ConfigPath = "",
    [string]$ServiceName = "MCPManager",
    [switch]$Force,
    [switch]$Background,
    [switch]$AutoRestart,
    [switch]$DetailedLogging,
    [switch]$SkipHealthCheck,
    [switch]$SkipValidation,
    [int]$Timeout = 300,
    [int]$HealthCheckInterval = 30,
    [int]$MonitorDuration = 0,
    [string]$LogLevel = "INFO"
)

# Module configuration
$ScriptRoot = $PSScriptRoot
$IntegrationRoot = Split-Path -Parent $ScriptRoot
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $IntegrationRoot)

# Component scripts
$ServiceManagerScript = Join-Path $ScriptRoot "MCPServiceManager.ps1"
$HealthMonitorScript = Join-Path $ScriptRoot "MCPHealthMonitor.ps1"
$ConfigManagerScript = Join-Path $ScriptRoot "MCPConfigManager.ps1"
$MCPManagerModule = Join-Path $ScriptRoot "MCPManager.psm1"

# Paths
$DefaultConfigPath = Join-Path $IntegrationRoot "config\mcp-services.yml"
$LogPath = Join-Path $IntegrationRoot "logs\orchestrator.log"
$StateFile = Join-Path $IntegrationRoot "data\orchestrator-state.json"
$LockFile = Join-Path $IntegrationRoot "data\orchestrator.lock"

# Use provided paths or defaults
$ConfigPath = if ($ConfigPath) { $ConfigPath } else { $DefaultConfigPath }

# Ensure required directories exist
$RequiredDirs = @(
    (Split-Path $LogPath -Parent),
    (Split-Path $StateFile -Parent),
    (Join-Path $IntegrationRoot "backups"),
    (Join-Path $IntegrationRoot "temp")
)

foreach ($dir in $RequiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Orchestrator state
$script:OrchestratorState = @{
    CurrentAction = $null
    StartTime = $null
    LastAction = $null
    LastActionTime = $null
    Environment = $Environment
    ServiceStatus = @{}
    HealthStatus = @{}
    Errors = @()
    Warnings = @()
    Statistics = @{
        TotalOperations = 0
        SuccessfulOperations = 0
        FailedOperations = 0
        AverageOperationTime = 0
    }
}

# Logging functions
function Write-OrchestratorLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG", "SUCCESS", "CRITICAL")]
        [string]$Level = "INFO",
        [string]$Component = "ORCHESTRATOR"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogEntry = "[$Timestamp] [$Component] [$Level] $Message"
    
    # Write to console with appropriate color
    $Color = switch ($Level) {
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
        "SUCCESS" { "Green" }
        "CRITICAL" { "Magenta" }
    }
    
    if ($DetailedLogging -or $Level -ne "DEBUG") {
        Write-Host $LogEntry -ForegroundColor $Color
    }
    
    # Write to log file
    try {
        Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
    }
    catch {
        # Ignore log file errors
    }
    
    # Track errors and warnings
    if ($Level -eq "ERROR") {
        $script:OrchestratorState.Errors += $Message
    }
    elseif ($Level -eq "WARN") {
        $script:OrchestratorState.Warnings += $Message
    }
}

# Lock file management for preventing concurrent operations
function New-OperationLock {
    param([string]$Operation)
    
    if (Test-Path $LockFile) {
        $LockInfo = Get-Content $LockFile | ConvertFrom-Json
        $LockAge = (Get-Date) - [datetime]$LockInfo.Created
        
        if ($LockAge.TotalMinutes -lt 30) {  # Lock expires after 30 minutes
            Write-OrchestratorLog "Another operation '$($LockInfo.Operation)' is in progress (PID: $($LockInfo.ProcessId))" -Level "ERROR"
            return $false
        }
        else {
            Write-OrchestratorLog "Removing stale lock file (age: $([math]::Round($LockAge.TotalMinutes, 1)) minutes)" -Level "WARN"
            Remove-Item $LockFile -Force
        }
    }
    
    $LockData = @{
        Operation = $Operation
        ProcessId = $PID
        Created = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Environment = $Environment
    }
    
    try {
        $LockData | ConvertTo-Json | Out-File -FilePath $LockFile -Encoding UTF8
        Write-OrchestratorLog "Operation lock acquired for: $Operation" -Level "DEBUG"
        return $true
    }
    catch {
        Write-OrchestratorLog "Failed to create operation lock: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Remove-OperationLock {
    try {
        if (Test-Path $LockFile) {
            Remove-Item $LockFile -Force
            Write-OrchestratorLog "Operation lock released" -Level "DEBUG"
        }
    }
    catch {
        Write-OrchestratorLog "Failed to remove operation lock: $($_.Exception.Message)" -Level "WARN"
    }
}

# State management
function Save-OrchestratorState {
    try {
        $script:OrchestratorState.LastActionTime = Get-Date
        $StateJson = $script:OrchestratorState | ConvertTo-Json -Depth 10
        $StateJson | Out-File -FilePath $StateFile -Encoding UTF8 -Force
    }
    catch {
        Write-OrchestratorLog "Failed to save orchestrator state: $($_.Exception.Message)" -Level "WARN"
    }
}

function Load-OrchestratorState {
    try {
        if (Test-Path $StateFile) {
            $SavedState = Get-Content $StateFile -Raw | ConvertFrom-Json
            
            # Merge with current state
            $script:OrchestratorState.LastAction = $SavedState.LastAction
            $script:OrchestratorState.LastActionTime = $SavedState.LastActionTime
            $script:OrchestratorState.Statistics = $SavedState.Statistics
            
            Write-OrchestratorLog "Loaded previous orchestrator state" -Level "DEBUG"
        }
    }
    catch {
        Write-OrchestratorLog "Failed to load orchestrator state: $($_.Exception.Message)" -Level "WARN"
    }
}

# Component execution functions
function Invoke-ServiceManager {
    param(
        [string]$Action,
        [hashtable]$Parameters = @{}
    )
    
    Write-OrchestratorLog "Executing service manager action: $Action" -Level "DEBUG"
    
    try {
        $Arguments = @("-Action", $Action, "-ServiceName", $ServiceName)
        
        foreach ($Key in $Parameters.Keys) {
            $Arguments += "-$Key"
            if ($Parameters[$Key] -ne $true) {
                $Arguments += $Parameters[$Key]
            }
        }
        
        if ($Force) { $Arguments += "-Force" }
        if ($Background) { $Arguments += "-Background" }
        
        $Result = & $ServiceManagerScript @Arguments
        $Success = $LASTEXITCODE -eq 0
        
        if ($Success) {
            Write-OrchestratorLog "Service manager action '$Action' completed successfully" -Level "SUCCESS"
        }
        else {
            Write-OrchestratorLog "Service manager action '$Action' failed with exit code $LASTEXITCODE" -Level "ERROR"
        }
        
        return @{
            Success = $Success
            ExitCode = $LASTEXITCODE
            Output = $Result
        }
    }
    catch {
        Write-OrchestratorLog "Service manager execution error: $($_.Exception.Message)" -Level "ERROR"
        return @{
            Success = $false
            ExitCode = -1
            Output = $null
        }
    }
}

function Invoke-HealthMonitor {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-OrchestratorLog "Executing health monitor..." -Level "DEBUG"
    
    try {
        $Arguments = @("-ConfigPath", $ConfigPath)
        
        foreach ($Key in $Parameters.Keys) {
            $Arguments += "-$Key"
            if ($Parameters[$Key] -ne $true) {
                $Arguments += $Parameters[$Key]
            }
        }
        
        if ($AutoRestart) { $Arguments += "-AutoRestart" }
        if ($DetailedLogging) { $Arguments += "-DetailedLogging" }
        
        $Result = & $HealthMonitorScript @Arguments
        $Success = $LASTEXITCODE -eq 0
        
        if ($Success) {
            Write-OrchestratorLog "Health monitor completed successfully" -Level "SUCCESS"
        }
        else {
            Write-OrchestratorLog "Health monitor failed with exit code $LASTEXITCODE" -Level "ERROR"
        }
        
        return @{
            Success = $Success
            ExitCode = $LASTEXITCODE
            Output = $Result
        }
    }
    catch {
        Write-OrchestratorLog "Health monitor execution error: $($_.Exception.Message)" -Level "ERROR"
        return @{
            Success = $false
            ExitCode = -1
            Output = $null
        }
    }
}

function Invoke-ConfigManager {
    param(
        [string]$Action,
        [hashtable]$Parameters = @{}
    )
    
    Write-OrchestratorLog "Executing config manager action: $Action" -Level "DEBUG"
    
    try {
        $Arguments = @("-Action", $Action, "-ConfigPath", $ConfigPath, "-Environment", $Environment)
        
        foreach ($Key in $Parameters.Keys) {
            $Arguments += "-$Key"
            if ($Parameters[$Key] -ne $true) {
                $Arguments += $Parameters[$Key]
            }
        }
        
        if ($Force) { $Arguments += "-Force" }
        if ($DetailedLogging) { $Arguments += "-Verbose" }
        
        $Result = & $ConfigManagerScript @Arguments
        $Success = $LASTEXITCODE -eq 0
        
        if ($Success) {
            Write-OrchestratorLog "Config manager action '$Action' completed successfully" -Level "SUCCESS"
        }
        else {
            Write-OrchestratorLog "Config manager action '$Action' failed with exit code $LASTEXITCODE" -Level "ERROR"
        }
        
        return @{
            Success = $Success
            ExitCode = $LASTEXITCODE
            Output = $Result
        }
    }
    catch {
        Write-OrchestratorLog "Config manager execution error: $($_.Exception.Message)" -Level "ERROR"
        return @{
            Success = $false
            ExitCode = -1
            Output = $null
        }
    }
}

# Orchestration workflows
function Start-DeploymentWorkflow {
    Write-OrchestratorLog "Starting deployment workflow for environment: $Environment" -Level "INFO"
    
    $Success = $true
    $Operations = @()
    
    try {
        # 1. Configuration validation and setup
        Write-OrchestratorLog "Phase 1: Configuration setup" -Level "INFO"
        
        if (-not (Test-Path $ConfigPath)) {
            Write-OrchestratorLog "Configuration not found, creating from template..." -Level "INFO"
            $ConfigResult = Invoke-ConfigManager -Action "Create" -Parameters @{ TemplateName = $Environment }
            $Operations += @{ Phase = "Config Creation"; Success = $ConfigResult.Success }
            if (-not $ConfigResult.Success) {
                $Success = $false
                Write-OrchestratorLog "Failed to create configuration" -Level "ERROR"
                return $false
            }
        }
        
        if (-not $SkipValidation) {
            $ValidationResult = Invoke-ConfigManager -Action "Validate"
            $Operations += @{ Phase = "Config Validation"; Success = $ValidationResult.Success }
            if (-not $ValidationResult.Success) {
                $Success = $false
                Write-OrchestratorLog "Configuration validation failed" -Level "ERROR"
                return $false
            }
        }
        
        # 2. Backup existing configuration
        Write-OrchestratorLog "Phase 2: Configuration backup" -Level "INFO"
        $BackupResult = Invoke-ConfigManager -Action "Backup"
        $Operations += @{ Phase = "Config Backup"; Success = $BackupResult.Success }
        
        # 3. Service installation/update
        Write-OrchestratorLog "Phase 3: Service management" -Level "INFO"
        
        # Install/update service
        $InstallResult = Invoke-ServiceManager -Action "Install"
        $Operations += @{ Phase = "Service Installation"; Success = $InstallResult.Success }
        if (-not $InstallResult.Success) {
            $Success = $false
            Write-OrchestratorLog "Service installation failed" -Level "ERROR"
            return $false
        }
        
        # Start service
        $StartResult = Invoke-ServiceManager -Action "Start"
        $Operations += @{ Phase = "Service Start"; Success = $StartResult.Success }
        if (-not $StartResult.Success) {
            $Success = $false
            Write-OrchestratorLog "Service start failed" -Level "ERROR"
            return $false
        }
        
        # 4. Health verification
        if (-not $SkipHealthCheck) {
            Write-OrchestratorLog "Phase 4: Health verification" -Level "INFO"
            Start-Sleep -Seconds 10  # Allow service to stabilize
            
            $HealthResult = Invoke-HealthMonitor -Parameters @{ RunOnce = $true }
            $Operations += @{ Phase = "Health Check"; Success = $HealthResult.Success }
            if (-not $HealthResult.Success) {
                Write-OrchestratorLog "Health check failed after deployment" -Level "WARN"
                # Don't fail deployment for health check issues
            }
        }
        
        # 5. Final verification
        Write-OrchestratorLog "Phase 5: Final verification" -Level "INFO"
        $StatusResult = Invoke-ServiceManager -Action "Status"
        $Operations += @{ Phase = "Status Verification"; Success = $StatusResult.Success }
        
        # Summary
        $SuccessfulOperations = ($Operations | Where-Object { $_.Success }).Count
        $TotalOperations = $Operations.Count
        
        Write-OrchestratorLog "Deployment workflow completed" -Level "INFO"
        Write-OrchestratorLog "Operations: $SuccessfulOperations/$TotalOperations successful" -Level "INFO"
        
        if ($Success) {
            Write-OrchestratorLog "Deployment successful!" -Level "SUCCESS"
        }
        else {
            Write-OrchestratorLog "Deployment failed!" -Level "ERROR"
        }
        
        return $Success
        
    }
    catch {
        Write-OrchestratorLog "Deployment workflow error: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Start-MonitoringWorkflow {
    param([int]$Duration = $MonitorDuration)
    
    Write-OrchestratorLog "Starting monitoring workflow" -Level "INFO"
    Write-OrchestratorLog "Health check interval: $HealthCheckInterval seconds" -Level "INFO"
    
    if ($Duration -gt 0) {
        Write-OrchestratorLog "Monitor duration: $Duration seconds" -Level "INFO"
    }
    else {
        Write-OrchestratorLog "Monitor duration: Infinite (Ctrl+C to stop)" -Level "INFO"
    }
    
    try {
        $MonitorParams = @{
            CheckInterval = $HealthCheckInterval
            Background = $Background
        }
        
        if ($Duration -gt 0) {
            # Run for specified duration
            $EndTime = (Get-Date).AddSeconds($Duration)
            
            while ((Get-Date) -lt $EndTime) {
                $HealthResult = Invoke-HealthMonitor -Parameters @{ RunOnce = $true; CheckInterval = $HealthCheckInterval }
                
                if (-not $HealthResult.Success) {
                    Write-OrchestratorLog "Health check failed during monitoring" -Level "WARN"
                }
                
                $RemainingTime = ($EndTime - (Get-Date)).TotalSeconds
                if ($RemainingTime -gt $HealthCheckInterval) {
                    Start-Sleep -Seconds $HealthCheckInterval
                }
                else {
                    Start-Sleep -Seconds $RemainingTime
                    break
                }
            }
        }
        else {
            # Run indefinitely
            $HealthResult = Invoke-HealthMonitor -Parameters $MonitorParams
        }
        
        Write-OrchestratorLog "Monitoring workflow completed" -Level "INFO"
        return $true
        
    }
    catch {
        Write-OrchestratorLog "Monitoring workflow error: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Start-CleanupWorkflow {
    Write-OrchestratorLog "Starting cleanup workflow" -Level "INFO"
    
    try {
        $CleanupOperations = @()
        
        # Stop service
        Write-OrchestratorLog "Stopping MCP Manager service..." -Level "INFO"
        $StopResult = Invoke-ServiceManager -Action "Stop"
        $CleanupOperations += @{ Operation = "Stop Service"; Success = $StopResult.Success }
        
        # Clean up temporary files
        Write-OrchestratorLog "Cleaning up temporary files..." -Level "INFO"
        $TempDir = Join-Path $IntegrationRoot "temp"
        if (Test-Path $TempDir) {
            try {
                Get-ChildItem -Path $TempDir -Recurse | Remove-Item -Force -Recurse
                Write-OrchestratorLog "Temporary files cleaned" -Level "SUCCESS"
                $CleanupOperations += @{ Operation = "Clean Temp Files"; Success = $true }
            }
            catch {
                Write-OrchestratorLog "Failed to clean temporary files: $($_.Exception.Message)" -Level "WARN"
                $CleanupOperations += @{ Operation = "Clean Temp Files"; Success = $false }
            }
        }
        
        # Clean up old log files (keep last 10)
        Write-OrchestratorLog "Cleaning up old log files..." -Level "INFO"
        $LogDir = Join-Path $IntegrationRoot "logs"
        if (Test-Path $LogDir) {
            try {
                $LogFiles = Get-ChildItem -Path $LogDir -Filter "*.log" | Sort-Object LastWriteTime -Descending
                if ($LogFiles.Count -gt 10) {
                    $FilesToDelete = $LogFiles | Select-Object -Skip 10
                    foreach ($File in $FilesToDelete) {
                        Remove-Item $File.FullName -Force
                    }
                    Write-OrchestratorLog "Cleaned up $($FilesToDelete.Count) old log files" -Level "SUCCESS"
                }
                $CleanupOperations += @{ Operation = "Clean Log Files"; Success = $true }
            }
            catch {
                Write-OrchestratorLog "Failed to clean log files: $($_.Exception.Message)" -Level "WARN"
                $CleanupOperations += @{ Operation = "Clean Log Files"; Success = $false }
            }
        }
        
        # Clean up old backups (keep last 20)
        Write-OrchestratorLog "Cleaning up old backups..." -Level "INFO"
        $BackupDir = Join-Path $IntegrationRoot "backups"
        if (Test-Path $BackupDir) {
            try {
                $BackupFiles = Get-ChildItem -Path $BackupDir -Filter "*.yml" | Sort-Object LastWriteTime -Descending
                if ($BackupFiles.Count -gt 20) {
                    $FilesToDelete = $BackupFiles | Select-Object -Skip 20
                    foreach ($File in $FilesToDelete) {
                        Remove-Item $File.FullName -Force
                    }
                    Write-OrchestratorLog "Cleaned up $($FilesToDelete.Count) old backup files" -Level "SUCCESS"
                }
                $CleanupOperations += @{ Operation = "Clean Backup Files"; Success = $true }
            }
            catch {
                Write-OrchestratorLog "Failed to clean backup files: $($_.Exception.Message)" -Level "WARN"
                $CleanupOperations += @{ Operation = "Clean Backup Files"; Success = $false }
            }
        }
        
        # Remove lock files
        Write-OrchestratorLog "Removing lock files..." -Level "INFO"
        try {
            $LockFiles = Get-ChildItem -Path (Join-Path $IntegrationRoot "data") -Filter "*.lock" -ErrorAction SilentlyContinue
            foreach ($LockFile in $LockFiles) {
                Remove-Item $LockFile.FullName -Force
            }
            Write-OrchestratorLog "Lock files removed" -Level "SUCCESS"
            $CleanupOperations += @{ Operation = "Remove Lock Files"; Success = $true }
        }
        catch {
            Write-OrchestratorLog "Failed to remove lock files: $($_.Exception.Message)" -Level "WARN"
            $CleanupOperations += @{ Operation = "Remove Lock Files"; Success = $false }
        }
        
        # Summary
        $SuccessfulOperations = ($CleanupOperations | Where-Object { $_.Success }).Count
        $TotalOperations = $CleanupOperations.Count
        
        Write-OrchestratorLog "Cleanup workflow completed" -Level "INFO"
        Write-OrchestratorLog "Operations: $SuccessfulOperations/$TotalOperations successful" -Level "INFO"
        
        return $SuccessfulOperations -eq $TotalOperations
        
    }
    catch {
        Write-OrchestratorLog "Cleanup workflow error: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Show-OrchestratorDashboard {
    Write-Host ""
    Write-Host "MCP Orchestrator Dashboard" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    
    # System information
    Write-Host "System Information:" -ForegroundColor Yellow
    Write-Host "  PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor White
    Write-Host "  Environment: $Environment" -ForegroundColor White
    Write-Host "  Configuration: $ConfigPath" -ForegroundColor Gray
    Write-Host "  Service Name: $ServiceName" -ForegroundColor White
    Write-Host ""
    
    # Service status
    Write-Host "Service Status:" -ForegroundColor Yellow
    try {
        $StatusResult = Invoke-ServiceManager -Action "Status"
        if ($StatusResult.Success) {
            Write-Host "  Status: Available" -ForegroundColor Green
        }
        else {
            Write-Host "  Status: Error" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  Status: Unknown" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Configuration status
    Write-Host "Configuration Status:" -ForegroundColor Yellow
    if (Test-Path $ConfigPath) {
        Write-Host "  Configuration: Found" -ForegroundColor Green
        $ConfigInfo = Get-Item $ConfigPath
        Write-Host "  Modified: $($ConfigInfo.LastWriteTime)" -ForegroundColor Gray
        Write-Host "  Size: $($ConfigInfo.Length) bytes" -ForegroundColor Gray
    }
    else {
        Write-Host "  Configuration: Not Found" -ForegroundColor Red
    }
    Write-Host ""
    
    # Orchestrator state
    if ($script:OrchestratorState.LastAction) {
        Write-Host "Last Operation:" -ForegroundColor Yellow
        Write-Host "  Action: $($script:OrchestratorState.LastAction)" -ForegroundColor White
        Write-Host "  Time: $($script:OrchestratorState.LastActionTime)" -ForegroundColor Gray
    }
    
    if ($script:OrchestratorState.Statistics.TotalOperations -gt 0) {
        Write-Host ""
        Write-Host "Statistics:" -ForegroundColor Yellow
        Write-Host "  Total Operations: $($script:OrchestratorState.Statistics.TotalOperations)" -ForegroundColor White
        Write-Host "  Successful: $($script:OrchestratorState.Statistics.SuccessfulOperations)" -ForegroundColor Green
        Write-Host "  Failed: $($script:OrchestratorState.Statistics.FailedOperations)" -ForegroundColor Red
    }
    
    if ($script:OrchestratorState.Errors.Count -gt 0) {
        Write-Host ""
        Write-Host "Recent Errors:" -ForegroundColor Red
        foreach ($Error in $script:OrchestratorState.Errors | Select-Object -Last 5) {
            Write-Host "  - $Error" -ForegroundColor Red
        }
    }
    
    if ($script:OrchestratorState.Warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "Recent Warnings:" -ForegroundColor Yellow
        foreach ($Warning in $script:OrchestratorState.Warnings | Select-Object -Last 5) {
            Write-Host "  - $Warning" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Available Actions:" -ForegroundColor Yellow
    Write-Host "  Deploy    - Full deployment workflow" -ForegroundColor Gray
    Write-Host "  Start     - Start MCP Manager service" -ForegroundColor Gray
    Write-Host "  Stop      - Stop MCP Manager service" -ForegroundColor Gray
    Write-Host "  Restart   - Restart MCP Manager service" -ForegroundColor Gray
    Write-Host "  Monitor   - Start health monitoring" -ForegroundColor Gray
    Write-Host "  Configure - Configure services" -ForegroundColor Gray
    Write-Host "  Clean     - Cleanup temporary files" -ForegroundColor Gray
    Write-Host "  Reset     - Full reset and redeploy" -ForegroundColor Gray
    Write-Host ""
}

# Execution tracking
function Start-OperationTracking {
    param([string]$Operation)
    
    $script:OrchestratorState.CurrentAction = $Operation
    $script:OrchestratorState.StartTime = Get-Date
    $script:OrchestratorState.Statistics.TotalOperations++
    
    Write-OrchestratorLog "Starting operation: $Operation" -Level "INFO"
}

function Complete-OperationTracking {
    param([bool]$Success)
    
    if ($script:OrchestratorState.StartTime) {
        $Duration = (Get-Date) - $script:OrchestratorState.StartTime
        $script:OrchestratorState.LastAction = $script:OrchestratorState.CurrentAction
        
        if ($Success) {
            $script:OrchestratorState.Statistics.SuccessfulOperations++
            Write-OrchestratorLog "Operation completed successfully in $([math]::Round($Duration.TotalSeconds, 2)) seconds" -Level "SUCCESS"
        }
        else {
            $script:OrchestratorState.Statistics.FailedOperations++
            Write-OrchestratorLog "Operation failed after $([math]::Round($Duration.TotalSeconds, 2)) seconds" -Level "ERROR"
        }
        
        $script:OrchestratorState.CurrentAction = $null
        $script:OrchestratorState.StartTime = $null
    }
}

# Main execution
try {
    Write-Host "MCP Orchestrator - Master PowerShell Orchestration System" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host ""
    
    # Initialize
    Load-OrchestratorState
    
    # Check for operation lock
    if (-not (New-OperationLock -Operation $Action)) {
        exit 1
    }
    
    # Start operation tracking
    Start-OperationTracking -Operation $Action
    
    $OperationSuccess = $false
    
    try {
        switch ($Action.ToLower()) {
            "deploy" {
                $OperationSuccess = Start-DeploymentWorkflow
            }
            
            "start" {
                $Result = Invoke-ServiceManager -Action "Start"
                $OperationSuccess = $Result.Success
            }
            
            "stop" {
                $Result = Invoke-ServiceManager -Action "Stop"
                $OperationSuccess = $Result.Success
            }
            
            "restart" {
                $Result = Invoke-ServiceManager -Action "Restart"
                $OperationSuccess = $Result.Success
            }
            
            "status" {
                Show-OrchestratorDashboard
                $OperationSuccess = $true
            }
            
            "monitor" {
                $OperationSuccess = Start-MonitoringWorkflow -Duration $MonitorDuration
            }
            
            "health" {
                $Result = Invoke-HealthMonitor -Parameters @{ RunOnce = $true }
                $OperationSuccess = $Result.Success
            }
            
            "configure" {
                $Result = Invoke-ConfigManager -Action "Status"
                $OperationSuccess = $Result.Success
            }
            
            "backup" {
                $Result = Invoke-ConfigManager -Action "Backup"
                $OperationSuccess = $Result.Success
            }
            
            "clean" {
                $OperationSuccess = Start-CleanupWorkflow
            }
            
            "reset" {
                Write-OrchestratorLog "Starting reset workflow..." -Level "INFO"
                
                # Stop service
                $StopResult = Invoke-ServiceManager -Action "Stop"
                
                # Cleanup
                $CleanResult = Start-CleanupWorkflow
                
                # Redeploy
                $DeployResult = Start-DeploymentWorkflow
                
                $OperationSuccess = $StopResult.Success -and $CleanResult -and $DeployResult
            }
            
            "logs" {
                Write-Host "Recent Orchestrator Logs:" -ForegroundColor Yellow
                if (Test-Path $LogPath) {
                    Get-Content $LogPath -Tail 50 | ForEach-Object {
                        $Color = "White"
                        if ($_ -match "\[ERROR\]") { $Color = "Red" }
                        elseif ($_ -match "\[WARN\]") { $Color = "Yellow" }
                        elseif ($_ -match "\[SUCCESS\]") { $Color = "Green" }
                        Write-Host $_ -ForegroundColor $Color
                    }
                }
                else {
                    Write-Host "No log file found" -ForegroundColor Gray
                }
                $OperationSuccess = $true
            }
            
            "dashboard" {
                Show-OrchestratorDashboard
                $OperationSuccess = $true
            }
            
            default {
                Write-OrchestratorLog "Unknown action: $Action" -Level "ERROR"
                Write-Host "Valid actions: Deploy, Start, Stop, Restart, Status, Monitor, Health, Configure, Backup, Clean, Reset, Logs, Dashboard" -ForegroundColor Yellow
                $OperationSuccess = $false
            }
        }
    }
    finally {
        # Complete operation tracking
        Complete-OperationTracking -Success $OperationSuccess
        
        # Save state
        Save-OrchestratorState
        
        # Remove lock
        Remove-OperationLock
    }
    
    exit $(if ($OperationSuccess) { 0 } else { 1 })
    
}
catch {
    Write-OrchestratorLog "Orchestrator error: $($_.Exception.Message)" -Level "CRITICAL"
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    
    # Cleanup on error
    Complete-OperationTracking -Success $false
    Save-OrchestratorState
    Remove-OperationLock
    
    exit 1
}