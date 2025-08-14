#!/usr/bin/env python3
"""
ngrok Tunnel Setup - V3.0+ Remote Access
Automatically configures and manages ngrok tunnels for remote access
"""

import os
import json
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Optional, List
import requests

class NgrokTunnelManager:
    """Manage ngrok tunnels for remote access"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        self.config_dir = self.claude_dir / 'tunnels'
        self.config_dir.mkdir(exist_ok=True)
        
        # ngrok settings
        tunnel_settings = self.settings.get('v3ExtendedFeatures', {}).get('tunnels', {})
        self.ngrok_token = tunnel_settings.get('ngrokToken', os.getenv('NGROK_TOKEN'))
        self.dashboard_port = tunnel_settings.get('dashboardPort', 8080)
        self.tunnel_name = tunnel_settings.get('tunnelName', 'claude-code-dashboard')
        self.subdomain = tunnel_settings.get('subdomain')  # Premium feature
        self.region = tunnel_settings.get('region', 'us')
        
        # Tunnel state
        self.tunnel_process = None
        self.tunnel_url = None
        self.tunnel_info = {}
        self.monitoring = False
    
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
    
    def check_ngrok_installed(self) -> bool:
        """Check if ngrok is installed"""
        try:
            result = subprocess.run(
                ['ngrok', 'version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_ngrok(self) -> bool:
        """Install ngrok (Windows)"""
        if os.name != 'nt':
            print("Automatic ngrok installation only supported on Windows")
            print("Please install ngrok manually: https://ngrok.com/download")
            return False
        
        try:
            print("Installing ngrok...")
            
            # Download ngrok
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            response = requests.get(url)
            
            if response.status_code == 200:
                # Create ngrok directory
                ngrok_dir = Path.home() / 'ngrok'
                ngrok_dir.mkdir(exist_ok=True)
                
                # Save and extract
                zip_path = ngrok_dir / 'ngrok.zip'
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(ngrok_dir)
                
                # Add to PATH
                ngrok_exe = ngrok_dir / 'ngrok.exe'
                if ngrok_exe.exists():
                    # Add to user PATH
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                        try:
                            current_path = winreg.QueryValueEx(key, 'PATH')[0]
                            if str(ngrok_dir) not in current_path:
                                new_path = f"{current_path};{ngrok_dir}"
                                winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                        except FileNotFoundError:
                            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, str(ngrok_dir))
                    
                    print(f"ngrok installed to {ngrok_dir}")
                    print("Please restart your terminal to use ngrok")
                    return True
                
            return False
            
        except Exception as e:
            print(f"Failed to install ngrok: {e}")
            return False
    
    def configure_ngrok(self) -> bool:
        """Configure ngrok with auth token"""
        if not self.ngrok_token:
            print("ngrok auth token not provided")
            print("Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
            return False
        
        try:
            result = subprocess.run(
                ['ngrok', 'config', 'add-authtoken', self.ngrok_token],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("ngrok configured successfully")
                return True
            else:
                print(f"Failed to configure ngrok: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error configuring ngrok: {e}")
            return False
    
    def create_tunnel_config(self) -> Path:
        """Create ngrok tunnel configuration"""
        config = {
            'version': '2',
            'authtoken': self.ngrok_token,
            'tunnels': {
                self.tunnel_name: {
                    'proto': 'http',
                    'addr': self.dashboard_port,
                    'bind_tls': True,
                    'inspect': True
                }
            }
        }
        
        # Add subdomain if provided (premium feature)
        if self.subdomain:
            config['tunnels'][self.tunnel_name]['subdomain'] = self.subdomain
        
        # Add region
        config['tunnels'][self.tunnel_name]['region'] = self.region
        
        # Save config
        config_path = self.config_dir / 'ngrok.yml'
        
        # Convert to YAML format
        yaml_content = f"""version: '2'
