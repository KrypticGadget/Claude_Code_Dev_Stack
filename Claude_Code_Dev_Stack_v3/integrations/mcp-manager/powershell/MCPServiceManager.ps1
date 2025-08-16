# MCP Service Manager - Advanced Windows Service Management
# Enhanced PowerShell wrapper for MCP Manager with Windows service integration
# 
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Install", "Uninstall", "Start", "Stop", "Restart", "Status", "Configure", "Monitor", "UpdateConfig", "Backup", "Restore")]
    [string]$Action = "Status",
    
    [string]$ServiceName = "MCPManager",
    [string]$DisplayName = "MCP Manager Service",
    [string]$Description = "Model Context Protocol Manager - Service orchestration and management",
    [string]$ConfigPath = "",
    [string]$LogPath = "",
    [switch]$Force,
    [switch]$Background,
    [switch]$Development,
    [int]$Port = 8000,
    [int]$MonitorInterval = 30,
    [string]$BackupPath = ""
)

# Service configuration
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$IntegrationRoot = Split-Path -Parent $ScriptRoot
$ServiceExecutable = Join-Path $PSScriptRoot "MCPServiceWrapper.exe"
$ServiceScript = Join-Path $PSScriptRoot "MCPServiceWrapper.ps1"
$DefaultConfigPath = Join-Path $IntegrationRoot "config\mcp-services.yml"
$DefaultLogPath = Join-Path $IntegrationRoot "logs\mcp-service.log"
$StateFile = Join-Path $IntegrationRoot "data\service-state.json"
$BackupDir = Join-Path $IntegrationRoot "backups"

# Use provided paths or defaults
$ConfigPath = if ($ConfigPath) { $ConfigPath } else { $DefaultConfigPath }
$LogPath = if ($LogPath) { $LogPath } else { $DefaultLogPath }
$BackupPath = if ($BackupPath) { $BackupPath } else { $BackupDir }

# Ensure required directories exist
$RequiredDirs = @(
    (Split-Path $ConfigPath -Parent),
    (Split-Path $LogPath -Parent),
    (Join-Path $IntegrationRoot "data"),
    $BackupPath
)

foreach ($dir in $RequiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Logging functions
function Write-ServiceLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    # Write to console with appropriate color
    $Color = switch ($Level) {
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
    }
    Write-Host $LogEntry -ForegroundColor $Color
    
    # Write to log file
    try {
        Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
    }
    catch {
        # Ignore log file errors
    }
}

