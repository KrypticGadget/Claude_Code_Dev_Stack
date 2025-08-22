@echo off
REM Repository Organization Script for Windows
REM Cleans and organizes the V3.6.9 repository structure

echo ================================================
echo  Claude Code Agents V3.6.9 Repository Organizer
echo ================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..

echo Repository location: %REPO_ROOT%
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Starting organization process...
echo.

REM Ask for confirmation unless --force is passed
if "%1"=="--force" goto :start_org
if "%1"=="--dry-run" goto :dry_run

echo This will organize your repository structure and create backups.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Organization cancelled.
    pause
    exit /b 0
)

:start_org
echo Starting repository organization...
python "%SCRIPT_DIR%automated-repository-organizer.py" "%REPO_ROOT%"
goto :end

:dry_run
echo Running in DRY RUN mode (no changes will be made)...
python "%SCRIPT_DIR%automated-repository-organizer.py" "%REPO_ROOT%" --dry-run
goto :end

:end
echo.
if %errorlevel% equ 0 (
    echo ✅ Repository organization completed successfully!
    echo.
    echo Next steps:
    echo 1. Review ORGANIZATION_GUIDE.md for usage instructions
    echo 2. Run: python scripts\validate-organization.py to verify
    echo 3. Set up scheduled maintenance if desired
) else (
    echo ❌ Repository organization encountered errors
    echo Check the organization report for details
)
echo.
pause