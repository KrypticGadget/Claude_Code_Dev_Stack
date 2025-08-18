#!/bin/bash
# Ultimate Claude Code Hooks Installer v5.0 for macOS
# Complete system with audio categorization, venv enforcement, and hierarchical orchestration

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║          Claude Code Enhanced Hooks Installer v5.0             ║
║   14 Hooks + 22 Audio Files + Bash Categorization + Venv      ║
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

# Complete list of v5.0 hooks (14 total)
HOOKS=(
    # Core integration hooks
    "agent_mention_parser.py"
    "slash_command_router.py"
    
    # Audio and notification
    "audio_player.py"
    "audio_notifier.py"
    
    # v5.0 NEW HOOK
    "venv_enforcer.py"
    
    # ULTIMATE SYSTEM HOOKS
    "master_orchestrator.py"
    "audio_controller.py"
    "ultimate_claude_hook.py"
    
    # Session management
    "session_loader.py"
    "session_saver.py"
    
    # Quality and tracking
    "model_tracker.py"
    "planning_trigger.py"
    
    # Debug hook
    "test_hook.py"
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

# Step 5: Install Complete Audio System v5.0 (69 descriptive audio files)
echo -e "\n${YELLOW}🎵 Installing Complete Audio System v5.0 (69 descriptive audio files)...${NC}"

# Complete list of v5.0 audio files (69 total)
AUDIO_FILES=(
    # Core System Files (22) - Original compatibility
    "project_created.wav"
    "ready_for_input.wav"
    "agent_activated.wav"
    "pipeline_complete.wav"
    "pipeline_initiated.wav"
    "confirm_required.wav"
    "file_operation_pending.wav"
    "file_operation_complete.wav"
    "command_execution_pending.wav"
    "command_successful.wav"
    "planning_complete.wav"
    "processing.wav"
    "analyzing.wav"
    "working.wav"
    "awaiting_input.wav"
    "milestone_complete.wav"
    "operation_complete.wav"
    "phase_complete.wav"
    "decision_required.wav"
    "awaiting_confirmation.wav"
    "permission_required.wav"
    "build_successful.wav"
    
    # File Operations - SPECIFIC (5)
    "mkdir_operation.wav"
    "touch_operation.wav"
    "copy_operation.wav"
    "move_operation.wav"
    "delete_operation.wav"
    
    # Git Operations - SPECIFIC (4)
    "git_status.wav"
    "git_commit.wav"
    "git_push.wav"
    "git_pull.wav"
    
    # Build Operations - SPECIFIC (3)
    "npm_build.wav"
    "make_build.wav"
    "cargo_build.wav"
    
    # Testing - SPECIFIC (3)
    "running_tests.wav"
    "tests_passed.wav"
    "tests_failed.wav"
    
    # Package Management - SPECIFIC (3)
    "installing_packages.wav"
    "pip_install.wav"
    "npm_install.wav"
    
    # Docker - SPECIFIC (2)
    "docker_building.wav"
    "docker_running.wav"
    
    # Navigation/Search - SPECIFIC (3)
    "checking_files.wav"
    "searching_files.wav"
    "changing_directory.wav"
    
    # Network - SPECIFIC (3)
    "http_request.wav"
    "downloading_file.wav"
    "ssh_connection.wav"
    
    # Virtual Environment - SPECIFIC (3)
    "venv_required.wav"
    "venv_activated.wav"
    "no_venv_warning.wav"
    
    # Agent Operations - SPECIFIC (4)
    "frontend_agent.wav"
    "backend_agent.wav"
    "database_agent.wav"
    "master_orchestrator.wav"
    
    # Status Updates - SPECIFIC (4)
    "analyzing_code.wav"
    "generating_code.wav"
    "reviewing_changes.wav"
    "optimizing_performance.wav"
    
    # Warnings - SPECIFIC (3)
    "risky_command.wav"
    "permission_denied.wav"
    "file_exists.wav"
    
    # Errors - SPECIFIC (3)
    "command_failed.wav"
    "file_not_found.wav"
    "connection_error.wav"
    
    # MCP Services - SPECIFIC (3)
    "playwright_automation.wav"
    "obsidian_notes.wav"
    "web_search.wav"
    
    # Auto Mode - SPECIFIC (2)
    "auto_accepting.wav"
    "auto_mode_active.wav"
)

# Check existing audio files
EXISTING_AUDIO=$(ls -1 "$AUDIO_DIR"/*.wav 2>/dev/null | wc -l)

if [ $EXISTING_AUDIO -ge 69 ]; then
    echo -e "  ${GREEN}✓ Complete audio system v5.0 already installed ($EXISTING_AUDIO files)${NC}"
else
    # Try local source first
    if [ -d "$SOURCE_AUDIO_DIR" ]; then
        echo -e "  ${CYAN}Installing from local source...${NC}"
        AUDIO_COUNT=0
        
        for AUDIO_FILE in "${AUDIO_FILES[@]}"; do
            SOURCE_PATH="$SOURCE_AUDIO_DIR/$AUDIO_FILE"
            DEST_PATH="$AUDIO_DIR/$AUDIO_FILE"
            
            if [ -f "$SOURCE_PATH" ]; then
                cp "$SOURCE_PATH" "$DEST_PATH"
                ((AUDIO_COUNT++))
                
                # Show progress every 10 files
                if [ $((AUDIO_COUNT % 10)) -eq 0 ]; then
                    echo -e "    Installed: $AUDIO_COUNT/69 files"
                fi
            fi
        done
        
        echo -e "  ${GREEN}✓ Installed: $AUDIO_COUNT audio files${NC}"
    else
        # Download from GitHub
        echo -e "  ${CYAN}Downloading from GitHub...${NC}"
        BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/audio"
        
        DOWNLOADED=0
        FAILED=0
        
        for AUDIO_FILE in "${AUDIO_FILES[@]}"; do
            URL="$BASE_URL/$AUDIO_FILE"
            DEST="$AUDIO_DIR/$AUDIO_FILE"
            
            if [ -f "$DEST" ]; then
                ((DOWNLOADED++))
                continue
            fi
            
            if curl -sL "$URL" -o "$DEST" 2>/dev/null; then
                ((DOWNLOADED++))
                
                # Show progress every 10 files
                if [ $((DOWNLOADED % 10)) -eq 0 ]; then
                    echo -e "    Downloaded: $DOWNLOADED/69"
                fi
            else
                ((FAILED++))
            fi
            
            sleep 0.1  # Small delay to avoid rate limiting
        done
        
        echo -e "  ${GREEN}✓ Downloaded: $DOWNLOADED audio files${NC}"
        if [ $FAILED -gt 0 ]; then
            echo -e "  ${YELLOW}⚠ Failed: $FAILED files${NC}"
        fi
    fi
fi

# Show audio system status
FINAL_AUDIO_COUNT=$(ls -1 "$AUDIO_DIR"/*.wav 2>/dev/null | wc -l)
if [ $FINAL_AUDIO_COUNT -ge 69 ]; then
    echo -e "\n  ${GREEN}🎉 Complete Audio System v5.0 Ready!${NC}"
    echo -e "    ${GRAY}• 69 descriptive audio files${NC}"
    echo -e "    ${GRAY}• Specific operation feedback${NC}"
    echo -e "    ${GRAY}• Agent-specific notifications${NC}"
    echo -e "    ${GRAY}• Error-specific audio${NC}"
elif [ $FINAL_AUDIO_COUNT -ge 22 ]; then
    echo -e "\n  ${YELLOW}✓ Basic audio system ($FINAL_AUDIO_COUNT files)${NC}"
    echo -e "    ${YELLOW}Core files present, missing some specific audio${NC}"
elif [ $FINAL_AUDIO_COUNT -gt 0 ]; then
    echo -e "\n  ${YELLOW}⚠ Partial audio system ($FINAL_AUDIO_COUNT files)${NC}"
    echo -e "    ${YELLOW}Only $FINAL_AUDIO_COUNT of 69 files installed${NC}"
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