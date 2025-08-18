# MCP Manager Startup Script for Windows
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

[CmdletBinding()]
param(
    [string]$ConfigPath = "",
    [int]$ApiPort = 8000,
    [switch]$Development,
    [switch]$Background,
    [switch]$InstallDependencies,
    [switch]$SetupEnvironment,
    [string]$PythonPath = "python",
    [string]$LogLevel = "INFO"
)

# Script configuration
$ScriptDir = Split-Path -Parent $PSScriptRoot
$IntegrationRoot = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent $IntegrationRoot
$RequirementsFile = Join-Path $IntegrationRoot "requirements.txt"
$VenvPath = Join-Path $IntegrationRoot "venv"
$ApiScript = Join-Path $IntegrationRoot "api\mcp_integration.py"
$ConfigFile = if ($ConfigPath) { $ConfigPath } else { Join-Path $IntegrationRoot "config\mcp-services.yml" }

Write-Host "MCP Manager Startup Script" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Integration Root: $IntegrationRoot" -ForegroundColor Gray
Write-Host "Config File: $ConfigFile" -ForegroundColor Gray
Write-Host "API Port: $ApiPort" -ForegroundColor Gray
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Python dependencies
function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    
    # Check if virtual environment exists
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        & $PythonPath -m venv $VenvPath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            return $false
        }
    }
    
    # Activate virtual environment
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        & $ActivateScript
    } else {
        Write-Warning "Virtual environment activation script not found"
    }
    
    # Update pip
    Write-Host "Updating pip..." -ForegroundColor Yellow
    & $PythonPath -m pip install --upgrade pip
    
    # Install requirements
    if (Test-Path $RequirementsFile) {
        Write-Host "Installing requirements from $RequirementsFile..." -ForegroundColor Yellow
        & $PythonPath -m pip install -r $RequirementsFile
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install requirements"
            return $false
        }
    } else {
        # Install core dependencies
        Write-Host "Installing core dependencies..." -ForegroundColor Yellow
        $CoreDependencies = @(
            "fastapi[all]",
            "uvicorn[standard]",
            "httpx",
            "pydantic",
            "pyyaml",
            "beautifulsoup4",
            "requests",
            "psutil",
            "asyncio",
            "pathlib",
            "playwright",
            "PyGithub"
        )
        
        foreach ($dep in $CoreDependencies) {
            Write-Host "Installing $dep..." -ForegroundColor Gray
            & $PythonPath -m pip install $dep
        }
    }
    
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
    return $true
}

# Function to setup environment
function Setup-Environment {
    Write-Host "Setting up environment..." -ForegroundColor Yellow
    
    # Create required directories
    $RequiredDirs = @(
        (Join-Path $IntegrationRoot "logs"),
        (Join-Path $IntegrationRoot "data"),
        (Join-Path $IntegrationRoot "temp"),
        (Join-Path $IntegrationRoot "backups")
    )
    
    foreach ($dir in $RequiredDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir" -ForegroundColor Gray
        }
    }
    
    # Setup Playwright
    Write-Host "Setting up Playwright browsers..." -ForegroundColor Yellow
    & $PythonPath -m playwright install
    
    # Create environment file if it doesn't exist
    $EnvFile = Join-Path $IntegrationRoot ".env"
    if (-not (Test-Path $EnvFile)) {
        $EnvContent = @"
# MCP Manager Environment Configuration
GITHUB_TOKEN=your_github_token_here
MCP_LOG_LEVEL=$LogLevel
MCP_API_PORT=$ApiPort
MCP_CONFIG_PATH=$ConfigFile
"@
        $EnvContent | Out-File -FilePath $EnvFile -Encoding UTF8
        Write-Host "Created environment file: $EnvFile" -ForegroundColor Gray
        Write-Warning "Please update the .env file with your GitHub token and other settings"
    }
    
    Write-Host "Environment setup completed" -ForegroundColor Green
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $PythonVersion = & $PythonPath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python found: $PythonVersion" -ForegroundColor Green
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python is required but not found. Please install Python 3.8+ and ensure it's in PATH."
        return $false
    }
    
    # Check if config file exists
    if (-not (Test-Path $ConfigFile)) {
        Write-Warning "Configuration file not found: $ConfigFile"
        Write-Host "Using default configuration..." -ForegroundColor Yellow
    }
    
    # Check if API script exists
    if (-not (Test-Path $ApiScript)) {
        Write-Error "API script not found: $ApiScript"
        return $false
    }
    
    Write-Host "Prerequisites check completed" -ForegroundColor Green
    return $true
}

