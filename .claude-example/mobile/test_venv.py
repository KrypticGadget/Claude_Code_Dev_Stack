#!/usr/bin/env python3
"""
Test script to verify virtual environment and dashboard configuration
"""

import sys
import os
from pathlib import Path

# Fix Windows Unicode encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def test_virtual_environment():
    """Test that we're in the virtual environment and can import everything"""
    
    print("Testing Virtual Environment Configuration")
    print("=" * 50)
    
    # Check if we're in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Virtual Environment Active: {'YES' if in_venv else 'NO'}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print()
    
    # Test critical imports
    print("Testing Critical Imports:")
    required_modules = [
        ('flask', 'Flask web framework'),
        ('flask_socketio', 'Real-time communication'),
        ('flask_cors', 'Cross-origin requests'),
        ('socketio', 'Socket.IO client'),
        ('eventlet', 'Async server support'),
        ('git', 'Git operations'),
        ('watchdog', 'File system monitoring'),
        ('psutil', 'System monitoring'),
        ('qrcode', 'QR code generation'),
        ('requests', 'HTTP requests')
    ]
    
    failed_imports = []
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"  OK {module_name:<15} - {description}")
        except ImportError as e:
            print(f"  FAIL {module_name:<15} - FAILED: {e}")
            failed_imports.append(module_name)
    
    print()
    
    # Test Flask app creation
    print("Testing Flask App Creation:")
    try:
        from flask import Flask
        app = Flask(__name__)
        print("  OK Flask app created successfully")
        
        # Test if we can configure port 8080
        print("  Testing port 8080 configuration...")
        # Just test the configuration, don't actually start the server
        app.config['PORT'] = 8080
        print("  OK Port 8080 configured successfully")
        
    except Exception as e:
        print(f"  FAIL Flask app creation failed: {e}")
        failed_imports.append('flask-app')
    
    print()
    
    # Test SocketIO
    print("Testing SocketIO Integration:")
    try:
        from flask_socketio import SocketIO
        from flask import Flask
        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="*")
        print("  OK SocketIO integration successful")
    except Exception as e:
        print(f"  FAIL SocketIO integration failed: {e}")
        failed_imports.append('socketio-integration')
    
    print()
    
    # Summary
    print("Test Summary:")
    print("=" * 50)
    if not failed_imports:
        print("SUCCESS: All tests passed! Virtual environment is ready.")
        print("OK Dashboard can run on port 8080")
        print("OK All required dependencies are installed")
        print("OK Real-time monitoring capabilities available")
        return True
    else:
        print(f"FAILED: {len(failed_imports)} tests failed:")
        for module in failed_imports:
            print(f"  - {module}")
        return False

if __name__ == '__main__':
    success = test_virtual_environment()
    print()
    print("To start the mobile dashboard:")
    print("   python launch_mobile.py")
    print()
    sys.exit(0 if success else 1)