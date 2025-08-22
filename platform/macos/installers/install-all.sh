#!/bin/bash
# Simple Claude Code Dev Stack Installer for macOS
# Downloads all components from GitHub to ~/.claude

# Setup logging
LOG_FILE="$HOME/claude_installer.log"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Claude Code Dev Stack Installer V3.0+"
log "========================================="
log "Log file: $LOG_FILE"

# Base URLs
BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/macos/installers"

log "Installing 4 V3.0+ components:"
log "1. V3+ Agents (28 enhanced files with smart orchestration)"
log "2. V3+ Commands (20+ files with /orchestrate-demo)"
log "3. V3+ Hooks & Audio (28 hooks + 102 audio files with mobile sync)"
log "4. V3+ MCPs (Playwright, Web Search, GitHub, Obsidian)"

# Component installers
COMPONENTS=(
    "V3+ Agents:install-agents-mac.sh"
    "V3+ Commands:install-commands-mac.sh"
    "V3+ Hooks & Audio:install-hooks-mac.sh"
    "V3+ MCPs:install-mcps-mac.sh"
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
        FILE_SIZE=$(stat -f%z "$TEMP_SCRIPT" 2>/dev/null || echo "unknown")
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