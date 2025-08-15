#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code Mobile Launcher - PowerShell Script V3.0
    
.DESCRIPTION
    Bulletproof launcher that handles virtual environment setup, dependency installation,
    and starts all Claude Code mobile services in the correct order.
    
.PARAMETER NoPhone
    Don't send access info to phone
    
.PARAMETER NoQr  
    Don't generate QR code
    
.PARAMETER Port
    Dashboard port (default: 8080)
    
.EXAMPLE
    .\launch_mobile.ps1
    
.EXAMPLE
    .\launch_mobile.ps1 -NoPhone -Port 9090
    
.NOTES
    Author: DevOps Engineering Agent V3.0
    Version: 3.0
    Requires: Python 3.8+, PowerShell 5.1+
#>

[CmdletBinding()]
param(
    [switch]$NoPhone,
    [switch]$NoQr,
    [int]$Port = 8080
)

# Set error handling
$ErrorActionPreference = "Stop"

# Enable UTF-8 encoding for better Unicode support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🚀 Claude Code Mobile Launcher - V3.0 Enhanced" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"
$LauncherScript = Join-Path $ScriptDir "launch_mobile.py"

Write-Host "📂 Working Directory: $ScriptDir" -ForegroundColor White
Write-Host "🐍 Virtual Environment: $VenvDir" -ForegroundColor White

# Function to safely execute commands with error handling
function Invoke-SafeCommand {
    param(
        [string]$Command,
        [array]$Arguments,
        [string]$Description,
        [switch]$ContinueOnError
    )
    
    try {
        Write-Host "🔄 $Description..." -ForegroundColor Yellow
        $result = & $Command @Arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed successfully" -ForegroundColor Green
            return $true
        } else {
            throw "Command failed with exit code: $LASTEXITCODE"
        }
    } catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        if (-not $ContinueOnError) {
            throw
        }
        return $false
    }
}

# Function to check if Python is available
function Test-PythonAvailable {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        # Python not found
    }
    
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and ensure it's in your PATH" -ForegroundColor Yellow
    return $false
}

# Function to create virtual environment
function New-VirtualEnvironment {
    param([string]$VenvPath)
    
    if (Test-Path $VenvPath) {
        Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
        return $true
    }
    
    try {
        Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
        python -m venv $VenvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
            return $true
        } else {
            throw "Failed to create virtual environment (exit code: $LASTEXITCODE)"
        }
    } catch {
        Write-Host "❌ Failed to create virtual environment: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to install dependencies
function Install-Dependencies {
    param([string]$VenvPythonPath, [string]$RequirementsPath)
    
    # Upgrade pip first
    Invoke-SafeCommand -Command $VenvPythonPath -Arguments @("-m", "pip", "install", "--upgrade", "pip") -Description "Upgrading pip" -ContinueOnError
    
    if (Test-Path $RequirementsPath) {
        Write-Host "📋 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
        Write-Host "   This may take a few minutes..." -ForegroundColor Gray
        
        try {
            & $VenvPythonPath -m pip install -r $RequirementsPath --upgrade
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠️ Some packages may have failed to install, trying individual installation..." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️ Error installing from requirements.txt: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    # Fallback: Install essential packages individually
    Write-Host "📦 Installing essential packages individually..." -ForegroundColor Yellow
    
    $essentialPackages = @(
        "flask>=2.3.0",
        "flask-socketio>=5.3.0", 
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "qrcode[pil]>=7.4.0",
        "watchdog>=3.0.0",
        "GitPython>=3.1.0"
    )
    
    foreach ($package in $essentialPackages) {
        try {
            Write-Host "   Installing $package..." -ForegroundColor Gray
            & $VenvPythonPath -m pip install $package --upgrade
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Installed $package" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Warning: Failed to install $package" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠️ Error installing $package : $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    return $true
}

try {
    # Step 1: Check if Python is available
    if (-not (Test-PythonAvailable)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Step 2: Create virtual environment
    if (-not (New-VirtualEnvironment -VenvPath $VenvDir)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Step 3: Verify virtual environment Python exists
    if (-not (Test-Path $VenvPython)) {
        Write-Host "❌ Virtual environment Python not found at: $VenvPython" -ForegroundColor Red
        Write-Host "Recreating virtual environment..." -ForegroundColor Yellow
        
        if (Test-Path $VenvDir) {
            Remove-Item -Path $VenvDir -Recurse -Force
        }
        
        if (-not (New-VirtualEnvironment -VenvPath $VenvDir)) {
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    Write-Host "✅ Virtual environment Python found: $VenvPython" -ForegroundColor Green
    
    # Step 4: Install dependencies
    Install-Dependencies -VenvPythonPath $VenvPython -RequirementsPath $RequirementsFile
    
    # Step 5: Verify launcher script exists
    if (-not (Test-Path $LauncherScript)) {
        Write-Host "❌ Launcher script not found: $LauncherScript" -ForegroundColor Red
        Write-Host "Please ensure launch_mobile.py exists in the same directory as this script" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "✅ Launcher script found: $LauncherScript" -ForegroundColor Green
    
    # Step 6: Set environment variables for better compatibility
    $env:PYTHONUNBUFFERED = "1"
    $env:PYTHONIOENCODING = "utf-8"
    
    # Step 7: Launch the mobile access system
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host "🚀 Starting Claude Code Mobile Access System..." -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📱 The system will start:" -ForegroundColor White
    Write-Host "   • QR server on port 5555" -ForegroundColor Gray
    Write-Host "   • Dashboard on port $Port" -ForegroundColor Gray  
    Write-Host "   • Terminal (ttyd) on port 7681" -ForegroundColor Gray
    Write-Host "   • Secure tunnel via ngrok" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🛑 Press Ctrl+C to stop all services" -ForegroundColor Yellow
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Change to the script directory to ensure relative paths work
    Push-Location $ScriptDir
    
    try {
        # Build arguments for the Python launcher
        $launcherArgs = @()
        
        if ($NoPhone) {
            $launcherArgs += "--no-phone"
        }
        
        if ($NoQr) {
            $launcherArgs += "--no-qr"
        }
        
        if ($Port -ne 8080) {
            $launcherArgs += "--port", $Port
        }
        
        # Run the Python launcher with the virtual environment Python
        & $VenvPython $LauncherScript @launcherArgs
        
        # Handle the exit code
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Mobile launcher completed successfully" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Mobile launcher exited with error code: $LASTEXITCODE" -ForegroundColor Red
            Write-Host "Check the output above for error details" -ForegroundColor Yellow
        }
        
    } finally {
        Pop-Location
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
    exit 1
} finally {
    Write-Host ""
    Write-Host "🧹 Cleanup completed" -ForegroundColor Green
    Read-Host "Press Enter to exit"
}