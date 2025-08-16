# MCP Health Monitor - Advanced health checking and auto-restart system
# Enhanced PowerShell health monitoring for MCP Manager services
# 
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

#Requires -Version 5.1

[CmdletBinding()]
param(
    [int]$CheckInterval = 30,
    [int]$TimeoutSeconds = 10,
    [int]$MaxRetries = 3,
    [int]$RetryDelay = 5,
    [switch]$AutoRestart,
    [switch]$DetailedLogging,
    [switch]$EmailAlerts,
    [switch]$WebhookAlerts,
    [switch]$RunOnce,
    [switch]$Background,
    [string]$ConfigPath = "",
    [string]$LogPath = "",
    [string]$AlertConfig = "",
    [string]$ServiceName = "MCPManager"
)

# Module configuration
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$IntegrationRoot = Split-Path -Parent $ScriptRoot
$DefaultConfigPath = Join-Path $IntegrationRoot "config\mcp-services.yml"
$DefaultLogPath = Join-Path $IntegrationRoot "logs\health-monitor.log"
$AlertConfigPath = if ($AlertConfig) { $AlertConfig } else { Join-Path $IntegrationRoot "config\alert-config.json" }
$StateFile = Join-Path $IntegrationRoot "data\health-monitor-state.json"

# Use provided paths or defaults
$ConfigPath = if ($ConfigPath) { $ConfigPath } else { $DefaultConfigPath }
$LogPath = if ($LogPath) { $LogPath } else { $DefaultLogPath }

# Health check thresholds
$script:HealthThresholds = @{
    ResponseTimeWarning = 5000  # milliseconds
    ResponseTimeCritical = 10000  # milliseconds
    MemoryWarning = 500  # MB
    MemoryCritical = 1000  # MB
    CPUWarning = 80  # percentage
    CPUCritical = 95  # percentage
    ErrorRateWarning = 5  # percentage
    ErrorRateCritical = 15  # percentage
}

# Health check state
$script:HealthState = @{
    Services = @{}
    LastCheck = $null
    AlertsSent = @{}
    Statistics = @{
        TotalChecks = 0
        SuccessfulChecks = 0
        FailedChecks = 0
        RestartAttempts = 0
        SuccessfulRestarts = 0
    }
}

# Logging functions
function Write-HealthLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG", "CRITICAL")]
        [string]$Level = "INFO",
        [string]$Component = "HEALTH"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogEntry = "[$Timestamp] [$Component] [$Level] $Message"
    
    # Write to console with appropriate color
    $Color = switch ($Level) {
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
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
}

