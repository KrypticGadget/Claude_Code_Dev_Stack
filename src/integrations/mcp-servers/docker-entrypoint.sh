#!/bin/bash
# GitHub MCP Server Docker Entrypoint Script
set -e

# Default values
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-8081}
export LOG_LEVEL=${LOG_LEVEL:-"info"}

# Configuration directory
CONFIG_DIR="/app/config"
LOG_DIR="/app/logs"
DATA_DIR="/app/data"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$DATA_DIR"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Function to validate environment
validate_environment() {
    log "Validating environment configuration..."
    
    # Check required GitHub authentication
    if [[ -z "$GITHUB_TOKEN" ]] && [[ -z "$GITHUB_APP_ID" || -z "$GITHUB_APP_PRIVATE_KEY" ]]; then
        log "ERROR: GitHub authentication not configured!"
        log "Please set either:"
        log "  - GITHUB_TOKEN (for personal access token)"
        log "  - GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY (for GitHub App)"
        exit 1
    fi
    
    # Validate port
    if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
        log "ERROR: Invalid port number: $PORT"
        exit 1
    fi
    
    # Check Redis connection if configured
    if [[ -n "$REDIS_HOST" ]] && [[ "$REDIS_HOST" != "localhost" ]]; then
        log "Testing Redis connection to $REDIS_HOST:${REDIS_PORT:-6379}..."
        if command -v redis-cli >/dev/null 2>&1; then
            if ! timeout 5 redis-cli -h "$REDIS_HOST" -p "${REDIS_PORT:-6379}" ping >/dev/null 2>&1; then
                log "WARNING: Redis connection failed, falling back to in-memory cache"
            else
                log "Redis connection successful"
            fi
        else
            log "WARNING: redis-cli not available, cannot test Redis connection"
        fi
    fi
    
    log "Environment validation completed"
}

# Function to setup configuration
setup_configuration() {
    log "Setting up configuration..."
    
    # Create runtime configuration from template
    if [[ -f "$CONFIG_DIR/github_mcp_config.yml" ]]; then
        log "Using configuration file: $CONFIG_DIR/github_mcp_config.yml"
    else
        log "WARNING: Configuration file not found, using defaults"
    fi
    
    # Set up logging configuration
    export PYTHONPATH="/app:$PYTHONPATH"
    
    log "Configuration setup completed"
}

# Function to handle graceful shutdown
graceful_shutdown() {
    log "Received shutdown signal, gracefully stopping..."
    
    # Send SIGTERM to the main process
    if [[ -n "$MAIN_PID" ]]; then
        kill -TERM "$MAIN_PID" 2>/dev/null || true
        
        # Wait for graceful shutdown
        local count=0
        while kill -0 "$MAIN_PID" 2>/dev/null && [ $count -lt 30 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$MAIN_PID" 2>/dev/null; then
            log "Forcing shutdown..."
            kill -KILL "$MAIN_PID" 2>/dev/null || true
        fi
    fi
    
    log "Shutdown completed"
    exit 0
}

# Function to monitor process health
monitor_health() {
    local health_url="http://localhost:$PORT/health"
    local max_failures=3
    local failure_count=0
    
    log "Starting health monitoring..."
    
    while true; do
        sleep 30
        
        if curl -sf "$health_url" >/dev/null 2>&1; then
            failure_count=0
        else
            failure_count=$((failure_count + 1))
            log "Health check failed ($failure_count/$max_failures)"
            
            if [ $failure_count -ge $max_failures ]; then
                log "ERROR: Health checks failed $max_failures times, service appears unhealthy"
                # Could trigger alerts or restart logic here
            fi
        fi
    done
}

# Setup signal handlers
trap graceful_shutdown SIGTERM SIGINT

# Validate environment
validate_environment

# Setup configuration
setup_configuration

# Display startup information
log "Starting GitHub MCP Server..."
log "Configuration:"
log "  Host: $HOST"
log "  Port: $PORT"
log "  Log Level: $LOG_LEVEL"
log "  GitHub Auth: $([ -n "$GITHUB_TOKEN" ] && echo "Token" || echo "App")"
log "  Redis: ${REDIS_HOST:-"disabled"}"
log "  WebSocket Max Connections: ${WEBSOCKET_MAX_CONNECTIONS:-100}"

# Start health monitoring in background
if [[ "${ENABLE_HEALTH_MONITORING:-true}" == "true" ]]; then
    monitor_health &
    MONITOR_PID=$!
fi

# Check if we should run as a service manager or directly
if [[ "$1" == "service" ]]; then
    log "Starting in service management mode..."
    exec python github_mcp_service.py start --config "$CONFIG_DIR/github_mcp_config.yml" "${@:2}"
elif [[ "$1" == "python" ]] && [[ "$2" == "github_mcp_server.py" ]]; then
    # Direct server execution
    log "Starting server directly..."
    exec "$@" &
    MAIN_PID=$!
    wait $MAIN_PID
elif [[ "$#" -eq 0 ]] || [[ "$1" == "python" ]]; then
    # Default: start the server
    log "Starting GitHub MCP Server..."
    exec python github_mcp_server.py "$PORT" &
    MAIN_PID=$!
    wait $MAIN_PID
else
    # Custom command
    log "Executing custom command: $*"
    exec "$@"
fi