# React Native Mobile App Setup Script (PowerShell)
# Ported from Flutter app by @9cat (MIT License)

Write-Host "🚀 Setting up Claude Code Mobile App (React Native)" -ForegroundColor Green

# Check Node.js version
try {
    $nodeVersion = node -v
    $nodeVersionNumber = $nodeVersion.Replace('v', '')
    Write-Host "✅ Node.js version $nodeVersionNumber found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js >= 16" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Check for Android SDK
if ($env:ANDROID_HOME -or $env:ANDROID_SDK_ROOT) {
    Write-Host "✅ Android SDK found" -ForegroundColor Green
} else {
    Write-Host "⚠️  Android SDK not found. Set ANDROID_HOME or ANDROID_SDK_ROOT for Android development" -ForegroundColor Yellow
}

# Create assets directory
if (!(Test-Path "assets")) {
    New-Item -ItemType Directory -Name "assets"
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 To start development:" -ForegroundColor Cyan
Write-Host "   npm start          # Start Metro bundler"
Write-Host "   npm run android    # Run on Android"
Write-Host ""
Write-Host "🔗 Connect to Claude Code server:" -ForegroundColor Cyan
Write-Host "   Default: http://192.168.2.178:64008"
Write-Host "   Credentials: admin/password123"
Write-Host ""
Write-Host "📚 Original Flutter app by @9cat (MIT License)" -ForegroundColor Magenta
Write-Host "   React Native port for Claude Code Dev Stack v3.0"
Write-Host ""