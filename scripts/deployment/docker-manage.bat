@echo off
REM Claude Code Dev Stack V3.6.9 - Docker Management Script (Windows)
REM Comprehensive management for all 11 services

setlocal EnableDelayedExpansion

set COMPOSE_FILE=docker-compose.yml
set PROJECT_NAME=claude-dev-stack
set LOG_DIR=.\logs
set BACKUP_DIR=.\backups

REM Colors (using PowerShell for colored output)
set RED=[31m
set GREEN=[32m
set YELLOW=[33m
set BLUE=[34m
set NC=[0m

REM Create directories
if not exist %LOG_DIR% mkdir %LOG_DIR%
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%
if not exist .\config\postgres mkdir .\config\postgres
if not exist .\config\redis mkdir .\config\redis
if not exist .\config\ngrok mkdir .\config\ngrok
if not exist .\config\consul mkdir .\config\consul
if not exist .\config\traefik\dynamic mkdir .\config\traefik\dynamic

REM Functions
:log
echo [%date% %time%] %~1
exit /b

:info
powershell -Command "Write-Host 'ℹ %~1' -ForegroundColor Blue"
exit /b

:success
powershell -Command "Write-Host '✓ %~1' -ForegroundColor Green"
exit /b

:warning
powershell -Command "Write-Host '⚠ %~1' -ForegroundColor Yellow"
exit /b

:error
powershell -Command "Write-Host '✗ %~1' -ForegroundColor Red"
exit /b

:check_prerequisites
call :info "Checking prerequisites..."

where docker >nul 2>nul
if errorlevel 1 (
    call :error "Docker is not installed"
    exit /b 1
)

where docker-compose >nul 2>nul
if errorlevel 1 (
    call :error "Docker Compose is not installed"
    exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
    call :error "Docker daemon is not running"
    exit /b 1
)

call :success "All prerequisites met"
exit /b

:setup_environment
call :info "Setting up environment variables..."

if not exist .env (
    echo # Claude Code Dev Stack V3.6.9 Environment Variables > .env
    echo. >> .env
    echo # Database Configuration >> .env
    echo POSTGRES_PASSWORD=claude_dev_db_secure_%random% >> .env
    echo REDIS_PASSWORD=claude_redis_secure_%random% >> .env
    echo. >> .env
    echo # Monitoring Configuration >> .env
    echo GRAFANA_PASSWORD=admin_%random% >> .env
    echo PROMETHEUS_RETENTION=30d >> .env
    echo. >> .env
    echo # External Services >> .env
    echo NGROK_AUTHTOKEN= >> .env
    echo NGROK_SUBDOMAIN= >> .env
    echo MCP_GITHUB_TOKEN= >> .env
    echo. >> .env
    echo # Development >> .env
    echo NODE_ENV=development >> .env
    echo DEBUG=claude:* >> .env
    echo LOG_LEVEL=info >> .env
    echo. >> .env
    echo # Performance >> .env
    echo REDIS_MAXMEMORY=512mb >> .env
    echo POSTGRES_SHARED_BUFFERS=256MB >> .env
    echo POSTGRES_MAX_CONNECTIONS=200 >> .env
    
    call :success "Environment file created: .env"
) else (
    call :info "Environment file already exists"
)
exit /b

:start_services
set PROFILE=%~1
if "%PROFILE%"=="" (
    call :info "Starting services..."
    docker-compose up -d
) else (
    call :info "Starting services with profile: %PROFILE%..."
    docker-compose --profile %PROFILE% up -d
)

call :success "Services started"
call :show_status
exit /b

:stop_services
call :info "Stopping services..."
docker-compose stop
call :success "Services stopped"
exit /b

:restart_services
call :info "Restarting services..."
docker-compose restart
call :success "Services restarted"
call :show_status
exit /b

:show_status
call :info "Service Status:"
echo ===========================================
docker-compose ps
echo ===========================================
exit /b

:show_logs
set SERVICE=%~1
set LINES=%~2
if "%LINES%"=="" set LINES=100

if "%SERVICE%"=="" (
    docker-compose logs --tail=%LINES% -f
) else (
    docker-compose logs --tail=%LINES% -f %SERVICE%
)
exit /b

:dev_setup
call :info "Setting up development environment..."
call :setup_environment
call :start_services "dev-tools"

timeout /t 10 /nobreak >nul

docker-compose exec claude-dev-stack npm run setup 2>nul

call :success "Development environment ready"
call :info "Available services:"
echo   Main App: http://localhost:3000
echo   UI/PWA: http://localhost:5173
echo   API: http://localhost:3001
echo   Grafana: http://localhost:3030 (admin/admin)
echo   Prometheus: http://localhost:9090
echo   Traefik: http://localhost:8080
echo   Consul: http://localhost:8500
exit /b

:test_setup
call :info "Setting up testing environment..."
call :start_services "testing"

timeout /t 5 /nobreak >nul

call :success "Testing environment ready"
call :info "Run tests with:"
echo   Unit tests: docker-compose run --rm test-env npm run test:unit
echo   Integration: docker-compose run --rm test-env npm run test:integration
echo   E2E tests: docker-compose run --rm test-env npm run test:e2e
exit /b

:backup_data
call :info "Creating backup..."
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set backup_file=%BACKUP_DIR%\claude-stack-backup-%timestamp%.tar.gz

docker-compose stop postgres redis

tar -czf %backup_file% data\ config\ .env docker-compose.yml 2>nul

docker-compose start postgres redis

call :success "Backup created: %backup_file%"
exit /b

:health_check
call :info "Running comprehensive health check..."
docker-compose exec healthcheck /healthcheck.sh check
exit /b

:show_help
echo Claude Code Dev Stack V3.6.9 - Docker Management Script (Windows)
echo.
echo Usage: %0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   start [profile]     Start all services (optional profile)
echo   stop               Stop all services
echo   restart            Restart all services
echo   status             Show service status
echo   logs [service]     Show logs for all services or specific service
echo.
echo   dev-setup          Setup development environment
echo   test-setup         Setup testing environment
echo.
echo   backup             Create data backup
echo   health-check       Run comprehensive health check
echo.
echo   help               Show this help message
echo.
echo Profiles:
echo   dev-tools          Development tools container
echo   frontend-dev       Frontend development container
echo   backend-dev        Backend development container
echo   testing            Testing environment
echo   monitoring         Health monitoring
echo.
echo Examples:
echo   %0 start                    # Start all services
echo   %0 start dev-tools          # Start with development tools
echo   %0 logs postgres            # Show PostgreSQL logs
echo   %0 backup                   # Create backup
echo.
echo Environment variables can be configured in .env file.
exit /b

REM Main command handling
set COMMAND=%~1
if "%COMMAND%"=="" set COMMAND=help

if "%COMMAND%"=="start" (
    call :check_prerequisites
    if errorlevel 1 exit /b 1
    call :setup_environment
    call :start_services %~2
) else if "%COMMAND%"=="stop" (
    call :stop_services
) else if "%COMMAND%"=="restart" (
    call :restart_services
) else if "%COMMAND%"=="status" (
    call :show_status
) else if "%COMMAND%"=="logs" (
    call :show_logs %~2 %~3
) else if "%COMMAND%"=="dev-setup" (
    call :check_prerequisites
    if errorlevel 1 exit /b 1
    call :dev_setup
) else if "%COMMAND%"=="test-setup" (
    call :check_prerequisites
    if errorlevel 1 exit /b 1
    call :test_setup
) else if "%COMMAND%"=="backup" (
    call :backup_data
) else if "%COMMAND%"=="health-check" (
    call :health_check
) else (
    call :show_help
)

endlocal