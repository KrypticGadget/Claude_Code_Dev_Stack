#!/usr/bin/env python3
"""
Dashboard Server - V3.0+ Web Monitoring Interface
Provides real-time monitoring dashboard for Claude Code Dev Stack
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import psutil

try:
    from flask import Flask, render_template, jsonify, send_from_directory, session, request
    from flask_socketio import SocketIO, emit
except ImportError:
    print("Flask and Flask-SocketIO required. Install with: pip install flask flask-socketio")
    sys.exit(1)

# Import mobile authentication
sys.path.append(str(Path(__file__).parent.parent / 'mobile'))
try:
    from mobile_auth import MobileAuthManager, create_auth_decorators
except ImportError:
    print("Warning: Mobile authentication not available")
    MobileAuthManager = None
    create_auth_decorators = None

class DashboardServer:
    """Web dashboard for monitoring Claude Code Dev Stack V3+"""
    
    def __init__(self, port: int = 8080, mobile_auth_token: str = None):
        self.port = port
        self.claude_dir = Path.home() / '.claude'
        self.dashboard_dir = Path(__file__).parent
        self.mobile_auth_token = mobile_auth_token
        
        # Mobile authentication setup
        self.auth_manager = None
        self.require_auth = None
        self.require_session = None
        
        if MobileAuthManager and mobile_auth_token:
            self.auth_manager = MobileAuthManager()
            self.require_auth, self.require_session = create_auth_decorators(self.auth_manager)
            print("🔒 Mobile authentication enabled")
        
        # Flask app setup
        self.app = Flask(__name__, 
                        template_folder=str(self.dashboard_dir / 'templates'),
                        static_folder=str(self.dashboard_dir / 'static'))
        
        # Generate secure secret key
        secret_key = os.getenv('CLAUDE_DASHBOARD_SECRET') or 'claude-code-dashboard-v3-' + str(time.time())
        self.app.config['SECRET_KEY'] = secret_key
        self.app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dashboard state
        self.metrics = {}
        self.alerts = []
        self.system_status = 'unknown'
        self.last_update = datetime.now()
        
        # Settings
        self.settings = self.load_settings()
        
        # Monitoring thread
        self.monitoring = True
        self.monitor_thread = None
        
        self.setup_routes()
        self.setup_socketio_events()
    
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
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        # Helper function to apply auth if available
        def maybe_auth(route_func):
            if self.require_auth:
                return self.require_auth(route_func)
            return route_func
        
        def maybe_session(route_func):
            if self.require_session:
                return self.require_session(route_func)
            return route_func
        
        @self.app.route('/')
        @maybe_auth
        def dashboard():
            """Main dashboard page"""
            # Add auth status to template context
            auth_status = {}
            if self.auth_manager:
                session_id = session.get('claude_session_id')
                if session_id:
                    auth_status = self.auth_manager.get_session_info(session_id) or {}
            
            return render_template('dashboard.html', auth_status=auth_status)
        
        @self.app.route('/api/auth/status')
        def api_auth_status():
            """Authentication status API"""
            if not self.auth_manager:
                return jsonify({'authenticated': False, 'auth_enabled': False})
            
            session_id = session.get('claude_session_id')
            if session_id:
                valid, session_data = self.auth_manager.validate_session(session_id)
                if valid:
                    return jsonify({
                        'authenticated': True,
                        'auth_enabled': True,
                        'session_info': self.auth_manager.get_session_info(session_id)
                    })
            
            return jsonify({'authenticated': False, 'auth_enabled': True})
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        def api_logout():
            """Logout API"""
            if self.auth_manager:
                session_id = session.get('claude_session_id')
                if session_id:
                    self.auth_manager.revoke_session(session_id)
                session.pop('claude_session_id', None)
            
            return jsonify({'success': True})
        
        @self.app.route('/api/status')
        @maybe_session
        def api_status():
            """System status API"""
            return jsonify({
                'status': self.system_status,
                'last_update': self.last_update.isoformat(),
                'uptime': self.get_uptime(),
                'version': '3.0+'
            })
        
        @self.app.route('/api/metrics')
        @maybe_session
        def api_metrics():
            """System metrics API"""
            return jsonify(self.get_current_metrics())
        
        @self.app.route('/api/alerts')
        @maybe_session
        def api_alerts():
            """Active alerts API"""
            return jsonify({
                'alerts': self.alerts[-50:],  # Last 50 alerts
                'count': len(self.alerts)
            })
        
        @self.app.route('/api/agents')
        @maybe_session
        def api_agents():
            """Agent status API"""
            return jsonify(self.get_agent_status())
        
        @self.app.route('/api/hooks')
        def api_hooks():
            """Hook status API"""
            return jsonify(self.get_hook_status())
        
        @self.app.route('/api/performance')
        def api_performance():
            """Performance metrics API"""
            return jsonify(self.get_performance_metrics())
        
        @self.app.route('/api/security')
        def api_security():
            """Security status API"""
            return jsonify(self.get_security_status())
        
        @self.app.route('/api/logs')
        def api_logs():
            """Recent logs API"""
            return jsonify(self.get_recent_logs())
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return send_from_directory(self.dashboard_dir / 'static', filename)
    
    def setup_socketio_events(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            emit('status_update', {
                'status': self.system_status,
                'timestamp': datetime.now().isoformat(),
                'message': 'Connected to dashboard'
            })
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle update request from client"""
            self.broadcast_update()
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Load performance metrics if available
            perf_file = self.claude_dir / 'state' / 'performance_metrics.json'
            perf_metrics = {}
            if perf_file.exists():
                try:
                    with open(perf_file, 'r') as f:
                        perf_data = json.load(f)
                        perf_metrics = perf_data.get('summary', {})
                except:
                    pass
            
            return {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_gb': round(memory.used / (1024**3), 2),
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'disk_percent': disk.percent,
                    'disk_used_gb': round(disk.used / (1024**3), 2),
                    'disk_total_gb': round(disk.total / (1024**3), 2)
                },
                'claude_code': {
                    'total_operations': perf_metrics.get('total_operations', 0),
                    'average_execution_time': perf_metrics.get('average_execution_time', 0),
                    'total_tokens_used': perf_metrics.get('total_tokens_used', 0),
                    'issues_detected': perf_metrics.get('issues_detected', 0)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f"Error getting metrics: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        agents_dir = self.claude_dir / '..' / '.claude-example' / 'agents'
        if not agents_dir.exists():
            agents_dir = Path.cwd() / '.claude-example' / 'agents'
        
        status = {
            'total_agents': 0,
            'active_agents': 0,
            'agents': []
        }
        
        if agents_dir.exists():
            agent_files = list(agents_dir.glob('*.md'))
            status['total_agents'] = len(agent_files)
            
            for agent_file in agent_files:
                agent_name = agent_file.stem
                
                # Check if agent has been used recently
                perf_file = self.claude_dir / 'state' / 'performance_metrics.json'
                last_used = None
                executions = 0
                
                if perf_file.exists():
                    try:
                        with open(perf_file, 'r') as f:
                            perf_data = json.load(f)
                            agent_metrics = perf_data.get('agent_metrics', {}).get(agent_name, {})
                            last_used = agent_metrics.get('last_execution')
                            executions = agent_metrics.get('executions', 0)
                            if last_used:
                                status['active_agents'] += 1
                    except:
                        pass
                
                status['agents'].append({
                    'name': agent_name,
                    'last_used': last_used,
                    'executions': executions,
                    'file_size': agent_file.stat().st_size if agent_file.exists() else 0
                })
        
        return status
    
    def get_hook_status(self) -> Dict:
        """Get status of all hooks"""
        hooks_dir = self.claude_dir / 'hooks'
        
        status = {
            'total_hooks': 0,
            'enabled_hooks': 0,
            'hooks': []
        }
        
        if hooks_dir.exists():
            hook_files = list(hooks_dir.glob('*.py'))
            status['total_hooks'] = len(hook_files)
            
            for hook_file in hook_files:
                hook_name = hook_file.stem
                
                # Check if hook is executable
                is_enabled = os.access(hook_file, os.X_OK) if os.name != 'nt' else True
                if is_enabled:
                    status['enabled_hooks'] += 1
                
                status['hooks'].append({
                    'name': hook_name,
                    'enabled': is_enabled,
                    'file_size': hook_file.stat().st_size,
                    'modified': hook_file.stat().st_mtime
                })
        
        return status
    
    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics"""
        perf_file = self.claude_dir / 'state' / 'performance_metrics.json'
        
        if not perf_file.exists():
            return {'error': 'Performance metrics not available'}
        
        try:
            with open(perf_file, 'r') as f:
                data = json.load(f)
            
            # Process resource metrics for charts
            resource_metrics = data.get('resource_metrics', [])
            if resource_metrics:
                # Get last 20 data points
                recent_metrics = resource_metrics[-20:]
                
                return {
                    'summary': data.get('summary', {}),
                    'agent_metrics': data.get('agent_metrics', {}),
                    'operation_metrics': data.get('operation_metrics', {}),
                    'resource_timeline': {
                        'timestamps': [m['timestamp'] for m in recent_metrics],
                        'cpu_usage': [m['cpu_percent'] for m in recent_metrics],
                        'memory_usage': [m['memory_percent'] for m in recent_metrics],
                        'disk_usage': [m['disk_percent'] for m in recent_metrics]
                    },
                    'recent_issues': data.get('performance_issues', [])[-10:]
                }
        except Exception as e:
            return {'error': f'Error loading performance metrics: {str(e)}'}
    
    def get_security_status(self) -> Dict:
        """Get security scan status"""
        # Look for recent security scan results
        scan_files = list((self.claude_dir / 'logs').glob('security_scan_*.json')) if (self.claude_dir / 'logs').exists() else []
        
        if not scan_files:
            return {
                'status': 'unknown',
                'message': 'No recent security scans found',
                'recommendations': ['Run security scan: python ~/.claude/hooks/security_scanner.py scan-directory']
            }
        
        # Get most recent scan
        latest_scan = max(scan_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_scan, 'r') as f:
                scan_data = json.load(f)
            
            high_issues = scan_data.get('severity_counts', {}).get('HIGH', 0)
            medium_issues = scan_data.get('severity_counts', {}).get('MEDIUM', 0)
            total_issues = scan_data.get('total_issues', 0)
            
            if high_issues > 0:
                status = 'critical'
            elif medium_issues > 0:
                status = 'warning'
            elif total_issues > 0:
                status = 'attention'
            else:
                status = 'secure'
            
            return {
                'status': status,
                'total_issues': total_issues,
                'severity_counts': scan_data.get('severity_counts', {}),
                'files_scanned': scan_data.get('files_scanned', 0),
                'last_scan': datetime.fromtimestamp(latest_scan.stat().st_mtime).isoformat(),
                'recent_issues': scan_data.get('issues', [])[:5]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error reading security scan: {str(e)}'
            }
    
    def get_recent_logs(self) -> Dict:
        """Get recent log entries"""
        logs_dir = self.claude_dir / 'logs'
        
        if not logs_dir.exists():
            return {'logs': [], 'message': 'No logs directory found'}
        
        logs = []
        
        # Get recent log files
        log_files = sorted(logs_dir.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True)
        
        for log_file in log_files[:5]:  # Last 5 log files
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines[-10:]:  # Last 10 lines of each file
                    if line.strip():
                        logs.append({
                            'file': log_file.name,
                            'content': line.strip(),
                            'timestamp': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                        })
            except:
                continue
        
        return {
            'logs': logs[:50],  # Last 50 log entries total
            'total_files': len(log_files)
        }
    
    def add_alert(self, level: str, message: str, details: str = None):
        """Add alert to dashboard"""
        alert = {
            'id': len(self.alerts),
            'level': level,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Broadcast alert via SocketIO
        self.socketio.emit('new_alert', alert)
    
    def update_system_status(self):
        """Update overall system status"""
        try:
            metrics = self.get_current_metrics()
            
            # Determine status based on metrics
            cpu = metrics['system']['cpu_percent']
            memory = metrics['system']['memory_percent']
            disk = metrics['system']['disk_percent']
            
            if cpu > 90 or memory > 90 or disk > 95:
                self.system_status = 'critical'
            elif cpu > 70 or memory > 70 or disk > 85:
                self.system_status = 'warning'
            else:
                self.system_status = 'healthy'
            
            self.last_update = datetime.now()
            
        except Exception as e:
            self.system_status = 'error'
            self.add_alert('error', f'System monitoring error: {str(e)}')
    
    def broadcast_update(self):
        """Broadcast update to all connected clients"""
        try:
            self.socketio.emit('metrics_update', self.get_current_metrics())
            self.socketio.emit('status_update', {
                'status': self.system_status,
                'timestamp': self.last_update.isoformat()
            })
        except Exception as e:
            print(f"Error broadcasting update: {e}")
    
    def monitor_system(self):
        """Background monitoring thread"""
        while self.monitoring:
            try:
                self.update_system_status()
                self.broadcast_update()
                
                # Check for new alerts every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer on errors
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """Run the dashboard server"""
        print(f"Starting Claude Code Dashboard V3+ on http://{host}:{self.port}")
        
        # Play startup audio
        self.play_audio('dashboard_started.wav')
        
        # Start monitoring
        self.start_monitoring()
        
        try:
            self.socketio.run(self.app, host=host, port=self.port, debug=debug)
        except KeyboardInterrupt:
            print("\\nShutting down dashboard...")
        finally:
            self.stop_monitoring()
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Code Dashboard V3+')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--mobile-auth', help='Mobile authentication token')
    
    args = parser.parse_args()
    
    # Check for mobile auth token in environment
    mobile_auth_token = args.mobile_auth or os.getenv('CLAUDE_MOBILE_AUTH_TOKEN')
    
    dashboard = DashboardServer(port=args.port, mobile_auth_token=mobile_auth_token)
    dashboard.run(host=args.host, debug=args.debug)

if __name__ == '__main__':
    main()