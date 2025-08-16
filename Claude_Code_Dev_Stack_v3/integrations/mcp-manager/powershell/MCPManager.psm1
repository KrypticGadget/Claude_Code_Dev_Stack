# MCP Manager PowerShell Module
# Windows wrapper for MCP service management
# 
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

using namespace System.Collections.Generic
using namespace System.Management.Automation

# Module variables
$script:MCPManagerPath = Split-Path -Parent $PSScriptRoot
$script:PythonScript = Join-Path $MCPManagerPath "core\manager.py"
$script:ConfigPath = Join-Path $MCPManagerPath "config\mcp-services.yml"
$script:LogPath = Join-Path $MCPManagerPath "logs\mcp-manager.log"

# Ensure required directories exist
$RequiredDirs = @(
    (Join-Path $MCPManagerPath "config"),
    (Join-Path $MCPManagerPath "logs"),
    (Join-Path $MCPManagerPath "data")
)

foreach ($dir in $RequiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

class MCPService {
    [string]$Id
    [string]$Name
    [string]$Type
    [string]$Host
    [int]$Port
    [string]$Status
    [string]$Version
    [string]$Description
    [hashtable]$Metrics
    [datetime]$LastSeen
    
    MCPService([hashtable]$Properties) {
        $this.Id = $Properties.id
        $this.Name = $Properties.name
        $this.Type = $Properties.type
        $this.Host = $Properties.host
        $this.Port = $Properties.port
        $this.Status = $Properties.status
        $this.Version = $Properties.version
        $this.Description = $Properties.description
        $this.Metrics = $Properties.metrics
        $this.LastSeen = if ($Properties.last_seen) { [datetime]$Properties.last_seen } else { [datetime]::MinValue }
    }
    
    [string] GetUrl() {
        return "http://$($this.Host):$($this.Port)"
    }
    
    [bool] IsHealthy() {
        return $this.Status -eq "running" -and $this.LastSeen -gt (Get-Date).AddMinutes(-5)
    }
}

class MCPManagerAPI {
    [string]$PythonPath
    [string]$ScriptPath
    [string]$ConfigPath
    
    MCPManagerAPI([string]$PythonPath, [string]$ScriptPath, [string]$ConfigPath) {
        $this.PythonPath = $PythonPath
        $this.ScriptPath = $ScriptPath
        $this.ConfigPath = $ConfigPath
    }
    
    [object] InvokeManagerCommand([string]$Command, [hashtable]$Parameters = @{}) {
        try {
            $ParamJson = $Parameters | ConvertTo-Json -Compress
            $Arguments = @(
                $this.ScriptPath,
                "--command", $Command,
                "--config", $this.ConfigPath
            )
            
            if ($Parameters.Count -gt 0) {
                $Arguments += @("--params", $ParamJson)
            }
            
            $Result = & $this.PythonPath @Arguments 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                if ($Result -and $Result.Count -gt 0) {
                    $JsonResult = $Result -join "`n"
                    return $JsonResult | ConvertFrom-Json
                }
                return $null
            } else {
                throw "MCP Manager command failed with exit code $LASTEXITCODE`: $Result"
            }
        }
        catch {
            Write-Error "Failed to invoke MCP Manager command '$Command': $($_.Exception.Message)"
            return $null
        }
    }
}

# Global manager instance
$script:MCPManager = $null

