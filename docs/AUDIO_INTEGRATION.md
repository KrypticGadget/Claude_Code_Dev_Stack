# Audio Integration for Claude Code Dev Stack

## Overview
Complete audio notification system integrated into the Claude Code Dev Stack, providing context-aware sound feedback for all major events and operations.

## Audio Assets

### Location
All audio files are stored in `.claude-example/audio/`:
- `ready.mp3` - Plays when session starts or agents are ready
- `task_complete.mp3` - Plays when tasks complete successfully
- `build_complete.mp3` - Plays when builds finish successfully
- `error_fixed.mp3` - Plays when errors are resolved
- `awaiting_instructions.mp3` - Plays when waiting for user input

### Audio Hook
**File**: `.claude-example/hooks/audio_player.py`

The audio player hook intelligently determines which sound to play based on:
- Hook event type (SessionStart, Stop, etc.)
- Tool being used (Task, Bash, MCP services)
- Operation outcome (success, error, build complete)

## Integration Points

### 1. Agent Invocations
When any agent is called via `@agent-` mentions or the Task tool:
- **Sound**: `ready.mp3`
- **Events**: PreToolUse with Task matcher

### 2. Session Events
- **Session Start**: `ready.mp3` - When Claude Code session begins
- **Session Stop**: `task_complete.mp3` - When session ends

### 3. Build Operations
Detected via Bash commands containing build keywords:
- `npm run build`, `make`, `cargo build`, `go build`
- **Sound**: `build_complete.mp3` on successful completion

### 4. Error Resolution
When errors are fixed or resolved:
- **Sound**: `error_fixed.mp3`
- **Detection**: Keywords "fixed", "resolved" in tool responses

### 5. Awaiting Instructions
When Claude Code is waiting for user input:
- **Sound**: `awaiting_instructions.mp3`
- **Event**: UserPromptSubmit with empty prompt

## Configuration

### Settings Integration
The audio hook is integrated into `settings-integrated.json` at multiple points:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/audio_player.py",
            "timeout": 1
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "SessionStart": [...],
    "Stop": [...]
  }
}
```

### Audio Configuration
**File**: `.claude-example/audio/audio_config.json`

```json
{
  "version": "2.1",
  "enabled": true,
  "audio_mappings": {
    "task_complete": "task_complete.mp3",
    "build_complete": "build_complete.mp3",
    "error_fixed": "error_fixed.mp3",
    "ready": "ready.mp3",
    "awaiting_instructions": "awaiting_instructions.mp3"
  }
}
```

## Installation

### One-Click Setup
```powershell
.\setup-integrated-audio.ps1
```

This script:
1. Copies all hooks including `audio_player.py` to `~/.claude/hooks/`
2. Copies all MP3 files to `~/.claude/audio/`
3. Installs `settings-integrated.json` with audio hooks
4. Creates audio configuration file
5. Sets up test scripts

### Manual Installation
1. Copy `.claude-example/hooks/audio_player.py` to `~/.claude/hooks/`
2. Copy `.claude-example/audio/*.mp3` to `~/.claude/audio/`
3. Use `.claude-example/settings-integrated.json` as your settings

## Testing

### Test Audio Hook
```powershell
# Run from Claude Code Dev Stack directory
.\test-integration-audio.ps1
```

### Test Individual Sounds
```python
# Test session start sound
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py

# Test task complete sound
echo '{"hook_event_name": "Stop"}' | python ~/.claude/hooks/audio_player.py
```

## Platform Support

### Windows
- Uses PowerShell's `Media.SoundPlayer` for playback
- All MP3 files are supported

### macOS
- Uses `afplay` command
- MP3, WAV, and other audio formats supported

### Linux
- Uses `aplay` command
- May require audio codec installation for MP3

## Features

### Non-Blocking
- Audio plays asynchronously
- No performance impact on Claude Code operations
- Timeouts set to 1 second for all audio hooks

### Graceful Degradation
- Missing audio files are silently skipped
- Audio player errors don't break hook chain
- Works even if audio system is unavailable

### Context Awareness
The audio player intelligently determines sounds based on:
- Event type
- Tool being used
- Command content
- Operation outcome

## Customization

### Adding New Sounds
1. Add MP3 file to `.claude-example/audio/`
2. Update `audio_mappings` in `audio_player.py`
3. Add detection logic in `determine_audio()` method

### Disabling Audio
To temporarily disable audio:
1. Set `"enabled": false` in `audio_config.json`
2. Or remove audio hooks from `settings.json`

### Volume Control
Platform-specific:
- **Windows**: System volume controls
- **macOS**: `afplay -v 0.5` for 50% volume
- **Linux**: `aplay` with ALSA mixer settings

## Troubleshooting

### No Sound Playing
1. Check audio files exist: `ls ~/.claude/audio/`
2. Test audio player: `python ~/.claude/hooks/audio_player.py < test.json`
3. Verify settings.json includes audio hooks

### Wrong Sound Playing
1. Check event detection in `audio_player.py`
2. Review `determine_audio()` method logic
3. Test with specific event JSON

### Performance Issues
- Audio plays asynchronously by default
- 1-second timeout prevents hanging
- Consider disabling for slow systems

## Integration with Dev Stack

The audio system works seamlessly with:
- **28 Agents**: Sound on every agent invocation
- **18 Slash Commands**: Audio feedback for commands
- **3 MCP Services**: Notification when MCPs activate
- **15 Hooks**: Coexists with all other hooks

Every major action in the Claude Code Dev Stack now provides audio feedback, creating a more engaging and informative development experience.