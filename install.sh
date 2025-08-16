#!/bin/bash
#
# Claude Code Dev Stack v3.0 - One-Line Bash Installer  
# Cross-platform installer for Linux and macOS
#
# Usage: curl -fsSL https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.sh | bash
#        or: wget -qO- https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.sh | bash
#
# Features:
# - Automatically detects OS and installs dependencies
# - Creates isolated virtual environments
# - Clones from GitHub and sets up complete stack
# - Validates installation with comprehensive health checks
# - Provides detailed error reporting and recovery options
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script metadata
readonly SCRIPT_VERSION="3.0.0"
readonly START_TIME=$(date +%s)
readonly LOG_FILE="/tmp/claude-stack-install-$(date +%Y%m%d-%H%M%S).log"
readonly INSTALL_DIR="${INSTALL_DIR:-$HOME/Claude_Code_Dev_Stack_v3}"
readonly GITHUB_REPO="${GITHUB_REPO:-yourusername/Claude_Code_Dev_Stack_v3}"
readonly BRANCH="${BRANCH:-main}"

# Counters
ERROR_COUNT=0
WARNING_COUNT=0

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color

# Logging functions
log_message() {
    local level="$1"
    local message="$2"
    local color="$3"
    local prefix="$4"
    
    local timestamp=$(date "+%H:%M:%S")
    local full_message="[$timestamp] $prefix$message"
    
    # Log to file
    echo "$full_message" >> "$LOG_FILE"
    
    # Console output with color
    if [[ -t 1 ]]; then
        echo -e "${color}${full_message}${NC}"
    else
        echo "$full_message"
    fi
}

log_success() { log_message "SUCCESS" "$1" "$GREEN" "✅ "; }
log_info() { log_message "INFO" "$1" "$CYAN" "ℹ️  "; }
log_warning() { log_message "WARNING" "$1" "$YELLOW" "⚠️  "; ((WARNING_COUNT++)); }
log_error() { log_message "ERROR" "$1" "$RED" "❌ "; ((ERROR_COUNT++)); }
log_progress() { log_message "PROGRESS" "$1" "$MAGENTA" "🔄 "; }

# Error handling
handle_error() {
    local line_number="$1"
    local error_code="$2"
    local command="$BASH_COMMAND"
    
    log_error "Command failed at line $line_number: $command (exit code: $error_code)"
    log_error "Installation failed. Check log: $LOG_FILE"
    
    # Cleanup on error
    cleanup_on_error
    exit 1
}

trap 'handle_error $LINENO $? "$BASH_COMMAND"' ERR

cleanup_on_error() {
    log_info "Performing cleanup after error..."
    
    # Stop any background processes
    if [[ -n "${WEB_PID:-}" ]]; then kill "$WEB_PID" 2>/dev/null || true; fi
    if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" 2>/dev/null || true; fi
    if [[ -n "${DASHBOARD_PID:-}" ]]; then kill "$DASHBOARD_PID" 2>/dev/null || true; fi
    
    log_info "Cleanup completed"
}

# OS Detection
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "$ID"
    elif [[ -f /etc/redhat-release ]]; then
        echo "rhel"
    elif [[ -f /etc/debian_version ]]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Dependency management
check_command() {
    command -v "$1" >/dev/null 2>&1
}

install_dependencies() {
    local os=$(detect_os)
    local distro=$(detect_distro)
    
    log_progress "Checking system dependencies..."
    
    # Define dependencies with install commands
    declare -A deps=(
        ["git"]="Git version control"
        ["python3"]="Python 3.8+"
        ["pip3"]="Python package manager"
        ["node"]="Node.js runtime"
        ["npm"]="Node.js package manager"
    )
    
    declare -A optional_deps=(
        ["docker"]="Docker containerization"
        ["curl"]="HTTP client"
        ["wget"]="File downloader"
    )
    
    # Check required dependencies
    local missing_deps=()
    for dep in "${!deps[@]}"; do
        if ! check_command "$dep"; then
            missing_deps+=("$dep")
            log_error "$dep is not installed - ${deps[$dep]}"
        else
            log_success "$dep is installed - ${deps[$dep]}"
        fi
    done
    
    # Check optional dependencies
    for dep in "${!optional_deps[@]}"; do
        if ! check_command "$dep"; then
            log_warning "$dep is not installed (optional) - ${optional_deps[$dep]}"
        else
            log_success "$dep is installed - ${optional_deps[$dep]}"
        fi
    done
    
    # Install missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_info "Missing dependencies found: ${missing_deps[*]}"
        
        # Ask for permission to install
        if [[ -t 0 ]]; then  # Interactive terminal
            read -p "Would you like to auto-install missing dependencies? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_error "Please install missing dependencies manually and re-run installer"
                exit 1
            fi
        fi
        
        install_system_dependencies "$os" "$distro" "${missing_deps[@]}"
    fi
}

