@echo off
REM Quick Consolidation Script for Windows
REM =====================================
REM Executes the v3 consolidation process with safety checks

echo.
echo ============================================================
echo  Claude Code Dev Stack v3 Consolidation
echo ============================================================
echo.

REM Change to the script directory
cd /d "%~dp0"
cd ..

REM Check if v3 directory exists
if not exist "Claude_Code_Dev_Stack_v3" (
    echo ERROR: Claude_Code_Dev_Stack_v3 directory not found
    echo Make sure you're running this from the correct location
    pause
    exit /b 1
)

REM Safety prompt
echo This will consolidate the v3 structure into the root level.
echo A full backup will be created before making any changes.
echo.
set /p CONFIRM="Do you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Consolidation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting consolidation process...
echo.

REM Try PowerShell first, then Python fallback
where powershell >nul 2>&1
if %errorlevel%==0 (
    echo Using PowerShell consolidation script...
    powershell -ExecutionPolicy Bypass -File "scripts\consolidate_v3_structure.ps1"
    set CONSOLIDATION_RESULT=%errorlevel%
) else (
    REM Check for Python
    where python >nul 2>&1
    if %errorlevel%==0 (
        echo Using Python consolidation script...
        python scripts\consolidate_v3_structure.py
        set CONSOLIDATION_RESULT=%errorlevel%
    ) else (
        echo ERROR: Neither PowerShell nor Python found
        echo Please install Python or enable PowerShell
        pause
        exit /b 1
    )
)

echo.
if %CONSOLIDATION_RESULT%==0 (
    echo ============================================================
    echo  CONSOLIDATION COMPLETED SUCCESSFULLY
    echo ============================================================
    echo.
    echo Next steps:
    echo 1. Run validation: scripts\validate_consolidation.ps1
    echo 2. Test functionality
    echo 3. Review CONSOLIDATION_REPORT.md
    echo.
) else (
    echo ============================================================
    echo  CONSOLIDATION FAILED
    echo ============================================================
    echo.
    echo Check the logs and restore from backup if needed.
    echo Backup location will be shown in the error output above.
    echo.
)

pause