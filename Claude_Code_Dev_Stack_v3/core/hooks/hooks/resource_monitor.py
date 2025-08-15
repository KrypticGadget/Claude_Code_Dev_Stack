#!/usr/bin/env python3
"""
Resource Monitor Hook - V3.0+ System Resource Management
Prevents file size issues, manages logs, and monitors disk/memory usage
"""

import os
import json
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import gzip

class ResourceMonitor:
    """Monitor and manage system resources to prevent Claude Code conflicts"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Resource limits from settings
        limits = self.settings.get('v3ExtendedFeatures', {}).get('resourceManagement', {})
        self.log_rotation = limits.get('logRotation', {})
        self.max_log_size = self.parse_size(self.log_rotation.get('maxSize', '10MB'))
        self.max_log_age = self.log_rotation.get('maxAge', 7)  # days
        self.compress_logs = self.log_rotation.get('compress', True)
        
        # Context compression
        context_config = limits.get('contextCompression', {})
        self.compression_threshold = context_config.get('threshold', 0.8)
        self.aggressive_threshold = context_config.get('aggressive', 0.9)
        
        # Directory limits
        self.max_audio_cache = self.parse_size('50MB')
        self.max_state_size = self.parse_size('5MB')
        self.max_total_size = self.parse_size('500MB')
        
        # Start cleanup on init
        self.cleanup_old_files()
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = self.claude_dir / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper().strip()
        units = {'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
        
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
        
        return int(size_str)  # Assume bytes if no unit
    
    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total
    
    def rotate_logs(self):
        """Rotate log files to prevent them from getting too large"""
        log_dir = self.claude_dir / 'logs'
        if not log_dir.exists():
            return
        
        rotated = []
        
        for log_file in log_dir.glob('*.log'):
            try:
                size = log_file.stat().st_size
                
                # Check if rotation needed
                if size > self.max_log_size:
                    # Create rotated filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    rotated_name = f"{log_file.stem}_{timestamp}.log"
                    
                    if self.compress_logs:
                        # Compress and rotate
                        rotated_path = log_dir / f"{rotated_name}.gz"
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(rotated_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    else:
                        # Just rename
                        rotated_path = log_dir / rotated_name
                        shutil.move(str(log_file), str(rotated_path))
                    
                    # Create new empty log file
                    log_file.touch()
                    rotated.append(str(rotated_path))
                    
            except Exception as e:
                print(f"Error rotating {log_file}: {e}")
        
        return rotated
    
    def cleanup_old_files(self):
        """Remove old log files and temporary files"""
        cutoff_date = datetime.now() - timedelta(days=self.max_log_age)
        removed = []
        
        # Clean old logs
        log_dir = self.claude_dir / 'logs'
        if log_dir.exists():
            for log_file in log_dir.glob('*'):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff_date:
                        log_file.unlink()
                        removed.append(str(log_file))
                except:
                    pass
        
        # Clean old state files
        state_dir = self.claude_dir / 'state'
        if state_dir.exists():
            for state_file in state_dir.glob('*.old'):
                try:
                    state_file.unlink()
                    removed.append(str(state_file))
                except:
                    pass
        
        # Clean temp files
        temp_patterns = ['*.tmp', '*.temp', '*~', '*.swp']
        for pattern in temp_patterns:
            for temp_file in self.claude_dir.rglob(pattern):
                try:
                    temp_file.unlink()
                    removed.append(str(temp_file))
                except:
                    pass
        
        return removed
    
    def compress_context(self, context: Dict) -> Dict:
        """Compress context to reduce size"""
        compressed = {}
        
        # Keep only essential fields
        essential_fields = [
            'current_phase', 'active_agents', 'token_usage',
            'recent_operations', 'critical_state'
        ]
        
        for field in essential_fields:
            if field in context:
                compressed[field] = context[field]
        
        # Truncate large fields
        if 'conversation_history' in context:
            # Keep only last 10 exchanges
            compressed['conversation_history'] = context['conversation_history'][-10:]
        
        if 'file_contents' in context:
            # Remove file contents, keep only paths
            compressed['file_paths'] = list(context['file_contents'].keys())
        
        return compressed
    
    def check_resource_usage(self) -> Dict[str, any]:
        """Check current resource usage"""
        usage = {
            'total_size': 0,
            'logs_size': 0,
            'audio_size': 0,
            'state_size': 0,
            'issues': [],
            'warnings': []
        }
        
        # Check total Claude directory size
        total_size = self.get_directory_size(self.claude_dir)
        usage['total_size'] = total_size
        
        if total_size > self.max_total_size:
            usage['issues'].append(f"Total size ({total_size/1024/1024:.1f}MB) exceeds limit")
        elif total_size > self.max_total_size * 0.8:
            usage['warnings'].append(f"Total size approaching limit (80% used)")
        
        # Check logs
        log_dir = self.claude_dir / 'logs'
        if log_dir.exists():
            logs_size = self.get_directory_size(log_dir)
            usage['logs_size'] = logs_size
            
            # Check individual log files
            for log_file in log_dir.glob('*.log'):
                if log_file.stat().st_size > self.max_log_size:
                    usage['issues'].append(f"Log file {log_file.name} needs rotation")
        
        # Check audio cache
        audio_dir = self.claude_dir / 'audio'
        if audio_dir.exists():
            audio_size = self.get_directory_size(audio_dir)
            usage['audio_size'] = audio_size
            
            if audio_size > self.max_audio_cache:
                usage['warnings'].append(f"Audio cache large ({audio_size/1024/1024:.1f}MB)")
        
        # Check state files
        state_dir = self.claude_dir / 'state'
        if state_dir.exists():
            state_size = self.get_directory_size(state_dir)
            usage['state_size'] = state_size
            
            if state_size > self.max_state_size:
                usage['issues'].append(f"State files too large ({state_size/1024/1024:.1f}MB)")
        
        return usage
    
    def auto_cleanup(self) -> Tuple[bool, List[str]]:
        """Automatically cleanup to free resources"""
        actions = []
        
        # Check resource usage
        usage = self.check_resource_usage()
        
        if usage['issues']:
            # Rotate logs if needed
            rotated = self.rotate_logs()
            if rotated:
                actions.append(f"Rotated {len(rotated)} log files")
            
            # Clean old files
            removed = self.cleanup_old_files()
            if removed:
                actions.append(f"Removed {len(removed)} old files")
            
            # Compress old state files
            state_dir = self.claude_dir / 'state'
            if state_dir.exists():
                for state_file in state_dir.glob('*.json'):
                    if state_file.stat().st_size > 1024 * 1024:  # > 1MB
                        try:
                            # Compress state file
                            with open(state_file, 'r') as f:
                                data = json.load(f)
                            compressed = self.compress_context(data)
                            with open(state_file, 'w') as f:
                                json.dump(compressed, f)
                            actions.append(f"Compressed {state_file.name}")
                        except:
                            pass
        
        # Trigger warnings if needed
        if usage['warnings']:
            self.trigger_warning(usage['warnings'])
        
        return len(usage['issues']) == 0, actions
    
    def trigger_warning(self, warnings: List[str]):
        """Trigger warning for resource issues"""
        try:
            # Play warning audio
            audio_path = self.claude_dir / 'audio' / 'resource_warning.wav'
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            # Send notification
            from notification_sender import get_sender
            sender = get_sender()
            sender.send_custom(
                "Resource Warning",
                "\n".join(warnings),
                1
            )
        except:
            pass
    
    def monitor_file_write(self, file_path: str, content_size: int) -> bool:
        """Check if file write would cause issues"""
        # Check if file would be too large
        if content_size > 10 * 1024 * 1024:  # 10MB
            return False
        
        # Check if we have space
        usage = self.check_resource_usage()
        if usage['total_size'] + content_size > self.max_total_size:
            # Try to cleanup first
            self.auto_cleanup()
            # Check again
            usage = self.check_resource_usage()
            if usage['total_size'] + content_size > self.max_total_size:
                return False
        
        return True

# Global instance
_monitor = None

def get_monitor():
    """Get or create monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = ResourceMonitor()
    return _monitor

def main():
    """Hook entry point"""
    import sys
    
    monitor = get_monitor()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'check':
            usage = monitor.check_resource_usage()
            print(json.dumps(usage, indent=2))
        
        elif action == 'cleanup':
            success, actions = monitor.auto_cleanup()
            print(f"Cleanup {'successful' if success else 'completed with issues'}")
            for action in actions:
                print(f"  - {action}")
        
        elif action == 'rotate':
            rotated = monitor.rotate_logs()
            print(f"Rotated {len(rotated)} log files")
        
        elif action == 'pre-write' and len(sys.argv) > 3:
            file_path = sys.argv[2]
            content_size = int(sys.argv[3])
            allowed = monitor.monitor_file_write(file_path, content_size)
            if not allowed:
                print(f"File write blocked: size too large or insufficient space")
                sys.exit(1)

if __name__ == '__main__':
    main()