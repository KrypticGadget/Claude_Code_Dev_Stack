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
    <title>Claude Code V3+ IDE Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            overflow: hidden;
            height: 100vh;
        }
        
        .ide-container {
            display: flex;
            height: 100vh;
            width: 100vw;
        }
        
        .sidebar {
            width: 280px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
            min-width: 240px;
            resize: horizontal;
            overflow: hidden;
        }
        
        .sidebar-tabs {
            display: flex;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            min-height: 35px;
        }
        
        .sidebar-tab {
            padding: 8px 16px;
            background: transparent;
            border: none;
            color: #cccccc;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-size: 13px;
            transition: all 0.2s ease;
        }
        
        .sidebar-tab.active {
            color: #ffffff;
            border-bottom-color: #007acc;
            background: rgba(0, 122, 204, 0.1);
        }
        
        .sidebar-tab:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .toolbar {
            height: 35px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 12px;
        }
        
        .toolbar-button {
            background: transparent;
            border: 1px solid #464647;
            color: #cccccc;
            padding: 4px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
        }
        
        .toolbar-button:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: #6c6c6c;
        }
        
        .search-box {
            flex: 1;
            max-width: 300px;
            padding: 4px 8px;
            background: #3c3c3c;
            border: 1px solid #464647;
            border-radius: 3px;
            color: #cccccc;
            font-size: 13px;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #007acc;
            background: #404040;
        }
        
        .editor-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        .editor-tabs {
            display: flex;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            min-height: 35px;
            overflow-x: auto;
        }
        
        .editor-tab {
            display: flex;
            align-items: center;
            padding: 8px 16px;
            background: transparent;
            border: none;
            color: #cccccc;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-size: 13px;
            white-space: nowrap;
            min-width: 120px;
        }
        
        .editor-tab.active {
            color: #ffffff;
            border-bottom-color: #007acc;
            background: #1e1e1e;
        }
        
        .editor-tab:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .editor-tab .close-btn {
            margin-left: 8px;
            color: #858585;
            font-size: 16px;
            line-height: 1;
        }
        
        .editor-tab .close-btn:hover {
            color: #ffffff;
        }
        
        .editor-pane {
            flex: 1;
            background: #1e1e1e;
            position: relative;
        }
        
        .monaco-editor-container {
            width: 100%;
            height: 100%;
        }
        
        .status-bar {
            height: 22px;
            background: #007acc;
            color: #ffffff;
            display: flex;
            align-items: center;
            padding: 0 16px;
            font-size: 12px;
            gap: 16px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* File Explorer Styles */
        .file-explorer {
            padding: 8px;
        }
        
        .file-tree {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .file-tree-item {
            position: relative;
            margin: 0;
            padding: 0;
        }
        
        .file-tree-node {
            display: flex;
            align-items: center;
            padding: 4px 8px;
            cursor: pointer;
            border-radius: 3px;
            transition: background-color 0.2s ease;
            user-select: none;
            font-size: 13px;
        }
        
        .file-tree-node:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .file-tree-node.selected {
            background: rgba(0, 122, 204, 0.3);
        }
        
        .file-tree-node.modified {
            color: #f0c674;
        }
        
        .file-tree-icon {
            width: 16px;
            height: 16px;
            margin-right: 6px;
            flex-shrink: 0;
        }
        
        .file-tree-expand {
            width: 16px;
            height: 16px;
            margin-right: 2px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2px;
            transition: background-color 0.2s ease;
        }
        
        .file-tree-expand:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .file-tree-expand::after {
            content: '▶';
            font-size: 10px;
            color: #cccccc;
            transition: transform 0.2s ease;
        }
        
        .file-tree-expand.expanded::after {
            transform: rotate(90deg);
        }
        
        .file-tree-children {
            margin-left: 18px;
            border-left: 1px solid #464647;
            padding-left: 8px;
        }
        
        .file-tree-children.collapsed {
            display: none;
        }
        
        /* Git Panel Styles */
        .git-panel {
            padding: 16px;
        }
        
        .git-status {
            margin-bottom: 16px;
            padding: 12px;
            background: #2d2d30;
            border-radius: 4px;
            border-left: 3px solid #007acc;
        }
        
        .git-branch {
            font-weight: 600;
            color: #4ec9b0;
            margin-bottom: 4px;
        }
        
        .git-changes {
            font-size: 12px;
            color: #cccccc;
        }
        
        .git-file-changes {
            margin-top: 16px;
        }
        
        .git-file-change {
            display: flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 3px;
            margin: 2px 0;
            font-size: 13px;
        }
        
        .git-file-change:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .git-status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 2px;
            margin-right: 8px;
            flex-shrink: 0;
        }
        
        .git-status-modified {
            background: #f0c674;
        }
        
        .git-status-added {
            background: #b5bd68;
        }
        
        .git-status-deleted {
            background: #cc6666;
        }
        
        .git-status-untracked {
            background: #de935f;
        }
        
        /* Search Panel Styles */
        .search-panel {
            padding: 16px;
        }
        
        .search-input-container {
            position: relative;
            margin-bottom: 16px;
        }
        
        .search-input {
            width: 100%;
            padding: 8px 32px 8px 12px;
            background: #3c3c3c;
            border: 1px solid #464647;
            border-radius: 3px;
            color: #cccccc;
            font-size: 13px;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #007acc;
        }
        
        .search-icon {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            color: #858585;
        }
        
        .search-results {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .search-result {
            padding: 8px;
            border-radius: 3px;
            margin: 2px 0;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .search-result:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .search-result-file {
            font-weight: 600;
            color: #4ec9b0;
            font-size: 12px;
            margin-bottom: 4px;
        }
        
        .search-result-line {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            color: #d4d4d4;
            white-space: pre-wrap;
            overflow: hidden;
        }
        
        .search-result-match {
            background: rgba(255, 215, 0, 0.3);
            color: #000;
        }
        
        /* Extensions Panel Styles */
        .extensions-panel {
            padding: 16px;
        }
        
        .extension-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #2d2d30;
            border-radius: 4px;
            margin: 8px 0;
            transition: background-color 0.2s ease;
        }
        
        .extension-item:hover {
            background: #3c3c3c;
        }
        
        .extension-icon {
            width: 32px;
            height: 32px;
            margin-right: 12px;
            border-radius: 4px;
            background: #007acc;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .extension-info {
            flex: 1;
        }
        
        .extension-name {
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 2px;
        }
        
        .extension-description {
            font-size: 12px;
            color: #cccccc;
        }
        
        /* Terminal Panel Styles */
        .terminal-panel {
            height: 300px;
            background: #1e1e1e;
            border-top: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }
        
        .terminal-tabs {
            display: flex;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            min-height: 30px;
        }
        
        .terminal-tab {
            padding: 6px 12px;
            background: transparent;
            border: none;
            color: #cccccc;
            cursor: pointer;
            font-size: 12px;
            border-bottom: 2px solid transparent;
        }
        
        .terminal-tab.active {
            color: #ffffff;
            border-bottom-color: #007acc;
        }
        
        .terminal-content {
            flex: 1;
            background: #1e1e1e;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            padding: 8px;
            overflow-y: auto;
        }
        
        /* Responsive Styles */
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                position: absolute;
                z-index: 1000;
                height: 100vh;
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                width: 100%;
            }
            
            .toolbar {
                padding: 0 8px;
            }
            
            .search-box {
                max-width: 200px;
            }
        }
        
        /* File Type Icons */
        .icon-python { color: #3776ab; }
        .icon-javascript { color: #f7df1e; }
        .icon-typescript { color: #3178c6; }
        .icon-react { color: #61dafb; }
        .icon-vue { color: #4fc08d; }
        .icon-angular { color: #dd0031; }
        .icon-html { color: #e34f26; }
        .icon-css { color: #1572b6; }
        .icon-scss { color: #cf649a; }
        .icon-json { color: #cbcb41; }
        .icon-xml { color: #e37933; }
        .icon-markdown { color: #083fa1; }
        .icon-yaml { color: #cb171e; }
        .icon-dockerfile { color: #2496ed; }
        .icon-shell { color: #89e051; }
        .icon-sql { color: #336791; }
        .icon-php { color: #777bb4; }
        .icon-ruby { color: #cc342d; }
        .icon-go { color: #00add8; }
        .icon-rust { color: #ce422b; }
        .icon-java { color: #ed8b00; }
        .icon-csharp { color: #239120; }
        .icon-cpp { color: #00599c; }
        .icon-folder { color: #f0c674; }
        .icon-file { color: #d4d4d4; }
        
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
    <div class="ide-container">
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-tabs">
                <button class="sidebar-tab active" onclick="switchSidebarTab('files')">📁 Files</button>
                <button class="sidebar-tab" onclick="switchSidebarTab('search')">🔍 Search</button>
                <button class="sidebar-tab" onclick="switchSidebarTab('git')">🔀 Git</button>
                <button class="sidebar-tab" onclick="switchSidebarTab('extensions')">🧩 Extensions</button>
            </div>
            
            <div class="sidebar-content">
                <!-- File Explorer Panel -->
                <div id="fileExplorerPanel" class="file-explorer">
                    <div class="file-tree" id="fileTree"></div>
                </div>
                
                <!-- Search Panel -->
                <div id="searchPanel" class="search-panel" style="display: none;">
                    <div class="search-input-container">
                        <input type="text" class="search-input" id="searchInput" placeholder="Search in files...">
                        <div class="search-icon">🔍</div>
                    </div>
                    <div class="search-results" id="searchResults"></div>
                </div>
                
                <!-- Git Panel -->
                <div id="gitPanel" class="git-panel" style="display: none;">
                    <div class="git-status" id="gitStatus">
                        <div class="git-branch">main</div>
                        <div class="git-changes">No changes</div>
                    </div>
                    <div class="git-file-changes" id="gitFileChanges"></div>
                </div>
                
                <!-- Extensions Panel -->
                <div id="extensionsPanel" class="extensions-panel" style="display: none;">
                    <div class="extension-item">
                        <div class="extension-icon">PY</div>
                        <div class="extension-info">
                            <div class="extension-name">Python Language Support</div>
                            <div class="extension-description">Syntax highlighting and IntelliSense for Python</div>
                        </div>
                    </div>
                    <div class="extension-item">
                        <div class="extension-icon">JS</div>
                        <div class="extension-info">
                            <div class="extension-name">JavaScript & TypeScript</div>
                            <div class="extension-description">Rich language support for JS/TS</div>
                        </div>
                    </div>
                    <div class="extension-item">
                        <div class="extension-icon">GIT</div>
                        <div class="extension-info">
                            <div class="extension-name">Git Integration</div>
                            <div class="extension-description">Built-in Git version control</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Toolbar -->
            <div class="toolbar">
                <button class="toolbar-button" onclick="toggleSidebar()">☰</button>
                <button class="toolbar-button" onclick="createNewFile()">📄 New</button>
                <button class="toolbar-button" onclick="openFile()">📂 Open</button>
                <button class="toolbar-button" onclick="saveFile()">💾 Save</button>
                <button class="toolbar-button" onclick="gitCommit()">🔄 Commit</button>
                <input type="text" class="search-box" id="globalSearch" placeholder="Search everywhere...">
                <button class="toolbar-button" onclick="runCode()">▶️ Run</button>
                <button class="toolbar-button" onclick="toggleTerminal()">💻 Terminal</button>
            </div>
            
            <!-- Editor Container -->
            <div class="editor-container">
                <div class="editor-pane">
                    <div class="editor-tabs" id="editorTabs">
                        <div class="editor-tab active" data-file="welcome.md">
                            <span>📋 Welcome</span>
                            <span class="close-btn" onclick="closeTab('welcome.md')">×</span>
                        </div>
                    </div>
                    <div class="monaco-editor-container" id="monacoEditor"></div>
                </div>
            </div>
            
            <!-- Terminal Panel -->
            <div class="terminal-panel" id="terminalPanel" style="display: none;">
                <div class="terminal-tabs">
                    <button class="terminal-tab active">bash</button>
                    <button class="terminal-tab">python</button>
                    <button class="terminal-tab">+</button>
                </div>
                <div class="terminal-content">
                    <iframe src="http://localhost:7681" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
        
        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <span id="connectionStatus">🔗 Connected</span>
            </div>
            <div class="status-item">
                <span id="currentBranch">🌿 main</span>
            </div>
            <div class="status-item">
                <span id="cursorPosition">Ln 1, Col 1</span>
            </div>
            <div class="status-item">
                <span id="fileEncoding">UTF-8</span>
            </div>
            <div class="status-item">
                <span id="fileType">Markdown</span>
            </div>
        </div>
    </div>

    <script>
        // Initialize SocketIO connection
        const socket = io();
        
        // Monaco Editor instance
        let monacoEditor;
        
        // IDE State
        let currentTab = 'welcome.md';
        let openTabs = new Map();
        let fileTree = new Map();
        let sidebarVisible = true;
        let terminalVisible = false;
        let currentSidebarTab = 'files';
        
        // File type language mapping
        const fileLanguageMap = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'plaintext',
            '.sh': 'shell',
            '.bash': 'shell',
            '.sql': 'sql',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.dockerfile': 'dockerfile'
        };
        
        // Initialize Monaco Editor
        function initializeMonacoEditor() {
            require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
            require(['vs/editor/editor.main'], function () {
                monacoEditor = monaco.editor.create(document.getElementById('monacoEditor'), {
                    value: `# Welcome to Claude Code V3+ IDE

## Features

### 🌲 File Tree Explorer
- Navigate through your project files
- Tree view with expand/collapse functionality
- File type icons and syntax highlighting
- Git status indicators for modified files

### 🔍 Global Search
- Search across all files in your project
- Regex support for advanced patterns
- Jump to specific line numbers
- Real-time search results

### 🔀 Git Integration
- View repository status and branch information
- See modified, added, and untracked files
- Commit changes directly from the IDE
- Visual diff for file changes

### 💻 Integrated Terminal
- Full terminal access with ttyd integration
- Multiple terminal sessions
- Execute commands directly in your project

### 🎨 Syntax Highlighting
Support for 20+ programming languages:
- Python, JavaScript, TypeScript
- HTML, CSS, SCSS, Sass
- React, Vue, Angular
- JSON, XML, YAML
- Markdown, SQL, PHP
- Ruby, Go, Rust, Java
- C#, C++, Shell scripts
- And many more...

### ⚡ Code Intelligence
- Auto-completion and IntelliSense
- Error highlighting and diagnostics
- Code formatting and linting
- Jump to definition

## Quick Start

1. **Open Files**: Click 📂 Open in the toolbar or use the file explorer
2. **Create New**: Click 📄 New to create a new file
3. **Search**: Use 🔍 in the sidebar for project-wide search
4. **Terminal**: Click 💻 Terminal to open the integrated terminal
5. **Git**: Use 🔀 Git panel to manage version control

Start coding and enjoy the full IDE experience!
`,
                    language: 'markdown',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    minimap: { enabled: true },
                    fontSize: 14,
                    fontFamily: 'Consolas, Monaco, monospace',
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    renderWhitespace: 'boundary',
                    formatOnPaste: true,
                    formatOnType: true
                });
                
                // Add editor event listeners
                monacoEditor.onDidChangeCursorPosition((e) => {
                    updateStatusBar('position', `Ln ${e.position.lineNumber}, Col ${e.position.column}`);
                });
                
                monacoEditor.onDidChangeModelContent(() => {
                    markTabAsModified(currentTab);
                });
                
                // Initialize welcome tab
                openTabs.set('welcome.md', {
                    content: monacoEditor.getValue(),
                    language: 'markdown',
                    modified: false
                });
            });
        }
        
        // Sidebar tab switching
        function switchSidebarTab(tabName) {
            // Update tab appearance
            document.querySelectorAll('.sidebar-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Hide all panels
            document.getElementById('fileExplorerPanel').style.display = 'none';
            document.getElementById('searchPanel').style.display = 'none';
            document.getElementById('gitPanel').style.display = 'none';
            document.getElementById('extensionsPanel').style.display = 'none';
            
            // Show selected panel
            switch(tabName) {
                case 'files':
                    document.getElementById('fileExplorerPanel').style.display = 'block';
                    loadFileTree();
                    break;
                case 'search':
                    document.getElementById('searchPanel').style.display = 'block';
                    break;
                case 'git':
                    document.getElementById('gitPanel').style.display = 'block';
                    loadGitStatus();
                    break;
                case 'extensions':
                    document.getElementById('extensionsPanel').style.display = 'block';
                    break;
            }
            
            currentSidebarTab = tabName;
        }
        
        // Toggle sidebar visibility
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebarVisible = !sidebarVisible;
            
            if (sidebarVisible) {
                sidebar.style.display = 'flex';
            } else {
                sidebar.style.display = 'none';
            }
        }
        
        // Toggle terminal visibility
        function toggleTerminal() {
            const terminal = document.getElementById('terminalPanel');
            terminalVisible = !terminalVisible;
            
            if (terminalVisible) {
                terminal.style.display = 'flex';
                terminal.style.height = '300px';
            } else {
                terminal.style.display = 'none';
            }
        }
        
        // File management functions
        function createNewFile() {
            const fileName = prompt('Enter file name:');
            if (fileName) {
                const language = getLanguageFromExtension(fileName);
                openTab(fileName, '', language, true);
                socket.emit('create_file', { path: fileName, content: '' });
            }
        }
        
        function openFile() {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.onchange = (e) => {
                Array.from(e.target.files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const language = getLanguageFromExtension(file.name);
                        openTab(file.name, e.target.result, language, false);
                    };
                    reader.readAsText(file);
                });
            };
            input.click();
        }
        
        function saveFile() {
            if (monacoEditor && currentTab) {
                const content = monacoEditor.getValue();
                const tabData = openTabs.get(currentTab);
                if (tabData) {
                    tabData.content = content;
                    tabData.modified = false;
                    updateTabTitle(currentTab, false);
                    socket.emit('save_file', { path: currentTab, content: content });
                    updateStatusBar('message', 'File saved successfully');
                }
            }
        }
        
        function runCode() {
            if (monacoEditor && currentTab) {
                const content = monacoEditor.getValue();
                const language = openTabs.get(currentTab)?.language;
                
                if (language === 'python') {
                    socket.emit('run_python', { code: content });
                } else if (language === 'javascript') {
                    socket.emit('run_javascript', { code: content });
                } else {
                    updateStatusBar('message', 'Run not supported for this language');
                }
            }
        }
        
        function gitCommit() {
            const message = prompt('Commit message:');
            if (message) {
                socket.emit('git_commit', { message: message });
            }
        }
        
        // Tab management
        function openTab(fileName, content, language, isNew) {
            // Save current tab content
            if (monacoEditor && currentTab && openTabs.has(currentTab)) {
                openTabs.get(currentTab).content = monacoEditor.getValue();
            }
            
            // Add to open tabs if not already open
            if (!openTabs.has(fileName)) {
                openTabs.set(fileName, {
                    content: content,
                    language: language,
                    modified: isNew
                });
                
                // Add tab to UI
                const tabsContainer = document.getElementById('editorTabs');
                const tabElement = document.createElement('div');
                tabElement.className = 'editor-tab';
                tabElement.setAttribute('data-file', fileName);
                tabElement.innerHTML = `
                    <span>${getFileIcon(fileName)} ${fileName}</span>
                    <span class="close-btn" onclick="closeTab('${fileName}')">×</span>
                `;
                tabElement.onclick = (e) => {
                    if (!e.target.classList.contains('close-btn')) {
                        switchTab(fileName);
                    }
                };
                tabsContainer.appendChild(tabElement);
            }
            
            // Switch to the tab
            switchTab(fileName);
        }
        
        function switchTab(fileName) {
            // Save current content
            if (monacoEditor && currentTab && openTabs.has(currentTab)) {
                openTabs.get(currentTab).content = monacoEditor.getValue();
            }
            
            // Update tab appearance
            document.querySelectorAll('.editor-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector(`[data-file="${fileName}"]`).classList.add('active');
            
            // Load tab content
            const tabData = openTabs.get(fileName);
            if (tabData && monacoEditor) {
                monaco.editor.setModelLanguage(monacoEditor.getModel(), tabData.language);
                monacoEditor.setValue(tabData.content);
                currentTab = fileName;
                
                // Update status bar
                updateStatusBar('fileType', tabData.language);
                updateStatusBar('encoding', 'UTF-8');
            }
        }
        
        function closeTab(fileName) {
            const tabData = openTabs.get(fileName);
            if (tabData && tabData.modified) {
                if (!confirm(`File ${fileName} has unsaved changes. Close anyway?`)) {
                    return;
                }
            }
            
            // Remove from open tabs
            openTabs.delete(fileName);
            
            // Remove from UI
            document.querySelector(`[data-file="${fileName}"]`).remove();
            
            // Switch to another tab if this was the current tab
            if (currentTab === fileName) {
                const remainingTabs = Array.from(openTabs.keys());
                if (remainingTabs.length > 0) {
                    switchTab(remainingTabs[0]);
                } else {
                    // Open welcome tab if no tabs remain
                    openTab('welcome.md', '# Welcome to Claude Code V3+ IDE', 'markdown', false);
                }
            }
        }
        
        function markTabAsModified(fileName) {
            const tabData = openTabs.get(fileName);
            if (tabData) {
                tabData.modified = true;
                updateTabTitle(fileName, true);
            }
        }
        
        function updateTabTitle(fileName, modified) {
            const tabElement = document.querySelector(`[data-file="${fileName}"]`);
            if (tabElement) {
                const span = tabElement.querySelector('span');
                const icon = getFileIcon(fileName);
                span.textContent = `${icon} ${fileName}${modified ? ' •' : ''}`;
            }
        }
        
        // File explorer functions
        function loadFileTree() {
            socket.emit('get_file_tree');
        }
        
        function createFileTreeNode(item, parentElement, level = 0) {
            const li = document.createElement('li');
            li.className = 'file-tree-item';
            
            const node = document.createElement('div');
            node.className = 'file-tree-node';
            node.style.paddingLeft = `${level * 16}px`;
            
            if (item.type === 'directory') {
                const expand = document.createElement('div');
                expand.className = 'file-tree-expand';
                expand.onclick = () => toggleDirectory(item.path, li);
                node.appendChild(expand);
                
                const icon = document.createElement('span');
                icon.className = 'file-tree-icon icon-folder';
                icon.textContent = '📁';
                node.appendChild(icon);
                
                const name = document.createElement('span');
                name.textContent = item.name;
                node.appendChild(name);
                
                li.appendChild(node);
                
                if (item.children && item.children.length > 0) {
                    const childrenUl = document.createElement('ul');
                    childrenUl.className = 'file-tree-children collapsed';
                    
                    item.children.forEach(child => {
                        createFileTreeNode(child, childrenUl, level + 1);
                    });
                    
                    li.appendChild(childrenUl);
                }
            } else {
                const icon = document.createElement('span');
                icon.className = 'file-tree-icon';
                icon.textContent = getFileIcon(item.name);
                node.appendChild(icon);
                
                const name = document.createElement('span');
                name.textContent = item.name;
                node.appendChild(name);
                
                node.onclick = () => openFileFromTree(item.path);
                
                li.appendChild(node);
            }
            
            parentElement.appendChild(li);
        }
        
        function toggleDirectory(path, element) {
            const children = element.querySelector('.file-tree-children');
            const expand = element.querySelector('.file-tree-expand');
            
            if (children) {
                if (children.classList.contains('collapsed')) {
                    children.classList.remove('collapsed');
                    expand.classList.add('expanded');
                } else {
                    children.classList.add('collapsed');
                    expand.classList.remove('expanded');
                }
            }
        }
        
        function openFileFromTree(filePath) {
            socket.emit('read_file', { path: filePath });
        }
        
        // Search functionality
        function performSearch() {
            const query = document.getElementById('searchInput').value;
            if (query.trim()) {
                socket.emit('search_files', { query: query });
            }
        }
        
        function displaySearchResults(results) {
            const container = document.getElementById('searchResults');
            container.innerHTML = '';
            
            results.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.className = 'search-result';
                resultElement.onclick = () => openSearchResult(result);
                
                resultElement.innerHTML = `
                    <div class="search-result-file">${result.file}</div>
                    <div class="search-result-line">${highlightSearchMatch(result.line, result.match)}</div>
                `;
                
                container.appendChild(resultElement);
            });
        }
        
        function highlightSearchMatch(line, match) {
            return line.replace(new RegExp(match, 'gi'), `<span class="search-result-match">${match}</span>`);
        }
        
        function openSearchResult(result) {
            socket.emit('read_file', { path: result.file });
            // TODO: Jump to specific line number
        }
        
        // Git functionality
        function loadGitStatus() {
            socket.emit('get_git_status');
        }
        
        function displayGitStatus(gitData) {
            const statusElement = document.getElementById('gitStatus');
            statusElement.innerHTML = `
                <div class="git-branch">${gitData.current_branch || 'main'}</div>
                <div class="git-changes">${gitData.modified_files || 0} files changed</div>
            `;
            
            const changesElement = document.getElementById('gitFileChanges');
            changesElement.innerHTML = '';
            
            if (gitData.changes && gitData.changes.length > 0) {
                gitData.changes.forEach(change => {
                    const changeElement = document.createElement('div');
                    changeElement.className = 'git-file-change';
                    
                    changeElement.innerHTML = `
                        <div class="git-status-indicator git-status-${change.status}"></div>
                        <span>${change.file}</span>
                    `;
                    
                    changesElement.appendChild(changeElement);
                });
            }
        }
        
        // Utility functions
        function getFileIcon(fileName) {
            const ext = fileName.toLowerCase().split('.').pop();
            const iconMap = {
                'py': '🐍', 'js': '📜', 'ts': '📘', 'jsx': '⚛️', 'tsx': '⚛️',
                'html': '🌐', 'css': '🎨', 'scss': '🎨', 'sass': '🎨',
                'json': '📋', 'xml': '📄', 'yaml': '⚙️', 'yml': '⚙️',
                'md': '📝', 'txt': '📄', 'sh': '💻', 'bash': '💻',
                'sql': '🗄️', 'php': '🐘', 'rb': '💎', 'go': '🐹',
                'rs': '🦀', 'java': '☕', 'cs': '🔷', 'cpp': '⚙️', 'c': '⚙️'
            };
            return iconMap[ext] || '📄';
        }
        
        function getLanguageFromExtension(fileName) {
            const ext = '.' + fileName.toLowerCase().split('.').pop();
            return fileLanguageMap[ext] || 'plaintext';
        }
        
        function updateStatusBar(type, content) {
            switch(type) {
                case 'position':
                    document.getElementById('cursorPosition').textContent = content;
                    break;
                case 'fileType':
                    document.getElementById('fileType').textContent = content;
                    break;
                case 'encoding':
                    document.getElementById('fileEncoding').textContent = content;
                    break;
                case 'branch':
                    document.getElementById('currentBranch').textContent = `🌿 ${content}`;
                    break;
                case 'connection':
                    document.getElementById('connectionStatus').textContent = content;
                    break;
                case 'message':
                    // Show temporary message
                    const originalText = document.getElementById('connectionStatus').textContent;
                    document.getElementById('connectionStatus').textContent = content;
                    setTimeout(() => {
                        document.getElementById('connectionStatus').textContent = originalText;
                    }, 3000);
                    break;
            }
        }
        
        // Event listeners
        document.getElementById('searchInput').addEventListener('input', performSearch);
        document.getElementById('globalSearch').addEventListener('input', function() {
            const query = this.value;
            if (query.trim()) {
                socket.emit('global_search', { query: query });
            }
        });
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to server');
            updateStatusBar('connection', '🔗 Connected');
            connectionStatus.className = 'connection-status connected';
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            updateStatusBar('connection', '🔗 Disconnected');
        });
        
        // IDE-specific socket handlers
        socket.on('file_tree', function(data) {
            const fileTreeContainer = document.getElementById('fileTree');
            fileTreeContainer.innerHTML = '';
            
            if (data.tree && data.tree.length > 0) {
                data.tree.forEach(item => {
                    createFileTreeNode(item, fileTreeContainer);
                });
            }
        });
        
        socket.on('file_content', function(data) {
            if (data.success) {
                const language = getLanguageFromExtension(data.path);
                openTab(data.path, data.content, language, false);
            } else {
                updateStatusBar('message', `Error reading file: ${data.error}`);
            }
        });
        
        socket.on('file_saved', function(data) {
            if (data.success) {
                updateStatusBar('message', `File ${data.path} saved successfully`);
            } else {
                updateStatusBar('message', `Error saving file: ${data.error}`);
            }
        });
        
        socket.on('search_results', function(data) {
            displaySearchResults(data.results || []);
        });
        
        socket.on('git_status_response', function(data) {
            displayGitStatus(data);
            updateStatusBar('branch', data.current_branch || 'main');
        });
        
        socket.on('code_execution_result', function(data) {
            if (terminalVisible) {
                // Display in terminal if visible
                const terminalContent = document.querySelector('.terminal-content');
                if (terminalContent) {
                    const output = document.createElement('div');
                    output.style.color = data.success ? '#00ff00' : '#ff0000';
                    output.textContent = data.output || data.error;
                    terminalContent.appendChild(output);
                }
            } else {
                updateStatusBar('message', data.success ? 'Code executed successfully' : `Error: ${data.error}`);
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'n':
                        e.preventDefault();
                        createNewFile();
                        break;
                    case 'o':
                        e.preventDefault();
                        openFile();
                        break;
                    case 's':
                        e.preventDefault();
                        saveFile();
                        break;
                    case '`':
                        e.preventDefault();
                        toggleTerminal();
                        break;
                    case 'b':
                        e.preventDefault();
                        toggleSidebar();
                        break;
                    case 'f':
                        e.preventDefault();
                        document.getElementById('globalSearch').focus();
                        break;
                }
            }
        });
        
        // Initialize the IDE when page loads
        window.addEventListener('load', function() {
            initializeMonacoEditor();
            loadFileTree();
            loadGitStatus();
            
            // Set up auto-save
            setInterval(() => {
                if (monacoEditor && currentTab && openTabs.has(currentTab)) {
                    const tabData = openTabs.get(currentTab);
                    if (tabData && tabData.modified) {
                        // Auto-save after 30 seconds of inactivity
                        saveFile();
                    }
                }
            }, 30000);
            
            console.log('Claude Code V3+ IDE initialized successfully');
        });
        
        // Handle mobile responsiveness
        function handleResize() {
            if (window.innerWidth <= 768) {
                // Mobile view
                if (sidebarVisible) {
                    document.getElementById('sidebar').classList.add('open');
                }
            } else {
                // Desktop view
                document.getElementById('sidebar').classList.remove('open');
            }
        }
        
        window.addEventListener('resize', handleResize);
        handleResize(); // Initial call
    </script>
</body>
</html>
"""

# File system utilities for IDE functionality
def get_file_tree(directory_path: str, max_depth: int = 3, current_depth: int = 0):
    """Generate file tree structure for the IDE"""
    if current_depth >= max_depth:
        return []
    
    tree = []
    try:
        items = sorted(os.listdir(directory_path))
        
        # Separate directories and files
        directories = []
        files = []
        
        for item in items:
            # Skip hidden files and common ignore patterns
            if item.startswith('.') and item not in ['.env', '.gitignore']:
                continue
            if item in ['node_modules', '__pycache__', '.git', 'venv', '.venv']:
                continue
                
            item_path = os.path.join(directory_path, item)
            
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)
        
        # Add directories first
        for directory in directories:
            dir_path = os.path.join(directory_path, directory)
            children = get_file_tree(dir_path, max_depth, current_depth + 1)
            
            tree.append({
                'name': directory,
                'path': os.path.relpath(dir_path, dashboard_data.working_directory),
                'type': 'directory',
                'children': children
            })
        
        # Add files
        for file in files:
            file_path = os.path.join(directory_path, file)
            tree.append({
                'name': file,
                'path': os.path.relpath(file_path, dashboard_data.working_directory),
                'type': 'file',
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            })
            
    except (OSError, PermissionError) as e:
        logger.error(f"Error reading directory {directory_path}: {e}")
    
    return tree

def search_in_files(query: str, directory: str, file_extensions: list = None):
    """Search for text in files"""
    if not file_extensions:
        file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', 
                         '.json', '.md', '.txt', '.sql', '.yaml', '.yml']
    
    results = []
    try:
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if query.lower() in line.lower():
                                    results.append({
                                        'file': os.path.relpath(file_path, directory),
                                        'line_number': line_num,
                                        'line': line.strip(),
                                        'match': query
                                    })
                                    
                                    # Limit results per file
                                    if len([r for r in results if r['file'] == os.path.relpath(file_path, directory)]) >= 5:
                                        break
                    except Exception as e:
                        continue
                        
            # Limit total results
            if len(results) >= 50:
                break
                
    except Exception as e:
        logger.error(f"Error searching files: {e}")
    
    return results

def get_enhanced_git_status():
    """Get enhanced git status with file changes"""
    if not dashboard_data.is_git_repo:
        return {'current_branch': 'main', 'modified_files': 0, 'changes': []}
    
    try:
        # Get current branch
        branch_result = subprocess.run([
            'git', 'branch', '--show-current'
        ], capture_output=True, text=True, cwd=dashboard_data.working_directory)
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'main'
        
        # Get detailed status
        status_result = subprocess.run([
            'git', 'status', '--porcelain'
        ], capture_output=True, text=True, cwd=dashboard_data.working_directory)
        
        changes = []
        if status_result.returncode == 0 and status_result.stdout.strip():
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    # Map git status codes to readable status
                    status_map = {
                        'M ': 'modified',
                        ' M': 'modified',
                        'A ': 'added',
                        ' A': 'added',
                        'D ': 'deleted',
                        ' D': 'deleted',
                        '??': 'untracked',
                        'R ': 'renamed',
                        'C ': 'copied'
                    }
                    
                    status = status_map.get(status_code, 'unknown')
                    changes.append({
                        'file': file_path,
                        'status': status
                    })
        
        return {
            'current_branch': current_branch,
            'modified_files': len(changes),
            'changes': changes
        }
        
    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        return {'current_branch': 'main', 'modified_files': 0, 'changes': []}

# WebSocket Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    logger.info(f"Client connected: {client_id}")
    
    # Send initial data for IDE
    emit('file_tree', {'tree': get_file_tree(dashboard_data.working_directory)})
    emit('git_status_response', get_enhanced_git_status())

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

# IDE-specific socket event handlers
@socketio.on('get_file_tree')
def handle_get_file_tree():
    """Handle file tree request"""
    try:
        tree = get_file_tree(dashboard_data.working_directory)
        emit('file_tree', {'tree': tree})
    except Exception as e:
        logger.error(f"Error getting file tree: {e}")
        emit('file_tree', {'tree': [], 'error': str(e)})

@socketio.on('read_file')
def handle_read_file(data):
    """Handle file read request"""
    file_path = data.get('path', '')
    if not file_path:
        emit('file_content', {'success': False, 'error': 'No file path provided'})
        return
    
    try:
        # Ensure path is within working directory for security
        full_path = os.path.join(dashboard_data.working_directory, file_path)
        full_path = os.path.abspath(full_path)
        
        if not full_path.startswith(os.path.abspath(dashboard_data.working_directory)):
            emit('file_content', {'success': False, 'error': 'Access denied'})
            return
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        emit('file_content', {
            'success': True,
            'path': file_path,
            'content': content
        })
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        emit('file_content', {
            'success': False,
            'path': file_path,
            'error': str(e)
        })

@socketio.on('save_file')
def handle_save_file(data):
    """Handle file save request"""
    file_path = data.get('path', '')
    content = data.get('content', '')
    
    if not file_path:
        emit('file_saved', {'success': False, 'error': 'No file path provided'})
        return
    
    try:
        # Ensure path is within working directory for security
        full_path = os.path.join(dashboard_data.working_directory, file_path)
        full_path = os.path.abspath(full_path)
        
        if not full_path.startswith(os.path.abspath(dashboard_data.working_directory)):
            emit('file_saved', {'success': False, 'error': 'Access denied'})
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        emit('file_saved', {
            'success': True,
            'path': file_path
        })
        
        # Refresh file tree
        emit('file_tree', {'tree': get_file_tree(dashboard_data.working_directory)})
        
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}")
        emit('file_saved', {
            'success': False,
            'path': file_path,
            'error': str(e)
        })

@socketio.on('create_file')
def handle_create_file(data):
    """Handle file creation request"""
    file_path = data.get('path', '')
    content = data.get('content', '')
    
    if not file_path:
        emit('file_saved', {'success': False, 'error': 'No file path provided'})
        return
    
    try:
        # Ensure path is within working directory for security
        full_path = os.path.join(dashboard_data.working_directory, file_path)
        full_path = os.path.abspath(full_path)
        
        if not full_path.startswith(os.path.abspath(dashboard_data.working_directory)):
            emit('file_saved', {'success': False, 'error': 'Access denied'})
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Only create if file doesn't exist
        if not os.path.exists(full_path):
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            emit('file_saved', {
                'success': True,
                'path': file_path
            })
            
            # Refresh file tree
            emit('file_tree', {'tree': get_file_tree(dashboard_data.working_directory)})
        else:
            emit('file_saved', {
                'success': False,
                'path': file_path,
                'error': 'File already exists'
            })
        
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        emit('file_saved', {
            'success': False,
            'path': file_path,
            'error': str(e)
        })

@socketio.on('search_files')
def handle_search_files(data):
    """Handle file search request"""
    query = data.get('query', '')
    if not query.strip():
        emit('search_results', {'results': []})
        return
    
    try:
        results = search_in_files(query, dashboard_data.working_directory)
        emit('search_results', {'results': results})
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        emit('search_results', {'results': [], 'error': str(e)})

@socketio.on('global_search')
def handle_global_search(data):
    """Handle global search request"""
    query = data.get('query', '')
    if not query.strip():
        return
    
    try:
        results = search_in_files(query, dashboard_data.working_directory)
        emit('search_results', {'results': results})
    except Exception as e:
        logger.error(f"Error in global search: {e}")

@socketio.on('get_git_status')
def handle_get_git_status():
    """Handle git status request"""
    try:
        git_status = get_enhanced_git_status()
        emit('git_status_response', git_status)
    except Exception as e:
        logger.error(f"Error getting git status: {e}")
        emit('git_status_response', {
            'current_branch': 'main',
            'modified_files': 0,
            'changes': [],
            'error': str(e)
        })

@socketio.on('git_commit')
def handle_git_commit(data):
    """Handle git commit request"""
    message = data.get('message', '')
    if not message.strip():
        emit('git_commit_result', {'success': False, 'error': 'No commit message provided'})
        return
    
    try:
        # Add all changes
        add_result = subprocess.run([
            'git', 'add', '.'
        ], capture_output=True, text=True, cwd=dashboard_data.working_directory)
        
        if add_result.returncode != 0:
            emit('git_commit_result', {
                'success': False,
                'error': f'Failed to stage files: {add_result.stderr}'
            })
            return
        
        # Commit changes
        commit_result = subprocess.run([
            'git', 'commit', '-m', message
        ], capture_output=True, text=True, cwd=dashboard_data.working_directory)
        
        if commit_result.returncode == 0:
            emit('git_commit_result', {
                'success': True,
                'message': 'Changes committed successfully'
            })
            
            # Refresh git status
            emit('git_status_response', get_enhanced_git_status())
        else:
            emit('git_commit_result', {
                'success': False,
                'error': commit_result.stderr or 'Commit failed'
            })
        
    except Exception as e:
        logger.error(f"Error committing changes: {e}")
        emit('git_commit_result', {
            'success': False,
            'error': str(e)
        })

@socketio.on('run_python')
def handle_run_python(data):
    """Handle Python code execution"""
    code = data.get('code', '')
    if not code.strip():
        emit('code_execution_result', {'success': False, 'error': 'No code provided'})
        return
    
    try:
        # Execute Python code with timeout
        result = subprocess.run([
            sys.executable, '-c', code
        ], capture_output=True, text=True, timeout=30, cwd=dashboard_data.working_directory)
        
        emit('code_execution_result', {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'language': 'python'
        })
        
    except subprocess.TimeoutExpired:
        emit('code_execution_result', {
            'success': False,
            'error': 'Code execution timed out (30s limit)',
            'language': 'python'
        })
    except Exception as e:
        logger.error(f"Error executing Python code: {e}")
        emit('code_execution_result', {
            'success': False,
            'error': str(e),
            'language': 'python'
        })

@socketio.on('run_javascript')
def handle_run_javascript(data):
    """Handle JavaScript code execution"""
    code = data.get('code', '')
    if not code.strip():
        emit('code_execution_result', {'success': False, 'error': 'No code provided'})
        return
    
    try:
        # Execute JavaScript code with Node.js
        result = subprocess.run([
            'node', '-e', code
        ], capture_output=True, text=True, timeout=30, cwd=dashboard_data.working_directory)
        
        emit('code_execution_result', {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'language': 'javascript'
        })
        
    except subprocess.TimeoutExpired:
        emit('code_execution_result', {
            'success': False,
            'error': 'Code execution timed out (30s limit)',
            'language': 'javascript'
        })
    except FileNotFoundError:
        emit('code_execution_result', {
            'success': False,
            'error': 'Node.js not found. Please install Node.js to run JavaScript code.',
            'language': 'javascript'
        })
    except Exception as e:
        logger.error(f"Error executing JavaScript code: {e}")
        emit('code_execution_result', {
            'success': False,
            'error': str(e),
            'language': 'javascript'
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