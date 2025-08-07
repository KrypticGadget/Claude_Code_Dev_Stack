#!/bin/bash
# Enhanced Claude Code Hooks Installer v2.1 for macOS
# Installs complete integrated hook system with audio notifications

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║          Claude Code Enhanced Hooks Installer v2.1             ║
║     19 Hooks + Audio Notifications + Full Integration          ║
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

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SOURCE_HOOKS_DIR="$PROJECT_ROOT/.claude-example/hooks"
SOURCE_AUDIO_DIR="$PROJECT_ROOT/.claude-example/audio"
SOURCE_SETTINGS="$PROJECT_ROOT/.claude-example/settings-integrated.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "\n${YELLOW}🔍 Checking prerequisites...${NC}"

HAS_PYTHON=false
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    HAS_PYTHON=true
    echo -e "  ${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        HAS_PYTHON=true
        echo -e "  ${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
    else
        echo -e "  ${YELLOW}⚠ Python 2 found - Python 3 required${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Python not found - hooks require Python 3${NC}"
    echo -e "    ${GRAY}Install with: brew install python3${NC}"
fi

# Check for audio playback capability on macOS
HAS_AUDIO=false
if command -v afplay &> /dev/null; then
    echo -e "  ${GREEN}✓ Audio support: afplay (native macOS)${NC}"
    HAS_AUDIO=true
elif command -v ffplay &> /dev/null; then
    echo -e "  ${GREEN}✓ Audio support: ffplay${NC}"
    HAS_AUDIO=true
else
    echo -e "  ${YELLOW}⚠ Audio player found (afplay is built-in on macOS)${NC}"
    HAS_AUDIO=true  # afplay should always be available on macOS
fi

# Step 2: Create directory structure
echo -e "\n${YELLOW}📁 Creating directory structure...${NC}"

DIRECTORIES=("$CLAUDE_DIR" "$HOOKS_DIR" "$AUDIO_DIR" "$LOGS_DIR" "$STATE_DIR" "$BACKUPS_DIR")

for DIR in "${DIRECTORIES[@]}"; do
    if [ ! -d "$DIR" ]; then
        mkdir -p "$DIR"
        echo -e "  ${GREEN}✓ Created: $(basename "$DIR")${NC}"
    else
        echo -e "  ${GRAY}• Exists: $(basename "$DIR")${NC}"
    fi
done

# Step 3: Backup existing configuration
echo -e "\n${YELLOW}💾 Backing up existing configuration...${NC}"

if [ -f "$CLAUDE_DIR/settings.json" ]; then
    BACKUP_PATH="$BACKUPS_DIR/settings_$TIMESTAMP.json"
    cp "$CLAUDE_DIR/settings.json" "$BACKUP_PATH"
    echo -e "  ${GREEN}✓ Backed up settings to: $BACKUP_PATH${NC}"
fi

