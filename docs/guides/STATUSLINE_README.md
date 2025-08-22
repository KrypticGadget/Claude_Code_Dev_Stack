# Claude Code Terminal Statusline

A comprehensive Python-based terminal statusline system with customizable segments, real-time updates, and cross-platform compatibility.

## Features

### 🎨 **Customizable Themes**
- **Default Theme**: Clean and simple styling
- **Minimal Theme**: Reduced visual elements for distraction-free work
- **Powerline Theme**: Modern powerline-style with arrows and colors
- **Terminal Theme**: Maximum compatibility with all terminal types
- **Nerd Font Theme**: Rich icons and symbols for enhanced displays
- **Custom Themes**: Define your own color schemes and styling

### 📊 **Intelligent Segments**

#### Directory Segment
- Current working directory with smart truncation
- Home directory replacement (`~`)
- Git repository root detection
- Folder icons and status indicators

#### Git Segment
- Branch name and status
- File modification indicators (modified, added, deleted, untracked)
- Ahead/behind tracking with remote repository
- Stash count display
- Conflict detection

#### Claude Session Segment
- Active session duration
- Token usage tracking with warning thresholds
- Model information display
- Conversation count
- Session health indicators

#### System Information Segment
- CPU usage with configurable thresholds
- Memory usage monitoring
- System load average (Unix systems)
- Disk usage tracking
- Network connectivity status

#### Agent Status Segment
- Active Claude Code agents display
- Agent tier distribution
- Current executing agent
- Agent health monitoring

#### Network Segment
- Internet connectivity testing
- Tunnel status (ngrok, SSH, CloudFlare)
- Ping time display
- IP address information

#### Time Segment
- Customizable time and date formats
- Timezone information
- Relative time descriptions
- Session uptime tracking
- World clock support

#### Custom Segment
- Command execution output
- File content monitoring
- API endpoint polling
- Environment variable display
- Script output integration

### 🖥️ **Terminal Compatibility**

#### Cross-Platform Support
- **Windows**: Command Prompt, PowerShell, Windows Terminal
- **macOS**: Terminal.app, iTerm2, Alacritty
- **Linux**: Bash, Zsh, Fish shells
- **Universal**: Any ANSI-compatible terminal

#### Color and Unicode Support
- Automatic color capability detection
- Graceful fallback for limited terminals
- Unicode symbol support with ASCII alternatives
- 256-color and truecolor support where available

### ⚡ **Performance Optimization**

#### Intelligent Caching
- Segment-level caching with configurable timeouts
- Multi-level cache system
- Smart cache invalidation
- Background refresh capabilities

#### Async Operations
- Non-blocking data collection
- Threaded updates for live mode
- Timeout protection for external calls
- Resource usage monitoring

### ⚙️ **Configuration System**

#### Flexible Configuration
- YAML and JSON configuration support
- Per-segment configuration options
- Runtime configuration updates
- Environment variable overrides

#### Layout Options
- **Left**: Traditional left-aligned layout
- **Right**: Right-aligned positioning
- **Center**: Centered display
- **Spread**: Evenly distributed segments
- **Justified**: Left and right aligned groups

## Installation

### Quick Install
```bash
# Clone or navigate to the Claude Code project
cd path/to/Claude_Code_Agents/V3.6.9

# Run the installation script
python scripts/install-statusline.py

# Or install with shell integration
python scripts/install-statusline.py --shells bash zsh
```

### Manual Installation

1. **Install Dependencies**
   ```bash
   pip install pyyaml psutil  # Optional: for enhanced features
   ```

2. **Copy Configuration**
   ```bash
   mkdir -p ~/.config/claude-code
   cp config/statusline.yml ~/.config/claude-code/
   ```

3. **Install Binary**
   ```bash
   cp bin/statusline.py ~/.local/bin/claude-statusline
   chmod +x ~/.local/bin/claude-statusline
   ```

4. **Shell Integration**
   ```bash
   # For Bash
   echo 'source <(claude-statusline shell bash)' >> ~/.bashrc
   
   # For Zsh
   echo 'source <(claude-statusline shell zsh)' >> ~/.zshrc
   
   # For Fish
   claude-statusline shell fish >> ~/.config/fish/config.fish
   ```

## Usage

### Command Line Interface

```bash
# Render statusline once
claude-statusline render

# Start live updates
claude-statusline render --live

# Show configuration
claude-statusline config --show

# List available themes
claude-statusline theme list

# Test specific segment
claude-statusline segments test git

# Install shell integration
claude-statusline install bash

# Run system tests
claude-statusline test
```

### Configuration

#### Basic Configuration (`~/.config/claude-code/statusline.yml`)

```yaml
# Display settings
layout: justified
position: bottom
theme: powerline

# Performance settings
update_interval: 1.0
cache_timeout: 1.0

# Segment configuration
segments:
  - type: directory
    enabled: true
    priority: 10
    config:
      max_depth: 3
      show_home_tilde: true
      
  - type: git
    enabled: true
    priority: 20
    config:
      show_branch: true
      show_status: true
      
  - type: claude_session
    enabled: true
    priority: 30
    config:
      show_token_usage: true
      token_warning_threshold: 80
      
  - type: system_info
    enabled: true
    priority: 40
    config:
      show_cpu: true
      show_memory: true
      
  - type: time
    enabled: true
    priority: 50
    config:
      format: "%H:%M:%S"
```

#### Custom Segment Examples

```yaml
# Weather information
- type: custom
  enabled: true
  priority: 60
  config:
    label: "Weather"
    data_source_type: "api"
    api_url: "https://wttr.in/?format=3"
    format_template: "🌤 {data}"

# Git commit count
- type: custom
  enabled: true
  priority: 25
  config:
    label: "Commits"
    data_source_type: "command"
    data_source: "git rev-list --count HEAD"
    value_type: "number"
    format_template: "📝 {data}"

# System uptime
- type: custom
  enabled: true
  priority: 45
  config:
    label: "Uptime"
    data_source_type: "command"
    data_source: "uptime -p"
    format_template: "⏱ {data}"
```

