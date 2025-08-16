#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Claude Code Dev Stack v3.0 - One-Line PowerShell Installer
    
.DESCRIPTION
    Cross-platform one-liner installer that clones from GitHub, installs dependencies, 
    sets up virtual environments, configures services, and validates installation.
    
    Usage: irm https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.ps1 | iex
    
.NOTES
    - Supports Windows, Linux, and macOS via PowerShell Core
    - Automatically detects and installs required dependencies
    - Creates isolated virtual environments for Python and Node.js
    - Validates installation with comprehensive health checks
    - Provides detailed error reporting and recovery options
#>

param(
    [string]$InstallPath = "$HOME\Claude_Code_Dev_Stack_v3",
    [string]$GitHubRepo = "yourusername/Claude_Code_Dev_Stack_v3",
    [string]$Branch = "main",
    [switch]$SkipValidation = $false,
    [switch]$Verbose = $false
)

# Script metadata
$script:Version = "3.0.0"
$script:StartTime = Get-Date
$script:LogFile = "$env:TEMP\claude-stack-install-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$script:ErrorCount = 0
$script:WarningCount = 0

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$ForegroundColor = "White",
        [string]$Prefix = ""
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $fullMessage = "[$timestamp] $Prefix$Message"
    
    # Log to file
    Add-Content -Path $script:LogFile -Value $fullMessage
    
    # Console output with color
    if ($Host.UI.RawUI.ForegroundColor) {
        Write-Host $fullMessage -ForegroundColor $ForegroundColor
    } else {
        Write-Output $fullMessage
    }
}

function Write-Success { param([string]$Message) Write-ColorOutput $Message "Green" "✅ " }
function Write-Info { param([string]$Message) Write-ColorOutput $Message "Cyan" "ℹ️  " }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message "Yellow" "⚠️  "; $script:WarningCount++ }
function Write-Error { param([string]$Message) Write-ColorOutput $Message "Red" "❌ "; $script:ErrorCount++ }
function Write-Progress { param([string]$Message) Write-ColorOutput $Message "Magenta" "🔄 " }

# Error handling
trap {
    Write-Error "Unhandled error: $_"
    Write-Error "Installation failed. Check log: $script:LogFile"
    exit 1
}

function Test-AdminPrivileges {
    """Check if running with admin privileges on Windows"""
    if ($IsWindows) {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    return $true
}

function Test-Dependencies {
    """Check and install required dependencies"""
    Write-Progress "Checking system dependencies..."
    
    $dependencies = @{
        "git" = @{
            command = "git --version"
            install = @{
                Windows = "winget install Git.Git"
                Linux = "sudo apt-get update && sudo apt-get install -y git"
                macOS = "xcode-select --install"
            }
        }
        "python" = @{
            command = "python --version"
            install = @{
                Windows = "winget install Python.Python.3.11"
                Linux = "sudo apt-get install -y python3 python3-pip python3-venv"
                macOS = "brew install python@3.11"
            }
        }
        "node" = @{
            command = "node --version"
            install = @{
                Windows = "winget install OpenJS.NodeJS"
                Linux = "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
                macOS = "brew install node"
            }
        }
        "docker" = @{
            command = "docker --version"
            install = @{
                Windows = "winget install Docker.DockerDesktop"
                Linux = "curl -fsSL https://get.docker.com | sh"
                macOS = "brew install --cask docker"
            }
            optional = $true
        }
    }
    
    $platform = if ($IsWindows) { "Windows" } elseif ($IsLinux) { "Linux" } else { "macOS" }
    $missing = @()
    
    foreach ($dep in $dependencies.Keys) {
        try {
            $null = Invoke-Expression $dependencies[$dep].command 2>$null
            Write-Success "$dep is installed"
        } catch {
            if ($dependencies[$dep].optional) {
                Write-Warning "$dep is not installed (optional)"
            } else {
                Write-Error "$dep is not installed"
                $missing += @{
                    name = $dep
                    command = $dependencies[$dep].install[$platform]
                }
            }
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Info "Missing dependencies found. Install commands:"
        foreach ($dep in $missing) {
            Write-Info "  $($dep.name): $($dep.command)"
        }
        
        $response = Read-Host "Would you like to auto-install missing dependencies? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            foreach ($dep in $missing) {
                Write-Progress "Installing $($dep.name)..."
                try {
                    Invoke-Expression $dep.command
                    Write-Success "$($dep.name) installed successfully"
                } catch {
                    Write-Error "Failed to install $($dep.name): $_"
                    Write-Info "Please install manually: $($dep.command)"
                }
            }
        } else {
            Write-Error "Please install missing dependencies manually and re-run installer"
            exit 1
        }
    }
}

