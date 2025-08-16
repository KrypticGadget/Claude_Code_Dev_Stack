#!/bin/bash
set -euo pipefail

# ==============================================================================
# CLAUDE CODE DEV STACK V3.0 MASTER LAUNCH SYSTEM (BASH)
# ==============================================================================
#
# Single command to orchestrate all Claude Code Dev Stack v3.0 services
# Includes environment validation, virtual environment activation, core services,
# MCP servers, dashboard, browser, mobile interfaces, and terminal tools.
#
# Usage:
#   ./claude-start.sh [OPTIONS]
#
# Options:
#   -m, --mode MODE         Launch mode: full|core|web|mobile|debug (default: full)
#   -s, --skip-health       Skip health checks for faster startup
#   -l, --log-level LEVEL   Logging level: debug|info|warn|error (default: info)
#   -b, --auto-browser      Automatically open browser
#   -p, --port PORT         Custom port for main dashboard
#   --local-only           Run in local-only mode (no tunnels)
#   -h, --help             Show this help message
#
# ==============================================================================

# Global variables
declare -g MODE="full"
declare -g SKIP_HEALTH_CHECK=false
declare -g LOG_LEVEL="info"
declare -g AUTO_BROWSER=false
declare -g CUSTOM_PORT=""
declare -g LOCAL_ONLY=false
declare -ga PROCESS_LIST=()
declare -gA SERVICE_STATUS=()
declare -g START_TIME
declare -g SCRIPT_DIR
declare -g PROJECT_ROOT

START_TIME=$(date +%s)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors and formatting
declare -r RED='\033[0;31m'
declare -r GREEN='\033[0;32m'
declare -r YELLOW='\033[1;33m'
declare -r BLUE='\033[0;34m'
declare -r CYAN='\033[0;36m'
declare -r GRAY='\033[0;37m'
declare -r BOLD='\033[1m'
declare -r NC='\033[0m' # No Color

# ==============================================================================
# LOGGING AND OUTPUT FUNCTIONS
# ==============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%H:%M:%S.%3N')
    
    # Log level filtering
    local level_num
    case "$LOG_LEVEL" in
        debug) level_num=0 ;;
        info)  level_num=1 ;;
        warn)  level_num=2 ;;
        error) level_num=3 ;;
        *) level_num=1 ;;
    esac
    
    local msg_level_num
    case "$level" in
        DEBUG) msg_level_num=0; local prefix="🔍"; local color="$GRAY" ;;
        INFO)  msg_level_num=1; local prefix="ℹ️"; local color="$CYAN" ;;
        WARN)  msg_level_num=2; local prefix="⚠️"; local color="$YELLOW" ;;
        ERROR) msg_level_num=3; local prefix="❌"; local color="$RED" ;;
        SUCCESS) msg_level_num=1; local prefix="✅"; local color="$GREEN" ;;
        *) msg_level_num=1; local prefix=""; local color="$NC" ;;
    esac
    
    if [[ $msg_level_num -ge $level_num ]]; then
        echo -e "${color}[$timestamp] $prefix $message${NC}" >&2
    fi
}

