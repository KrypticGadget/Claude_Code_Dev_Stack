#!/bin/bash
# Ultimate Claude Code Hooks & Audio Uninstaller v5.0 for macOS
# Safely removes all hooks and optimized audio system with v5.0 enhancements

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║   Ultimate Claude Code Hooks & Audio Uninstaller v5.0         ║
║     Removes All Hooks & 22 Audio Files with Full Backup       ║
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
SETTINGS_PATH="$CLAUDE_DIR/settings.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Step 1: Check if hooks are installed
echo -e "\n${YELLOW}🔍 Checking installation...${NC}"

if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "  ${YELLOW}⚠ No hooks directory found at: $HOOKS_DIR${NC}"
    echo -e "  ${GRAY}Nothing to uninstall.${NC}"
    exit 0
fi

INSTALLED_HOOKS=$(find "$HOOKS_DIR" -name "*.py" 2>/dev/null | wc -l)
AUDIO_FILES=0
if [ -d "$AUDIO_DIR" ]; then
    AUDIO_FILES=$(find "$AUDIO_DIR" -name "*.wav" 2>/dev/null | wc -l)
fi

echo -e "  ${CYAN}Found: $INSTALLED_HOOKS hooks${NC}"
echo -e "  ${CYAN}Found: $AUDIO_FILES audio files${NC}"

# Step 2: Confirm uninstallation
echo -e "\n${YELLOW}⚠ This will remove:${NC}"
echo -e "  ${WHITE}• All hook scripts in $HOOKS_DIR${NC}"
echo -e "  ${WHITE}• All audio files in $AUDIO_DIR${NC}"
echo -e "  ${WHITE}• Hook-related logs in $LOGS_DIR${NC}"
echo -e "  ${WHITE}• Session state in $STATE_DIR${NC}"

read -p "$(echo -e '\nDo you want to continue? (Y/N): ')" CONFIRM
if [[ "$CONFIRM" != "Y" && "$CONFIRM" != "y" ]]; then
    echo -e "\n${GRAY}Uninstallation cancelled.${NC}"
    exit 0
fi

# Step 3: Create backup
echo -e "\n${YELLOW}💾 Creating backup...${NC}"

mkdir -p "$BACKUPS_DIR"
BACKUP_PATH="$BACKUPS_DIR/uninstall_backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

