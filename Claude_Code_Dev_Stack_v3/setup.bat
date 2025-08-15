@echo off
REM Claude Code Dev Stack v3.0 - Windows Setup Script
REM This script sets up the complete development environment

echo ==========================================
echo 🚀 Claude Code Dev Stack v3.0 Setup
echo ==========================================
echo.

REM Check Python installation
where python >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python is not installed. Please install Python 3.8 or higher.
        pause
        exit /b 1
    )
)

echo 🐍 Using Python: %PYTHON_CMD%
echo.

REM Run Python setup script
echo 📦 Setting up virtual environment...
%PYTHON_CMD% setup_environment.py

REM Check if venv was created successfully
if exist "venv" (
    echo ✅ Virtual environment created
    echo.
    
    REM Create quick start script
    echo @echo off > start_dev.bat
    echo call activate.bat >> start_dev.bat
    echo echo. >> start_dev.bat
    echo echo Claude Code Dev Stack v3.0 - Development Environment >> start_dev.bat
    echo echo ========================================== >> start_dev.bat
    echo echo. >> start_dev.bat
    echo echo Available commands: >> start_dev.bat
    echo echo   - cd apps\web ^&^& npm run dev    : Start PWA >> start_dev.bat
    echo echo   - cd apps\mobile ^&^& npm start   : Start Mobile >> start_dev.bat
    echo echo   - python -m pytest              : Run tests >> start_dev.bat
    echo echo. >> start_dev.bat
    
    echo ==========================================
    echo ✅ Setup Complete!
    echo ==========================================
    echo.
    echo 📚 Next Steps:
    echo 1. Activate virtual environment:
    echo    activate.bat
    echo.
    echo 2. Install Node.js dependencies:
    echo    cd apps\web ^&^& npm install
    echo    cd apps\mobile ^&^& npm install
    echo.
    echo 3. Start development:
    echo    PWA: cd apps\web ^&^& npm run dev
    echo    Mobile: cd apps\mobile ^&^& npm start
    echo.
    echo 4. Quick start (after setup):
    echo    start_dev.bat
    echo.
    echo 📖 Documentation: docs\README.md
    echo 🔧 Configuration: .env.example
    echo.
    echo 🙏 Attribution:
    echo    See CREDITS.md for all integrated projects
    echo ==========================================
) else (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

pause