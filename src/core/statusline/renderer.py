"""
Terminal Statusline Renderer

Main renderer class that coordinates all statusline segments and handles
terminal output with proper color support and performance optimization.
"""

import sys
import os
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .config import StatuslineConfig
from .segments.base import BaseSegment
from .themes import Theme
from .utils import TerminalUtils, ColorUtils


@dataclass
class RendererStats:
    """Performance and usage statistics for the renderer"""
    render_count: int = 0
    last_render_time: float = 0.0
    average_render_time: float = 0.0
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class StatuslineRenderer:
    """
    Main statusline renderer that coordinates segments and handles terminal output
    """
    
    def __init__(self, config: StatuslineConfig):
        self.config = config
        self.segments: List[BaseSegment] = []
        self.theme = config.theme
        self.terminal = TerminalUtils()
        self.color_utils = ColorUtils(self.terminal.supports_color())
        self.stats = RendererStats()
        
        # Cache and performance
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = 1.0  # 1 second cache timeout
        self._last_update = 0.0
        
        # Threading for async updates
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # Terminal state
        self._terminal_width = self.terminal.get_width()
        self._last_output = ""
        
        self._setup_segments()
    
    def _setup_segments(self):
        """Initialize segments based on configuration"""
        from .segments import (
            DirectorySegment, GitSegment, ClaudeSessionSegment,
            SystemInfoSegment, AgentStatusSegment, NetworkSegment,
            TimeSegment, CustomSegment
        )
        
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
        
        for segment_config in self.config.segments:
            segment_type = segment_config.type
            if segment_type in segment_classes:
                segment_class = segment_classes[segment_type]
                segment = segment_class(segment_config.config, self.color_utils, self.theme)
                self.segments.append(segment)
    
    def add_segment(self, segment: BaseSegment):
        """Add a custom segment to the statusline"""
        with self._lock:
            self.segments.append(segment)
    
    def remove_segment(self, segment_id: str):
        """Remove a segment by ID"""
        with self._lock:
            self.segments = [s for s in self.segments if s.id != segment_id]
    
    def render(self, force_refresh: bool = False) -> str:
        """
        Render the complete statusline
        
        Args:
            force_refresh: If True, bypasses cache and forces segment updates
            
        Returns:
            Formatted statusline string ready for terminal output
        """
        start_time = time.time()
        
        try:
            # Check if we need to update based on cache timeout
            current_time = time.time()
            if not force_refresh and (current_time - self._last_update) < self._cache_timeout:
                if 'rendered_output' in self._cache:
                    self.stats.cache_hits += 1
                    return self._cache['rendered_output']
            
            self.stats.cache_misses += 1
            self._last_update = current_time
            
            # Get terminal width for responsive layout
            terminal_width = self.terminal.get_width()
            if terminal_width != self._terminal_width:
                self._terminal_width = terminal_width
                force_refresh = True
            
            # Render each segment
            rendered_segments = []
            total_length = 0
            
            with self._lock:
                for segment in self.segments:
                    if not segment.enabled:
                        continue
                    
                    try:
                        segment_output = segment.render(force_refresh)
                        if segment_output:
                            rendered_segments.append(segment_output)
                            # Calculate approximate display length (ignoring color codes)
                            display_length = len(self.color_utils.strip_ansi(segment_output))
                            total_length += display_length
                    except Exception as e:
                        self.stats.error_count += 1
                        if self.config.debug:
                            print(f"Error rendering segment {segment.id}: {e}", file=sys.stderr)
            
            # Apply layout and spacing
            output = self._apply_layout(rendered_segments, total_length, terminal_width)
            
            # Cache the result
            self._cache['rendered_output'] = output
            
            # Update stats
            render_time = time.time() - start_time
            self.stats.render_count += 1
            self.stats.last_render_time = render_time
            if self.stats.render_count == 1:
                self.stats.average_render_time = render_time
            else:
                self.stats.average_render_time = (
                    (self.stats.average_render_time * (self.stats.render_count - 1) + render_time) 
                    / self.stats.render_count
                )
            
            return output
            
        except Exception as e:
            self.stats.error_count += 1
            if self.config.debug:
                print(f"Error in statusline render: {e}", file=sys.stderr)
            return self._get_error_output(str(e))
    
    def _apply_layout(self, segments: List[str], total_length: int, terminal_width: int) -> str:
        """Apply layout strategy to arrange segments"""
        if not segments:
            return ""
        
        layout = self.config.layout
        
        if layout == 'left':
            return self._layout_left(segments)
        elif layout == 'right':
            return self._layout_right(segments, terminal_width)
        elif layout == 'center':
            return self._layout_center(segments, terminal_width)
        elif layout == 'spread':
            return self._layout_spread(segments, terminal_width)
        elif layout == 'justified':
            return self._layout_justified(segments, total_length, terminal_width)
        else:
            return self._layout_left(segments)  # Default fallback
    
    def _layout_left(self, segments: List[str]) -> str:
        """Left-aligned layout"""
        separator = self.theme.separator if hasattr(self.theme, 'separator') else ' '
        return separator.join(segments)
    
    def _layout_right(self, segments: List[str], terminal_width: int) -> str:
        """Right-aligned layout"""
        separator = self.theme.separator if hasattr(self.theme, 'separator') else ' '
        content = separator.join(segments)
        content_length = len(self.color_utils.strip_ansi(content))
        
        if content_length < terminal_width:
            padding = ' ' * (terminal_width - content_length)
            return padding + content
        return content
    
    def _layout_center(self, segments: List[str], terminal_width: int) -> str:
        """Center-aligned layout"""
        separator = self.theme.separator if hasattr(self.theme, 'separator') else ' '
        content = separator.join(segments)
        content_length = len(self.color_utils.strip_ansi(content))
        
        if content_length < terminal_width:
            total_padding = terminal_width - content_length
            left_padding = total_padding // 2
            right_padding = total_padding - left_padding
            return ' ' * left_padding + content + ' ' * right_padding
        return content
    
    def _layout_spread(self, segments: List[str], terminal_width: int) -> str:
        """Spread segments evenly across terminal width"""
        if len(segments) <= 1:
            return segments[0] if segments else ""
        
        total_content_length = sum(len(self.color_utils.strip_ansi(seg)) for seg in segments)
        available_space = terminal_width - total_content_length
        
        if available_space <= 0:
            return ' '.join(segments)
        
        spacing_per_gap = available_space // (len(segments) - 1)
        extra_spaces = available_space % (len(segments) - 1)
        
        result = segments[0]
        for i, segment in enumerate(segments[1:], 1):
            spaces = spacing_per_gap + (1 if i <= extra_spaces else 0)
            result += ' ' * spaces + segment
        
        return result
    
    def _layout_justified(self, segments: List[str], total_length: int, terminal_width: int) -> str:
        """Justified layout with left and right aligned segments"""
        if len(segments) <= 1:
            return self._layout_left(segments)
        
        # Split segments into left and right groups
        mid_point = len(segments) // 2
        left_segments = segments[:mid_point]
        right_segments = segments[mid_point:]
        
        left_content = ' '.join(left_segments)
        right_content = ' '.join(right_segments)
        
        left_length = len(self.color_utils.strip_ansi(left_content))
        right_length = len(self.color_utils.strip_ansi(right_content))
        
        available_space = terminal_width - left_length - right_length
        
        if available_space > 0:
            return left_content + ' ' * available_space + right_content
        else:
            return left_content + ' ' + right_content
    
    def _get_error_output(self, error_msg: str) -> str:
        """Generate error output when rendering fails"""
        error_color = self.color_utils.colorize("[ERROR]", "red")
        return f"{error_color} Statusline render failed: {error_msg}"
    
    def start_live_updates(self, interval: float = 1.0):
        """Start background thread for live statusline updates"""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._update_thread = threading.Thread(
            target=self._update_loop,
            args=(interval,),
            daemon=True
        )
        self._update_thread.start()
    
    def stop_live_updates(self):
        """Stop background updates"""
        if self._update_thread:
            self._stop_event.set()
            self._update_thread.join(timeout=2.0)
    
    def _update_loop(self, interval: float):
        """Background update loop for live updates"""
        while not self._stop_event.is_set():
            try:
                output = self.render()
                if output != self._last_output:
                    self._last_output = output
                    self._write_to_terminal(output)
                
                self._stop_event.wait(interval)
            except Exception as e:
                if self.config.debug:
                    print(f"Error in update loop: {e}", file=sys.stderr)
                break
    
    def _write_to_terminal(self, output: str):
        """Write output to terminal with proper positioning"""
        if self.config.position == 'top':
            # Save cursor, move to top, write, restore cursor
            sys.stdout.write(f"\033[s\033[1;1H{output}\033[K\033[u")
        elif self.config.position == 'bottom':
            # Move to bottom, write
            rows = self.terminal.get_height()
            sys.stdout.write(f"\033[{rows};1H{output}\033[K")
        else:
            # Just write at current position
            sys.stdout.write(f"{output}\n")
        
        sys.stdout.flush()
    
    def get_stats(self) -> RendererStats:
        """Get renderer performance statistics"""
        return self.stats
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = RendererStats()
    
    def clear_cache(self):
        """Clear the renderer cache"""
        with self._lock:
            self._cache.clear()
    
    def update_config(self, new_config: StatuslineConfig):
        """Update configuration and reinitialize segments"""
        self.config = new_config
        self.theme = new_config.theme
        self.segments.clear()
        self._setup_segments()
        self.clear_cache()
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration as dictionary"""
        return {
            'segments': [
                {
                    'type': segment.__class__.__name__.lower().replace('segment', ''),
                    'enabled': segment.enabled,
                    'config': segment.config
                }
                for segment in self.segments
            ],
            'theme': self.theme.__class__.__name__,
            'layout': self.config.layout,
            'position': self.config.position,
            'update_interval': self.config.update_interval
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.stop_live_updates()