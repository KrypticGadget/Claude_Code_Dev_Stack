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

# Install packages
Write-ColorText "`n📦 Installing required Python packages..." $Blue
$packages = @("flask", "flask-socketio", "qrcode[pil]", "requests", "psutil")
foreach ($pkg in $packages) {
    Write-ColorText "Installing $pkg..." $Yellow
    pip install $pkg --quiet --disable-pip-version-check 2>$null
}
Write-ColorText "✅ Package installation complete" $Green

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
    @{path="mobile/README.md"; dest="$mobileDir\README.md"},
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

try {
    # Run Python script
    & python launch_mobile.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "`n✅ Mobile launcher completed!" $Green
        Write-ColorText "📱 Visit http://localhost:6000 for QR code and access info" $Blue
        Write-ColorText "" $White
        Write-ColorText "The page at localhost:6000 will show:" $Yellow
        Write-ColorText "  • QR code for mobile scanning" $Gray
        Write-ColorText "  • Tunnel URL for remote access" $Gray
        Write-ColorText "  • Auth token for secure connection" $Gray
        Write-ColorText "  • Instructions for Samsung Galaxy S25 Edge" $Gray
    } else {
        Write-ColorText "`n❌ Mobile launcher encountered an error" $Red
        Write-ColorText "Try running directly: python $mobileDir\launch_mobile.py" $Yellow
    }
} catch {
    Write-ColorText "❌ Error: $_" $Red
} finally {
    Pop-Location
}

Write-ColorText "`n✅ Mobile access launcher completed!" $Green