function Initialize-MCPManager {
    <#
    .SYNOPSIS
        Initialize the MCP Manager
    
    .DESCRIPTION
        Sets up the MCP Manager with Python environment and configuration
    
    .PARAMETER PythonPath
        Path to Python executable (defaults to 'python')
    
    .PARAMETER ConfigPath
        Path to MCP configuration file
    
    .EXAMPLE
        Initialize-MCPManager
        
    .EXAMPLE
        Initialize-MCPManager -PythonPath "C:\Python39\python.exe"
    #>
    
    [CmdletBinding()]
    param(
        [string]$PythonPath = "python",
        [string]$ConfigPath = $script:ConfigPath
    )
    
    try {
        # Test Python availability
        $PythonVersion = & $PythonPath --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found at path: $PythonPath"
        }
        
        Write-Verbose "Using Python: $PythonVersion"
        
        # Create manager instance
        $script:MCPManager = [MCPManagerAPI]::new($PythonPath, $script:PythonScript, $ConfigPath)
        
        # Create default config if it doesn't exist
        if (-not (Test-Path $ConfigPath)) {
            Write-Verbose "Creating default configuration at: $ConfigPath"
            New-MCPConfiguration -ConfigPath $ConfigPath
        }
        
        Write-Host "MCP Manager initialized successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to initialize MCP Manager: $($_.Exception.Message)"
        return $false
    }
}

function Start-MCPManager {
    <#
    .SYNOPSIS
        Start the MCP Manager service
    
    .DESCRIPTION
        Starts the MCP Manager and begins service discovery and monitoring
    
    .PARAMETER Background
        Run in background mode
    
    .EXAMPLE
        Start-MCPManager
        
    .EXAMPLE
        Start-MCPManager -Background
    #>
    
    [CmdletBinding()]
    param(
        [switch]$Background
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $false
    }
    
    try {
        Write-Host "Starting MCP Manager..." -ForegroundColor Yellow
        
        $Parameters = @{
            background = $Background.IsPresent
        }
        
        $Result = $script:MCPManager.InvokeManagerCommand("start", $Parameters)
        
        if ($Result) {
            Write-Host "MCP Manager started successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to start MCP Manager"
            return $false
        }
    }
    catch {
        Write-Error "Error starting MCP Manager: $($_.Exception.Message)"
        return $false
    }
}

function Stop-MCPManager {
    <#
    .SYNOPSIS
        Stop the MCP Manager service
    
    .DESCRIPTION
        Stops the MCP Manager and all monitoring
    
    .EXAMPLE
        Stop-MCPManager
    #>
    
    [CmdletBinding()]
    param()
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized."
        return $false
    }
    
    try {
        Write-Host "Stopping MCP Manager..." -ForegroundColor Yellow
        
        $Result = $script:MCPManager.InvokeManagerCommand("stop")
        
        Write-Host "MCP Manager stopped successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Error stopping MCP Manager: $($_.Exception.Message)"
        return $false
    }
}

function Get-MCPServices {
    <#
    .SYNOPSIS
        Get all registered MCP services
    
    .DESCRIPTION
        Retrieves information about all registered MCP services
    
    .PARAMETER ServiceType
        Filter by service type (core, playwright, github, websearch, custom)
    
    .PARAMETER Status
        Filter by service status (running, stopped, error, starting)
    
    .EXAMPLE
        Get-MCPServices
        
    .EXAMPLE
        Get-MCPServices -ServiceType playwright
        
    .EXAMPLE
        Get-MCPServices -Status running
    #>
    
    [CmdletBinding()]
    param(
        [ValidateSet("core", "playwright", "github", "websearch", "custom", "proxy", "gateway")]
        [string]$ServiceType,
        
        [ValidateSet("running", "stopped", "error", "starting", "unknown")]
        [string]$Status
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return @()
    }
    
    try {
        $Parameters = @{}
        if ($ServiceType) { $Parameters.service_type = $ServiceType }
        if ($Status) { $Parameters.status = $Status }
        
        $Result = $script:MCPManager.InvokeManagerCommand("get_services", $Parameters)
        
        if ($Result -and $Result.services) {
            $Services = @()
            foreach ($ServiceData in $Result.services) {
                $Services += [MCPService]::new($ServiceData)
            }
            return $Services
        }
        
        return @()
    }
    catch {
        Write-Error "Error retrieving MCP services: $($_.Exception.Message)"
        return @()
    }
}

