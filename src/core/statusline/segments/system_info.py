"""
System Info Segment

Displays system performance information including CPU usage, memory usage,
load average, and other system metrics.
"""

import os
import time
from typing import Dict, Any, Optional, Tuple

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils, SystemUtils, format_bytes
from ..themes import Theme


class SystemInfoSegment(BaseSegment):
    """Segment that displays system performance information"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.show_cpu = config.get('show_cpu', True)
        self.show_memory = config.get('show_memory', True)
        self.show_load = config.get('show_load', False)
        self.show_disk = config.get('show_disk', False)
        self.show_uptime = config.get('show_uptime', False)
        self.compact_display = config.get('compact_display', True)
        self.show_icons = config.get('show_icons', True)
        
        # Thresholds for status determination
        self.cpu_warning_threshold = config.get('cpu_warning_threshold', 70.0)
        self.cpu_critical_threshold = config.get('cpu_critical_threshold', 90.0)
        self.memory_warning_threshold = config.get('memory_warning_threshold', 80.0)
        self.memory_critical_threshold = config.get('memory_critical_threshold', 95.0)
        self.load_warning_threshold = config.get('load_warning_threshold', 2.0)
        self.load_critical_threshold = config.get('load_critical_threshold', 4.0)
        
        # Update intervals (different for different metrics)
        self.cpu_update_interval = config.get('cpu_update_interval', 2.0)
        self.memory_update_interval = config.get('memory_update_interval', 5.0)
        self.disk_update_interval = config.get('disk_update_interval', 30.0)
        
        # System utilities
        self.system_utils = SystemUtils()
        
        # Cache for different metrics with different timeouts
        self._metric_cache = {}
        self._metric_timestamps = {}
    
    def _collect_data(self) -> SegmentData:
        """Collect system performance information"""
        content_parts = []
        overall_status = 'normal'
        
        # CPU usage
        if self.show_cpu:
            cpu_info = self._get_cpu_info()
            if cpu_info:
                content_parts.append(cpu_info['display'])
                if cpu_info['status'] != 'normal':
                    overall_status = cpu_info['status']
        
        # Memory usage
        if self.show_memory:
            memory_info = self._get_memory_info()
            if memory_info:
                content_parts.append(memory_info['display'])
                if memory_info['status'] != 'normal' and overall_status == 'normal':
                    overall_status = memory_info['status']
        
        # Load average (Unix only)
        if self.show_load:
            load_info = self._get_load_info()
            if load_info:
                content_parts.append(load_info['display'])
                if load_info['status'] != 'normal' and overall_status == 'normal':
                    overall_status = load_info['status']
        
        # Disk usage
        if self.show_disk:
            disk_info = self._get_disk_info()
            if disk_info:
                content_parts.append(disk_info['display'])
                if disk_info['status'] != 'normal' and overall_status == 'normal':
                    overall_status = disk_info['status']
        
        # Uptime
        if self.show_uptime:
            uptime_info = self._get_uptime_info()
            if uptime_info:
                content_parts.append(uptime_info['display'])
        
        content = ' '.join(content_parts) if content_parts else ""
        
        # Generate tooltip
        tooltip = self._generate_tooltip()
        
        return SegmentData(
            content=content,
            status=overall_status,
            icon=self._get_system_icon(),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format system info data for display"""
        return data.content
    
    def _get_cpu_info(self) -> Optional[Dict[str, Any]]:
        """Get CPU usage information"""
        try:
            # Check cache
            if self._should_use_metric_cache('cpu', self.cpu_update_interval):
                return self._metric_cache.get('cpu')
            
            cpu_percent = self.system_utils.get_cpu_usage()
            
            # Determine status
            if cpu_percent >= self.cpu_critical_threshold:
                status = 'critical'
            elif cpu_percent >= self.cpu_warning_threshold:
                status = 'warning'
            else:
                status = 'normal'
            
            # Format display
            if self.compact_display:
                display = f"{cpu_percent:.0f}%"
            else:
                cpu_icon = self._get_cpu_icon()
                display = f"{cpu_icon}{cpu_percent:.1f}%" if cpu_icon else f"CPU {cpu_percent:.1f}%"
            
            result = {
                'value': cpu_percent,
                'status': status,
                'display': display
            }
            
            # Cache the result
            self._metric_cache['cpu'] = result
            self._metric_timestamps['cpu'] = time.time()
            
            return result
            
        except Exception:
            return None
    
    def _get_memory_info(self) -> Optional[Dict[str, Any]]:
        """Get memory usage information"""
        try:
            # Check cache
            if self._should_use_metric_cache('memory', self.memory_update_interval):
                return self._metric_cache.get('memory')
            
            memory_percent, memory_used_gb = self.system_utils.get_memory_usage()
            
            # Determine status
            if memory_percent >= self.memory_critical_threshold:
                status = 'critical'
            elif memory_percent >= self.memory_warning_threshold:
                status = 'warning'
            else:
                status = 'normal'
            
            # Format display
            if self.compact_display:
                display = f"{memory_percent:.0f}%"
            else:
                memory_icon = self._get_memory_icon()
                if memory_icon:
                    display = f"{memory_icon}{memory_percent:.1f}%"
                else:
                    display = f"MEM {memory_percent:.1f}%"
            
            result = {
                'percent': memory_percent,
                'used_gb': memory_used_gb,
                'status': status,
                'display': display
            }
            
            # Cache the result
            self._metric_cache['memory'] = result
            self._metric_timestamps['memory'] = time.time()
            
            return result
            
        except Exception:
            return None
    
    def _get_load_info(self) -> Optional[Dict[str, Any]]:
        """Get system load average information"""
        try:
            load_avg = self.system_utils.get_load_average()
            if not load_avg:
                return None
            
            # Use 1-minute load average
            load_1min = load_avg[0]
            
            # Determine status
            if load_1min >= self.load_critical_threshold:
                status = 'critical'
            elif load_1min >= self.load_warning_threshold:
                status = 'warning'
            else:
                status = 'normal'
            
            # Format display
            if self.compact_display:
                display = f"{load_1min:.1f}"
            else:
                display = f"LOAD {load_1min:.2f}"
            
            return {
                'load_1min': load_1min,
                'load_5min': load_avg[1],
                'load_15min': load_avg[2],
                'status': status,
                'display': display
            }
            
        except Exception:
            return None
    
    def _get_disk_info(self) -> Optional[Dict[str, Any]]:
        """Get disk usage information"""
        try:
            # Check cache
            if self._should_use_metric_cache('disk', self.disk_update_interval):
                return self._metric_cache.get('disk')
            
            disk_percent, disk_free_gb = self.system_utils.get_disk_usage()
            
            # Determine status
            if disk_percent >= 95.0:
                status = 'critical'
            elif disk_percent >= 85.0:
                status = 'warning'
            else:
                status = 'normal'
            
            # Format display
            if self.compact_display:
                display = f"{disk_percent:.0f}%"
            else:
                display = f"DISK {disk_percent:.1f}%"
            
            result = {
                'percent': disk_percent,
                'free_gb': disk_free_gb,
                'status': status,
                'display': display
            }
            
            # Cache the result
            self._metric_cache['disk'] = result
            self._metric_timestamps['disk'] = time.time()
            
            return result
            
        except Exception:
            return None
    
    def _get_uptime_info(self) -> Optional[Dict[str, Any]]:
        """Get system uptime information"""
        try:
            # Different methods for different platforms
            uptime_seconds = None
            
            if hasattr(os, 'getloadavg'):  # Unix-like systems
                try:
                    with open('/proc/uptime', 'r') as f:
                        uptime_seconds = float(f.readline().split()[0])
                except:
                    pass
            
            if uptime_seconds is None:
                # Fallback: use time since process start (not accurate but something)
                import psutil
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
            
            if uptime_seconds is None:
                return None
            
            # Format uptime
            if uptime_seconds < 3600:  # Less than 1 hour
                display = f"{int(uptime_seconds // 60)}m"
            elif uptime_seconds < 86400:  # Less than 1 day
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                display = f"{hours}h{minutes}m"
            else:  # More than 1 day
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                display = f"{days}d{hours}h"
            
            return {
                'uptime_seconds': uptime_seconds,
                'display': display
            }
            
        except Exception:
            return None
    
    def _should_use_metric_cache(self, metric: str, update_interval: float) -> bool:
        """Check if cached metric should be used"""
        if metric not in self._metric_cache or metric not in self._metric_timestamps:
            return False
        
        age = time.time() - self._metric_timestamps[metric]
        return age < update_interval
    
    def _get_system_icon(self) -> Optional[str]:
        """Get system monitoring icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('cpu', '⚙')
        
        return '⚙'
    
    def _get_cpu_icon(self) -> Optional[str]:
        """Get CPU icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('cpu', '⚙')
        
        return '⚙'
    
    def _get_memory_icon(self) -> Optional[str]:
        """Get memory icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('memory', '🧠')
        
        return '🧠'
    
    def _generate_tooltip(self) -> str:
        """Generate detailed tooltip for system info"""
        lines = []
        
        # CPU information
        cpu_info = self._get_cpu_info()
        if cpu_info:
            lines.append(f"CPU Usage: {cpu_info['value']:.1f}%")
        
        # Memory information
        memory_info = self._get_memory_info()
        if memory_info:
            lines.append(f"Memory Usage: {memory_info['percent']:.1f}% ({memory_info['used_gb']:.1f} GB)")
        
        # Load average
        load_info = self._get_load_info()
        if load_info:
            lines.append(f"Load Average: {load_info['load_1min']:.2f}, {load_info['load_5min']:.2f}, {load_info['load_15min']:.2f}")
        
        # Disk usage
        disk_info = self._get_disk_info()
        if disk_info:
            lines.append(f"Disk Usage: {disk_info['percent']:.1f}% ({disk_info['free_gb']:.1f} GB free)")
        
        # Uptime
        uptime_info = self._get_uptime_info()
        if uptime_info:
            lines.append(f"Uptime: {uptime_info['display']}")
        
        # System info
        try:
            import platform
            lines.append(f"System: {platform.system()} {platform.release()}")
        except:
            pass
        
        return '\n'.join(lines)
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed system statistics"""
        stats = {}
        
        # Refresh all metrics
        self._metric_cache.clear()
        self._metric_timestamps.clear()
        
        # Collect all available metrics
        cpu_info = self._get_cpu_info()
        if cpu_info:
            stats['cpu'] = cpu_info
        
        memory_info = self._get_memory_info()
        if memory_info:
            stats['memory'] = memory_info
        
        load_info = self._get_load_info()
        if load_info:
            stats['load'] = load_info
        
        disk_info = self._get_disk_info()
        if disk_info:
            stats['disk'] = disk_info
        
        uptime_info = self._get_uptime_info()
        if uptime_info:
            stats['uptime'] = uptime_info
        
        # Add system information
        try:
            import platform
            stats['platform'] = {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
        except:
            pass
        
        return stats
    
    def is_system_healthy(self) -> bool:
        """Check if system is operating within normal parameters"""
        try:
            # Check CPU
            cpu_info = self._get_cpu_info()
            if cpu_info and cpu_info['status'] in ['critical', 'warning']:
                return False
            
            # Check memory
            memory_info = self._get_memory_info()
            if memory_info and memory_info['status'] in ['critical', 'warning']:
                return False
            
            # Check load (if available)
            load_info = self._get_load_info()
            if load_info and load_info['status'] in ['critical', 'warning']:
                return False
            
            # Check disk
            disk_info = self._get_disk_info()
            if disk_info and disk_info['status'] == 'critical':
                return False
            
            return True
            
        except Exception:
            return False  # Assume unhealthy if we can't check
    
    def get_alerts(self) -> list:
        """Get list of system alerts"""
        alerts = []
        
        # Check each metric for alerts
        cpu_info = self._get_cpu_info()
        if cpu_info and cpu_info['status'] != 'normal':
            alerts.append({
                'metric': 'cpu',
                'level': cpu_info['status'],
                'message': f"CPU usage high: {cpu_info['value']:.1f}%",
                'value': cpu_info['value']
            })
        
        memory_info = self._get_memory_info()
        if memory_info and memory_info['status'] != 'normal':
            alerts.append({
                'metric': 'memory',
                'level': memory_info['status'],
                'message': f"Memory usage high: {memory_info['percent']:.1f}%",
                'value': memory_info['percent']
            })
        
        load_info = self._get_load_info()
        if load_info and load_info['status'] != 'normal':
            alerts.append({
                'metric': 'load',
                'level': load_info['status'],
                'message': f"System load high: {load_info['load_1min']:.2f}",
                'value': load_info['load_1min']
            })
        
        disk_info = self._get_disk_info()
        if disk_info and disk_info['status'] != 'normal':
            alerts.append({
                'metric': 'disk',
                'level': disk_info['status'],
                'message': f"Disk usage high: {disk_info['percent']:.1f}%",
                'value': disk_info['percent']
            })
        
        return alerts
    
    def clear_metric_cache(self):
        """Clear all metric caches"""
        self._metric_cache.clear()
        self._metric_timestamps.clear()