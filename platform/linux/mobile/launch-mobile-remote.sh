#!/bin/bash
# Claude Code V3+ Mobile Access Remote Launcher
# One-liner mobile access that downloads and runs from GitHub
# Usage: curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/mobile/launch-mobile-remote.sh | bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default parameters
NO_PHONE=false
NO_QR=false
PORT=8080
DEBUG=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-phone)
            NO_PHONE=true
            shift
            ;;
        --no-qr)
            NO_QR=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

function print_color() {
    echo -e "$1$2${NC}"
}

function test_python_installation() {
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1)
        print_color "$GREEN" "✅ Python found: $python_version"
        return 0
    elif command -v python &> /dev/null; then
        local python_version=$(python --version 2>&1)
        if [[ $python_version == *"Python 3"* ]]; then
            print_color "$GREEN" "✅ Python found: $python_version"
            return 0
        fi
    fi
    
    print_color "$RED" "❌ Python 3 not found. Please install Python 3.7+ from python.org"
    return 1
}

function install_python_packages() {
    print_color "$BLUE" "📦 Installing required Python packages..."
    
    local packages=("flask" "flask-socketio" "qrcode[pil]" "requests" "psutil")
    local python_cmd="python3"
    
    # Use python if python3 not available but python is Python 3
    if ! command -v python3 &> /dev/null && command -v python &> /dev/null; then
        local python_version=$(python --version 2>&1)
        if [[ $python_version == *"Python 3"* ]]; then
            python_cmd="python"
        fi
    fi
    
    for package in "${packages[@]}"; do
        print_color "$YELLOW" "Installing $package..."
        if ! $python_cmd -m pip install "$package" --quiet --upgrade; then
            print_color "$YELLOW" "⚠️  Warning: Failed to install $package"
        fi
    done
    
    print_color "$GREEN" "✅ Package installation complete"
}

function test_v3_installation() {
    local claude_dir="$HOME/.claude"
    
    if [[ ! -d "$claude_dir" ]]; then
        print_color "$RED" "❌ Claude Code V3+ not installed"
        print_color "$YELLOW" "Please run the installer first:"
        print_color "$BLUE" 'curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash'
        return 1
    fi
    
    # Check for key components
    local agents_dir="$claude_dir/agents"
    local hooks_dir="$claude_dir/hooks"
    local audio_dir="$claude_dir/audio"
    
    if [[ ! -d "$agents_dir" || ! -d "$hooks_dir" || ! -d "$audio_dir" ]]; then
        print_color "$RED" "❌ Incomplete V3+ installation detected"
        print_color "$YELLOW" "Please run the full installer:"
        print_color "$BLUE" 'curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers/install-all.sh | bash'
        return 1
    fi
    
    print_color "$GREEN" "✅ Claude Code V3+ installation verified"
    return 0
}

function download_mobile_components() {
    local claude_dir="$HOME/.claude"
    local mobile_dir="$claude_dir/mobile"
    local dashboard_dir="$claude_dir/dashboard"
    local tunnels_dir="$claude_dir/tunnels"
    
    # Create directories
    mkdir -p "$mobile_dir" "$dashboard_dir" "$tunnels_dir"
    
    print_color "$BLUE" "📥 Downloading mobile components from GitHub..."
    
    local base_url="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"
    
    # Mobile components
    local mobile_files=(
        "mobile/launch_mobile.py"
        "mobile/mobile_auth.py"
        "mobile/qr_generator.py"
        "mobile/README.md"
    )
    
    # Dashboard components
    local dashboard_files=(
        "dashboard/dashboard_server.py"
        "dashboard/requirements.txt"
        "dashboard/templates/dashboard.html"
    )
    
    # Tunnel components
    local tunnel_files=(
        "tunnels/tunnel_manager.py"
        "tunnels/setup_ngrok.py"
        "tunnels/setup_cloudflare.py"
    )
    
    local all_files=("${mobile_files[@]}" "${dashboard_files[@]}" "${tunnel_files[@]}")
    local downloaded_count=0
    
    for file in "${all_files[@]}"; do
        local url="$base_url/$file"
        local local_path="$claude_dir/$file"
        local local_dir=$(dirname "$local_path")
        
        # Ensure directory exists
        mkdir -p "$local_dir"
        
        print_color "$YELLOW" "  Downloading $file..."
        if curl -fsSL "$url" -o "$local_path"; then
            ((downloaded_count++))
        else
            print_color "$YELLOW" "⚠️  Warning: Failed to download $file"
        fi
    done
    
    # Ensure dashboard templates directory exists
    mkdir -p "$dashboard_dir/templates"
    
    print_color "$GREEN" "✅ Downloaded $downloaded_count mobile components"
    echo "$mobile_dir"
}