### Theme Customization

#### Custom Theme Definition

```yaml
theme:
  name: "custom"
  colors:
    directory: "cyan"
    git_clean: "green"
    git_dirty: "yellow"
    claude_active: "magenta"
    system_normal: "blue"
    time: "white"
  separator: " :: "
  segments:
    directory:
      default:
        fg: "cyan"
        bold: true
    git:
      clean:
        fg: "green"
        bold: true
      dirty:
        fg: "yellow"
        bold: true
```

### Advanced Features

#### Live Updates
```bash
# Start with custom interval
claude-statusline render --live --interval 2.0

# With specific position
claude-statusline render --live --position top
```

#### Performance Monitoring
```bash
# Run performance tests
claude-statusline test --performance

# Monitor segment performance
claude-statusline segments test --all --stats
```

#### Integration with Scripts
```python
#!/usr/bin/env python3
from statusline import StatuslineRenderer, ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Render statusline
with StatuslineRenderer(config) as renderer:
    output = renderer.render()
    print(output)
```

## Shell Integration

### Bash Integration
```bash
# Add to ~/.bashrc
function _claude_statusline_update() {
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$(claude-statusline render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            printf '\033[s\033[1;1H%s\033[K\033[u' "$statusline_output"
        fi
    fi
}

# Update before each prompt
PROMPT_COMMAND="_claude_statusline_update${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
```

### PowerShell Integration
```powershell
# Add to $PROFILE
function Update-ClaudeStatusline {
    if ($Host.UI.RawUI.WindowSize) {
        try {
            $statuslineOutput = & claude-statusline render 2>$null
            if ($LASTEXITCODE -eq 0 -and $statuslineOutput) {
                $position = $Host.UI.RawUI.CursorPosition
                $Host.UI.RawUI.CursorPosition = @{X=0; Y=0}
                Write-Host $statuslineOutput -NoNewline
                $Host.UI.RawUI.CursorPosition = $position
            }
        } catch {
            # Silently ignore errors
        }
    }
}

$function:prompt = {
    Update-ClaudeStatusline
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}
```

## Development

### Project Structure
```
core/statusline/
├── __init__.py           # Main module exports
├── renderer.py           # Core rendering engine
├── config.py            # Configuration management
├── themes.py            # Theme system
├── utils.py             # Utility functions
└── segments/            # Segment implementations
    ├── __init__.py
    ├── base.py          # Base segment class
    ├── directory.py     # Directory segment
    ├── git.py           # Git segment
    ├── claude_session.py # Claude session segment
    ├── system_info.py   # System information
    ├── agent_status.py  # Agent status
    ├── network.py       # Network status
    ├── time.py          # Time and date
    └── custom.py        # Custom segments

bin/
└── statusline.py        # Main CLI application

scripts/
├── install-statusline.py              # Installation script
├── statusline-demo.py                  # Interactive demo
├── statusline-shell-integration.sh    # Unix shell integration
└── statusline-shell-integration.bat   # Windows integration

config/
└── statusline.yml       # Default configuration
```

### Creating Custom Segments

```python
from statusline.segments.base import BaseSegment, SegmentData

class MyCustomSegment(BaseSegment):
    def _collect_data(self) -> SegmentData:
        # Gather your data
        content = "My Data"
        status = "normal"
        
        return SegmentData(
            content=content,
            status=status,
            tooltip="Custom segment tooltip"
        )
    
    def _format_data(self, data: SegmentData) -> str:
        # Format for display
        return data.content
```

### Testing

```bash
# Run all tests
claude-statusline test

# Test specific components
claude-statusline test --segments
claude-statusline test --themes
claude-statusline test --performance

# Test individual segment
claude-statusline segments test directory
```

## Troubleshooting

### Common Issues

#### Statusline Not Appearing
1. Check shell integration: `claude-statusline config --validate`
2. Test rendering: `claude-statusline render`
3. Verify terminal compatibility: Check `$TERM` environment variable
4. Review shell configuration for conflicts

#### Performance Issues
1. Increase cache timeouts in configuration
2. Disable expensive segments temporarily
3. Check system resource usage
4. Run performance test: `claude-statusline test --performance`

#### Color/Unicode Issues
1. Verify terminal capabilities: `echo $TERM`
2. Check locale settings: `locale`
3. Try minimal theme: Set `theme: minimal` in config
4. Disable Unicode: Set `unicode_support: false`

### Debug Mode
```bash
# Enable debug output
claude-statusline render --debug

# Verbose configuration validation
claude-statusline config --validate --debug
```

### Log Files
- Configuration: `~/.config/claude-code/statusline.yml`
- Cache: `~/.cache/claude-code/statusline/`
- Logs: `~/.cache/claude-code/logs/statusline.log`

## Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd Claude_Code_Agents/V3.6.9

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run demo
python scripts/statusline-demo.py
```

### Adding New Segments
1. Create segment file in `core/statusline/segments/`
2. Inherit from `BaseSegment`
3. Implement `_collect_data()` and `_format_data()`
4. Add to segment registry in `__init__.py`
5. Add configuration options
6. Write tests

### Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include error handling
- Write unit tests
- Update documentation

## License

This project is part of the Claude Code Agents system. See the main project license for details.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting guide above
2. Review existing issues in the project repository
3. Create a new issue with detailed information
4. Include system information and configuration

---

**Claude Code Terminal Statusline** - Bringing intelligence and style to your terminal experience! 🚀