# Health check functions
function Test-ServiceHealth {
    param(
        [string]$ServiceId,
        [string]$ServiceName,
        [string]$HealthUrl,
        [int]$Port,
        [string]$ServiceType = "unknown"
    )
    
    $HealthResult = @{
        ServiceId = $ServiceId
        ServiceName = $ServiceName
        ServiceType = $ServiceType
        IsHealthy = $false
        Status = "unknown"
        ResponseTime = $null
        StatusCode = $null
        ErrorMessage = $null
        Metrics = @{}
        Timestamp = Get-Date
        Checks = @{
            Connectivity = $false
            Response = $false
            Performance = $false
            ProcessHealth = $false
        }
    }
    
    try {
        Write-HealthLog "Checking health for service: $ServiceName ($ServiceId)" -Level "DEBUG"
        
        # 1. Connectivity check
        $ConnectivityResult = Test-ServiceConnectivity -ServiceId $ServiceId -Port $Port
        $HealthResult.Checks.Connectivity = $ConnectivityResult.Success
        
        if (-not $ConnectivityResult.Success) {
            $HealthResult.ErrorMessage = $ConnectivityResult.ErrorMessage
            Write-HealthLog "Connectivity check failed for $ServiceName`: $($ConnectivityResult.ErrorMessage)" -Level "WARN"
            return $HealthResult
        }
        
        # 2. HTTP response check
        $ResponseResult = Test-ServiceResponse -HealthUrl $HealthUrl
        $HealthResult.Checks.Response = $ResponseResult.Success
        $HealthResult.ResponseTime = $ResponseResult.ResponseTime
        $HealthResult.StatusCode = $ResponseResult.StatusCode
        
        if (-not $ResponseResult.Success) {
            $HealthResult.ErrorMessage = $ResponseResult.ErrorMessage
            Write-HealthLog "Response check failed for $ServiceName`: $($ResponseResult.ErrorMessage)" -Level "WARN"
            return $HealthResult
        }
        
        # 3. Performance metrics check
        $PerformanceResult = Get-ServicePerformanceMetrics -ServiceId $ServiceId
        $HealthResult.Checks.Performance = $PerformanceResult.Success
        $HealthResult.Metrics = $PerformanceResult.Metrics
        
        # 4. Process health check
        $ProcessResult = Test-ServiceProcess -ServiceName $ServiceName
        $HealthResult.Checks.ProcessHealth = $ProcessResult.Success
        
        # Overall health determination
        $HealthResult.IsHealthy = $HealthResult.Checks.Connectivity -and 
                                 $HealthResult.Checks.Response -and 
                                 $HealthResult.Checks.Performance -and
                                 $HealthResult.Checks.ProcessHealth
        
        $HealthResult.Status = if ($HealthResult.IsHealthy) { "healthy" } else { "unhealthy" }
        
        Write-HealthLog "Health check completed for $ServiceName - Status: $($HealthResult.Status)" -Level "DEBUG"
        
    }
    catch {
        $HealthResult.ErrorMessage = $_.Exception.Message
        $HealthResult.Status = "error"
        Write-HealthLog "Health check error for $ServiceName`: $($_.Exception.Message)" -Level "ERROR"
    }
    
    return $HealthResult
}

function Test-ServiceConnectivity {
    param(
        [string]$ServiceId,
        [int]$Port,
        [string]$Host = "localhost"
    )
    
    try {
        $TcpClient = New-Object System.Net.Sockets.TcpClient
        $AsyncResult = $TcpClient.BeginConnect($Host, $Port, $null, $null)
        $Success = $AsyncResult.AsyncWaitHandle.WaitOne($TimeoutSeconds * 1000)
        
        if ($Success) {
            $TcpClient.EndConnect($AsyncResult)
            $TcpClient.Close()
            return @{ Success = $true; ErrorMessage = $null }
        }
        else {
            $TcpClient.Close()
            return @{ Success = $false; ErrorMessage = "Connection timeout" }
        }
    }
    catch {
        return @{ Success = $false; ErrorMessage = $_.Exception.Message }
    }
}

function Test-ServiceResponse {
    param([string]$HealthUrl)
    
    try {
        $StartTime = Get-Date
        $Response = Invoke-WebRequest -Uri $HealthUrl -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        $EndTime = Get-Date
        $ResponseTime = ($EndTime - $StartTime).TotalMilliseconds
        
        return @{
            Success = $true
            StatusCode = $Response.StatusCode
            ResponseTime = $ResponseTime
            ErrorMessage = $null
        }
    }
    catch {
        return @{
            Success = $false
            StatusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { $null }
            ResponseTime = $null
            ErrorMessage = $_.Exception.Message
        }
    }
}

