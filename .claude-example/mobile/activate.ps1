# PowerShell activation script for Claude Code mobile monitoring system
Write-Host "Activating Claude Code Mobile Virtual Environment..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found. Please run setup first." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Activate virtual environment
try {
    & .\.venv\Scripts\Activate.ps1
    
    # Verify activation
    if ($env:VIRTUAL_ENV) {
        Write-Host ""
        Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
        Write-Host "Python path: $env:VIRTUAL_ENV" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  python launch_mobile.py    - Start mobile dashboard" -ForegroundColor White
        Write-Host "  pip list                   - Show installed packages" -ForegroundColor White
        Write-Host "  deactivate                 - Exit virtual environment" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error activating virtual environment: $_" -ForegroundColor Red
    exit 1
}