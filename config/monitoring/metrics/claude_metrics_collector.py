#!/usr/bin/env python3
"""
Claude Code Metrics Collector - V3.6.9
Prometheus metrics exporter for Claude Code agents and system performance
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class MetricsCollector:
    """Collect and export Claude Code metrics to Prometheus"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.metrics_dir = self.claude_dir / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics storage
        self.metrics = {
            'agent_metrics': {},
            'hook_metrics': {},
            'session_metrics': {},
            'resource_metrics': {},
            'performance_metrics': {},
            'integration_metrics': {}
        }
        
        # Prometheus metrics registry
        self.prometheus_metrics = {}
        self.initialize_prometheus_metrics()
        
        # Start collection thread
        self.collecting = True
        self.collection_thread = threading.Thread(target=self.collect_metrics_loop, daemon=True)
        self.collection_thread.start()
    
    def initialize_prometheus_metrics(self):
        """Initialize Prometheus metric definitions"""
        self.prometheus_metrics = {
            # Agent metrics
            'claude_agent_executions_total': {
                'type': 'counter',
                'help': 'Total number of agent executions',
                'labels': ['agent_name', 'status']
            },
            'claude_agent_execution_time_seconds': {
                'type': 'histogram',
                'help': 'Agent execution time in seconds',
                'labels': ['agent_name'],
                'buckets': [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            },
            'claude_agent_active': {
                'type': 'gauge',
                'help': 'Currently active agents',
                'labels': ['agent_name']
            },
            'claude_tokens_used_total': {
                'type': 'counter',
                'help': 'Total tokens used by Claude'
            },
            'claude_tokens_daily_total': {
                'type': 'gauge',
                'help': 'Daily token usage total'
            },
            
            # Hook metrics
            'claude_hook_executions_total': {
                'type': 'counter',
                'help': 'Total hook executions',
                'labels': ['hook_name', 'status']
            },
            'claude_hook_execution_time_seconds': {
                'type': 'histogram',
                'help': 'Hook execution time in seconds',
                'labels': ['hook_name'],
                'buckets': [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
            },
            'claude_hook_active': {
                'type': 'gauge',
                'help': 'Currently active hooks',
                'labels': ['hook_name']
            },
            'claude_hook_memory_usage_bytes': {
                'type': 'gauge',
                'help': 'Memory usage by hook',
                'labels': ['hook_name']
            },
            
            # Session metrics
            'claude_session_loads_total': {
                'type': 'counter',
                'help': 'Total session loads',
                'labels': ['status']
            },
            'claude_session_saves_total': {
                'type': 'counter',
                'help': 'Total session saves',
                'labels': ['status']
            },
            'claude_session_load_duration_seconds': {
                'type': 'histogram',
                'help': 'Session load duration in seconds',
                'buckets': [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            'claude_session_size_bytes': {
                'type': 'gauge',
                'help': 'Session size in bytes',
                'labels': ['session_id']
            },
            'claude_active_sessions_total': {
                'type': 'gauge',
                'help': 'Currently active sessions'
            },
            'claude_session_operations_total': {
                'type': 'counter',
                'help': 'Total session operations',
                'labels': ['operation_type']
            },
            
            # Resource metrics
            'claude_process_memory_bytes': {
                'type': 'gauge',
                'help': 'Memory usage by process',
                'labels': ['process']
            },
            'claude_storage_used_bytes': {
                'type': 'gauge',
                'help': 'Storage used by Claude Code'
            },
            'claude_storage_by_type_bytes': {
                'type': 'gauge',
                'help': 'Storage usage by type',
                'labels': ['storage_type']
            },
            'claude_cleanup_operations_total': {
                'type': 'counter',
                'help': 'Total cleanup operations',
                'labels': ['operation_type']
            },
            'claude_component_memory_bytes': {
                'type': 'gauge',
                'help': 'Memory usage by component',
                'labels': ['component']
            },
            'claude_performance_issues_total': {
                'type': 'counter',
                'help': 'Total performance issues detected',
                'labels': ['issue_type']
            },
            
            # Integration metrics
            'mcp_connection_status': {
                'type': 'gauge',
                'help': 'MCP connection status',
                'labels': ['service']
            },
            'mcp_connection_failures_total': {
                'type': 'counter',
                'help': 'Total MCP connection failures',
                'labels': ['service']
            },
            'browser_integration_requests_total': {
                'type': 'counter',
                'help': 'Total browser integration requests',
                'labels': ['status']
            }
        }
    
    def collect_metrics_loop(self):
        """Main metrics collection loop"""
        while self.collecting:
            try:
                # Collect from various sources
                self.collect_agent_metrics()
                self.collect_hook_metrics()
                self.collect_session_metrics()
                self.collect_resource_metrics()
                self.collect_performance_metrics()
                self.collect_integration_metrics()
                
                # Save metrics snapshot
                self.save_metrics_snapshot()
                
            except Exception as e:
                print(f"Metrics collection error: {e}")
            
            time.sleep(15)  # Collect every 15 seconds
    
    def collect_agent_metrics(self):
        """Collect agent execution metrics"""
        try:
            # Load from performance monitor
            perf_file = self.claude_dir / 'state' / 'performance_metrics.json'
            if perf_file.exists():
                with open(perf_file) as f:
                    perf_data = json.load(f)
                
                # Agent metrics
                for agent_name, metrics in perf_data.get('agent_metrics', {}).items():
                    self.update_metric('claude_agent_executions_total', 
                                     metrics.get('executions', 0),
                                     {'agent_name': agent_name, 'status': 'success'})
                    
                    if 'average_time' in metrics:
                        self.record_histogram('claude_agent_execution_time_seconds',
                                            metrics['average_time'],
                                            {'agent_name': agent_name})
                
                # Token usage
                summary = perf_data.get('summary', {})
                total_tokens = summary.get('total_tokens_used', 0)
                self.update_metric('claude_tokens_used_total', total_tokens)
                
                # Daily token tracking
                today = datetime.now().date()
                daily_file = self.metrics_dir / f'daily_tokens_{today}.json'
                if daily_file.exists():
                    with open(daily_file) as f:
                        daily_data = json.load(f)
                    daily_total = daily_data.get('total', 0)
                else:
                    daily_total = 0
                
                self.update_metric('claude_tokens_daily_total', daily_total)
                
        except Exception as e:
            print(f"Agent metrics collection error: {e}")
    
    def collect_hook_metrics(self):
        """Collect hook execution metrics"""
        try:
            # Load hook execution data
            hook_file = self.claude_dir / 'state' / 'hook_metrics.json'
            if hook_file.exists():
                with open(hook_file) as f:
                    hook_data = json.load(f)
                
                for hook_name, metrics in hook_data.get('hooks', {}).items():
                    executions = metrics.get('executions', 0)
                    failures = metrics.get('failures', 0)
                    
                    self.update_metric('claude_hook_executions_total',
                                     executions,
                                     {'hook_name': hook_name, 'status': 'success'})
                    
                    self.update_metric('claude_hook_executions_total',
                                     failures,
                                     {'hook_name': hook_name, 'status': 'failure'})
                    
                    if 'average_time' in metrics:
                        self.record_histogram('claude_hook_execution_time_seconds',
                                            metrics['average_time'],
                                            {'hook_name': hook_name})
                    
                    # Memory usage
                    memory_usage = metrics.get('memory_usage', 0)
                    self.update_metric('claude_hook_memory_usage_bytes',
                                     memory_usage,
                                     {'hook_name': hook_name})
                    
                    # Active status
                    is_active = metrics.get('active', False)
                    self.update_metric('claude_hook_active',
                                     1 if is_active else 0,
                                     {'hook_name': hook_name})
                
        except Exception as e:
            print(f"Hook metrics collection error: {e}")
    
    def collect_session_metrics(self):
        """Collect session management metrics"""
        try:
            # Load session data
            session_file = self.claude_dir / 'state' / 'session_metrics.json'
            if session_file.exists():
                with open(session_file) as f:
                    session_data = json.load(f)
                
                # Session operations
                operations = session_data.get('operations', {})
                for op_type, count in operations.items():
                    self.update_metric('claude_session_operations_total',
                                     count,
                                     {'operation_type': op_type})
                
                # Session sizes
                sessions = session_data.get('sessions', {})
                active_sessions = 0
                for session_id, info in sessions.items():
                    size = info.get('size', 0)
                    self.update_metric('claude_session_size_bytes',
                                     size,
                                     {'session_id': session_id})
                    
                    if info.get('active', False):
                        active_sessions += 1
                
                self.update_metric('claude_active_sessions_total', active_sessions)
                
                # Load/save metrics
                loads = session_data.get('loads', {})
                saves = session_data.get('saves', {})
                
                for status, count in loads.items():
                    self.update_metric('claude_session_loads_total',
                                     count,
                                     {'status': status})
                
                for status, count in saves.items():
                    self.update_metric('claude_session_saves_total',
                                     count,
                                     {'status': status})
                
        except Exception as e:
            print(f"Session metrics collection error: {e}")
    
    def collect_resource_metrics(self):
        """Collect resource usage metrics"""
        try:
            # System resources
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Process-specific metrics
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'claude' in proc.info['name'].lower() or 'python' in proc.info['name'].lower():
                        memory_bytes = proc.info['memory_info'].rss
                        self.update_metric('claude_process_memory_bytes',
                                         memory_bytes,
                                         {'process': proc.info['name']})
                except:
                    continue
            
            # Storage usage
            claude_dir_size = self.get_directory_size(self.claude_dir)
            self.update_metric('claude_storage_used_bytes', claude_dir_size)
            
            # Storage by type
            storage_types = {
                'logs': self.get_directory_size(self.claude_dir / 'logs'),
                'state': self.get_directory_size(self.claude_dir / 'state'),
                'audio': self.get_directory_size(self.claude_dir / 'audio'),
                'metrics': self.get_directory_size(self.metrics_dir)
            }
            
            for storage_type, size in storage_types.items():
                self.update_metric('claude_storage_by_type_bytes',
                                 size,
                                 {'storage_type': storage_type})
            
            # Component memory usage
            components = {
                'orchestrator': self.estimate_component_memory('orchestrator'),
                'hooks': self.estimate_component_memory('hooks'),
                'integrations': self.estimate_component_memory('integrations')
            }
            
            for component, memory in components.items():
                self.update_metric('claude_component_memory_bytes',
                                 memory,
                                 {'component': component})
                
        except Exception as e:
            print(f"Resource metrics collection error: {e}")
    
    def collect_performance_metrics(self):
        """Collect performance issue metrics"""
        try:
            perf_file = self.claude_dir / 'state' / 'performance_metrics.json'
            if perf_file.exists():
                with open(perf_file) as f:
                    perf_data = json.load(f)
                
                issues = perf_data.get('performance_issues', [])
                issue_counts = {}
                
                for issue in issues:
                    for issue_text in issue.get('issues', []):
                        if 'slow execution' in issue_text.lower():
                            issue_type = 'slow_execution'
                        elif 'high token usage' in issue_text.lower():
                            issue_type = 'high_token_usage'
                        elif 'high memory usage' in issue_text.lower():
                            issue_type = 'high_memory_usage'
                        elif 'operation failed' in issue_text.lower():
                            issue_type = 'operation_failure'
                        else:
                            issue_type = 'other'
                        
                        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
                
                for issue_type, count in issue_counts.items():
                    self.update_metric('claude_performance_issues_total',
                                     count,
                                     {'issue_type': issue_type})
                
        except Exception as e:
            print(f"Performance metrics collection error: {e}")
    
    def collect_integration_metrics(self):
        """Collect integration service metrics"""
        try:
            # MCP Manager metrics
            mcp_file = self.claude_dir / 'state' / 'mcp_metrics.json'
            if mcp_file.exists():
                with open(mcp_file) as f:
                    mcp_data = json.load(f)
                
                for service, status in mcp_data.get('connections', {}).items():
                    self.update_metric('mcp_connection_status',
                                     1 if status == 'connected' else 0,
                                     {'service': service})
                
                for service, failures in mcp_data.get('failures', {}).items():
                    self.update_metric('mcp_connection_failures_total',
                                     failures,
                                     {'service': service})
            
            # Browser integration metrics
            browser_file = self.claude_dir / 'state' / 'browser_metrics.json'
            if browser_file.exists():
                with open(browser_file) as f:
                    browser_data = json.load(f)
                
                for status, count in browser_data.get('requests', {}).items():
                    self.update_metric('browser_integration_requests_total',
                                     count,
                                     {'status': status})
                
        except Exception as e:
            print(f"Integration metrics collection error: {e}")
    
    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory"""
        total = 0
        try:
            if path.exists():
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
        except:
            pass
        return total
    
    def estimate_component_memory(self, component: str) -> int:
        """Estimate memory usage for component"""
        # This is a simplified estimation
        # In practice, you'd use more sophisticated memory profiling
        estimates = {
            'orchestrator': 50 * 1024 * 1024,  # 50MB
            'hooks': 30 * 1024 * 1024,         # 30MB
            'integrations': 20 * 1024 * 1024   # 20MB
        }
        return estimates.get(component, 0)
    
    def update_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Update a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = {}
        
        label_key = json.dumps(labels or {}, sort_keys=True)
        self.metrics[metric_name][label_key] = {
            'value': value,
            'timestamp': time.time(),
            'labels': labels or {}
        }
    
    def record_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        # For simplicity, we'll store the raw value
        # In production, you'd implement proper histogram buckets
        self.update_metric(metric_name, value, labels)
    
    def save_metrics_snapshot(self):
        """Save current metrics snapshot"""
        snapshot_file = self.metrics_dir / f'snapshot_{int(time.time())}.json'
        try:
            with open(snapshot_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            
            # Keep only last 100 snapshots
            snapshots = sorted(self.metrics_dir.glob('snapshot_*.json'))
            if len(snapshots) > 100:
                for snapshot in snapshots[:-100]:
                    snapshot.unlink()
                    
        except Exception as e:
            print(f"Error saving metrics snapshot: {e}")
    
    def get_prometheus_output(self) -> str:
        """Generate Prometheus metrics format output"""
        output = []
        
        for metric_name, metric_def in self.prometheus_metrics.items():
            if metric_name in self.metrics:
                # Add metric help and type
                output.append(f"# HELP {metric_name} {metric_def['help']}")
                output.append(f"# TYPE {metric_name} {metric_def['type']}")
                
                # Add metric values
                for label_key, data in self.metrics[metric_name].items():
                    labels = data['labels']
                    value = data['value']
                    
                    if labels:
                        label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                        output.append(f"{metric_name}{{{label_str}}} {value}")
                    else:
                        output.append(f"{metric_name} {value}")
                
                output.append("")  # Empty line between metrics
        
        return '\n'.join(output)
    
    def cleanup(self):
        """Cleanup collector"""
        self.collecting = False

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint"""
    
    def do_GET(self):
        if self.path == '/metrics':
            try:
                metrics_output = collector.get_prometheus_output()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(metrics_output.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error generating metrics: {e}".encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics server"""
    try:
        server = HTTPServer(('localhost', port), MetricsHandler)
        print(f"Claude Code metrics server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start metrics server: {e}")

# Global collector instance
collector = None

def main():
    """Main entry point"""
    global collector
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            collector = MetricsCollector()
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
            start_metrics_server(port)
        
        elif command == 'collect':
            collector = MetricsCollector()
            time.sleep(5)  # Let it collect some data
            print("Metrics collection completed")
            collector.cleanup()
        
        elif command == 'export':
            collector = MetricsCollector()
            time.sleep(2)  # Brief collection
            print(collector.get_prometheus_output())
            collector.cleanup()
        
        else:
            print("Usage: claude_metrics_collector.py [start|collect|export] [port]")
    else:
        # Default: start collection and server
        collector = MetricsCollector()
        start_metrics_server()

if __name__ == '__main__':
    main()