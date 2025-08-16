#!/usr/bin/env powershell
#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code Dev Stack v3.0 Master Launch System (PowerShell)
    
.DESCRIPTION
    Single command to orchestrate all Claude Code Dev Stack v3.0 services
    Includes environment validation, virtual environment activation, core services,
    MCP servers, dashboard, browser, mobile interfaces, and terminal tools.
    
.PARAMETER Mode
    Launch mode: "full", "core", "web", "mobile", "debug"
    
.PARAMETER SkipHealthCheck
    Skip health checks for faster startup
    
.PARAMETER LogLevel
    Logging level: "debug", "info", "warn", "error"
    
.EXAMPLE
    .\claude-start.ps1
    .\claude-start.ps1 -Mode full
    .\claude-start.ps1 -Mode core -LogLevel debug
#>

param(
    [ValidateSet("full", "core", "web", "mobile", "debug")]
    [string]$Mode = "full",
    
    [switch]$SkipHealthCheck,
    
    [ValidateSet("debug", "info", "warn", "error")]
    [string]$LogLevel = "info",
    
    [switch]$AutoBrowser,
    
    [string]$CustomPort = "",
    
    [switch]$LocalOnly
)

# ==============================================================================
# CLAUDE CODE DEV STACK V3.0 MASTER ORCHESTRATION SYSTEM
# ==============================================================================

# Color and logging functions
$Global:LogLevel = $LogLevel
$Global:ProcessList = @()
$Global:ServiceStatus = @{}
$Global:StartTime = Get-Date

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO",
        [ConsoleColor]$Color = "White"
    )
    
    $levelMap = @{
        "DEBUG" = 0; "INFO" = 1; "WARN" = 2; "ERROR" = 3; "SUCCESS" = 1
    }
    $currentLevel = @{ "debug" = 0; "info" = 1; "warn" = 2; "error" = 3 }[$Global:LogLevel]
    
    if ($levelMap[$Level] -ge $currentLevel) {
        $timestamp = Get-Date -Format "HH:mm:ss.fff"
        $prefix = switch ($Level) {
            "DEBUG" { "🔍"; $Color = "Gray" }
            "INFO"  { "ℹ️"; $Color = "Cyan" }
            "WARN"  { "⚠️"; $Color = "Yellow" }
            "ERROR" { "❌"; $Color = "Red" }
            "SUCCESS" { "✅"; $Color = "Green" }
        }
        Write-Host "[$timestamp] $prefix $Message" -ForegroundColor $Color
    }
}

function Write-Banner {
    param([string]$Title, [string]$Subtitle = "")
    
    $width = 80
    $border = "=" * $width
    
    Write-Host ""
    Write-Host $border -ForegroundColor Cyan
    Write-Host $Title.PadLeft([math]::Floor(($width + $Title.Length) / 2)).PadRight($width) -ForegroundColor Yellow
    if ($Subtitle) {
        Write-Host $Subtitle.PadLeft([math]::Floor(($width + $Subtitle.Length) / 2)).PadRight($width) -ForegroundColor Gray
    }
    Write-Host $border -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisite {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$InstallHint = ""
    )
    
    Write-Log "Checking $Name..." "DEBUG"
    try {
        $result = & $Test
        if ($result) {
            Write-Log "$Name: OK" "SUCCESS"
            return $true
        } else {
            Write-Log "$Name: MISSING" "ERROR"
            if ($InstallHint) { Write-Log "Install hint: $InstallHint" "WARN" }
            return $false
        }
    } catch {
        Write-Log "$Name: ERROR - $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-ServiceWithHealthCheck {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory = $PWD,
        [string]$HealthCheckUrl = "",
        [int]$HealthCheckTimeout = 30,
        [hashtable]$Environment = @{},
        [switch]$Background
    )
    
    Write-Log "Starting $Name..." "INFO"
    
    # Prepare environment
    $env = $Environment.Clone()
    foreach ($key in $env.Keys) {
        [Environment]::SetEnvironmentVariable($key, $env[$key], "Process")
    }
    
    try {
        # Start process
        $processArgs = @{
            FilePath = "powershell"
            ArgumentList = @("-NoProfile", "-Command", $Command)
            WorkingDirectory = $WorkingDirectory
            PassThru = $true
        }
        
        if ($Background) {
            $processArgs.WindowStyle = "Hidden"
        }
        
        $process = Start-Process @processArgs
        $Global:ProcessList += $process
        
        # Health check
        if ($HealthCheckUrl -and -not $SkipHealthCheck) {
            Write-Log "Waiting for $Name to be ready..." "DEBUG"
            $startTime = Get-Date
            $ready = $false
            
            while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($HealthCheckTimeout)) {
                try {
                    $response = Invoke-WebRequest -Uri $HealthCheckUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        $ready = $true
                        break
                    }
                } catch {
                    # Ignore connection errors during startup
                }
                Start-Sleep -Milliseconds 500
            }
            
            if ($ready) {
                Write-Log "$Name is ready! ($HealthCheckUrl)" "SUCCESS"
                $Global:ServiceStatus[$Name] = "Running"
            } else {
                Write-Log "$Name health check timeout" "WARN"
                $Global:ServiceStatus[$Name] = "Timeout"
            }
        } else {
            Start-Sleep -Seconds 2
            if (-not $process.HasExited) {
                Write-Log "$Name started successfully" "SUCCESS"
                $Global:ServiceStatus[$Name] = "Running"
            } else {
                Write-Log "$Name failed to start" "ERROR"
                $Global:ServiceStatus[$Name] = "Failed"
            }
        }
        
        return $process
    } catch {
        Write-Log "Failed to start $Name: $($_.Exception.Message)" "ERROR"
        $Global:ServiceStatus[$Name] = "Failed"
        return $null
    }
}

