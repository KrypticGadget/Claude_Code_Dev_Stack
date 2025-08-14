# Claude Code V3+ Mobile Access Remote Launcher
# One-liner mobile access that downloads and runs from GitHub
# Usage: iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mobile/launch-mobile-remote.ps1" -UseBasicParsing | iex

param(
    [switch]$NoPhone,
    [switch]$NoQR,
    [int]$Port = 8080,
    [switch]$Debug
)

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorText {
    param($Text, $Color = $Reset)
    Write-Host "$Color$Text$Reset"
}

function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Python found: $pythonVersion" $Green
            return $true
        }
    }
    catch {}
    
    Write-ColorText "❌ Python not found. Please install Python 3.7+ from python.org" $Red
    return $false
}

function Install-PythonPackages {
    Write-ColorText "📦 Installing required Python packages..." $Blue
    
    $packages = @("flask", "flask-socketio", "qrcode[pil]", "requests", "psutil")
    
    foreach ($package in $packages) {
        Write-ColorText "Installing $package..." $Yellow
        try {
            python -m pip install $package --quiet --upgrade
            if ($LASTEXITCODE -ne 0) {
                Write-ColorText "⚠️  Warning: Failed to install $package" $Yellow
            }
        }
        catch {
            Write-ColorText "⚠️  Warning: Error installing $package" $Yellow
        }
    }
    
    Write-ColorText "✅ Package installation complete" $Green
}

function Test-V3Installation {
    $claudeDir = "$env:USERPROFILE\.claude"
    
    if (-not (Test-Path $claudeDir)) {
        Write-ColorText "❌ Claude Code V3+ not installed" $Red
        Write-ColorText "Please run the installer first:" $Yellow
        Write-ColorText 'iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1" -UseBasicParsing | iex' $Blue
        return $false
    }
    
    # Check for key components
    $agentsDir = "$claudeDir\agents"
    $hooksDir = "$claudeDir\hooks"
    $audioDir = "$claudeDir\audio"
    
    if (-not (Test-Path $agentsDir) -or -not (Test-Path $hooksDir) -or -not (Test-Path $audioDir)) {
        Write-ColorText "❌ Incomplete V3+ installation detected" $Red
        Write-ColorText "Please run the full installer:" $Yellow
        Write-ColorText 'iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-all.ps1" -UseBasicParsing | iex' $Blue
        return $false
    }
    
    Write-ColorText "✅ Claude Code V3+ installation verified" $Green
    return $true
}

function Download-MobileComponents {
    $claudeDir = "$env:USERPROFILE\.claude"
    $mobileDir = "$claudeDir\mobile"
    $dashboardDir = "$claudeDir\dashboard"
    $tunnelsDir = "$claudeDir\tunnels"
    
    # Create directories
    @($mobileDir, $dashboardDir, $tunnelsDir) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }
    
    Write-ColorText "📥 Downloading mobile components from GitHub..." $Blue
    
    $baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"
    
    # Mobile components
    $mobileFiles = @(
        "mobile/launch_mobile.py",
        "mobile/mobile_auth.py", 
        "mobile/qr_generator.py",
        "mobile/README.md"
    )
    
    # Dashboard components
    $dashboardFiles = @(
        "dashboard/dashboard_server.py",
        "dashboard/requirements.txt",
        "dashboard/templates/dashboard.html"
    )
    
    # Tunnel components  
    $tunnelFiles = @(
        "tunnels/tunnel_manager.py",
        "tunnels/setup_ngrok.py",
        "tunnels/setup_cloudflare.py"
    )
    
    $allFiles = $mobileFiles + $dashboardFiles + $tunnelFiles
    $downloadedCount = 0
    
    foreach ($file in $allFiles) {
        $url = "$baseUrl/$file"
        $localPath = "$claudeDir\$($file.Replace('/', '\'))"
        $localDir = Split-Path $localPath -Parent
        
        # Ensure directory exists
        if (-not (Test-Path $localDir)) {
            New-Item -ItemType Directory -Path $localDir -Force | Out-Null
        }
        
        try {
            Write-ColorText "  Downloading $file..." $Yellow
            Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing
            $downloadedCount++
        }
        catch {
            Write-ColorText "⚠️  Warning: Failed to download $file" $Yellow
        }
    }
    
    # Download dashboard template directory
    $templateDir = "$dashboardDir\templates"
    if (-not (Test-Path $templateDir)) {
        New-Item -ItemType Directory -Path $templateDir -Force | Out-Null
    }
    
    Write-ColorText "✅ Downloaded $downloadedCount mobile components" $Green
    return $mobileDir
}

function Start-MobileAccess {
    param($MobileDir)
    
    $launchScript = "$MobileDir\launch_mobile.py"
    
    if (-not (Test-Path $launchScript)) {
        Write-ColorText "❌ Mobile launcher not found at $launchScript" $Red
        return $false
    }
    
    Write-ColorText "🚀 Starting Claude Code V3+ Mobile Access..." $Green
    Write-ColorText "=" * 60 $Blue
    
    # Build arguments
    $args = @()
    if ($NoPhone) { $args += "--no-phone" }
    if ($NoQR) { $args += "--no-qr" }
    if ($Port -ne 8080) { $args += "--port", $Port }
    
    # Set working directory to mobile directory
    Push-Location $MobileDir
    
    try {
        # Start mobile access
        python launch_mobile.py @args
    }
    catch {
        Write-ColorText "❌ Error starting mobile access: $_" $Red
        return $false
    }
    finally {
        Pop-Location
    }
    
    return $true
}

function Show-Header {
    Write-ColorText @"
🚀 Claude Code V3+ Mobile Access Remote Launcher
=================================================
📱 Secure one-liner mobile access to your V3+ system
🌐 Downloads components from GitHub automatically  
🔒 Enterprise-grade security with token authentication
📊 Real-time monitoring dashboard for Samsung Galaxy S25 Edge
"@ $Blue
    Write-Host ""
}

function Show-Usage {
    Write-ColorText @"
Usage Examples:

Basic Launch:
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mobile/launch-mobile-remote.ps1" -UseBasicParsing | iex

Advanced Options:
```powershell
# Download script first for options
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mobile/launch-mobile-remote.ps1" -OutFile "launch-mobile.ps1"

# Run with options
.\launch-mobile.ps1 -NoPhone -Port 9090
```

Parameters:
  -NoPhone    : Don't send notifications to phone
  -NoQR       : Don't generate QR code  
  -Port <num> : Custom dashboard port (default: 8080)
  -Debug      : Enable debug mode
"@ $Yellow
}

# Main execution
try {
    Show-Header
    
    # Check prerequisites
    if (-not (Test-PythonInstallation)) {
        exit 1
    }
    
    # Check V3+ installation
    if (-not (Test-V3Installation)) {
        exit 1
    }
    
    # Install Python packages
    Install-PythonPackages
    
    # Download mobile components
    $mobileDir = Download-MobileComponents
    
    if (-not $mobileDir) {
        Write-ColorText "❌ Failed to download mobile components" $Red
        exit 1
    }
    
    # Start mobile access
    if (-not (Start-MobileAccess $mobileDir)) {
        Write-ColorText "❌ Failed to start mobile access" $Red
        exit 1
    }
    
}
catch {
    Write-ColorText "❌ Unexpected error: $_" $Red
    Write-ColorText "Please try running the command again or check your internet connection." $Yellow
    exit 1
}

# If we get here, everything worked
Write-ColorText "✅ Mobile access launcher completed successfully!" $Green