install_system_dependencies() {
    local os="$1"
    local distro="$2"
    shift 2
    local deps=("$@")
    
    log_progress "Installing system dependencies..."
    
    case "$os" in
        "linux")
            case "$distro" in
                "ubuntu"|"debian")
                    sudo apt-get update
                    for dep in "${deps[@]}"; do
                        case "$dep" in
                            "python3") sudo apt-get install -y python3 python3-pip python3-venv ;;
                            "pip3") sudo apt-get install -y python3-pip ;;
                            "node") 
                                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                                sudo apt-get install -y nodejs
                                ;;
                            "npm") sudo apt-get install -y npm ;;
                            "git") sudo apt-get install -y git ;;
                            "docker") 
                                curl -fsSL https://get.docker.com | sh
                                sudo usermod -aG docker "$USER"
                                ;;
                            "curl") sudo apt-get install -y curl ;;
                            "wget") sudo apt-get install -y wget ;;
                        esac
                    done
                    ;;
                "rhel"|"centos"|"fedora")
                    if check_command "dnf"; then
                        PKG_MGR="dnf"
                    else
                        PKG_MGR="yum"
                    fi
                    
                    for dep in "${deps[@]}"; do
                        case "$dep" in
                            "python3") sudo $PKG_MGR install -y python3 python3-pip ;;
                            "pip3") sudo $PKG_MGR install -y python3-pip ;;
                            "node") 
                                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                                sudo $PKG_MGR install -y nodejs
                                ;;
                            "npm") sudo $PKG_MGR install -y npm ;;
                            "git") sudo $PKG_MGR install -y git ;;
                            "docker") 
                                curl -fsSL https://get.docker.com | sh
                                sudo usermod -aG docker "$USER"
                                ;;
                            "curl") sudo $PKG_MGR install -y curl ;;
                            "wget") sudo $PKG_MGR install -y wget ;;
                        esac
                    done
                    ;;
                "arch")
                    for dep in "${deps[@]}"; do
                        case "$dep" in
                            "python3") sudo pacman -S --noconfirm python python-pip ;;
                            "pip3") sudo pacman -S --noconfirm python-pip ;;
                            "node") sudo pacman -S --noconfirm nodejs npm ;;
                            "npm") sudo pacman -S --noconfirm npm ;;
                            "git") sudo pacman -S --noconfirm git ;;
                            "docker") 
                                sudo pacman -S --noconfirm docker
                                sudo usermod -aG docker "$USER"
                                ;;
                            "curl") sudo pacman -S --noconfirm curl ;;
                            "wget") sudo pacman -S --noconfirm wget ;;
                        esac
                    done
                    ;;
            esac
            ;;
        "macos")
            # Check for Homebrew
            if ! check_command "brew"; then
                log_progress "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            for dep in "${deps[@]}"; do
                case "$dep" in
                    "python3") brew install python@3.11 ;;
                    "pip3") brew install python@3.11 ;;  # pip comes with python
                    "node") brew install node ;;
                    "npm") brew install node ;;  # npm comes with node
                    "git") 
                        if ! check_command "git"; then
                            xcode-select --install 2>/dev/null || brew install git
                        fi
                        ;;
                    "docker") brew install --cask docker ;;
                    "curl") brew install curl ;;
                    "wget") brew install wget ;;
                esac
            done
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Repository management
clone_repository() {
    log_progress "Cloning repository from GitHub..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        log_warning "Installation directory already exists: $INSTALL_DIR"
        if [[ -t 0 ]]; then  # Interactive terminal
            read -p "Remove existing directory? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$INSTALL_DIR"
                log_info "Existing directory removed"
            else
                log_error "Installation cancelled"
                exit 1
            fi
        else
            # Non-interactive: backup existing directory
            local backup_dir="${INSTALL_DIR}.backup.$(date +%s)"
            mv "$INSTALL_DIR" "$backup_dir"
            log_info "Existing directory backed up to: $backup_dir"
        fi
    fi
    
    # Clone repository
    git clone --depth 1 --branch "$BRANCH" "https://github.com/$GITHUB_REPO.git" "$INSTALL_DIR"
    log_success "Repository cloned successfully"
    
    # Navigate to installation directory
    cd "$INSTALL_DIR"
    log_info "Changed directory to: $INSTALL_DIR"
}