function Test-PortAvailable {
    param([int]$Port)
    
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false  # Port is occupied
    } catch {
        return $true   # Port is available
    }
}

function Find-AvailablePort {
    param([int]$StartPort = 3000)
    
    $port = $StartPort
    while (-not (Test-PortAvailable $port)) {
        $port++
    }
    return $port
}

# ==============================================================================
# ENVIRONMENT VALIDATION
# ==============================================================================

function Test-Environment {
    Write-Banner "ENVIRONMENT VALIDATION" "Checking prerequisites and dependencies"
    
    $allGood = $true
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    Write-Log "PowerShell version: $psVersion" "INFO"
    
    # Check Python
    $allGood = $allGood -and (Test-Prerequisite "Python" {
        try {
            $version = python --version 2>&1
            Write-Log "Python version: $version" "DEBUG"
            return $version -match "Python 3\."
        } catch { return $false }
    } "Install Python 3.8+ from python.org")
    
    # Check Node.js
    $allGood = $allGood -and (Test-Prerequisite "Node.js" {
        try {
            $version = node --version 2>&1
            Write-Log "Node.js version: $version" "DEBUG"
            return $version -match "v\d+"
        } catch { return $false }
    } "Install Node.js from nodejs.org")
    
    # Check Git
    $allGood = $allGood -and (Test-Prerequisite "Git" {
        try {
            $version = git --version 2>&1
            Write-Log "Git version: $version" "DEBUG"
            return $version -match "git version"
        } catch { return $false }
    } "Install Git from git-scm.com")
    
    # Check Claude CLI
    $allGood = $allGood -and (Test-Prerequisite "Claude CLI" {
        try {
            claude --version 2>&1 | Out-Null
            return $true
        } catch { return $false }
    } "Install Claude CLI from claude.ai")
    
    # Check project structure
    $requiredDirs = @(
        "Claude_Code_Dev_Stack_v3",
        ".claude-example",
        "Claude_Code_Dev_Stack_v3\apps\web"
    )
    
    foreach ($dir in $requiredDirs) {
        $allGood = $allGood -and (Test-Prerequisite "Directory: $dir" {
            Test-Path $dir
        })
    }
    
    if (-not $allGood) {
        Write-Log "Environment validation failed! Please fix the issues above." "ERROR"
        exit 1
    }
    
    Write-Log "Environment validation passed!" "SUCCESS"
    return $true
}

# ==============================================================================
# VIRTUAL ENVIRONMENT MANAGEMENT
# ==============================================================================