function Get-ServicePerformanceMetrics {
    param([string]$ServiceId)
    
    try {
        # Get process information
        $Processes = Get-Process | Where-Object { $_.ProcessName -like "*python*" -or $_.ProcessName -like "*mcp*" }
        
        $Metrics = @{
            MemoryUsage = 0
            CPUUsage = 0
            ProcessCount = $Processes.Count
            HandleCount = 0
            ThreadCount = 0
        }
        
        foreach ($Process in $Processes) {
            $Metrics.MemoryUsage += $Process.WorkingSet64 / 1MB
            $Metrics.HandleCount += $Process.HandleCount
            $Metrics.ThreadCount += $Process.Threads.Count
        }
        
        # CPU usage calculation (simplified)
        if ($Processes.Count -gt 0) {
            $TotalCPU = ($Processes | Measure-Object -Property CPU -Sum).Sum
            $Metrics.CPUUsage = [math]::Round($TotalCPU / $Processes.Count, 2)
        }
        
        $Metrics.MemoryUsage = [math]::Round($Metrics.MemoryUsage, 2)
        
        # Performance thresholds check
        $Success = $true
        if ($Metrics.MemoryUsage -gt $script:HealthThresholds.MemoryCritical) {
            $Success = $false
        }
        
        return @{
            Success = $Success
            Metrics = $Metrics
        }
    }
    catch {
        return @{
            Success = $false
            Metrics = @{}
            ErrorMessage = $_.Exception.Message
        }
    }
}

function Test-ServiceProcess {
    param([string]$ServiceName)
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if (-not $Service) {
            return @{ Success = $false; ErrorMessage = "Service not found" }
        }
        
        $IsRunning = $Service.Status -eq "Running"
        
        return @{ 
            Success = $IsRunning
            ErrorMessage = if (-not $IsRunning) { "Service is not running" } else { $null }
        }
    }
    catch {
        return @{ Success = $false; ErrorMessage = $_.Exception.Message }
    }
}

# Alert functions
function Send-HealthAlert {
    param(
        [string]$ServiceName,
        [string]$AlertType,
        [string]$Message,
        [string]$Severity = "warning"
    )
    
    $AlertKey = "$ServiceName-$AlertType"
    $CurrentTime = Get-Date
    
    # Check if we've already sent this alert recently (throttling)
    if ($script:HealthState.AlertsSent.ContainsKey($AlertKey)) {
        $LastAlert = $script:HealthState.AlertsSent[$AlertKey]
        $TimeDiff = ($CurrentTime - $LastAlert).TotalMinutes
        
        # Don't send same alert more than once every 30 minutes
        if ($TimeDiff -lt 30) {
            Write-HealthLog "Alert throttled for $AlertKey (last sent $([math]::Round($TimeDiff, 1)) minutes ago)" -Level "DEBUG"
            return
        }
    }
    
    Write-HealthLog "Sending $Severity alert for $ServiceName`: $Message" -Level "WARN"
    
    # Update alert tracking
    $script:HealthState.AlertsSent[$AlertKey] = $CurrentTime
    
    # Send email alert
    if ($EmailAlerts) {
        Send-EmailAlert -ServiceName $ServiceName -Message $Message -Severity $Severity
    }
    
    # Send webhook alert
    if ($WebhookAlerts) {
        Send-WebhookAlert -ServiceName $ServiceName -Message $Message -Severity $Severity
    }
    
    # Log to Windows Event Log
    try {
        $EventLogSource = "MCP Health Monitor"
        $EventID = switch ($Severity) {
            "critical" { 1001 }
            "error" { 1002 }
            "warning" { 1003 }
            default { 1000 }
        }
        
        if (-not [System.Diagnostics.EventLog]::SourceExists($EventLogSource)) {
            New-EventLog -LogName Application -Source $EventLogSource
        }
        
        Write-EventLog -LogName Application -Source $EventLogSource -EventId $EventID -EntryType Warning -Message "MCP Health Alert: $ServiceName - $Message"
    }
    catch {
        Write-HealthLog "Failed to write to event log: $($_.Exception.Message)" -Level "WARN"
    }
}

