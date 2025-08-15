#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code V3+ Monitoring Services
Comprehensive real-time monitoring system for Claude sessions, Git activity, file changes, and system metrics
Optimized for Windows compatibility and Samsung Galaxy S25 Edge mobile access
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from queue import Queue, Empty
import psutil

# Fix Windows Unicode encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def safe_print(text: str):
    """Safe printing that handles Unicode on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

@dataclass
class MonitorEvent:
    """Data class for monitor events"""
    timestamp: datetime
    monitor_type: str
    event_type: str
    data: Dict[str, Any]
    session_id: Optional[str] = None

class BaseMonitor:
    """Base class for all monitors"""
    
    def __init__(self, name: str, update_interval: float = 5.0):
        self.name = name
        self.update_interval = update_interval
        self.is_running = False
        self.last_update = None
        self.event_queue = Queue()
        self.callbacks: List[Callable] = []
        self.logger = logging.getLogger(f'monitor.{name}')
        self._thread = None
        self._stop_event = threading.Event()
    
    def add_callback(self, callback: Callable[[MonitorEvent], None]):
        """Add a callback function to be called on events"""
        self.callbacks.append(callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any], session_id: Optional[str] = None):
        """Emit a monitoring event"""
        event = MonitorEvent(
            timestamp=datetime.now(),
            monitor_type=self.name,
            event_type=event_type,
            data=data,
            session_id=session_id
        )
        
        # Add to queue
        try:
            self.event_queue.put_nowait(event)
        except:
            pass  # Queue full, skip
        
        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Error in callback: {e}")
    
    def start(self):
        """Start monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        self.logger.info(f"Started {self.name} monitor")
    
    def stop(self):
        """Stop monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        
        self.logger.info(f"Stopped {self.name} monitor")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running and not self._stop_event.is_set():
            try:
                start_time = time.time()
                self.update()
                self.last_update = datetime.now()
                
                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                
                if sleep_time > 0:
                    self._stop_event.wait(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                self._stop_event.wait(1)  # Brief pause on error
    
    def update(self):
        """Override this method to implement monitoring logic"""
        raise NotImplementedError
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest monitoring data"""
        return None

class ClaudeMonitor(BaseMonitor):
    """Monitor Claude sessions and activity"""
    
    def __init__(self, update_interval: float = 5.0):
        super().__init__('claude', update_interval)
        self.claude_dir = Path.home() / '.claude'
        self.sessions_dir = self.claude_dir / 'sessions'
        self.last_session_states = {}
        self.active_sessions = {}
    
    def update(self):
        """Update Claude session monitoring"""
        try:
            sessions = self.scan_sessions()
            
            # Check for new, updated, or removed sessions
            current_session_ids = set(sessions.keys())
            previous_session_ids = set(self.last_session_states.keys())
            
            # New sessions
            new_sessions = current_session_ids - previous_session_ids
            for session_id in new_sessions:
                self.emit_event('session_created', sessions[session_id], session_id)
            
            # Updated sessions
            for session_id in current_session_ids & previous_session_ids:
                current = sessions[session_id]
                previous = self.last_session_states[session_id]
                
                if current.get('last_updated') != previous.get('last_updated'):
                    self.emit_event('session_updated', current, session_id)
                
                if current.get('message_count', 0) > previous.get('message_count', 0):
                    self.emit_event('new_message', {
                        'session_id': session_id,
                        'new_messages': current.get('message_count', 0) - previous.get('message_count', 0),
                        'total_messages': current.get('message_count', 0)
                    }, session_id)
            
            # Removed sessions
            removed_sessions = previous_session_ids - current_session_ids
            for session_id in removed_sessions:
                self.emit_event('session_removed', {'session_id': session_id}, session_id)
            
            # Update active sessions
            self.active_sessions = {k: v for k, v in sessions.items() if v.get('active', False)}
            self.last_session_states = sessions
            
            # Emit summary data
            self.emit_event('sessions_summary', {
                'total_sessions': len(sessions),
                'active_sessions': len(self.active_sessions),
                'new_sessions': len(new_sessions),
                'updated_sessions': len(current_session_ids & previous_session_ids)
            })
            
        except Exception as e:
            self.logger.error(f"Error updating Claude sessions: {e}")
            self.emit_event('error', {'error': str(e)})
    
    def scan_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Scan and parse Claude session files"""
        sessions = {}
        
        if not self.sessions_dir.exists():
            return sessions
        
        try:
            for session_file in self.sessions_dir.glob('*.json'):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    session_id = session_file.stem
                    sessions[session_id] = self.parse_session_data(session_id, session_data)
                    
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    self.logger.warning(f"Could not parse session file {session_file}: {e}")
                except Exception as e:
                    self.logger.error(f"Error reading session file {session_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error scanning sessions directory: {e}")
        
        return sessions
    
    def parse_session_data(self, session_id: str, data: Dict) -> Dict[str, Any]:
        """Parse session data into standardized format"""
        try:
            messages = data.get('messages', [])
            
            # Calculate session metrics
            message_count = len(messages)
            last_message_time = None
            user_messages = 0
            assistant_messages = 0
            
            if messages:
                # Count message types
                for msg in messages:
                    if msg.get('role') == 'user':
                        user_messages += 1
                    elif msg.get('role') == 'assistant':
                        assistant_messages += 1
                
                # Get last message timestamp
                last_msg = messages[-1]
                last_message_time = last_msg.get('timestamp') or last_msg.get('created_at')
            
            # Determine if session is active (updated within last hour)
            is_active = False
            if last_message_time:
                try:
                    if isinstance(last_message_time, str):
                        from dateutil import parser
                        last_time = parser.parse(last_message_time)
                    else:
                        last_time = datetime.fromtimestamp(last_message_time)
                    
                    time_diff = datetime.now(last_time.tzinfo) - last_time
                    is_active = time_diff.total_seconds() < 3600  # 1 hour
                except Exception:
                    pass
            
            return {
                'id': session_id,
                'created_at': data.get('created_at'),
                'last_updated': data.get('updated_at') or last_message_time,
                'message_count': message_count,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'active': is_active,
                'model': data.get('model', 'unknown'),
                'title': data.get('title', ''),
                'last_message_time': last_message_time,
                'file_path': str(self.sessions_dir / f"{session_id}.json")
            }
        
        except Exception as e:
            self.logger.error(f"Error parsing session data for {session_id}: {e}")
            return {
                'id': session_id,
                'error': str(e),
                'active': False,
                'message_count': 0
            }
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get latest Claude session data"""
        return {
            'sessions': list(self.last_session_states.values()),
            'active_sessions': list(self.active_sessions.values()),
            'summary': {
                'total': len(self.last_session_states),
                'active': len(self.active_sessions)
            }
        }
    
    def get_claude_sessions(self) -> List[Dict]:
        """Get Claude sessions in the format expected by dashboard"""
        return list(self.last_session_states.values())

class GitMonitor(BaseMonitor):
    """Monitor Git repository activity"""
    
    def __init__(self, repo_path: str = ".", update_interval: float = 3.0):
        super().__init__('git', update_interval)
        self.repo_path = Path(repo_path).resolve()
        self.last_commit_hash = None
        self.last_status = None
        self.last_branch = None
        self.git_available = self.check_git_available()
    
    def check_git_available(self) -> bool:
        """Check if git is available and this is a git repository"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  cwd=self.repo_path, capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def update(self):
        """Update Git monitoring"""
        if not self.git_available:
            return
        
        try:
            # Get current status
            current_status = self.get_git_status_detailed()
            current_commit = current_status.get('current_commit')
            current_branch = current_status.get('branch')
            
            # Check for changes
            if current_commit != self.last_commit_hash:
                if self.last_commit_hash is not None:  # Not first run
                    self.emit_event('new_commit', {
                        'commit': current_commit,
                        'previous_commit': self.last_commit_hash,
                        'branch': current_branch
                    })
                self.last_commit_hash = current_commit
            
            if current_branch != self.last_branch:
                if self.last_branch is not None:  # Not first run
                    self.emit_event('branch_changed', {
                        'new_branch': current_branch,
                        'previous_branch': self.last_branch
                    })
                self.last_branch = current_branch
            
            # Check for status changes
            current_status_summary = current_status.get('status')
            if current_status_summary != self.last_status:
                self.emit_event('status_changed', {
                    'status': current_status_summary,
                    'changes': current_status.get('changes', []),
                    'untracked': current_status.get('untracked', [])
                })
                self.last_status = current_status_summary
            
            # Emit regular update
            self.emit_event('status_update', current_status)
            
        except Exception as e:
            self.logger.error(f"Error updating Git status: {e}")
            self.emit_event('error', {'error': str(e)})
    
    def get_git_status_detailed(self) -> Dict[str, Any]:
        """Get detailed Git status information"""
        status_info = {
            'status': 'unknown',
            'branch': 'unknown',
            'current_commit': None,
            'commits': [],
            'changes': [],
            'untracked': [],
            'ahead': 0,
            'behind': 0
        }
        
        try:
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=self.repo_path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status_info['branch'] = result.stdout.strip() or 'detached'
            
            # Get current commit
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=self.repo_path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status_info['current_commit'] = result.stdout.strip()
            
            # Get recent commits
            result = subprocess.run(['git', 'log', '--oneline', '-10', '--format=%H|%s|%an|%ad'], 
                                  cwd=self.repo_path, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) >= 2:
                            commits.append({
                                'hash': parts[0][:8],  # Short hash
                                'full_hash': parts[0],
                                'message': parts[1],
                                'author': parts[2] if len(parts) > 2 else 'unknown',
                                'date': parts[3] if len(parts) > 3 else 'unknown'
                            })
                status_info['commits'] = commits
            
            # Get working directory status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.repo_path, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                changes = []
                untracked = []
                
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        filename = line[3:]
                        
                        change_info = {
                            'status': status_code,
                            'file': filename,
                            'staged': status_code[0] != ' ',
                            'modified': status_code[1] != ' '
                        }
                        
                        if status_code.startswith('??'):
                            untracked.append(change_info)
                        else:
                            changes.append(change_info)
                
                status_info['changes'] = changes
                status_info['untracked'] = untracked
                
                if not changes and not untracked:
                    status_info['status'] = 'clean'
                else:
                    status_info['status'] = 'modified'
            
            # Get ahead/behind information
            try:
                result = subprocess.run(['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'], 
                                      cwd=self.repo_path, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    counts = result.stdout.strip().split('\t')
                    if len(counts) == 2:
                        status_info['ahead'] = int(counts[0])
                        status_info['behind'] = int(counts[1])
            except Exception:
                pass  # Upstream not configured
            
        except subprocess.TimeoutExpired:
            status_info['status'] = 'timeout'
        except Exception as e:
            status_info['status'] = f'error: {str(e)}'
        
        return status_info
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get latest Git data"""
        return self.get_git_status_detailed()
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get Git status in the format expected by dashboard"""
        return self.get_git_status_detailed()

class FileMonitor(BaseMonitor):
    """Monitor file system changes"""
    
    def __init__(self, watch_paths: List[str] = None, update_interval: float = 1.0):
        super().__init__('file', update_interval)
        self.watch_paths = watch_paths or ['.']
        self.file_states = {}
        self.recent_changes = []
        self.max_recent_changes = 50
        self.ignore_patterns = {
            '.git', '__pycache__', '.pyc', '.tmp', '.log', 
            'node_modules', '.cache', '.vscode', '.idea',
            '.DS_Store', 'Thumbs.db'
        }
    
    def update(self):
        """Update file monitoring"""
        try:
            current_changes = []
            
            for watch_path in self.watch_paths:
                path = Path(watch_path)
                if path.exists():
                    changes = self.scan_directory(path)
                    current_changes.extend(changes)
            
            # Emit events for new changes
            for change in current_changes:
                self.emit_event('file_changed', change)
            
            # Update recent changes list
            self.recent_changes.extend(current_changes)
            self.recent_changes = self.recent_changes[-self.max_recent_changes:]
            
            if current_changes:
                self.emit_event('changes_summary', {
                    'new_changes': len(current_changes),
                    'total_recent': len(self.recent_changes)
                })
            
        except Exception as e:
            self.logger.error(f"Error updating file monitoring: {e}")
            self.emit_event('error', {'error': str(e)})
    
    def scan_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan directory for file changes"""
        changes = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if not self.should_ignore(d)]
                
                for file in files:
                    if self.should_ignore(file):
                        continue
                    
                    file_path = Path(root) / file
                    try:
                        stat = file_path.stat()
                        current_state = {
                            'path': str(file_path),
                            'size': stat.st_size,
                            'mtime': stat.st_mtime,
                            'ctime': stat.st_ctime
                        }
                        
                        previous_state = self.file_states.get(str(file_path))
                        
                        if previous_state is None:
                            # New file
                            change = {
                                'type': 'created',
                                'file': str(file_path),
                                'size': stat.st_size,
                                'timestamp': datetime.now().isoformat(),
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            }
                            changes.append(change)
                        elif (current_state['mtime'] != previous_state['mtime'] or 
                              current_state['size'] != previous_state['size']):
                            # Modified file
                            change = {
                                'type': 'modified',
                                'file': str(file_path),
                                'size': stat.st_size,
                                'size_change': stat.st_size - previous_state['size'],
                                'timestamp': datetime.now().isoformat(),
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            }
                            changes.append(change)
                        
                        self.file_states[str(file_path)] = current_state
                        
                    except (OSError, PermissionError) as e:
                        self.logger.debug(f"Cannot access file {file_path}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        return changes
    
    def should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored"""
        name_lower = name.lower()
        
        # Check exact matches
        if name in self.ignore_patterns or name_lower in self.ignore_patterns:
            return True
        
        # Check patterns
        for pattern in self.ignore_patterns:
            if pattern.startswith('.') and name_lower.endswith(pattern):
                return True
            if pattern in name_lower:
                return True
        
        return False
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get latest file monitoring data"""
        return {
            'recent_changes': self.recent_changes[-20:],  # Last 20 changes
            'total_files_tracked': len(self.file_states),
            'watch_paths': self.watch_paths
        }
    
    def get_recent_file_changes(self) -> List[Dict]:
        """Get recent file changes in the format expected by dashboard"""
        return self.recent_changes[-10:]  # Last 10 changes

class SystemMonitor(BaseMonitor):
    """Monitor system performance metrics"""
    
    def __init__(self, update_interval: float = 2.0):
        super().__init__('system', update_interval)
        self.process_history = {}
        self.max_history_length = 100
    
    def update(self):
        """Update system monitoring"""
        try:
            metrics = self.get_system_metrics_detailed()
            
            # Emit system metrics
            self.emit_event('metrics_update', metrics)
            
            # Check for alerts
            alerts = self.check_alerts(metrics)
            for alert in alerts:
                self.emit_event('alert', alert)
            
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {e}")
            self.emit_event('error', {'error': str(e)})
    
    def get_system_metrics_detailed(self) -> Dict[str, Any]:
        """Get detailed system metrics"""
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network information
            network = psutil.net_io_counters()
            
            # Process information
            processes = []
            claude_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Track Claude-related processes
                    if any(keyword in proc_name for keyword in ['claude', 'python', 'node']):
                        detailed_info = {
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'] or 0,
                            'memory_percent': proc_info['memory_percent'] or 0,
                            'create_time': proc_info['create_time'],
                            'created': datetime.fromtimestamp(proc_info['create_time']).isoformat() if proc_info['create_time'] else None
                        }
                        
                        if 'claude' in proc_name:
                            claude_processes.append(detailed_info)
                        else:
                            processes.append(detailed_info)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # System load (on Unix systems)
            load_avg = None
            try:
                if hasattr(os, 'getloadavg'):
                    load_avg = os.getloadavg()
            except Exception:
                pass
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.used / disk.total * 100 if disk.total > 0 else 0
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'total': len(list(psutil.process_iter())),
                    'claude_processes': claude_processes,
                    'python_processes': [p for p in processes if 'python' in p['name'].lower()]
                }
            }
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for system alerts based on metrics"""
        alerts = []
        
        try:
            # CPU alert
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning' if cpu_percent < 90 else 'critical',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'value': cpu_percent
                })
            
            # Memory alert
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning' if memory_percent < 95 else 'critical',
                    'message': f'High memory usage: {memory_percent:.1f}%',
                    'value': memory_percent
                })
            
            # Disk alert
            disk_percent = metrics.get('disk', {}).get('percent', 0)
            if disk_percent > 90:
                alerts.append({
                    'type': 'low_disk',
                    'severity': 'warning' if disk_percent < 95 else 'critical',
                    'message': f'Low disk space: {disk_percent:.1f}% used',
                    'value': disk_percent
                })
        
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
        
        return alerts
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get latest system metrics"""
        return self.get_system_metrics_detailed()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics in the format expected by dashboard"""
        return self.get_system_metrics_detailed()

class MonitorManager:
    """Main manager for all monitoring services"""
    
    def __init__(self):
        self.monitors = {}
        self.event_handlers = []
        self.logger = logging.getLogger('monitor_manager')
        self.is_running = False
        
        # Initialize monitors
        self.claude_monitor = ClaudeMonitor()
        self.git_monitor = GitMonitor()
        self.file_monitor = FileMonitor()
        self.system_monitor = SystemMonitor()
        
        self.monitors = {
            'claude': self.claude_monitor,
            'git': self.git_monitor,
            'file': self.file_monitor,
            'system': self.system_monitor
        }
        
        # Add event handlers to monitors
        for monitor in self.monitors.values():
            monitor.add_callback(self.handle_monitor_event)
    
    def add_event_handler(self, handler: Callable[[MonitorEvent], None]):
        """Add an event handler for all monitor events"""
        self.event_handlers.append(handler)
    
    def handle_monitor_event(self, event: MonitorEvent):
        """Handle events from monitors"""
        try:
            self.logger.debug(f"Event from {event.monitor_type}: {event.event_type}")
            
            # Call all event handlers
            for handler in self.event_handlers:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
        
        except Exception as e:
            self.logger.error(f"Error handling monitor event: {e}")
    
    def start_all(self):
        """Start all monitors"""
        if self.is_running:
            return
        
        self.is_running = True
        safe_print("🔍 Starting all monitoring services...")
        
        for name, monitor in self.monitors.items():
            try:
                monitor.start()
                safe_print(f"✅ Started {name} monitor")
            except Exception as e:
                safe_print(f"❌ Failed to start {name} monitor: {e}")
    
    def stop_all(self):
        """Stop all monitors"""
        if not self.is_running:
            return
        
        self.is_running = False
        safe_print("🛑 Stopping all monitoring services...")
        
        for name, monitor in self.monitors.items():
            try:
                monitor.stop()
                safe_print(f"✅ Stopped {name} monitor")
            except Exception as e:
                safe_print(f"❌ Error stopping {name} monitor: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all monitors"""
        status = {
            'manager_running': self.is_running,
            'monitors': {}
        }
        
        for name, monitor in self.monitors.items():
            status['monitors'][name] = {
                'running': monitor.is_running,
                'last_update': monitor.last_update.isoformat() if monitor.last_update else None,
                'update_interval': monitor.update_interval
            }
        
        return status
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get latest data from all monitors"""
        data = {}
        
        for name, monitor in self.monitors.items():
            try:
                data[name] = monitor.get_latest_data()
            except Exception as e:
                data[name] = {'error': str(e)}
        
        return data
    
    # Convenience methods for dashboard integration
    def get_claude_sessions(self) -> List[Dict]:
        """Get Claude sessions for dashboard"""
        try:
            return self.claude_monitor.get_claude_sessions()
        except Exception as e:
            self.logger.error(f"Error getting Claude sessions: {e}")
            return []
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get Git status for dashboard"""
        try:
            return self.git_monitor.get_git_status()
        except Exception as e:
            self.logger.error(f"Error getting Git status: {e}")
            return {'error': str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics for dashboard"""
        try:
            return self.system_monitor.get_system_metrics()
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    def get_recent_file_changes(self) -> List[Dict]:
        """Get recent file changes for dashboard"""
        try:
            return self.file_monitor.get_recent_file_changes()
        except Exception as e:
            self.logger.error(f"Error getting file changes: {e}")
            return []

def main():
    """Main function for testing monitors"""
    logging.basicConfig(level=logging.INFO)
    
    # Create and start monitor manager
    manager = MonitorManager()
    
    def print_event(event: MonitorEvent):
        safe_print(f"[{event.timestamp}] {event.monitor_type}.{event.event_type}: {event.data}")
    
    manager.add_event_handler(print_event)
    
    try:
        manager.start_all()
        
        safe_print("Monitors running... Press Ctrl+C to stop")
        
        # Keep running and print status every 30 seconds
        while True:
            time.sleep(30)
            status = manager.get_status()
            safe_print(f"Status: {json.dumps(status, indent=2)}")
    
    except KeyboardInterrupt:
        safe_print("\nStopping monitors...")
        manager.stop_all()
        safe_print("✅ All monitors stopped")

if __name__ == '__main__':
    main()