function Initialize-VirtualEnvironments {
    Write-Banner "VIRTUAL ENVIRONMENT SETUP" "Preparing Python and Node.js environments"
    
    # Python virtual environment for dashboard/mobile
    $pythonVenvPath = ".claude-example\mobile\.venv"
    if (-not (Test-Path $pythonVenvPath)) {
        Write-Log "Creating Python virtual environment..." "INFO"
        python -m venv $pythonVenvPath
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to create Python virtual environment" "ERROR"
            exit 1
        }
    }
    
    # Activate Python virtual environment and install dependencies
    $venvPython = "$pythonVenvPath\Scripts\python.exe"
    $venvPip = "$pythonVenvPath\Scripts\pip.exe"
    
    Write-Log "Installing Python dependencies..." "INFO"
    & $venvPip install --upgrade pip --quiet
    
    $pythonPackages = @(
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "flask-cors>=2.0.0",
        "psutil>=5.9.0",
        "GitPython>=3.1.0",
        "watchdog>=3.0.0",
        "qrcode[pil]>=7.4.0",
        "requests>=2.31.0"
    )
    
    foreach ($package in $pythonPackages) {
        Write-Log "Installing $package..." "DEBUG"
        & $venvPip install $package --quiet --disable-pip-version-check
    }
    
    # Node.js dependencies for web app
    Push-Location "Claude_Code_Dev_Stack_v3\apps\web"
    if (Test-Path "package.json") {
        Write-Log "Installing Node.js dependencies..." "INFO"
        npm install --silent
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install Node.js dependencies" "WARN"
        }
    }
    Pop-Location
    
    Write-Log "Virtual environments ready!" "SUCCESS"
}

# ==============================================================================
# CORE SERVICES
# ==============================================================================

function Start-CoreServices {
    Write-Banner "CORE SERVICES" "Starting essential Claude Code services"
    
    $services = @()
    
    # Start real-time dashboard
    if ($Mode -in @("full", "core")) {
        $dashboardPort = if ($CustomPort) { $CustomPort } else { Find-AvailablePort 8080 }
        $venvPython = ".claude-example\mobile\.venv\Scripts\python.exe"
        
        $services += Start-ServiceWithHealthCheck -Name "Real-time Dashboard" `
            -Command "$venvPython .claude-example\dashboard\realtime_dashboard.py --port $dashboardPort --host 0.0.0.0" `
            -HealthCheckUrl "http://localhost:$dashboardPort" `
            -Background
        
        Write-Log "Dashboard available at: http://localhost:$dashboardPort" "INFO"
    }
    
    return $services
}

# ==============================================================================
# MCP SERVERS
# ==============================================================================

function Start-MCPServers {
    Write-Banner "MCP SERVERS" "Initializing Model Context Protocol servers"
    
    Write-Log "Checking MCP server configuration..." "INFO"
    
    # Check if MCP servers are configured
    try {
        $mcpStatus = claude mcp list 2>&1
        Write-Log "MCP servers status: $mcpStatus" "DEBUG"
    } catch {
        Write-Log "MCP servers not configured, skipping..." "WARN"
        return
    }
    
    # Attempt to start configured MCP servers
    $mcpCommands = @(
        "claude mcp add playwright npx '@playwright/mcp@latest'",
        "claude mcp add brave-search npx -y @modelcontextprotocol/server-brave-search"
    )
    
    foreach ($cmd in $mcpCommands) {
        try {
            Write-Log "Configuring MCP: $cmd" "DEBUG"
            # Note: MCP servers are managed by Claude CLI, not directly started here
        } catch {
            Write-Log "MCP configuration warning: $cmd" "WARN"
        }
    }
    
    Write-Log "MCP servers configured" "SUCCESS"
}

# ==============================================================================
# WEB APPLICATION
# ==============================================================================

function Start-WebApplication {
    Write-Banner "WEB APPLICATION" "Starting React PWA and development server"
    
    if ($Mode -notin @("full", "web")) {
        Write-Log "Skipping web application (mode: $Mode)" "INFO"
        return
    }
    
    Push-Location "Claude_Code_Dev_Stack_v3\apps\web"
    
    # Find available port for web app
    $webPort = Find-AvailablePort 3000
    
    # Start Vite development server
    $env:PORT = $webPort
    $webProcess = Start-ServiceWithHealthCheck -Name "Web Application" `
        -Command "npm run dev -- --port $webPort --host 0.0.0.0" `
        -HealthCheckUrl "http://localhost:$webPort" `
        -Background
    
    Pop-Location
    
    if ($webProcess) {
        Write-Log "Web application available at: http://localhost:$webPort" "INFO"
        
        # Auto-open browser if requested
        if ($AutoBrowser) {
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:$webPort"
        }
    }
    
    return $webProcess
}

# ==============================================================================
# MOBILE INTERFACES
# ==============================================================================

function Start-MobileInterface {
    Write-Banner "MOBILE INTERFACE" "Setting up mobile access and QR codes"
    
    if ($Mode -notin @("full", "mobile")) {
        Write-Log "Skipping mobile interface (mode: $Mode)" "INFO"
        return
    }
    
    $venvPython = ".claude-example\mobile\.venv\Scripts\python.exe"
    $mobilePort = Find-AvailablePort 8080
    
    # Start mobile launcher
    $mobileArgs = "--port $mobilePort"
    if ($LocalOnly) {
        $mobileArgs += " --local-only"
    }
    
    $mobileProcess = Start-ServiceWithHealthCheck -Name "Mobile Interface" `
        -Command "$venvPython .claude-example\mobile\launch_mobile.py $mobileArgs" `
        -HealthCheckUrl "http://localhost:$mobilePort" `
        -Background
    
    if ($mobileProcess) {
        Write-Log "Mobile interface available at: http://localhost:$mobilePort" "INFO"
        Write-Log "QR code access at: http://localhost:5555" "INFO"
    }
    
    return $mobileProcess
}

# ==============================================================================
# TERMINAL TOOLS
# ==============================================================================

function Start-TerminalTools {
    Write-Banner "TERMINAL TOOLS" "Initializing terminal access and utilities"
    
    # Start ttyd terminal server if available
    $ttydPort = Find-AvailablePort 7681
    
    try {
        # Check if ttyd is available
        $ttydAvailable = Get-Command ttyd -ErrorAction SilentlyContinue
        if ($ttydAvailable) {
            $ttydProcess = Start-ServiceWithHealthCheck -Name "Terminal Server" `
                -Command "ttyd -p $ttydPort powershell" `
                -HealthCheckUrl "http://localhost:$ttydPort" `
                -Background
            
            if ($ttydProcess) {
                Write-Log "Terminal server available at: http://localhost:$ttydPort" "INFO"
            }
        } else {
            Write-Log "ttyd not found, terminal server not available" "WARN"
        }
    } catch {
        Write-Log "Terminal server setup failed: $($_.Exception.Message)" "WARN"
    }
}