banner() {
    local title="$1"
    local subtitle="${2:-}"
    local width=80
    local border
    border=$(printf '=%.0s' $(seq 1 $width))
    
    echo ""
    echo -e "${CYAN}$border${NC}"
    printf "${YELLOW}%*s${NC}\n" $(((${#title} + width) / 2)) "$title"
    if [[ -n "$subtitle" ]]; then
        printf "${GRAY}%*s${NC}\n" $(((${#subtitle} + width) / 2)) "$subtitle"
    fi
    echo -e "${CYAN}$border${NC}"
    echo ""
}

show_help() {
    cat << EOF
Claude Code Dev Stack v3.0 Master Launch System

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -m, --mode MODE         Launch mode: full|core|web|mobile|debug (default: full)
    -s, --skip-health       Skip health checks for faster startup
    -l, --log-level LEVEL   Logging level: debug|info|warn|error (default: info)
    -b, --auto-browser      Automatically open browser
    -p, --port PORT         Custom port for main dashboard
    --local-only           Run in local-only mode (no tunnels)
    -h, --help             Show this help message

MODES:
    full      Start all services (default)
    core      Start only core services and MCP servers
    web       Start only web application
    mobile    Start only mobile interface
    debug     Start core services with debug logging

EXAMPLES:
    $0                                  # Start all services
    $0 -m core -l debug                # Core services with debug logging
    $0 -m web -b -p 3001               # Web app on port 3001, auto-open browser
    $0 -m mobile --local-only          # Mobile interface, local only

EOF
}

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

check_command() {
    local cmd="$1"
    local install_hint="${2:-}"
    
    log "DEBUG" "Checking $cmd..."
    if command -v "$cmd" &> /dev/null; then
        local version
        case "$cmd" in
            python|python3) version=$($cmd --version 2>&1) ;;
            node) version=$($cmd --version 2>&1) ;;
            git) version=$($cmd --version 2>&1) ;;
            claude) version=$($cmd --version 2>&1 || echo "claude CLI available") ;;
            *) version="available" ;;
        esac
        log "SUCCESS" "$cmd: OK ($version)"
        return 0
    else
        log "ERROR" "$cmd: MISSING"
        if [[ -n "$install_hint" ]]; then
            log "WARN" "Install hint: $install_hint"
        fi
        return 1
    fi
}

find_available_port() {
    local start_port="${1:-3000}"
    local port="$start_port"
    
    while lsof -Pi ":$port" -sTCP:LISTEN -t &>/dev/null; do
        ((port++))
    done
    
    echo "$port"
}

wait_for_service() {
    local url="$1"
    local timeout="${2:-30}"
    local service_name="${3:-Service}"
    
    if [[ "$SKIP_HEALTH_CHECK" == true ]]; then
        log "DEBUG" "Skipping health check for $service_name"
        return 0
    fi
    
    log "DEBUG" "Waiting for $service_name to be ready at $url..."
    local start_time
    start_time=$(date +%s)
    
    while true; do
        local current_time
        current_time=$(date +%s)
        if (( current_time - start_time >= timeout )); then
            log "WARN" "$service_name health check timeout"
            return 1
        fi
        
        if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200"; then
            log "SUCCESS" "$service_name is ready! ($url)"
            return 0
        fi
        
        sleep 0.5
    done
}

start_service() {
    local name="$1"
    local command="$2"
    local working_dir="${3:-$PWD}"
    local health_url="${4:-}"
    local timeout="${5:-30}"
    
    log "INFO" "Starting $name..."
    
    # Create log directory
    mkdir -p "$PROJECT_ROOT/logs"
    local log_file="$PROJECT_ROOT/logs/${name,,}.log"
    log_file="${log_file// /_}"  # Replace spaces with underscores
    
    # Start the service in background
    (
        cd "$working_dir"
        eval "$command" > "$log_file" 2>&1 &
        echo $! > "${log_file}.pid"
    )
    
    # Get the process ID
    sleep 1
    local pid_file="${log_file}.pid"
    if [[ -f "$pid_file" ]]; then
        local pid
        pid=$(cat "$pid_file")
        PROCESS_LIST+=("$pid")
        
        # Health check
        if [[ -n "$health_url" ]]; then
            if wait_for_service "$health_url" "$timeout" "$name"; then
                SERVICE_STATUS["$name"]="Running"
                log "SUCCESS" "$name started successfully (PID: $pid)"
                return 0
            else
                SERVICE_STATUS["$name"]="Timeout"
                return 1
            fi
        else
            # Simple process check
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                SERVICE_STATUS["$name"]="Running"
                log "SUCCESS" "$name started successfully (PID: $pid)"
                return 0
            else
                SERVICE_STATUS["$name"]="Failed"
                log "ERROR" "$name failed to start"
                return 1
            fi
        fi
    else
        SERVICE_STATUS["$name"]="Failed"
        log "ERROR" "Failed to start $name - no PID file"
        return 1
    fi
}

# ==============================================================================
# ENVIRONMENT VALIDATION
# ==============================================================================

validate_environment() {
    banner "ENVIRONMENT VALIDATION" "Checking prerequisites and dependencies"
    
    local all_good=true
    
    # Check shell
    log "INFO" "Shell: $SHELL"
    log "INFO" "OS: $(uname -s) $(uname -r)"
    
    # Check essential commands
    check_command "python3" "Install Python 3.8+ from python.org" || all_good=false
    check_command "node" "Install Node.js from nodejs.org" || all_good=false
    check_command "git" "Install Git from git-scm.com" || all_good=false
    check_command "curl" "Install curl (usually pre-installed)" || all_good=false
    
    # Check optional but recommended commands
    check_command "claude" "Install Claude CLI from claude.ai" || log "WARN" "Claude CLI not found - MCP features may not work"
    
    # Check project structure
    local required_dirs=(
        "Claude_Code_Dev_Stack_v3"
        ".claude-example"
        "Claude_Code_Dev_Stack_v3/apps/web"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$PROJECT_ROOT/$dir" ]]; then
            log "SUCCESS" "Directory: $dir"
        else
            log "ERROR" "Missing directory: $dir"
            all_good=false
        fi
    done
    
    if [[ "$all_good" != true ]]; then
        log "ERROR" "Environment validation failed! Please fix the issues above."
        exit 1
    fi
    
    log "SUCCESS" "Environment validation passed!"
}

# ==============================================================================
# VIRTUAL ENVIRONMENT SETUP
# ==============================================================================

setup_virtual_environments() {
    banner "VIRTUAL ENVIRONMENT SETUP" "Preparing Python and Node.js environments"
    
    # Python virtual environment
    local python_venv="$PROJECT_ROOT/.claude-example/mobile/.venv"
    if [[ ! -d "$python_venv" ]]; then
        log "INFO" "Creating Python virtual environment..."
        python3 -m venv "$python_venv"
        if [[ $? -ne 0 ]]; then
            log "ERROR" "Failed to create Python virtual environment"
            exit 1
        fi
    fi
    
    # Activate Python virtual environment and install dependencies
    local venv_python="$python_venv/bin/python"
    local venv_pip="$python_venv/bin/pip"
    
    log "INFO" "Installing Python dependencies..."
    "$venv_pip" install --upgrade pip --quiet
    
    local python_packages=(
        "flask>=2.3.0"
        "flask-socketio>=5.3.0"
        "flask-cors>=2.0.0"
        "psutil>=5.9.0"
        "GitPython>=3.1.0"
        "watchdog>=3.0.0"
        "qrcode[pil]>=7.4.0"
        "requests>=2.31.0"
    )
    
    for package in "${python_packages[@]}"; do
        log "DEBUG" "Installing $package..."
        "$venv_pip" install "$package" --quiet --disable-pip-version-check
    done
    
    # Node.js dependencies for web app
    if [[ -f "$PROJECT_ROOT/Claude_Code_Dev_Stack_v3/apps/web/package.json" ]]; then
        log "INFO" "Installing Node.js dependencies..."
        (
            cd "$PROJECT_ROOT/Claude_Code_Dev_Stack_v3/apps/web"
            npm install --silent
        )
        if [[ $? -ne 0 ]]; then
            log "WARN" "Failed to install Node.js dependencies"
        fi
    fi
    
    log "SUCCESS" "Virtual environments ready!"
}

# ==============================================================================
# SERVICE STARTUP FUNCTIONS
# ==============================================================================

start_core_services() {
    banner "CORE SERVICES" "Starting essential Claude Code services"
    
    if [[ "$MODE" == "full" || "$MODE" == "core" ]]; then
        local dashboard_port
        dashboard_port="${CUSTOM_PORT:-$(find_available_port 8080)}"
        local venv_python="$PROJECT_ROOT/.claude-example/mobile/.venv/bin/python"
        
        start_service "Real-time Dashboard" \
            "$venv_python $PROJECT_ROOT/.claude-example/dashboard/realtime_dashboard.py --port $dashboard_port --host 0.0.0.0" \
            "$PROJECT_ROOT" \
            "http://localhost:$dashboard_port"
        
        log "INFO" "Dashboard available at: http://localhost:$dashboard_port"
    fi
}

start_mcp_servers() {
    banner "MCP SERVERS" "Initializing Model Context Protocol servers"
    
    log "INFO" "Checking MCP server configuration..."
    
    # Check if Claude CLI is available
    if command -v claude &> /dev/null; then
        # Check MCP status
        local mcp_status
        mcp_status=$(claude mcp list 2>&1 || echo "No MCP servers configured")
        log "DEBUG" "MCP servers status: $mcp_status"
        
        # Note: MCP servers are managed by Claude CLI, not directly started here
        log "SUCCESS" "MCP servers configured"
    else
        log "WARN" "Claude CLI not found, skipping MCP server setup"
    fi
}

start_web_application() {
    banner "WEB APPLICATION" "Starting React PWA and development server"
    
    if [[ "$MODE" != "full" && "$MODE" != "web" ]]; then
        log "INFO" "Skipping web application (mode: $MODE)"
        return
    fi
    
    local web_port
    web_port=$(find_available_port 3000)
    
    start_service "Web Application" \
        "npm run dev -- --port $web_port --host 0.0.0.0" \
        "$PROJECT_ROOT/Claude_Code_Dev_Stack_v3/apps/web" \
        "http://localhost:$web_port"
    
    if [[ "${SERVICE_STATUS["Web Application"]}" == "Running" ]]; then
        log "INFO" "Web application available at: http://localhost:$web_port"
        
        # Auto-open browser if requested
        if [[ "$AUTO_BROWSER" == true ]]; then
            sleep 3
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:$web_port" &
            elif command -v open &> /dev/null; then
                open "http://localhost:$web_port" &
            else
                log "WARN" "Cannot auto-open browser on this system"
            fi
        fi
    fi
}

start_mobile_interface() {
    banner "MOBILE INTERFACE" "Setting up mobile access and QR codes"
    
    if [[ "$MODE" != "full" && "$MODE" != "mobile" ]]; then
        log "INFO" "Skipping mobile interface (mode: $MODE)"
        return
    fi
    
    local venv_python="$PROJECT_ROOT/.claude-example/mobile/.venv/bin/python"
    local mobile_port
    mobile_port=$(find_available_port 8080)
    
    local mobile_args="--port $mobile_port"
    if [[ "$LOCAL_ONLY" == true ]]; then
        mobile_args="$mobile_args --local-only"
    fi
    
    start_service "Mobile Interface" \
        "$venv_python $PROJECT_ROOT/.claude-example/mobile/launch_mobile.py $mobile_args" \
        "$PROJECT_ROOT" \
        "http://localhost:$mobile_port"
    
    if [[ "${SERVICE_STATUS["Mobile Interface"]}" == "Running" ]]; then
        log "INFO" "Mobile interface available at: http://localhost:$mobile_port"
        log "INFO" "QR code access at: http://localhost:5555"
    fi
}

start_terminal_tools() {
    banner "TERMINAL TOOLS" "Initializing terminal access and utilities"
    
    # Start ttyd terminal server if available
    if command -v ttyd &> /dev/null; then
        local ttyd_port
        ttyd_port=$(find_available_port 7681)
        
        start_service "Terminal Server" \
            "ttyd -p $ttyd_port bash" \
            "$PROJECT_ROOT" \
            "http://localhost:$ttyd_port"
        
        if [[ "${SERVICE_STATUS["Terminal Server"]}" == "Running" ]]; then
            log "INFO" "Terminal server available at: http://localhost:$ttyd_port"
        fi
    else
        log "WARN" "ttyd not found, terminal server not available"
        log "INFO" "Install ttyd for web-based terminal access"
    fi
}

# ==============================================================================
# MONITORING AND STATUS
# ==============================================================================

start_health_monitoring() {
    banner "HEALTH MONITORING" "Setting up service monitoring and recovery"
    
    # Create monitoring function that runs in background
    (
        while true; do
            sleep 30
            for pid in "${PROCESS_LIST[@]}"; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    log "WARN" "Process $pid has exited!"
                fi
            done
        done
    ) &
    
    local monitor_pid=$!
    PROCESS_LIST+=("$monitor_pid")
    
    log "SUCCESS" "Health monitoring started (PID: $monitor_pid)"
}

show_service_status() {
    banner "SERVICE STATUS" "Current status of all Claude Code services"
    
    local total_services=${#SERVICE_STATUS[@]}
    local running_services=0
    local failed_services=0
    
    for status in "${SERVICE_STATUS[@]}"; do
        if [[ "$status" == "Running" ]]; then
            ((running_services++))
        elif [[ "$status" == "Failed" ]]; then
            ((failed_services++))
        fi
    done
    
    echo -e "${CYAN}📊 Service Summary:${NC}"
    echo -e "   Total Services: $total_services"
    echo -e "   ${GREEN}Running: $running_services${NC}"
    echo -e "   ${RED}Failed: $failed_services${NC}"
    echo ""
    
    echo -e "${CYAN}📋 Detailed Status:${NC}"
    for service in "${!SERVICE_STATUS[@]}"; do
        local status="${SERVICE_STATUS[$service]}"
        local color icon
        case "$status" in
            "Running") color="$GREEN"; icon="✅" ;;
            "Failed") color="$RED"; icon="❌" ;;
            "Timeout") color="$YELLOW"; icon="⏰" ;;
            *) color="$GRAY"; icon="❓" ;;
        esac
        echo -e "   ${color}$icon $service: $status${NC}"
    done
    
    echo ""
    local uptime
    uptime=$(($(date +%s) - START_TIME))
    printf "${CYAN}⏱️  Uptime: %02d:%02d:%02d${NC}\n" $((uptime/3600)) $((uptime%3600/60)) $((uptime%60))
}

show_access_urls() {
    banner "ACCESS POINTS" "Available URLs and interfaces"
    
    local urls=()
    
    # Collect available URLs based on running services
    for service in "${!SERVICE_STATUS[@]}"; do
        if [[ "${SERVICE_STATUS[$service]}" == "Running" ]]; then
            case "$service" in
                "Real-time Dashboard") urls+=("🖥️  Dashboard: http://localhost:8080") ;;
                "Web Application") urls+=("🌐 Web App: http://localhost:3000") ;;
                "Mobile Interface") urls+=("📱 Mobile: http://localhost:8080") ;;
                "Terminal Server") urls+=("💻 Terminal: http://localhost:7681") ;;
            esac
        fi
    done
    
    if [[ ${#urls[@]} -eq 0 ]]; then
        echo -e "${RED}❌ No services are currently running${NC}"
    else
        for url in "${urls[@]}"; do
            echo -e "   ${GREEN}$url${NC}"
        done
    fi
    
    echo ""
    echo -e "${CYAN}🔧 Control Commands:${NC}"
    echo -e "   ${GRAY}Ctrl+C: Stop all services${NC}"
    echo -e "   ${GRAY}$0 -m debug: Debug mode${NC}"
}

# ==============================================================================
# CLEANUP AND SHUTDOWN
# ==============================================================================

cleanup() {
    banner "SHUTDOWN" "Stopping all Claude Code services"
    
    for pid in "${PROCESS_LIST[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            log "INFO" "Stopping process $pid"
            kill "$pid" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    # Clean up PID files
    rm -f "$PROJECT_ROOT/logs/"*.pid 2>/dev/null || true
    
    log "SUCCESS" "All services stopped"
}

# Set up trap for cleanup on exit
trap cleanup EXIT INT TERM

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                MODE="$2"
                shift 2
                ;;
            -s|--skip-health)
                SKIP_HEALTH_CHECK=true
                shift
                ;;
            -l|--log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            -b|--auto-browser)
                AUTO_BROWSER=true
                shift
                ;;
            -p|--port)
                CUSTOM_PORT="$2"
                shift 2
                ;;
            --local-only)
                LOCAL_ONLY=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate mode
    case "$MODE" in
        full|core|web|mobile|debug) ;;
        *)
            log "ERROR" "Invalid mode: $MODE"
            show_help
            exit 1
            ;;
    esac
    
    # Validate log level
    case "$LOG_LEVEL" in
        debug|info|warn|error) ;;
        *)
            log "ERROR" "Invalid log level: $LOG_LEVEL"
            show_help
            exit 1
            ;;
    esac
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main() {
    # Show banner
    banner "CLAUDE CODE DEV STACK V3.0" "Master Launch System - Mode: $MODE"
    
    # Environment validation
    validate_environment
    
    # Initialize virtual environments
    setup_virtual_environments
    
    # Start services based on mode
    case "$MODE" in
        "full")
            start_core_services
            start_mcp_servers
            start_web_application
            start_mobile_interface
            start_terminal_tools
            ;;
        "core")
            start_core_services
            start_mcp_servers
            ;;
        "web")
            start_web_application
            ;;
        "mobile")
            start_mobile_interface
            ;;
        "debug")
            LOG_LEVEL="debug"
            start_core_services
            start_terminal_tools
            ;;
    esac
    
    # Start health monitoring
    start_health_monitoring
    
    # Show status
    sleep 3
    show_service_status
    show_access_urls
    
    # Keep running and monitor
    log "SUCCESS" "Claude Code Dev Stack v3.0 is running! Press Ctrl+C to stop."
    
    # Monitoring loop
    while true; do
        sleep 10
        
        # Quick health check
        local dead_processes=0
        for pid in "${PROCESS_LIST[@]}"; do
            if ! kill -0 "$pid" 2>/dev/null; then
                ((dead_processes++))
            fi
        done
        
        if [[ $dead_processes -gt 0 ]]; then
            log "WARN" "$dead_processes service(s) have stopped"
            show_service_status
        fi
    done
}

# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_arguments "$@"
    main
fi