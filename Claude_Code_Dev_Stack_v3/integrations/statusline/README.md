# Claude Code Dev Stack - Enhanced Statusline

An enhanced statusline integration for Claude Code Dev Stack, built on top of Claude Powerline by @Owloops. This statusline provides real-time monitoring of Dev Stack components including agents, tasks, hooks, and audio notifications.

## Features

### Original Claude Powerline Features
- **Git Integration**: Branch, status, ahead/behind, working tree, operations, tags, and more
- **Cost Tracking**: Real-time session and daily cost monitoring with budget warnings
- **Model Display**: Current Claude model information
- **Context Tracking**: Token usage and context size monitoring
- **Multiple Themes**: Dark, light, Nord, Tokyo Night, Rose Pine, and custom themes
- **Powerline Style**: Beautiful vim-style powerline with proper separators

### Dev Stack Enhancements
- **Agent Monitoring**: Track active agents (0-28) with status indicators
- **Task Tracking**: Monitor task progress and completion status
- **Hook Status**: Monitor hook activity (0-28) with error tracking
- **Audio Notifications**: Display audio system status and queue information

## Installation

```bash
cd integrations/statusline
npm install
npm run build
```

## Configuration

### Basic Configuration
Create a `dev-stack-statusline.json` file or use the provided example:

```json
{
  "theme": "dark",
  "display": {
    "style": "powerline",
    "lines": [
      {
        "segments": {
          "directory": { "enabled": true, "showBasename": true },
          "git": { "enabled": true, "showSha": true, "showWorkingTree": true },
          "model": { "enabled": true }
        }
      },
      {
        "segments": {
          "agent": { "enabled": true, "showCount": true, "showStatus": true },
          "task": { "enabled": true, "showCount": true, "showProgress": true },
          "hook": { "enabled": true, "showCount": true, "showErrors": true },
          "audio": { "enabled": true, "showQueue": true }
        }
      }
    ]
  }
}
```

### Dev Stack Segment Options

#### Agent Monitor
```json
{
  "agent": {
    "enabled": true,
    "showCount": true,        // Show active/total count
    "showList": false,        // Show list of active agents
    "showStatus": true,       // Show status indicator
    "maxDisplay": 3           // Max agents to show in list
  }
}
```

#### Task Tracker
```json
{
  "task": {
    "enabled": true,
    "showCount": true,        // Show active/total count
    "showCurrent": false,     // Show current task name
    "showProgress": true,     // Show completion percentage
    "maxTaskLength": 15       // Max characters for task name
  }
}
```

#### Hook Status
```json
{
  "hook": {
    "enabled": true,
    "showCount": true,        // Show active/total count
    "showTypes": false,       // Show hook types
    "showErrors": true,       // Show error count
    "showLastTrigger": false, // Show time since last trigger
    "maxTypes": 2             // Max hook types to display
  }
}
```

#### Audio Notifications
```json
{
  "audio": {
    "enabled": true,
    "showVolume": false,      // Show volume level
    "showQueue": true,        // Show queue size
    "showCount": false,       // Show notification count
    "showLastActivity": false // Show last activity time
  }
}
```

## Usage

### Command Line
```bash
# Basic usage
dev-stack-statusline

# With custom config
dev-stack-statusline --config=/path/to/config.json

# With specific theme
dev-stack-statusline --theme=nord

# Help
dev-stack-statusline --help
```

### PWA Integration
```typescript
import { createDevStackStatusline } from './pwa-integration';

const statusline = createDevStackStatusline('./dev-stack-statusline.json');

// Get formatted statusline for display
const hookData = {
  session_id: 'current-session',
  workspace: { project_dir: '/path/to/project' },
  model: { id: 'claude-3-5-sonnet', display_name: 'Claude 3.5 Sonnet' }
};

const statusData = await statusline.generateForPWA(hookData);
console.log(statusData.segments);

// Get Dev Stack metrics
const metrics = await statusline.getDevStackMetrics();
console.log(metrics.agents, metrics.tasks, metrics.hooks, metrics.audio);
```

### Claude Code Settings
Add to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "dev-stack-statusline --config=./integrations/statusline/dev-stack-statusline.json",
    "padding": 0
  }
}
```

## Themes

The statusline supports all original Claude Powerline themes plus custom Dev Stack colors:

- **Dark**: Default dark theme with high contrast
- **Light**: Clean light theme
- **Nord**: Nord color scheme
- **Tokyo Night**: Tokyo Night theme
- **Rose Pine**: Rose Pine theme
- **Custom**: Define your own colors

### Custom Theme Example
```json
{
  "theme": "custom",
  "colors": {
    "custom": {
      "agent": { "bg": "#4c1d95", "fg": "#e0e7ff" },
      "task": { "bg": "#059669", "fg": "#d1fae5" },
      "hook": { "bg": "#dc2626", "fg": "#fef2f2" },
      "audio": { "bg": "#7c2d12", "fg": "#fef2f2" }
    }
  }
}
```

## Data Sources

The Dev Stack segments monitor these locations:

- **Agents**: `.claude/agents/*.json` - Agent status files
- **Tasks**: `.claude/tasks/*.json` - Task tracking files  
- **Hooks**: `.claude/hooks/*.json` - Hook status files
- **Audio**: `.claude/audio/config.json` - Audio configuration

## Status Indicators

### Agent Monitor
- ○ Idle (no active agents)
- ● Active (agents running)
- ⚠ Error (agent errors detected)

### Task Tracker
- ⏸ Idle (no active tasks)
- ▶ Active (tasks running)
- ⚠ Error (task errors)

### Hook Status
- ○ Idle (no recent hook activity)
- ◉ Active (hooks recently triggered)
- ⚠ Error (hook errors)

### Audio Notifications
- 🔇 Muted/Disabled
- 🔊 Active
- ⚠ Error

## Attribution

This integration is built on top of [Claude Powerline](https://github.com/Owloops/claude-powerline) by @Owloops, licensed under MIT License. The original work provides the foundation for git integration, cost tracking, and powerline styling.

### Original Features by @Owloops:
- Core powerline rendering engine
- Git status integration
- Cost and token tracking
- Theme system
- Configuration loading

### Dev Stack Extensions:
- Agent monitoring system
- Task tracking integration
- Hook status monitoring
- Audio notification status
- PWA integration layer

## License

MIT License - See [ATTRIBUTION.md](./ATTRIBUTION.md) for full attribution details.

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Development with watch
npm run dev

# Lint
npm run lint
npm run lint:fix
```

## Troubleshooting

### Common Issues

1. **Statusline not showing Dev Stack segments**
   - Ensure the `.claude` directory exists in your project
   - Check that segment files are being created by the Dev Stack

2. **Permission errors**
   - Verify read permissions on `.claude` directory
   - Check that the statusline process can access project files

3. **Theme not applying**
   - Verify theme name in configuration
   - Check custom theme color definitions

### Debug Mode
Enable debug logging:
```bash
CLAUDE_POWERLINE_DEBUG=1 dev-stack-statusline
```

## Contributing

Contributions are welcome! Please ensure:
- All changes maintain backward compatibility with original Claude Powerline
- Dev Stack specific features are clearly separated
- Proper attribution is maintained
- Tests are included for new features