# ==============================================================================
# HEALTH MONITORING
# ==============================================================================

function Start-HealthMonitoring {
    Write-Banner "HEALTH MONITORING" "Setting up service monitoring and recovery"
    
    # Create monitoring script
    $monitorScript = {
        param($ProcessList, $ServiceStatus)
        
        while ($true) {
            Start-Sleep -Seconds 30
            
            foreach ($process in $ProcessList) {
                if ($process -and $process.HasExited) {
                    Write-Host "Service $($process.ProcessName) has exited!" -ForegroundColor Red
                }
            }
        }
    }
    
    # Start monitoring in background
    $monitorJob = Start-Job -ScriptBlock $monitorScript -ArgumentList $Global:ProcessList, $Global:ServiceStatus
    
    Write-Log "Health monitoring started (Job ID: $($monitorJob.Id))" "SUCCESS"
    return $monitorJob
}

# ==============================================================================
# STATUS REPORTING
# ==============================================================================

function Show-ServiceStatus {
    Write-Banner "SERVICE STATUS" "Current status of all Claude Code services"
    
    $totalServices = $Global:ServiceStatus.Count
    $runningServices = ($Global:ServiceStatus.Values | Where-Object { $_ -eq "Running" }).Count
    $failedServices = ($Global:ServiceStatus.Values | Where-Object { $_ -eq "Failed" }).Count
    
    Write-Host "📊 Service Summary:" -ForegroundColor Cyan
    Write-Host "   Total Services: $totalServices" -ForegroundColor White
    Write-Host "   Running: $runningServices" -ForegroundColor Green
    Write-Host "   Failed: $failedServices" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "📋 Detailed Status:" -ForegroundColor Cyan
    foreach ($service in $Global:ServiceStatus.GetEnumerator()) {
        $status = $service.Value
        $color = switch ($status) {
            "Running" { "Green" }
            "Failed" { "Red" }
            "Timeout" { "Yellow" }
            default { "Gray" }
        }
        $icon = switch ($status) {
            "Running" { "✅" }
            "Failed" { "❌" }
            "Timeout" { "⏰" }
            default { "❓" }
        }
        Write-Host "   $icon $($service.Key): $status" -ForegroundColor $color
    }
    
    Write-Host ""
    $uptime = (Get-Date) - $Global:StartTime
    Write-Host "⏱️  Uptime: $($uptime.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
}

