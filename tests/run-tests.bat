@echo off
REM Windows batch script for running agent tests
REM Agent Test Framework V3.6.9

echo.
echo ================================================================
echo    AGENT TEST FRAMEWORK V3.6.9
echo    Comprehensive Testing for all 37 Agents
echo ================================================================
echo.

REM Check if Python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.9+ and add to PATH
    exit /b 1
)

REM Check if we're in the right directory
if not exist "test-runner.py" (
    echo ❌ Please run this script from the tests\ directory
    echo Current directory: %cd%
    exit /b 1
)

REM Setup environment if needed
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports

echo 🔧 Setting up test environment...

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing dependencies...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ⚠️  No requirements.txt found, skipping dependency installation
)

echo.
echo 🚀 Starting comprehensive agent testing...
echo.

REM Default to running all tests unless arguments provided
if "%1"=="" (
    echo Running all test suites...
    python test-runner.py --verbose
) else (
    echo Running with custom arguments: %*
    python test-runner.py %*
)

set TEST_EXIT_CODE=%errorlevel%

echo.
if %TEST_EXIT_CODE% equ 0 (
    echo ✅ Tests completed successfully!
    echo.
    echo 📊 Check results in:
    echo   - HTML Report: reports\test-report-*.html
    echo   - JSON Results: reports\test-results-*.json
    echo   - Logs: logs\agent-test-execution.log
) else (
    echo ❌ Tests failed with exit code %TEST_EXIT_CODE%
    echo.
    echo 🔍 Check logs for details:
    echo   - Logs: logs\agent-test-execution.log
    echo   - Reports: reports\
)

echo.
echo ================================================================
echo    For help: python test-runner.py --help
echo    Documentation: README.md
echo ================================================================

exit /b %TEST_EXIT_CODE%