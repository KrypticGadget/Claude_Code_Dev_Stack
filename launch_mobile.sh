#!/bin/bash
# Claude Code V3+ Mobile Launcher - One-Line Command
# Securely launches dashboard with tunnel and sends access to phone

echo "🚀 Claude Code V3+ Mobile Access Launcher"
echo "==========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f ".claude-example/mobile/launch_mobile.py" ]; then
    echo "❌ Not in Claude Code Dev Stack directory"
    echo "Please run this from: Claude_Code_Dev_Stack/"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
python3 -c "import flask, qrcode" &>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip3 install flask flask-socketio qrcode[pil] requests psutil
fi

# Launch mobile access
echo "🚀 Starting secure mobile access..."
python3 .claude-example/mobile/launch_mobile.py "$@"