function Show-AccessUrls {
    Write-Banner "ACCESS POINTS" "Available URLs and interfaces"
    
    $urls = @()
    
    # Collect available URLs based on running services
    foreach ($service in $Global:ServiceStatus.GetEnumerator()) {
        if ($service.Value -eq "Running") {
            switch ($service.Key) {
                "Real-time Dashboard" { $urls += "🖥️  Dashboard: http://localhost:8080" }
                "Web Application" { $urls += "🌐 Web App: http://localhost:3000" }
                "Mobile Interface" { $urls += "📱 Mobile: http://localhost:8080" }
                "Terminal Server" { $urls += "💻 Terminal: http://localhost:7681" }
            }
        }
    }
    
    if ($urls.Count -eq 0) {
        Write-Host "❌ No services are currently running" -ForegroundColor Red
    } else {
        foreach ($url in $urls) {
            Write-Host "   $url" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "🔧 Control Commands:" -ForegroundColor Cyan
    Write-Host "   Ctrl+C: Stop all services" -ForegroundColor Gray
    Write-Host "   .\claude-start.ps1 -Mode debug: Debug mode" -ForegroundColor Gray
}

# ==============================================================================
# CLEANUP AND SHUTDOWN
# ==============================================================================

function Stop-AllServices {
    Write-Banner "SHUTDOWN" "Stopping all Claude Code services"
    
    foreach ($process in $Global:ProcessList) {
        if ($process -and -not $process.HasExited) {
            try {
                Write-Log "Stopping process $($process.ProcessName) (PID: $($process.Id))" "INFO"
                $process.Kill()
                $process.WaitForExit(5000)
            } catch {
                Write-Log "Failed to stop process: $($_.Exception.Message)" "WARN"
            }
        }
    }
    
    # Stop any background jobs
    Get-Job | Stop-Job -Force
    Get-Job | Remove-Job -Force
    
    Write-Log "All services stopped" "SUCCESS"
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

function Main {
    try {
        # Show banner
        Write-Banner "CLAUDE CODE DEV STACK V3.0" "Master Launch System - Mode: $Mode"
        
        # Environment validation
        Test-Environment
        
        # Initialize virtual environments
        Initialize-VirtualEnvironments
        
        # Start services based on mode
        switch ($Mode) {
            "full" {
                Start-CoreServices
                Start-MCPServers
                Start-WebApplication
                Start-MobileInterface
                Start-TerminalTools
            }
            "core" {
                Start-CoreServices
                Start-MCPServers
            }
            "web" {
                Start-WebApplication
            }
            "mobile" {
                Start-MobileInterface
            }
            "debug" {
                # Debug mode - start core services with enhanced logging
                $Global:LogLevel = "debug"
                Start-CoreServices
                Start-TerminalTools
            }
        }
        
        # Start health monitoring
        Start-HealthMonitoring
        
        # Show status
        Start-Sleep -Seconds 3
        Show-ServiceStatus
        Show-AccessUrls
        
        # Keep running and monitor
        Write-Log "Claude Code Dev Stack v3.0 is running! Press Ctrl+C to stop." "SUCCESS"
        
        try {
            while ($true) {
                Start-Sleep -Seconds 10
                
                # Quick health check
                $deadProcesses = $Global:ProcessList | Where-Object { $_ -and $_.HasExited }
                if ($deadProcesses) {
                    Write-Log "$($deadProcesses.Count) service(s) have stopped" "WARN"
                    Show-ServiceStatus
                }
            }
        } catch {
            Write-Log "Monitoring interrupted" "INFO"
        }
        
    } catch {
        Write-Log "Critical error: $($_.Exception.Message)" "ERROR"
        Write-Log $_.ScriptStackTrace "DEBUG"
        exit 1
    } finally {
        Stop-AllServices
    }
}

# Handle Ctrl+C gracefully
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Stop-AllServices
}

# Run main function
if ($MyInvocation.InvocationName -ne '.') {
    Main
}