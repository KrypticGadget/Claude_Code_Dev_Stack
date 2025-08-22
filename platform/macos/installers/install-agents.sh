#!/bin/bash
# Simple Claude Code Agents Installer for macOS
# Just downloads agent files from GitHub to ~/.claude/agents

# Logging
LOG_FILE="$HOME/claude_agents.log"
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Claude Code Agents Installer"
log "============================="
log "Log file: $LOG_FILE"

# Setup paths
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
log "Target directory: $AGENTS_DIR"

# Create directories
log "Setting up directories..."
if [ ! -d "$CLAUDE_DIR" ]; then
    log "Creating $CLAUDE_DIR"
    mkdir -p "$CLAUDE_DIR"
fi
if [ ! -d "$AGENTS_DIR" ]; then
    log "Creating $AGENTS_DIR"
    mkdir -p "$AGENTS_DIR"
fi
log "Directory ready: $AGENTS_DIR"

# List of agent files (NO -agent suffix!)
AGENTS=(
    "api-integration-specialist.md"
    "backend-services.md"
    "business-analyst.md"
    "business-tech-alignment.md"
    "ceo-strategy.md"
    "database-architecture.md"
    "development-prompt.md"
    "devops-engineering.md"
    "financial-analyst.md"
    "frontend-architecture.md"
    "frontend-mockup.md"
    "integration-setup.md"
    "master-orchestrator.md"
    "middleware-specialist.md"
    "mobile-development.md"
    "performance-optimization.md"
    "production-frontend.md"
    "project-manager.md"
    "prompt-engineer.md"
    "quality-assurance.md"
    "script-automation.md"
    "security-architecture.md"
    "technical-cto.md"
    "technical-documentation.md"
    "technical-specifications.md"
    "testing-automation.md"
    "ui-ux-design.md"
    "usage-guide.md"
)

BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/agents"

log "Downloading ${#AGENTS[@]} agents..."
SUCCESS=0
FAILED=0
COUNT=0

for agent in "${AGENTS[@]}"; do
    COUNT=$((COUNT + 1))
    log "[$COUNT/${#AGENTS[@]}] Downloading: $agent"
    URL="$BASE_URL/$agent"
    DEST="$AGENTS_DIR/$agent"
    
    log "  URL: $URL"
    log "  Dest: $DEST"
    
    if curl -sL "$URL" -o "$DEST"; then
        FILE_SIZE=$(stat -f%z "$DEST" 2>/dev/null || echo "0")
        log "  Response size: $FILE_SIZE bytes"
        log "  SUCCESS"
        SUCCESS=$((SUCCESS + 1))
    else
        log "  ERROR: Failed to download"
        FAILED=$((FAILED + 1))
    fi
    
    sleep 0.2
done

log "Complete!"
log "Success: $SUCCESS"
if [ $FAILED -gt 0 ]; then
    log "Failed: $FAILED"
fi
log "Location: $AGENTS_DIR"
log "Agents installer finished"

# Return instead of exit to avoid killing terminal
return 0 2>/dev/null || true