#!/usr/bin/env python3
"""
Claude Code Dev Stack v3.0 - Environment Setup
Automatically creates and configures virtual environment
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class EnvironmentSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_dir = self.base_dir / 'venv'
        self.platform = platform.system().lower()
        self.python_cmd = sys.executable
        
    def create_venv(self):
        """Create virtual environment"""
        print("[INFO] Creating virtual environment...")
        try:
            subprocess.run([self.python_cmd, '-m', 'venv', str(self.venv_dir)], check=True)
            print("[OK] Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to create virtual environment: {e}")
            return False
    
    def get_activation_script(self):
        """Get the correct activation script based on platform"""
        if self.platform == 'windows':
            activate_script = self.venv_dir / 'Scripts' / 'activate.bat'
            activate_ps = self.venv_dir / 'Scripts' / 'Activate.ps1'
            pip_exe = self.venv_dir / 'Scripts' / 'pip.exe'
            python_exe = self.venv_dir / 'Scripts' / 'python.exe'
        else:
            activate_script = self.venv_dir / 'bin' / 'activate'
            activate_ps = None
            pip_exe = self.venv_dir / 'bin' / 'pip'
            python_exe = self.venv_dir / 'bin' / 'python'
            
        return {
            'activate': activate_script,
            'activate_ps': activate_ps,
            'pip': pip_exe,
            'python': python_exe
        }
    
    def install_requirements(self):
        """Install Python requirements"""
        scripts = self.get_activation_script()
        pip_cmd = str(scripts['pip'])
        
        print("[INSTALL] Installing Python requirements...")
        
        # Core requirements
        core_requirements = [
            'flask>=2.3.0',
            'flask-cors>=4.0.0',
            'flask-socketio>=5.3.0',
            'python-socketio>=5.10.0',
            'websocket-client>=1.6.0',
            'requests>=2.31.0',
            'pyyaml>=6.0',
            'python-dotenv>=1.0.0',
            'watchdog>=3.0.0',
            'colorama>=0.4.6',
            'rich>=13.7.0',
            'click>=8.1.0',
            'jinja2>=3.1.0',
            'markdown>=3.5.0',
            'pygments>=2.17.0',
            'numpy>=1.24.0',
            'pandas>=2.0.0',
            'matplotlib>=3.7.0',
            'plotly>=5.18.0',
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.12.0',
            'flake8>=6.1.0',
            'mypy>=1.7.0',
            'coverage>=7.3.0'
        ]
        
        # MCP related requirements
        mcp_requirements = [
            'anthropic-mcp>=0.1.0',
            'openapi-spec-validator>=0.6.0',
            'openapi-core>=0.18.0',
            'pydantic>=2.5.0',
            'fastapi>=0.104.0',
            'uvicorn>=0.24.0',
            'httpx>=0.25.0'
        ]
        
        # Audio and voice requirements
        audio_requirements = [
            'pydub>=0.25.1',
            'simpleaudio>=1.0.4',
            'sounddevice>=0.4.6',
            'scipy>=1.11.0',
            'speechrecognition>=3.10.0',
            'pyaudio>=0.2.13'
        ]
        
        all_requirements = core_requirements + mcp_requirements + audio_requirements
        
        for package in all_requirements:
            try:
                subprocess.run([pip_cmd, 'install', package], check=True, capture_output=True)
                print(f"  [OK] Installed {package}")
            except subprocess.CalledProcessError:
                print(f"  [WARN] Failed to install {package}, continuing...")
        
        print("[OK] Requirements installation complete")
        
    def create_activation_scripts(self):
        """Create convenient activation scripts"""
        print("[INFO] Creating activation scripts...")
        
        # Windows batch script
        activate_bat = self.base_dir / 'activate.bat'
        activate_bat.write_text(
            f'@echo off\n'
            f'call "{self.venv_dir}\\Scripts\\activate.bat"\n'
            f'echo Virtual environment activated for Claude Code Dev Stack v3.0\n'
            f'echo Python: %VIRTUAL_ENV%\\Scripts\\python.exe\n'
            f'echo.\n'
            f'echo To deactivate, type: deactivate\n'
        )
        
        # Windows PowerShell script
        activate_ps1 = self.base_dir / 'activate.ps1'
        activate_ps1.write_text(
            f'& "{self.venv_dir}\\Scripts\\Activate.ps1"\n'
            f'Write-Host "Virtual environment activated for Claude Code Dev Stack v3.0" -ForegroundColor Green\n'
            f'Write-Host "Python: $env:VIRTUAL_ENV\\Scripts\\python.exe" -ForegroundColor Cyan\n'
            f'Write-Host ""\n'
            f'Write-Host "To deactivate, type: deactivate" -ForegroundColor Yellow\n'
        )
        
        # Unix/Linux/Mac script
        activate_sh = self.base_dir / 'activate.sh'
        activate_sh.write_text(
            f'#!/bin/bash\n'
            f'source "{self.venv_dir}/bin/activate"\n'
            f'echo "Virtual environment activated for Claude Code Dev Stack v3.0"\n'
            f'echo "Python: $VIRTUAL_ENV/bin/python"\n'
            f'echo ""\n'
            f'echo "To deactivate, type: deactivate"\n'
        )
        
        if self.platform != 'windows':
            os.chmod(activate_sh, 0o755)
        
        print("[OK] Activation scripts created")
        
    def create_requirements_txt(self):
        """Create requirements.txt for easy installation"""
        requirements_content = """# Claude Code Dev Stack v3.0 - Python Requirements
