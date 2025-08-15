#!/bin/bash
# React Native Mobile App Setup Script
# Ported from Flutter app by @9cat (MIT License)

echo "🚀 Setting up Claude Code Mobile App (React Native)"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js >= 16"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="16.0.0"

if ! node -pe "process.exit(require('semver').gte(process.version, '$REQUIRED_VERSION') ? 0 : 1)" 2>/dev/null; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js >= 16"
    exit 1
fi

echo "✅ Node.js version $NODE_VERSION is compatible"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check React Native CLI
if ! command -v npx &> /dev/null; then
    echo "❌ npx is not available. Please reinstall Node.js"
    exit 1
fi

# Platform-specific setup
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected - setting up iOS dependencies"
    
    # Check if Xcode is installed
    if ! command -v xcodebuild &> /dev/null; then
        echo "⚠️  Xcode not found. Install Xcode from the App Store for iOS development"
    else
        echo "✅ Xcode found"
    fi
    
    # Check CocoaPods
    if ! command -v pod &> /dev/null; then
        echo "📦 Installing CocoaPods..."
        sudo gem install cocoapods
    fi
    
    # Install iOS dependencies
    if [ -d "ios" ]; then
        echo "📦 Installing iOS pods..."
        cd ios && pod install && cd ..
        echo "✅ iOS pods installed"
    fi
fi

# Check Android setup
if [ -d "$ANDROID_HOME" ] || [ -d "$ANDROID_SDK_ROOT" ]; then
    echo "✅ Android SDK found"
else
    echo "⚠️  Android SDK not found. Set ANDROID_HOME or ANDROID_SDK_ROOT for Android development"
fi

# Create assets directory
mkdir -p assets

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 To start development:"
echo "   npm start          # Start Metro bundler"
echo "   npm run android    # Run on Android"
echo "   npm run ios        # Run on iOS"
echo ""
echo "🔗 Connect to Claude Code server:"
echo "   Default: http://192.168.2.178:64008"
echo "   Credentials: admin/password123"
echo ""
echo "📚 Original Flutter app by @9cat (MIT License)"
echo "   React Native port for Claude Code Dev Stack v3.0"
echo ""