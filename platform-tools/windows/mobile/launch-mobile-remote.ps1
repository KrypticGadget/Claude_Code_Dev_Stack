# Claude Code V3+ Mobile Access Remote Launcher
# WORKING VERSION - Always prompts for token

# Color functions
function Write-ColorText {
    param([string]$Text, [ConsoleColor]$Color = "White")
    Write-Host $Text -ForegroundColor $Color -NoNewline
    Write-Host ""
}

$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"
$Gray = "Gray"

Write-ColorText @"
🚀 Claude Code V3+ Mobile Access Remote Launcher
=================================================
📱 Secure one-liner mobile access to your V3+ system
🌐 Downloads components from GitHub automatically
🔒 Enterprise-grade security with token authentication
📊 Real-time monitoring dashboard for Samsung Galaxy S25 Edge
"@ $Blue

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-ColorText "✅ Python found: $pythonVersion" $Green
} catch {
    Write-ColorText "❌ Python not found. Please install Python 3.8+" $Red
    exit 1
}

# Check Claude installation
$claudeDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $claudeDir)) {
    Write-ColorText "❌ Claude Code not installed" $Red
    Write-ColorText "Please run the installer first" $Yellow
    exit 1
}

Write-ColorText "✅ Claude Code V3+ installation verified" $Green

# Setup Python Virtual Environment
Write-ColorText "`n🔧 Setting up Python virtual environment..." $Blue

$mobileDir = "$claudeDir\mobile"
$venvDir = "$mobileDir\.venv"

# Create mobile directory if it doesn't exist
if (-not (Test-Path $mobileDir)) {
    New-Item -ItemType Directory -Path $mobileDir -Force | Out-Null
}

# Check if virtual environment exists
if (Test-Path $venvDir) {
    Write-ColorText "✅ Virtual environment already exists" $Green
} else {
    Write-ColorText "Creating virtual environment..." $Yellow
    try {
        & python -m venv $venvDir
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Virtual environment created successfully" $Green
        } else {
            Write-ColorText "❌ Failed to create virtual environment" $Red
            exit 1
        }
    } catch {
        Write-ColorText "❌ Error creating virtual environment: $_" $Red
        exit 1
    }
}

# Setup venv paths
$venvPython = "$venvDir\Scripts\python.exe"
$venvPip = "$venvDir\Scripts\pip.exe"

# Verify venv python exists
if (-not (Test-Path $venvPython)) {
    Write-ColorText "❌ Virtual environment Python not found at $venvPython" $Red
    exit 1
}

# Upgrade pip in virtual environment
Write-ColorText "Upgrading pip in virtual environment..." $Yellow
try {
    & $venvPython -m pip install --upgrade pip --quiet
    Write-ColorText "✅ Pip upgraded successfully" $Green
} catch {
    Write-ColorText "⚠️ Warning: Could not upgrade pip" $Yellow
}

# Install packages in virtual environment
Write-ColorText "`n📦 Installing required Python packages in virtual environment..." $Blue

# Check if requirements.txt exists in mobile directory
$requirementsFile = "$mobileDir\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-ColorText "📋 Installing from requirements.txt..." $Yellow
    try {
        & $venvPython -m pip install -r $requirementsFile --upgrade --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ All packages installed from requirements.txt" $Green
        } else {
            Write-ColorText "⚠️ Some packages may have failed, installing individually..." $Yellow
        }
    } catch {
        Write-ColorText "⚠️ Error with requirements.txt, installing individually..." $Yellow
    }
} else {
    Write-ColorText "⚠️ requirements.txt not found, installing essential packages..." $Yellow
}

# Fallback: Install essential packages individually
$packages = @(
    "flask>=2.3.0",
    "flask-socketio>=5.3.0", 
    "flask-cors>=2.0.0",
    "python-socketio>=5.8.0",
    "eventlet>=0.33.0",
    "GitPython>=3.1.0",
    "watchdog>=3.0.0",
    "psutil>=5.9.0",
    "qrcode[pil]>=7.4.0",
    "requests>=2.31.0"
)

foreach ($pkg in $packages) {
    Write-ColorText "Installing $pkg..." $Yellow
    try {
        & $venvPython -m pip install $pkg --upgrade --quiet --disable-pip-version-check
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Installed $pkg" $Green
        } else {
            Write-ColorText "⚠️ Warning: Failed to install $pkg" $Yellow
        }
    } catch {
        Write-ColorText "⚠️ Warning: Error installing $pkg : $_" $Yellow
    }
}

Write-ColorText "✅ Virtual environment setup complete" $Green

# Download components
Write-ColorText "`n📥 Downloading mobile components from GitHub..." $Blue

$mobileDir = "$claudeDir\mobile"
$dashboardDir = "$claudeDir\dashboard"
$tunnelsDir = "$claudeDir\tunnels"

# Create directories
@($mobileDir, $dashboardDir, $tunnelsDir, "$dashboardDir\templates") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"

$files = @(
    @{path="mobile/launch_mobile.py"; dest="$mobileDir\launch_mobile.py"},
    @{path="mobile/mobile_display_server.py"; dest="$mobileDir\mobile_display_server.py"},
    @{path="mobile/mobile_auth.py"; dest="$mobileDir\mobile_auth.py"},
    @{path="mobile/qr_generator.py"; dest="$mobileDir\qr_generator.py"},
    @{path="mobile/requirements.txt"; dest="$mobileDir\requirements.txt"},
    @{path="mobile/README.md"; dest="$mobileDir\README.md"},
    @{path="dashboard/simple_dashboard.py"; dest="$dashboardDir\simple_dashboard.py"},
    @{path="dashboard/dashboard_server.py"; dest="$dashboardDir\dashboard_server.py"},
    @{path="dashboard/requirements.txt"; dest="$dashboardDir\requirements.txt"},
    @{path="dashboard/templates/dashboard.html"; dest="$dashboardDir\templates\dashboard.html"},
    @{path="tunnels/tunnel_manager.py"; dest="$tunnelsDir\tunnel_manager.py"},
    @{path="tunnels/setup_ngrok.py"; dest="$tunnelsDir\setup_ngrok.py"},
    @{path="tunnels/setup_cloudflare.py"; dest="$tunnelsDir\setup_cloudflare.py"}
)

