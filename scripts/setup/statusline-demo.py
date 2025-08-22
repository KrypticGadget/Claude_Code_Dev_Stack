#!/usr/bin/env python3
"""
Statusline Demo Script

Demonstrates the capabilities of the Claude Code terminal statusline system
with various themes, configurations, and live examples.
"""

import sys
import os
import time
import random
import threading
from pathlib import Path

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

from statusline import (
    StatuslineRenderer, StatuslineConfig, ConfigManager, 
    ThemeManager, DefaultTheme, MinimalTheme, PowerlineTheme
)
from statusline.segments import (
    DirectorySegment, GitSegment, ClaudeSessionSegment,
    SystemInfoSegment, AgentStatusSegment, NetworkSegment,
    TimeSegment, CustomSegment
)
from statusline.utils import ColorUtils


class StatuslineDemo:
    """Interactive demo of statusline capabilities"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.running = False
        
    def run_demo(self):
        """Run the complete demo"""
        print("🎨 Claude Code Terminal Statusline Demo")
        print("=" * 50)
        
        try:
            self._welcome_message()
            self._demo_basic_rendering()
            self._demo_themes()
            self._demo_segments()
            self._demo_live_updates()
            self._demo_customization()
            
            print("\n🎉 Demo completed! Thank you for trying the statusline system.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user. Thanks for watching!")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
    
    def _welcome_message(self):
        """Display welcome message"""
        print("\nThis demo showcases the Claude Code terminal statusline system.")
        print("The statusline provides real-time information about your development environment:")
        print("  • Current directory and git status")
        print("  • Claude session information")
        print("  • System performance metrics")
        print("  • Active agents and network status")
        print("  • Customizable themes and segments")
        
        input("\nPress Enter to continue...")
    
    def _demo_basic_rendering(self):
        """Demonstrate basic statusline rendering"""
        print("\n📋 Basic Rendering Demo")
        print("-" * 25)
        
        # Create basic configuration
        config = self.config_manager._create_default_config()
        config.debug = False
        
        print("Default statusline configuration:")
        with StatuslineRenderer(config) as renderer:
            output = renderer.render()
            print(f"Output: {output}")
            
            stats = renderer.get_stats()
            print(f"Render time: {stats.last_render_time*1000:.2f}ms")
        
        input("\nPress Enter to continue...")
    
    def _demo_themes(self):
        """Demonstrate different themes"""
        print("\n🎨 Theme Demo")
        print("-" * 15)
        
        themes = {
            'default': DefaultTheme(),
            'minimal': MinimalTheme(),
            'powerline': PowerlineTheme()
        }
        
        config = self.config_manager._create_default_config()
        
        for theme_name, theme in themes.items():
            print(f"\n{theme_name.title()} Theme:")
            config.theme = theme
            
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"  {output}")
        
        input("\nPress Enter to continue...")
    
    def _demo_segments(self):
        """Demonstrate individual segments"""
        print("\n🧩 Segment Demo")
        print("-" * 17)
        
        color_utils = ColorUtils()
        theme = DefaultTheme()
        
        # Test each segment type
        segments = [
            ('Directory', DirectorySegment, {}),
            ('Git', GitSegment, {}),
            ('Claude Session', ClaudeSessionSegment, {}),
            ('System Info', SystemInfoSegment, {'show_cpu': True, 'show_memory': True}),
            ('Agent Status', AgentStatusSegment, {}),
            ('Network', NetworkSegment, {}),
            ('Time', TimeSegment, {'show_seconds': True}),
            ('Custom', CustomSegment, {
                'label': 'Demo',
                'data_source_type': 'env',
                'env_variable': 'USER',
                'env_default': 'unknown'
            })
        ]
        
        for name, segment_class, config in segments:
            print(f"\n{name} Segment:")
            try:
                segment = segment_class(config, color_utils, theme)
                output = segment.render()
                status = segment.get_status()
                print(f"  Output: {output}")
                print(f"  Status: {status}")
            except Exception as e:
                print(f"  Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def _demo_live_updates(self):
        """Demonstrate live updating capabilities"""
        print("\n🔄 Live Updates Demo")
        print("-" * 20)
        
        print("Starting live statusline updates for 10 seconds...")
        print("Watch the time segment update in real-time!")
        print("(You can press Ctrl+C to stop early)")
        
        config = self.config_manager._create_default_config()
        config.update_interval = 1.0
        
        start_time = time.time()
        
        try:
            with StatuslineRenderer(config) as renderer:
                # Start live updates
                renderer.start_live_updates(1.0)
                
                # Run for 10 seconds or until interrupted
                while time.time() - start_time < 10:
                    time.sleep(0.5)
                
                renderer.stop_live_updates()
                
        except KeyboardInterrupt:
            print("\nLive updates stopped by user.")
        
        print("\nLive updates demo completed.")
        input("Press Enter to continue...")
    
    def _demo_customization(self):
        """Demonstrate customization options"""
        print("\n⚙️  Customization Demo")
        print("-" * 22)
        
        print("Different layout options:")
        
        layouts = ['left', 'right', 'center', 'spread', 'justified']
        config = self.config_manager._create_default_config()
        
        for layout in layouts:
            print(f"\n{layout.title()} layout:")
            config.layout = layout
            
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"  {output}")
        
        print("\nDifferent position options:")
        positions = ['top', 'bottom', 'inline']
        
        for position in positions:
            print(f"\n{position.title()} position:")
            config.position = position
            config.layout = 'left'  # Reset layout
            
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"  {output}")
        
        input("\nPress Enter to continue...")
    
    def _interactive_demo(self):
        """Interactive demo mode"""
        print("\n🎮 Interactive Demo Mode")
        print("-" * 24)
        
        config = self.config_manager._create_default_config()
        
        while True:
            print("\nOptions:")
            print("1. Change theme")
            print("2. Change layout")
            print("3. Toggle segments")
            print("4. Live updates")
            print("5. Performance test")
            print("0. Exit")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self._interactive_theme_selection(config)
            elif choice == '2':
                self._interactive_layout_selection(config)
            elif choice == '3':
                self._interactive_segment_toggle(config)
            elif choice == '4':
                self._interactive_live_updates(config)
            elif choice == '5':
                self._interactive_performance_test(config)
            else:
                print("Invalid option. Please try again.")
    
    def _interactive_theme_selection(self, config):
        """Interactive theme selection"""
        themes = self.theme_manager.list_themes()
        
        print("\nAvailable themes:")
        for i, theme_name in enumerate(themes, 1):
            print(f"{i}. {theme_name}")
        
        try:
            choice = int(input(f"\nSelect theme (1-{len(themes)}): ")) - 1
            if 0 <= choice < len(themes):
                theme_name = themes[choice]
                config.theme = self.theme_manager.get_theme(theme_name)
                
                with StatuslineRenderer(config) as renderer:
                    output = renderer.render()
                    print(f"\nPreview with {theme_name} theme:")
                    print(f"  {output}")
            else:
                print("Invalid selection.")
        except (ValueError, IndexError):
            print("Invalid input.")
    
    def _interactive_layout_selection(self, config):
        """Interactive layout selection"""
        layouts = ['left', 'right', 'center', 'spread', 'justified']
        
        print("\nAvailable layouts:")
        for i, layout in enumerate(layouts, 1):
            print(f"{i}. {layout}")
        
        try:
            choice = int(input(f"\nSelect layout (1-{len(layouts)}): ")) - 1
            if 0 <= choice < len(layouts):
                config.layout = layouts[choice]
                
                with StatuslineRenderer(config) as renderer:
                    output = renderer.render()
                    print(f"\nPreview with {layouts[choice]} layout:")
                    print(f"  {output}")
            else:
                print("Invalid selection.")
        except (ValueError, IndexError):
            print("Invalid input.")
    
    def _interactive_segment_toggle(self, config):
        """Interactive segment toggling"""
        print("\nCurrent segments:")
        for i, segment in enumerate(config.segments, 1):
            status = "enabled" if segment.enabled else "disabled"
            print(f"{i}. {segment.type} ({status})")
        
        try:
            choice = int(input(f"\nSelect segment to toggle (1-{len(config.segments)}): ")) - 1
            if 0 <= choice < len(config.segments):
                segment = config.segments[choice]
                segment.enabled = not segment.enabled
                status = "enabled" if segment.enabled else "disabled"
                print(f"Toggled {segment.type} segment: {status}")
                
                with StatuslineRenderer(config) as renderer:
                    output = renderer.render()
                    print(f"\nUpdated statusline:")
                    print(f"  {output}")
            else:
                print("Invalid selection.")
        except (ValueError, IndexError):
            print("Invalid input.")
    
    def _interactive_live_updates(self, config):
        """Interactive live updates"""
        duration = input("Enter duration in seconds (default 5): ").strip()
        try:
            duration = float(duration) if duration else 5.0
        except ValueError:
            duration = 5.0
        
        print(f"\nStarting live updates for {duration} seconds...")
        
        try:
            with StatuslineRenderer(config) as renderer:
                renderer.start_live_updates(1.0)
                time.sleep(duration)
                renderer.stop_live_updates()
                
                stats = renderer.get_stats()
                print(f"\nLive updates completed.")
                print(f"Total renders: {stats.render_count}")
                print(f"Average render time: {stats.average_render_time*1000:.2f}ms")
                
        except KeyboardInterrupt:
            print("\nLive updates interrupted.")
    
    def _interactive_performance_test(self, config):
        """Interactive performance test"""
        render_count = input("Enter number of renders (default 100): ").strip()
        try:
            render_count = int(render_count) if render_count else 100
        except ValueError:
            render_count = 100
        
        print(f"\nRunning performance test with {render_count} renders...")
        
        with StatuslineRenderer(config) as renderer:
            start_time = time.time()
            
            for _ in range(render_count):
                renderer.render()
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / render_count
            
            stats = renderer.get_stats()
            
            print(f"\nPerformance test results:")
            print(f"Total time: {total_time:.3f}s")
            print(f"Average render time: {avg_time*1000:.2f}ms")
            print(f"Renders per second: {render_count/total_time:.1f}")
            print(f"Cache hit rate: {stats.cache_hits}/{stats.cache_hits + stats.cache_misses}")
    
    def _demo_error_handling(self):
        """Demonstrate error handling"""
        print("\n🛠️  Error Handling Demo")
        print("-" * 23)
        
        print("Testing error conditions...")
        
        # Test with invalid configuration
        try:
            from statusline.config import SegmentConfig
            
            config = self.config_manager._create_default_config()
            
            # Add an invalid segment
            invalid_segment = SegmentConfig(type='nonexistent')
            config.segments.append(invalid_segment)
            
            with StatuslineRenderer(config) as renderer:
                output = renderer.render()
                print(f"With invalid segment: {output}")
                
                stats = renderer.get_stats()
                print(f"Errors: {stats.error_count}")
                
        except Exception as e:
            print(f"Handled error: {e}")
        
        input("\nPress Enter to continue...")


def main():
    """Main demo entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Statusline Demo")
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive demo mode')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Run quick demo (skip interactive parts)')
    
    args = parser.parse_args()
    
    demo = StatuslineDemo()
    
    if args.interactive:
        demo._interactive_demo()
    elif args.quick:
        # Quick non-interactive demo
        config = demo.config_manager._create_default_config()
        with StatuslineRenderer(config) as renderer:
            output = renderer.render()
            print(f"Quick demo output: {output}")
    else:
        demo.run_demo()


if __name__ == '__main__':
    main()