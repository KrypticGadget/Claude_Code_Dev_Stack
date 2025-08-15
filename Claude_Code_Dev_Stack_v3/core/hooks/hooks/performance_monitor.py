#!/usr/bin/env python3
"""
Performance Monitor Hook - V3.0+ System Metrics
Tracks agent execution times, token usage, and performance metrics
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import psutil
import threading

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics_file = Path.home() / '.claude' / 'state' / 'performance_metrics.json'
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing metrics
        self.metrics = self.load_metrics()
        
        # Settings
        self.settings = self.load_settings()
        self.thresholds = self.settings.get('v3ExtendedFeatures', {}).get('monitoring', {}).get('performanceThresholds', {})
        
        # Default thresholds
        self.agent_time_threshold = self.thresholds.get('agentExecutionTime', 30)  # seconds
        self.token_threshold = self.thresholds.get('tokenUsagePerOperation', 50000)
        self.memory_threshold = self.thresholds.get('memoryUsagePercent', 80)
        
        # Current tracking
        self.active_operations = {}
        self.start_time = time.time()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.monitor_thread.start()
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = Path.home() / '.claude' / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def load_metrics(self) -> Dict:
        """Load existing metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize metrics structure
        return {
            'agent_metrics': {},
            'operation_metrics': {},
            'resource_metrics': [],
            'performance_issues': [],
            'summary': {
                'total_operations': 0,
                'average_execution_time': 0,
                'total_tokens_used': 0,
                'peak_memory_usage': 0,
                'issues_detected': 0
            }
        }
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def start_operation(self, operation_id: str, operation_type: str, metadata: Dict = None):
        """Start tracking an operation"""
        self.active_operations[operation_id] = {
            'type': operation_type,
            'start_time': time.time(),
            'metadata': metadata or {},
            'memory_start': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    
    def end_operation(self, operation_id: str, tokens_used: int = 0, success: bool = True):
        """End tracking an operation"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations.pop(operation_id)
        duration = time.time() - operation['start_time']
        memory_end = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_end - operation['memory_start']
        
        # Record metrics
        op_type = operation['type']
        if op_type not in self.metrics['operation_metrics']:
            self.metrics['operation_metrics'][op_type] = {
                'count': 0,
                'total_time': 0,
                'total_tokens': 0,
                'average_time': 0,
                'average_tokens': 0,
                'max_time': 0,
                'max_tokens': 0
            }
        
        metrics = self.metrics['operation_metrics'][op_type]
        metrics['count'] += 1
        metrics['total_time'] += duration
        metrics['total_tokens'] += tokens_used
        metrics['average_time'] = metrics['total_time'] / metrics['count']
        metrics['average_tokens'] = metrics['total_tokens'] / metrics['count']
        metrics['max_time'] = max(metrics['max_time'], duration)
        metrics['max_tokens'] = max(metrics['max_tokens'], tokens_used)
        
        # Update summary
        self.metrics['summary']['total_operations'] += 1
        self.metrics['summary']['total_tokens_used'] += tokens_used
        
        # Check for performance issues
        issues = []
        if duration > self.agent_time_threshold:
            issues.append(f"Slow execution: {duration:.1f}s (threshold: {self.agent_time_threshold}s)")
            self.trigger_notification('performance_warning', op_type, duration)
        
        if tokens_used > self.token_threshold:
            issues.append(f"High token usage: {tokens_used:,} (threshold: {self.token_threshold:,})")
        
        if memory_used > 100:  # MB
            issues.append(f"High memory usage: {memory_used:.1f}MB")
        
        if issues and not success:
            issues.append("Operation failed")
        
        if issues:
            self.metrics['performance_issues'].append({
                'timestamp': datetime.now().isoformat(),
                'operation': op_type,
                'operation_id': operation_id,
                'duration': duration,
                'tokens': tokens_used,
                'memory': memory_used,
                'issues': issues
            })
            self.metrics['summary']['issues_detected'] += 1
        
        # Keep only last 100 issues
        if len(self.metrics['performance_issues']) > 100:
            self.metrics['performance_issues'] = self.metrics['performance_issues'][-100:]
        
        self.save_metrics()
    
    def track_agent(self, agent_name: str, start: bool = True, tokens: int = 0):
        """Track agent execution"""
        if agent_name not in self.metrics['agent_metrics']:
            self.metrics['agent_metrics'][agent_name] = {
                'executions': 0,
                'total_time': 0,
                'total_tokens': 0,
                'average_time': 0,
                'average_tokens': 0,
                'last_execution': None
            }
        
        if start:
            self.start_operation(f"agent_{agent_name}", agent_name)
        else:
            self.end_operation(f"agent_{agent_name}", tokens)
            
            # Update agent-specific metrics
            metrics = self.metrics['agent_metrics'][agent_name]
            metrics['executions'] += 1
            metrics['total_tokens'] += tokens
            metrics['average_tokens'] = metrics['total_tokens'] / metrics['executions']
            metrics['last_execution'] = datetime.now().isoformat()
    
    def monitor_resources(self):
        """Background thread to monitor system resources"""
        while self.monitoring:
            try:
                # Get current metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Record snapshot
                snapshot = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': memory.used / 1024 / 1024,
                    'disk_percent': disk.percent
                }
                
                self.metrics['resource_metrics'].append(snapshot)
                
                # Keep only last 100 snapshots
                if len(self.metrics['resource_metrics']) > 100:
                    self.metrics['resource_metrics'] = self.metrics['resource_metrics'][-100:]
                
                # Update peak memory
                self.metrics['summary']['peak_memory_usage'] = max(
                    self.metrics['summary']['peak_memory_usage'],
                    memory.percent
                )
                
                # Check thresholds
                if memory.percent > self.memory_threshold:
                    self.trigger_notification('resource_warning', 'memory', memory.percent)
                
                if cpu_percent > 90:
                    self.trigger_notification('resource_warning', 'cpu', cpu_percent)
                
                # Save periodically
                if time.time() % 60 < 5:  # Every minute
                    self.save_metrics()
                
            except Exception as e:
                print(f"Resource monitoring error: {e}")
            
            time.sleep(5)  # Check every 5 seconds
    
    def trigger_notification(self, event_type: str, resource: str, value: float):
        """Trigger notification for performance issue"""
        try:
            # Play audio
            audio_file = f"{event_type}.wav"
            audio_path = Path.home() / '.claude' / 'audio' / audio_file
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            # Send remote notification
            from notification_sender import get_sender
            sender = get_sender()
            
            if event_type == 'performance_warning':
                sender.send_custom(
                    "Performance Warning",
                    f"{resource} execution took {value:.1f} seconds",
                    1
                )
            elif event_type == 'resource_warning':
                sender.send_custom(
                    "Resource Warning",
                    f"{resource.upper()} usage at {value:.1f}%",
                    1
                )
        except:
            pass
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        # Calculate current uptime
        uptime = time.time() - self.start_time
        hours = uptime / 3600
        
        # Calculate average execution time
        total_ops = self.metrics['summary']['total_operations']
        if total_ops > 0:
            total_time = sum(m['total_time'] for m in self.metrics['operation_metrics'].values())
            avg_time = total_time / total_ops
        else:
            avg_time = 0
        
        return {
            'uptime_hours': round(hours, 2),
            'total_operations': total_ops,
            'average_execution_time': round(avg_time, 2),
            'total_tokens_used': self.metrics['summary']['total_tokens_used'],
            'peak_memory_percent': round(self.metrics['summary']['peak_memory_usage'], 1),
            'issues_detected': self.metrics['summary']['issues_detected'],
            'top_agents': self.get_top_agents(),
            'recent_issues': self.metrics['performance_issues'][-5:]
        }
    
    def get_top_agents(self, limit: int = 5) -> List[Dict]:
        """Get top agents by execution count"""
        agents = []
        for name, metrics in self.metrics['agent_metrics'].items():
            agents.append({
                'name': name,
                'executions': metrics['executions'],
                'avg_time': round(metrics['average_time'], 2) if 'average_time' in metrics else 0,
                'avg_tokens': round(metrics['average_tokens']) if 'average_tokens' in metrics else 0
            })
        
        # Sort by executions
        agents.sort(key=lambda x: x['executions'], reverse=True)
        return agents[:limit]
    
    def cleanup(self):
        """Cleanup and save final metrics"""
        self.monitoring = False
        self.save_metrics()

# Global instance
_monitor = None

def get_monitor():
    """Get or create monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor

def main():
    """Hook entry point"""
    import sys
    
    monitor = get_monitor()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'start' and len(sys.argv) > 3:
            operation_id = sys.argv[2]
            operation_type = sys.argv[3]
            monitor.start_operation(operation_id, operation_type)
        
        elif action == 'end' and len(sys.argv) > 2:
            operation_id = sys.argv[2]
            tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            success = sys.argv[4] != 'false' if len(sys.argv) > 4 else True
            monitor.end_operation(operation_id, tokens, success)
        
        elif action == 'agent-start' and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            monitor.track_agent(agent_name, start=True)
        
        elif action == 'agent-end' and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            monitor.track_agent(agent_name, start=False, tokens=tokens)
        
        elif action == 'summary':
            summary = monitor.get_summary()
            print(json.dumps(summary, indent=2))
        
        elif action == 'cleanup':
            monitor.cleanup()

if __name__ == '__main__':
    main()