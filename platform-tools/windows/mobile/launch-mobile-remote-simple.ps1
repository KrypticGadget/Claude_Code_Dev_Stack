# Simplified Claude Code V3+ Mobile Access Launcher
# No regex issues, just works!

Write-Host @"
🚀 Claude Code V3+ Mobile Access Remote Launcher
=================================================
📱 Secure one-liner mobile access to your V3+ system
"@ -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Setup directories
$claudeDir = "$env:USERPROFILE\.claude"
$mobileDir = "$claudeDir\mobile"

# Create directories
@($mobileDir, "$claudeDir\dashboard", "$claudeDir\tunnels") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Install packages
Write-Host "`n📦 Installing required packages..." -ForegroundColor Yellow
pip install flask flask-socketio qrcode[pil] requests psutil --quiet 2>$null
Write-Host "✅ Packages installed" -ForegroundColor Green

# Download components
Write-Host "`n📥 Downloading components..." -ForegroundColor Yellow
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"

$files = @(
    "mobile/launch_mobile.py",
    "mobile/mobile_display_server.py",
    "mobile/mobile_auth.py",
    "mobile/qr_generator.py",
    "dashboard/dashboard_server.py",
    "tunnels/tunnel_manager.py",
    "tunnels/setup_ngrok.py",
    "tunnels/setup_cloudflare.py"
)

foreach ($file in $files) {
    $url = "$baseUrl/$file"
    $dest = "$claudeDir\$($file.Replace('/', '\'))"
    $destDir = Split-Path $dest -Parent
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    } catch {
        Write-Host "  Failed: $file" -ForegroundColor Yellow
    }
}

# Download dashboard template
$templateDir = "$claudeDir\dashboard\templates"
if (-not (Test-Path $templateDir)) {
    New-Item -ItemType Directory -Path $templateDir -Force | Out-Null
}
Invoke-WebRequest -Uri "$baseUrl/dashboard/templates/dashboard.html" -OutFile "$templateDir\dashboard.html" -UseBasicParsing

Write-Host "✅ Components downloaded" -ForegroundColor Green

# Check for ngrok token
if (-not $env:NGROK_AUTH_TOKEN) {
    Write-Host @"

🔐 ngrok Authentication Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ngrok needs a free auth token to create secure tunnels.

📋 To get your token:
1. Go to: https://dashboard.ngrok.com/signup
2. Sign up for a free account (takes 30 seconds)
3. Copy your auth token from the dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"@ -ForegroundColor Yellow
    
    $authToken = Read-Host "`n🔑 Enter your ngrok auth token (or press Enter to skip)"
    
    if ($authToken) {
        $env:NGROK_AUTH_TOKEN = $authToken
        [Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $authToken, "User")
        Write-Host "✅ Auth token saved" -ForegroundColor Green
    }
} else {
    Write-Host "✅ ngrok auth token found" -ForegroundColor Green
}

# Launch
Write-Host "`n🚀 Launching mobile access..." -ForegroundColor Green
Push-Location $mobileDir
python launch_mobile.py
Pop-Location

Write-Host "`n📱 Visit http://localhost:6000 to see QR code and access info" -ForegroundColor Cyan