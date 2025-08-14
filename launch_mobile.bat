@echo off
REM Claude Code V3+ Mobile Launcher - One-Line Command
REM Securely launches dashboard with tunnel and sends access to phone

echo 🚀 Claude Code V3+ Mobile Access Launcher
echo ===========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist ".claude-example\mobile\launch_mobile.py" (
    echo ❌ Not in Claude Code Dev Stack directory
    echo Please run this from: Claude_Code_Dev_Stack\
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import flask, qrcode" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install flask flask-socketio qrcode[pil] requests psutil
)

REM Launch mobile access
echo 🚀 Starting secure mobile access...
python .claude-example\mobile\launch_mobile.py %*

pause