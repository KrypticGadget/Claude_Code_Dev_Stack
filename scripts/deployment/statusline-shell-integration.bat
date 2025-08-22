@echo off
REM Windows Batch Script for Statusline Shell Integration
REM Provides statusline integration for Windows Command Prompt and PowerShell

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "STATUSLINE_CMD=%PROJECT_ROOT%\bin\statusline.py"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if statusline script exists
if not exist "%STATUSLINE_CMD%" (
    echo Error: Statusline script not found at %STATUSLINE_CMD%
    exit /b 1
)

echo Claude Code Terminal Statusline - Windows Integration
echo =====================================================

REM Function to render statusline
:render_statusline
python "%STATUSLINE_CMD%" render 2>nul
if %errorlevel% equ 0 (
    goto :eof
) else (
    REM Silently ignore errors
    goto :eof
)

REM Check command line arguments
if "%1"=="render" (
    call :render_statusline
    goto :eof
)

if "%1"=="install" (
    goto :install_integration
)

if "%1"=="uninstall" (
    goto :uninstall_integration
)

REM Default action - show help
echo Usage:
echo   %~nx0 render      - Render statusline once
echo   %~nx0 install     - Install PowerShell integration
echo   %~nx0 uninstall   - Remove PowerShell integration
echo.
echo For Command Prompt integration, add this to your AutoRun registry:
echo   %~f0 render
echo.
echo For PowerShell, run: %~nx0 install
goto :eof

:install_integration
echo Installing PowerShell integration...

REM Find PowerShell profile path
set "PS_PROFILE="
for /f "delims=" %%i in ('powershell -Command "Split-Path $PROFILE"') do set "PS_PROFILE_DIR=%%i"
if not defined PS_PROFILE_DIR (
    echo Error: Could not determine PowerShell profile directory
    exit /b 1
)

set "PS_PROFILE=%PS_PROFILE_DIR%\Microsoft.PowerShell_profile.ps1"

REM Create profile directory if it doesn't exist
if not exist "%PS_PROFILE_DIR%" (
    mkdir "%PS_PROFILE_DIR%"
)

REM Check if integration already exists
if exist "%PS_PROFILE%" (
    findstr /C:"Claude Code Statusline" "%PS_PROFILE%" >nul
    if !errorlevel! equ 0 (
        echo PowerShell integration already installed
        goto :eof
    )
)

REM Add integration to PowerShell profile
echo. >> "%PS_PROFILE%"
echo # Claude Code Statusline Integration >> "%PS_PROFILE%"
echo function Update-ClaudeStatusline { >> "%PS_PROFILE%"
echo     if ($Host.UI.RawUI.WindowSize) { >> "%PS_PROFILE%"
echo         try { >> "%PS_PROFILE%"
echo             $statuslineOutput = ^& python "%STATUSLINE_CMD%" render 2^>$null >> "%PS_PROFILE%"
echo             if ($LASTEXITCODE -eq 0 -and $statuslineOutput) { >> "%PS_PROFILE%"
echo                 $position = $Host.UI.RawUI.CursorPosition >> "%PS_PROFILE%"
echo                 $Host.UI.RawUI.CursorPosition = @{X=0; Y=0} >> "%PS_PROFILE%"
echo                 Write-Host $statuslineOutput -NoNewline >> "%PS_PROFILE%"
echo                 $Host.UI.RawUI.CursorPosition = $position >> "%PS_PROFILE%"
echo             } >> "%PS_PROFILE%"
echo         } catch { >> "%PS_PROFILE%"
echo             # Silently ignore errors >> "%PS_PROFILE%"
echo         } >> "%PS_PROFILE%"
echo     } >> "%PS_PROFILE%"
echo } >> "%PS_PROFILE%"
echo. >> "%PS_PROFILE%"
echo # Update statusline with each prompt >> "%PS_PROFILE%"
echo $function:prompt = { >> "%PS_PROFILE%"
echo     Update-ClaudeStatusline >> "%PS_PROFILE%"
echo     "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) " >> "%PS_PROFILE%"
echo } >> "%PS_PROFILE%"

echo PowerShell integration installed to: %PS_PROFILE%
echo Restart PowerShell to activate the statusline
goto :eof

:uninstall_integration
echo Removing PowerShell integration...

set "PS_PROFILE="
for /f "delims=" %%i in ('powershell -Command "$PROFILE"') do set "PS_PROFILE=%%i"

if not exist "%PS_PROFILE%" (
    echo No PowerShell profile found
    goto :eof
)

REM Create a temporary file without statusline integration
set "TEMP_PROFILE=%TEMP%\ps_profile_temp.ps1"
type nul > "%TEMP_PROFILE%"

set "SKIP_BLOCK=0"
for /f "delims=" %%i in (%PS_PROFILE%) do (
    set "LINE=%%i"
    echo !LINE! | findstr /C:"Claude Code Statusline" >nul
    if !errorlevel! equ 0 (
        set "SKIP_BLOCK=1"
    ) else (
        if "!SKIP_BLOCK!"=="1" (
            echo !LINE! | findstr /R "^$" >nul
            if !errorlevel! equ 0 (
                set "SKIP_BLOCK=0"
            )
        ) else (
            echo !LINE! >> "%TEMP_PROFILE%"
        )
    )
)

REM Replace original profile with cleaned version
move "%TEMP_PROFILE%" "%PS_PROFILE%"
echo PowerShell integration removed
goto :eof