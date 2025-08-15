#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code V3+ Real-Time Monitoring Dashboard
Comprehensive real-time monitoring with WebSocket support
Designed for Samsung Galaxy S25 Edge mobile access
"""

import os
import sys
import json
import time
import uuid
import logging
import threading
import subprocess
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from flask import Flask, render_template_string, request, jsonify, session
from flask_socketio import SocketIO, emit, disconnect
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

class RealtimeDashboard:
    """Real-time monitoring dashboard with WebSocket support"""
    
    def __init__(self, port: int = 8080, auth_token: str = None):
        self.port = port
        self.auth_token = auth_token
        self.claude_dir = Path.home() / '.claude'
        self.mobile_dir = Path(__file__).parent
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Initialize monitors
        self.monitors = {}
        self.monitoring_active = False
        self.monitor_threads = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup routes and socket handlers
        self.setup_routes()
        self.setup_socket_handlers()
        
        # Initialize monitoring services
        self.initialize_monitors()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            # Check authentication if auth token is provided
            if self.auth_token:
                provided_auth = request.args.get('auth')
                if provided_auth != self.auth_token:
                    return "Access denied: Invalid or missing authentication token", 403
            
            return render_template_string(self.get_dashboard_template())
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            return jsonify({
                'status': 'active',
                'monitoring': self.monitoring_active,
                'monitors': list(self.monitors.keys()),
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            })
        
        @self.app.route('/api/execute', methods=['POST'])
        def api_execute():
            """API endpoint for command execution"""
            try:
                data = request.get_json()
                command = data.get('command', '').strip()
                
                if not command:
                    return jsonify({'error': 'No command provided'}), 400
                
                # Security check - only allow safe commands
                if not self.is_safe_command(command):
                    return jsonify({'error': 'Command not allowed for security reasons'}), 403
                
                result = self.execute_command(command)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/claude-sessions')
        def api_claude_sessions():
            """API endpoint for Claude session data"""
            try:
                sessions = self.get_claude_sessions()
                return jsonify({'sessions': sessions, 'timestamp': datetime.now().isoformat()})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/git-status')
        def api_git_status():
            """API endpoint for Git status"""
            try:
                git_data = self.get_git_status()
                return jsonify({'git': git_data, 'timestamp': datetime.now().isoformat()})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def setup_socket_handlers(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            self.logger.info(f"Client connected: {session_id}")
            
            # Send initial data
            emit('system_status', {
                'status': 'connected',
                'session_id': session_id,
                'monitoring_active': self.monitoring_active,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            session_id = session.get('session_id', 'unknown')
            self.logger.info(f"Client disconnected: {session_id}")
        
        @self.socketio.on('start_monitoring')
        def handle_start_monitoring():
            """Start real-time monitoring"""
            self.start_monitoring()
            emit('monitoring_status', {'active': True, 'timestamp': datetime.now().isoformat()})
        
        @self.socketio.on('stop_monitoring')
        def handle_stop_monitoring():
            """Stop real-time monitoring"""
            self.stop_monitoring()
            emit('monitoring_status', {'active': False, 'timestamp': datetime.now().isoformat()})
        
        @self.socketio.on('execute_command')
        def handle_execute_command(data):
            """Handle command execution via WebSocket"""
            try:
                command = data.get('command', '').strip()
                if not command:
                    emit('command_error', {'error': 'No command provided'})
                    return
                
                if not self.is_safe_command(command):
                    emit('command_error', {'error': 'Command not allowed for security reasons'})
                    return
                
                result = self.execute_command(command)
                emit('command_result', result)
                
            except Exception as e:
                emit('command_error', {'error': str(e)})
        
        @self.socketio.on('request_data')
        def handle_request_data(data):
            """Handle specific data requests"""
            data_type = data.get('type')
            
            try:
                if data_type == 'claude_sessions':
                    sessions = self.get_claude_sessions()
                    emit('claude_sessions', sessions)
                elif data_type == 'git_status':
                    git_data = self.get_git_status()
                    emit('git_activity', git_data)
                elif data_type == 'system_metrics':
                    metrics = self.get_system_metrics()
                    emit('system_metrics', metrics)
                elif data_type == 'file_changes':
                    changes = self.get_recent_file_changes()
                    emit('file_changes', changes)
                else:
                    emit('data_error', {'error': f'Unknown data type: {data_type}'})
            except Exception as e:
                emit('data_error', {'error': str(e)})
    
    def initialize_monitors(self):
        """Initialize monitoring services"""
        try:
            # Import monitors.py if it exists
            monitors_file = self.mobile_dir / 'monitors.py'
            if monitors_file.exists():
                spec = importlib.util.spec_from_file_location("monitors", monitors_file)
                monitors_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(monitors_module)
                
                # Initialize monitor manager
                if hasattr(monitors_module, 'MonitorManager'):
                    self.monitor_manager = monitors_module.MonitorManager()
                    safe_print("✅ Monitor Manager initialized")
                else:
                    self.monitor_manager = None
                    safe_print("⚠️ MonitorManager not found in monitors.py")
            else:
                self.monitor_manager = None
                safe_print("⚠️ monitors.py not found - using basic monitoring")
        except Exception as e:
            self.logger.error(f"Error initializing monitors: {e}")
            self.monitor_manager = None
    
    def start_monitoring(self):
        """Start real-time monitoring threads"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        safe_print("🔍 Starting real-time monitoring...")
        
        # Start monitoring threads
        self.monitor_threads = {
            'claude_sessions': threading.Thread(target=self.monitor_claude_sessions, daemon=True),
            'git_activity': threading.Thread(target=self.monitor_git_activity, daemon=True),
            'system_metrics': threading.Thread(target=self.monitor_system_metrics, daemon=True),
            'file_changes': threading.Thread(target=self.monitor_file_changes, daemon=True)
        }
        
        for thread in self.monitor_threads.values():
            thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        safe_print("🛑 Stopping real-time monitoring...")
    
    def monitor_claude_sessions(self):
        """Monitor Claude sessions in real-time"""
        while self.monitoring_active:
            try:
                sessions = self.get_claude_sessions()
                self.socketio.emit('claude_sessions', sessions)
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.logger.error(f"Error monitoring Claude sessions: {e}")
                time.sleep(10)
    
    def monitor_git_activity(self):
        """Monitor Git activity in real-time"""
        while self.monitoring_active:
            try:
                git_data = self.get_git_status()
                self.socketio.emit('git_activity', git_data)
                time.sleep(3)  # Update every 3 seconds
            except Exception as e:
                self.logger.error(f"Error monitoring Git activity: {e}")
                time.sleep(10)
    
    def monitor_system_metrics(self):
        """Monitor system metrics in real-time"""
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()
                self.socketio.emit('system_metrics', metrics)
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Error monitoring system metrics: {e}")
                time.sleep(10)
    
    def monitor_file_changes(self):
        """Monitor file changes in real-time"""
        while self.monitoring_active:
            try:
                changes = self.get_recent_file_changes()
                if changes:
                    self.socketio.emit('file_changes', changes)
                time.sleep(1)  # Update every 1 second for responsiveness
            except Exception as e:
                self.logger.error(f"Error monitoring file changes: {e}")
                time.sleep(5)
    
    def get_claude_sessions(self) -> List[Dict]:
        """Get active Claude sessions"""
        try:
            if self.monitor_manager and hasattr(self.monitor_manager, 'get_claude_sessions'):
                return self.monitor_manager.get_claude_sessions()
            
            # Fallback implementation
            sessions = []
            sessions_dir = self.claude_dir / 'sessions'
            
            if sessions_dir.exists():
                for session_file in sessions_dir.glob('*.json'):
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        
                        # Extract session info
                        session_info = {
                            'id': session_file.stem,
                            'created': session_data.get('created_at', 'unknown'),
                            'last_updated': session_data.get('updated_at', 'unknown'),
                            'messages': len(session_data.get('messages', [])),
                            'active': self.is_session_active(session_data)
                        }
                        sessions.append(session_info)
                    except Exception as e:
                        self.logger.error(f"Error reading session {session_file}: {e}")
            
            return sorted(sessions, key=lambda x: x.get('last_updated', ''), reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error getting Claude sessions: {e}")
            return []
    
    def is_session_active(self, session_data: Dict) -> bool:
        """Check if a Claude session is active"""
        try:
            last_updated = session_data.get('updated_at')
            if not last_updated:
                return False
            
            # Parse timestamp and check if updated within last hour
            from dateutil import parser
            update_time = parser.parse(last_updated)
            now = datetime.now(update_time.tzinfo)
            return (now - update_time).total_seconds() < 3600
        except:
            return False
    
    def get_git_status(self) -> Dict:
        """Get Git repository status"""
        try:
            if self.monitor_manager and hasattr(self.monitor_manager, 'get_git_status'):
                return self.monitor_manager.get_git_status()
            
            # Fallback implementation
            git_data = {
                'status': 'unknown',
                'branch': 'unknown',
                'commits': [],
                'changes': []
            }
            
            try:
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    git_data['branch'] = result.stdout.strip()
                
                # Get recent commits
                result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    commits = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(' ', 1)
                            if len(parts) == 2:
                                commits.append({
                                    'hash': parts[0],
                                    'message': parts[1]
                                })
                    git_data['commits'] = commits
                
                # Get status
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    changes = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            status = line[:2]
                            filename = line[3:]
                            changes.append({
                                'status': status,
                                'file': filename
                            })
                    git_data['changes'] = changes
                    git_data['status'] = 'clean' if not changes else 'modified'
                
            except subprocess.TimeoutExpired:
                git_data['status'] = 'timeout'
            except Exception as e:
                git_data['status'] = f'error: {str(e)}'
            
            return git_data
        
        except Exception as e:
            self.logger.error(f"Error getting Git status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_system_metrics(self) -> Dict:
        """Get system performance metrics"""
        try:
            if self.monitor_manager and hasattr(self.monitor_manager, 'get_system_metrics'):
                return self.monitor_manager.get_system_metrics()
            
            # Fallback implementation using psutil
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('/')._asdict(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add process information
            claude_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'claude' in proc.info['name'].lower():
                        claude_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            metrics['claude_processes'] = claude_processes
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    def get_recent_file_changes(self) -> List[Dict]:
        """Get recent file changes"""
        try:
            if self.monitor_manager and hasattr(self.monitor_manager, 'get_recent_file_changes'):
                return self.monitor_manager.get_recent_file_changes()
            
            # Fallback implementation - check modification times
            changes = []
            now = time.time()
            
            # Check current directory and subdirectories
            for root, dirs, files in os.walk('.'):
                # Skip hidden directories and common build/cache dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = Path(root) / file
                    try:
                        mtime = file_path.stat().st_mtime
                        if now - mtime < 60:  # Modified in last minute
                            changes.append({
                                'file': str(file_path),
                                'modified': datetime.fromtimestamp(mtime).isoformat(),
                                'size': file_path.stat().st_size
                            })
                    except (OSError, PermissionError):
                        pass
            
            return sorted(changes, key=lambda x: x['modified'], reverse=True)[:10]
        
        except Exception as e:
            self.logger.error(f"Error getting file changes: {e}")
            return []
    
    def is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Only allow specific safe commands
        safe_commands = [
            'git status', 'git log', 'git branch', 'git diff',
            'ls', 'dir', 'pwd', 'cd', 'echo',
            'python --version', 'pip list', 'npm --version',
            'claude --version', 'code --version'
        ]
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm ', 'del ', 'format', 'shutdown', 'reboot',
            'sudo', 'su ', '>', '>>', '|', '&', ';',
            'curl', 'wget', 'chmod', 'chown'
        ]
        
        command_lower = command.lower()
        
        # Check if it's in safe commands or starts with safe prefixes
        for safe_cmd in safe_commands:
            if command_lower.startswith(safe_cmd.lower()):
                return True
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False
        
        return False  # Default to not safe
    
    def execute_command(self, command: str) -> Dict:
        """Execute a safe command and return result"""
        try:
            start_time = time.time()
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10,
                cwd=os.getcwd()
            )
            
            execution_time = time.time() - start_time
            
            return {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
        
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'error': 'Command timed out',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'command': command,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_dashboard_template(self) -> str:
        """Get the complete dashboard HTML template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code V3+ Real-Time Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-bar {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            margin: 5px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active { background: #4CAF50; }
        .status-inactive { background: #f44336; }
        .status-warning { background: #ff9800; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .card-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        
        .card-content {
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s ease;
        }
        
        .command-input {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: opacity 0.3s ease;
        }
        
        .btn:hover {
            opacity: 0.9;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .output {
            background: #1a1a1a;
            color: #00ff00;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 10px;
        }
        
        .session-item, .commit-item, .file-item {
            padding: 8px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        
        .session-active {
            border-left-color: #4CAF50;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        .error {
            color: #f44336;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .status-bar {
                flex-direction: column;
                text-align: center;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Claude Code V3+ Dashboard</h1>
            <p>Real-Time Monitoring for Samsung Galaxy S25 Edge</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator status-inactive" id="connection-status"></div>
                <span id="connection-text">Connecting...</span>
            </div>
            <div class="status-item">
                <div class="status-indicator status-inactive" id="monitoring-status"></div>
                <span id="monitoring-text">Monitoring Stopped</span>
            </div>
            <div class="status-item">
                <button class="btn" id="monitoring-toggle">Start Monitoring</button>
            </div>
            <div class="status-item">
                <span id="last-update">Last Update: Never</span>
            </div>
        </div>
        
        <div class="grid">
            <!-- Claude Sessions Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📝 Claude Sessions</h3>
                </div>
                <div class="card-content" id="claude-sessions">
                    <div class="loading">Loading sessions...</div>
                </div>
            </div>
            
            <!-- Git Activity Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🔧 Git Activity</h3>
                </div>
                <div class="card-content" id="git-activity">
                    <div class="loading">Loading git status...</div>
                </div>
            </div>
            
            <!-- System Metrics Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📊 System Metrics</h3>
                </div>
                <div class="card-content" id="system-metrics">
                    <div class="loading">Loading system metrics...</div>
                </div>
            </div>
            
            <!-- File Changes Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📁 Recent File Changes</h3>
                </div>
                <div class="card-content" id="file-changes">
                    <div class="loading">Loading file changes...</div>
                </div>
            </div>
            
            <!-- Command Execution Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">💻 Command Execution</h3>
                </div>
                <div class="card-content">
                    <input type="text" class="command-input" id="command-input" placeholder="Enter safe command (e.g., git status)" />
                    <button class="btn" id="execute-btn">Execute</button>
                    <div class="output" id="command-output">Ready to execute commands...</div>
                </div>
            </div>
            
            <!-- Terminal Access Card -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🖥️ Terminal Access</h3>
                </div>
                <div class="card-content">
                    <p>Access the terminal directly in your browser:</p>
                    <button class="btn" id="terminal-btn" onclick="openTerminal()">Open Terminal (Port 7681)</button>
                    <p class="timestamp">Terminal access via ttyd</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        let monitoringActive = false;
        
        // DOM elements
        const connectionStatus = document.getElementById('connection-status');
        const connectionText = document.getElementById('connection-text');
        const monitoringStatus = document.getElementById('monitoring-status');
        const monitoringText = document.getElementById('monitoring-text');
        const monitoringToggle = document.getElementById('monitoring-toggle');
        const lastUpdate = document.getElementById('last-update');
        const executeBtn = document.getElementById('execute-btn');
        const commandInput = document.getElementById('command-input');
        const commandOutput = document.getElementById('command-output');
        
        // Socket event handlers
        socket.on('connect', function() {
            connectionStatus.className = 'status-indicator status-active';
            connectionText.textContent = 'Connected';
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            connectionStatus.className = 'status-indicator status-inactive';
            connectionText.textContent = 'Disconnected';
            console.log('Disconnected from server');
        });
        
        socket.on('system_status', function(data) {
            console.log('System status:', data);
            updateLastUpdate();
        });
        
        socket.on('monitoring_status', function(data) {
            monitoringActive = data.active;
            updateMonitoringStatus();
        });
        
        socket.on('claude_sessions', function(data) {
            updateClaudeSessions(data);
            updateLastUpdate();
        });
        
        socket.on('git_activity', function(data) {
            updateGitActivity(data);
            updateLastUpdate();
        });
        
        socket.on('system_metrics', function(data) {
            updateSystemMetrics(data);
            updateLastUpdate();
        });
        
        socket.on('file_changes', function(data) {
            updateFileChanges(data);
            updateLastUpdate();
        });
        
        socket.on('command_result', function(data) {
            displayCommandResult(data);
        });
        
        socket.on('command_error', function(data) {
            displayCommandError(data);
        });
        
        // Event listeners
        monitoringToggle.addEventListener('click', function() {
            if (monitoringActive) {
                socket.emit('stop_monitoring');
            } else {
                socket.emit('start_monitoring');
            }
        });
        
        executeBtn.addEventListener('click', function() {
            executeCommand();
        });
        
        commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
        
        // Update functions
        function updateMonitoringStatus() {
            if (monitoringActive) {
                monitoringStatus.className = 'status-indicator status-active';
                monitoringText.textContent = 'Monitoring Active';
                monitoringToggle.textContent = 'Stop Monitoring';
            } else {
                monitoringStatus.className = 'status-indicator status-inactive';
                monitoringText.textContent = 'Monitoring Stopped';
                monitoringToggle.textContent = 'Start Monitoring';
            }
        }
        
        function updateLastUpdate() {
            const now = new Date();
            lastUpdate.textContent = `Last Update: ${now.toLocaleTimeString()}`;
        }
        
        function updateClaudeSessions(sessions) {
            const container = document.getElementById('claude-sessions');
            
            if (!sessions || sessions.length === 0) {
                container.innerHTML = '<div class="loading">No active sessions found</div>';
                return;
            }
            
            let html = '';
            sessions.forEach(session => {
                const activeClass = session.active ? 'session-active' : '';
                html += `
                    <div class="session-item ${activeClass}">
                        <strong>Session: ${session.id}</strong><br>
                        <small>Messages: ${session.messages}</small><br>
                        <small class="timestamp">Updated: ${session.last_updated}</small>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function updateGitActivity(data) {
            const container = document.getElementById('git-activity');
            
            if (data.error) {
                container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                return;
            }
            
            let html = `
                <div class="metric">
                    <span>Branch:</span>
                    <span><strong>${data.branch || 'unknown'}</strong></span>
                </div>
                <div class="metric">
                    <span>Status:</span>
                    <span><strong>${data.status || 'unknown'}</strong></span>
                </div>
            `;
            
            if (data.commits && data.commits.length > 0) {
                html += '<h4>Recent Commits:</h4>';
                data.commits.forEach(commit => {
                    html += `
                        <div class="commit-item">
                            <strong>${commit.hash}</strong><br>
                            <small>${commit.message}</small>
                        </div>
                    `;
                });
            }
            
            if (data.changes && data.changes.length > 0) {
                html += '<h4>Changes:</h4>';
                data.changes.forEach(change => {
                    html += `
                        <div class="file-item">
                            <strong>${change.status}</strong> ${change.file}
                        </div>
                    `;
                });
            }
            
            container.innerHTML = html;
        }
        
        function updateSystemMetrics(data) {
            const container = document.getElementById('system-metrics');
            
            if (data.error) {
                container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                return;
            }
            
            let html = `
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span><strong>${data.cpu_percent?.toFixed(1) || 'N/A'}%</strong></span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.cpu_percent || 0}%"></div>
                </div>
            `;
            
            if (data.memory) {
                const memoryPercent = (data.memory.used / data.memory.total * 100).toFixed(1);
                html += `
                    <div class="metric">
                        <span>Memory Usage:</span>
                        <span><strong>${memoryPercent}%</strong></span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${memoryPercent}%"></div>
                    </div>
                `;
            }
            
            if (data.claude_processes && data.claude_processes.length > 0) {
                html += '<h4>Claude Processes:</h4>';
                data.claude_processes.forEach(proc => {
                    html += `
                        <div class="metric">
                            <span>${proc.name} (${proc.pid})</span>
                            <span>CPU: ${proc.cpu_percent?.toFixed(1) || 'N/A'}%</span>
                        </div>
                    `;
                });
            }
            
            container.innerHTML = html;
        }
        
        function updateFileChanges(changes) {
            const container = document.getElementById('file-changes');
            
            if (!changes || changes.length === 0) {
                container.innerHTML = '<div class="loading">No recent changes</div>';
                return;
            }
            
            let html = '';
            changes.forEach(change => {
                html += `
                    <div class="file-item">
                        <strong>${change.file}</strong><br>
                        <small class="timestamp">Modified: ${new Date(change.modified).toLocaleString()}</small><br>
                        <small>Size: ${change.size} bytes</small>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function executeCommand() {
            const command = commandInput.value.trim();
            if (!command) return;
            
            executeBtn.disabled = true;
            commandOutput.textContent = 'Executing command...';
            
            socket.emit('execute_command', { command: command });
            
            setTimeout(() => {
                executeBtn.disabled = false;
            }, 2000);
        }
        
        function displayCommandResult(data) {
            let output = `Command: ${data.command}\n`;
            output += `Return Code: ${data.returncode}\n`;
            output += `Execution Time: ${data.execution_time?.toFixed(2) || 'N/A'}s\n\n`;
            
            if (data.stdout) {
                output += `STDOUT:\n${data.stdout}\n\n`;
            }
            
            if (data.stderr) {
                output += `STDERR:\n${data.stderr}\n`;
            }
            
            commandOutput.textContent = output;
            commandInput.value = '';
        }
        
        function displayCommandError(data) {
            commandOutput.textContent = `Error: ${data.error}`;
        }
        
        function openTerminal() {
            // Get the current host and replace the port
            const currentHost = window.location.hostname;
            const terminalUrl = `http://${currentHost}:7681`;
            window.open(terminalUrl, '_blank');
        }
        
        // Initial data requests
        socket.on('connect', function() {
            socket.emit('request_data', { type: 'claude_sessions' });
            socket.emit('request_data', { type: 'git_status' });
            socket.emit('request_data', { type: 'system_metrics' });
            socket.emit('request_data', { type: 'file_changes' });
        });
        
        // Auto-refresh data every 30 seconds when not monitoring
        setInterval(function() {
            if (!monitoringActive) {
                socket.emit('request_data', { type: 'claude_sessions' });
                socket.emit('request_data', { type: 'git_status' });
                socket.emit('request_data', { type: 'system_metrics' });
                socket.emit('request_data', { type: 'file_changes' });
            }
        }, 30000);
    </script>
</body>
</html>
        '''
    
    def run(self):
        """Start the dashboard server"""
        self.start_time = time.time()
        safe_print(f"🚀 Starting Real-Time Dashboard on port {self.port}")
        safe_print(f"🔒 Authentication: {'Enabled' if self.auth_token else 'Disabled'}")
        
        try:
            self.socketio.run(
                self.app, 
                host='0.0.0.0', 
                port=self.port, 
                debug=False,
                allow_unsafe_werkzeug=True
            )
        except Exception as e:
            safe_print(f"❌ Error starting dashboard: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Code V3+ Real-Time Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run dashboard on')
    parser.add_argument('--mobile-auth', type=str, help='Mobile authentication token')
    parser.add_argument('--auth-token', type=str, help='Authentication token')
    
    args = parser.parse_args()
    
    # Get auth token from args or environment
    auth_token = args.mobile_auth or args.auth_token or os.environ.get('CLAUDE_MOBILE_AUTH_TOKEN')
    
    dashboard = RealtimeDashboard(port=args.port, auth_token=auth_token)
    dashboard.run()

if __name__ == '__main__':
    main()