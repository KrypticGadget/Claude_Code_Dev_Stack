@echo off
REM Claude Code Mobile Launcher - Windows Batch Script
REM Bulletproof launcher that handles virtual environment setup and dependency installation
REM Author: DevOps Engineering Agent V3.0

setlocal EnableDelayedExpansion

echo ===========================================================
echo 🚀 Claude Code Mobile Launcher - V3.0 Enhanced
echo ===========================================================

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"
set "REQUIREMENTS_FILE=%SCRIPT_DIR%requirements.txt"
set "LAUNCHER_SCRIPT=%SCRIPT_DIR%launch_mobile.py"

echo 📂 Working Directory: %SCRIPT_DIR%
echo 🐍 Virtual Environment: %VENV_DIR%

REM Step 1: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    pause
    exit /b 1
)

echo ✅ Python is available
python --version

REM Step 2: Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo 🔧 Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created successfully
) else (
    echo ✅ Virtual environment already exists
)

REM Step 3: Verify virtual environment Python exists
if not exist "%VENV_PYTHON%" (
    echo ❌ Virtual environment Python not found at: %VENV_PYTHON%
    echo Recreating virtual environment...
    rmdir /s /q "%VENV_DIR%"
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Failed to recreate virtual environment
        pause
        exit /b 1
    )
)

echo ✅ Virtual environment Python found: %VENV_PYTHON%

REM Step 4: Activate virtual environment and upgrade pip
echo 📦 Updating pip in virtual environment...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️ Warning: Failed to upgrade pip, continuing...
) else (
    echo ✅ pip upgraded successfully
)

REM Step 5: Install dependencies from requirements.txt
if exist "%REQUIREMENTS_FILE%" (
    echo 📋 Installing dependencies from requirements.txt...
    echo    This may take a few minutes...
    "%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS_FILE%" --upgrade
    if errorlevel 1 (
        echo ⚠️ Warning: Some packages may have failed to install
        echo Continuing with individual package installation...
        
        REM Fallback: Install essential packages individually
        echo 📦 Installing essential packages...
        "%VENV_PYTHON%" -m pip install flask>=2.3.0
        "%VENV_PYTHON%" -m pip install flask-socketio>=5.3.0
        "%VENV_PYTHON%" -m pip install psutil>=5.9.0
        "%VENV_PYTHON%" -m pip install requests>=2.31.0
        "%VENV_PYTHON%" -m pip install qrcode[pil]>=7.4.0
        "%VENV_PYTHON%" -m pip install watchdog>=3.0.0
        "%VENV_PYTHON%" -m pip install GitPython>=3.1.0
    ) else (
        echo ✅ All dependencies installed successfully
    )
) else (
    echo ⚠️ requirements.txt not found, installing essential packages...
    "%VENV_PYTHON%" -m pip install flask flask-socketio psutil requests qrcode[pil] watchdog GitPython
)

REM Step 6: Verify launcher script exists
if not exist "%LAUNCHER_SCRIPT%" (
    echo ❌ Launcher script not found: %LAUNCHER_SCRIPT%
    echo Please ensure launch_mobile.py exists in the same directory as this batch file
    pause
    exit /b 1
)

echo ✅ Launcher script found: %LAUNCHER_SCRIPT%

REM Step 7: Set environment variables for better Windows compatibility
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

REM Step 8: Launch the mobile access system
echo ===========================================================
echo 🚀 Starting Claude Code Mobile Access System...
echo ===========================================================
echo.
echo 📱 The system will start:
echo    • QR server on port 5555
echo    • Dashboard on port 8080  
echo    • Terminal (ttyd) on port 7681
echo    • Secure tunnel via ngrok
echo.
echo 🛑 Press Ctrl+C to stop all services
echo ===========================================================
echo.

REM Change to the script directory to ensure relative paths work
cd /d "%SCRIPT_DIR%"

REM Run the Python launcher with the virtual environment Python
"%VENV_PYTHON%" "%LAUNCHER_SCRIPT%" %*

REM Handle the exit code
if errorlevel 1 (
    echo.
    echo ❌ Mobile launcher exited with error code: %errorlevel%
    echo Check the output above for error details
) else (
    echo.
    echo ✅ Mobile launcher completed successfully
)

echo.
echo 🧹 Cleanup completed
pause