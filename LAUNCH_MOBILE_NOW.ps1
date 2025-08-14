# WORKING Claude Code V3+ Mobile Launcher - USE THIS ONE!
# This version ALWAYS prompts for token and WORKS

Write-Host @"
🚀 Claude Code V3+ Mobile Access Launcher
=========================================
📱 This will launch mobile access with QR code at localhost:6000
"@ -ForegroundColor Cyan

# Always get fresh token
Write-Host @"

🔐 ngrok Token Required
━━━━━━━━━━━━━━━━━━━━━━━
Your token: 31GCejnXcxdT7Hcu4UP88y4DF3k_6mxiWHwD7MuhUyYrRdJvw
(or get from https://dashboard.ngrok.com)
━━━━━━━━━━━━━━━━━━━━━━━
"@ -ForegroundColor Yellow

$token = Read-Host "Enter ngrok token"
if (-not $token) {
    $token = "31GCejnXcxdT7Hcu4UP88y4DF3k_6mxiWHwD7MuhUyYrRdJvw"
}

# Set token everywhere
$env:NGROK_AUTH_TOKEN = $token
[Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $token, "Process")
[Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $token, "User")

# Configure ngrok
try {
    & C:\Users\Zach\ngrok.exe config add-authtoken $token 2>$null
    Write-Host "✅ ngrok configured" -ForegroundColor Green
} catch {}

# Go to mobile dir and run
$mobileDir = "$env:USERPROFILE\.claude\mobile"
if (Test-Path $mobileDir) {
    Push-Location $mobileDir
    
    Write-Host "`n🚀 Launching mobile access..." -ForegroundColor Green
    Write-Host "This will:" -ForegroundColor Cyan
    Write-Host "  1. Start dashboard on port 8080" -ForegroundColor Gray
    Write-Host "  2. Create ngrok tunnel" -ForegroundColor Gray  
    Write-Host "  3. Generate QR code" -ForegroundColor Gray
    Write-Host "  4. Open web display at http://localhost:6000" -ForegroundColor Gray
    Write-Host ""
    
    # Run Python script
    python launch_mobile.py
    
    Pop-Location
} else {
    Write-Host "❌ Mobile directory not found. Run the installer first." -ForegroundColor Red
}

Write-Host "`n📱 Check http://localhost:6000 for QR code!" -ForegroundColor Cyan