authtoken: {self.ngrok_token}
tunnels:
  {self.tunnel_name}:
    proto: http
    addr: {self.dashboard_port}
    bind_tls: true
    inspect: true
    region: {self.region}"""
        
        if self.subdomain:
            yaml_content += f"\\n    subdomain: {self.subdomain}"
        
        with open(config_path, 'w') as f:
            f.write(yaml_content)
        
        return config_path
    
    def start_tunnel(self) -> bool:
        """Start ngrok tunnel"""
        if not self.check_ngrok_installed():
            print("ngrok not installed. Installing...")
            if not self.install_ngrok():
                return False
        
        if not self.configure_ngrok():
            return False
        
        # Create config
        config_path = self.create_tunnel_config()
        
        try:
            print(f"Starting ngrok tunnel on port {self.dashboard_port}...")
            
            # Start ngrok process
            self.tunnel_process = subprocess.Popen(
                ['ngrok', 'start', '--config', str(config_path), self.tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Get tunnel info
            tunnel_info = self.get_tunnel_info()
            if tunnel_info:
                self.tunnel_url = tunnel_info.get('public_url')
                self.tunnel_info = tunnel_info
                
                print(f"Tunnel started successfully!")
                print(f"Public URL: {self.tunnel_url}")
                print(f"Dashboard URL: {self.tunnel_url}")
                
                # Save tunnel info
                self.save_tunnel_info()
                
                # Play audio notification
                self.play_audio('tunnel_connected.wav')
                
                # Send notification
                self.send_notification()
                
                return True
            else:
                print("Failed to get tunnel information")
                self.stop_tunnel()
                return False
                
        except Exception as e:
            print(f"Failed to start tunnel: {e}")
            return False
    
    def stop_tunnel(self) -> bool:
        """Stop ngrok tunnel"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=10)
                print("Tunnel stopped")
                
                # Play audio notification
                self.play_audio('tunnel_disconnected.wav')
                
                return True
            except Exception as e:
                print(f"Error stopping tunnel: {e}")
                try:
                    self.tunnel_process.kill()
                except:
                    pass
                return False
        
        return True
    
    def get_tunnel_info(self) -> Optional[Dict]:
        """Get tunnel information from ngrok API"""
        try:
            # ngrok API endpoint
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if tunnel.get('name') == self.tunnel_name:
                        return {
                            'name': tunnel.get('name'),
                            'public_url': tunnel.get('public_url'),
                            'config': tunnel.get('config', {}),
                            'metrics': tunnel.get('metrics', {})
                        }
            
            return None
            
        except Exception as e:
            print(f"Error getting tunnel info: {e}")
            return None
    
    def save_tunnel_info(self):
        """Save tunnel information to file"""
        info_file = self.config_dir / 'tunnel_info.json'
        
        tunnel_data = {
            'url': self.tunnel_url,
            'name': self.tunnel_name,
            'port': self.dashboard_port,
            'started': time.time(),
            'info': self.tunnel_info
        }
        
        try:
            with open(info_file, 'w') as f:
                json.dump(tunnel_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tunnel info: {e}")
    
    def load_tunnel_info(self) -> Optional[Dict]:
        """Load saved tunnel information"""
        info_file = self.config_dir / 'tunnel_info.json'
        
        if info_file.exists():
            try:
                with open(info_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tunnel info: {e}")
        
        return None
    
    def get_status(self) -> Dict:
        """Get tunnel status"""
        status = {
            'running': False,
            'url': None,
            'process_running': False,
            'api_accessible': False
        }
        
        # Check if process is running
        if self.tunnel_process and self.tunnel_process.poll() is None:
            status['process_running'] = True
        
        # Check if API is accessible
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            if response.status_code == 200:
                status['api_accessible'] = True
                
                # Get current tunnel info
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if tunnel.get('name') == self.tunnel_name:
                        status['running'] = True
                        status['url'] = tunnel.get('public_url')
                        break
        except:
            pass
        
        return status
    
    def monitor_tunnel(self):
        """Monitor tunnel status"""
        self.monitoring = True
        
        while self.monitoring:
            status = self.get_status()
            
            if not status['running'] and self.tunnel_process:
                print("Tunnel disconnected, attempting restart...")
                self.start_tunnel()
            
            time.sleep(30)  # Check every 30 seconds
    
    def start_monitoring(self):
        """Start tunnel monitoring thread"""
        if not hasattr(self, 'monitor_thread') or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_tunnel, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop tunnel monitoring"""
        self.monitoring = False
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass
    
    def send_notification(self):
        """Send notification about tunnel"""
        try:
            # Import notification sender
            sys.path.append(str(self.claude_dir / 'hooks'))
            from notification_sender import get_sender
            
            sender = get_sender()
            sender.send_custom(
                "Tunnel Connected",
                f"Claude Code Dashboard accessible at:\\n{self.tunnel_url}",
                1
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

def main():
    """Main entry point"""
    tunnel_manager = NgrokTunnelManager()
    
    if len(sys.argv) < 2:
        print("Usage: setup_ngrok.py <action> [options]")
        print("Actions:")
        print("  start             - Start ngrok tunnel")
        print("  stop              - Stop ngrok tunnel")
        print("  status            - Check tunnel status")
        print("  install           - Install ngrok")
        print("  configure <token> - Configure ngrok with auth token")
        print("  monitor           - Start monitoring tunnel")
        print("  url               - Get tunnel URL")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'start':
        success = tunnel_manager.start_tunnel()
        if success:
            print("\\nTunnel started successfully!")
            print(f"Access dashboard at: {tunnel_manager.tunnel_url}")
            
            # Start monitoring
            tunnel_manager.start_monitoring()
            
            try:
                # Keep running
                while tunnel_manager.get_status()['running']:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\\nStopping tunnel...")
                tunnel_manager.stop_tunnel()
        
        sys.exit(0 if success else 1)
    
    elif action == 'stop':
        success = tunnel_manager.stop_tunnel()
        sys.exit(0 if success else 1)
    
    elif action == 'status':
        status = tunnel_manager.get_status()
        print(json.dumps(status, indent=2))
        sys.exit(0 if status['running'] else 1)
    
    elif action == 'install':
        success = tunnel_manager.install_ngrok()
        sys.exit(0 if success else 1)
    
    elif action == 'configure' and len(sys.argv) > 2:
        tunnel_manager.ngrok_token = sys.argv[2]
        success = tunnel_manager.configure_ngrok()
        sys.exit(0 if success else 1)
    
    elif action == 'monitor':
        tunnel_manager.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            tunnel_manager.stop_monitoring()
    
    elif action == 'url':
        status = tunnel_manager.get_status()
        if status['url']:
            print(status['url'])
        else:
            print("No active tunnel")
            sys.exit(1)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()