function Send-EmailAlert {
    param(
        [string]$ServiceName,
        [string]$Message,
        [string]$Severity
    )
    
    try {
        if (-not (Test-Path $AlertConfigPath)) {
            Write-HealthLog "Email alert config not found: $AlertConfigPath" -Level "WARN"
            return
        }
        
        $AlertConfig = Get-Content $AlertConfigPath | ConvertFrom-Json
        
        if (-not $AlertConfig.email -or -not $AlertConfig.email.enabled) {
            Write-HealthLog "Email alerts not configured or disabled" -Level "DEBUG"
            return
        }
        
        $EmailConfig = $AlertConfig.email
        
        $Subject = "MCP Health Alert - $ServiceName ($Severity)"
        $Body = @"
MCP Health Monitor Alert

Service: $ServiceName
Severity: $Severity
Message: $Message
Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

This is an automated alert from the MCP Health Monitor.
"@
        
        # Send email using Send-MailMessage
        $MailParams = @{
            From = $EmailConfig.from
            To = $EmailConfig.to
            Subject = $Subject
            Body = $Body
            SmtpServer = $EmailConfig.smtp_server
        }
        
        if ($EmailConfig.smtp_port) {
            $MailParams.Port = $EmailConfig.smtp_port
        }
        
        if ($EmailConfig.use_ssl) {
            $MailParams.UseSsl = $true
        }
        
        if ($EmailConfig.username -and $EmailConfig.password) {
            $SecurePassword = ConvertTo-SecureString $EmailConfig.password -AsPlainText -Force
            $Credential = New-Object System.Management.Automation.PSCredential ($EmailConfig.username, $SecurePassword)
            $MailParams.Credential = $Credential
        }
        
        Send-MailMessage @MailParams
        Write-HealthLog "Email alert sent successfully" -Level "DEBUG"
        
    }
    catch {
        Write-HealthLog "Failed to send email alert: $($_.Exception.Message)" -Level "ERROR"
    }
}

function Send-WebhookAlert {
    param(
        [string]$ServiceName,
        [string]$Message,
        [string]$Severity
    )
    
    try {
        if (-not (Test-Path $AlertConfigPath)) {
            return
        }
        
        $AlertConfig = Get-Content $AlertConfigPath | ConvertFrom-Json
        
        if (-not $AlertConfig.webhook -or -not $AlertConfig.webhook.enabled) {
            return
        }
        
        $WebhookConfig = $AlertConfig.webhook
        
        $Payload = @{
            service = $ServiceName
            severity = $Severity
            message = $Message
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            source = "MCP Health Monitor"
        } | ConvertTo-Json
        
        $Headers = @{
            'Content-Type' = 'application/json'
        }
        
        if ($WebhookConfig.auth_header) {
            $Headers[$WebhookConfig.auth_header.name] = $WebhookConfig.auth_header.value
        }
        
        Invoke-RestMethod -Uri $WebhookConfig.url -Method Post -Body $Payload -Headers $Headers -TimeoutSec 10
        Write-HealthLog "Webhook alert sent successfully" -Level "DEBUG"
        
    }
    catch {
        Write-HealthLog "Failed to send webhook alert: $($_.Exception.Message)" -Level "ERROR"
    }
}

# Auto-restart functions
function Start-ServiceRestart {
    param(
        [string]$ServiceName,
        [string]$ServiceId,
        [string]$Reason
    )
    
    Write-HealthLog "Initiating restart for $ServiceName - Reason: $Reason" -Level "WARN" -Component "RESTART"
    
    $script:HealthState.Statistics.RestartAttempts++
    
    try {
        # Import service manager
        $ServiceManagerPath = Join-Path $PSScriptRoot "MCPServiceManager.ps1"
        
        if (Test-Path $ServiceManagerPath) {
            # Use service manager for restart
            $RestartResult = & $ServiceManagerPath -Action Restart -ServiceName $ServiceName
            
            if ($RestartResult) {
                $script:HealthState.Statistics.SuccessfulRestarts++
                Write-HealthLog "Service restart successful for $ServiceName" -Level "INFO" -Component "RESTART"
                
                # Send success alert
                Send-HealthAlert -ServiceName $ServiceName -AlertType "restart-success" -Message "Service successfully restarted after health check failure" -Severity "info"
                
                # Wait for service to stabilize
                Start-Sleep -Seconds 10
                
                return $true
            }
            else {
                Write-HealthLog "Service restart failed for $ServiceName" -Level "ERROR" -Component "RESTART"
                
                # Send failure alert
                Send-HealthAlert -ServiceName $ServiceName -AlertType "restart-failed" -Message "Failed to restart service after health check failure" -Severity "critical"
                
                return $false
            }
        }
        else {
            Write-HealthLog "Service manager not found: $ServiceManagerPath" -Level "ERROR" -Component "RESTART"
            return $false
        }
        
    }
    catch {
        Write-HealthLog "Error during service restart: $($_.Exception.Message)" -Level "ERROR" -Component "RESTART"
        return $false
    }
}