function Install-ClaudeStack {
    """Main installation function"""
    Write-Info "=== Claude Code Dev Stack v3.0 Installer ==="
    Write-Info "Install Path: $InstallPath"
    Write-Info "GitHub Repo: $GitHubRepo"
    Write-Info "Branch: $Branch"
    Write-Info "Log File: $script:LogFile"
    Write-Info ""
    
    # Step 1: Check dependencies
    Test-Dependencies
    
    # Step 2: Clone repository
    Write-Progress "Cloning repository from GitHub..."
    if (Test-Path $InstallPath) {
        Write-Warning "Installation directory already exists"
        $response = Read-Host "Remove existing directory? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item -Path $InstallPath -Recurse -Force
            Write-Info "Existing directory removed"
        } else {
            Write-Error "Installation cancelled"
            exit 1
        }
    }
    
    try {
        git clone --depth 1 --branch $Branch "https://github.com/$GitHubRepo.git" $InstallPath
        Write-Success "Repository cloned successfully"
    } catch {
        Write-Error "Failed to clone repository: $_"
        exit 1
    }
    
    # Step 3: Navigate to installation directory
    Set-Location $InstallPath
    
    # Step 4: Setup Python virtual environment
    Write-Progress "Setting up Python virtual environment..."
    try {
        python -m venv venv
        
        # Activate virtual environment
        $activateScript = if ($IsWindows) { ".\venv\Scripts\Activate.ps1" } else { "source ./venv/bin/activate" }
        
        if ($IsWindows) {
            & ".\venv\Scripts\Activate.ps1"
            $pythonExe = ".\venv\Scripts\python.exe"
            $pipExe = ".\venv\Scripts\pip.exe"
        } else {
            # For Unix-like systems, we need to source in the same shell
            $env:VIRTUAL_ENV = "$InstallPath/venv"
            $env:PATH = "$InstallPath/venv/bin:$env:PATH"
            $pythonExe = "./venv/bin/python"
            $pipExe = "./venv/bin/pip"
        }
        
        Write-Success "Python virtual environment created"
    } catch {
        Write-Error "Failed to create Python virtual environment: $_"
        exit 1
    }
    
    # Step 5: Install Python dependencies
    Write-Progress "Installing Python dependencies..."
    try {
        if (Test-Path "requirements.txt") {
            & $pipExe install --upgrade pip
            & $pipExe install -r requirements.txt
            Write-Success "Python dependencies installed"
        } else {
            Write-Warning "requirements.txt not found, running setup_environment.py"
            & $pythonExe setup_environment.py
        }
    } catch {
        Write-Error "Failed to install Python dependencies: $_"
        exit 1
    }
    
    # Step 6: Setup Node.js environment
    Write-Progress "Setting up Node.js environment..."
    if (Test-Path "apps/web/package.json") {
        Set-Location "apps/web"
        try {
            npm ci
            Write-Success "Node.js dependencies installed"
        } catch {
            Write-Warning "npm ci failed, trying npm install..."
            npm install
            Write-Success "Node.js dependencies installed (fallback)"
        }
        Set-Location "../.."
    }
    
    # Step 7: Configure services
    Write-Progress "Configuring services..."
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        @"
# Claude Code Dev Stack v3.0 Configuration
# Generated by installer on $(Get-Date)

# Core Settings
CLAUDE_API_KEY=your_api_key_here
NODE_ENV=development
PYTHON_ENV=development

# Service Ports
WEB_PORT=3000
API_PORT=8000
MOBILE_PORT=8080
DASHBOARD_PORT=8081
MCP_PORT=8085

# Database (if using)
DATABASE_URL=sqlite:///./claude_stack.db

# Audio & Voice
ENABLE_AUDIO=true
AUDIO_SAMPLE_RATE=44100

