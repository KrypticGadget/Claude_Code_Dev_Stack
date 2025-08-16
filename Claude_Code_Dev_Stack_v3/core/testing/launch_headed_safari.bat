@echo off
echo Starting Playwright Headed Safari (WebKit) Testing...
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
playwright install webkit
playwright install-deps

REM Set environment variables for headed mode
set BROWSER_TYPE=webkit
set HEADLESS=false
set SLOW_MO=500
set RECORD_VIDEO=true

echo.
echo Configuration:
echo - Browser: Safari (WebKit)
echo - Mode: Headed (visible browser)
echo - Slow Motion: 500ms
echo - Video Recording: Enabled
echo - Output Directory: test_outputs
echo.

REM Launch the testing framework
python launch_headed_testing.py ^
    --browser webkit ^
    --viewport-width 1920 ^
    --viewport-height 1080 ^
    --slow-mo 500 ^
    --record-video ^
    --output-dir test_outputs ^
    --test-suite all ^
    --base-url http://localhost:3000

pause