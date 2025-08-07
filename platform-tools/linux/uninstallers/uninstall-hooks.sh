#!/bin/bash
# Enhanced Claude Code Hooks Uninstaller v2.1 for Linux
# Safely removes all hook components with backup

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         Claude Code Enhanced Hooks Uninstaller v2.1            ║
║           Safely Removes Hooks with Backup Option              ║
╚════════════════════════════════════════════════════════════════╝
EOF

# Configuration
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
AUDIO_DIR="$CLAUDE_DIR/audio"
LOGS_DIR="$CLAUDE_DIR/logs"
STATE_DIR="$CLAUDE_DIR/state"
BACKUPS_DIR="$CLAUDE_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Step 1: Check if hooks are installed
echo -e "\n${YELLOW}🔍 Checking installation...${NC}"

if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "  ${YELLOW}⚠ No hooks directory found at: $HOOKS_DIR${NC}"
    echo -e "  ${GRAY}Nothing to uninstall.${NC}"
    exit 0
fi

INSTALLED_HOOKS=$(find "$HOOKS_DIR" -name "*.py" -type f 2>/dev/null | wc -l)
AUDIO_FILES=0
if [ -d "$AUDIO_DIR" ]; then
    AUDIO_FILES=$(find "$AUDIO_DIR" -name "*.mp3" -type f 2>/dev/null | wc -l)
fi

echo -e "  ${CYAN}Found: $INSTALLED_HOOKS hooks${NC}"
echo -e "  ${CYAN}Found: $AUDIO_FILES audio files${NC}"

# Step 2: Confirm uninstallation
echo -e "\n${YELLOW}⚠ This will remove:${NC}"
echo -e "  ${WHITE}• All hook scripts in $HOOKS_DIR${NC}"
echo -e "  ${WHITE}• All audio files in $AUDIO_DIR${NC}"
echo -e "  ${WHITE}• Hook-related logs in $LOGS_DIR${NC}"
echo -e "  ${WHITE}• Session state in $STATE_DIR${NC}"

echo -n -e "\n${WHITE}Do you want to continue? (Y/N): ${NC}"
read -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "\n${GRAY}Uninstallation cancelled.${NC}"
    exit 0
fi

# Step 3: Create backup
echo -e "\n${YELLOW}💾 Creating backup...${NC}"

# Create backup directory
if [ ! -d "$BACKUPS_DIR" ]; then
    mkdir -p "$BACKUPS_DIR"
fi
BACKUP_PATH="$BACKUPS_DIR/uninstall_backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