# Python environment setup
setup_python_environment() {
    log_progress "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    log_success "Python virtual environment created"
    
    # Activate virtual environment
    source venv/bin/activate
    log_info "Python virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    log_success "pip upgraded"
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log_progress "Installing Python dependencies from requirements.txt..."
        pip install -r requirements.txt
        log_success "Python dependencies installed from requirements.txt"
    elif [[ -f "setup_environment.py" ]]; then
        log_progress "Running setup_environment.py..."
        python setup_environment.py
        log_success "Python environment setup completed"
    else
        log_warning "No requirements.txt or setup_environment.py found"
        
        # Install core dependencies manually
        log_progress "Installing core Python dependencies..."
        pip install flask flask-cors flask-socketio requests pyyaml python-dotenv
        log_success "Core Python dependencies installed"
    fi
}

# Node.js environment setup
setup_nodejs_environment() {
    log_progress "Setting up Node.js environment..."
    
    if [[ -d "apps/web" && -f "apps/web/package.json" ]]; then
        cd apps/web
        
        # Install Node.js dependencies
        if npm ci >/dev/null 2>&1; then
            log_success "Node.js dependencies installed with npm ci"
        else
            log_warning "npm ci failed, trying npm install..."
            npm install
            log_success "Node.js dependencies installed with npm install"
        fi
        
        # Build application
        if npm run build >/dev/null 2>&1; then
            log_success "Web application built successfully"
        else
            log_warning "Build failed, will use development mode"
        fi
        
        cd ../..
    else
        log_warning "No web application found (apps/web/package.json missing)"
    fi
}

# Service configuration
configure_services() {
    log_progress "Configuring services..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Claude Code Dev Stack v3.0 Configuration
# Generated by installer on $(date)

# Core Settings
CLAUDE_API_KEY=your_api_key_here
NODE_ENV=development
PYTHON_ENV=development

# Service Ports
WEB_PORT=3000
API_PORT=8000
MOBILE_PORT=8080
DASHBOARD_PORT=8081
MCP_PORT=8085

# Database (if using)
DATABASE_URL=sqlite:///./claude_stack.db

# Audio & Voice
ENABLE_AUDIO=true
AUDIO_SAMPLE_RATE=44100

# Security
SESSION_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Debug
DEBUG=false
VERBOSE_LOGGING=false
EOF
        log_success "Environment configuration created (.env)"
    else
        log_info "Environment configuration already exists (.env)"
    fi
    
    # Create necessary directories
    mkdir -p .claude/{agents,hooks,status,logs,temp} data logs
    log_success "Service directories created"
    
    # Initialize services
    source venv/bin/activate
    python3 -c "
import sys
from pathlib import Path

# Verify Python environment
try:
    import flask, requests
    print('Core Python modules available')
except ImportError as e:
    print(f'Missing Python modules: {e}')

# Create status files
status_dir = Path('.claude/status')
status_dir.mkdir(parents=True, exist_ok=True)

status_files = {
    'agent-count': '0/28',
    'task-count': '0/0',
    'hook-count': '0/28',
    'audio-status': '🔇 Silent'
}

for filename, content in status_files.items():
    (status_dir / filename).write_text(content)

print('Service initialization completed')
"
    log_success "Services initialized"
}

# Installation validation
validate_installation() {
    log_progress "Validating installation..."
    
    local tests=(
        "python_env:Python Environment:test -d venv"
        "python_deps:Python Dependencies:source venv/bin/activate && python -c 'import flask, requests' 2>/dev/null"
        "nodejs_deps:Node.js Dependencies:test -d apps/web/node_modules"
        "config_files:Configuration Files:test -f .env && test -f requirements.txt"
        "service_dirs:Service Directories:test -d .claude && test -d logs"
        "status_files:Status Files:test -f .claude/status/agent-count"
    )
    
    local passed=0
    local total=${#tests[@]}
    
    for test in "${tests[@]}"; do
        IFS=':' read -r test_id test_name test_command <<< "$test"
        
        if eval "$test_command" >/dev/null 2>&1; then
            log_success "$test_name: PASS"
            ((passed++))
        else
            log_error "$test_name: FAIL"
        fi
    done
    
    log_info "Validation Results: $passed/$total tests passed"
    
    if [[ $passed -eq $total ]]; then
        log_success "All validation tests passed!"
        return 0
    elif [[ $passed -ge $((total * 80 / 100)) ]]; then
        log_warning "Most tests passed, installation should work with minor issues"
        return 0
    else
        log_error "Many tests failed, installation may have serious issues"
        return 1
    fi
}

# Launcher script creation
create_launcher_scripts() {
    log_progress "Creating launcher scripts..."
    
    # Create start.sh script
    cat > start.sh << 'EOF'
#!/bin/bash
# Claude Code Dev Stack v3.0 Launcher

set -e

echo "Starting Claude Code Dev Stack v3.0..."
cd "$(dirname "$0")"

echo "Activating Python environment..."
source venv/bin/activate

echo "Starting services..."

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    if [[ -n "${WEB_PID:-}" ]]; then kill "$WEB_PID" 2>/dev/null || true; fi
    if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" 2>/dev/null || true; fi
    if [[ -n "${DASHBOARD_PID:-}" ]]; then kill "$DASHBOARD_PID" 2>/dev/null || true; fi
    echo "Services stopped"
    exit 0
}

trap cleanup INT TERM

# Start web app
if [[ -d "apps/web" ]]; then
    cd apps/web
    npm run dev &
    WEB_PID=$!
    echo "Started Web App (PID: $WEB_PID)"
    cd ../..
fi

# Start API server
if [[ -f "core/api/server.py" ]]; then
    python core/api/server.py &
    API_PID=$!
    echo "Started API Server (PID: $API_PID)"
fi

# Start dashboard
if [[ -f ".claude-example/dashboard/realtime_dashboard.py" ]]; then
    python .claude-example/dashboard/realtime_dashboard.py &
    DASHBOARD_PID=$!
    echo "Started Dashboard (PID: $DASHBOARD_PID)"
fi

echo ""
echo "Services started! URLs:"
echo "  📱 Mobile: http://localhost:8080"
echo "  🌐 Web App: http://localhost:3000"
echo "  📊 Dashboard: http://localhost:8081"
echo "  🔌 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for services
wait
EOF
    
    chmod +x start.sh
    log_success "Launcher script created (start.sh)"
    
    # Create quick launcher alias
    cat > run << 'EOF'
#!/bin/bash
exec ./start.sh "$@"
EOF
    chmod +x run
    log_success "Quick launcher created (run)"
}