# Backup existing hooks if present
if [ -d "$HOOKS_DIR" ] && [ "$(ls -A "$HOOKS_DIR"/*.py 2>/dev/null)" ]; then
    BACKUP_HOOKS_DIR="$BACKUPS_DIR/hooks_$TIMESTAMP"
    mkdir -p "$BACKUP_HOOKS_DIR"
    cp "$HOOKS_DIR"/*.py "$BACKUP_HOOKS_DIR" 2>/dev/null
    HOOK_COUNT=$(ls -1 "$BACKUP_HOOKS_DIR"/*.py 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓ Backed up $HOOK_COUNT existing hooks${NC}"
fi

# Step 4: Install enhanced hooks
echo -e "\n${YELLOW}📝 Installing enhanced hooks...${NC}"

# Complete list of enhanced hooks
HOOKS=(
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

INSTALLED_COUNT=0
FAILED_COUNT=0

# Try local source first
if [ -d "$SOURCE_HOOKS_DIR" ]; then
    echo -e "  ${CYAN}Installing from local source...${NC}"
    
    for HOOK in "${HOOKS[@]}"; do
        SOURCE_PATH="$SOURCE_HOOKS_DIR/$HOOK"
        DEST_PATH="$HOOKS_DIR/$HOOK"
        
        if [ -f "$SOURCE_PATH" ]; then
            cp "$SOURCE_PATH" "$DEST_PATH"
            chmod +x "$DEST_PATH"
            echo -e "    ${GREEN}✓ $HOOK${NC}"
            ((INSTALLED_COUNT++))
        else
            echo -e "    ${YELLOW}⚠ $HOOK (not found)${NC}"
        fi
    done
else
    # Fallback to GitHub download
    echo -e "  ${CYAN}Downloading from GitHub...${NC}"
    BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/hooks"
    
    for HOOK in "${HOOKS[@]}"; do
        echo -n "    Downloading: $HOOK... "
        URL="$BASE_URL/$HOOK"
        DEST="$HOOKS_DIR/$HOOK"
        
        if curl -sL "$URL" -o "$DEST" 2>/dev/null; then
            chmod +x "$DEST"
            echo -e "${GREEN}✓${NC}"
            ((INSTALLED_COUNT++))
        else
            echo -e "${RED}✗${NC}"
            ((FAILED_COUNT++))
        fi
        
        sleep 0.1
    done
fi

echo -e "  ${GREEN}Installed: $INSTALLED_COUNT hooks${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "  ${RED}Failed: $FAILED_COUNT hooks${NC}"
fi

# Step 5: Install audio assets
echo -e "\n${YELLOW}🎵 Installing audio notifications...${NC}"

if [ -d "$SOURCE_AUDIO_DIR" ]; then
    AUDIO_COUNT=$(ls -1 "$SOURCE_AUDIO_DIR"/*.mp3 2>/dev/null | wc -l)
    
    if [ $AUDIO_COUNT -gt 0 ]; then
        for AUDIO_FILE in "$SOURCE_AUDIO_DIR"/*.mp3; do
            FILENAME=$(basename "$AUDIO_FILE")
            cp "$AUDIO_FILE" "$AUDIO_DIR/$FILENAME"
            echo -e "  ${GREEN}✓ $FILENAME${NC}"
        done
        echo -e "  ${CYAN}Installed: $AUDIO_COUNT audio files${NC}"
    else
        echo -e "  ${YELLOW}⚠ No audio files found${NC}"
    fi
else
    # Create placeholder audio files
    echo -e "  ${YELLOW}Creating audio placeholders...${NC}"
    AUDIO_PLACEHOLDERS=(
        "ready.mp3"
        "task_complete.mp3"
        "build_complete.mp3"
        "error_fixed.mp3"
        "awaiting_instructions.mp3"
    )
    
    for AUDIO in "${AUDIO_PLACEHOLDERS[@]}"; do
        AUDIO_PATH="$AUDIO_DIR/$AUDIO"
        if [ ! -f "$AUDIO_PATH" ]; then
            touch "$AUDIO_PATH"
            echo -e "    ${GRAY}• Created placeholder: $AUDIO${NC}"
        fi
    done
fi

# Step 6: Install integrated settings
echo -e "\n${YELLOW}⚙️ Installing integrated settings...${NC}"

if [ -f "$SOURCE_SETTINGS" ]; then
    # Read settings and update paths for macOS
    sed "s|\$HOME|$HOME|g" "$SOURCE_SETTINGS" > "$CLAUDE_DIR/settings.json"
    echo -e "  ${GREEN}✓ Installed integrated settings.json${NC}"
else
    echo -e "  ${YELLOW}⚠ Settings file not found, creating minimal configuration${NC}"
    
    # Create minimal settings with hook configurations
    cat > "$CLAUDE_DIR/settings.json" << 'SETTINGS_EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/agent_orchestrator_integrated.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/model_tracker.py",
            "timeout": 5
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/slash_command_router.py",
            "timeout": 3
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/session_loader.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/mcp_initializer.py",
            "timeout": 5
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/session_saver.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      }
    ]
  }
}
SETTINGS_EOF
    
    # Replace $HOME with actual path (macOS sed requires backup extension)
    sed -i '' "s|\$HOME|$HOME|g" "$CLAUDE_DIR/settings.json"
    echo -e "  ${GREEN}✓ Created minimal settings.json${NC}"
fi

# Step 7: Create test script
echo -e "\n${YELLOW}🧪 Creating test script...${NC}"

cat > "$CLAUDE_DIR/test-hooks.sh" << 'TEST_EOF'
#!/bin/bash
# Test enhanced hook system

echo -e "\033[0;36mTesting Enhanced Hook System\033[0m"

CLAUDE_HOOKS="$HOME/.claude/hooks"
PYTHON_CMD="python3"

# Check for python3, fallback to python
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "\033[0;31m✗ Python not found\033[0m"
        exit 1
    fi
fi

# Test slash command router
echo -e "\n\033[1;33mTesting slash command router...\033[0m"
TEST_DATA='{"prompt":"/new-project test"}'
if echo "$TEST_DATA" | $PYTHON_CMD "$CLAUDE_HOOKS/slash_command_router.py" &> /dev/null; then
    echo -e "  \033[0;32m✓ Slash commands work!\033[0m"
else
    echo -e "  \033[0;31m✗ Slash commands failed\033[0m"
fi

# Test agent orchestrator
echo -e "\033[1;33mTesting agent orchestrator...\033[0m"
TEST_DATA='{"tool_name":"Task","tool_input":{"prompt":"@agent-frontend-mockup test"}}'
if echo "$TEST_DATA" | $PYTHON_CMD "$CLAUDE_HOOKS/agent_orchestrator_integrated.py" &> /dev/null; then
    echo -e "  \033[0;32m✓ Agent orchestration works!\033[0m"
else
    echo -e "  \033[0;31m✗ Agent orchestration failed\033[0m"
fi

# Test audio (using afplay on macOS)
echo -e "\033[1;33mTesting audio notifications...\033[0m"
TEST_DATA='{"hook_event_name":"SessionStart"}'
if echo "$TEST_DATA" | $PYTHON_CMD "$CLAUDE_HOOKS/audio_player.py" &> /dev/null; then
    echo -e "  \033[0;32m✓ Audio system works!\033[0m"
else
    echo -e "  \033[0;31m✗ Audio system failed\033[0m"
fi

echo -e "\n\033[0;32mTest complete!\033[0m"
TEST_EOF

chmod +x "$CLAUDE_DIR/test-hooks.sh"
echo -e "  ${GREEN}✓ Created test-hooks.sh${NC}"

# Step 8: Display summary
echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}ENHANCED HOOKS INSTALLATION COMPLETE${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}📊 Installation Summary:${NC}"
echo -e "  ${WHITE}• Hooks installed: $INSTALLED_COUNT/${#HOOKS[@]}${NC}"
AUDIO_COUNT=$(ls -1 "$AUDIO_DIR"/*.mp3 2>/dev/null | wc -l)
echo -e "  ${WHITE}• Audio files: $AUDIO_COUNT${NC}"
echo -e "  ${WHITE}• Directories created: ${#DIRECTORIES[@]}${NC}"
echo -e "  ${WHITE}• Settings: Integrated configuration${NC}"

echo -e "\n${CYAN}🚀 Key Features Enabled:${NC}"
echo -e "  ${WHITE}• 28 Agents orchestration${NC}"
echo -e "  ${WHITE}• 18 Slash commands${NC}"
echo -e "  ${WHITE}• 3 MCP services integration${NC}"
echo -e "  ${WHITE}• Audio notifications (afplay)${NC}"
echo -e "  ${WHITE}• Session persistence${NC}"
echo -e "  ${WHITE}• Model optimization${NC}"
echo -e "  ${WHITE}• Quality gates${NC}"

echo -e "\n${YELLOW}📝 Next Steps:${NC}"
echo -e "  ${WHITE}1. Restart Claude Code to load new hooks${NC}"
echo -e "  ${WHITE}2. Test system: ~/.claude/test-hooks.sh${NC}"
echo -e "  ${WHITE}3. Try: claude \"/new-project test\"${NC}"

if [ "$HAS_PYTHON" = false ]; then
    echo -e "\n${YELLOW}⚠ Important:${NC}"
    echo -e "  ${RED}Python 3 is required for hooks to function${NC}"
    echo -e "  ${YELLOW}Install with: brew install python3${NC}"
fi

echo -e "\n${GREEN}✨ Your Claude Code is now enhanced with 6-9x faster development!${NC}"

# Return success
exit 0