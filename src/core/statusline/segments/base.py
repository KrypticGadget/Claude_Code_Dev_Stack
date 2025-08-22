"""
Base Segment Class

Abstract base class for all statusline segments, defining the interface
and common functionality for segment implementation.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..utils import ColorUtils
from ..themes import Theme


@dataclass
class SegmentData:
    """Data structure for segment content and metadata"""
    content: str
    status: str = 'normal'
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    clickable: bool = False
    priority: int = 100


class BaseSegment(ABC):
    """
    Abstract base class for all statusline segments
    
    Segments are responsible for:
    1. Gathering their specific data
    2. Formatting the data for display
    3. Managing their own caching and updates
    4. Providing status information
    """
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        """
        Initialize segment with configuration
        
        Args:
            config: Segment-specific configuration
            color_utils: Color utility instance
            theme: Theme instance for styling
        """
        self.config = config
        self.color_utils = color_utils
        self.theme = theme
        
        # Basic properties
        self.id = self._generate_id()
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 100)
        self.cache_timeout = config.get('cache_timeout', 1.0)
        self.max_width = config.get('max_width')
        
        # Cache management
        self._cache: Dict[str, Any] = {}
        self._last_update = 0.0
        self._error_count = 0
        self._last_error = None
        
        # Performance tracking
        self._render_count = 0
        self._total_render_time = 0.0
    
    def _generate_id(self) -> str:
        """Generate unique ID for this segment"""
        base_name = self.__class__.__name__.lower().replace('segment', '')
        return f"{base_name}_{id(self)}"
    
    @abstractmethod
    def _collect_data(self) -> SegmentData:
        """
        Collect data for this segment
        
        This method should gather all necessary information and return
        a SegmentData object with the content and metadata.
        
        Returns:
            SegmentData object with segment information
        """
        pass
    
    @abstractmethod
    def _format_data(self, data: SegmentData) -> str:
        """
        Format collected data for display
        
        Args:
            data: SegmentData object to format
            
        Returns:
            Formatted string ready for display
        """
        pass
    
    def render(self, force_refresh: bool = False) -> str:
        """
        Render the segment
        
        Args:
            force_refresh: If True, bypasses cache and forces data collection
            
        Returns:
            Formatted segment string
        """
        if not self.enabled:
            return ""
        
        start_time = time.time()
        
        try:
            # Check cache
            current_time = time.time()
            if not force_refresh and self._should_use_cache(current_time):
                return self._cache.get('rendered', '')
            
            # Collect fresh data
            data = self._collect_data()
            
            # Format the data
            formatted = self._format_data(data)
            
            # Apply theme styling
            styled = self._apply_styling(formatted, data.status)
            
            # Apply width constraints
            final_output = self._apply_width_constraints(styled)
            
            # Update cache
            self._cache.update({
                'data': data,
                'rendered': final_output,
                'timestamp': current_time,
                'status': data.status
            })
            self._last_update = current_time
            
            # Update performance metrics
            render_time = time.time() - start_time
            self._render_count += 1
            self._total_render_time += render_time
            
            return final_output
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            return self._get_error_output(str(e))
    
    def _should_use_cache(self, current_time: float) -> bool:
        """Check if cached data should be used"""
        if 'timestamp' not in self._cache:
            return False
        
        cache_age = current_time - self._cache['timestamp']
        return cache_age < self.cache_timeout
    
    def _apply_styling(self, content: str, status: str) -> str:
        """Apply theme styling to content"""
        segment_type = self.__class__.__name__.lower().replace('segment', '')
        style = self.theme.get_segment_style(segment_type, status)
        
        return self.color_utils.colorize(
            content,
            style.get('fg', 'white'),
            style.get('bg'),
            bold=style.get('bold', False),
            italic=style.get('italic', False),
            underline=style.get('underline', False)
        )
    
    def _apply_width_constraints(self, content: str) -> str:
        """Apply maximum width constraints"""
        if not self.max_width:
            return content
        
        display_length = self.color_utils.get_display_length(content)
        if display_length <= self.max_width:
            return content
        
        # Truncate using configured mode
        truncate_mode = self.config.get('truncate_mode', 'ellipsis')
        return self.color_utils.truncate(content, self.max_width, truncate_mode)
    
    def _get_error_output(self, error_msg: str) -> str:
        """Generate error output when segment fails"""
        error_icon = self.theme.unicode_symbols.get('cross', '✗')
        error_color = 'red'
        
        if self.config.get('show_errors', True):
            content = f"{error_icon} Error"
            return self.color_utils.colorize(content, error_color)
        else:
            return ""  # Hide errors if configured to do so
    
    def get_data(self) -> Optional[SegmentData]:
        """Get the last collected data"""
        return self._cache.get('data')
    
    def get_status(self) -> str:
        """Get current segment status"""
        return self._cache.get('status', 'unknown')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this segment"""
        avg_render_time = (
            self._total_render_time / self._render_count 
            if self._render_count > 0 else 0.0
        )
        
        return {
            'id': self.id,
            'enabled': self.enabled,
            'render_count': self._render_count,
            'error_count': self._error_count,
            'last_error': self._last_error,
            'average_render_time': avg_render_time,
            'cache_age': time.time() - self._last_update if self._last_update > 0 else 0,
            'last_status': self.get_status()
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self._render_count = 0
        self._total_render_time = 0.0
        self._error_count = 0
        self._last_error = None
    
    def clear_cache(self):
        """Clear segment cache"""
        self._cache.clear()
        self._last_update = 0.0
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update segment configuration"""
        self.config.update(new_config)
        
        # Update configurable properties
        self.enabled = self.config.get('enabled', self.enabled)
        self.priority = self.config.get('priority', self.priority)
        self.cache_timeout = self.config.get('cache_timeout', self.cache_timeout)
        self.max_width = self.config.get('max_width', self.max_width)
        
        # Clear cache to force refresh with new config
        self.clear_cache()
    
    def is_healthy(self) -> bool:
        """Check if segment is operating normally"""
        # Consider unhealthy if error rate is high
        if self._render_count > 10:
            error_rate = self._error_count / self._render_count
            return error_rate < 0.5
        
        return True
    
    def get_tooltip(self) -> Optional[str]:
        """Get tooltip text for this segment"""
        data = self.get_data()
        if data and data.tooltip:
            return data.tooltip
        
        # Default tooltip with basic info
        stats = self.get_stats()
        return f"{self.__class__.__name__}: {stats['last_status']} (errors: {stats['error_count']})"
    
    def __str__(self) -> str:
        """String representation of segment"""
        return f"{self.__class__.__name__}(id={self.id}, enabled={self.enabled})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"{self.__class__.__name__}(id={self.id}, enabled={self.enabled}, "
                f"priority={self.priority}, cache_timeout={self.cache_timeout})")


class CachedSegment(BaseSegment):
    """
    Enhanced base segment with advanced caching capabilities
    
    Provides additional caching features like:
    - Multiple cache levels
    - Cache warming
    - Smart invalidation
    """
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Multi-level cache
        self._memory_cache: Dict[str, Any] = {}
        self._persistent_cache: Dict[str, Any] = {}
        
        # Cache warming
        self._warm_cache = config.get('warm_cache', False)
        self._background_refresh = config.get('background_refresh', False)
    
    def warm_cache(self):
        """Pre-populate cache with initial data"""
        if self._warm_cache:
            try:
                self._collect_data()
            except:
                pass  # Ignore errors during cache warming
    
    def get_cached_data(self, key: str, max_age: Optional[float] = None) -> Optional[Any]:
        """Get data from cache with optional age check"""
        max_age = max_age or self.cache_timeout
        
        if key in self._memory_cache:
            cache_entry = self._memory_cache[key]
            if (time.time() - cache_entry['timestamp']) < max_age:
                return cache_entry['data']
        
        return None
    
    def set_cached_data(self, key: str, data: Any):
        """Store data in cache"""
        self._memory_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def invalidate_cache(self, key: Optional[str] = None):
        """Invalidate cache entries"""
        if key:
            self._memory_cache.pop(key, None)
        else:
            self._memory_cache.clear()
            self.clear_cache()


class AsyncSegment(BaseSegment):
    """
    Base segment with async data collection support
    
    Allows segments to collect data asynchronously without blocking
    the main render loop.
    """
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        self._async_data: Optional[SegmentData] = None
        self._async_pending = False
        self._async_enabled = config.get('async_enabled', False)
    
    def start_async_collection(self):
        """Start asynchronous data collection"""
        if self._async_enabled and not self._async_pending:
            self._async_pending = True
            # Implementation would use threading or asyncio
            # This is a placeholder for the interface
    
    def get_async_data(self) -> Optional[SegmentData]:
        """Get asynchronously collected data"""
        if self._async_data:
            data = self._async_data
            self._async_data = None
            self._async_pending = False
            return data
        return None