# Health monitoring main loop
function Start-HealthMonitoring {
    Write-HealthLog "Starting MCP health monitoring..." -Level "INFO"
    Write-HealthLog "Check interval: $CheckInterval seconds" -Level "INFO"
    Write-HealthLog "Auto-restart enabled: $AutoRestart" -Level "INFO"
    
    if (-not $RunOnce) {
        Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
        Write-Host ""
    }
    
    try {
        do {
            $script:HealthState.LastCheck = Get-Date
            $script:HealthState.Statistics.TotalChecks++
            
            Write-HealthLog "Starting health check cycle $(Get-Date -Format 'HH:mm:ss')" -Level "INFO"
            
            # Load service configuration
            $Services = Get-ServicesFromConfig
            
            if ($Services.Count -eq 0) {
                Write-HealthLog "No services found in configuration" -Level "WARN"
                Start-Sleep -Seconds $CheckInterval
                continue
            }
            
            $HealthyServices = 0
            $UnhealthyServices = 0
            
            foreach ($Service in $Services) {
                try {
                    $HealthResult = Test-ServiceHealth -ServiceId $Service.id -ServiceName $Service.name -HealthUrl $Service.health_url -Port $Service.port -ServiceType $Service.type
                    
                    # Update service state
                    $script:HealthState.Services[$Service.id] = $HealthResult
                    
                    if ($HealthResult.IsHealthy) {
                        $HealthyServices++
                        Write-HealthLog "✓ $($Service.name) - Healthy (${$HealthResult.ResponseTime}ms)" -Level "DEBUG"
                    }
                    else {
                        $UnhealthyServices++
                        Write-HealthLog "✗ $($Service.name) - Unhealthy: $($HealthResult.ErrorMessage)" -Level "WARN"
                        
                        # Send alert
                        Send-HealthAlert -ServiceName $Service.name -AlertType "health-failure" -Message $HealthResult.ErrorMessage -Severity "warning"
                        
                        # Auto-restart if enabled
                        if ($AutoRestart) {
                            Write-HealthLog "Auto-restart triggered for $($Service.name)" -Level "INFO"
                            Start-ServiceRestart -ServiceName $ServiceName -ServiceId $Service.id -Reason $HealthResult.ErrorMessage
                        }
                    }
                }
                catch {
                    Write-HealthLog "Error checking service $($Service.name): $($_.Exception.Message)" -Level "ERROR"
                    $UnhealthyServices++
                }
            }
            
            # Update statistics
            if ($UnhealthyServices -eq 0) {
                $script:HealthState.Statistics.SuccessfulChecks++
            }
            else {
                $script:HealthState.Statistics.FailedChecks++
            }
            
            # Summary log
            Write-HealthLog "Health check cycle completed - Healthy: $HealthyServices, Unhealthy: $UnhealthyServices" -Level "INFO"
            
            # Save state
            Save-HealthState
            
            if (-not $RunOnce) {
                Start-Sleep -Seconds $CheckInterval
            }
            
        } while (-not $RunOnce)
        
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-HealthLog "Health monitoring stopped by user" -Level "INFO"
    }
    catch {
        Write-HealthLog "Health monitoring error: $($_.Exception.Message)" -Level "ERROR"
    }
    finally {
        Write-HealthLog "Health monitoring stopped" -Level "INFO"
        Save-HealthState
    }
}