# Backup hooks
if [ "$INSTALLED_HOOKS" -gt 0 ]; then
    HOOKS_BACKUP_DIR="$BACKUP_PATH/hooks"
    mkdir -p "$HOOKS_BACKUP_DIR"
    cp "$HOOKS_DIR"/*.py "$HOOKS_BACKUP_DIR" 2>/dev/null
    echo -e "  ${GREEN}✓ Backed up $INSTALLED_HOOKS hooks${NC}"
fi

# Backup audio files
if [ "$AUDIO_FILES" -gt 0 ]; then
    AUDIO_BACKUP_DIR="$BACKUP_PATH/audio"
    mkdir -p "$AUDIO_BACKUP_DIR"
    cp "$AUDIO_DIR"/*.mp3 "$AUDIO_BACKUP_DIR" 2>/dev/null
    echo -e "  ${GREEN}✓ Backed up $AUDIO_FILES audio files${NC}"
fi

# Backup settings.json
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    cp "$CLAUDE_DIR/settings.json" "$BACKUP_PATH/settings.json"
    echo -e "  ${GREEN}✓ Backed up settings.json${NC}"
fi

# Backup state if exists
if [ -d "$STATE_DIR" ]; then
    STATE_FILES=$(find "$STATE_DIR" -type f 2>/dev/null | wc -l)
    if [ "$STATE_FILES" -gt 0 ]; then
        STATE_BACKUP_DIR="$BACKUP_PATH/state"
        mkdir -p "$STATE_BACKUP_DIR"
        cp -r "$STATE_DIR"/* "$STATE_BACKUP_DIR" 2>/dev/null
        echo -e "  ${GREEN}✓ Backed up state files${NC}"
    fi
fi

echo -e "  ${CYAN}Backup location: $BACKUP_PATH${NC}"

# Step 4: Remove hook scripts
echo -e "\n${YELLOW}🗑️ Removing hooks...${NC}"

# List of all possible enhanced hooks
ALL_HOOKS=(
    "agent_mention_parser.py"
    "agent_orchestrator.py"
    "agent_orchestrator_integrated.py"
    "slash_command_router.py"
    "mcp_gateway.py"
    "mcp_gateway_enhanced.py"
    "mcp_initializer.py"
    "audio_player.py"
    "audio_notifier.py"
    "session_loader.py"
    "session_saver.py"
    "quality_gate.py"
    "model_tracker.py"
    "planning_trigger.py"
    "pre_command.py"
    "post_command.py"
    "pre_project.py"
    "post_project.py"
    "base_hook.py"
)

REMOVED_COUNT=0
for HOOK in "${ALL_HOOKS[@]}"; do
    HOOK_PATH="$HOOKS_DIR/$HOOK"
    if [ -f "$HOOK_PATH" ]; then
        rm -f "$HOOK_PATH"
        echo -e "  ${GREEN}✓ Removed: $HOOK${NC}"
        ((REMOVED_COUNT++))
    fi
done

echo -e "  ${CYAN}Removed: $REMOVED_COUNT hooks${NC}"

# Step 5: Remove audio files
echo -e "\n${YELLOW}🎵 Removing audio files...${NC}"

AUDIO_COUNT=0
if [ -d "$AUDIO_DIR" ]; then
    for AUDIO_FILE in "$AUDIO_DIR"/*.mp3; do
        if [ -f "$AUDIO_FILE" ]; then
            rm -f "$AUDIO_FILE"
            ((AUDIO_COUNT++))
        fi
    done
    echo -e "  ${GREEN}✓ Removed: $AUDIO_COUNT audio files${NC}"
    
    # Remove audio directory if empty
    if [ -z "$(ls -A "$AUDIO_DIR" 2>/dev/null)" ]; then
        rmdir "$AUDIO_DIR"
        echo -e "  ${GREEN}✓ Removed empty audio directory${NC}"
    fi
fi

# Step 6: Clean up logs
echo -e "\n${YELLOW}📝 Cleaning logs...${NC}"

LOGS_REMOVED=0
if [ -d "$LOGS_DIR" ]; then
    # Remove hook-related logs
    LOG_PATTERNS=(
        "orchestration.jsonl"
        "mcp_operations.jsonl"
        "agent_routing.jsonl"
        "slash_commands.jsonl"
        "model_usage.jsonl"
    )
    
    for PATTERN in "${LOG_PATTERNS[@]}"; do
        LOG_FILE="$LOGS_DIR/$PATTERN"
        if [ -f "$LOG_FILE" ]; then
            rm -f "$LOG_FILE"
            ((LOGS_REMOVED++))
        fi
    done
    
    echo -e "  ${GREEN}✓ Removed: $LOGS_REMOVED log files${NC}"
fi

# Step 7: Clean up state
echo -e "\n${YELLOW}💾 Cleaning state...${NC}"

STATE_REMOVED=0
if [ -d "$STATE_DIR" ]; then
    # Remove hook-related state files
    STATE_PATTERNS=(
        "agent_routing.json"
        "active_agents.json"
        "orchestration_plan.json"
        "mcp_state.json"
        "session_state.json"
    )
    
    for PATTERN in "${STATE_PATTERNS[@]}"; do
        STATE_FILE="$STATE_DIR/$PATTERN"
        if [ -f "$STATE_FILE" ]; then
            rm -f "$STATE_FILE"
            ((STATE_REMOVED++))
        fi
    done
    
    echo -e "  ${GREEN}✓ Removed: $STATE_REMOVED state files${NC}"
    
    # Remove state directory if empty
    if [ -z "$(ls -A "$STATE_DIR" 2>/dev/null)" ]; then
        rmdir "$STATE_DIR"
        echo -e "  ${GREEN}✓ Removed empty state directory${NC}"
    fi
fi

# Step 8: Update settings.json
echo -e "\n${YELLOW}⚙️ Updating settings...${NC}"

SETTINGS_PATH="$CLAUDE_DIR/settings.json"
if [ -f "$SETTINGS_PATH" ]; then
    # Check if jq is available
    if command -v jq &> /dev/null; then
        # Use jq to remove hooks configuration
        jq 'del(.hooks)' "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp" && mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
        echo -e "  ${GREEN}✓ Removed hooks configuration from settings${NC}"
    else
        # Fallback: create empty settings
        echo '{}' > "$SETTINGS_PATH"
        echo -e "  ${YELLOW}⚠ Reset settings.json (jq not available)${NC}"
    fi
fi

# Step 9: Remove hooks directory if empty
if [ -d "$HOOKS_DIR" ] && [ -z "$(ls -A "$HOOKS_DIR" 2>/dev/null)" ]; then
    rmdir "$HOOKS_DIR"
    echo -e "\n${GREEN}✓ Removed empty hooks directory${NC}"
fi

# Step 10: Display summary
echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}UNINSTALLATION COMPLETE${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}📊 Removal Summary:${NC}"
echo -e "  ${WHITE}• Hooks removed: $REMOVED_COUNT${NC}"
echo -e "  ${WHITE}• Audio files removed: $AUDIO_COUNT${NC}"
echo -e "  ${WHITE}• Logs cleaned: $LOGS_REMOVED${NC}"
echo -e "  ${WHITE}• State files cleaned: $STATE_REMOVED${NC}"

echo -e "\n${YELLOW}💾 Backup Information:${NC}"
echo -e "  ${WHITE}Location: $BACKUP_PATH${NC}"
echo -e "  ${WHITE}Contains: Hooks, audio, settings, and state${NC}"

echo -e "\n${CYAN}🔄 To Restore:${NC}"
echo -e "  ${WHITE}1. Copy files from backup to original locations${NC}"
echo -e "  ${WHITE}2. Or run install-hooks.sh for fresh installation${NC}"

echo -e "\n${GREEN}✅ Enhanced hooks have been safely removed.${NC}"

# Return success
exit 0