function Get-MCPServiceStatus {
    <#
    .SYNOPSIS
        Get overall MCP service status summary
    
    .DESCRIPTION
        Retrieves a summary of all service statuses and health metrics
    
    .EXAMPLE
        Get-MCPServiceStatus
    #>
    
    [CmdletBinding()]
    param()
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $null
    }
    
    try {
        $Result = $script:MCPManager.InvokeManagerCommand("get_status")
        return $Result
    }
    catch {
        Write-Error "Error retrieving MCP service status: $($_.Exception.Message)"
        return $null
    }
}

function Register-MCPService {
    <#
    .SYNOPSIS
        Register a new MCP service
    
    .DESCRIPTION
        Registers a new MCP service with the manager
    
    .PARAMETER Name
        Service name
    
    .PARAMETER Type
        Service type
    
    .PARAMETER Host
        Service host (default: localhost)
    
    .PARAMETER Port
        Service port
    
    .PARAMETER Path
        Service path (default: /)
    
    .PARAMETER Description
        Service description
    
    .EXAMPLE
        Register-MCPService -Name "Custom Service" -Type custom -Port 8090
        
    .EXAMPLE
        Register-MCPService -Name "GitHub Service" -Type github -Host "github.service.local" -Port 8081 -Description "GitHub integration service"
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,
        
        [Parameter(Mandatory)]
        [ValidateSet("core", "playwright", "github", "websearch", "custom", "proxy", "gateway")]
        [string]$Type,
        
        [string]$Host = "localhost",
        
        [Parameter(Mandatory)]
        [int]$Port,
        
        [string]$Path = "/",
        
        [string]$Description = ""
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $false
    }
    
    try {
        $ServiceConfig = @{
            name = $Name
            type = $Type
            host = $Host
            port = $Port
            path = $Path
            description = $Description
        }
        
        $Parameters = @{
            service_config = $ServiceConfig
        }
        
        $Result = $script:MCPManager.InvokeManagerCommand("register_service", $Parameters)
        
        if ($Result -and $Result.success) {
            Write-Host "Service '$Name' registered successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to register service '$Name'"
            return $false
        }
    }
    catch {
        Write-Error "Error registering MCP service: $($_.Exception.Message)"
        return $false
    }
}

function Start-MCPService {
    <#
    .SYNOPSIS
        Start an MCP service
    
    .DESCRIPTION
        Starts a specific MCP service by ID or name
    
    .PARAMETER Id
        Service ID
    
    .PARAMETER Name
        Service name
    
    .EXAMPLE
        Start-MCPService -Id "playwright-service"
        
    .EXAMPLE
        Start-MCPService -Name "GitHub Service"
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(ParameterSetName = "ById")]
        [string]$Id,
        
        [Parameter(ParameterSetName = "ByName")]
        [string]$Name
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $false
    }
    
    try {
        $Parameters = @{}
        if ($Id) { $Parameters.service_id = $Id }
        if ($Name) { $Parameters.service_name = $Name }
        
        $Result = $script:MCPManager.InvokeManagerCommand("start_service", $Parameters)
        
        if ($Result -and $Result.success) {
            $ServiceName = if ($Name) { $Name } else { $Id }
            Write-Host "Service '$ServiceName' started successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to start service"
            return $false
        }
    }
    catch {
        Write-Error "Error starting MCP service: $($_.Exception.Message)"
        return $false
    }
}

function Stop-MCPService {
    <#
    .SYNOPSIS
        Stop an MCP service
    
    .DESCRIPTION
        Stops a specific MCP service by ID or name
    
    .PARAMETER Id
        Service ID
    
    .PARAMETER Name
        Service name
    
    .EXAMPLE
        Stop-MCPService -Id "playwright-service"
        
    .EXAMPLE
        Stop-MCPService -Name "GitHub Service"
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(ParameterSetName = "ById")]
        [string]$Id,
        
        [Parameter(ParameterSetName = "ByName")]
        [string]$Name
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $false
    }
    
    try {
        $Parameters = @{}
        if ($Id) { $Parameters.service_id = $Id }
        if ($Name) { $Parameters.service_name = $Name }
        
        $Result = $script:MCPManager.InvokeManagerCommand("stop_service", $Parameters)
        
        if ($Result -and $Result.success) {
            $ServiceName = if ($Name) { $Name } else { $Id }
            Write-Host "Service '$ServiceName' stopped successfully" -ForegroundColor Yellow
            return $true
        } else {
            Write-Error "Failed to stop service"
            return $false
        }
    }
    catch {
        Write-Error "Error stopping MCP service: $($_.Exception.Message)"
        return $false
    }
}

