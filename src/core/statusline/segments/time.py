"""
Time Segment

Displays current time, date, and optionally timezone information
with customizable formatting.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils
from ..themes import Theme


class TimeSegment(BaseSegment):
    """Segment that displays current time and date"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.time_format = config.get('format', '%H:%M:%S')
        self.show_date = config.get('show_date', False)
        self.date_format = config.get('date_format', '%Y-%m-%d')
        self.show_timezone = config.get('show_timezone', False)
        self.timezone_format = config.get('timezone_format', '%Z')
        self.show_seconds = config.get('show_seconds', True)
        self.compact_display = config.get('compact_display', True)
        self.show_icons = config.get('show_icons', True)
        self.use_24_hour = config.get('use_24_hour', True)
        self.show_day_of_week = config.get('show_day_of_week', False)
        
        # Special time formats
        self.relative_time = config.get('relative_time', False)
        self.show_uptime = config.get('show_uptime', False)
        self.uptime_reference = config.get('uptime_reference', time.time())
        
        # Update frequency for seconds display
        if self.show_seconds:
            self.cache_timeout = 1.0  # Update every second
        else:
            self.cache_timeout = 60.0  # Update every minute
    
    def _collect_data(self) -> SegmentData:
        """Collect current time information"""
        now = datetime.now()
        
        content_parts = []
        
        # Day of week
        if self.show_day_of_week:
            if self.compact_display:
                day_name = now.strftime('%a')  # Short day name (Mon, Tue, etc.)
            else:
                day_name = now.strftime('%A')  # Full day name (Monday, Tuesday, etc.)
            content_parts.append(day_name)
        
        # Date
        if self.show_date:
            date_str = now.strftime(self.date_format)
            content_parts.append(date_str)
        
        # Time
        if self.relative_time:
            time_str = self._get_relative_time(now)
        else:
            # Adjust time format based on configuration
            time_format = self.time_format
            if not self.use_24_hour and '%H' in time_format:
                time_format = time_format.replace('%H', '%I')
                if '%p' not in time_format:
                    time_format += ' %p'
            
            if not self.show_seconds:
                time_format = time_format.replace(':%S', '')
            
            time_str = now.strftime(time_format)
        
        content_parts.append(time_str)
        
        # Timezone
        if self.show_timezone:
            tz_str = now.strftime(self.timezone_format)
            if tz_str:
                content_parts.append(f"({tz_str})")
        
        # Uptime
        if self.show_uptime:
            uptime_str = self._get_uptime()
            if uptime_str:
                content_parts.append(f"up {uptime_str}")
        
        # Combine content
        if self.compact_display:
            content = ' '.join(content_parts)
        else:
            content = ' '.join(content_parts)
        
        # Add icon if enabled
        if self.show_icons:
            time_icon = self._get_time_icon(now)
            if time_icon:
                content = f"{time_icon} {content}"
        
        # Determine status based on time of day
        status = self._determine_time_status(now)
        
        # Generate tooltip
        tooltip = self._generate_tooltip(now)
        
        return SegmentData(
            content=content,
            status=status,
            icon=self._get_time_icon(now),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format time data for display"""
        return data.content
    
    def _get_relative_time(self, now: datetime) -> str:
        """Get relative time description"""
        hour = now.hour
        
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"
    
    def _get_uptime(self) -> Optional[str]:
        """Get system or session uptime"""
        try:
            current_time = time.time()
            uptime_seconds = current_time - self.uptime_reference
            
            if uptime_seconds < 60:
                return f"{int(uptime_seconds)}s"
            elif uptime_seconds < 3600:
                minutes = int(uptime_seconds // 60)
                seconds = int(uptime_seconds % 60)
                return f"{minutes}m{seconds}s"
            elif uptime_seconds < 86400:
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h{minutes}m"
            else:
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                return f"{days}d{hours}h"
                
        except Exception:
            return None
    
    def _determine_time_status(self, now: datetime) -> str:
        """Determine status based on time of day"""
        hour = now.hour
        
        if 6 <= hour < 9:
            return 'morning'
        elif 9 <= hour < 12:
            return 'late_morning'
        elif 12 <= hour < 14:
            return 'lunch'
        elif 14 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 20:
            return 'evening'
        elif 20 <= hour < 23:
            return 'night'
        else:
            return 'late_night'
    
    def _get_time_icon(self, now: datetime) -> Optional[str]:
        """Get appropriate time icon based on current time"""
        if not self.show_icons:
            return None
        
        # For compatibility, use simple ASCII representation
        # Future enhancement: check terminal Unicode support
        return '@'
    
    def _generate_tooltip(self, now: datetime) -> str:
        """Generate detailed tooltip for time segment"""
        lines = []
        
        # Full date and time
        full_datetime = now.strftime('%A, %B %d, %Y at %H:%M:%S')
        lines.append(f"Current time: {full_datetime}")
        
        # Timezone information
        try:
            tz_name = now.astimezone().tzname()
            tz_offset = now.astimezone().strftime('%z')
            if tz_name and tz_offset:
                lines.append(f"Timezone: {tz_name} (UTC{tz_offset[:3]}:{tz_offset[3:]})")
        except Exception:
            pass
        
        # UTC time
        utc_time = datetime.now(timezone.utc).strftime('%H:%M:%S UTC')
        lines.append(f"UTC time: {utc_time}")
        
        # Unix timestamp
        timestamp = int(now.timestamp())
        lines.append(f"Unix timestamp: {timestamp}")
        
        # Day information
        day_of_year = now.timetuple().tm_yday
        week_number = now.isocalendar()[1]
        lines.append(f"Day {day_of_year} of year, week {week_number}")
        
        # Uptime if enabled
        if self.show_uptime:
            uptime_str = self._get_uptime()
            if uptime_str:
                lines.append(f"Session uptime: {uptime_str}")
        
        # Time-based greeting
        hour = now.hour
        if 5 <= hour < 12:
            greeting = "Good morning!"
        elif 12 <= hour < 17:
            greeting = "Good afternoon!"
        elif 17 <= hour < 21:
            greeting = "Good evening!"
        else:
            greeting = "Good night!"
        
        lines.append(greeting)
        
        return '\n'.join(lines)
    
    def get_current_time(self) -> datetime:
        """Get current datetime object"""
        return datetime.now()
    
    def get_formatted_time(self, format_string: str = None) -> str:
        """Get current time with custom format"""
        now = self.get_current_time()
        format_str = format_string or self.time_format
        return now.strftime(format_str)
    
    def get_timezone_info(self) -> Dict[str, Any]:
        """Get detailed timezone information"""
        now = datetime.now()
        
        try:
            local_tz = now.astimezone()
            utc_offset = local_tz.utcoffset().total_seconds()
            
            return {
                'timezone_name': local_tz.tzname(),
                'timezone_abbreviation': now.strftime('%Z'),
                'utc_offset_seconds': utc_offset,
                'utc_offset_hours': utc_offset / 3600,
                'utc_offset_string': local_tz.strftime('%z'),
                'is_dst': time.daylight and time.localtime().tm_isdst,
                'local_time': now.isoformat(),
                'utc_time': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_time_until(self, target_time: str) -> Optional[str]:
        """Get time remaining until target time (HH:MM format)"""
        try:
            now = datetime.now()
            target_hour, target_minute = map(int, target_time.split(':'))
            
            # Create target datetime for today
            target_dt = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            
            # If target time has passed today, set it for tomorrow
            if target_dt <= now:
                target_dt = target_dt.replace(day=target_dt.day + 1)
            
            time_diff = target_dt - now
            total_seconds = int(time_diff.total_seconds())
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
                
        except Exception:
            return None
    
    def get_time_since(self, reference_time: float) -> str:
        """Get time elapsed since reference timestamp"""
        try:
            current_time = time.time()
            elapsed_seconds = current_time - reference_time
            
            if elapsed_seconds < 60:
                return f"{int(elapsed_seconds)} seconds ago"
            elif elapsed_seconds < 3600:
                minutes = int(elapsed_seconds // 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif elapsed_seconds < 86400:
                hours = int(elapsed_seconds // 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(elapsed_seconds // 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
                
        except Exception:
            return "Unknown"
    
    def set_custom_format(self, time_format: str = None, date_format: str = None):
        """Set custom time and date formats"""
        if time_format:
            self.time_format = time_format
        if date_format:
            self.date_format = date_format
        
        # Clear cache to apply new format
        self.clear_cache()
    
    def toggle_24_hour_format(self):
        """Toggle between 12-hour and 24-hour time format"""
        self.use_24_hour = not self.use_24_hour
        
        if self.use_24_hour:
            self.time_format = '%H:%M:%S'
        else:
            self.time_format = '%I:%M:%S %p'
        
        self.clear_cache()
    
    def reset_uptime_reference(self):
        """Reset uptime reference to current time"""
        self.uptime_reference = time.time()
        self.clear_cache()
    
    def get_world_times(self, timezones: List[str] = None) -> Dict[str, str]:
        """Get current time in different timezones"""
        import zoneinfo
        
        default_zones = [
            'UTC',
            'US/Eastern',
            'US/Pacific', 
            'Europe/London',
            'Europe/Paris',
            'Asia/Tokyo',
            'Australia/Sydney'
        ]
        
        zones = timezones or default_zones
        world_times = {}
        
        for zone_name in zones:
            try:
                tz = zoneinfo.ZoneInfo(zone_name)
                zone_time = datetime.now(tz)
                world_times[zone_name] = zone_time.strftime('%H:%M %Z')
            except Exception:
                # Fallback for systems without zoneinfo
                try:
                    import pytz
                    tz = pytz.timezone(zone_name)
                    zone_time = datetime.now(tz)
                    world_times[zone_name] = zone_time.strftime('%H:%M %Z')
                except Exception:
                    world_times[zone_name] = 'Unknown'
        
        return world_times
    
    def is_business_hours(self, start_hour: int = 9, end_hour: int = 17) -> bool:
        """Check if current time is within business hours"""
        current_hour = datetime.now().hour
        return start_hour <= current_hour < end_hour
    
    def get_time_period(self) -> str:
        """Get current time period description"""
        hour = datetime.now().hour
        
        periods = {
            (0, 6): 'Late Night',
            (6, 9): 'Early Morning',
            (9, 12): 'Morning',
            (12, 14): 'Lunch Time',
            (14, 17): 'Afternoon',
            (17, 20): 'Evening',
            (20, 24): 'Night'
        }
        
        for (start, end), period in periods.items():
            if start <= hour < end:
                return period
        
        return 'Unknown'