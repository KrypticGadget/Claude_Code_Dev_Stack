@echo off
echo Starting Playwright Headed Chrome Testing...
echo.

REM Set the working directory to the testing folder
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium
playwright install-deps

REM Set environment variables for headed mode
set BROWSER_TYPE=chromium
set HEADLESS=false
set SLOW_MO=500
set RECORD_VIDEO=false

echo.
echo Configuration:
echo - Browser: Chrome (Chromium)
echo - Mode: Headed (visible browser)
echo - Slow Motion: 500ms
echo - Video Recording: Disabled
echo - Output Directory: test_outputs
echo.

REM Launch the testing framework
python launch_headed_testing.py ^
    --browser chromium ^
    --viewport-width 1920 ^
    --viewport-height 1080 ^
    --slow-mo 500 ^
    --output-dir test_outputs ^
    --test-suite all ^
    --base-url http://localhost:3000

pause