# Service management functions
function Install-MCPService {
    Write-ServiceLog "Installing MCP Manager as Windows service..." -Level "INFO"
    
    try {
        # Check if service already exists
        $ExistingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($ExistingService) {
            if (-not $Force) {
                Write-ServiceLog "Service '$ServiceName' already exists. Use -Force to reinstall." -Level "WARN"
                return $false
            }
            Write-ServiceLog "Removing existing service..." -Level "INFO"
            Uninstall-MCPService
        }
        
        # Create service wrapper if it doesn't exist
        if (-not (Test-Path $ServiceScript)) {
            Create-ServiceWrapper
        }
        
        # Install the service using New-Service or sc.exe
        try {
            # Try PowerShell New-Service first (Windows 10/Server 2016+)
            New-Service -Name $ServiceName -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File `"$ServiceScript`"" -DisplayName $DisplayName -Description $Description -StartupType Automatic
            Write-ServiceLog "Service installed using New-Service" -Level "INFO"
        }
        catch {
            # Fallback to sc.exe for older Windows versions
            $BinaryPath = "powershell.exe -ExecutionPolicy Bypass -File `"$ServiceScript`""
            $Result = & sc.exe create $ServiceName binPath= $BinaryPath DisplayName= $DisplayName start= auto
            if ($LASTEXITCODE -eq 0) {
                & sc.exe description $ServiceName $Description | Out-Null
                Write-ServiceLog "Service installed using sc.exe" -Level "INFO"
            }
            else {
                throw "sc.exe failed with exit code $LASTEXITCODE"
            }
        }
        
        # Configure service recovery options
        Configure-ServiceRecovery
        
        Write-ServiceLog "MCP Manager service installed successfully" -Level "INFO"
        return $true
        
    }
    catch {
        Write-ServiceLog "Failed to install service: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Uninstall-MCPService {
    Write-ServiceLog "Uninstalling MCP Manager service..." -Level "INFO"
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-ServiceLog "Service '$ServiceName' not found" -Level "WARN"
            return $true
        }
        
        # Stop service if running
        if ($Service.Status -eq "Running") {
            Write-ServiceLog "Stopping service before uninstall..." -Level "INFO"
            Stop-MCPService
            Start-Sleep -Seconds 5
        }
        
        # Remove the service
        & sc.exe delete $ServiceName | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ServiceLog "MCP Manager service uninstalled successfully" -Level "INFO"
            return $true
        }
        else {
            throw "Failed to delete service with sc.exe"
        }
        
    }
    catch {
        Write-ServiceLog "Failed to uninstall service: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Start-MCPService {
    Write-ServiceLog "Starting MCP Manager service..." -Level "INFO"
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-ServiceLog "Service '$ServiceName' not found. Install the service first." -Level "ERROR"
            return $false
        }
        
        if ($Service.Status -eq "Running") {
            Write-ServiceLog "Service is already running" -Level "INFO"
            return $true
        }
        
        Start-Service -Name $ServiceName
        
        # Wait for service to start and verify
        $Timeout = 30
        $Started = $false
        for ($i = 0; $i -lt $Timeout; $i++) {
            Start-Sleep -Seconds 1
            $Service = Get-Service -Name $ServiceName
            if ($Service.Status -eq "Running") {
                $Started = $true
                break
            }
        }
        
        if ($Started) {
            Write-ServiceLog "MCP Manager service started successfully" -Level "INFO"
            Update-ServiceState "started"
            return $true
        }
        else {
            Write-ServiceLog "Service failed to start within $Timeout seconds" -Level "ERROR"
            return $false
        }
        
    }
    catch {
        Write-ServiceLog "Failed to start service: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Stop-MCPService {
    Write-ServiceLog "Stopping MCP Manager service..." -Level "INFO"
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-ServiceLog "Service '$ServiceName' not found" -Level "WARN"
            return $true
        }
        
        if ($Service.Status -eq "Stopped") {
            Write-ServiceLog "Service is already stopped" -Level "INFO"
            return $true
        }
        
        Stop-Service -Name $ServiceName -Force
        
        # Wait for service to stop
        $Timeout = 30
        $Stopped = $false
        for ($i = 0; $i -lt $Timeout; $i++) {
            Start-Sleep -Seconds 1
            $Service = Get-Service -Name $ServiceName
            if ($Service.Status -eq "Stopped") {
                $Stopped = $true
                break
            }
        }
        
        if ($Stopped) {
            Write-ServiceLog "MCP Manager service stopped successfully" -Level "INFO"
            Update-ServiceState "stopped"
            return $true
        }
        else {
            Write-ServiceLog "Service failed to stop within $Timeout seconds" -Level "ERROR"
            return $false
        }
        
    }
    catch {
        Write-ServiceLog "Failed to stop service: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Restart-MCPService {
    Write-ServiceLog "Restarting MCP Manager service..." -Level "INFO"
    
    if (Stop-MCPService) {
        Start-Sleep -Seconds 2
        return Start-MCPService
    }
    return $false
}

function Get-MCPServiceStatus {
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if (-not $Service) {
            return @{
                ServiceExists = $false
                Status = "Not Installed"
                ProcessId = $null
                StartTime = $null
                Memory = $null
                CPU = $null
            }
        }
        
        $Status = @{
            ServiceExists = $true
            Status = $Service.Status.ToString()
            ProcessId = $null
            StartTime = $null
            Memory = $null
            CPU = $null
        }
        
        # Get process information if service is running
        if ($Service.Status -eq "Running") {
            try {
                $ServiceProcess = Get-WmiObject -Class Win32_Service -Filter "Name='$ServiceName'" | 
                    Select-Object -ExpandProperty ProcessId
                
                if ($ServiceProcess) {
                    $Process = Get-Process -Id $ServiceProcess -ErrorAction SilentlyContinue
                    if ($Process) {
                        $Status.ProcessId = $Process.Id
                        $Status.StartTime = $Process.StartTime
                        $Status.Memory = [math]::Round($Process.WorkingSet64 / 1MB, 2)
                        $Status.CPU = [math]::Round($Process.CPU, 2)
                    }
                }
            }
            catch {
                # Process information not available
            }
        }
        
        return $Status
        
    }
    catch {
        Write-ServiceLog "Failed to get service status: $($_.Exception.Message)" -Level "ERROR"
        return @{
            ServiceExists = $false
            Status = "Error"
            ProcessId = $null
            StartTime = $null
            Memory = $null
            CPU = $null
        }
    }
}

function Configure-ServiceRecovery {
    Write-ServiceLog "Configuring service recovery options..." -Level "INFO"
    
    try {
        # Configure service to restart on failure
        & sc.exe failure $ServiceName reset= 3600 actions= restart/5000/restart/10000/restart/30000 | Out-Null
        
        # Set service to restart after 5 seconds on failure
        & sc.exe failureflag $ServiceName 1 | Out-Null
        
        Write-ServiceLog "Service recovery options configured" -Level "INFO"
    }
    catch {
        Write-ServiceLog "Failed to configure service recovery: $($_.Exception.Message)" -Level "WARN"
    }
}

function Create-ServiceWrapper {
    Write-ServiceLog "Creating service wrapper script..." -Level "INFO"
    
    $WrapperContent = @"
# MCP Service Wrapper - Runs MCP Manager as Windows Service
# This script is executed by the Windows Service Controller

param()

# Service configuration
`$IntegrationRoot = "$IntegrationRoot"
`$ConfigPath = "$ConfigPath"
`$LogPath = "$LogPath"
`$Port = $Port

# Import MCP Manager module
`$ModulePath = Join-Path `$PSScriptRoot "MCPManager.psm1"
if (Test-Path `$ModulePath) {
    Import-Module `$ModulePath -Force
}

# Setup logging
function Write-ServiceLog {
    param([string]`$Message, [string]`$Level = "INFO")
    `$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    `$LogEntry = "[`$Timestamp] [SERVICE] [`$Level] `$Message"
    Add-Content -Path `$LogPath -Value `$LogEntry -ErrorAction SilentlyContinue
}

# Service main function
function Start-MCPManagerService {
    Write-ServiceLog "MCP Manager Service starting..."
    
    try {
        # Initialize MCP Manager
        if (Initialize-MCPManager -ConfigPath `$ConfigPath) {
            Write-ServiceLog "MCP Manager initialized successfully"
            
            # Start the manager
            if (Start-MCPManager -Background) {
                Write-ServiceLog "MCP Manager started successfully"
                
                # Keep the service running
                while (`$true) {
                    Start-Sleep -Seconds 30
                    
                    # Health check
                    try {
                        `$Status = Get-MCPServiceStatus
                        if (`$Status -and `$Status.total_services -ge 0) {
                            Write-ServiceLog "Health check passed - Total services: `$(`$Status.total_services)" -Level "DEBUG"
                        }
                        else {
                            Write-ServiceLog "Health check failed" -Level "WARN"
                        }
                    }
                    catch {
                        Write-ServiceLog "Health check error: `$(`$_.Exception.Message)" -Level "ERROR"
                    }
                }
            }
            else {
                Write-ServiceLog "Failed to start MCP Manager" -Level "ERROR"
                exit 1
            }
        }
        else {
            Write-ServiceLog "Failed to initialize MCP Manager" -Level "ERROR"
            exit 1
        }
    }
    catch {
        Write-ServiceLog "Service error: `$(`$_.Exception.Message)" -Level "ERROR"
        exit 1
    }
    finally {
        Write-ServiceLog "MCP Manager Service stopping..."
        try {
            Stop-MCPManager
        }
        catch {
            Write-ServiceLog "Error during shutdown: `$(`$_.Exception.Message)" -Level "ERROR"
        }
    }
}

# Handle service control events
if (`$args.Length -gt 0) {
    switch (`$args[0]) {
        "start" { Start-MCPManagerService }
        "stop" { 
            Write-ServiceLog "Service stop requested"
            exit 0 
        }
        default { Start-MCPManagerService }
    }
}
else {
    Start-MCPManagerService
}
"@
    
    try {
        $WrapperContent | Out-File -FilePath $ServiceScript -Encoding UTF8 -Force
        Write-ServiceLog "Service wrapper created at: $ServiceScript" -Level "INFO"
        return $true
    }
    catch {
        Write-ServiceLog "Failed to create service wrapper: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Start-MCPMonitoring {
    param(
        [int]$Interval = $MonitorInterval,
        [int]$Duration = 0  # 0 = infinite
    )
    
    Write-ServiceLog "Starting MCP service monitoring (Interval: ${Interval}s)..." -Level "INFO"
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    Write-Host ""
    
    $StartTime = Get-Date
    $MonitorCount = 0
    
    try {
        while ($true) {
            Clear-Host
            
            Write-Host "MCP Manager Service Monitor - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
            Write-Host "=" * 70 -ForegroundColor Cyan
            Write-Host ""
            
            # Service status
            $ServiceStatus = Get-MCPServiceStatus
            Write-Host "Service Status:" -ForegroundColor Yellow
            Write-Host "  Name: $ServiceName" -ForegroundColor White
            Write-Host "  Status: $($ServiceStatus.Status)" -ForegroundColor $(if ($ServiceStatus.Status -eq "Running") { "Green" } else { "Red" })
            
            if ($ServiceStatus.ProcessId) {
                Write-Host "  Process ID: $($ServiceStatus.ProcessId)" -ForegroundColor White
                Write-Host "  Memory Usage: $($ServiceStatus.Memory) MB" -ForegroundColor White
                Write-Host "  CPU Time: $($ServiceStatus.CPU) seconds" -ForegroundColor White
                
                if ($ServiceStatus.StartTime) {
                    $Uptime = (Get-Date) - $ServiceStatus.StartTime
                    Write-Host "  Uptime: $($Uptime.ToString('dd\.hh\:mm\:ss'))" -ForegroundColor White
                }
            }
            Write-Host ""
            
            # MCP Manager status
            if ($ServiceStatus.Status -eq "Running") {
                try {
                    Import-Module (Join-Path $PSScriptRoot "MCPManager.psm1") -Force -ErrorAction SilentlyContinue
                    
                    if (Get-Command "Get-MCPServiceStatus" -ErrorAction SilentlyContinue) {
                        $MCPStatus = Get-MCPServiceStatus
                        if ($MCPStatus) {
                            Write-Host "MCP Manager Status:" -ForegroundColor Yellow
                            Write-Host "  Total Services: $($MCPStatus.total_services)" -ForegroundColor White
                            Write-Host "  Healthy Services: $($MCPStatus.healthy_services)" -ForegroundColor Green
                            
                            if ($MCPStatus.status_breakdown) {
                                Write-Host "  Status Breakdown:" -ForegroundColor Gray
                                foreach ($Status in $MCPStatus.status_breakdown.PSObject.Properties) {
                                    $Color = switch ($Status.Name) {
                                        "running" { "Green" }
                                        "error" { "Red" }
                                        "stopped" { "Gray" }
                                        "starting" { "Yellow" }
                                        default { "White" }
                                    }
                                    Write-Host "    $($Status.Name): $($Status.Value)" -ForegroundColor $Color
                                }
                            }
                        }
                        else {
                            Write-Host "MCP Manager Status: Not Available" -ForegroundColor Red
                        }
                    }
                }
                catch {
                    Write-Host "MCP Manager Status: Error retrieving status" -ForegroundColor Red
                }
            }
            else {
                Write-Host "MCP Manager Status: Service not running" -ForegroundColor Red
            }
            
            Write-Host ""
            Write-Host "Monitor Statistics:" -ForegroundColor Yellow
            Write-Host "  Monitoring for: $((Get-Date) - $StartTime)" -ForegroundColor White
            Write-Host "  Check count: $MonitorCount" -ForegroundColor White
            Write-Host "  Next check in: $Interval seconds" -ForegroundColor Gray
            
            $MonitorCount++
            
            # Check duration limit
            if ($Duration -gt 0 -and ((Get-Date) - $StartTime).TotalSeconds -ge $Duration) {
                Write-Host ""
                Write-Host "Monitoring duration completed" -ForegroundColor Yellow
                break
            }
            
            Start-Sleep -Seconds $Interval
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host ""
        Write-Host "Monitoring stopped by user" -ForegroundColor Yellow
    }
    catch {
        Write-ServiceLog "Monitoring error: $($_.Exception.Message)" -Level "ERROR"
    }
}

function Update-ServiceState {
    param([string]$State)
    
    try {
        $StateData = @{
            LastAction = $State
            Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            ServiceName = $ServiceName
            ConfigPath = $ConfigPath
            LogPath = $LogPath
        }
        
        $StateJson = $StateData | ConvertTo-Json -Depth 2
        $StateJson | Out-File -FilePath $StateFile -Encoding UTF8 -Force
    }
    catch {
        Write-ServiceLog "Failed to update service state: $($_.Exception.Message)" -Level "WARN"
    }
}

function Backup-MCPConfiguration {
    param([string]$BackupLocation = $BackupPath)
    
    Write-ServiceLog "Creating configuration backup..." -Level "INFO"
    
    try {
        $BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $BackupName = "mcp-config-backup-$BackupTimestamp"
        $BackupFullPath = Join-Path $BackupLocation $BackupName
        
        # Create backup directory
        New-Item -ItemType Directory -Path $BackupFullPath -Force | Out-Null
        
        # Backup configuration files
        $FilesToBackup = @(
            $ConfigPath,
            $StateFile,
            (Join-Path $IntegrationRoot "requirements.txt"),
            (Join-Path $IntegrationRoot ".env")
        )
        
        foreach ($File in $FilesToBackup) {
            if (Test-Path $File) {
                $DestFile = Join-Path $BackupFullPath (Split-Path $File -Leaf)
                Copy-Item -Path $File -Destination $DestFile -Force
                Write-ServiceLog "Backed up: $(Split-Path $File -Leaf)" -Level "DEBUG"
            }
        }
        
        # Create backup manifest
        $BackupManifest = @{
            BackupDate = Get-Date
            BackupName = $BackupName
            ServiceName = $ServiceName
            ConfigPath = $ConfigPath
            Files = $FilesToBackup | Where-Object { Test-Path $_ } | ForEach-Object { Split-Path $_ -Leaf }
        }
        
        $ManifestJson = $BackupManifest | ConvertTo-Json -Depth 2
        $ManifestPath = Join-Path $BackupFullPath "backup-manifest.json"
        $ManifestJson | Out-File -FilePath $ManifestPath -Encoding UTF8
        
        Write-ServiceLog "Configuration backup completed: $BackupFullPath" -Level "INFO"
        return $BackupFullPath
    }
    catch {
        Write-ServiceLog "Failed to create backup: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

function Restore-MCPConfiguration {
    param([string]$BackupLocation)
    
    if (-not $BackupLocation -or -not (Test-Path $BackupLocation)) {
        Write-ServiceLog "Invalid backup location: $BackupLocation" -Level "ERROR"
        return $false
    }
    
    Write-ServiceLog "Restoring configuration from: $BackupLocation" -Level "INFO"
    
    try {
        # Check for backup manifest
        $ManifestPath = Join-Path $BackupLocation "backup-manifest.json"
        if (Test-Path $ManifestPath) {
            $Manifest = Get-Content $ManifestPath | ConvertFrom-Json
            Write-ServiceLog "Found backup manifest: $($Manifest.BackupName)" -Level "INFO"
        }
        
        # Stop service before restore
        $ServiceStatus = Get-MCPServiceStatus
        $WasRunning = $ServiceStatus.Status -eq "Running"
        
        if ($WasRunning) {
            Write-ServiceLog "Stopping service for restore..." -Level "INFO"
            Stop-MCPService
        }
        
        # Restore files
        $BackupFiles = Get-ChildItem -Path $BackupLocation -File | Where-Object { $_.Name -ne "backup-manifest.json" }
        
        foreach ($BackupFile in $BackupFiles) {
            $TargetPath = switch ($BackupFile.Name) {
                "mcp-services.yml" { $ConfigPath }
                "service-state.json" { $StateFile }
                "requirements.txt" { Join-Path $IntegrationRoot "requirements.txt" }
                ".env" { Join-Path $IntegrationRoot ".env" }
                default { Join-Path $IntegrationRoot $BackupFile.Name }
            }
            
            # Create target directory if needed
            $TargetDir = Split-Path $TargetPath -Parent
            if (-not (Test-Path $TargetDir)) {
                New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
            }
            
            Copy-Item -Path $BackupFile.FullName -Destination $TargetPath -Force
            Write-ServiceLog "Restored: $($BackupFile.Name)" -Level "DEBUG"
        }
        
        # Restart service if it was running
        if ($WasRunning) {
            Write-ServiceLog "Restarting service after restore..." -Level "INFO"
            Start-MCPService
        }
        
        Write-ServiceLog "Configuration restore completed successfully" -Level "INFO"
        return $true
    }
    catch {
        Write-ServiceLog "Failed to restore configuration: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Show-ServiceDashboard {
    Write-ServiceLog "Displaying service dashboard..." -Level "INFO"
    
    $Status = Get-MCPServiceStatus
    
    Write-Host ""
    Write-Host "MCP Manager Service Dashboard" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Service Information:" -ForegroundColor Yellow
    Write-Host "  Name: $ServiceName" -ForegroundColor White
    Write-Host "  Display Name: $DisplayName" -ForegroundColor White
    Write-Host "  Status: $($Status.Status)" -ForegroundColor $(if ($Status.Status -eq "Running") { "Green" } else { "Red" })
    Write-Host "  Configuration: $ConfigPath" -ForegroundColor Gray
    Write-Host "  Log File: $LogPath" -ForegroundColor Gray
    Write-Host ""
    
    if ($Status.Status -eq "Running") {
        Write-Host "Runtime Information:" -ForegroundColor Yellow
        Write-Host "  Process ID: $($Status.ProcessId)" -ForegroundColor White
        Write-Host "  Memory Usage: $($Status.Memory) MB" -ForegroundColor White
        Write-Host "  CPU Time: $($Status.CPU) seconds" -ForegroundColor White
        
        if ($Status.StartTime) {
            $Uptime = (Get-Date) - $Status.StartTime
            Write-Host "  Uptime: $($Uptime.ToString('dd\.hh\:mm\:ss'))" -ForegroundColor White
        }
        Write-Host ""
    }
    
    Write-Host "Available Actions:" -ForegroundColor Yellow
    Write-Host "  Install   - Install service" -ForegroundColor Gray
    Write-Host "  Uninstall - Remove service" -ForegroundColor Gray
    Write-Host "  Start     - Start service" -ForegroundColor Gray
    Write-Host "  Stop      - Stop service" -ForegroundColor Gray
    Write-Host "  Restart   - Restart service" -ForegroundColor Gray
    Write-Host "  Monitor   - Start monitoring" -ForegroundColor Gray
    Write-Host "  Backup    - Backup configuration" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
try {
    Write-Host "MCP Service Manager - Windows Service Integration" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    
    switch ($Action.ToLower()) {
        "install" {
            $Success = Install-MCPService
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "uninstall" {
            $Success = Uninstall-MCPService
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "start" {
            $Success = Start-MCPService
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "stop" {
            $Success = Stop-MCPService
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "restart" {
            $Success = Restart-MCPService
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "status" {
            Show-ServiceDashboard
        }
        
        "configure" {
            Write-ServiceLog "Configuring service..." -Level "INFO"
            if (Test-Path $ConfigPath) {
                & notepad.exe $ConfigPath
            }
            else {
                Write-ServiceLog "Configuration file not found: $ConfigPath" -Level "ERROR"
            }
        }
        
        "monitor" {
            Start-MCPMonitoring -Interval $MonitorInterval
        }
        
        "backup" {
            $BackupResult = Backup-MCPConfiguration
            if ($BackupResult) {
                Write-Host "Backup created: $BackupResult" -ForegroundColor Green
            }
        }
        
        "restore" {
            if ($BackupPath) {
                $Success = Restore-MCPConfiguration -BackupLocation $BackupPath
                exit $(if ($Success) { 0 } else { 1 })
            }
            else {
                Write-ServiceLog "Backup path required for restore operation" -Level "ERROR"
                exit 1
            }
        }
        
        default {
            Write-ServiceLog "Unknown action: $Action" -Level "ERROR"
            Write-Host "Valid actions: Install, Uninstall, Start, Stop, Restart, Status, Configure, Monitor, Backup, Restore" -ForegroundColor Yellow
            exit 1
        }
    }
}
catch {
    Write-ServiceLog "Script error: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}