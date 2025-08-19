# Claude Code Dev Stack v3.0 - Unified Startup Script
# Starts all services for the complete unified experience

param(
    [switch]$InstallDeps,
    [switch]$TestMode,
    [switch]$Docker
)

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Claude Code Dev Stack v3.0 - Unified Startup    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running in Docker mode
if ($Docker) {
    Write-Host "Starting in Docker mode..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Docker services started. Access at http://localhost:5173" -ForegroundColor Green
    exit
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    
    # Install unified server dependencies
    Write-Host "Installing server dependencies..." -ForegroundColor Cyan
    Set-Location -Path "server"
    npm install express ws cors
    Set-Location -Path ".."
    
    # Install PWA dependencies
    Write-Host "Installing PWA dependencies..." -ForegroundColor Cyan
    Set-Location -Path "ui\react-pwa"
    npm install
    Set-Location -Path "..\.."
    
    Write-Host "Dependencies installed!" -ForegroundColor Green
}

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow

# Kill any existing processes on our ports
Write-Host "Cleaning up existing processes..." -ForegroundColor Cyan
netstat -ano | findstr :8000 | ForEach-Object {
    $parts = $_ -split '\s+'
    $pid = $parts[-1]
    if ($pid -ne "0") {
        try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
}
netstat -ano | findstr :5173 | ForEach-Object {
    $parts = $_ -split '\s+'
    $pid = $parts[-1]
    if ($pid -ne "0") {
        try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
}

# Start unified backend server
Write-Host "Starting unified backend server on port 8000..." -ForegroundColor Cyan
$serverJob = Start-Job -ScriptBlock {
    Set-Location -Path $using:PWD
    node server\unified-server.js
}

# Wait for server to start
Start-Sleep -Seconds 3

# Start React PWA
Write-Host "Starting React PWA on port 5173..." -ForegroundColor Cyan
$pwaJob = Start-Job -ScriptBlock {
    Set-Location -Path "$using:PWD\ui\react-pwa"
    npm run dev
}

# Wait for PWA to start
Start-Sleep -Seconds 5

# Check if services are running
$serverRunning = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
$pwaRunning = Test-NetConnection -ComputerName localhost -Port 5173 -InformationLevel Quiet

if ($serverRunning -and $pwaRunning) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║           ALL SERVICES STARTED SUCCESSFULLY       ║" -ForegroundColor Green
    Write-Host "╠════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║                                                    ║" -ForegroundColor Green
    Write-Host "║   PWA Interface:  http://localhost:5173           ║" -ForegroundColor Green
    Write-Host "║   Backend API:    http://localhost:8000           ║" -ForegroundColor Green
    Write-Host "║   WebSocket:      ws://localhost:8000/ws          ║" -ForegroundColor Green
    Write-Host "║                                                    ║" -ForegroundColor Green
    Write-Host "║   Features Available:                             ║" -ForegroundColor Green
    Write-Host "║   • 28 AI Agents                                  ║" -ForegroundColor Green
    Write-Host "║   • 37 Event Hooks                                ║" -ForegroundColor Green
    Write-Host "║   • Audio System with Phase Awareness             ║" -ForegroundColor Green
    Write-Host "║   • MCP Code Generators (Python & Node.js)        ║" -ForegroundColor Green
    Write-Host "║   • LSP Diagnostics                               ║" -ForegroundColor Green
    Write-Host "║   • Semantic Analysis                             ║" -ForegroundColor Green
    Write-Host "║   • AI Pattern Detection                          ║" -ForegroundColor Green
    Write-Host "║   • Visual Documentation Pipeline                 ║" -ForegroundColor Green
    Write-Host "║   • BMAD Planning Methodology                     ║" -ForegroundColor Green
    Write-Host "║   • Voice Assistant                               ║" -ForegroundColor Green
    Write-Host "║   • Real-time WebSocket Updates                   ║" -ForegroundColor Green
    Write-Host "║   • PWA with Offline Support                      ║" -ForegroundColor Green
    Write-Host "║                                                    ║" -ForegroundColor Green
    Write-Host "║   Press Ctrl+C to stop all services               ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    # Run tests if requested
    if ($TestMode) {
        Write-Host ""
        Write-Host "Running Playwright tests in 10 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        Set-Location -Path "tests\e2e"
        npm test
        Set-Location -Path "..\.."
    }
    
    # Keep script running
    Write-Host ""
    Write-Host "Services are running. Press Ctrl+C to stop." -ForegroundColor Cyan
    
    # Monitor jobs
    while ($true) {
        if ($serverJob.State -ne "Running" -or $pwaJob.State -ne "Running") {
            Write-Host "A service has stopped. Checking status..." -ForegroundColor Yellow
            
            if ($serverJob.State -ne "Running") {
                Write-Host "Backend server stopped. Error:" -ForegroundColor Red
                Receive-Job $serverJob
            }
            
            if ($pwaJob.State -ne "Running") {
                Write-Host "PWA stopped. Error:" -ForegroundColor Red
                Receive-Job $pwaJob
            }
            
            break
        }
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "Failed to start services!" -ForegroundColor Red
    if (-not $serverRunning) {
        Write-Host "Backend server failed to start on port 8000" -ForegroundColor Red
        Receive-Job $serverJob
    }
    if (-not $pwaRunning) {
        Write-Host "PWA failed to start on port 5173" -ForegroundColor Red
        Receive-Job $pwaJob
    }
}

# Cleanup on exit
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Job $serverJob -ErrorAction SilentlyContinue
Stop-Job $pwaJob -ErrorAction SilentlyContinue
Remove-Job $serverJob -ErrorAction SilentlyContinue
Remove-Job $pwaJob -ErrorAction SilentlyContinue
Write-Host "Services stopped." -ForegroundColor Green