# Configuration functions
function Get-ServicesFromConfig {
    try {
        if (-not (Test-Path $ConfigPath)) {
            Write-HealthLog "Configuration file not found: $ConfigPath" -Level "WARN"
            return @()
        }
        
        $ConfigContent = Get-Content $ConfigPath -Raw
        
        # Try YAML parsing
        try {
            # Simple YAML parsing for services section
            $YamlLines = $ConfigContent -split "`n"
            $InServicesSection = $false
            $Services = @()
            $CurrentService = $null
            
            foreach ($Line in $YamlLines) {
                $Line = $Line.Trim()
                
                if ($Line -eq "services:") {
                    $InServicesSection = $true
                    continue
                }
                
                if ($InServicesSection) {
                    if ($Line.StartsWith("- ") -or $Line.StartsWith("-")) {
                        # New service entry
                        if ($CurrentService) {
                            $Services += $CurrentService
                        }
                        $CurrentService = @{}
                    }
                    elseif ($Line -and -not $Line.StartsWith("#") -and $CurrentService -ne $null) {
                        if ($Line.Contains(":")) {
                            $Parts = $Line -split ":", 2
                            $Key = $Parts[0].Trim()
                            $Value = $Parts[1].Trim().Trim('"').Trim("'")
                            
                            switch ($Key) {
                                "id" { $CurrentService.id = $Value }
                                "name" { $CurrentService.name = $Value }
                                "type" { $CurrentService.type = $Value }
                                "host" { $CurrentService.host = $Value }
                                "port" { $CurrentService.port = [int]$Value }
                                "health_check_url" { $CurrentService.health_url = $Value }
                            }
                        }
                    }
                    elseif ($Line -and -not $Line.StartsWith("-") -and -not $Line.Contains(":")) {
                        # End of services section
                        break
                    }
                }
            }
            
            # Add last service
            if ($CurrentService) {
                $Services += $CurrentService
            }
            
            # Set default health URLs for services that don't have them
            foreach ($Service in $Services) {
                if (-not $Service.health_url) {
                    $Protocol = if ($Service.protocol) { $Service.protocol } else { "http" }
                    $Host = if ($Service.host) { $Service.host } else { "localhost" }
                    $Service.health_url = "${Protocol}://${Host}:$($Service.port)/health"
                }
            }
            
            Write-HealthLog "Loaded $($Services.Count) services from configuration" -Level "DEBUG"
            return $Services
            
        }
        catch {
            Write-HealthLog "Failed to parse configuration file: $($_.Exception.Message)" -Level "ERROR"
            return @()
        }
    }
    catch {
        Write-HealthLog "Error loading configuration: $($_.Exception.Message)" -Level "ERROR"
        return @()
    }
}

function Save-HealthState {
    try {
        $StateJson = $script:HealthState | ConvertTo-Json -Depth 10
        $StateJson | Out-File -FilePath $StateFile -Encoding UTF8 -Force
    }
    catch {
        Write-HealthLog "Failed to save health state: $($_.Exception.Message)" -Level "WARN"
    }
}

function Load-HealthState {
    try {
        if (Test-Path $StateFile) {
            $StateContent = Get-Content $StateFile -Raw | ConvertFrom-Json
            
            # Merge with current state structure
            if ($StateContent.Statistics) {
                $script:HealthState.Statistics = $StateContent.Statistics
            }
            if ($StateContent.AlertsSent) {
                $script:HealthState.AlertsSent = $StateContent.AlertsSent
            }
            
            Write-HealthLog "Loaded previous health state" -Level "DEBUG"
        }
    }
    catch {
        Write-HealthLog "Failed to load health state: $($_.Exception.Message)" -Level "WARN"
    }
}

