"""
Claude Session Segment

Displays Claude Code session information including token usage,
session duration, and active conversation status.
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils, format_duration
from ..themes import Theme


class ClaudeSessionSegment(BaseSegment):
    """Segment that displays Claude session information"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.show_token_usage = config.get('show_token_usage', True)
        self.show_session_time = config.get('show_session_time', True)
        self.show_conversation_count = config.get('show_conversation_count', False)
        self.show_model_info = config.get('show_model_info', False)
        self.compact_display = config.get('compact_display', True)
        self.token_warning_threshold = config.get('token_warning_threshold', 80)  # Percentage
        self.token_critical_threshold = config.get('token_critical_threshold', 95)  # Percentage
        
        # Session tracking
        self.session_start_time = time.time()
        self._last_token_check = 0
        self._token_cache = {}
        
        # Claude session paths
        self.claude_config_path = self._find_claude_config()
    
    def _find_claude_config(self) -> Optional[str]:
        """Find Claude configuration directory"""
        possible_paths = [
            os.path.expanduser("~/.config/claude-code"),
            os.path.expanduser("~/.claude"),
            os.path.join(os.getcwd(), ".claude"),
            os.path.join(os.getcwd(), "config"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _collect_data(self) -> SegmentData:
        """Collect Claude session information"""
        content_parts = []
        
        # Session status indicator
        session_icon = self._get_session_icon()
        if session_icon:
            content_parts.append(session_icon)
        
        # Token usage
        if self.show_token_usage:
            token_info = self._get_token_usage()
            if token_info:
                content_parts.append(token_info)
        
        # Session duration
        if self.show_session_time:
            duration = self._get_session_duration()
            if duration:
                content_parts.append(duration)
        
        # Conversation count
        if self.show_conversation_count:
            conv_count = self._get_conversation_count()
            if conv_count:
                content_parts.append(conv_count)
        
        # Model information
        if self.show_model_info:
            model_info = self._get_model_info()
            if model_info:
                content_parts.append(model_info)
        
        content = ' '.join(content_parts) if content_parts else "Claude"
        
        # Determine status based on token usage and session health
        status = self._determine_status()
        
        # Generate tooltip
        tooltip = self._generate_tooltip()
        
        return SegmentData(
            content=content,
            status=status,
            icon=session_icon,
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format Claude session data for display"""
        return data.content
    
    def _get_session_icon(self) -> str:
        """Get session status icon"""
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('agent', '🤖')
        return '🤖'
    
    def _get_token_usage(self) -> Optional[str]:
        """Get token usage information"""
        try:
            token_data = self._fetch_token_data()
            if not token_data:
                return None
            
            used_tokens = token_data.get('used_tokens', 0)
            total_tokens = token_data.get('total_tokens', 0)
            
            if total_tokens == 0:
                return None
            
            percentage = (used_tokens / total_tokens) * 100
            
            if self.compact_display:
                return f"{percentage:.0f}%"
            else:
                return f"{used_tokens:,}/{total_tokens:,}"
                
        except Exception:
            return None
    
    def _get_session_duration(self) -> Optional[str]:
        """Get session duration"""
        duration = time.time() - self.session_start_time
        
        if self.compact_display:
            if duration < 3600:  # Less than 1 hour
                return f"{int(duration // 60)}m"
            else:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                return f"{hours}h{minutes}m"
        else:
            return format_duration(duration)
    
    def _get_conversation_count(self) -> Optional[str]:
        """Get number of active conversations"""
        try:
            # Look for conversation files or session data
            conv_count = self._count_conversations()
            if conv_count > 0:
                return f"{conv_count} conv"
        except Exception:
            pass
        
        return None
    
    def _get_model_info(self) -> Optional[str]:
        """Get current model information"""
        try:
            model_data = self._fetch_model_data()
            if model_data:
                model_name = model_data.get('model', '')
                if model_name:
                    # Abbreviate common model names
                    if 'claude-3' in model_name.lower():
                        if 'sonnet' in model_name.lower():
                            return 'Sonnet'
                        elif 'opus' in model_name.lower():
                            return 'Opus'
                        elif 'haiku' in model_name.lower():
                            return 'Haiku'
                    return model_name.split('-')[-1]  # Return last part
        except Exception:
            pass
        
        return None
    
    def _fetch_token_data(self) -> Dict[str, Any]:
        """Fetch token usage data from Claude session"""
        current_time = time.time()
        
        # Use cache if recent
        if (current_time - self._last_token_check) < 5.0 and self._token_cache:
            return self._token_cache
        
        token_data = {}
        
        try:
            # Try to read from Claude config
            if self.claude_config_path:
                session_file = os.path.join(self.claude_config_path, "session.json")
                if os.path.exists(session_file):
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        token_data = session_data.get('tokens', {})
            
            # Try environment variables
            if not token_data:
                used = os.getenv('CLAUDE_TOKENS_USED')
                total = os.getenv('CLAUDE_TOKENS_TOTAL')
                if used and total:
                    token_data = {
                        'used_tokens': int(used),
                        'total_tokens': int(total)
                    }
            
            # Try to parse from recent logs
            if not token_data:
                token_data = self._parse_token_from_logs()
            
        except Exception:
            pass
        
        self._token_cache = token_data
        self._last_token_check = current_time
        
        return token_data
    
    def _fetch_model_data(self) -> Dict[str, Any]:
        """Fetch current model information"""
        try:
            if self.claude_config_path:
                config_file = os.path.join(self.claude_config_path, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        return config_data
            
            # Try environment variables
            model = os.getenv('CLAUDE_MODEL')
            if model:
                return {'model': model}
                
        except Exception:
            pass
        
        return {}
    
    def _count_conversations(self) -> int:
        """Count active conversations"""
        try:
            if self.claude_config_path:
                conversations_dir = os.path.join(self.claude_config_path, "conversations")
                if os.path.exists(conversations_dir):
                    # Count conversation files
                    conv_files = [f for f in os.listdir(conversations_dir) 
                                 if f.endswith('.json')]
                    return len(conv_files)
        except Exception:
            pass
        
        return 0
    
    def _parse_token_from_logs(self) -> Dict[str, Any]:
        """Parse token usage from log files"""
        try:
            log_paths = [
                os.path.join(os.getcwd(), "logs", "claude.log"),
                os.path.expanduser("~/.claude/logs/session.log"),
                "/tmp/claude-session.log"
            ]
            
            for log_path in log_paths:
                if os.path.exists(log_path):
                    # Read last few lines of log file
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        
                    # Look for token usage patterns in recent lines
                    for line in reversed(lines[-50:]):  # Check last 50 lines
                        if 'tokens' in line.lower():
                            # Try to extract token information
                            # This is a simplified parser - could be enhanced
                            import re
                            
                            # Pattern: "tokens: 1234/5000"
                            pattern = r'tokens?[:\s]+(\d+)[/,\s]+(\d+)'
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                return {
                                    'used_tokens': int(match.group(1)),
                                    'total_tokens': int(match.group(2))
                                }
        except Exception:
            pass
        
        return {}
    
    def _determine_status(self) -> str:
        """Determine session status"""
        try:
            token_data = self._fetch_token_data()
            if token_data and token_data.get('total_tokens', 0) > 0:
                used = token_data.get('used_tokens', 0)
                total = token_data.get('total_tokens', 0)
                percentage = (used / total) * 100
                
                if percentage >= self.token_critical_threshold:
                    return 'critical'
                elif percentage >= self.token_warning_threshold:
                    return 'warning'
                else:
                    return 'active'
            
            # Check session duration
            duration = time.time() - self.session_start_time
            if duration > 3600:  # More than 1 hour
                return 'long_session'
            
            return 'active'
            
        except Exception:
            return 'unknown'
    
    def _generate_tooltip(self) -> str:
        """Generate detailed tooltip for Claude session"""
        lines = []
        
        # Session duration
        duration = time.time() - self.session_start_time
        lines.append(f"Session duration: {format_duration(duration)}")
        
        # Token usage
        try:
            token_data = self._fetch_token_data()
            if token_data and token_data.get('total_tokens', 0) > 0:
                used = token_data.get('used_tokens', 0)
                total = token_data.get('total_tokens', 0)
                percentage = (used / total) * 100
                
                lines.append(f"Token usage: {used:,}/{total:,} ({percentage:.1f}%)")
                
                remaining = total - used
                lines.append(f"Tokens remaining: {remaining:,}")
        except Exception:
            lines.append("Token usage: Unknown")
        
        # Model info
        try:
            model_data = self._fetch_model_data()
            model = model_data.get('model', 'Unknown')
            lines.append(f"Model: {model}")
        except Exception:
            pass
        
        # Conversation count
        try:
            conv_count = self._count_conversations()
            if conv_count > 0:
                lines.append(f"Active conversations: {conv_count}")
        except Exception:
            pass
        
        # Session start time
        start_time = datetime.fromtimestamp(self.session_start_time)
        lines.append(f"Started: {start_time.strftime('%H:%M:%S')}")
        
        return '\n'.join(lines)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get detailed session statistics"""
        stats = {
            'session_duration': time.time() - self.session_start_time,
            'session_start_time': self.session_start_time,
            'status': self._determine_status()
        }
        
        # Add token information
        try:
            token_data = self._fetch_token_data()
            stats.update(token_data)
        except Exception:
            pass
        
        # Add model information
        try:
            model_data = self._fetch_model_data()
            stats.update(model_data)
        except Exception:
            pass
        
        # Add conversation count
        try:
            stats['conversation_count'] = self._count_conversations()
        except Exception:
            stats['conversation_count'] = 0
        
        return stats
    
    def reset_session_timer(self):
        """Reset the session start time"""
        self.session_start_time = time.time()
        self.clear_cache()
    
    def update_token_usage(self, used_tokens: int, total_tokens: int):
        """Manually update token usage information"""
        self._token_cache = {
            'used_tokens': used_tokens,
            'total_tokens': total_tokens
        }
        self._last_token_check = time.time()
        self.clear_cache()
    
    def get_token_usage_percentage(self) -> float:
        """Get current token usage as percentage"""
        try:
            token_data = self._fetch_token_data()
            if token_data and token_data.get('total_tokens', 0) > 0:
                used = token_data.get('used_tokens', 0)
                total = token_data.get('total_tokens', 0)
                return (used / total) * 100
        except Exception:
            pass
        
        return 0.0
    
    def is_token_usage_critical(self) -> bool:
        """Check if token usage is at critical level"""
        percentage = self.get_token_usage_percentage()
        return percentage >= self.token_critical_threshold
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export session data for external use"""
        return {
            'timestamp': time.time(),
            'session_stats': self.get_session_stats(),
            'config': self.config,
            'status': self._determine_status()
        }