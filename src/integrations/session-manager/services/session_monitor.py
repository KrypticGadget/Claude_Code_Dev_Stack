"""
Session Monitoring Service
=========================

Real-time monitoring and analytics for Claude Code sessions.
Tracks performance metrics, resource usage, and session health.
"""

import asyncio
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import asdict

import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.session_models import Session, SessionMetrics, SessionStatus


class SessionMonitor:
    """
    Real-time session monitoring service that tracks performance,
    resource usage, and session health metrics.
    """
    
    def __init__(self, update_interval: float = 1.0):
        self.logger = logging.getLogger(__name__)
        self.update_interval = update_interval
        
        # Monitoring state
        self.monitored_sessions: Dict[str, Session] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Metrics collection
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_entries = 1000
        
        # Alert thresholds
        self.alert_thresholds = {
            'memory_usage_percent': 85.0,
            'cpu_usage_percent': 80.0,
            'disk_usage_percent': 90.0,
            'error_rate_percent': 10.0,
            'response_time_ms': 5000.0
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Performance baselines
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
    
    def add_session(self, session: Session):
        """Add a session to monitoring."""
        self.monitored_sessions[session.id] = session
        self.metrics_history[session.id] = []
        
        # Initialize performance baseline
        self.performance_baselines[session.id] = {
            'cpu_baseline': 0.0,
            'memory_baseline': 0.0,
            'response_time_baseline': 0.0,
            'baseline_established': False
        }
        
        self.logger.info(f"Added session {session.id} to monitoring")
        
        # Start monitoring if not already active
        if not self.monitoring_active:
            self.start_monitoring()
    
    def remove_session(self, session_id: str):
        """Remove a session from monitoring."""
        if session_id in self.monitored_sessions:
            del self.monitored_sessions[session_id]
            
            # Keep metrics history for analysis
            if session_id in self.metrics_history:
                # Archive the history before removing
                self._archive_session_metrics(session_id)
            
            if session_id in self.performance_baselines:
                del self.performance_baselines[session_id]
            
            self.logger.info(f"Removed session {session_id} from monitoring")
            
            # Stop monitoring if no sessions left
            if not self.monitored_sessions and self.monitoring_active:
                self.stop_monitoring()
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Session monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        self.logger.info("Session monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Collect metrics for all monitored sessions
                for session_id, session in self.monitored_sessions.items():
                    try:
                        self._collect_session_metrics(session)
                    except Exception as e:
                        self.logger.error(f"Failed to collect metrics for session {session_id}: {e}")
                
                # Check for alerts
                self._check_alerts()
                
                # Sleep for remaining interval time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(1.0)  # Brief pause before retrying
    
    def _collect_session_metrics(self, session: Session):
        """Collect metrics for a single session."""
        try:
            # System metrics
            system_metrics = self._get_system_metrics()
            
            # Session-specific metrics
            session_metrics = self._get_session_specific_metrics(session)
            
            # Performance metrics
            performance_metrics = self._get_performance_metrics(session)
            
            # Combine all metrics
            combined_metrics = {
                'timestamp': time.time(),
                'session_id': session.id,
                'system': system_metrics,
                'session': session_metrics,
                'performance': performance_metrics
            }
            
            # Update session metrics object
            self._update_session_metrics(session, combined_metrics)
            
            # Store in history
            self._store_metrics_history(session.id, combined_metrics)
            
            # Update performance baselines
            self._update_performance_baseline(session.id, combined_metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics for session {session.id}: {e}")
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'percent': memory_percent,
                    'available_gb': memory_available_gb,
                    'total_gb': memory_total_gb,
                    'used_gb': memory_total_gb - memory_available_gb
                },
                'disk': {
                    'percent': disk_percent,
                    'free_gb': disk_free_gb,
                    'total_gb': disk_total_gb,
                    'used_gb': disk_total_gb - disk_free_gb
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': process_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def _get_session_specific_metrics(self, session: Session) -> Dict[str, Any]:
        """Get session-specific metrics."""
        try:
            working_dir = Path(session.configuration.working_directory)
            
            # Directory metrics
            dir_metrics = self._get_directory_metrics(working_dir)
            
            # Agent metrics
            agent_metrics = self._get_agent_metrics(session)
            
            # Session duration
            duration = time.time() - session.created_at
            
            # Error tracking
            error_count = session.metrics.errors_encountered
            
            return {
                'duration_seconds': duration,
                'status': session.status.value,
                'working_directory': str(working_dir),
                'directory': dir_metrics,
                'agents': agent_metrics,
                'errors': {
                    'total': error_count,
                    'rate_per_hour': (error_count / duration * 3600) if duration > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session metrics for {session.id}: {e}")
            return {}
    
    def _get_directory_metrics(self, directory: Path) -> Dict[str, Any]:
        """Get metrics for the session working directory."""
        try:
            if not directory.exists():
                return {'exists': False}
            
            # Count files and directories
            file_count = 0
            dir_count = 0
            total_size = 0
            
            for item in directory.rglob('*'):
                if item.is_file():
                    file_count += 1
                    try:
                        total_size += item.stat().st_size
                    except:
                        pass
                elif item.is_dir():
                    dir_count += 1
            
            # Recent activity (files modified in last hour)
            recent_cutoff = time.time() - 3600
            recent_files = 0
            
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        if item.stat().st_mtime > recent_cutoff:
                            recent_files += 1
                    except:
                        pass
            
            return {
                'exists': True,
                'file_count': file_count,
                'directory_count': dir_count,
                'total_size_mb': total_size / (1024**2),
                'recent_files_modified': recent_files,
                'is_git_repo': (directory / '.git').exists()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get directory metrics for {directory}: {e}")
            return {'exists': False, 'error': str(e)}
    
    def _get_agent_metrics(self, session: Session) -> Dict[str, Any]:
        """Get metrics for session agents."""
        try:
            agent_count = len(session.configuration.agents)
            active_agents = len(session.context.active_agents)
            
            # Agent activation statistics
            activations = session.metrics.agent_activations
            total_activations = sum(activations.values())
            
            # Most active agent
            most_active_agent = None
            max_activations = 0
            
            for agent_name, count in activations.items():
                if count > max_activations:
                    max_activations = count
                    most_active_agent = agent_name
            
            return {
                'total_configured': agent_count,
                'currently_active': active_agents,
                'total_activations': total_activations,
                'most_active_agent': most_active_agent,
                'max_activations': max_activations,
                'activation_distribution': activations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get agent metrics for session {session.id}: {e}")
            return {}
    
    def _get_performance_metrics(self, session: Session) -> Dict[str, Any]:
        """Get performance-related metrics."""
        try:
            # Calculate average response time (simplified)
            commands_executed = session.metrics.commands_executed
            duration = time.time() - session.created_at
            
            avg_command_time = (duration / commands_executed) if commands_executed > 0 else 0
            
            # Memory usage estimate
            memory_usage = session.metrics.memory_usage_mb
            
            # CPU usage estimate (would need more sophisticated tracking)
            cpu_usage = session.metrics.cpu_usage_percent
            
            # Files modified rate
            files_modified = session.metrics.files_modified
            files_per_hour = (files_modified / duration * 3600) if duration > 0 else 0
            
            return {
                'avg_command_time_ms': avg_command_time * 1000,
                'memory_usage_mb': memory_usage,
                'cpu_usage_percent': cpu_usage,
                'files_modified_per_hour': files_per_hour,
                'commands_per_hour': (commands_executed / duration * 3600) if duration > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics for session {session.id}: {e}")
            return {}
    
    def _update_session_metrics(self, session: Session, metrics: Dict[str, Any]):
        """Update the session's metrics object."""
        try:
            # Update system resource usage
            if 'system' in metrics:
                system = metrics['system']
                session.metrics.memory_usage_mb = system.get('memory', {}).get('used_gb', 0) * 1024
                session.metrics.cpu_usage_percent = system.get('cpu', {}).get('percent', 0)
            
            # Update performance metrics
            if 'performance' in metrics:
                perf = metrics['performance']
                session.metrics.performance_metrics.update({
                    'avg_response_time': perf.get('avg_command_time_ms', 0),
                    'memory_usage': perf.get('memory_usage_mb', 0),
                    'cpu_usage': perf.get('cpu_usage_percent', 0)
                })
            
            # Update session metrics with file counts
            if 'session' in metrics and 'directory' in metrics['session']:
                dir_metrics = metrics['session']['directory']
                # Could update files_modified based on recent_files_modified
            
        except Exception as e:
            self.logger.error(f"Failed to update session metrics for {session.id}: {e}")
    
    def _store_metrics_history(self, session_id: str, metrics: Dict[str, Any]):
        """Store metrics in history for analysis."""
        if session_id not in self.metrics_history:
            self.metrics_history[session_id] = []
        
        history = self.metrics_history[session_id]
        history.append(metrics)
        
        # Limit history size
        if len(history) > self.max_history_entries:
            history.pop(0)
    
    def _update_performance_baseline(self, session_id: str, metrics: Dict[str, Any]):
        """Update performance baseline for anomaly detection."""
        if session_id not in self.performance_baselines:
            return
        
        baseline = self.performance_baselines[session_id]
        
        # Extract current values
        system = metrics.get('system', {})
        performance = metrics.get('performance', {})
        
        current_cpu = system.get('cpu', {}).get('percent', 0)
        current_memory = system.get('memory', {}).get('used_gb', 0)
        current_response_time = performance.get('avg_command_time_ms', 0)
        
        # Update baseline with exponential moving average
        alpha = 0.1  # Smoothing factor
        
        if baseline['baseline_established']:
            baseline['cpu_baseline'] = (1 - alpha) * baseline['cpu_baseline'] + alpha * current_cpu
            baseline['memory_baseline'] = (1 - alpha) * baseline['memory_baseline'] + alpha * current_memory
            baseline['response_time_baseline'] = (1 - alpha) * baseline['response_time_baseline'] + alpha * current_response_time
        else:
            # First measurement
            baseline['cpu_baseline'] = current_cpu
            baseline['memory_baseline'] = current_memory
            baseline['response_time_baseline'] = current_response_time
            baseline['baseline_established'] = True
    
    def _check_alerts(self):
        """Check for alert conditions across all monitored sessions."""
        for session_id, session in self.monitored_sessions.items():
            try:
                self._check_session_alerts(session)
            except Exception as e:
                self.logger.error(f"Failed to check alerts for session {session_id}: {e}")
    
    def _check_session_alerts(self, session: Session):
        """Check alerts for a specific session."""
        session_id = session.id
        
        if session_id not in self.metrics_history:
            return
        
        history = self.metrics_history[session_id]
        if not history:
            return
        
        latest_metrics = history[-1]
        
        # Check system resource alerts
        system = latest_metrics.get('system', {})
        
        # Memory alert
        memory_percent = system.get('memory', {}).get('percent', 0)
        if memory_percent > self.alert_thresholds['memory_usage_percent']:
            self._trigger_alert(session_id, 'high_memory_usage', {
                'current': memory_percent,
                'threshold': self.alert_thresholds['memory_usage_percent']
            })
        
        # CPU alert
        cpu_percent = system.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.alert_thresholds['cpu_usage_percent']:
            self._trigger_alert(session_id, 'high_cpu_usage', {
                'current': cpu_percent,
                'threshold': self.alert_thresholds['cpu_usage_percent']
            })
        
        # Disk alert
        disk_percent = system.get('disk', {}).get('percent', 0)
        if disk_percent > self.alert_thresholds['disk_usage_percent']:
            self._trigger_alert(session_id, 'high_disk_usage', {
                'current': disk_percent,
                'threshold': self.alert_thresholds['disk_usage_percent']
            })
        
        # Performance alerts
        performance = latest_metrics.get('performance', {})
        response_time = performance.get('avg_command_time_ms', 0)
        
        if response_time > self.alert_thresholds['response_time_ms']:
            self._trigger_alert(session_id, 'slow_response_time', {
                'current': response_time,
                'threshold': self.alert_thresholds['response_time_ms']
            })
        
        # Error rate alert
        session_metrics = latest_metrics.get('session', {})
        error_rate = session_metrics.get('errors', {}).get('rate_per_hour', 0)
        
        if error_rate > self.alert_thresholds['error_rate_percent']:
            self._trigger_alert(session_id, 'high_error_rate', {
                'current': error_rate,
                'threshold': self.alert_thresholds['error_rate_percent']
            })
    
    def _trigger_alert(self, session_id: str, alert_type: str, data: Dict[str, Any]):
        """Trigger an alert for a session."""
        alert = {
            'timestamp': time.time(),
            'session_id': session_id,
            'alert_type': alert_type,
            'data': data,
            'severity': self._get_alert_severity(alert_type, data)
        }
        
        self.logger.warning(f"Alert triggered for session {session_id}: {alert_type} - {data}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def _get_alert_severity(self, alert_type: str, data: Dict[str, Any]) -> str:
        """Determine alert severity based on type and data."""
        current = data.get('current', 0)
        threshold = data.get('threshold', 0)
        
        if threshold == 0:
            return 'medium'
        
        ratio = current / threshold
        
        if ratio > 1.5:
            return 'critical'
        elif ratio > 1.2:
            return 'high'
        else:
            return 'medium'
    
    def add_alert_callback(self, callback: Callable):
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable):
        """Remove an alert callback function."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def get_session_metrics(self, session_id: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for a session."""
        if session_id not in self.metrics_history:
            return []
        
        history = self.metrics_history[session_id]
        
        # Filter by time if specified
        if hours > 0:
            cutoff_time = time.time() - (hours * 3600)
            history = [m for m in history if m.get('timestamp', 0) > cutoff_time]
        
        return history
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session metrics."""
        if session_id not in self.monitored_sessions:
            return {}
        
        session = self.monitored_sessions[session_id]
        history = self.metrics_history.get(session_id, [])
        
        if not history:
            return {'session_id': session_id, 'status': 'no_data'}
        
        # Calculate summary statistics
        latest = history[-1]
        
        # Average metrics over last hour
        hour_ago = time.time() - 3600
        recent_metrics = [m for m in history if m.get('timestamp', 0) > hour_ago]
        
        if recent_metrics:
            avg_cpu = sum(m.get('system', {}).get('cpu', {}).get('percent', 0) for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.get('system', {}).get('memory', {}).get('percent', 0) for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = 0
            avg_memory = 0
        
        return {
            'session_id': session_id,
            'status': session.status.value,
            'duration_hours': (time.time() - session.created_at) / 3600,
            'latest_metrics': latest,
            'averages_last_hour': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory
            },
            'total_data_points': len(history),
            'monitoring_since': history[0].get('timestamp') if history else None
        }
    
    def _archive_session_metrics(self, session_id: str):
        """Archive metrics history for a removed session."""
        if session_id not in self.metrics_history:
            return
        
        try:
            archive_dir = Path.home() / ".claude" / "session_metrics"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_file = archive_dir / f"session_{session_id}_{int(time.time())}.json"
            
            with open(archive_file, 'w') as f:
                json.dump({
                    'session_id': session_id,
                    'archived_at': time.time(),
                    'metrics_history': self.metrics_history[session_id]
                }, f, indent=2)
            
            # Remove from memory
            del self.metrics_history[session_id]
            
            self.logger.info(f"Archived metrics for session {session_id} to {archive_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to archive metrics for session {session_id}: {e}")
    
    def cleanup(self):
        """Cleanup monitoring resources."""
        self.stop_monitoring()
        
        # Archive all remaining metrics
        for session_id in list(self.metrics_history.keys()):
            self._archive_session_metrics(session_id)
        
        self.monitored_sessions.clear()
        self.performance_baselines.clear()
        self.alert_callbacks.clear()