# Installation summary
show_installation_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    log_info ""
    log_info "============================================="
    log_success "Claude Code Dev Stack v3.0 Installed!"
    log_info "============================================="
    log_info ""
    log_info "Installation Details:"
    log_info "  Location: $INSTALL_DIR"
    log_info "  Duration: ${minutes}m ${seconds}s"
    log_info "  Warnings: $WARNING_COUNT"
    log_info "  Errors: $ERROR_COUNT"
    log_info "  Log File: $LOG_FILE"
    log_info ""
    log_info "Quick Start Commands:"
    log_info "  cd $INSTALL_DIR"
    log_info "  ./start.sh    # Start all services"
    log_info "  ./run         # Quick launcher alias"
    log_info ""
    log_info "Service URLs:"
    log_info "  📱 Mobile: http://localhost:8080"
    log_info "  🌐 Web App: http://localhost:3000"
    log_info "  📊 Dashboard: http://localhost:8081"
    log_info "  🔌 API: http://localhost:8000"
    log_info ""
    log_info "Configuration:"
    log_info "  Edit .env file for API keys and settings"
    log_info "  Python env: venv/ (auto-activated in scripts)"
    log_info "  Node.js deps: apps/web/node_modules/"
    log_info ""
    log_info "Manual activation:"
    log_info "  source venv/bin/activate"
    log_info ""
    
    if [[ $ERROR_COUNT -eq 0 ]]; then
        log_success "Installation completed successfully! 🎉"
    elif [[ $ERROR_COUNT -le 2 ]]; then
        log_warning "Installation completed with minor issues. Check log file."
    else
        log_error "Installation completed with issues. Review errors in log file."
    fi
    
    log_info ""
    log_info "Next Steps:"
    log_info "1. cd $INSTALL_DIR"
    log_info "2. Add your CLAUDE_API_KEY to .env file"
    log_info "3. Run ./start.sh to start all services"
    log_info "4. Visit http://localhost:3000 to begin"
    log_info "5. Check documentation in docs/ folder"
    log_info ""
    log_info "Support: Check GitHub issues or README.md"
    log_info "============================================="
}

# Main installation function
main() {
    log_info "=== Claude Code Dev Stack v3.0 Installer ==="
    log_info "Install Path: $INSTALL_DIR"
    log_info "GitHub Repo: $GITHUB_REPO"
    log_info "Branch: $BRANCH"
    log_info "OS: $(detect_os)"
    log_info "Log File: $LOG_FILE"
    log_info ""
    
    # Step 1: Install system dependencies
    install_dependencies
    
    # Step 2: Clone repository
    clone_repository
    
    # Step 3: Setup Python environment
    setup_python_environment
    
    # Step 4: Setup Node.js environment
    setup_nodejs_environment
    
    # Step 5: Configure services
    configure_services
    
    # Step 6: Validate installation
    if ! validate_installation; then
        log_warning "Validation had issues, but continuing..."
    fi
    
    # Step 7: Create launcher scripts
    create_launcher_scripts
    
    # Step 8: Show summary
    show_installation_summary
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi