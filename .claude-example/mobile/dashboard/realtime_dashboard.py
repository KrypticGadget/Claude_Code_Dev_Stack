#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code V3+ Real-time Monitoring Dashboard
A complete Flask-SocketIO server with embedded responsive UI for monitoring
Claude sessions, git activity, file changes, and system metrics.
"""

import os
import sys
import json
import time
import psutil
import threading
import subprocess
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional

# Flask and SocketIO imports
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

# Windows Unicode support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    # Windows console encoding fix
    try:
        import win32console
        win32console.SetConsoleOutputCP(65001)  # UTF-8
    except ImportError:
        os.system('chcp 65001 > nul')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'claude-code-v3-dashboard-2025'
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    async_mode='threading'
)

# Global data stores
claude_sessions = deque(maxlen=100)
git_activities = deque(maxlen=50)
file_changes = deque(maxlen=100)
system_metrics_history = deque(maxlen=60)  # 2 minutes of data
connected_clients = set()
command_history = deque(maxlen=50)

class DashboardData:
    """Centralized data management for the dashboard"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.working_directory = os.getcwd()
        self.is_git_repo = self._check_git_repo()
        
    def _check_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(['git', 'status'], 
                         capture_output=True, check=True, cwd=self.working_directory)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_claude_sessions(self) -> List[Dict[str, Any]]:
        """Get mock Claude sessions data"""
        current_time = datetime.now()
        
        # Simulate active sessions
        sessions = [
            {
                'id': f'session_{i}',
                'status': 'active' if i < 3 else 'idle',
                'model': 'claude-sonnet-4-20250514' if i % 2 == 0 else 'claude-haiku-3.5',
                'tokens_used': 15000 + (i * 2500),
                'max_tokens': 200000,
                'start_time': (current_time - timedelta(minutes=30 + i * 10)).isoformat(),
                'last_activity': (current_time - timedelta(minutes=i * 2)).isoformat(),
                'current_task': f'Backend Services Engineering - Task {i + 1}',
                'files_modified': i + 1,
                'tools_used': ['Read', 'Write', 'Edit', 'Bash'][:i + 1]
            }
            for i in range(5)
        ]
        
        return sessions
    
    def get_git_activity(self) -> List[Dict[str, Any]]:
        """Get recent git activity"""
        if not self.is_git_repo:
            return []
        
        try:
            # Get recent commits
            result = subprocess.run([
                'git', 'log', '--oneline', '--max-count=10', 
                '--pretty=format:%H|%s|%an|%ad', '--date=iso'
            ], capture_output=True, text=True, cwd=self.working_directory)
            
            activities = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) == 4:
                            activities.append({
                                'type': 'commit',
                                'hash': parts[0][:8],
                                'message': parts[1],
                                'author': parts[2],
                                'timestamp': parts[3]
                            })
            
            # Get current branch and status
            branch_result = subprocess.run([
                'git', 'branch', '--show-current'
            ], capture_output=True, text=True, cwd=self.working_directory)
            
            status_result = subprocess.run([
                'git', 'status', '--porcelain'
            ], capture_output=True, text=True, cwd=self.working_directory)
            
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'main'
            modified_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            return {
                'current_branch': current_branch,
                'modified_files': modified_files,
                'recent_commits': activities[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting git activity: {e}")
            return {'current_branch': 'unknown', 'modified_files': 0, 'recent_commits': []}
    
    def get_file_changes(self) -> List[Dict[str, Any]]:
        """Monitor recent file changes in the working directory"""
        changes = []
        try:
            # Get recently modified files
            for root, dirs, files in os.walk(self.working_directory):
                # Skip .git and node_modules directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        modified_time = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Only include files modified in the last 24 hours
                        if modified_time > datetime.now() - timedelta(hours=24):
                            relative_path = os.path.relpath(file_path, self.working_directory)
                            changes.append({
                                'file': relative_path,
                                'type': self._get_file_type(file),
                                'size': stat.st_size,
                                'modified': modified_time.isoformat(),
                                'action': 'modified'
                            })
                    except (OSError, PermissionError):
                        continue
            
            # Sort by modification time, most recent first
            changes.sort(key=lambda x: x['modified'], reverse=True)
            return changes[:20]  # Return latest 20 changes
            
        except Exception as e:
            logger.error(f"Error getting file changes: {e}")
            return []
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = os.path.splitext(filename)[1].lower()
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'sass',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql'
        }
        return type_map.get(ext, 'unknown')
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(self.working_directory)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'cores': psutil.cpu_count()
                },
                'memory': {
                    'percent': round(memory.percent, 1),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2)
                },
                'disk': {
                    'percent': round(disk.percent, 1),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2)
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'processes': process_count,
                'uptime': str(datetime.now() - self.start_time).split('.')[0]
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {'percent': 0, 'cores': 1},
                'memory': {'percent': 0, 'used_gb': 0, 'total_gb': 0, 'available_gb': 0},
                'disk': {'percent': 0, 'used_gb': 0, 'total_gb': 0, 'free_gb': 0},
                'network': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0},
                'processes': 0,
                'uptime': '00:00:00'
            }

# Initialize dashboard data
dashboard_data = DashboardData()

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code V3+ Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.min.js"></script>
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
            overflow-x: hidden;
        }
        
        .dashboard {
            min-height: 100vh;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            grid-gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .card-title {
            font-size: 1.4em;
            font-weight: 600;
            color: #2c3e50;
            margin-left: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-active { background-color: #2ecc71; }
        .status-idle { background-color: #f39c12; }
        .status-error { background-color: #e74c3c; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .terminal-container {
            grid-column: 1 / -1;
            min-height: 400px;
        }
        
        .terminal-iframe {
            width: 100%;
            height: 400px;
            border: none;
            border-radius: 10px;
            background: #1a1a1a;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .metric-item {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 10px;
            border: 1px solid #dee2e6;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #495057;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .session-item, .activity-item, .file-item {
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            transition: background-color 0.3s ease;
        }
        
        .session-item:hover, .activity-item:hover, .file-item:hover {
            background: #e9ecef;
        }
        
        .session-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .session-id {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .session-model {
            font-size: 0.85em;
            background: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 8px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            transition: width 0.3s ease;
        }
        
        .command-input {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .command-input input {
            flex: 1;
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .command-input input:focus {
            border-color: #007bff;
        }
        
        .command-input button {
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }
        
        .command-input button:hover {
            background: #0056b3;
        }
        
        .log-container {
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .log-entry {
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .log-entry:last-child {
            border-bottom: none;
        }
        
        .timestamp {
            color: #6c757d;
            font-size: 0.8em;
        }
        
        .chart-container {
            position: relative;
            height: 200px;
            margin-top: 15px;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .connected {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .disconnected {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 10px;
                grid-gap: 15px;
            }
            
            .card {
                padding: 20px;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .terminal-container {
                grid-column: 1;
            }
        }
        
        .icon {
            width: 20px;
            height: 20px;
            fill: currentColor;
        }
        
        .file-type-python { border-left-color: #3776ab; }
        .file-type-javascript { border-left-color: #f7df1e; }
        .file-type-typescript { border-left-color: #3178c6; }
        .file-type-react { border-left-color: #61dafb; }
        .file-type-html { border-left-color: #e34f26; }
        .file-type-css { border-left-color: #1572b6; }
        .file-type-json { border-left-color: #000000; }
        .file-type-markdown { border-left-color: #083fa1; }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">
        <span class="status-indicator status-active"></span>
        Connecting...
    </div>
    
    <div class="dashboard">
        <!-- Terminal Access -->
        <div class="card terminal-container">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M20,19V7H4V19H20M20,3A2,2 0 0,1 22,5V19A2,2 0 0,1 20,21H4A2,2 0 0,1 2,19V5A2,2 0 0,1 4,3H20M13,17V15H18V17H13M9.58,13L5.57,9H8.4L11.7,12.3C12.09,12.69 12.09,13.33 11.7,13.72L8.42,17H5.59L9.58,13Z"/>
                </svg>
                <h2 class="card-title">Terminal Access</h2>
            </div>
            <iframe src="http://localhost:7681" class="terminal-iframe" title="Terminal"></iframe>
        </div>
        
        <!-- Claude Sessions -->
        <div class="card">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H14A7,7 0 0,1 21,14H22A1,1 0 0,1 23,15V18A1,1 0 0,1 22,19H21V20A2,2 0 0,1 19,22H5A2,2 0 0,1 3,20V19H2A1,1 0 0,1 1,18V15A1,1 0 0,1 2,14H3A7,7 0 0,1 10,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M7.5,13A2.5,2.5 0 0,0 5,15.5A2.5,2.5 0 0,0 7.5,18A2.5,2.5 0 0,0 10,15.5A2.5,2.5 0 0,0 7.5,13M16.5,13A2.5,2.5 0 0,0 14,15.5A2.5,2.5 0 0,0 16.5,18A2.5,2.5 0 0,0 19,15.5A2.5,2.5 0 0,0 16.5,13Z"/>
                </svg>
                <h2 class="card-title">Claude Sessions</h2>
            </div>
            <div id="claudeSessions"></div>
        </div>
        
        <!-- Git Activity -->
        <div class="card">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M2.6,10.59L8.38,4.8L10.07,6.5C9.83,7.35 10.22,8.28 11,8.73V14.27C10.4,14.61 10,15.26 10,16A2,2 0 0,0 12,18A2,2 0 0,0 14,16C14,15.26 13.6,14.61 13,14.27V9.41L15.07,11.5C15,11.65 15,11.82 15,12A2,2 0 0,0 17,14A2,2 0 0,0 19,12A2,2 0 0,0 17,10C16.82,10 16.65,10 16.5,10.07L13.93,7.5C14.19,6.57 13.71,5.55 12.78,5.16C11.85,4.77 10.83,5.25 10.44,6.18C10.05,7.11 10.53,8.13 11.46,8.52C11.64,8.6 11.82,8.65 12,8.65V9.41L9.93,7.35C10.19,6.57 9.71,5.55 8.78,5.16C7.85,4.77 6.83,5.25 6.44,6.18C6.05,7.11 6.53,8.13 7.46,8.52C7.64,8.6 7.82,8.65 8,8.65C8.18,8.65 8.36,8.6 8.54,8.52L2.6,10.59Z"/>
                </svg>
                <h2 class="card-title">Git Activity</h2>
            </div>
            <div id="gitActivity"></div>
        </div>
        
        <!-- File Changes -->
        <div class="card">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M13,9V3.5L18.5,9M6,2C4.89,2 4,2.89 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2H6Z"/>
                </svg>
                <h2 class="card-title">File Changes</h2>
            </div>
            <div id="fileChanges"></div>
        </div>
        
        <!-- System Metrics -->
        <div class="card">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M13,2.05V5.08C16.39,5.57 19,8.47 19,12C19,12.9 18.82,13.75 18.5,14.54L21.12,16.07C21.68,14.83 22,13.45 22,12C22,6.82 18.05,2.55 13,2.05M12,19C8.47,19 5.57,16.39 5.08,13H2.05C2.55,18.05 6.82,22 12,22C13.45,22 14.83,21.68 16.07,21.12L14.54,18.5C13.75,18.82 12.9,19 12,19M2.05,11H5.08C5.57,7.61 8.47,5 12,5C12.9,5 13.75,5.18 14.54,5.5L16.07,2.88C14.83,2.32 13.45,2 12,2C6.82,2 2.55,6.95 2.05,11Z"/>
                </svg>
                <h2 class="card-title">System Metrics</h2>
            </div>
            <div class="metrics-grid" id="systemMetrics"></div>
            <div class="chart-container">
                <canvas id="metricsChart"></canvas>
            </div>
        </div>
        
        <!-- Command Execution -->
        <div class="card">
            <div class="card-header">
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M20,4C21.11,4 22,4.89 22,6V18C22,19.11 21.11,20 20,20H4C2.89,20 2,19.11 2,18V6C2,4.89 2.89,4 4,4H20M13,17V15H18V17H13M9.58,13L5.57,9H8.4L11.7,12.3C12.09,12.69 12.09,13.33 11.7,13.72L8.42,17H5.59L9.58,13Z"/>
                </svg>
                <h2 class="card-title">Command Execution</h2>
            </div>
            <div class="command-input">
                <input type="text" id="commandInput" placeholder="Enter command..." />
                <button onclick="executeCommand()">Execute</button>
            </div>
            <div class="log-container" id="commandLog"></div>
        </div>
    </div>

    <script>
        // Initialize SocketIO connection
        const socket = io();
        
        // Chart instance for metrics
        let metricsChart;
        
        // Data stores
        let metricsHistory = [];
        
        // Connection status
        const connectionStatus = document.getElementById('connectionStatus');
        
        socket.on('connect', function() {
            console.log('Connected to server');
            connectionStatus.innerHTML = '<span class="status-indicator status-active"></span>Connected';
            connectionStatus.className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            connectionStatus.innerHTML = '<span class="status-indicator status-error"></span>Disconnected';
            connectionStatus.className = 'connection-status disconnected';
        });
        
        // Claude Sessions handler
        socket.on('claude_sessions', function(data) {
            const container = document.getElementById('claudeSessions');
            container.innerHTML = '';
            
            data.sessions.forEach(session => {
                const sessionDiv = document.createElement('div');
                sessionDiv.className = 'session-item';
                
                const tokensUsed = ((session.tokens_used / session.max_tokens) * 100).toFixed(1);
                
                sessionDiv.innerHTML = `
                    <div class="session-header">
                        <span class="session-id">${session.id}</span>
                        <span class="session-model">${session.model.split('-').pop()}</span>
                    </div>
                    <div>Status: <span class="status-indicator status-${session.status}"></span>${session.status}</div>
                    <div>Task: ${session.current_task}</div>
                    <div>Tokens: ${session.tokens_used.toLocaleString()} / ${session.max_tokens.toLocaleString()}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${tokensUsed}%"></div>
                    </div>
                    <div>Files modified: ${session.files_modified}</div>
                    <div>Tools: ${session.tools_used.join(', ')}</div>
                `;
                
                container.appendChild(sessionDiv);
            });
        });
        
        // Git Activity handler
        socket.on('git_activity', function(data) {
            const container = document.getElementById('gitActivity');
            container.innerHTML = '';
            
            // Current status
            const statusDiv = document.createElement('div');
            statusDiv.className = 'activity-item';
            statusDiv.innerHTML = `
                <div><strong>Current Branch:</strong> ${data.current_branch}</div>
                <div><strong>Modified Files:</strong> ${data.modified_files}</div>
            `;
            container.appendChild(statusDiv);
            
            // Recent commits
            if (data.recent_commits && data.recent_commits.length > 0) {
                data.recent_commits.forEach(commit => {
                    const commitDiv = document.createElement('div');
                    commitDiv.className = 'activity-item';
                    commitDiv.innerHTML = `
                        <div><strong>${commit.hash}</strong> - ${commit.message}</div>
                        <div class="timestamp">by ${commit.author} on ${new Date(commit.timestamp).toLocaleString()}</div>
                    `;
                    container.appendChild(commitDiv);
                });
            }
        });
        
        // File Changes handler
        socket.on('file_changes', function(data) {
            const container = document.getElementById('fileChanges');
            container.innerHTML = '';
            
            data.changes.slice(0, 10).forEach(change => {
                const fileDiv = document.createElement('div');
                fileDiv.className = `file-item file-type-${change.type}`;
                
                const fileSize = (change.size / 1024).toFixed(1);
                const modifiedTime = new Date(change.modified).toLocaleString();
                
                fileDiv.innerHTML = `
                    <div><strong>${change.file}</strong></div>
                    <div>Type: ${change.type} | Size: ${fileSize} KB</div>
                    <div class="timestamp">Modified: ${modifiedTime}</div>
                `;
                
                container.appendChild(fileDiv);
            });
        });
        
        // System Metrics handler
        socket.on('system_metrics', function(data) {
            updateSystemMetrics(data);
            updateMetricsChart(data);
        });
        
        function updateSystemMetrics(metrics) {
            const container = document.getElementById('systemMetrics');
            container.innerHTML = `
                <div class="metric-item">
                    <div class="metric-value">${metrics.cpu.percent}%</div>
                    <div class="metric-label">CPU</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.memory.percent}%</div>
                    <div class="metric-label">Memory</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.disk.percent}%</div>
                    <div class="metric-label">Disk</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.processes}</div>
                    <div class="metric-label">Processes</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.memory.used_gb}GB</div>
                    <div class="metric-label">RAM Used</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.uptime}</div>
                    <div class="metric-label">Uptime</div>
                </div>
            `;
        }
        
        function updateMetricsChart(metrics) {
            metricsHistory.push({
                timestamp: new Date(metrics.timestamp),
                cpu: metrics.cpu.percent,
                memory: metrics.memory.percent,
                disk: metrics.disk.percent
            });
            
            // Keep last 30 data points
            if (metricsHistory.length > 30) {
                metricsHistory.shift();
            }
            
            if (!metricsChart) {
                const ctx = document.getElementById('metricsChart').getContext('2d');
                metricsChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [
                            {
                                label: 'CPU %',
                                data: [],
                                borderColor: '#007bff',
                                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                                tension: 0.4
                            },
                            {
                                label: 'Memory %',
                                data: [],
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                tension: 0.4
                            },
                            {
                                label: 'Disk %',
                                data: [],
                                borderColor: '#ffc107',
                                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                                tension: 0.4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top'
                            }
                        }
                    }
                });
            }
            
            // Update chart data
            metricsChart.data.labels = metricsHistory.map(m => 
                m.timestamp.toLocaleTimeString()
            );
            metricsChart.data.datasets[0].data = metricsHistory.map(m => m.cpu);
            metricsChart.data.datasets[1].data = metricsHistory.map(m => m.memory);
            metricsChart.data.datasets[2].data = metricsHistory.map(m => m.disk);
            metricsChart.update('none');
        }
        
        // Command execution
        function executeCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            
            if (command) {
                socket.emit('execute_command', { command: command });
                
                // Add to log
                addToCommandLog(`> ${command}`, 'command');
                input.value = '';
            }
        }
        
        // Command result handler
        socket.on('command_result', function(data) {
            addToCommandLog(data.output || data.error, data.success ? 'output' : 'error');
        });
        
        function addToCommandLog(message, type) {
            const log = document.getElementById('commandLog');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            entry.innerHTML = `
                <span class="timestamp">[${timestamp}]</span> ${message}
            `;
            
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
            
            // Keep last 50 entries
            while (log.children.length > 50) {
                log.removeChild(log.firstChild);
            }
        }
        
        // Enter key for command input
        document.getElementById('commandInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
        
        console.log('Dashboard initialized');
    </script>
</body>
</html>
"""

# WebSocket Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    logger.info(f"Client connected: {client_id}")
    
    # Send initial data
    emit('claude_sessions', {'sessions': dashboard_data.get_claude_sessions()})
    emit('git_activity', dashboard_data.get_git_activity())
    emit('file_changes', {'changes': dashboard_data.get_file_changes()})
    emit('system_metrics', dashboard_data.get_system_metrics())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    connected_clients.discard(client_id)
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('execute_command')
def handle_execute_command(data):
    """Handle command execution requests"""
    command = data.get('command', '').strip()
    client_id = request.sid
    
    if not command:
        emit('command_result', {
            'success': False,
            'error': 'Empty command',
            'command': command
        })
        return
    
    logger.info(f"Executing command from client {client_id}: {command}")
    
    try:
        # Security: Only allow safe commands
        allowed_commands = [
            'git', 'ls', 'dir', 'pwd', 'whoami', 'date', 'echo', 
            'python', 'node', 'npm', 'pip', 'poetry', 'docker'
        ]
        
        command_parts = command.split()
        if command_parts and command_parts[0] not in allowed_commands:
            emit('command_result', {
                'success': False,
                'error': f'Command not allowed: {command_parts[0]}',
                'command': command
            })
            return
        
        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=dashboard_data.working_directory,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Store command in history
        command_history.append({
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
        
        # Send result back to client
        emit('command_result', {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'command': command,
            'return_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        emit('command_result', {
            'success': False,
            'error': 'Command timed out (30s limit)',
            'command': command
        })
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        emit('command_result', {
            'success': False,
            'error': str(e),
            'command': command
        })

# Periodic data emission functions
def emit_claude_sessions():
    """Emit Claude sessions data every 3 seconds"""
    while True:
        try:
            if connected_clients:
                sessions_data = {'sessions': dashboard_data.get_claude_sessions()}
                socketio.emit('claude_sessions', sessions_data)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Error emitting Claude sessions: {e}")
            time.sleep(3)

def emit_git_activity():
    """Emit git activity data every 5 seconds"""
    while True:
        try:
            if connected_clients:
                git_data = dashboard_data.get_git_activity()
                socketio.emit('git_activity', git_data)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error emitting git activity: {e}")
            time.sleep(5)

def emit_file_changes():
    """Emit file changes data every 10 seconds"""
    while True:
        try:
            if connected_clients:
                file_data = {'changes': dashboard_data.get_file_changes()}
                socketio.emit('file_changes', file_data)
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error emitting file changes: {e}")
            time.sleep(10)

def emit_system_metrics():
    """Emit system metrics every 2 seconds"""
    while True:
        try:
            if connected_clients:
                metrics_data = dashboard_data.get_system_metrics()
                system_metrics_history.append(metrics_data)
                socketio.emit('system_metrics', metrics_data)
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error emitting system metrics: {e}")
            time.sleep(2)

# Flask Routes
@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API endpoint for dashboard status"""
    return jsonify({
        'status': 'running',
        'connected_clients': len(connected_clients),
        'uptime': str(datetime.now() - dashboard_data.start_time).split('.')[0],
        'working_directory': dashboard_data.working_directory,
        'is_git_repo': dashboard_data.is_git_repo
    })

@app.route('/api/command-history')
def api_command_history():
    """API endpoint for command history"""
    return jsonify(list(command_history))

@app.route('/api/metrics-history')
def api_metrics_history():
    """API endpoint for metrics history"""
    return jsonify(list(system_metrics_history))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def start_background_tasks():
    """Start background tasks for data emission"""
    tasks = [
        threading.Thread(target=emit_claude_sessions, daemon=True),
        threading.Thread(target=emit_git_activity, daemon=True),
        threading.Thread(target=emit_file_changes, daemon=True),
        threading.Thread(target=emit_system_metrics, daemon=True),
    ]
    
    for task in tasks:
        task.start()
        logger.info(f"Started background task: {task.name}")

if __name__ == '__main__':
    try:
        # Print startup information
        print("\n" + "="*60)
        print("🚀 Claude Code V3+ Real-time Dashboard")
        print("="*60)
        print(f"📁 Working Directory: {dashboard_data.working_directory}")
        print(f"🔧 Git Repository: {'Yes' if dashboard_data.is_git_repo else 'No'}")
        print(f"🌐 Dashboard URL: http://localhost:5000")
        print(f"💻 Terminal URL: http://localhost:7681")
        print("="*60)
        
        # Start background tasks
        start_background_tasks()
        
        # Start the Flask-SocketIO server
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("Dashboard server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start dashboard server: {e}")
        sys.exit(1)