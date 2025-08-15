@echo off
REM Windows batch activation script for Claude Code mobile monitoring system
echo Activating Claude Code Mobile Virtual Environment...

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check activation
if "%VIRTUAL_ENV%" == "" (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo ✅ Virtual environment activated successfully!
echo Python path: %VIRTUAL_ENV%
echo.
echo Available commands:
echo   python launch_mobile.py    - Start mobile dashboard
echo   pip list                   - Show installed packages
echo   deactivate                 - Exit virtual environment
echo.