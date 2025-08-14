# Setup ngrok for Claude Code V3+ Mobile Access

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║            Setup ngrok for Mobile Tunnel Access                 ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "`n📱 ngrok is required for mobile tunnel access" -ForegroundColor Yellow
Write-Host "This creates a secure HTTPS tunnel to your local dashboard" -ForegroundColor Gray

# Step 1: Check if ngrok is installed
$ngrokPath = "$env:USERPROFILE\ngrok.exe"
if (Test-Path $ngrokPath) {
    Write-Host "✅ ngrok is already installed" -ForegroundColor Green
} else {
    Write-Host "❌ ngrok not found - please run the mobile launcher to auto-install" -ForegroundColor Red
}

# Step 2: Guide user to get auth token
Write-Host "`n🔐 You need a free ngrok auth token:" -ForegroundColor Yellow
Write-Host "1. Go to: https://dashboard.ngrok.com/signup" -ForegroundColor White
Write-Host "2. Sign up for a free account" -ForegroundColor White
Write-Host "3. Copy your auth token from the dashboard" -ForegroundColor White
Write-Host "4. Come back here and paste it" -ForegroundColor White

Write-Host "`n⏸️  Press Enter to open ngrok signup page..." -ForegroundColor Cyan
Read-Host
Start-Process "https://dashboard.ngrok.com/signup"

Write-Host "`n📋 Paste your ngrok auth token here:" -ForegroundColor Yellow
$authToken = Read-Host

if ($authToken) {
    Write-Host "`n⚙️  Configuring ngrok..." -ForegroundColor Yellow
    
    # Add token to ngrok config
    & "$ngrokPath" config add-authtoken $authToken
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ngrok configured successfully!" -ForegroundColor Green
        
        # Save to environment variable for future use
        [Environment]::SetEnvironmentVariable("NGROK_AUTH_TOKEN", $authToken, "User")
        Write-Host "✅ Auth token saved to environment" -ForegroundColor Green
        
        Write-Host "`n🎉 ngrok is ready! Now run the mobile launcher again:" -ForegroundColor Green
        Write-Host @"
        
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mobile/launch-mobile-remote.ps1" -UseBasicParsing | iex

"@ -ForegroundColor Cyan
        
        Write-Host "The mobile launcher will now:" -ForegroundColor White
        Write-Host "  1. Start the dashboard on port 8080" -ForegroundColor Gray
        Write-Host "  2. Create HTTPS tunnel with ngrok" -ForegroundColor Gray
        Write-Host "  3. Open http://localhost:6000 with QR code" -ForegroundColor Gray
        Write-Host "  4. Display mobile URL and auth token" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Failed to configure ngrok" -ForegroundColor Red
        Write-Host "Try running manually: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No auth token provided" -ForegroundColor Red
    Write-Host "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
}

Write-Host "`n✨ Alternative: Use Cloudflare Tunnel (no signup required)" -ForegroundColor Cyan
Write-Host "The mobile launcher will automatically try Cloudflare if ngrok fails" -ForegroundColor Gray