function Show-HealthSummary {
    Write-Host ""
    Write-Host "MCP Health Monitor Summary" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Monitoring Statistics:" -ForegroundColor Yellow
    Write-Host "  Total Checks: $($script:HealthState.Statistics.TotalChecks)" -ForegroundColor White
    Write-Host "  Successful Checks: $($script:HealthState.Statistics.SuccessfulChecks)" -ForegroundColor Green
    Write-Host "  Failed Checks: $($script:HealthState.Statistics.FailedChecks)" -ForegroundColor Red
    Write-Host "  Restart Attempts: $($script:HealthState.Statistics.RestartAttempts)" -ForegroundColor Yellow
    Write-Host "  Successful Restarts: $($script:HealthState.Statistics.SuccessfulRestarts)" -ForegroundColor Green
    
    if ($script:HealthState.LastCheck) {
        Write-Host "  Last Check: $($script:HealthState.LastCheck.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    if ($script:HealthState.Services.Count -gt 0) {
        Write-Host "Service Health Status:" -ForegroundColor Yellow
        
        foreach ($ServiceState in $script:HealthState.Services.Values) {
            $StatusColor = if ($ServiceState.IsHealthy) { "Green" } else { "Red" }
            $StatusIcon = if ($ServiceState.IsHealthy) { "✓" } else { "✗" }
            
            Write-Host "  $StatusIcon $($ServiceState.ServiceName)" -ForegroundColor $StatusColor
            
            if ($ServiceState.ResponseTime) {
                Write-Host "    Response Time: $([math]::Round($ServiceState.ResponseTime, 1))ms" -ForegroundColor Gray
            }
            
            if ($ServiceState.ErrorMessage) {
                Write-Host "    Error: $($ServiceState.ErrorMessage)" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "No service health data available" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Create default alert configuration if it doesn't exist
function Initialize-AlertConfiguration {
    if (-not (Test-Path $AlertConfigPath)) {
        Write-HealthLog "Creating default alert configuration..." -Level "INFO"
        
        $DefaultAlertConfig = @{
            email = @{
                enabled = $false
                smtp_server = "smtp.example.com"
                smtp_port = 587
                use_ssl = $true
                username = ""
                password = ""
                from = "mcp-monitor@example.com"
                to = @("admin@example.com")
            }
            webhook = @{
                enabled = $false
                url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                auth_header = @{
                    name = "Authorization"
                    value = "Bearer YOUR_TOKEN"
                }
            }
        }
        
        try {
            $ConfigDir = Split-Path $AlertConfigPath -Parent
            if (-not (Test-Path $ConfigDir)) {
                New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
            }
            
            $DefaultAlertConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $AlertConfigPath -Encoding UTF8
            Write-HealthLog "Default alert configuration created: $AlertConfigPath" -Level "INFO"
        }
        catch {
            Write-HealthLog "Failed to create alert configuration: $($_.Exception.Message)" -Level "WARN"
        }
    }
}

# Main execution
try {
    Write-Host "MCP Health Monitor - Advanced Health Checking System" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    
    # Initialize
    Initialize-AlertConfiguration
    Load-HealthState
    
    # Show current configuration
    Write-HealthLog "Health Monitor Configuration:" -Level "INFO"
    Write-HealthLog "  Config Path: $ConfigPath" -Level "INFO"
    Write-HealthLog "  Log Path: $LogPath" -Level "INFO"
    Write-HealthLog "  Check Interval: $CheckInterval seconds" -Level "INFO"
    Write-HealthLog "  Timeout: $TimeoutSeconds seconds" -Level "INFO"
    Write-HealthLog "  Auto Restart: $AutoRestart" -Level "INFO"
    Write-HealthLog "  Email Alerts: $EmailAlerts" -Level "INFO"
    Write-HealthLog "  Webhook Alerts: $WebhookAlerts" -Level "INFO"
    Write-Host ""
    
    if ($Background) {
        # Run in background
        Write-HealthLog "Starting background monitoring..." -Level "INFO"
        Start-HealthMonitoring
    }
    elseif ($RunOnce) {
        # Single check
        Write-HealthLog "Performing single health check..." -Level "INFO"
        Start-HealthMonitoring
        Show-HealthSummary
    }
    else {
        # Interactive monitoring
        Start-HealthMonitoring
    }
    
}
catch {
    Write-HealthLog "Health monitor error: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}