# Security
SESSION_SECRET=$(New-Guid)
JWT_SECRET=$(New-Guid)

# Debug
DEBUG=false
VERBOSE_LOGGING=false
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Environment configuration created"
    }
    
    # Step 8: Build web application
    if (Test-Path "apps/web") {
        Write-Progress "Building web application..."
        Set-Location "apps/web"
        try {
            npm run build
            Write-Success "Web application built successfully"
        } catch {
            Write-Warning "Build failed, continuing with development setup"
        }
        Set-Location "../.."
    }
    
    # Step 9: Initialize database and services
    Write-Progress "Initializing services..."
    try {
        & $pythonExe -c "
import sys
sys.path.append('.')
from pathlib import Path

# Create necessary directories
dirs = [
    '.claude',
    '.claude/agents',
    '.claude/hooks', 
    '.claude/status',
    '.claude/logs',
    '.claude/temp',
    'data',
    'logs'
]

for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f'Created directory: {dir_path}')

print('Service directories initialized')
"
        Write-Success "Services initialized"
    } catch {
        Write-Warning "Service initialization had issues, but continuing..."
    }
    
    # Step 10: Validation (if not skipped)
    if (-not $SkipValidation) {
        Write-Progress "Validating installation..."
        Invoke-ValidationTests
    }
    
    # Step 11: Create launcher scripts
    Write-Progress "Creating launcher scripts..."
    Create-LauncherScripts
    
    # Step 12: Installation summary
    Show-InstallationSummary
}

function Invoke-ValidationTests {
    """Comprehensive installation validation"""
    Write-Info "Running validation tests..."
    
    $tests = @(
        @{
            name = "Python Environment"
            test = { Test-Path "venv" }
        },
        @{
            name = "Python Dependencies"
            test = { 
                try { 
                    $result = & ".\venv\Scripts\python.exe" -c "import flask, requests, yaml; print('OK')" 2>$null
                    return $result -eq "OK"
                } catch { return $false }
            }
        },
        @{
            name = "Node.js Dependencies"
            test = { Test-Path "apps/web/node_modules" }
        },
        @{
            name = "Configuration Files"
            test = { (Test-Path ".env") -and (Test-Path "requirements.txt") }
        },
        @{
            name = "Service Directories"
            test = { (Test-Path ".claude") -and (Test-Path "logs") }
        }
    )
    
    $passed = 0
    $total = $tests.Count
    
    foreach ($test in $tests) {
        try {
            if (& $test.test) {
                Write-Success "$($test.name): PASS"
                $passed++
            } else {
                Write-Error "$($test.name): FAIL"
            }
        } catch {
            Write-Error "$($test.name): ERROR - $_"
        }
    }
    
    Write-Info "Validation Results: $passed/$total tests passed"
    
    if ($passed -eq $total) {
        Write-Success "All validation tests passed!"
    } elseif ($passed -ge ($total * 0.8)) {
        Write-Warning "Most tests passed, installation should work with minor issues"
    } else {
        Write-Error "Many tests failed, installation may have serious issues"
    }
}

