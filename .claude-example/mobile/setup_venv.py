#!/usr/bin/env python3
"""
Claude Code Mobile Virtual Environment Setup Script
Creates and configures the virtual environment with all required dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

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
        # Fallback: replace problematic characters
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def setup_virtual_environment():
    """Setup complete virtual environment for Claude Code mobile monitoring"""
    
    current_dir = Path(__file__).parent
    venv_dir = current_dir / '.venv'
    requirements_file = current_dir / 'requirements.txt'
    
    safe_print("🚀 Setting up Claude Code Mobile Virtual Environment...")
    safe_print("=" * 60)
    
    # Step 1: Create virtual environment
    if venv_dir.exists():
        safe_print("⚠️ Virtual environment already exists, skipping creation...")
    else:
        safe_print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', '.venv'], 
                          cwd=current_dir, check=True)
            safe_print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError as e:
            safe_print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    # Step 2: Get virtual environment Python
    if sys.platform.startswith('win'):
        venv_python = venv_dir / 'Scripts' / 'python.exe'
        venv_pip = venv_dir / 'Scripts' / 'pip.exe'
    else:
        venv_python = venv_dir / 'bin' / 'python'
        venv_pip = venv_dir / 'bin' / 'pip'
    
    if not venv_python.exists():
        safe_print("❌ Virtual environment Python not found")
        return False
    
    safe_print(f"🐍 Using Python: {venv_python}")
    
    # Step 3: Upgrade pip
    safe_print("⬆️ Upgrading pip...")
    try:
        subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        safe_print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        safe_print(f"⚠️ Warning: Failed to upgrade pip: {e}")
    
    # Step 4: Install requirements
    if requirements_file.exists():
        safe_print("📋 Installing dependencies from requirements.txt...")
        try:
            result = subprocess.run([
                str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)
            ], check=True, capture_output=True, text=True)
            safe_print("✅ All dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            safe_print(f"❌ Failed to install dependencies: {e}")
            safe_print(f"Error output: {e.stderr}")
            return False
    else:
        safe_print("⚠️ requirements.txt not found, installing basic packages...")
        basic_packages = [
            'flask>=2.3.0',
            'flask-socketio>=5.3.0',
            'flask-cors>=2.0.0',
            'python-socketio>=5.8.0',
            'eventlet>=0.33.0',
            'GitPython>=3.1.0',
            'watchdog>=3.0.0',
            'psutil>=5.9.0',
            'qrcode[pil]>=7.4.0',
            'requests>=2.31.0'
        ]
        
        for package in basic_packages:
            try:
                subprocess.run([str(venv_python), '-m', 'pip', 'install', package], 
                              check=True, capture_output=True)
                safe_print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                safe_print(f"⚠️ Failed to install {package}: {e}")
    
    # Step 5: Test imports
    safe_print("\n🧪 Testing critical imports...")
    test_imports = [
        'flask', 'flask_socketio', 'flask_cors', 'socketio', 
        'eventlet', 'git', 'watchdog', 'psutil', 'qrcode', 'requests'
    ]
    
    failed_imports = []
    for module in test_imports:
        try:
            result = subprocess.run([
                str(venv_python), '-c', f'import {module}; print("OK {module}")'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                safe_print(f"✅ {module}")
            else:
                safe_print(f"❌ Failed to import {module}")
                failed_imports.append(module)
        except Exception as e:
            safe_print(f"❌ Error testing {module}: {e}")
            failed_imports.append(module)
    
    # Step 6: Generate activation instructions
    safe_print("\n" + "=" * 60)
    safe_print("🎉 Virtual Environment Setup Complete!")
    safe_print("=" * 60)
    
    if failed_imports:
        safe_print("⚠️ Some imports failed: " + ', '.join(failed_imports))
        safe_print("You may need to install additional dependencies.")
    else:
        safe_print("✅ All critical imports working!")
    
    safe_print("\n📋 Activation Instructions:")
    safe_print("Windows CMD:")
    safe_print(f"   cd \"{current_dir}\"")
    safe_print("   activate.bat")
    safe_print("\nWindows PowerShell:")
    safe_print(f"   cd \"{current_dir}\"")
    safe_print("   .\\activate.ps1")
    safe_print("\nDirect activation:")
    safe_print(f"   {venv_dir / 'Scripts' / 'activate.bat'}")
    
    safe_print("\n🚀 Usage:")
    safe_print("   python launch_mobile.py  # Start mobile dashboard")
    safe_print("   pip list                 # Show installed packages")
    safe_print("   deactivate               # Exit virtual environment")
    
    # Step 7: Create activation info file
    activation_info = {
        "venv_path": str(venv_dir),
        "python_path": str(venv_python),
        "pip_path": str(venv_pip),
        "created": True,
        "tested_imports": [m for m in test_imports if m not in failed_imports],
        "failed_imports": failed_imports
    }
    
    info_file = current_dir / 'venv_info.json'
    with open(info_file, 'w') as f:
        json.dump(activation_info, f, indent=2)
    
    safe_print(f"\n💾 Environment info saved to: {info_file}")
    
    return len(failed_imports) == 0

if __name__ == '__main__':
    success = setup_virtual_environment()
    sys.exit(0 if success else 1)