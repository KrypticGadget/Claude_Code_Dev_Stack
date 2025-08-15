#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Mobile Launcher - V3.0+ One-Line Mobile Access
Single command to securely start dashboard, tunnel, and send access to phone
"""

import os
import sys
import json
import time
import uuid
import secrets
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

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

# Ensure we're using the virtual environment Python
def ensure_virtual_environment():
    """Ensure we're running in the virtual environment and create it if missing"""
    current_dir = Path(__file__).parent
    venv_dir = current_dir / '.venv'
    venv_python = venv_dir / 'Scripts' / 'python.exe'
    venv_activate = venv_dir / 'Scripts' / 'activate.bat'
    
    # Step 1: Create virtual environment if it doesn't exist
    if not venv_dir.exists() or not venv_python.exists():
        safe_print("🔧 Creating virtual environment...")
        try:
            # Create virtual environment using system Python
            result = subprocess.run([
                sys.executable, '-m', 'venv', str(venv_dir)
            ], check=True, capture_output=True, text=True)
            
            safe_print("✅ Virtual environment created successfully")
            
            # Upgrade pip in the new environment
            safe_print("📦 Upgrading pip...")
            subprocess.run([
                str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True, text=True)
            
        except subprocess.CalledProcessError as e:
            safe_print(f"❌ Failed to create virtual environment: {e}")
            safe_print(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No error details'}")
            return False
    
    # Step 2: Check if we're already in the virtual environment
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        sys.executable == str(venv_python)
    )
    
    if in_venv:
        safe_print("✅ Already running in virtual environment")
        return True
    
    # Step 3: If virtual environment exists and we're not in it, restart with venv python
    if venv_python.exists() and sys.executable != str(venv_python):
        safe_print("🔄 Switching to virtual environment...")
        try:
            # Restart the script with virtual environment Python
            result = subprocess.run([str(venv_python)] + sys.argv, capture_output=False)
            sys.exit(result.returncode)
        except subprocess.CalledProcessError as e:
            safe_print(f"❌ Failed to start with virtual environment: {e}")
            return False
    
    return True

# Ensure virtual environment is active
ensure_virtual_environment()

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / 'dashboard'))
sys.path.append(str(Path(__file__).parent.parent / 'tunnels'))
sys.path.append(str(Path(__file__).parent.parent / 'hooks'))