# Auto-generated by setup_environment.py

# Core Requirements
flask>=2.3.0
flask-cors>=4.0.0
flask-socketio>=5.3.0
python-socketio>=5.10.0
websocket-client>=1.6.0
requests>=2.31.0
pyyaml>=6.0
python-dotenv>=1.0.0
watchdog>=3.0.0
colorama>=0.4.6
rich>=13.7.0
click>=8.1.0
jinja2>=3.1.0
markdown>=3.5.0
pygments>=2.17.0

# Data Processing
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
plotly>=5.18.0

# Testing & Quality
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.12.0
flake8>=6.1.0
mypy>=1.7.0
coverage>=7.3.0

# MCP Integration
# anthropic-mcp>=0.1.0  # Uncomment when available
openapi-spec-validator>=0.6.0
openapi-core>=0.18.0
pydantic>=2.5.0
fastapi>=0.104.0
uvicorn>=0.24.0
httpx>=0.25.0

# Audio & Voice
pydub>=0.25.1
simpleaudio>=1.0.4
sounddevice>=0.4.6
scipy>=1.11.0
SpeechRecognition>=3.10.0
# PyAudio>=0.2.13  # May require manual installation on some systems
"""
        
        requirements_file = self.base_dir / 'requirements.txt'
        requirements_file.write_text(requirements_content)
        print("[OK] requirements.txt created")
        
    def create_venv_info(self):
        """Create venv info JSON for other tools to use"""
        scripts = self.get_activation_script()
        
        venv_info = {
            'venv_dir': str(self.venv_dir),
            'python': str(scripts['python']),
            'pip': str(scripts['pip']),
            'activate_cmd': f'"{scripts["activate"]}"' if self.platform == 'windows' else f'source "{scripts["activate"]}"',
            'platform': self.platform,
            'created': True
        }
        
        info_file = self.base_dir / 'venv_info.json'
        with open(info_file, 'w') as f:
            json.dump(venv_info, f, indent=2)
        
        print("[OK] venv_info.json created")
        
    def setup(self):
        """Run complete setup"""
        print("=" * 60)
        print("[SETUP] Claude Code Dev Stack v3.0 - Environment Setup")
        print("=" * 60)
        print(f"[DIR] Base directory: {self.base_dir}")
        print(f"[OS] Platform: {self.platform}")
        print(f"[PYTHON] Python: {self.python_cmd}")
        print("=" * 60)
        
        # Check if venv already exists
        if self.venv_dir.exists():
            print("[WARN] Virtual environment already exists")
            response = input("Do you want to recreate it? (y/n): ")
            if response.lower() != 'y':
                print("Skipping venv creation...")
            else:
                import shutil
                shutil.rmtree(self.venv_dir)
                self.create_venv()
        else:
            self.create_venv()
        
        if self.venv_dir.exists():
            self.create_requirements_txt()
            self.install_requirements()
            self.create_activation_scripts()
            self.create_venv_info()
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Environment setup complete!")
            print("=" * 60)
            print("\n[INFO] To activate the virtual environment:")
            
            if self.platform == 'windows':
                print("   Command Prompt: activate.bat")
                print("   PowerShell: .\\activate.ps1")
            else:
                print("   Bash/Zsh: source activate.sh")
            
            print("\n[INFO] To install requirements manually:")
            scripts = self.get_activation_script()
            print(f"   {scripts['pip']} install -r requirements.txt")
            
            print("\n[READY] Ready to run Claude Code Dev Stack v3.0!")
            print("=" * 60)

if __name__ == '__main__':
    setup = EnvironmentSetup()
    setup.setup()