function start_mobile_access() {
    local mobile_dir="$1"
    local launch_script="$mobile_dir/launch_mobile.py"
    
    if [[ ! -f "$launch_script" ]]; then
        print_color "$RED" "❌ Mobile launcher not found at $launch_script"
        return 1
    fi
    
    print_color "$GREEN" "🚀 Starting Claude Code V3+ Mobile Access..."
    print_color "$BLUE" "$(printf '=%.0s' {1..60})"
    
    # Build arguments
    local args=()
    if [[ "$NO_PHONE" == true ]]; then
        args+=(--no-phone)
    fi
    if [[ "$NO_QR" == true ]]; then
        args+=(--no-qr)
    fi
    if [[ "$PORT" != "8080" ]]; then
        args+=(--port "$PORT")
    fi
    
    # Determine Python command
    local python_cmd="python3"
    if ! command -v python3 &> /dev/null && command -v python &> /dev/null; then
        local python_version=$(python --version 2>&1)
        if [[ $python_version == *"Python 3"* ]]; then
            python_cmd="python"
        fi
    fi
    
    # Change to mobile directory and start
    cd "$mobile_dir" || return 1
    
    if ! $python_cmd launch_mobile.py "${args[@]}"; then
        print_color "$RED" "❌ Error starting mobile access"
        return 1
    fi
    
    return 0
}

function show_header() {
    print_color "$BLUE" "🚀 Claude Code V3+ Mobile Access Remote Launcher"
    print_color "$BLUE" "================================================="
    print_color "$BLUE" "📱 Secure one-liner mobile access to your V3+ system"
    print_color "$BLUE" "🌐 Downloads components from GitHub automatically"
    print_color "$BLUE" "🔒 Enterprise-grade security with token authentication"
    print_color "$BLUE" "📊 Real-time monitoring dashboard for Samsung Galaxy S25 Edge"
    echo ""
}

function show_usage() {
    print_color "$YELLOW" "Usage Examples:"
    echo ""
    print_color "$YELLOW" "Basic Launch:"
    print_color "$YELLOW" "curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/mobile/launch-mobile-remote.sh | bash"
    echo ""
    print_color "$YELLOW" "Advanced Options:"
    print_color "$YELLOW" "# Download script first for options"
    print_color "$YELLOW" "curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/mobile/launch-mobile-remote.sh -o launch-mobile.sh"
    print_color "$YELLOW" "chmod +x launch-mobile.sh"
    echo ""
    print_color "$YELLOW" "# Run with options"
    print_color "$YELLOW" "./launch-mobile.sh --no-phone --port 9090"
    echo ""
    print_color "$YELLOW" "Parameters:"
    print_color "$YELLOW" "  --no-phone    : Don't send notifications to phone"
    print_color "$YELLOW" "  --no-qr       : Don't generate QR code"
    print_color "$YELLOW" "  --port <num>  : Custom dashboard port (default: 8080)"
    print_color "$YELLOW" "  --debug       : Enable debug mode"
}

# Main execution
main() {
    show_header
    
    # Check prerequisites
    if ! test_python_installation; then
        exit 1
    fi
    
    # Check V3+ installation
    if ! test_v3_installation; then
        exit 1
    fi
    
    # Install Python packages
    install_python_packages
    
    # Download mobile components
    local mobile_dir
    mobile_dir=$(download_mobile_components)
    
    if [[ -z "$mobile_dir" ]]; then
        print_color "$RED" "❌ Failed to download mobile components"
        exit 1
    fi
    
    # Start mobile access
    if ! start_mobile_access "$mobile_dir"; then
        print_color "$RED" "❌ Failed to start mobile access"
        exit 1
    fi
}

# Handle errors
set -e
trap 'print_color "$RED" "❌ Unexpected error occurred. Please try running the command again or check your internet connection."' ERR

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

# If we get here, everything worked
print_color "$GREEN" "✅ Mobile access launcher completed successfully!"