class SecureMobileLauncher:
    """One-liner secure mobile access launcher"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.mobile_dir = Path(__file__).parent
        self.mobile_dir.mkdir(exist_ok=True)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Security settings
        self.session_timeout = 24 * 60 * 60  # 24 hours
        self.auth_token = None
        self.tunnel_url = None
        self.dashboard_port = 8080
        self.ttyd_port = 7681
        self.use_enhanced_dashboard = True
        
        # Processes
        self.dashboard_process = None
        self.tunnel_process = None
        self.display_thread = None
        self.ttyd_process = None
        self.realtime_dashboard_process = None
        
        # Mobile access info
        self.mobile_access_file = self.mobile_dir / 'current_access.json'
    
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
    
    def generate_auth_token(self) -> str:
        """Generate secure authentication token"""
        # Create a strong random token
        token = secrets.token_urlsafe(32)
        
        # Add timestamp for expiry
        timestamp = int(time.time())
        
        # Combine token with timestamp
        auth_data = {
            'token': token,
            'created': timestamp,
            'expires': timestamp + self.session_timeout,
            'session_id': str(uuid.uuid4())
        }
        
        # Save token for dashboard authentication
        token_file = self.mobile_dir / 'auth_tokens.json'
        
        # Load existing tokens
        tokens = {}
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
            except:
                pass
        
        # Clean expired tokens
        current_time = int(time.time())
        tokens = {k: v for k, v in tokens.items() if v.get('expires', 0) > current_time}
        
        # Add new token
        tokens[token] = auth_data
        
        # Save tokens
        try:
            with open(token_file, 'w') as f:
                json.dump(tokens, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save auth token: {e}")
        
        self.auth_token = token
        return token
    
    def download_component(self, component_name: str, file_name: str) -> bool:
        """Download component from GitHub if not exists"""
        component_dir = self.mobile_dir / component_name
        component_dir.mkdir(exist_ok=True)
        
        file_path = component_dir / file_name
        if file_path.exists():
            return True
            
        try:
            safe_print(f"📥 Downloading {component_name}/{file_name}...")
            import requests
            url = f"https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/{component_name}/{file_name}"
            response = requests.get(url)
            response.raise_for_status()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            safe_print(f"✅ Downloaded {file_name}")
            return True
        except Exception as e:
            safe_print(f"❌ Failed to download {file_name}: {e}")
            return False

    def install_dependencies(self, packages: list) -> bool:
        """Install required Python packages in virtual environment"""
        try:
            # Ensure we're using virtual environment Python
            venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
            if not venv_python.exists():
                safe_print("❌ Virtual environment not found! Creating...")
                if not ensure_virtual_environment():
                    return False
                    
            python_exe = str(venv_python)
            
            safe_print(f"📦 Installing dependencies in virtual environment...")
            safe_print(f"🐍 Using Python: {python_exe}")
            
            # First, ensure pip is up to date
            safe_print("🔧 Updating pip...")
            try:
                result = subprocess.run([
                    python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    safe_print("✅ pip updated successfully")
                else:
                    safe_print(f"⚠️ Warning: Failed to update pip: {result.stderr[:200]}")
            except Exception as e:
                safe_print(f"⚠️ Error updating pip: {e}")
            
            # Check if requirements.txt exists and install from it
            requirements_file = self.mobile_dir / 'requirements.txt'
            if requirements_file.exists():
                safe_print("📋 Installing from requirements.txt...")
                try:
                    result = subprocess.run([
                        python_exe, '-m', 'pip', 'install', '-r', str(requirements_file), '--upgrade'
                    ], capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        safe_print("✅ All requirements installed from requirements.txt")
                        return True
                    else:
                        safe_print(f"⚠️ Warning: Failed to install from requirements.txt:")
                        safe_print(f"   Error: {result.stderr[:500] if result.stderr else 'No error details'}")
                        safe_print(f"   Output: {result.stdout[:500] if result.stdout else 'No output'}")
                        # Continue with individual package installation
                except subprocess.TimeoutExpired:
                    safe_print("⚠️ Timeout installing from requirements.txt, trying individual packages...")
                except Exception as e:
                    safe_print(f"⚠️ Error with requirements.txt: {e}")
            
            # Fallback to individual package installation with essential packages
            essential_packages = [
                'flask>=2.3.0',
                'flask-socketio>=5.3.0', 
                'psutil>=5.9.0',
                'requests>=2.31.0',
                'qrcode[pil]>=7.4.0',
                'watchdog>=3.0.0',
                'GitPython>=3.1.0'
            ]
            
            # Use essential packages if provided packages list is empty
            packages_to_install = packages if packages else essential_packages
            
            safe_print("📦 Installing essential packages individually...")
            for package in packages_to_install:
                try:
                    safe_print(f"   Installing {package}...")
                    result = subprocess.run([
                        python_exe, '-m', 'pip', 'install', package, '--upgrade'
                    ], capture_output=True, text=True, timeout=180)
                    
                    if result.returncode == 0:
                        safe_print(f"✅ Installed {package}")
                    else:
                        safe_print(f"⚠️ Warning: Failed to install {package}: {result.stderr[:200] if result.stderr else 'No error'}")
                        
                except subprocess.TimeoutExpired:
                    safe_print(f"⚠️ Timeout installing {package}")
                except Exception as e:
                    safe_print(f"⚠️ Error installing {package}: {e}")
            
            return True
            
        except Exception as e:
            safe_print(f"❌ Error during dependency installation: {e}")
            return False

    def start_enhanced_dashboard(self) -> bool:
        """Start enhanced dashboard with real-time monitoring and ttyd terminal"""
        try:
            safe_print("🚀 Starting Enhanced Dashboard with Real-time Monitoring...")
            
            # Step 1: Download required components
            components = [
                ('dashboard', 'realtime_dashboard.py'),
                ('dashboard', 'monitors.py'),
                ('dashboard', 'ttyd_manager.py')
            ]
            
            for component_dir, filename in components:
                if not self.download_component(component_dir, filename):
                    safe_print(f"❌ Failed to download {filename}, falling back to secure dashboard...")
                    return self.start_secure_dashboard()
            
            # Step 2: Install dependencies
            dependencies = [
                'flask',
                'flask-socketio',
                'flask-cors',
                'gitpython',
                'watchdog',
                'psutil'
            ]
            
            self.install_dependencies(dependencies)
            
            # Step 3: Generate auth token
            auth_token = self.generate_auth_token()
            
            # Step 4: Start ttyd terminal manager
            safe_print("🖥️ Starting ttyd terminal manager...")
            ttyd_script = self.mobile_dir / 'dashboard' / 'ttyd_manager.py'
            
            if ttyd_script.exists():
                try:
                    # Use virtual environment Python
                    venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
                    python_exe = str(venv_python)
                    
                    # Set environment for ttyd manager
                    env = os.environ.copy()
                    env['CLAUDE_MOBILE_AUTH_TOKEN'] = auth_token
                    env['CLAUDE_MOBILE_AUTH_DIR'] = str(self.mobile_dir)
                    
                    self.ttyd_process = subprocess.Popen([
                        python_exe, str(ttyd_script),
                        '--port', str(self.ttyd_port),
                        '--auth', auth_token
                    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    # Wait for ttyd to start
                    time.sleep(3)
                    
                    if self.ttyd_process.poll() is None:
                        safe_print(f"✅ ttyd terminal manager started on port {self.ttyd_port}")
                    else:
                        safe_print("⚠️ ttyd terminal manager failed to start (continuing without terminal)")
                        self.ttyd_process = None
                        
                except Exception as e:
                    safe_print(f"⚠️ Error starting ttyd manager: {e}")
                    self.ttyd_process = None
            
            # Step 5: Start real-time dashboard
            safe_print("📊 Starting real-time dashboard...")
            dashboard_script = self.mobile_dir / 'dashboard' / 'realtime_dashboard.py'
            
            # Use virtual environment Python
            venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
            python_exe = str(venv_python)
            
            # Set environment variables for dashboard
            env = os.environ.copy()
            env['CLAUDE_MOBILE_AUTH_TOKEN'] = auth_token
            env['CLAUDE_MOBILE_AUTH_DIR'] = str(self.mobile_dir)
            env['TTYD_PORT'] = str(self.ttyd_port)
            env['DASHBOARD_PORT'] = str(self.dashboard_port)
            
            self.realtime_dashboard_process = subprocess.Popen([
                python_exe, str(dashboard_script),
                '--port', str(self.dashboard_port),
                '--auth', auth_token,
                '--ttyd-port', str(self.ttyd_port)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for dashboard to start
            time.sleep(5)
            
            # Check if dashboard is running
            if self.realtime_dashboard_process.poll() is None:
                safe_print(f"✅ Enhanced dashboard started on port {self.dashboard_port}")
                safe_print(f"📊 Real-time monitoring: http://localhost:{self.dashboard_port}")
                safe_print(f"🖥️ Terminal access: http://localhost:{self.ttyd_port}")
                return True
            else:
                stdout, stderr = self.realtime_dashboard_process.communicate()
                safe_print("❌ Enhanced dashboard failed to start:")
                if stdout:
                    safe_print(f"stdout: {stdout.decode()[:500]}")
                if stderr:
                    safe_print(f"stderr: {stderr.decode()[:500]}")
                
                # Fallback to secure dashboard
                safe_print("🔄 Falling back to secure dashboard...")
                return self.start_secure_dashboard()
                
        except Exception as e:
            safe_print(f"❌ Error starting enhanced dashboard: {e}")
            safe_print("🔄 Falling back to secure dashboard...")
            return self.start_secure_dashboard()

    def start_secure_dashboard(self) -> bool:
        """Start dashboard with authentication (fallback method)"""
        try:
            # Download dashboard components if needed
            # Try simple dashboard first
            if not self.download_component('dashboard', 'simple_dashboard.py'):
                safe_print("⚠️ Could not download simple dashboard, trying complex version...")
                if not self.download_component('dashboard', 'dashboard_server.py'):
                    return False
            
            # Generate auth token if not already generated
            if not self.auth_token:
                auth_token = self.generate_auth_token()
            else:
                auth_token = self.auth_token
            
            safe_print("🔒 Starting secure dashboard with authentication...")
            
            # Use virtual environment Python
            venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
            python_exe = str(venv_python)
            
            # Set environment variable for dashboard authentication
            env = os.environ.copy()
            env['CLAUDE_MOBILE_AUTH_TOKEN'] = auth_token
            env['CLAUDE_MOBILE_AUTH_DIR'] = str(self.mobile_dir)
            
            # Try simple dashboard first
            simple_dashboard = self.mobile_dir / 'dashboard' / 'simple_dashboard.py'
            dashboard_script = self.mobile_dir / 'dashboard' / 'dashboard_server.py'
            
            if simple_dashboard.exists():
                script_to_use = simple_dashboard
                safe_print("Using simple dashboard (no complex dependencies)...")
            elif dashboard_script.exists():
                script_to_use = dashboard_script
                safe_print("Using full dashboard...")
            else:
                safe_print("❌ No dashboard script found")
                return False
            
            self.dashboard_process = subprocess.Popen([
                python_exe, str(script_to_use),
                '--mobile-auth', auth_token,
                '--port', str(self.dashboard_port)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for dashboard to start
            time.sleep(3)
            
            # Check if dashboard is running
            if self.dashboard_process.poll() is None:
                safe_print(f"✅ Dashboard started securely on port {self.dashboard_port}")
                return True
            else:
                stdout, stderr = self.dashboard_process.communicate()
                safe_print(f"❌ Dashboard failed to start:")
                if stdout:
                    print(f"stdout: {stdout.decode()[:500]}")
                if stderr:
                    print(f"stderr: {stderr.decode()[:500]}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Error starting dashboard: {e}")
            return False
    
    def start_tunnel(self) -> Optional[str]:
        """Start tunnel and return public URL"""
        try:
            # Check if ngrok auth token is set
            auth_token = os.environ.get('NGROK_AUTH_TOKEN')
            if not auth_token:
                safe_print("\n⚠️ ngrok auth token not found in environment")
                safe_print("Please set NGROK_AUTH_TOKEN environment variable or run the launcher again")
                return None
            
            safe_print("🌐 Starting secure tunnel with ngrok...")
            
            # Try to start ngrok directly first
            ngrok_paths = [
                Path.home() / "ngrok" / "ngrok.exe",
                Path.home() / "ngrok.exe",
                Path("C:/Users") / os.environ.get('USERNAME', 'User') / "ngrok" / "ngrok.exe",
                Path("C:/Users") / os.environ.get('USERNAME', 'User') / "ngrok.exe"
            ]
            
            ngrok_exe = None
            for path in ngrok_paths:
                if path.exists():
                    ngrok_exe = str(path)
                    break
            
            if ngrok_exe:
                safe_print(f"✅ Found ngrok at: {ngrok_exe}")
                
                # Start ngrok directly with the auth token
                ngrok_cmd = [ngrok_exe, "http", str(self.dashboard_port), "--authtoken", auth_token]
                
                # Start ngrok in background
                self.tunnel_process = subprocess.Popen(
                    ngrok_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for ngrok to start
                time.sleep(5)
                
                # Get tunnel URL from ngrok API
                try:
                    import requests
                    response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        tunnels = data.get('tunnels', [])
                        for tunnel in tunnels:
                            if tunnel.get('proto') == 'https':
                                self.tunnel_url = tunnel.get('public_url')
                                safe_print(f"✅ Tunnel started: {self.tunnel_url}")
                                return self.tunnel_url
                except:
                    pass
                
                safe_print("⚠️ Tunnel started but couldn't get URL - check http://localhost:4040")
                return "http://localhost:8080"  # Fallback to local
            
            # Fallback to tunnel manager if ngrok not found directly
            safe_print("⚠️ ngrok not found, trying tunnel manager...")
            
            # Download tunnel components if needed
            if not self.download_component('tunnels', 'tunnel_manager.py'):
                return None
            
            # Start tunnel manager
            tunnel_script = self.mobile_dir / 'tunnels' / 'tunnel_manager.py'
            
            # Use virtual environment Python
            venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
            python_exe = str(venv_python)
            
            # Pass auth token via environment
            env = os.environ.copy()
            env['NGROK_AUTH_TOKEN'] = auth_token
            
            tunnel_cmd = [python_exe, str(tunnel_script), 'start']
            
            result = subprocess.run(tunnel_cmd, capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode == 0:
                # Parse result to get URL
                try:
                    tunnel_result = json.loads(result.stdout)
                    if tunnel_result.get('success'):
                        self.tunnel_url = tunnel_result.get('url')
                        safe_print(f"✅ Tunnel started: {self.tunnel_url}")
                        return self.tunnel_url
                    else:
                        safe_print(f"❌ Tunnel failed: {tunnel_result.get('error')}")
                        return None
                except json.JSONDecodeError:
                    # Try to extract URL from text output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'https://' in line and ('ngrok.io' in line or 'tunnel' in line):
                            url = line.split('https://')[1].split()[0]
                            self.tunnel_url = f"https://{url}"
                            safe_print(f"✅ Tunnel started: {self.tunnel_url}")
                            return self.tunnel_url
                    
                    print("❌ Could not extract tunnel URL from output")
                    return None
            else:
                safe_print(f"❌ Tunnel command failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Tunnel startup timed out")
            return None
        except Exception as e:
            safe_print(f"❌ Error starting tunnel: {e}")
            return None
    
    def generate_qr_code(self, url: str, auth_token: str) -> str:
        """Generate QR code for mobile access"""
        try:
            import qrcode
            from io import BytesIO
            import base64
            
            # Create QR code with just the tunnel URL (no auth parameter)
            # The dashboard doesn't understand the auth parameter
            qr_data = url
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            qr_file = self.mobile_dir / 'mobile_access_qr.png'
            img.save(qr_file)
            
            safe_print(f"📱 QR code saved: {qr_file}")
            
            # Also create ASCII QR for terminal display
            qr_ascii = qrcode.QRCode()
            qr_ascii.add_data(url)  # Just the URL, no auth
            qr_ascii.make()
            
            # Print ASCII QR code
            print("\n📱 QR Code for Mobile Access:")
            print("=" * 50)
            qr_ascii.print_ascii(invert=True)
            print("=" * 50)
            
            return str(qr_file)
            
        except ImportError:
            safe_print("⚠️  QR code generation requires 'qrcode' package")
            print("Install with: pip install qrcode[pil]")
            return ""
        except Exception as e:
            safe_print(f"⚠️  Error generating QR code: {e}")
            return ""
    
    def send_to_phone(self, url: str, auth_token: str) -> bool:
        """Send secure access info to phone"""
        try:
            # Import notification sender
            from notification_sender import get_sender
            
            sender = get_sender()
            
            # Create secure message
            message = f"""🚀 Claude Code V3+ Mobile Access Ready!

