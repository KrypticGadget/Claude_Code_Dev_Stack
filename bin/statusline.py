#!/usr/bin/env python3
"""
Claude Code Terminal Statusline

Main CLI application for the terminal statusline renderer.
Provides commands for rendering, configuration, and testing.
"""

import sys
import os
import argparse
import json
import time
from typing import Optional, Dict, Any

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

from statusline import (
    StatuslineRenderer, StatuslineConfig, 
    ConfigManager, ThemeManager
)


class StatuslineCLI:
    """Command-line interface for the statusline system"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        
    def run(self):
        """Main entry point for CLI"""
        parser = self._create_parser()
        args = parser.parse_args()
        
        try:
            if hasattr(args, 'func'):
                args.func(args)
            else:
                parser.print_help()
        except KeyboardInterrupt:
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if args.debug if hasattr(args, 'debug') else False:
                raise
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="Claude Code Terminal Statusline",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s render                    # Render statusline once
  %(prog)s render --live             # Start live statusline updates
  %(prog)s config --example          # Show example configuration
  %(prog)s test                      # Test all segments
  %(prog)s theme list                # List available themes
  %(prog)s segments list             # List available segments
            """
        )
        
        parser.add_argument(
            '--config', '-c',
            help='Path to configuration file'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Render command
        render_parser = subparsers.add_parser('render', help='Render statusline')
        render_parser.add_argument(
            '--live', '-l',
            action='store_true',
            help='Enable live updates'
        )
        render_parser.add_argument(
            '--interval', '-i',
            type=float,
            default=1.0,
            help='Update interval in seconds (default: 1.0)'
        )
        render_parser.add_argument(
            '--position',
            choices=['top', 'bottom', 'inline'],
            help='Override statusline position'
        )
        render_parser.add_argument(
            '--layout',
            choices=['left', 'right', 'center', 'spread', 'justified'],
            help='Override statusline layout'
        )
        render_parser.set_defaults(func=self._cmd_render)
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_group = config_parser.add_mutually_exclusive_group(required=True)
        config_group.add_argument(
            '--show',
            action='store_true',
            help='Show current configuration'
        )
        config_group.add_argument(
            '--example',
            action='store_true',
            help='Show example configuration'
        )
        config_group.add_argument(
            '--validate',
            action='store_true',
            help='Validate configuration file'
        )
        config_group.add_argument(
            '--create',
            metavar='PATH',
            help='Create new configuration file'
        )
        config_parser.set_defaults(func=self._cmd_config)
        
        # Theme command
        theme_parser = subparsers.add_parser('theme', help='Theme management')
        theme_subparsers = theme_parser.add_subparsers(dest='theme_action', required=True)
        
        theme_list_parser = theme_subparsers.add_parser('list', help='List available themes')
        theme_list_parser.set_defaults(func=self._cmd_theme_list)
        
        theme_show_parser = theme_subparsers.add_parser('show', help='Show theme details')
        theme_show_parser.add_argument('theme_name', help='Theme name to show')
        theme_show_parser.set_defaults(func=self._cmd_theme_show)
        
        theme_test_parser = theme_subparsers.add_parser('test', help='Test theme rendering')
        theme_test_parser.add_argument('theme_name', help='Theme name to test')
        theme_test_parser.set_defaults(func=self._cmd_theme_test)
        
        # Segments command
        segments_parser = subparsers.add_parser('segments', help='Segment management')
        segments_subparsers = segments_parser.add_subparsers(dest='segments_action', required=True)
        
        segments_list_parser = segments_subparsers.add_parser('list', help='List available segments')
        segments_list_parser.set_defaults(func=self._cmd_segments_list)
        
        segments_test_parser = segments_subparsers.add_parser('test', help='Test specific segment')
        segments_test_parser.add_argument('segment_type', help='Segment type to test')
        segments_test_parser.set_defaults(func=self._cmd_segments_test)
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test statusline system')
        test_parser.add_argument(
            '--segments',
            action='store_true',
            help='Test all segments'
        )
        test_parser.add_argument(
            '--themes',
            action='store_true',
            help='Test all themes'
        )
        test_parser.add_argument(
            '--performance',
            action='store_true',
            help='Run performance tests'
        )
        test_parser.set_defaults(func=self._cmd_test)
        
        # Install command
        install_parser = subparsers.add_parser('install', help='Install shell integration')
        install_parser.add_argument(
            'shell',
            choices=['bash', 'zsh', 'fish', 'powershell'],
            help='Shell to install integration for'
        )
        install_parser.add_argument(
            '--global',
            action='store_true',
            dest='global_install',
            help='Install globally for all users'
        )
        install_parser.set_defaults(func=self._cmd_install)
        
        return parser
    
    def _load_config(self, args) -> StatuslineConfig:
        """Load configuration from args or default locations"""
        config_path = getattr(args, 'config', None)
        config = self.config_manager.load_config(config_path)
        
        # Override with command-line arguments
        if hasattr(args, 'position') and args.position:
            config.position = args.position
        if hasattr(args, 'layout') and args.layout:
            config.layout = args.layout
        if hasattr(args, 'debug') and args.debug:
            config.debug = args.debug
        
        return config
    
    def _cmd_render(self, args):
        """Render statusline command"""
        config = self._load_config(args)
        
        with StatuslineRenderer(config) as renderer:
            if args.live:
                print("Starting live statusline updates... (Press Ctrl+C to stop)")
                renderer.start_live_updates(args.interval)
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping live updates...")
                    renderer.stop_live_updates()
            else:
                # Single render
                output = renderer.render()
                print(output)
    
    def _cmd_config(self, args):
        """Configuration management command"""
        if args.show:
            config = self._load_config(args)
            exported = self.config_manager._config_to_dict(config)
            print(json.dumps(exported, indent=2))
        
        elif args.example:
            example = self.config_manager.get_example_config()
            print(json.dumps(example, indent=2))
        
        elif args.validate:
            try:
                config = self._load_config(args)
                issues = self.config_manager.validate_config(config)
                
                if issues:
                    print("Configuration issues found:")
                    for issue in issues:
                        print(f"  - {issue}")
                    sys.exit(1)
                else:
                    print("Configuration is valid")
            except Exception as e:
                print(f"Configuration error: {e}")
                sys.exit(1)
        
        elif args.create:
            try:
                default_config = self.config_manager._create_default_config()
                self.config_manager.save_config(default_config, args.create)
                print(f"Created configuration file: {args.create}")
            except Exception as e:
                print(f"Failed to create configuration: {e}")
                sys.exit(1)
    
    def _cmd_theme_list(self, args):
        """List available themes"""
        themes = self.theme_manager.list_themes()
        print("Available themes:")
        for theme_name in themes:
            print(f"  - {theme_name}")
    
    def _cmd_theme_show(self, args):
        """Show theme details"""
        try:
            theme = self.theme_manager.get_theme(args.theme_name)
            config = self.theme_manager.export_theme_config(theme)
            print(f"Theme: {args.theme_name}")
            print(json.dumps(config, indent=2))
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def _cmd_theme_test(self, args):
        """Test theme rendering"""
        try:
            config = self._load_config(args)
            theme = self.theme_manager.get_theme(args.theme_name)
            config.theme = theme
            
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"Theme '{args.theme_name}' preview:")
                print(output)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def _cmd_segments_list(self, args):
        """List available segments"""
        segments = [
            'directory', 'git', 'claude_session', 'system_info',
            'agent_status', 'network', 'time', 'custom'
        ]
        
        print("Available segments:")
        for segment in segments:
            print(f"  - {segment}")
    
    def _cmd_segments_test(self, args):
        """Test specific segment"""
        from statusline.segments import (
            DirectorySegment, GitSegment, ClaudeSessionSegment,
            SystemInfoSegment, AgentStatusSegment, NetworkSegment,
            TimeSegment, CustomSegment
        )
        from statusline.utils import ColorUtils
        from statusline.themes import DefaultTheme
        
        segment_classes = {
            'directory': DirectorySegment,
            'git': GitSegment,
            'claude_session': ClaudeSessionSegment,
            'system_info': SystemInfoSegment,
            'agent_status': AgentStatusSegment,
            'network': NetworkSegment,
            'time': TimeSegment,
            'custom': CustomSegment
        }
        
        if args.segment_type not in segment_classes:
            print(f"Unknown segment type: {args.segment_type}")
            sys.exit(1)
        
        try:
            segment_class = segment_classes[args.segment_type]
            color_utils = ColorUtils()
            theme = DefaultTheme()
            
            segment = segment_class({}, color_utils, theme)
            output = segment.render()
            
            print(f"Segment '{args.segment_type}' test:")
            print(f"Output: {output}")
            print(f"Status: {segment.get_status()}")
            
            stats = segment.get_stats()
            print(f"Stats: {json.dumps(stats, indent=2)}")
            
        except Exception as e:
            print(f"Segment test failed: {e}")
            if args.debug:
                raise
            sys.exit(1)
    
    def _cmd_test(self, args):
        """Test statusline system"""
        config = self._load_config(args)
        
        print("Testing statusline system...")
        
        # Test basic rendering
        try:
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"✓ Basic rendering works: {output}")
                
                stats = renderer.get_stats()
                print(f"✓ Renderer stats: {stats.render_count} renders, {stats.error_count} errors")
        except Exception as e:
            print(f"✗ Basic rendering failed: {e}")
            return
        
        # Test segments if requested
        if args.segments or not any([args.themes, args.performance]):
            self._test_segments(config)
        
        # Test themes if requested
        if args.themes:
            self._test_themes(config)
        
        # Performance tests if requested
        if args.performance:
            self._test_performance(config)
        
        print("\nAll tests completed!")
    
    def _test_segments(self, config: StatuslineConfig):
        """Test all configured segments"""
        print("\nTesting segments...")
        
        with StatuslineRenderer(config) as renderer:
            for segment in renderer.segments:
                try:
                    output = segment.render()
                    status = segment.get_status()
                    print(f"✓ {segment.__class__.__name__}: {output} ({status})")
                except Exception as e:
                    print(f"✗ {segment.__class__.__name__}: {e}")
    
    def _test_themes(self, config: StatuslineConfig):
        """Test all available themes"""
        print("\nTesting themes...")
        
        themes = self.theme_manager.list_themes()
        for theme_name in themes:
            try:
                theme = self.theme_manager.get_theme(theme_name)
                test_config = config
                test_config.theme = theme
                
                with StatuslineRenderer(test_config) as renderer:
                    output = renderer.render()
                    print(f"✓ {theme_name}: {output}")
            except Exception as e:
                print(f"✗ {theme_name}: {e}")
    
    def _test_performance(self, config: StatuslineConfig):
        """Run performance tests"""
        print("\nRunning performance tests...")
        
        with StatuslineRenderer(config) as renderer:
            # Test multiple renders
            start_time = time.time()
            render_count = 100
            
            for _ in range(render_count):
                renderer.render()
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / render_count
            
            print(f"✓ Performance: {render_count} renders in {total_time:.3f}s")
            print(f"✓ Average render time: {avg_time*1000:.2f}ms")
            
            stats = renderer.get_stats()
            print(f"✓ Cache hit rate: {stats.cache_hits}/{stats.cache_hits + stats.cache_misses}")
    
    def _cmd_install(self, args):
        """Install shell integration"""
        shell_scripts = {
            'bash': self._generate_bash_integration,
            'zsh': self._generate_zsh_integration,
            'fish': self._generate_fish_integration,
            'powershell': self._generate_powershell_integration
        }
        
        if args.shell not in shell_scripts:
            print(f"Unsupported shell: {args.shell}")
            sys.exit(1)
        
        try:
            script_content = shell_scripts[args.shell]()
            
            # Determine installation path
            if args.global_install:
                if args.shell == 'bash':
                    install_path = '/etc/bash.bashrc.d/statusline.sh'
                elif args.shell == 'zsh':
                    install_path = '/etc/zsh/zshrc.d/statusline.zsh'
                else:
                    print(f"Global installation not supported for {args.shell}")
                    sys.exit(1)
            else:
                home = os.path.expanduser('~')
                if args.shell == 'bash':
                    install_path = os.path.join(home, '.bashrc.d', 'statusline.sh')
                elif args.shell == 'zsh':
                    install_path = os.path.join(home, '.zshrc.d', 'statusline.zsh')
                elif args.shell == 'fish':
                    install_path = os.path.join(home, '.config', 'fish', 'conf.d', 'statusline.fish')
                elif args.shell == 'powershell':
                    install_path = os.path.join(home, 'Documents', 'PowerShell', 'Profile.ps1')
            
            # Create directory if needed
            os.makedirs(os.path.dirname(install_path), exist_ok=True)
            
            # Write script
            with open(install_path, 'w') as f:
                f.write(script_content)
            
            print(f"✓ Installed {args.shell} integration to: {install_path}")
            print(f"✓ Restart your shell or source the file to activate")
            
        except Exception as e:
            print(f"Installation failed: {e}")
            sys.exit(1)
    
    def _generate_bash_integration(self) -> str:
        """Generate bash integration script"""
        script_path = os.path.abspath(__file__)
        return f'''# Claude Code Statusline Integration for Bash

# Function to update statusline
function _claude_statusline_update() {{
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$("{script_path}" render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        fi
    fi
}}

# Update statusline before each prompt
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_claude_statusline_update"
else
    PROMPT_COMMAND="$PROMPT_COMMAND; _claude_statusline_update"
fi
'''
    
    def _generate_zsh_integration(self) -> str:
        """Generate zsh integration script"""
        script_path = os.path.abspath(__file__)
        return f'''# Claude Code Statusline Integration for Zsh

# Function to update statusline
function _claude_statusline_update() {{
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$("{script_path}" render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        fi
    fi
}}

# Add to precmd hooks
autoload -Uz add-zsh-hook
add-zsh-hook precmd _claude_statusline_update
'''
    
    def _generate_fish_integration(self) -> str:
        """Generate fish shell integration script"""
        script_path = os.path.abspath(__file__)
        return f'''# Claude Code Statusline Integration for Fish

# Function to update statusline
function _claude_statusline_update --on-event fish_prompt
    if test "$TERM" != "dumb"; and isatty stdout
        set statusline_output ("{script_path}" render 2>/dev/null)
        if test $status -eq 0; and test -n "$statusline_output"
            echo -e "\\033[s\\033[1;1H$statusline_output\\033[K\\033[u"
        end
    end
end
'''
    
    def _generate_powershell_integration(self) -> str:
        """Generate PowerShell integration script"""
        script_path = os.path.abspath(__file__)
        return f'''# Claude Code Statusline Integration for PowerShell

# Function to update statusline
function Update-ClaudeStatusline {{
    if ($Host.UI.RawUI.WindowSize) {{
        try {{
            $statuslineOutput = & python "{script_path}" render 2>$null
            if ($LASTEXITCODE -eq 0 -and $statuslineOutput) {{
                $position = $Host.UI.RawUI.CursorPosition
                $Host.UI.RawUI.CursorPosition = @{{X=0; Y=0}}
                Write-Host $statuslineOutput -NoNewline
                $Host.UI.RawUI.CursorPosition = $position
            }}
        }} catch {{
            # Silently ignore errors
        }}
    }}
}}

# Update statusline with each prompt
$function:prompt = {{
    Update-ClaudeStatusline
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}}
'''


def main():
    """Main entry point"""
    cli = StatuslineCLI()
    cli.run()


if __name__ == '__main__':
    main()