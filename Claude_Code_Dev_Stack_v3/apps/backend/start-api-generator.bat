@echo off
echo Starting API Generator Service...
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist "package.json" (
    echo Setting up package.json...
    if exist "api-generator-package.json" (
        copy "api-generator-package.json" "package.json"
    ) else (
        echo Error: No package configuration found
        pause
        exit /b 1
    )
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the service
echo.
echo Starting API Generator on port 8082...
echo Open http://localhost:3000/api-generator in your browser
echo.
echo Press Ctrl+C to stop the service
echo.

node start-api-generator.js