@echo off
REM Setup Windows Task for weekly maintenance

schtasks /create /tn "Repository Maintenance" /tr "python scripts\weekly-maintenance.py" /sc weekly /d SUN /st 02:00 /f

echo Windows Task created for weekly repository maintenance
pause