🔗 URL: {url}
🔐 Auth: {auth_token}

📱 Quick Access:
{url}?auth={auth_token}

⏰ Expires: {datetime.fromtimestamp(int(time.time()) + self.session_timeout).strftime('%Y-%m-%d %H:%M')}

🛡️ This is a secure, temporary access link."""
            
            # Send high-priority notification
            success = sender.send_custom(
                title="🚀 Claude Code Mobile Access",
                message=message,
                priority=2  # High priority
            )
            
            if success:
                safe_print("📱 Secure access info sent to phone!")
                return True
            else:
                safe_print("⚠️  Could not send to phone - check notification settings")
                return False
                
        except Exception as e:
            safe_print(f"⚠️  Error sending to phone: {e}")
            return False
    
    def save_mobile_access_info(self, url: str, auth_token: str, qr_file: str = ""):
        """Save current mobile access information"""
        access_info = {
            'url': url,
            'auth_token': auth_token,
            'qr_file': qr_file,
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat(),
            'dashboard_port': self.dashboard_port,
            'session_id': str(uuid.uuid4())
        }
        
        try:
            with open(self.mobile_access_file, 'w') as f:
                json.dump(access_info, f, indent=2)
            print(f"💾 Access info saved: {self.mobile_access_file}")
        except Exception as e:
            safe_print(f"⚠️  Could not save access info: {e}")
    
    def display_access_info(self, url: str, auth_token: str):
        """Display mobile access information in browser"""
        try:
            # Download display server if needed
            if not self.download_component('mobile', 'mobile_display_server.py'):
                # Fallback to terminal display
                print("\n" + "=" * 60)
                safe_print("🚀 CLAUDE CODE V3+ MOBILE ACCESS READY!")
                print("=" * 60)
                safe_print(f"📱 Mobile URL: {url}")
                safe_print(f"🔐 Auth Token: {auth_token}")
                safe_print(f"🌐 Quick Link: {url}?auth={auth_token}")
                return
            
            # Import and start display server
            import webbrowser
            import base64
            from io import BytesIO
            
            # Prepare access information
            access_info = {
                'url': url,
                'auth_token': auth_token,
                'expires': datetime.fromtimestamp(int(time.time()) + self.session_timeout).strftime('%Y-%m-%d %H:%M'),
                'dashboard_port': self.dashboard_port
            }
            
            # Add QR code as base64 if available
            qr_file = self.mobile_dir / 'mobile_access_qr.png'
            if qr_file.exists():
                with open(qr_file, 'rb') as f:
                    qr_data = f.read()
                    access_info['qr_code_base64'] = base64.b64encode(qr_data).decode('utf-8')
            
            # Import display server module
            sys.path.append(str(self.mobile_dir))
            from mobile_display_server import start_display_server
            
            # Start display server on port 5555 (safe port)
            safe_print("\n" + "=" * 60)
            safe_print("🌐 Starting mobile access portal...")
            display_thread = start_display_server(access_info, port=5555)
            
            # Keep reference to thread
            self.display_thread = display_thread
            
            # Give clear instructions
            safe_print("\n✅ MOBILE ACCESS PORTAL READY!")
            safe_print("=" * 60)
            safe_print("📱 Open this URL in your browser:")
            safe_print("   http://localhost:5555")
            safe_print("")
            safe_print("🔗 This page will show:")
            safe_print("   • QR code for mobile scanning")
            safe_print("   • Tunnel URL: " + url)
            safe_print("   • Auth token for secure access")
            safe_print("   • Copy buttons for easy access")
            safe_print("=" * 60)
            
        except Exception as e:
            safe_print(f"⚠️ Could not start web display: {e}")
            # Fallback to terminal display
            print("\n" + "=" * 60)
            safe_print("🚀 CLAUDE CODE V3+ MOBILE ACCESS READY!")
            print("=" * 60)
            safe_print(f"📱 Mobile URL: {url}")
            safe_print(f"🔐 Auth Token: {auth_token}")
            safe_print(f"🌐 Quick Link: {url}?auth={auth_token}")
    
    def launch(self, send_to_phone: bool = True, generate_qr: bool = True, local_only: bool = False) -> bool:
        """Main launch function - the one-liner entry point"""
        safe_print("🚀 Starting Claude Code V3+ Enhanced Mobile Access...")
        safe_print("=" * 60)
        
        try:
            # Step 1: Start enhanced dashboard (with fallback to secure dashboard)
            if not self.start_enhanced_dashboard():
                print("❌ Failed to start dashboard")
                return False
            
            # Step 2: Start tunnel (unless local_only mode)
            tunnel_url = None
            if not local_only:
                tunnel_url = self.start_tunnel()
                if not tunnel_url:
                    safe_print("⚠️ Tunnel failed, running in local-only mode")
                    local_only = True
            
            # Use local URL if no tunnel
            if local_only or not tunnel_url:
                tunnel_url = f"http://localhost:{self.dashboard_port}"
                safe_print(f"🏠 Running in local-only mode: {tunnel_url}")
            
            # Step 3: Generate QR code (only if not local-only)
            qr_file = ""
            if generate_qr and not local_only:
                qr_file = self.generate_qr_code(tunnel_url, self.auth_token)
            
            # Step 4: Send to phone (only if not local-only)
            if send_to_phone and not local_only:
                self.send_to_phone(tunnel_url, self.auth_token)
            
            # Step 5: Save access info
            self.save_mobile_access_info(tunnel_url, self.auth_token, qr_file)
            
            # Step 6: Display info
            if not local_only:
                self.display_access_info(tunnel_url, self.auth_token)
            
            # Success!
            safe_print("\n✅ Enhanced dashboard launched successfully!")
            if local_only:
                safe_print("\n🏠 LOCAL ACCESS ONLY:")
                safe_print(f"   • Dashboard: http://localhost:{self.dashboard_port}")
                safe_print(f"   • Terminal: http://localhost:{self.ttyd_port}")
                safe_print("   • This is only accessible from this computer")
            else:
                safe_print("\n📱 MOBILE ACCESS:")
                safe_print("   • QR code for mobile access")
                safe_print("   • Tunnel URL and auth credentials")
                safe_print("   • Samsung Galaxy S25 Edge instructions")
            safe_print("")
            safe_print("📊 Enhanced features available:")
            safe_print(f"   • Real-time dashboard: {tunnel_url}")
            safe_print(f"   • Terminal access: http://localhost:{self.ttyd_port}")
            safe_print("   • Live system monitoring")
            safe_print("   • File system watching")
            safe_print("   • Git integration")
            safe_print("")
            safe_print("📱 Access URLs:")
            safe_print(f"   Dashboard: {tunnel_url}")
            safe_print(f"   Terminal: http://localhost:{self.ttyd_port}")
            safe_print("")
            print("🔄 Monitoring enhanced system... Press Ctrl+C to stop")
            
            # Keep running and monitor
            self.monitor_system()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down mobile access...")
            self.cleanup()
            return True
        except Exception as e:
            safe_print(f"❌ Error during launch: {e}")
            self.cleanup()
            return False
    
    def monitor_system(self):
        """Monitor dashboard, ttyd terminal, and tunnel"""
        try:
            while True:
                # Check realtime dashboard
                if self.realtime_dashboard_process and self.realtime_dashboard_process.poll() is not None:
                    safe_print("⚠️ Real-time dashboard process stopped")
                    break
                
                # Check ttyd terminal manager
                if self.ttyd_process and self.ttyd_process.poll() is not None:
                    safe_print("⚠️ ttyd terminal manager process stopped")
                    # Continue monitoring other processes
                
                # Check fallback dashboard
                if self.dashboard_process and self.dashboard_process.poll() is not None:
                    safe_print("⚠️ Dashboard process stopped")
                    break
                
                # Sleep and continue monitoring
                time.sleep(10)
                
        except KeyboardInterrupt:
            pass
    
    def cleanup(self):
        """Clean up processes"""
        print("🧹 Cleaning up...")
        
        # Stop realtime dashboard
        if self.realtime_dashboard_process:
            try:
                self.realtime_dashboard_process.terminate()
                self.realtime_dashboard_process.wait(timeout=5)
                print("✅ Real-time dashboard stopped")
            except:
                try:
                    self.realtime_dashboard_process.kill()
                except:
                    pass
        
        # Stop ttyd terminal manager
        if self.ttyd_process:
            try:
                self.ttyd_process.terminate()
                self.ttyd_process.wait(timeout=5)
                print("✅ ttyd terminal manager stopped")
            except:
                try:
                    self.ttyd_process.kill()
                except:
                    pass
        
        # Stop fallback dashboard
        if self.dashboard_process:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
                print("✅ Dashboard stopped")
            except:
                try:
                    self.dashboard_process.kill()
                except:
                    pass
        
        # Stop tunnel (via tunnel manager)
        try:
            tunnel_script = self.mobile_dir / 'tunnels' / 'tunnel_manager.py'
            if tunnel_script.exists():
                # Use virtual environment Python
                venv_python = self.mobile_dir / '.venv' / 'Scripts' / 'python.exe'
                python_exe = str(venv_python)
                subprocess.run([python_exe, str(tunnel_script), 'stop'], timeout=10)
            print("✅ Tunnel stopped")
        except:
            pass
        
        print("✅ Cleanup complete")

def main():
    """Main entry point for one-liner command"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Code V3+ Secure Mobile Launcher')
    parser.add_argument('--no-phone', action='store_true', help='Don\'t send to phone')
    parser.add_argument('--no-qr', action='store_true', help='Don\'t generate QR code')
    parser.add_argument('--port', type=int, default=8080, help='Dashboard port')
    parser.add_argument('--local-only', action='store_true', help='Run in local-only mode (no tunnel)')
    
    args = parser.parse_args()
    
    launcher = SecureMobileLauncher()
    
    if args.port != 8080:
        launcher.dashboard_port = args.port
    
    success = launcher.launch(
        send_to_phone=not args.no_phone,
        generate_qr=not args.no_qr,
        local_only=args.local_only
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()