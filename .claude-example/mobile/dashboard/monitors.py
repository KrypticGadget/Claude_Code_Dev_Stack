#!/usr/bin/env python3
"""
Comprehensive Monitoring Services for Claude Code V3+ Dashboard
Real-time monitoring of Claude sessions, Git repositories, file changes, and system metrics
"""

import json
import os
import threading
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil

try:
    import git
    from git import Repo
except ImportError:
    print("GitPython required. Install with: pip install GitPython")
    git = None

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Watchdog required. Install with: pip install watchdog")
    Observer = None
    FileSystemEventHandler = None

# Import socketio from dashboard_server to emit events
try:
    from dashboard_server import DashboardServer
except ImportError:
    DashboardServer = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseMonitor:
    """Base class for all monitors"""
    
    def __init__(self, name: str, socketio=None):
        self.name = name
        self.socketio = socketio
        self.running = False
        self.thread = None
        self.error_count = 0
        self.last_error = None
        self.start_time = None
        
    def start(self):
        """Start the monitor"""
        if self.running:
            logger.warning(f"{self.name} monitor already running")
            return
            
        logger.info(f"Starting {self.name} monitor")
        self.running = True
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the monitor"""
        if not self.running:
            return
            
        logger.info(f"Stopping {self.name} monitor")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def _run_loop(self):
        """Main monitoring loop - to be implemented by subclasses"""
        raise NotImplementedError
    
    def _emit_event(self, event_name: str, data: Dict):
        """Emit event via SocketIO if available"""
        if self.socketio:
            try:
                self.socketio.emit(event_name, {
                    'monitor': self.name,
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                })
            except Exception as e:
                logger.error(f"Error emitting event {event_name}: {e}")
    
    def _handle_error(self, error: Exception):
        """Handle errors gracefully"""
        self.error_count += 1
        self.last_error = str(error)
        logger.error(f"{self.name} monitor error: {error}")
        
        # Emit error event
        self._emit_event('monitor_error', {
            'monitor': self.name,
            'error': str(error),
            'error_count': self.error_count
        })
    
    def get_status(self) -> Dict:
        """Get monitor status"""
        return {
            'name': self.name,
            'running': self.running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None
        }

class ClaudeMonitor(BaseMonitor):
    """Monitor Claude sessions from ~/.claude/sessions/*.json files"""
    
    def __init__(self, socketio=None):
        super().__init__("Claude", socketio)
        self.claude_dir = Path.home() / '.claude'
        self.sessions_dir = self.claude_dir / 'sessions'
        self.last_sessions = {}
        self.emit_interval = 3  # seconds
        
    def _run_loop(self):
        """Monitor Claude sessions every 3 seconds"""
        while self.running:
            try:
                session_data = self._get_session_data()
                
                # Only emit if data has changed
                if session_data != self.last_sessions:
                    self._emit_event('claude_sessions_update', session_data)
                    self.last_sessions = session_data.copy()
                
                time.sleep(self.emit_interval)
                
            except Exception as e:
                self._handle_error(e)
                time.sleep(self.emit_interval * 2)  # Wait longer on error
    
    def _get_session_data(self) -> Dict:
        """Parse session files and extract data"""
        if not self.sessions_dir.exists():
            return {'sessions': [], 'total': 0, 'active': 0}
        
        sessions = []
        active_count = 0
        total_tokens = 0
        total_cost = 0.0
        
        try:
            session_files = list(self.sessions_dir.glob('*.json'))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # Extract session information
                    session_id = session_file.stem
                    status = self._determine_session_status(session_data, session_file)
                    tokens = self._extract_token_usage(session_data)
                    cost = self._estimate_cost(tokens)
                    last_activity = self._get_last_activity(session_file)
                    
                    session_info = {
                        'id': session_id,
                        'status': status,
                        'tokens_used': tokens,
                        'estimated_cost': cost,
                        'last_activity': last_activity,
                        'file_size': session_file.stat().st_size,
                        'created': datetime.fromtimestamp(session_file.stat().st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(session_file.stat().st_mtime).isoformat()
                    }
                    
                    sessions.append(session_info)
                    
                    if status == 'active':
                        active_count += 1
                    
                    total_tokens += tokens
                    total_cost += cost
                    
                except Exception as e:
                    logger.error(f"Error parsing session {session_file}: {e}")
                    continue
            
            # Sort by last activity
            sessions.sort(key=lambda x: x['last_activity'] or '', reverse=True)
            
            return {
                'sessions': sessions,
                'total': len(sessions),
                'active': active_count,
                'total_tokens': total_tokens,
                'total_cost': round(total_cost, 4),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting session data: {e}")
            return {'sessions': [], 'total': 0, 'active': 0, 'error': str(e)}
    
    def _determine_session_status(self, session_data: Dict, session_file: Path) -> str:
        """Determine if session is active, idle, or closed"""
        try:
            # Check file modification time
            mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)
            time_diff = datetime.now() - mod_time
            
            if time_diff < timedelta(minutes=5):
                return 'active'
            elif time_diff < timedelta(hours=1):
                return 'idle'
            else:
                return 'closed'
                
        except:
            return 'unknown'
    
    def _extract_token_usage(self, session_data: Dict) -> int:
        """Extract token usage from session data"""
        try:
            # Look for various token fields
            if isinstance(session_data, dict):
                # Check common token fields
                for field in ['tokens_used', 'total_tokens', 'token_count']:
                    if field in session_data:
                        return int(session_data[field])
                
                # Check for conversation data
                if 'conversations' in session_data:
                    conversations = session_data['conversations']
                    if isinstance(conversations, list):
                        total = 0
                        for conv in conversations:
                            if isinstance(conv, dict) and 'tokens' in conv:
                                total += int(conv.get('tokens', 0))
                        return total
                
                # Estimate from text length
                if 'content' in session_data or 'messages' in session_data:
                    content = str(session_data.get('content', '')) + str(session_data.get('messages', ''))
                    return len(content) // 4  # Rough estimate: 1 token per 4 characters
            
            return 0
            
        except Exception as e:
            logger.debug(f"Error extracting tokens: {e}")
            return 0
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage"""
        # Rough estimates for Claude pricing (adjust as needed)
        cost_per_1k_tokens = 0.008  # $0.008 per 1K tokens (approximate)
        return (tokens / 1000) * cost_per_1k_tokens
    
    def _get_last_activity(self, session_file: Path) -> Optional[str]:
        """Get last activity timestamp"""
        try:
            mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)
            return mod_time.isoformat()
        except:
            return None

class GitMonitor(BaseMonitor):
    """Monitor Git repository status and changes"""
    
    def __init__(self, repo_path: Optional[str] = None, socketio=None):
        super().__init__("Git", socketio)
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        self.last_commit_hash = None
        self.last_branch = None
        self.last_status = {}
        self.emit_interval = 5  # seconds
        
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize Git repository"""
        try:
            if git:
                self.repo = Repo(self.repo_path)
                logger.info(f"Git monitor initialized for: {self.repo_path}")
            else:
                logger.error("GitPython not available")
        except Exception as e:
            logger.error(f"Failed to initialize Git repo: {e}")
            self.repo = None
    
    def _run_loop(self):
        """Monitor Git repository every 5 seconds"""
        while self.running:
            try:
                if self.repo:
                    git_data = self._get_git_data()
                    
                    # Check for changes
                    current_commit = git_data.get('latest_commit', {}).get('hash')
                    current_branch = git_data.get('current_branch')
                    current_status = git_data.get('status', {})
                    
                    if (current_commit != self.last_commit_hash or 
                        current_branch != self.last_branch or
                        current_status != self.last_status):
                        
                        self._emit_event('git_status_update', git_data)
                        
                        self.last_commit_hash = current_commit
                        self.last_branch = current_branch
                        self.last_status = current_status
                
                time.sleep(self.emit_interval)
                
            except Exception as e:
                self._handle_error(e)
                time.sleep(self.emit_interval * 2)
    
    def _get_git_data(self) -> Dict:
        """Get comprehensive Git repository data"""
        if not self.repo:
            return {'error': 'Git repository not available'}
        
        try:
            # Current branch
            try:
                current_branch = self.repo.active_branch.name
            except:
                current_branch = 'detached HEAD'
            
            # Latest commit
            latest_commit = self.repo.head.commit
            commit_info = {
                'hash': latest_commit.hexsha[:8],
                'full_hash': latest_commit.hexsha,
                'message': latest_commit.message.strip(),
                'author': str(latest_commit.author),
                'date': datetime.fromtimestamp(latest_commit.committed_date).isoformat(),
                'timestamp': latest_commit.committed_date
            }
            
            # Repository status
            status = {
                'modified_files': [],
                'staged_files': [],
                'untracked_files': [],
                'deleted_files': []
            }
            
            # Get modified/staged files
            for item in self.repo.index.diff(None):
                status['modified_files'].append({
                    'path': item.a_path,
                    'change_type': item.change_type
                })
            
            # Get staged files
            for item in self.repo.index.diff('HEAD'):
                status['staged_files'].append({
                    'path': item.a_path,
                    'change_type': item.change_type
                })
            
            # Get untracked files
            status['untracked_files'] = list(self.repo.untracked_files)
            
            # Recent commits (last 10)
            recent_commits = []
            for commit in list(self.repo.iter_commits(max_count=10)):
                recent_commits.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip().split('\n')[0][:80],
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat()
                })
            
            # Branch information
            branches = []
            for branch in self.repo.branches:
                branches.append({
                    'name': branch.name,
                    'active': branch.name == current_branch,
                    'commit': branch.commit.hexsha[:8]
                })
            
            # Remote information
            remotes = []
            for remote in self.repo.remotes:
                remotes.append({
                    'name': remote.name,
                    'url': list(remote.urls)[0] if remote.urls else None
                })
            
            return {
                'repo_path': str(self.repo_path),
                'current_branch': current_branch,
                'latest_commit': commit_info,
                'status': status,
                'recent_commits': recent_commits,
                'branches': branches,
                'remotes': remotes,
                'stats': {
                    'total_commits': len(list(self.repo.iter_commits())),
                    'total_branches': len(branches),
                    'total_remotes': len(remotes),
                    'modified_files': len(status['modified_files']),
                    'staged_files': len(status['staged_files']),
                    'untracked_files': len(status['untracked_files'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting Git data: {e}")
            return {'error': str(e)}

class FileMonitor(BaseMonitor):
    """Monitor file system changes using watchdog"""
    
    def __init__(self, watch_paths: List[str] = None, socketio=None):
        super().__init__("FileSystem", socketio)
        self.watch_paths = watch_paths or [os.getcwd()]
        self.observers = []
        self.ignored_patterns = [
            '.git',
            '__pycache__',
            'node_modules',
            '.vscode',
            '.idea',
            '*.pyc',
            '*.pyo',
            '*.log',
            '.DS_Store',
            'Thumbs.db'
        ]
        
    def start(self):
        """Start file monitoring with watchdog observers"""
        if Observer is None or FileSystemEventHandler is None:
            logger.error("Watchdog not available for file monitoring")
            return
            
        logger.info(f"Starting file monitor for paths: {self.watch_paths}")
        self.running = True
        self.start_time = datetime.now()
        
        try:
            for path in self.watch_paths:
                if os.path.exists(path):
                    observer = Observer()
                    event_handler = FileChangeHandler(self)
                    observer.schedule(event_handler, path, recursive=True)
                    observer.start()
                    self.observers.append(observer)
                    logger.info(f"Watching path: {path}")
                else:
                    logger.warning(f"Path does not exist: {path}")
                    
        except Exception as e:
            self._handle_error(e)
    
    def stop(self):
        """Stop all file observers"""
        self.running = False
        
        for observer in self.observers:
            try:
                observer.stop()
                observer.join(timeout=2)
            except Exception as e:
                logger.error(f"Error stopping observer: {e}")
        
        self.observers.clear()
        logger.info("File monitor stopped")
    
    def _run_loop(self):
        """File monitor uses observers, no loop needed"""
        pass
    
    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored"""
        path_lower = path.lower()
        
        for pattern in self.ignored_patterns:
            if pattern.startswith('*'):
                # Extension pattern
                if path_lower.endswith(pattern[1:]):
                    return True
            else:
                # Directory/file pattern
                if pattern in path_lower:
                    return True
        
        return False
    
    def emit_file_change(self, event_type: str, path: str, is_directory: bool = False):
        """Emit file change event"""
        if self.should_ignore_path(path):
            return
            
        file_info = self._get_file_info(path)
        
        self._emit_event('file_change', {
            'event_type': event_type,
            'path': path,
            'is_directory': is_directory,
            'file_info': file_info
        })
    
    def _get_file_info(self, path: str) -> Dict:
        """Get file information"""
        try:
            if os.path.exists(path):
                stat = os.stat(path)
                return {
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'extension': os.path.splitext(path)[1] if not os.path.isdir(path) else None,
                    'name': os.path.basename(path)
                }
            return {}
        except:
            return {}

class FileChangeHandler(FileSystemEventHandler):
    """File system event handler"""
    
    def __init__(self, file_monitor: FileMonitor):
        super().__init__()
        self.file_monitor = file_monitor
    
    def on_modified(self, event):
        self.file_monitor.emit_file_change('modified', event.src_path, event.is_directory)
    
    def on_created(self, event):
        self.file_monitor.emit_file_change('created', event.src_path, event.is_directory)
    
    def on_deleted(self, event):
        self.file_monitor.emit_file_change('deleted', event.src_path, event.is_directory)
    
    def on_moved(self, event):
        self.file_monitor.emit_file_change('moved', event.dest_path, event.is_directory)

class SystemMonitor(BaseMonitor):
    """Monitor system metrics using psutil"""
    
    def __init__(self, socketio=None):
        super().__init__("System", socketio)
        self.emit_interval = 2  # seconds
        self.history_size = 60  # Keep 60 data points (2 minutes of history)
        self.metrics_history = []
        
    def _run_loop(self):
        """Monitor system metrics every 2 seconds"""
        while self.running:
            try:
                metrics = self._get_system_metrics()
                
                # Add to history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.history_size:
                    self.metrics_history.pop(0)
                
                # Emit current metrics with history
                self._emit_event('system_metrics_update', {
                    'current': metrics,
                    'history': self.metrics_history[-20:] if len(self.metrics_history) >= 20 else self.metrics_history
                })
                
                time.sleep(self.emit_interval)
                
            except Exception as e:
                self._handle_error(e)
                time.sleep(self.emit_interval * 2)
    
    def _get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Boot time and uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            # Load average (Unix-like systems)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except:
                pass
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else None,
                        'min': cpu_freq.min if cpu_freq else None,
                        'max': cpu_freq.max if cpu_freq else None
                    } if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2)
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent,
                    'total_gb': round(swap.total / (1024**3), 2) if swap.total > 0 else 0,
                    'used_gb': round(swap.used / (1024**3), 2) if swap.used > 0 else 0
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent,
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'io': {
                        'read_bytes': disk_io.read_bytes if disk_io else 0,
                        'write_bytes': disk_io.write_bytes if disk_io else 0,
                        'read_count': disk_io.read_count if disk_io else 0,
                        'write_count': disk_io.write_count if disk_io else 0
                    } if disk_io else None
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent if net_io else 0,
                    'bytes_recv': net_io.bytes_recv if net_io else 0,
                    'packets_sent': net_io.packets_sent if net_io else 0,
                    'packets_recv': net_io.packets_recv if net_io else 0,
                    'errin': net_io.errin if net_io else 0,
                    'errout': net_io.errout if net_io else 0,
                    'dropin': net_io.dropin if net_io else 0,
                    'dropout': net_io.dropout if net_io else 0
                } if net_io else None,
                'system': {
                    'process_count': process_count,
                    'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                    'uptime_seconds': uptime,
                    'uptime_formatted': self._format_uptime(uptime),
                    'load_average': load_avg
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human readable format"""
        try:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"

class MonitorManager:
    """Coordinate all monitoring services"""
    
    def __init__(self, socketio=None, config: Dict = None):
        self.socketio = socketio
        self.config = config or {}
        self.monitors = {}
        self.running = False
        
        # Initialize monitors
        self._initialize_monitors()
    
    def _initialize_monitors(self):
        """Initialize all monitor instances"""
        try:
            # Claude Monitor
            self.monitors['claude'] = ClaudeMonitor(self.socketio)
            
            # Git Monitor
            repo_path = self.config.get('git_repo_path')
            self.monitors['git'] = GitMonitor(repo_path, self.socketio)
            
            # File Monitor
            watch_paths = self.config.get('watch_paths', [os.getcwd()])
            self.monitors['file'] = FileMonitor(watch_paths, self.socketio)
            
            # System Monitor
            self.monitors['system'] = SystemMonitor(self.socketio)
            
            logger.info(f"Initialized {len(self.monitors)} monitors")
            
        except Exception as e:
            logger.error(f"Error initializing monitors: {e}")
    
    def start_all(self):
        """Start all monitors"""
        logger.info("Starting all monitors")
        self.running = True
        
        for name, monitor in self.monitors.items():
            try:
                monitor.start()
                logger.info(f"Started {name} monitor")
            except Exception as e:
                logger.error(f"Failed to start {name} monitor: {e}")
        
        # Emit manager status
        self._emit_status_update()
    
    def stop_all(self):
        """Stop all monitors"""
        logger.info("Stopping all monitors")
        self.running = False
        
        for name, monitor in self.monitors.items():
            try:
                monitor.stop()
                logger.info(f"Stopped {name} monitor")
            except Exception as e:
                logger.error(f"Error stopping {name} monitor: {e}")
    
    def get_monitor_status(self) -> Dict:
        """Get status of all monitors"""
        status = {
            'manager_running': self.running,
            'total_monitors': len(self.monitors),
            'running_monitors': 0,
            'monitors': {}
        }
        
        for name, monitor in self.monitors.items():
            monitor_status = monitor.get_status()
            status['monitors'][name] = monitor_status
            
            if monitor_status['running']:
                status['running_monitors'] += 1
        
        return status
    
    def restart_monitor(self, monitor_name: str):
        """Restart a specific monitor"""
        if monitor_name in self.monitors:
            try:
                monitor = self.monitors[monitor_name]
                logger.info(f"Restarting {monitor_name} monitor")
                
                monitor.stop()
                time.sleep(1)  # Brief pause
                monitor.start()
                
                logger.info(f"Restarted {monitor_name} monitor")
                
            except Exception as e:
                logger.error(f"Error restarting {monitor_name} monitor: {e}")
        else:
            logger.error(f"Monitor {monitor_name} not found")
    
    def _emit_status_update(self):
        """Emit monitor manager status update"""
        if self.socketio:
            try:
                status = self.get_monitor_status()
                self.socketio.emit('monitor_status_update', {
                    'timestamp': datetime.now().isoformat(),
                    'status': status
                })
            except Exception as e:
                logger.error(f"Error emitting status update: {e}")
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return {
            'config': self.config,
            'monitor_count': len(self.monitors),
            'running': self.running
        }
    
    def update_config(self, new_config: Dict):
        """Update configuration and restart affected monitors"""
        self.config.update(new_config)
        logger.info("Configuration updated")
        
        # For now, restart all monitors on config change
        # Could be optimized to only restart affected monitors
        if self.running:
            self.stop_all()
            time.sleep(2)
            self._initialize_monitors()
            self.start_all()

# Global instance
monitor_manager = None

def create_monitor_manager(socketio=None, config: Dict = None) -> MonitorManager:
    """Create and return monitor manager instance"""
    global monitor_manager
    
    if monitor_manager is None:
        monitor_manager = MonitorManager(socketio, config)
    
    return monitor_manager

def get_monitor_manager() -> Optional[MonitorManager]:
    """Get existing monitor manager instance"""
    return monitor_manager

# Example usage and testing
if __name__ == '__main__':
    # Test monitoring without SocketIO
    print("Testing monitors without SocketIO...")
    
    config = {
        'watch_paths': [os.getcwd()],
        'git_repo_path': os.getcwd()
    }
    
    manager = create_monitor_manager(config=config)
    
    try:
        manager.start_all()
        
        # Let it run for a bit
        print("Monitors running... Press Ctrl+C to stop")
        
        while True:
            time.sleep(5)
            status = manager.get_monitor_status()
            print(f"Status: {status['running_monitors']}/{status['total_monitors']} monitors running")
            
    except KeyboardInterrupt:
        print("\nStopping monitors...")
        manager.stop_all()
        print("Monitors stopped.")