$downloaded = 0
foreach ($file in $files) {
    Write-ColorText "  Downloading $($file.path)..." $Yellow
    try {
        $url = "$baseUrl/$($file.path)"
        Invoke-WebRequest -Uri $url -OutFile $file.dest -UseBasicParsing
        $downloaded++
    } catch {
        Write-ColorText "  Failed: $($file.path)" $Red
    }
}

Write-ColorText "✅ Downloaded $downloaded mobile components" $Green

# ALWAYS prompt for ngrok token
Write-ColorText "`n🚀 Starting Claude Code V3+ Mobile Access..." $Green
Write-ColorText ("=" * 60) $Blue

Write-ColorText @"

🔐 ngrok Authentication Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ngrok needs a free auth token to create secure tunnels.

📋 To get your token:
1. Go to: https://dashboard.ngrok.com/signup
2. Sign up for a free account (takes 30 seconds)
3. Copy your auth token from the dashboard

Your token looks like: 2fN9S1K8VxH3n7wP1mQ4567890_1AbCdEfGhIjKlMnOpQrStUv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"@ $Yellow

Write-Host ""
$authToken = Read-Host "🔑 Enter your ngrok auth token"

if (-not $authToken) {
    Write-ColorText "❌ No token provided - tunnel will not work!" $Red
    Write-ColorText "Please run again with your ngrok auth token" $Yellow
    exit 1
}

# Set token everywhere to ensure it works
$env:NGROK_AUTH_TOKEN = $authToken
[System.Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $authToken, "Process")
[System.Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $authToken, "User")
Write-ColorText "✅ Auth token set" $Green

# Configure ngrok directly if possible
$ngrokPath = "C:\Users\$env:USERNAME\ngrok.exe"
if (Test-Path $ngrokPath) {
    try {
        & $ngrokPath config add-authtoken $authToken 2>$null
        Write-ColorText "✅ ngrok configured with token" $Green
    } catch {
        Write-ColorText "⚠️ Could not configure ngrok directly" $Yellow
    }
}

# Launch mobile access
Write-ColorText "`n🚀 Launching mobile access system..." $Green
Write-Host ""

Push-Location $mobileDir

# Download required management files if needed
$venvManagerFile = "$mobileDir\venv_manager.py"
if (-not (Test-Path $venvManagerFile)) {
    Write-ColorText "📥 Downloading venv_manager.py..." $Yellow
    try {
        $url = "$baseUrl/mobile/venv_manager.py"
        Invoke-WebRequest -Uri $url -OutFile $venvManagerFile -UseBasicParsing
        Write-ColorText "✅ Downloaded venv_manager.py" $Green
    } catch {
        Write-ColorText "❌ Failed to download venv_manager.py" $Red
    }
}

$startupCheckFile = "$mobileDir\startup_check.py"
if (-not (Test-Path $startupCheckFile)) {
    Write-ColorText "📥 Downloading startup_check.py..." $Yellow
    try {
        $url = "$baseUrl/mobile/startup_check.py"
        Invoke-WebRequest -Uri $url -OutFile $startupCheckFile -UseBasicParsing
        Write-ColorText "✅ Downloaded startup_check.py" $Green
    } catch {
        Write-ColorText "❌ Failed to download startup_check.py" $Red
    }
}

# Run startup diagnostics first
Write-ColorText "`n🔍 Running startup diagnostics..." $Blue
try {
    & $venvPython "$startupCheckFile"
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✅ Startup diagnostics passed" $Green
    } else {
        Write-ColorText "⚠️ Some diagnostic checks failed - continuing anyway" $Yellow
    }
} catch {
    Write-ColorText "⚠️ Could not run diagnostics: $_" $Yellow
}

try {
    # Run Python script using virtual environment Python
    Write-ColorText "`n🚀 Launching mobile access with virtual environment..." $Green
    & $venvPython launch_mobile.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "`n✅ Mobile launcher completed!" $Green
        Write-ColorText "📱 Visit http://localhost:5555 for QR code and access info" $Blue
        Write-ColorText "" $White
        Write-ColorText "The page at localhost:5555 will show:" $Yellow
        Write-ColorText "  • QR code for mobile scanning" $Gray
        Write-ColorText "  • Tunnel URL for remote access" $Gray
        Write-ColorText "  • Auth token for secure connection" $Gray
        Write-ColorText "  • Instructions for Samsung Galaxy S25 Edge" $Gray
    } else {
        Write-ColorText "`n❌ Mobile launcher encountered an error" $Red
        Write-ColorText "Try running diagnostics: $venvPython $startupCheckFile" $Yellow
        Write-ColorText "Or run directly: $venvPython $mobileDir\launch_mobile.py" $Yellow
    }
} catch {
    Write-ColorText "❌ Error: $_" $Red
    Write-ColorText "Virtual Environment Python: $venvPython" $Gray
    Write-ColorText "Try running diagnostics for troubleshooting" $Yellow
} finally {
    Pop-Location
}

Write-ColorText "`n✅ Mobile access launcher completed!" $Green