function Create-LauncherScripts {
    """Create convenient launcher scripts"""
    
    # Windows launcher
    if ($IsWindows) {
        @"
@echo off
echo Starting Claude Code Dev Stack v3.0...
cd /d "%~dp0"

echo Activating Python environment...
call venv\Scripts\activate.bat

echo Starting services...
start "Web App" cmd /k "cd apps\web && npm run dev"
start "API Server" cmd /k "python core\api\server.py"
start "Dashboard" cmd /k "python .claude-example\dashboard\realtime_dashboard.py"

echo Services started! Check the opened windows.
echo Web App: http://localhost:3000
echo API: http://localhost:8000  
echo Dashboard: http://localhost:8081
pause
"@ | Out-File -FilePath "start.bat" -Encoding ASCII
        
        @"
Write-Host "Starting Claude Code Dev Stack v3.0..." -ForegroundColor Cyan
Set-Location $PSScriptRoot

Write-Host "Activating Python environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Starting services..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\apps\web'; npm run dev" -WindowStyle Normal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python core\api\server.py" -WindowStyle Normal  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python .claude-example\dashboard\realtime_dashboard.py" -WindowStyle Normal

Write-Host ""
Write-Host "Services started! URLs:" -ForegroundColor Green
Write-Host "  Web App: http://localhost:3000" -ForegroundColor White
Write-Host "  API: http://localhost:8000" -ForegroundColor White
Write-Host "  Dashboard: http://localhost:8081" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
"@ | Out-File -FilePath "start.ps1" -Encoding UTF8
    }
    
    # Unix launcher
    @"
#!/bin/bash
echo "Starting Claude Code Dev Stack v3.0..."
cd "$(dirname "$0")"

echo "Activating Python environment..."
source venv/bin/activate

echo "Starting services..."
# Start web app in background
cd apps/web && npm run dev &
WEB_PID=$!

# Start API server in background  
cd ../.. && python core/api/server.py &
API_PID=$!

# Start dashboard in background
python .claude-example/dashboard/realtime_dashboard.py &
DASHBOARD_PID=$!

echo ""
echo "Services started! URLs:"
echo "  Web App: http://localhost:3000"
echo "  API: http://localhost:8000"
echo "  Dashboard: http://localhost:8081"
echo ""
echo "PIDs: Web=$WEB_PID, API=$API_PID, Dashboard=$DASHBOARD_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait and cleanup
trap "kill $WEB_PID $API_PID $DASHBOARD_PID 2>/dev/null; exit" INT TERM
wait
"@ | Out-File -FilePath "start.sh" -Encoding UTF8
    
    if (-not $IsWindows) {
        chmod +x start.sh
    }
    
    Write-Success "Launcher scripts created"
}

function Show-InstallationSummary {
    """Display installation summary and next steps"""
    $duration = (Get-Date) - $script:StartTime
    
    Write-Info ""
    Write-Info "============================================="
    Write-Success "Claude Code Dev Stack v3.0 Installed!"
    Write-Info "============================================="
    Write-Info ""
    Write-Info "Installation Details:"
    Write-Info "  Location: $InstallPath"
    Write-Info "  Duration: $($duration.ToString('mm\:ss'))"
    Write-Info "  Warnings: $script:WarningCount"
    Write-Info "  Errors: $script:ErrorCount"
    Write-Info "  Log File: $script:LogFile"
    Write-Info ""
    Write-Info "Quick Start Commands:"
    Write-Info "  Windows: start.bat or start.ps1"
    Write-Info "  Linux/Mac: ./start.sh"
    Write-Info ""
    Write-Info "Service URLs:"
    Write-Info "  📱 Mobile: http://localhost:8080"
    Write-Info "  🌐 Web App: http://localhost:3000"
    Write-Info "  📊 Dashboard: http://localhost:8081"
    Write-Info "  🔌 API: http://localhost:8000"
    Write-Info ""
    Write-Info "Configuration:"
    Write-Info "  Edit .env file for API keys and settings"
    Write-Info "  Python env: venv/ (auto-activated)"
    Write-Info "  Node.js deps: apps/web/node_modules/"
    Write-Info ""
    Write-Info "Manual activation:"
    if ($IsWindows) {
        Write-Info "  PowerShell: .\venv\Scripts\Activate.ps1"
        Write-Info "  CMD: venv\Scripts\activate.bat"
    } else {
        Write-Info "  Bash/Zsh: source venv/bin/activate"
    }
    Write-Info ""
    
    if ($script:ErrorCount -eq 0) {
        Write-Success "Installation completed successfully! 🎉"
    } elseif ($script:ErrorCount -le 2) {
        Write-Warning "Installation completed with minor issues. Check log file."
    } else {
        Write-Error "Installation completed with issues. Review errors in log file."
    }
    
    Write-Info ""
    Write-Info "Next Steps:"
    Write-Info "1. Add your CLAUDE_API_KEY to .env file"
    Write-Info "2. Run launcher script to start services" 
    Write-Info "3. Visit http://localhost:3000 to begin"
    Write-Info "4. Check documentation in docs/ folder"
    Write-Info ""
    Write-Info "Support: Check GitHub issues or README.md"
    Write-Info "============================================="
}

# Main execution
try {
    Install-ClaudeStack
} catch {
    Write-Error "Installation failed: $_"
    Write-Error "Check log file: $script:LogFile"
    exit 1
}