function Test-MCPServiceHealth {
    <#
    .SYNOPSIS
        Test MCP service health
    
    .DESCRIPTION
        Performs health checks on specified services
    
    .PARAMETER Id
        Service ID to test
    
    .PARAMETER All
        Test all services
    
    .EXAMPLE
        Test-MCPServiceHealth -Id "playwright-service"
        
    .EXAMPLE
        Test-MCPServiceHealth -All
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(ParameterSetName = "Single")]
        [string]$Id,
        
        [Parameter(ParameterSetName = "All")]
        [switch]$All
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $null
    }
    
    try {
        $Parameters = @{}
        if ($Id) { $Parameters.service_id = $Id }
        if ($All) { $Parameters.all_services = $true }
        
        $Result = $script:MCPManager.InvokeManagerCommand("health_check", $Parameters)
        return $Result
    }
    catch {
        Write-Error "Error testing MCP service health: $($_.Exception.Message)"
        return $null
    }
}

function Show-MCPDashboard {
    <#
    .SYNOPSIS
        Display MCP Manager dashboard
    
    .DESCRIPTION
        Shows a real-time dashboard of MCP services and their status
    
    .PARAMETER RefreshInterval
        Refresh interval in seconds (default: 5)
    
    .EXAMPLE
        Show-MCPDashboard
        
    .EXAMPLE
        Show-MCPDashboard -RefreshInterval 10
    #>
    
    [CmdletBinding()]
    param(
        [int]$RefreshInterval = 5
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return
    }
    
    try {
        Write-Host "MCP Manager Dashboard" -ForegroundColor Cyan
        Write-Host "=====================" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
        Write-Host ""
        
        while ($true) {
            Clear-Host
            
            Write-Host "MCP Manager Dashboard - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
            Write-Host "=" * 60 -ForegroundColor Cyan
            
            # Get service status
            $Status = Get-MCPServiceStatus
            if ($Status) {
                Write-Host "Total Services: $($Status.total_services)" -ForegroundColor White
                Write-Host "Healthy Services: $($Status.healthy_services)" -ForegroundColor Green
                
                if ($Status.status_breakdown) {
                    Write-Host ""
                    Write-Host "Status Breakdown:" -ForegroundColor Yellow
                    foreach ($StatusType in $Status.status_breakdown.PSObject.Properties) {
                        $Color = switch ($StatusType.Name) {
                            "running" { "Green" }
                            "error" { "Red" }
                            "stopped" { "Gray" }
                            "starting" { "Yellow" }
                            default { "White" }
                        }
                        Write-Host "  $($StatusType.Name): $($StatusType.Value)" -ForegroundColor $Color
                    }
                }
            }
            
            Write-Host ""
            Write-Host "Services:" -ForegroundColor Yellow
            Write-Host "-" * 40 -ForegroundColor Gray
            
            # Get all services
            $Services = Get-MCPServices
            if ($Services.Count -gt 0) {
                foreach ($Service in $Services) {
                    $StatusColor = switch ($Service.Status) {
                        "running" { "Green" }
                        "error" { "Red" }
                        "stopped" { "Gray" }
                        "starting" { "Yellow" }
                        default { "White" }
                    }
                    
                    $HealthIcon = if ($Service.IsHealthy()) { "✓" } else { "✗" }
                    
                    Write-Host "  $HealthIcon $($Service.Name) [$($Service.Type)]" -ForegroundColor $StatusColor
                    Write-Host "    $($Service.GetUrl()) - $($Service.Status)" -ForegroundColor Gray
                    
                    if ($Service.Metrics -and $Service.Metrics.requests_total) {
                        Write-Host "    Requests: $($Service.Metrics.requests_total), Errors: $($Service.Metrics.error_count)" -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "  No services registered" -ForegroundColor Gray
            }
            
            Write-Host ""
            Write-Host "Next refresh in $RefreshInterval seconds..." -ForegroundColor DarkGray
            
            Start-Sleep -Seconds $RefreshInterval
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host ""
        Write-Host "Dashboard stopped by user" -ForegroundColor Yellow
    }
    catch {
        Write-Error "Error displaying dashboard: $($_.Exception.Message)"
    }
}

function New-MCPConfiguration {
    <#
    .SYNOPSIS
        Create a new MCP configuration file
    
    .DESCRIPTION
        Creates a default MCP configuration file with sample services
    
    .PARAMETER ConfigPath
        Path for the configuration file
    
    .PARAMETER Force
        Overwrite existing configuration
    
    .EXAMPLE
        New-MCPConfiguration
        
    .EXAMPLE
        New-MCPConfiguration -ConfigPath "custom-config.yml" -Force
    #>
    
    [CmdletBinding()]
    param(
        [string]$ConfigPath = $script:ConfigPath,
        [switch]$Force
    )
    
    if ((Test-Path $ConfigPath) -and -not $Force) {
        Write-Warning "Configuration file already exists at: $ConfigPath"
        Write-Host "Use -Force to overwrite" -ForegroundColor Yellow
        return $false
    }
    
    try {
        $DefaultConfig = @"
# MCP Manager Configuration
# Generated by MCP Manager PowerShell Module

health_check_interval: 30

services:
  - name: "Playwright MCP"
    type: "playwright"
    host: "localhost"
    port: 8080
    path: "/"
    description: "Browser automation and testing service"
    tags: ["automation", "testing", "browser"]
    
  - name: "GitHub MCP"
    type: "github"
    host: "localhost"
    port: 8081
    path: "/"
    description: "GitHub repository management service"
    tags: ["git", "repository", "github"]
    
  - name: "Web Search MCP"
    type: "websearch"
    host: "localhost"
    port: 8082
    path: "/"
    description: "Web search and scraping service"
    tags: ["search", "web", "scraping"]

load_balancing:
  default_algorithm: "round_robin"
  health_check_timeout: 10
  
logging:
  level: "INFO"
  file: "mcp-manager.log"
"@
        
        # Ensure directory exists
        $ConfigDir = Split-Path -Parent $ConfigPath
        if (-not (Test-Path $ConfigDir)) {
            New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
        }
        
        $DefaultConfig | Out-File -FilePath $ConfigPath -Encoding UTF8
        
        Write-Host "Default configuration created at: $ConfigPath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to create configuration file: $($_.Exception.Message)"
        return $false
    }
}

function Export-MCPConfiguration {
    <#
    .SYNOPSIS
        Export current MCP configuration
    
    .DESCRIPTION
        Exports the current service configuration to a file
    
    .PARAMETER OutputPath
        Output file path
    
    .PARAMETER Format
        Output format (yaml, json)
    
    .EXAMPLE
        Export-MCPConfiguration -OutputPath "backup-config.yml"
        
    .EXAMPLE
        Export-MCPConfiguration -OutputPath "config.json" -Format json
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$OutputPath,
        
        [ValidateSet("yaml", "json")]
        [string]$Format = "yaml"
    )
    
    if (-not $script:MCPManager) {
        Write-Warning "MCP Manager not initialized. Run Initialize-MCPManager first."
        return $false
    }
    
    try {
        $Parameters = @{
            output_path = $OutputPath
            format = $Format
        }
        
        $Result = $script:MCPManager.InvokeManagerCommand("export_config", $Parameters)
        
        if ($Result -and $Result.success) {
            Write-Host "Configuration exported to: $OutputPath" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to export configuration"
            return $false
        }
    }
    catch {
        Write-Error "Error exporting configuration: $($_.Exception.Message)"
        return $false
    }
}

# Enhanced Windows-specific functions

function Get-MCPProcessInfo {
    <#
    .SYNOPSIS
        Get detailed process information for MCP services
    
    .DESCRIPTION
        Retrieves detailed Windows process information for running MCP services
    
    .EXAMPLE
        Get-MCPProcessInfo
    #>
    
    [CmdletBinding()]
    param()
    
    try {
        $MCPProcesses = @()
        $PythonProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -or $_.Name -like "*mcp*" }
        
        foreach ($Process in $PythonProcesses) {
            try {
                $ProcessInfo = @{
                    ProcessId = $Process.Id
                    ProcessName = $Process.ProcessName
                    StartTime = $Process.StartTime
                    CPU = [math]::Round($Process.CPU, 2)
                    WorkingSet = [math]::Round($Process.WorkingSet64 / 1MB, 2)
                    VirtualMemory = [math]::Round($Process.VirtualMemorySize64 / 1MB, 2)
                    HandleCount = $Process.HandleCount
                    ThreadCount = $Process.Threads.Count
                    CommandLine = $null
                }
                
                # Try to get command line
                try {
                    $WmiProcess = Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($Process.Id)" -ErrorAction SilentlyContinue
                    if ($WmiProcess) {
                        $ProcessInfo.CommandLine = $WmiProcess.CommandLine
                    }
                }
                catch {
                    # Command line not available
                }
                
                # Check if this is likely an MCP process
                if ($ProcessInfo.CommandLine -and ($ProcessInfo.CommandLine -like "*mcp*" -or $ProcessInfo.CommandLine -like "*8080*" -or $ProcessInfo.CommandLine -like "*8081*" -or $ProcessInfo.CommandLine -like "*8082*")) {
                    $MCPProcesses += $ProcessInfo
                }
                elseif (-not $ProcessInfo.CommandLine -and $Process.ProcessName -like "*python*") {
                    $MCPProcesses += $ProcessInfo
                }
            }
            catch {
                Write-Verbose "Error getting info for process $($Process.Id): $($_.Exception.Message)"
            }
        }
        
        return $MCPProcesses
    }
    catch {
        Write-Error "Failed to get MCP process information: $($_.Exception.Message)"
        return @()
    }
}

function Test-MCPPortAvailability {
    <#
    .SYNOPSIS
        Test if MCP service ports are available
    
    .DESCRIPTION
        Checks if the standard MCP service ports are available or in use
    
    .PARAMETER Ports
        Array of ports to check (defaults to standard MCP ports)
    
    .EXAMPLE
        Test-MCPPortAvailability
        
    .EXAMPLE
        Test-MCPPortAvailability -Ports @(8080, 8081, 8082)
    #>
    
    [CmdletBinding()]
    param(
        [int[]]$Ports = @(8080, 8081, 8082, 8090, 8091, 8092)
    )
    
    $PortStatus = @()
    
    foreach ($Port in $Ports) {
        try {
            $TcpClient = New-Object System.Net.Sockets.TcpClient
            $AsyncResult = $TcpClient.BeginConnect("localhost", $Port, $null, $null)
            $Success = $AsyncResult.AsyncWaitHandle.WaitOne(1000)  # 1 second timeout
            
            if ($Success) {
                $TcpClient.EndConnect($AsyncResult)
                $TcpClient.Close()
                
                # Port is in use, try to identify the process
                $ProcessInfo = $null
                try {
                    $NetStatResult = netstat -ano | Select-String ":$Port "
                    if ($NetStatResult) {
                        $ProcessId = ($NetStatResult.ToString() -split '\s+')[-1]
                        if ($ProcessId -match '^\d+$') {
                            $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
                            if ($Process) {
                                $ProcessInfo = @{
                                    ProcessId = $Process.Id
                                    ProcessName = $Process.ProcessName
                                    StartTime = $Process.StartTime
                                }
                            }
                        }
                    }
                }
                catch {
                    # Process identification failed
                }
                
                $PortStatus += @{
                    Port = $Port
                    Available = $false
                    InUse = $true
                    Process = $ProcessInfo
                }
            }
            else {
                $TcpClient.Close()
                $PortStatus += @{
                    Port = $Port
                    Available = $true
                    InUse = $false
                    Process = $null
                }
            }
        }
        catch {
            $PortStatus += @{
                Port = $Port
                Available = $true
                InUse = $false
                Process = $null
            }
        }
    }
    
    return $PortStatus
}

function Get-MCPSystemRequirements {
    <#
    .SYNOPSIS
        Check system requirements for MCP Manager
    
    .DESCRIPTION
        Validates that the system meets requirements for running MCP Manager
    
    .EXAMPLE
        Get-MCPSystemRequirements
    #>
    
    [CmdletBinding()]
    param()
    
    $Requirements = @{
        PowerShellVersion = @{
            Required = "5.1"
            Current = $PSVersionTable.PSVersion.ToString()
            Status = "Unknown"
        }
        PythonVersion = @{
            Required = "3.8+"
            Current = $null
            Status = "Unknown"
        }
        AvailableMemory = @{
            Required = "2 GB"
            Current = $null
            Status = "Unknown"
        }
        DiskSpace = @{
            Required = "1 GB"
            Current = $null
            Status = "Unknown"
        }
        NetworkPorts = @{
            Required = "8080-8092"
            Current = $null
            Status = "Unknown"
        }
    }
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        $Requirements.PowerShellVersion.Status = "Pass"
    }
    else {
        $Requirements.PowerShellVersion.Status = "Fail"
    }
    
    # Check Python version
    try {
        $PythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $Requirements.PythonVersion.Current = $PythonVersion.ToString()
            if ($PythonVersion -match "Python 3\.([8-9]|\d{2})") {
                $Requirements.PythonVersion.Status = "Pass"
            }
            else {
                $Requirements.PythonVersion.Status = "Fail"
            }
        }
        else {
            $Requirements.PythonVersion.Current = "Not found"
            $Requirements.PythonVersion.Status = "Fail"
        }
    }
    catch {
        $Requirements.PythonVersion.Current = "Not found"
        $Requirements.PythonVersion.Status = "Fail"
    }
    
    # Check available memory
    try {
        $Memory = Get-WmiObject -Class Win32_ComputerSystem
        $AvailableMemoryGB = [math]::Round($Memory.TotalPhysicalMemory / 1GB, 2)
        $Requirements.AvailableMemory.Current = "$AvailableMemoryGB GB"
        
        if ($AvailableMemoryGB -ge 2) {
            $Requirements.AvailableMemory.Status = "Pass"
        }
        else {
            $Requirements.AvailableMemory.Status = "Fail"
        }
    }
    catch {
        $Requirements.AvailableMemory.Current = "Unknown"
        $Requirements.AvailableMemory.Status = "Unknown"
    }
    
    # Check disk space
    try {
        $Disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
        $FreeSpaceGB = [math]::Round($Disk.FreeSpace / 1GB, 2)
        $Requirements.DiskSpace.Current = "$FreeSpaceGB GB free"
        
        if ($FreeSpaceGB -ge 1) {
            $Requirements.DiskSpace.Status = "Pass"
        }
        else {
            $Requirements.DiskSpace.Status = "Fail"
        }
    }
    catch {
        $Requirements.DiskSpace.Current = "Unknown"
        $Requirements.DiskSpace.Status = "Unknown"
    }
    
    # Check network ports
    $PortStatus = Test-MCPPortAvailability
    $AvailablePorts = ($PortStatus | Where-Object { $_.Available }).Count
    $TotalPorts = $PortStatus.Count
    
    $Requirements.NetworkPorts.Current = "$AvailablePorts/$TotalPorts available"
    if ($AvailablePorts -ge ($TotalPorts * 0.5)) {
        $Requirements.NetworkPorts.Status = "Pass"
    }
    else {
        $Requirements.NetworkPorts.Status = "Warn"
    }
    
    return $Requirements
}

