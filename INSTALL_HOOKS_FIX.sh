#!/bin/bash
# Bash Script to Fix Hook Installation for Linux/WSL
# Run this to properly install all hooks

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║           Claude Code Hook System Fix v2.1                     ║
║           Installing and Configuring All 19 Hooks              ║
╚════════════════════════════════════════════════════════════════╝
EOF

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Step 1: Create directories
echo -e "\n${YELLOW}📁 Creating directories...${NC}"
directories=(
    "$HOME/.claude"
    "$HOME/.claude/hooks"
    "$HOME/.claude/audio"
    "$HOME/.claude/logs"
    "$HOME/.claude/state"
    "$HOME/.claude/backups"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "  ${GREEN}✓ Created: $dir${NC}"
    else
        echo -e "  ${GRAY}• Exists: $dir${NC}"
    fi
done

# Step 2: Backup existing settings
echo -e "\n${YELLOW}💾 Backing up existing settings...${NC}"
timestamp=$(date +"%Y%m%d_%H%M%S")
if [ -f "$HOME/.claude/settings.json" ]; then
    cp "$HOME/.claude/settings.json" "$HOME/.claude/backups/settings_backup_$timestamp.json"
    echo -e "  ${GREEN}✓ Backed up to: settings_backup_$timestamp.json${NC}"
fi

# Step 3: Copy all hooks
echo -e "\n${YELLOW}📝 Installing hooks...${NC}"
SOURCE_DIR="$(pwd)/.claude-example/hooks"
DEST_DIR="$HOME/.claude/hooks"

hook_files=(
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
    "test_hook.py"
)

copied_count=0
for hook in "${hook_files[@]}"; do
    if [ -f "$SOURCE_DIR/$hook" ]; then
        cp "$SOURCE_DIR/$hook" "$DEST_DIR/$hook"
        chmod +x "$DEST_DIR/$hook"
        echo -e "  ${GREEN}✓ Installed: $hook${NC}"
        ((copied_count++))
    else
        echo -e "  ${RED}✗ Not found: $hook${NC}"
    fi
done

echo -e "  ${CYAN}Installed $copied_count hooks${NC}"

# Step 4: Copy audio files
echo -e "\n${YELLOW}🎵 Installing audio files...${NC}"
SOURCE_AUDIO="$(pwd)/.claude-example/audio"
DEST_AUDIO="$HOME/.claude/audio"

if [ -d "$SOURCE_AUDIO" ]; then
    for audio in "$SOURCE_AUDIO"/*.mp3; do
        if [ -f "$audio" ]; then
            cp "$audio" "$DEST_AUDIO/"
            echo -e "  ${GREEN}✓ Installed: $(basename "$audio")${NC}"
        fi
    done
else
    echo -e "  ${YELLOW}⚠ Audio directory not found, creating placeholders...${NC}"
    for placeholder in ready.mp3 task_complete.mp3 build_complete.mp3 error_fixed.mp3 awaiting_instructions.mp3; do
        touch "$DEST_AUDIO/$placeholder"
        echo -e "  ${GRAY}• Created placeholder: $placeholder${NC}"
    done
fi

# Step 5: Determine Python command
echo -e "\n${YELLOW}⚙️ Checking Python...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    PYTHON_CMD="python3"
    echo -e "  ${GREEN}✓ Found Python 3: $PYTHON_VERSION${NC}"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo -e "  ${GREEN}✓ Found Python 3: $PYTHON_VERSION${NC}"
    else
        echo -e "  ${RED}⚠ Python 2 found - Python 3 required!${NC}"
        PYTHON_CMD="python"
    fi
else
    echo -e "  ${RED}⚠ Python not found - hooks will not work!${NC}"
    PYTHON_CMD="python3"
fi

# Step 6: Create corrected settings.json
echo -e "\n${YELLOW}⚙️ Installing corrected settings.json...${NC}"

cat > "$HOME/.claude/settings.json" << SETTINGS_EOF
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/agent_orchestrator_integrated.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/quality_gate.py",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/pre_command.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/test_hook.py",
            "timeout": 2
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/model_tracker.py",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/post_command.py",
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
            "command": "$PYTHON_CMD $HOME/.claude/hooks/agent_mention_parser.py",
            "timeout": 3
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/slash_command_router.py",
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
            "command": "$PYTHON_CMD $HOME/.claude/hooks/session_loader.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/mcp_initializer.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/session_saver.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "$PYTHON_CMD $HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      }
    ]
  }
}
SETTINGS_EOF

echo -e "  ${GREEN}✓ Installed corrected settings.json${NC}"

# Step 7: Validate installation
echo -e "\n${YELLOW}🔍 Validating installation...${NC}"

# Check if settings.json is valid JSON
if python3 -m json.tool "$HOME/.claude/settings.json" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ settings.json is valid JSON${NC}"
else
    echo -e "  ${RED}✗ settings.json has JSON errors!${NC}"
fi

# Count installed hooks
INSTALLED_HOOKS=$(find "$HOME/.claude/hooks" -name "*.py" -type f | wc -l)
echo -e "  ${GREEN}✓ $INSTALLED_HOOKS Python hooks installed${NC}"

# Test a hook
echo -e "\n${YELLOW}🧪 Testing hook execution...${NC}"
TEST_INPUT='{"hook_event_name": "test", "tool_name": "Bash"}'

if echo "$TEST_INPUT" | $PYTHON_CMD "$HOME/.claude/hooks/test_hook.py" 2>&1; then
    echo -e "  ${GREEN}✓ Test hook executed successfully${NC}"
    
    # Check if log was created
    if [ -f "$HOME/.claude/logs/test_hook.log" ]; then
        echo -e "  ${GREEN}✓ Test hook log created${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Test hook execution failed (check Python installation)${NC}"
fi

# Final instructions
echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}INSTALLATION COMPLETE${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}📋 Summary:${NC}"
echo -e "  ${WHITE}• Hooks installed: $INSTALLED_HOOKS${NC}"
echo -e "  ${WHITE}• Settings.json: Configured with correct paths${NC}"
echo -e "  ${WHITE}• Python command: $PYTHON_CMD${NC}"
echo -e "  ${WHITE}• Test hook: Installed for debugging${NC}"

echo -e "\n${YELLOW}⚠️ CRITICAL NEXT STEPS:${NC}"
echo -e "  ${WHITE}1. EXIT Claude Code completely${NC}"
echo -e "  ${WHITE}2. Restart Claude Code${NC}"
echo -e "  ${WHITE}3. Run in debug mode to verify: claude --debug${NC}"
echo -e "  ${WHITE}4. Type: /hooks${NC}"
echo -e "  ${WHITE}5. You should see all hooks listed${NC}"

echo -e "\n${CYAN}🧪 To verify hooks are working:${NC}"
echo -e "  ${WHITE}1. Run: ls${NC}"
echo -e "  ${WHITE}2. Check: cat ~/.claude/logs/test_hook.log${NC}"
echo -e "  ${WHITE}3. Try: @agent-frontend-mockup test${NC}"
echo -e "  ${WHITE}4. Try: /new-project test${NC}"

echo -e "\n${YELLOW}💡 If hooks don't appear:${NC}"
echo -e "  ${WHITE}• Make sure Python 3 is installed${NC}"
echo -e "  ${WHITE}• Check that scripts have execute permissions${NC}"
echo -e "  ${WHITE}• Verify paths in settings.json${NC}"
echo -e "  ${WHITE}• Run Claude Code with --debug flag${NC}"

echo -e "\n${GREEN}✨ Your hook system should now be working!${NC}"