# Function to start MCP Manager
function Start-MCPManagerService {
    Write-Host "Starting MCP Manager..." -ForegroundColor Yellow
    
    # Set environment variables
    $env:PYTHONPATH = $IntegrationRoot
    
    # Build command arguments
    $Arguments = @(
        $ApiScript,
        "--host", "0.0.0.0",
        "--port", $ApiPort.ToString(),
        "--log-level", $LogLevel.ToLower()
    )
    
    if ($Development) {
        $Arguments += "--reload"
    }
    
    try {
        if ($Background) {
            # Start in background
            Write-Host "Starting MCP Manager in background mode..." -ForegroundColor Green
            $Process = Start-Process -FilePath $PythonPath -ArgumentList $Arguments -WindowStyle Hidden -PassThru
            
            # Wait a moment and check if process is still running
            Start-Sleep -Seconds 3
            if ($Process.HasExited) {
                Write-Error "MCP Manager failed to start"
                return $false
            }
            
            Write-Host "MCP Manager started successfully (PID: $($Process.Id))" -ForegroundColor Green
            Write-Host "API available at: http://localhost:$ApiPort" -ForegroundColor Cyan
            Write-Host "Health check: http://localhost:$ApiPort/health" -ForegroundColor Cyan
            Write-Host "API docs: http://localhost:$ApiPort/docs" -ForegroundColor Cyan
            
            # Save process ID for later reference
            $PidFile = Join-Path $IntegrationRoot "data\mcp-manager.pid"
            $Process.Id | Out-File -FilePath $PidFile -Encoding UTF8
            
            return $true
        } else {
            # Start in foreground
            Write-Host "Starting MCP Manager in foreground mode..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "API will be available at: http://localhost:$ApiPort" -ForegroundColor Cyan
            Write-Host "Health check: http://localhost:$ApiPort/health" -ForegroundColor Cyan
            Write-Host "API docs: http://localhost:$ApiPort/docs" -ForegroundColor Cyan
            Write-Host ""
            
            & $PythonPath @Arguments
            return $LASTEXITCODE -eq 0
        }
    } catch {
        Write-Error "Failed to start MCP Manager: $($_.Exception.Message)"
        return $false
    }
}

# Function to check if MCP Manager is running
function Test-MCPManagerRunning {
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:$ApiPort/health" -TimeoutSec 5 -ErrorAction Stop
        return $Response.status -eq "healthy"
    } catch {
        return $false
    }
}

# Function to display banner
function Show-Banner {
    Write-Host ""
    Write-Host "  __  __  ____  ____    __  __" -ForegroundColor Cyan
    Write-Host " |  \/  |/ ___|/ ___|  |  \/  | __ _ _ __   __ _  __ _  ___ _ __" -ForegroundColor Cyan
    Write-Host " | |\/| | |   | |      | |\/| |/ _' | '_ \ / _' |/ _' |/ _ \ '__|" -ForegroundColor Cyan
    Write-Host " | |  | | |___| |___   | |  | | (_| | | | | (_| | (_| |  __/ |" -ForegroundColor Cyan
    Write-Host " |_|  |_|\____|\____|  |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|" -ForegroundColor Cyan
    Write-Host "                                                |___/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Model Context Protocol Manager - DevOps Agent Enhanced" -ForegroundColor White
    Write-Host "Original concept by @qdhenry (MIT License)" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
try {
    Show-Banner
    
    # Handle special flags
    if ($InstallDependencies) {
        if (-not (Install-Dependencies)) {
            exit 1
        }
    }
    
    if ($SetupEnvironment) {
        Setup-Environment
    }
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Host ""
        Write-Host "Prerequisites check failed. Please resolve the issues above." -ForegroundColor Red
        exit 1
    }
    
    # Check if already running
    if (Test-MCPManagerRunning) {
        Write-Host "MCP Manager is already running on port $ApiPort" -ForegroundColor Yellow
        Write-Host "API available at: http://localhost:$ApiPort" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To stop the service, use: Stop-MCPManager.ps1" -ForegroundColor Gray
        exit 0
    }
    
    # Start the service
    $Success = Start-MCPManagerService
    
    if ($Success) {
        Write-Host ""
        Write-Host "MCP Manager started successfully!" -ForegroundColor Green
        
        if ($Background) {
            Write-Host ""
            Write-Host "Service is running in the background." -ForegroundColor Yellow
            Write-Host "To stop the service, use: Stop-MCPManager.ps1" -ForegroundColor Gray
            Write-Host "To view logs, check: $IntegrationRoot\logs\mcp-manager.log" -ForegroundColor Gray
        }
    } else {
        Write-Host ""
        Write-Host "Failed to start MCP Manager" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Error "An error occurred: $($_.Exception.Message)"
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}

# Wait for user input if running interactively and not in background
if (-not $Background -and [Environment]::UserInteractive) {
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}