@echo off
REM MCP Manager Quick Launch Script
REM Original concept by @qdhenry (MIT License)
REM Enhanced for Claude Code Dev Stack by DevOps Agent

echo.
echo  __  __  ____  ____    __  __
echo ^|  \/  ^|/ ___^|/ ___^|  ^|  \/  ^| __ _ _ __   __ _  __ _  ___ _ __
echo ^| ^|\/^| ^| ^|   ^| ^|      ^| ^|\/^| ^|/ _' ^| '_ \ / _' ^|/ _' ^|/ _ \ '^|
echo ^| ^|  ^| ^| ^|___^| ^|___   ^| ^|  ^| ^| (^_^| ^| ^| ^| ^| (^_^| ^| (^_^| ^|  __/ ^|
echo ^|_^|  ^|_^|\____^|\____^|  ^|_^|  ^|_^|\__,_^|_^| ^|_^|\__,_^|\__, ^|\_^^_^|_^|
echo                                                ^|___/
echo.
echo Model Context Protocol Manager - Enhanced for Claude Code Dev Stack
echo Original concept by @qdhenry (MIT License)
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: PowerShell not found. Please install PowerShell.
    pause
    exit /b 1
)

REM Set working directory to script location
cd /d "%~dp0"

echo Starting MCP Manager...
echo.

REM Launch the PowerShell script
powershell -ExecutionPolicy Bypass -File "scripts\Start-MCPManager.ps1" -InstallDependencies -SetupEnvironment -Background

if %ERRORLEVEL% equ 0 (
    echo.
    echo MCP Manager started successfully!
    echo.
    echo Services:
    echo - API Server: http://localhost:8000
    echo - Health Check: http://localhost:8000/health
    echo - API Documentation: http://localhost:8000/docs
    echo.
    echo Services will automatically start on these ports:
    echo - Playwright MCP: http://localhost:8080
    echo - GitHub MCP: http://localhost:8081
    echo - WebSearch MCP: http://localhost:8082
    echo.
    echo To manage services, open the PWA dashboard or use PowerShell commands.
    echo.
) else (
    echo.
    echo Failed to start MCP Manager. Check the logs for details.
    echo.
)

pause