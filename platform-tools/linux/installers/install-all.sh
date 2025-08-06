#!/bin/bash
# Simple Claude Code Dev Stack Installer for Linux
# Downloads all components from GitHub to ~/.claude

# Setup logging
LOG_FILE="$HOME/claude_installer.log"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Claude Code Dev Stack Installer v2.1"
log "========================================="
log "Log file: $LOG_FILE"

# Base URLs
BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/linux/installers"

log "Installing 4 components:"
log "1. Agents (28 files)"
log "2. Commands (18 files)"
log "3. Hooks (13 files)"
log "4. MCP configs"

# Component installers
COMPONENTS=(
    "Agents:install-agents.sh"
    "Commands:install-commands.sh"
    "Hooks:install-hooks.sh"
    "MCPs:install-mcps.sh"
)

for component in "${COMPONENTS[@]}"; do
    IFS=':' read -r name script <<< "$component"
    
    log "----------------------------------------"
    log "Installing $name..."
    
    SCRIPT_URL="$BASE_URL/$script"
    log "Downloading from: $SCRIPT_URL"
    
    # Download and run the component installer
    log "Fetching script content..."
    TEMP_SCRIPT="/tmp/claude_$script"
    
    if curl -sL "$SCRIPT_URL" -o "$TEMP_SCRIPT"; then
        FILE_SIZE=$(stat -c%s "$TEMP_SCRIPT" 2>/dev/null || stat -f%z "$TEMP_SCRIPT" 2>/dev/null || echo "unknown")
        log "Script downloaded, size: $FILE_SIZE bytes"
        log "Executing $name installer..."
        
        chmod +x "$TEMP_SCRIPT"
        log "Running script..."
        
        # Run the script
        if bash "$TEMP_SCRIPT"; then
            log "Script completed successfully"
        else
            log "Script failed with exit code: $?"
        fi
        
        rm -f "$TEMP_SCRIPT"
    else
        log "ERROR: Failed to download $name installer"
    fi
    
    log ""
done

echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Files installed to: $HOME/.claude"
echo ""
echo "To use:"
echo "1. Open Claude Code"
echo "2. Type @ to see agents"
echo "3. Type / to see commands"
echo ""

# Don't use exit to avoid killing terminal when sourced
return 0 2>/dev/null || true