function Show-MCPSystemInfo {
    <#
    .SYNOPSIS
        Display comprehensive MCP system information
    
    .DESCRIPTION
        Shows detailed system information relevant to MCP Manager
    
    .EXAMPLE
        Show-MCPSystemInfo
    #>
    
    [CmdletBinding()]
    param()
    
    Write-Host ""
    Write-Host "MCP Manager System Information" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    
    # System requirements
    Write-Host "System Requirements:" -ForegroundColor Yellow
    $Requirements = Get-MCPSystemRequirements
    
    foreach ($Requirement in $Requirements.Keys) {
        $Req = $Requirements[$Requirement]
        $StatusColor = switch ($Req.Status) {
            "Pass" { "Green" }
            "Fail" { "Red" }
            "Warn" { "Yellow" }
            default { "Gray" }
        }
        
        Write-Host "  $Requirement`: $($Req.Status)" -ForegroundColor $StatusColor
        Write-Host "    Required: $($Req.Required)" -ForegroundColor Gray
        Write-Host "    Current: $($Req.Current)" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Process information
    Write-Host "MCP Processes:" -ForegroundColor Yellow
    $Processes = Get-MCPProcessInfo
    
    if ($Processes.Count -gt 0) {
        foreach ($Process in $Processes) {
            Write-Host "  PID $($Process.ProcessId) - $($Process.ProcessName)" -ForegroundColor White
            Write-Host "    Memory: $($Process.WorkingSet) MB" -ForegroundColor Gray
            Write-Host "    CPU: $($Process.CPU) seconds" -ForegroundColor Gray
            Write-Host "    Handles: $($Process.HandleCount)" -ForegroundColor Gray
            if ($Process.CommandLine) {
                $CmdLine = if ($Process.CommandLine.Length -gt 60) { $Process.CommandLine.Substring(0, 57) + "..." } else { $Process.CommandLine }
                Write-Host "    Command: $CmdLine" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }
    else {
        Write-Host "  No MCP processes found" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Port status
    Write-Host "Port Status:" -ForegroundColor Yellow
    $PortStatus = Test-MCPPortAvailability
    
    foreach ($Port in $PortStatus) {
        $StatusText = if ($Port.Available) { "Available" } else { "In Use" }
        $StatusColor = if ($Port.Available) { "Green" } else { "Red" }
        
        Write-Host "  Port $($Port.Port): $StatusText" -ForegroundColor $StatusColor
        
        if ($Port.Process) {
            Write-Host "    Used by: $($Port.Process.ProcessName) (PID $($Port.Process.ProcessId))" -ForegroundColor Gray
        }
    }
    Write-Host ""
}

# Export module members
Export-ModuleMember -Function @(
    'Initialize-MCPManager',
    'Start-MCPManager',
    'Stop-MCPManager',
    'Get-MCPServices',
    'Get-MCPServiceStatus',
    'Register-MCPService',
    'Start-MCPService',
    'Stop-MCPService',
    'Test-MCPServiceHealth',
    'Show-MCPDashboard',
    'New-MCPConfiguration',
    'Export-MCPConfiguration',
    'Get-MCPProcessInfo',
    'Test-MCPPortAvailability',
    'Get-MCPSystemRequirements',
    'Show-MCPSystemInfo'
)

# Module initialization
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Warning "This module requires PowerShell 5.0 or later"
}

Write-Host "MCP Manager PowerShell Module loaded" -ForegroundColor Green
Write-Host "Run 'Initialize-MCPManager' to get started" -ForegroundColor Yellow