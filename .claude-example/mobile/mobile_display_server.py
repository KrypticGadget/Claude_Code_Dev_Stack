#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Display Server - Shows QR code and access info in browser
"""
import os
import sys
import json
import base64
import webbrowser
from pathlib import Path
from flask import Flask, render_template_string
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Global variables for access info
ACCESS_INFO = {}

# HTML template for the display page
DISPLAY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code V3+ Mobile Access</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2em;
        }
        
        .qr-section {
            text-align: center;
            margin: 30px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .qr-code {
            display: inline-block;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .qr-code img {
            max-width: 300px;
            height: auto;
        }
        
        .access-info {
            background: #f0f8ff;
            border-left: 4px solid #4CAF50;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .info-row {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 10px;
            background: white;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        
        .info-row:hover {
            transform: translateX(5px);
        }
        
        .info-label {
            font-weight: bold;
            color: #555;
            min-width: 120px;
            margin-right: 15px;
        }
        
        .info-value {
            flex: 1;
            font-family: 'Courier New', monospace;
            color: #333;
            word-break: break-all;
            background: #f5f5f5;
            padding: 8px 12px;
            border-radius: 5px;
        }
        
        .copy-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
            transition: background 0.3s;
        }
        
        .copy-btn:hover {
            background: #45a049;
        }
        
        .copy-btn:active {
            transform: scale(0.95);
        }
        
        .instructions {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 20px;
            margin: 30px 0;
        }
        
        .instructions h3 {
            color: #856404;
            margin-bottom: 15px;
        }
        
        .instructions ol {
            margin-left: 20px;
            color: #856404;
        }
        
        .instructions li {
            margin: 10px 0;
        }
        
        .status {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background: #e8f5e9;
            border-radius: 10px;
        }
        
        .status-item {
            text-align: center;
        }
        
        .status-icon {
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .status-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .success-badge {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }
        
        .samsung-badge {
            background: linear-gradient(45deg, #1e3c72, #2a5298);
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            display: inline-block;
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Claude Code V3+</h1>
            <div class="subtitle">Mobile Access Portal</div>
            <div class="success-badge">✅ Mobile Access Active</div>
        </div>
        
        <div class="status">
            <div class="status-item">
                <div class="status-icon">🔒</div>
                <div class="status-label">Secure Tunnel</div>
            </div>
            <div class="status-item">
                <div class="status-icon">📱</div>
                <div class="status-label">Mobile Ready</div>
            </div>
            <div class="status-item">
                <div class="status-icon">🌐</div>
                <div class="status-label">Dashboard Active</div>
            </div>
        </div>
        
        <div class="qr-section">
            <h2>📱 Scan QR Code for Mobile Access</h2>
            <div class="qr-code">
                {% if qr_code %}
                <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code for Mobile Access">
                {% else %}
                <p>QR Code generation in progress...</p>
                {% endif %}
            </div>
        </div>
        
        <div class="access-info">
            <h3>🔐 Access Credentials</h3>
            
            <div class="info-row">
                <span class="info-label">📱 Mobile URL:</span>
                <span class="info-value">{{ url }}</span>
                <button class="copy-btn" onclick="copyToClipboard('{{ url }}')">Copy</button>
            </div>
            
            <div class="info-row">
                <span class="info-label">🔑 Auth Token:</span>
                <span class="info-value">{{ auth_token }}</span>
                <button class="copy-btn" onclick="copyToClipboard('{{ auth_token }}')">Copy</button>
            </div>
            
            <div class="info-row">
                <span class="info-label">🔗 Quick Link:</span>
                <span class="info-value">{{ url }}?auth={{ auth_token }}</span>
                <button class="copy-btn" onclick="copyToClipboard('{{ url }}?auth={{ auth_token }}')">Copy</button>
            </div>
            
            <div class="info-row">
                <span class="info-label">⏰ Expires:</span>
                <span class="info-value">{{ expires }}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">🖥️ Local Dashboard:</span>
                <span class="info-value">http://localhost:{{ dashboard_port }}</span>
                <button class="copy-btn" onclick="window.open('http://localhost:{{ dashboard_port }}')">Open</button>
            </div>
        </div>
        
        <div class="instructions">
            <h3>📋 How to Access on Samsung Galaxy S25 Edge</h3>
            <ol>
                <li><strong>Method 1:</strong> Scan the QR code above with your Samsung Camera</li>
                <li><strong>Method 2:</strong> Copy the Quick Link and paste in Samsung Internet Browser</li>
                <li><strong>Method 3:</strong> Check your phone notifications for the push notification</li>
            </ol>
            <p style="margin-top: 15px;">
                <strong>Features:</strong> Real-time sync, Edge lighting effects, Haptic feedback, 
                Full V3+ dashboard control with all 28 agents
            </p>
        </div>
        
        <div class="footer">
            <div class="samsung-badge">🌟 Optimized for Samsung Galaxy S25 Edge</div>
            <p style="margin-top: 10px;">Claude Code V3.0+ • Enterprise Development Stack</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                // Show success message
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                btn.style.background = '#4CAF50';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        }
        
        // Auto-refresh every 5 seconds to update status
        setTimeout(() => {
            location.reload();
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Display the mobile access information"""
    return render_template_string(
        DISPLAY_TEMPLATE,
        url=ACCESS_INFO.get('url', 'Waiting for tunnel...'),
        auth_token=ACCESS_INFO.get('auth_token', 'Generating...'),
        expires=ACCESS_INFO.get('expires', 'N/A'),
        dashboard_port=ACCESS_INFO.get('dashboard_port', 8080),
        qr_code=ACCESS_INFO.get('qr_code_base64', None)
    )

def start_display_server(access_info: dict, port: int = 6000):
    """Start the display server with access information"""
    global ACCESS_INFO
    ACCESS_INFO = access_info
    
    # Start Flask in a thread
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    url = f"http://localhost:{port}"
    print(f"🌐 Opening mobile access portal at {url}")
    webbrowser.open(url)
    
    return server_thread

if __name__ == "__main__":
    # Test mode
    test_info = {
        'url': 'https://test.ngrok.io',
        'auth_token': 'test_token_123',
        'expires': datetime.now().isoformat(),
        'dashboard_port': 8080
    }
    start_display_server(test_info)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down display server...")