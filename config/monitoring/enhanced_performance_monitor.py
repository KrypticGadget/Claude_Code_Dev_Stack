#!/usr/bin/env python3
"""
Enhanced Performance Monitor - V3.6.9 with Prometheus Integration
Real-time performance monitoring with metrics export for Claude Code
"""

import json
import time
import os
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

class EnhancedPerformanceMonitor:
    """Enhanced performance monitor with Prometheus metrics export"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.logs_dir = self.claude_dir / 'logs' / 'performance'
        self.metrics_dir = self.claude_dir / 'metrics'
        self.state_dir = self.claude_dir / 'state'
        
        # Create directories
        for directory in [self.logs_dir, self.metrics_dir, self.state_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Performance metrics storage
        self.metrics = {
            'agent_performance': {},
            'hook_performance': {},
            'session_performance': {},
            'system_performance': {},
            'resource_usage': {},
            'baselines': {},
            'alerts': []
        }
        
        # Prometheus metrics
        self.prometheus_metrics = {}
        
        # Performance baselines
        self.baselines = self.load_baselines()
        
        # Monitoring settings
        self.monitoring_active = True
        self.collection_interval = 15  # seconds
        self.baseline_update_interval = 3600  # 1 hour
        
        # Start monitoring threads
        self.start_monitoring_threads()
    
    def setup_logging(self):
        """Setup structured logging for performance monitoring"""
        log_file = self.logs_dir / 'performance_monitor.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] Performance: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring_threads(self):
        """Start all monitoring threads"""
        threads = [
            threading.Thread(target=self.system_metrics_loop, daemon=True),
            threading.Thread(target=self.agent_metrics_loop, daemon=True),
            threading.Thread(target=self.session_metrics_loop, daemon=True),
            threading.Thread(target=self.baseline_update_loop, daemon=True),
            threading.Thread(target=self.alert_processing_loop, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        self.logger.info("Enhanced performance monitoring started")
    
    def system_metrics_loop(self):
        """Continuously collect system performance metrics"""
        while self.monitoring_active:
            try:
                metrics = self.collect_system_metrics()
                self.update_system_performance(metrics)
                self.check_system_thresholds(metrics)
                
            except Exception as e:
                self.logger.error(f"System metrics collection error: {e}")
            
            time.sleep(self.collection_interval)
    
    def agent_metrics_loop(self):
        """Continuously collect agent performance metrics"""
        while self.monitoring_active:
            try:
                metrics = self.collect_agent_metrics()
                self.update_agent_performance(metrics)
                self.check_agent_thresholds(metrics)
                
            except Exception as e:
                self.logger.error(f"Agent metrics collection error: {e}")
            
            time.sleep(self.collection_interval)
    
    def session_metrics_loop(self):
        """Continuously collect session performance metrics"""
        while self.monitoring_active:
            try:
                metrics = self.collect_session_metrics()
                self.update_session_performance(metrics)
                self.check_session_thresholds(metrics)
                
            except Exception as e:
                self.logger.error(f"Session metrics collection error: {e}")
            
            time.sleep(self.collection_interval)
    
    def baseline_update_loop(self):
        """Periodically update performance baselines"""
        while self.monitoring_active:
            try:
                self.update_performance_baselines()
                self.save_baselines()
                
            except Exception as e:
                self.logger.error(f"Baseline update error: {e}")
            
            time.sleep(self.baseline_update_interval)
    
    def alert_processing_loop(self):
        """Process and send alerts"""
        while self.monitoring_active:
            try:
                self.process_alerts()
                
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
            
            time.sleep(30)  # Check alerts every 30 seconds
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent if network_io else 0,
                    'bytes_recv': network_io.bytes_recv if network_io else 0,
                    'packets_sent': network_io.packets_sent if network_io else 0,
                    'packets_recv': network_io.packets_recv if network_io else 0
                },
                'processes': {
                    'count': process_count
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
            return {}
    
    def collect_agent_metrics(self) -> Dict[str, Any]:
        """Collect agent performance metrics"""
        try:
            perf_file = self.state_dir / 'performance_metrics.json'
            orchestration_file = self.state_dir / 'orchestration_history.json'
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'agents': {},
                'orchestration': {}
            }
            
            # Load performance metrics
            if perf_file.exists():
                with open(perf_file) as f:
                    perf_data = json.load(f)
                
                agent_metrics = perf_data.get('agent_metrics', {})
                for agent_name, agent_data in agent_metrics.items():
                    metrics['agents'][agent_name] = {
                        'executions': agent_data.get('executions', 0),
                        'total_time': agent_data.get('total_time', 0),
                        'average_time': agent_data.get('average_time', 0),
                        'total_tokens': agent_data.get('total_tokens', 0),
                        'average_tokens': agent_data.get('average_tokens', 0),
                        'last_execution': agent_data.get('last_execution'),
                        'success_rate': self.calculate_success_rate(agent_name)
                    }
            
            # Load orchestration metrics
            if orchestration_file.exists():
                with open(orchestration_file) as f:
                    orch_data = json.load(f)
                
                metrics['orchestration'] = {
                    'total_orchestrations': len(orch_data),
                    'recent_complexity': self.analyze_recent_complexity(orch_data),
                    'agent_usage_patterns': self.analyze_agent_patterns(orch_data)
                }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Agent metrics collection failed: {e}")
            return {}
    
    def collect_session_metrics(self) -> Dict[str, Any]:
        """Collect session performance metrics"""
        try:
            session_files = list(self.state_dir.glob('session_*.json'))
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'active_sessions': 0,
                'total_sessions': len(session_files),
                'session_sizes': [],
                'load_times': [],
                'save_times': []
            }
            
            for session_file in session_files:
                try:
                    with open(session_file) as f:
                        session_data = json.load(f)
                    
                    # Check if session is active (modified recently)
                    mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                    if datetime.now() - mod_time < timedelta(hours=1):
                        metrics['active_sessions'] += 1
                    
                    # Session size
                    size = session_file.stat().st_size
                    metrics['session_sizes'].append(size)
                    
                    # Performance data if available
                    if 'performance' in session_data:
                        perf = session_data['performance']
                        if 'load_time' in perf:
                            metrics['load_times'].append(perf['load_time'])
                        if 'save_time' in perf:
                            metrics['save_times'].append(perf['save_time'])
                
                except Exception as e:
                    self.logger.warning(f"Error processing session {session_file}: {e}")
            
            # Calculate averages
            if metrics['session_sizes']:
                metrics['average_session_size'] = sum(metrics['session_sizes']) / len(metrics['session_sizes'])
                metrics['max_session_size'] = max(metrics['session_sizes'])
            
            if metrics['load_times']:
                metrics['average_load_time'] = sum(metrics['load_times']) / len(metrics['load_times'])
            
            if metrics['save_times']:
                metrics['average_save_time'] = sum(metrics['save_times']) / len(metrics['save_times'])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Session metrics collection failed: {e}")
            return {}
    
    def update_system_performance(self, metrics: Dict[str, Any]):
        """Update system performance metrics and Prometheus exports"""
        if not metrics:
            return
        
        timestamp = metrics.get('timestamp', datetime.now().isoformat())
        
        # Store in metrics
        self.metrics['system_performance'][timestamp] = metrics
        
        # Update Prometheus metrics
        self.update_prometheus_metric('claude_system_cpu_percent', metrics['cpu']['percent'])
        self.update_prometheus_metric('claude_system_memory_percent', metrics['memory']['percent'])
        self.update_prometheus_metric('claude_system_disk_percent', metrics['disk']['percent'])
        self.update_prometheus_metric('claude_system_process_count', metrics['processes']['count'])
        
        # Log significant changes
        if metrics['cpu']['percent'] > 80:
            self.logger.warning(f"High CPU usage: {metrics['cpu']['percent']:.1f}%")
        
        if metrics['memory']['percent'] > 85:
            self.logger.warning(f"High memory usage: {metrics['memory']['percent']:.1f}%")
        
        # Keep only recent metrics (last 24 hours)
        self.cleanup_old_metrics('system_performance', hours=24)
    
    def update_agent_performance(self, metrics: Dict[str, Any]):
        """Update agent performance metrics"""
        if not metrics:
            return
        
        timestamp = metrics.get('timestamp', datetime.now().isoformat())
        self.metrics['agent_performance'][timestamp] = metrics
        
        # Update Prometheus metrics for each agent
        for agent_name, agent_data in metrics.get('agents', {}).items():
            labels = {'agent_name': agent_name}
            
            self.update_prometheus_metric('claude_agent_executions_total', 
                                        agent_data.get('executions', 0), labels)
            self.update_prometheus_metric('claude_agent_average_time_seconds', 
                                        agent_data.get('average_time', 0), labels)
            self.update_prometheus_metric('claude_agent_total_tokens', 
                                        agent_data.get('total_tokens', 0), labels)
            self.update_prometheus_metric('claude_agent_success_rate', 
                                        agent_data.get('success_rate', 1.0), labels)
        
        self.cleanup_old_metrics('agent_performance', hours=48)
    
    def update_session_performance(self, metrics: Dict[str, Any]):
        """Update session performance metrics"""
        if not metrics:
            return
        
        timestamp = metrics.get('timestamp', datetime.now().isoformat())
        self.metrics['session_performance'][timestamp] = metrics
        
        # Update Prometheus metrics
        self.update_prometheus_metric('claude_active_sessions', metrics.get('active_sessions', 0))
        self.update_prometheus_metric('claude_total_sessions', metrics.get('total_sessions', 0))
        
        if 'average_session_size' in metrics:
            self.update_prometheus_metric('claude_average_session_size_bytes', 
                                        metrics['average_session_size'])
        
        if 'average_load_time' in metrics:
            self.update_prometheus_metric('claude_average_session_load_time_seconds', 
                                        metrics['average_load_time'])
        
        self.cleanup_old_metrics('session_performance', hours=24)
    
    def update_prometheus_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Update Prometheus metric"""
        if metric_name not in self.prometheus_metrics:
            self.prometheus_metrics[metric_name] = {}
        
        label_key = json.dumps(labels or {}, sort_keys=True)
        self.prometheus_metrics[metric_name][label_key] = {
            'value': value,
            'timestamp': time.time(),
            'labels': labels or {}
        }
    
    def calculate_success_rate(self, agent_name: str) -> float:
        """Calculate agent success rate from recent executions"""
        try:
            # This would integrate with actual execution tracking
            # For now, return a default high success rate
            return 0.95
        except:
            return 1.0
    
    def analyze_recent_complexity(self, orchestration_data: Dict) -> str:
        """Analyze recent orchestration complexity"""
        try:
            recent_orchestrations = list(orchestration_data.values())[-10:]
            if not recent_orchestrations:
                return "low"
            
            avg_complexity = sum(
                len(orch.get('agents', [])) for orch in recent_orchestrations
            ) / len(recent_orchestrations)
            
            if avg_complexity > 5:
                return "high"
            elif avg_complexity > 2:
                return "medium"
            else:
                return "low"
        except:
            return "unknown"
    
    def analyze_agent_patterns(self, orchestration_data: Dict) -> Dict[str, int]:
        """Analyze agent usage patterns"""
        try:
            agent_counts = {}
            for orch in orchestration_data.values():
                for agent in orch.get('agents', []):
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
            return agent_counts
        except:
            return {}
    
    def cleanup_old_metrics(self, metric_type: str, hours: int = 24):
        """Remove old metrics to prevent memory bloat"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if metric_type in self.metrics:
            metrics_dict = self.metrics[metric_type]
            old_keys = []
            
            for timestamp_str in metrics_dict.keys():
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp < cutoff_time:
                        old_keys.append(timestamp_str)
                except:
                    old_keys.append(timestamp_str)  # Remove invalid timestamps
            
            for key in old_keys:
                del metrics_dict[key]
    
    def check_system_thresholds(self, metrics: Dict[str, Any]):
        """Check system metrics against thresholds and generate alerts"""
        if not metrics:
            return
        
        alerts = []
        
        # CPU threshold
        cpu_percent = metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > 90:
            alerts.append({
                'type': 'system_cpu_high',
                'severity': 'critical',
                'message': f"CPU usage critical: {cpu_percent:.1f}%",
                'value': cpu_percent,
                'threshold': 90
            })
        elif cpu_percent > 80:
            alerts.append({
                'type': 'system_cpu_warning',
                'severity': 'warning',
                'message': f"CPU usage high: {cpu_percent:.1f}%",
                'value': cpu_percent,
                'threshold': 80
            })
        
        # Memory threshold
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        if memory_percent > 90:
            alerts.append({
                'type': 'system_memory_critical',
                'severity': 'critical',
                'message': f"Memory usage critical: {memory_percent:.1f}%",
                'value': memory_percent,
                'threshold': 90
            })
        elif memory_percent > 85:
            alerts.append({
                'type': 'system_memory_warning',
                'severity': 'warning',
                'message': f"Memory usage high: {memory_percent:.1f}%",
                'value': memory_percent,
                'threshold': 85
            })
        
        # Disk threshold
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        if disk_percent > 95:
            alerts.append({
                'type': 'system_disk_critical',
                'severity': 'critical',
                'message': f"Disk usage critical: {disk_percent:.1f}%",
                'value': disk_percent,
                'threshold': 95
            })
        elif disk_percent > 90:
            alerts.append({
                'type': 'system_disk_warning',
                'severity': 'warning',
                'message': f"Disk usage high: {disk_percent:.1f}%",
                'value': disk_percent,
                'threshold': 90
            })
        
        # Add alerts to queue
        for alert in alerts:
            alert['timestamp'] = datetime.now().isoformat()
            alert['component'] = 'system'
            self.add_alert(alert)
    
    def check_agent_thresholds(self, metrics: Dict[str, Any]):
        """Check agent metrics against thresholds"""
        if not metrics:
            return
        
        for agent_name, agent_data in metrics.get('agents', {}).items():
            # Check execution time
            avg_time = agent_data.get('average_time', 0)
            if avg_time > 30:
                self.add_alert({
                    'type': 'agent_slow_execution',
                    'severity': 'warning',
                    'message': f"Agent {agent_name} slow execution: {avg_time:.1f}s",
                    'agent_name': agent_name,
                    'value': avg_time,
                    'threshold': 30,
                    'timestamp': datetime.now().isoformat(),
                    'component': 'agent'
                })
            
            # Check success rate
            success_rate = agent_data.get('success_rate', 1.0)
            if success_rate < 0.9:
                self.add_alert({
                    'type': 'agent_low_success_rate',
                    'severity': 'warning',
                    'message': f"Agent {agent_name} low success rate: {success_rate:.1%}",
                    'agent_name': agent_name,
                    'value': success_rate,
                    'threshold': 0.9,
                    'timestamp': datetime.now().isoformat(),
                    'component': 'agent'
                })
    
    def check_session_thresholds(self, metrics: Dict[str, Any]):
        """Check session metrics against thresholds"""
        if not metrics:
            return
        
        # Check large sessions
        max_size = metrics.get('max_session_size', 0)
        if max_size > 10 * 1024 * 1024:  # 10MB
            self.add_alert({
                'type': 'session_size_large',
                'severity': 'warning',
                'message': f"Large session detected: {max_size / 1024 / 1024:.1f}MB",
                'value': max_size,
                'threshold': 10 * 1024 * 1024,
                'timestamp': datetime.now().isoformat(),
                'component': 'session'
            })
        
        # Check load times
        avg_load_time = metrics.get('average_load_time', 0)
        if avg_load_time > 5.0:
            self.add_alert({
                'type': 'session_slow_load',
                'severity': 'warning',
                'message': f"Slow session loading: {avg_load_time:.1f}s",
                'value': avg_load_time,
                'threshold': 5.0,
                'timestamp': datetime.now().isoformat(),
                'component': 'session'
            })
    
    def add_alert(self, alert: Dict[str, Any]):
        """Add alert to queue"""
        self.metrics['alerts'].append(alert)
        
        # Keep only last 100 alerts
        if len(self.metrics['alerts']) > 100:
            self.metrics['alerts'] = self.metrics['alerts'][-100:]
        
        # Log alert
        severity = alert.get('severity', 'info')
        message = alert.get('message', 'Unknown alert')
        
        if severity == 'critical':
            self.logger.error(f"ALERT: {message}")
        elif severity == 'warning':
            self.logger.warning(f"ALERT: {message}")
        else:
            self.logger.info(f"ALERT: {message}")
    
    def process_alerts(self):
        """Process and send alerts"""
        # This would integrate with notification systems
        # For now, just log recent alerts
        recent_alerts = [
            alert for alert in self.metrics['alerts']
            if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(minutes=5)
        ]
        
        if recent_alerts:
            self.logger.info(f"Recent alerts: {len(recent_alerts)}")
    
    def load_baselines(self) -> Dict[str, Any]:
        """Load performance baselines"""
        baseline_file = self.metrics_dir / 'performance_baselines.json'
        if baseline_file.exists():
            try:
                with open(baseline_file) as f:
                    return json.load(f)
            except:
                pass
        
        # Default baselines
        return {
            'system': {
                'cpu_normal': 20.0,
                'memory_normal': 50.0,
                'disk_normal': 30.0
            },
            'agent': {
                'execution_time_normal': 5.0,
                'success_rate_normal': 0.95
            },
            'session': {
                'size_normal': 1024 * 1024,  # 1MB
                'load_time_normal': 1.0
            }
        }
    
    def update_performance_baselines(self):
        """Update performance baselines based on recent data"""
        try:
            # Calculate new baselines from recent data
            self.calculate_system_baselines()
            self.calculate_agent_baselines()
            self.calculate_session_baselines()
            
            self.logger.info("Performance baselines updated")
            
        except Exception as e:
            self.logger.error(f"Baseline update failed: {e}")
    
    def calculate_system_baselines(self):
        """Calculate system performance baselines"""
        recent_metrics = list(self.metrics['system_performance'].values())[-100:]
        if not recent_metrics:
            return
        
        cpu_values = [m['cpu']['percent'] for m in recent_metrics if 'cpu' in m]
        memory_values = [m['memory']['percent'] for m in recent_metrics if 'memory' in m]
        
        if cpu_values:
            self.baselines['system']['cpu_normal'] = sum(cpu_values) / len(cpu_values)
        
        if memory_values:
            self.baselines['system']['memory_normal'] = sum(memory_values) / len(memory_values)
    
    def calculate_agent_baselines(self):
        """Calculate agent performance baselines"""
        recent_metrics = list(self.metrics['agent_performance'].values())[-50:]
        if not recent_metrics:
            return
        
        all_exec_times = []
        all_success_rates = []
        
        for metric in recent_metrics:
            for agent_data in metric.get('agents', {}).values():
                if 'average_time' in agent_data:
                    all_exec_times.append(agent_data['average_time'])
                if 'success_rate' in agent_data:
                    all_success_rates.append(agent_data['success_rate'])
        
        if all_exec_times:
            self.baselines['agent']['execution_time_normal'] = sum(all_exec_times) / len(all_exec_times)
        
        if all_success_rates:
            self.baselines['agent']['success_rate_normal'] = sum(all_success_rates) / len(all_success_rates)
    
    def calculate_session_baselines(self):
        """Calculate session performance baselines"""
        recent_metrics = list(self.metrics['session_performance'].values())[-50:]
        if not recent_metrics:
            return
        
        all_sizes = []
        all_load_times = []
        
        for metric in recent_metrics:
            if 'average_session_size' in metric:
                all_sizes.append(metric['average_session_size'])
            if 'average_load_time' in metric:
                all_load_times.append(metric['average_load_time'])
        
        if all_sizes:
            self.baselines['session']['size_normal'] = sum(all_sizes) / len(all_sizes)
        
        if all_load_times:
            self.baselines['session']['load_time_normal'] = sum(all_load_times) / len(all_load_times)
    
    def save_baselines(self):
        """Save performance baselines"""
        baseline_file = self.metrics_dir / 'performance_baselines.json'
        try:
            with open(baseline_file, 'w') as f:
                json.dump(self.baselines, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save baselines: {e}")
    
    def get_prometheus_metrics(self) -> str:
        """Generate Prometheus metrics format"""
        output = []
        
        for metric_name, metric_data in self.prometheus_metrics.items():
            # Add metric help
            output.append(f"# HELP {metric_name} {metric_name.replace('_', ' ').title()}")
            output.append(f"# TYPE {metric_name} gauge")
            
            # Add metric values
            for label_key, data in metric_data.items():
                labels = data['labels']
                value = data['value']
                
                if labels:
                    label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                    output.append(f"{metric_name}{{{label_str}}} {value}")
                else:
                    output.append(f"{metric_name} {value}")
            
            output.append("")  # Empty line
        
        return '\n'.join(output)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        try:
            # Latest metrics
            latest_system = list(self.metrics['system_performance'].values())[-1:] if self.metrics['system_performance'] else [{}]
            latest_agent = list(self.metrics['agent_performance'].values())[-1:] if self.metrics['agent_performance'] else [{}]
            latest_session = list(self.metrics['session_performance'].values())[-1:] if self.metrics['session_performance'] else [{}]
            
            system_metrics = latest_system[0] if latest_system else {}
            agent_metrics = latest_agent[0] if latest_agent else {}
            session_metrics = latest_session[0] if latest_session else {}
            
            # Recent alerts
            recent_alerts = [
                alert for alert in self.metrics['alerts']
                if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=1)
            ]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': system_metrics.get('cpu', {}).get('percent', 0),
                    'memory_percent': system_metrics.get('memory', {}).get('percent', 0),
                    'disk_percent': system_metrics.get('disk', {}).get('percent', 0),
                    'process_count': system_metrics.get('processes', {}).get('count', 0)
                },
                'agents': {
                    'total_agents': len(agent_metrics.get('agents', {})),
                    'total_executions': sum(
                        agent.get('executions', 0) 
                        for agent in agent_metrics.get('agents', {}).values()
                    ),
                    'average_execution_time': sum(
                        agent.get('average_time', 0) 
                        for agent in agent_metrics.get('agents', {}).values()
                    ) / max(len(agent_metrics.get('agents', {})), 1)
                },
                'sessions': {
                    'active_sessions': session_metrics.get('active_sessions', 0),
                    'total_sessions': session_metrics.get('total_sessions', 0),
                    'average_size_mb': session_metrics.get('average_session_size', 0) / 1024 / 1024,
                    'average_load_time': session_metrics.get('average_load_time', 0)
                },
                'alerts': {
                    'recent_count': len(recent_alerts),
                    'critical_count': len([a for a in recent_alerts if a.get('severity') == 'critical']),
                    'warning_count': len([a for a in recent_alerts if a.get('severity') == 'warning'])
                },
                'baselines': self.baselines
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {e}")
            return {}
    
    def cleanup(self):
        """Stop monitoring and cleanup"""
        self.monitoring_active = False
        self.save_baselines()
        
        # Save final metrics snapshot
        metrics_file = self.metrics_dir / f'final_snapshot_{int(time.time())}.json'
        try:
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save final metrics: {e}")
        
        self.logger.info("Enhanced performance monitoring stopped")

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint"""
    
    def do_GET(self):
        if self.path == '/metrics':
            try:
                metrics_output = monitor.get_prometheus_metrics()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(metrics_output.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())
        
        elif self.path == '/performance-metrics':
            try:
                summary = monitor.get_performance_summary()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(summary, indent=2).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def start_metrics_server(port: int = 8005):
    """Start metrics HTTP server"""
    try:
        server = HTTPServer(('localhost', port), MetricsHandler)
        print(f"Enhanced performance metrics server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start metrics server: {e}")

# Global monitor instance
monitor = None

def main():
    """Main entry point"""
    global monitor
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            monitor = EnhancedPerformanceMonitor()
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8005
            start_metrics_server(port)
        
        elif command == 'summary':
            monitor = EnhancedPerformanceMonitor()
            time.sleep(5)  # Let it collect some data
            summary = monitor.get_performance_summary()
            print(json.dumps(summary, indent=2))
            monitor.cleanup()
        
        elif command == 'export':
            monitor = EnhancedPerformanceMonitor()
            time.sleep(2)
            print(monitor.get_prometheus_metrics())
            monitor.cleanup()
        
        else:
            print("Usage: enhanced_performance_monitor.py [start|summary|export] [port]")
    else:
        # Default: start monitoring
        monitor = EnhancedPerformanceMonitor()
        start_metrics_server()

if __name__ == '__main__':
    main()