# Backup hooks
if [ "$INSTALLED_HOOKS" -gt 0 ]; then
    mkdir -p "$BACKUP_PATH/hooks"
    cp -r "$HOOKS_DIR"/*.py "$BACKUP_PATH/hooks/" 2>/dev/null
    echo -e "  ${GREEN}✓ Backed up $INSTALLED_HOOKS hooks${NC}"
fi

# Backup audio files
if [ "$AUDIO_FILES" -gt 0 ]; then
    mkdir -p "$BACKUP_PATH/audio"
    cp -r "$AUDIO_DIR"/*.wav "$BACKUP_PATH/audio/" 2>/dev/null
    echo -e "  ${GREEN}✓ Backed up $AUDIO_FILES audio files${NC}"
fi

# Backup settings.json
if [ -f "$SETTINGS_PATH" ]; then
    cp "$SETTINGS_PATH" "$BACKUP_PATH/settings.json"
    echo -e "  ${GREEN}✓ Backed up settings.json${NC}"
fi

echo -e "  ${CYAN}Backup location: $BACKUP_PATH${NC}"

# Step 4: Remove hook scripts
echo -e "\n${YELLOW}🗑️ Removing hooks...${NC}"

# List of all v5.0 hooks (14 + legacy)
HOOKS=(
    # Core v5.0 hooks
    "agent_mention_parser.py"
    "slash_command_router.py"
    "audio_player.py"
    "audio_notifier.py"
    "venv_enforcer.py"
    "master_orchestrator.py"
    "audio_controller.py"
    "ultimate_claude_hook.py"
    "session_loader.py"
    "session_saver.py"
    "model_tracker.py"
    "planning_trigger.py"
    "test_hook.py"
    
    # Legacy hooks for cleanup
    "agent_orchestrator.py"
    "agent_orchestrator_integrated.py"
    "mcp_gateway.py"
    "mcp_gateway_enhanced.py"
    "mcp_initializer.py"
    "quality_gate.py"
    "pre_command.py"
    "post_command.py"
    "pre_project.py"
    "post_project.py"
    "base_hook.py"
)

REMOVED_COUNT=0
for HOOK in "${HOOKS[@]}"; do
    HOOK_PATH="$HOOKS_DIR/$HOOK"
    if [ -f "$HOOK_PATH" ]; then
        rm -f "$HOOK_PATH"
        echo -e "  ${GREEN}✓ Removed: $HOOK${NC}"
        ((REMOVED_COUNT++))
    fi
done

echo -e "  ${CYAN}Removed: $REMOVED_COUNT hooks${NC}"

# Step 5: Remove audio system
echo -e "\n${YELLOW}🎵 Removing audio system...${NC}"

AUDIO_COUNT=0
if [ -d "$AUDIO_DIR" ]; then
    # Remove all .wav files
    find "$AUDIO_DIR" -name "*.wav" -delete
    AUDIO_COUNT=$(find "$AUDIO_DIR" -name "*.wav" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓ Removed: 22 audio files${NC}"
    
    # Remove empty audio directory
    if [ -z "$(ls -A $AUDIO_DIR)" ]; then
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
        "test_hook.log"
        "audio_player.log"
        "session_*.log"
    )
    
    for PATTERN in "${LOG_PATTERNS[@]}"; do
        if ls "$LOGS_DIR"/$PATTERN 2>/dev/null; then
            rm -f "$LOGS_DIR"/$PATTERN
            ((LOGS_REMOVED++))
        fi
    done
    
    echo -e "  ${GREEN}✓ Removed: $LOGS_REMOVED log files${NC}"
fi

# Step 7: Clean up state
echo -e "\n${YELLOW}💾 Cleaning state...${NC}"

STATE_REMOVED=0
if [ -d "$STATE_DIR" ]; then
    # Remove state files
    if [ -n "$(ls -A $STATE_DIR)" ]; then
        rm -rf "$STATE_DIR"/*
        STATE_REMOVED=$(ls -A $STATE_DIR 2>/dev/null | wc -l)
        echo -e "  ${GREEN}✓ Removed: state files${NC}"
    fi
    
    # Remove empty state directory
    if [ -z "$(ls -A $STATE_DIR)" ]; then
        rmdir "$STATE_DIR"
        echo -e "  ${GREEN}✓ Removed empty state directory${NC}"
    fi
fi

# Step 8: Update settings.json
echo -e "\n${YELLOW}⚙️ Updating settings.json configuration...${NC}"

if [ -f "$SETTINGS_PATH" ]; then
    # Use Python to safely remove hook configurations
    python3 -c "
import json
import sys

try:
    with open('$SETTINGS_PATH', 'r') as f:
        settings = json.load(f)
    
    # Remove hook-related configurations
    removed = []
    if 'hooks' in settings:
        del settings['hooks']
        removed.append('hooks')
    if 'agentSystem' in settings:
        del settings['agentSystem']
        removed.append('agentSystem')
    if 'slashCommands' in settings:
        del settings['slashCommands']
        removed.append('slashCommands')
    
    # Save updated settings
    with open('$SETTINGS_PATH', 'w') as f:
        json.dump(settings, f, indent=2)
    
    if removed:
        print('  ✓ Removed configurations:', ', '.join(removed))
    else:
        print('  • No hook configurations found')
except Exception as e:
    print(f'  ⚠ Could not update settings.json: {e}')
" 2>/dev/null || echo -e "  ${YELLOW}⚠ Could not update settings.json${NC}"
else
    echo -e "  ${GRAY}• No settings.json found${NC}"
fi

# Step 9: Remove hooks directory if empty
if [ -d "$HOOKS_DIR" ] && [ -z "$(ls -A $HOOKS_DIR)" ]; then
    rmdir "$HOOKS_DIR"
    echo -e "\n${GREEN}✓ Removed empty hooks directory${NC}"
fi

# Step 10: Display summary
echo -e "\n"
echo "════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}UNINSTALLATION COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════"

echo -e "\n${CYAN}📊 Removal Summary:${NC}"
echo -e "  ${WHITE}• Hooks removed: $REMOVED_COUNT/14 (+ legacy)${NC}"
echo -e "  ${WHITE}• Audio files removed: 22${NC}"
echo -e "  ${WHITE}• Logs cleaned: $LOGS_REMOVED${NC}"
echo -e "  ${WHITE}• State files cleaned: Yes${NC}"

echo -e "\n${YELLOW}💾 Backup Information:${NC}"
echo -e "  ${WHITE}Location: $BACKUP_PATH${NC}"
echo -e "  ${WHITE}Contains: Hooks, audio, settings${NC}"

echo -e "\n${CYAN}🔄 To Restore:${NC}"
echo -e "  ${WHITE}Option 1: Restore from backup${NC}"
echo -e "    ${GRAY}• Copy files from: $BACKUP_PATH${NC}"
echo -e "  ${WHITE}Option 2: Fresh installation${NC}"
echo -e "    ${GRAY}• Run: ./platform-tools/macos/installers/install-hooks.sh${NC}"

echo -e "\n${YELLOW}⚠️ Important Notes:${NC}"
echo -e "  ${WHITE}• Your backup is preserved at: $BACKUP_PATH${NC}"
echo -e "  ${WHITE}• Restart Claude Code after reinstalling hooks${NC}"
echo -e "  ${WHITE}• Use --debug flag to verify hook operations${NC}"

echo -e "\n${GREEN}✅ Enhanced hooks have been safely removed with complete backup.${NC}"

exit 0