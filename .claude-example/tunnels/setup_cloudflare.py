#!/usr/bin/env python3
"""
Cloudflare Tunnel Setup - V3.0+ Remote Access
Configures and manages Cloudflare tunnels for secure remote access
"""

import os
import json
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Optional, List
import uuid

class CloudflareTunnelManager:
    """Manage Cloudflare tunnels for remote access"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        self.config_dir = self.claude_dir / 'tunnels'
        self.config_dir.mkdir(exist_ok=True)
        
        # Cloudflare settings
        tunnel_settings = self.settings.get('v3ExtendedFeatures', {}).get('tunnels', {})
        self.tunnel_name = tunnel_settings.get('cloudflareTunnelName', 'claude-code-dashboard')
        self.dashboard_port = tunnel_settings.get('dashboardPort', 8080)
        self.domain = tunnel_settings.get('domain')  # Custom domain
        self.subdomain = tunnel_settings.get('subdomain', 'claude-code')
        
        # Tunnel state
        self.tunnel_process = None
        self.tunnel_id = None
        self.tunnel_url = None
        self.credentials_file = None
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
    
    def check_cloudflared_installed(self) -> bool:
        """Check if cloudflared is installed"""
        try:
            result = subprocess.run(
                ['cloudflared', 'version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_cloudflared(self) -> bool:
        """Install cloudflared"""
        if os.name == 'nt':
            # Windows
            try:
                print("Installing cloudflared for Windows...")
                
                # Download URL for Windows
                import requests
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
                
                response = requests.get(url)
                if response.status_code == 200:
                    # Create cloudflared directory
                    cf_dir = Path.home() / 'cloudflared'
                    cf_dir.mkdir(exist_ok=True)
                    
                    # Save executable
                    cf_exe = cf_dir / 'cloudflared.exe'
                    with open(cf_exe, 'wb') as f:
                        f.write(response.content)
                    
                    # Add to PATH
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                        try:
                            current_path = winreg.QueryValueEx(key, 'PATH')[0]
                            if str(cf_dir) not in current_path:
                                new_path = f"{current_path};{cf_dir}"
                                winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                        except FileNotFoundError:
                            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, str(cf_dir))
                    
                    print(f"cloudflared installed to {cf_dir}")
                    print("Please restart your terminal to use cloudflared")
                    return True
                
                return False
                
            except Exception as e:
                print(f"Failed to install cloudflared: {e}")
                return False
        
        else:
            # Linux/macOS
            print("Please install cloudflared manually:")
            print("Linux: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/#linux")
            print("macOS: brew install cloudflared")
            return False
    
    def login_cloudflare(self) -> bool:
        """Login to Cloudflare"""
        try:
            print("Opening browser for Cloudflare login...")
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'login'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("Cloudflare login successful")
                return True
            else:
                print(f"Login failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def create_tunnel(self) -> bool:
        """Create Cloudflare tunnel"""
        try:
            print(f"Creating tunnel: {self.tunnel_name}")
            
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'create', self.tunnel_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract tunnel ID from output
                lines = result.stderr.split('\\n')
                for line in lines:
                    if 'Created tunnel' in line and 'with id' in line:
                        # Extract UUID from line
                        parts = line.split()
                        for part in parts:
                            try:
                                uuid.UUID(part)
                                self.tunnel_id = part
                                break
                            except ValueError:
                                continue
                        break
                
                if self.tunnel_id:
                    print(f"Tunnel created with ID: {self.tunnel_id}")
                    
                    # Find credentials file
                    self.find_credentials_file()
                    
                    return True
                else:
                    print("Failed to extract tunnel ID")
                    return False
            else:
                print(f"Failed to create tunnel: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error creating tunnel: {e}")
            return False
    
    def find_credentials_file(self):
        """Find tunnel credentials file"""
        if not self.tunnel_id:
            return
        
        # Common locations for credentials
        possible_paths = [
            Path.home() / '.cloudflared' / f'{self.tunnel_id}.json',
            Path('~/.cloudflared').expanduser() / f'{self.tunnel_id}.json',
            self.config_dir / f'{self.tunnel_id}.json'
        ]
        
        for path in possible_paths:
            if path.exists():
                self.credentials_file = str(path)
                print(f"Found credentials file: {self.credentials_file}")
                return
        
        print("Warning: Could not find credentials file")
    
    def create_dns_record(self) -> bool:
        """Create DNS record for tunnel"""
        if not self.tunnel_id:
            print("No tunnel ID available")
            return False
        
        # Determine hostname
        if self.domain:
            hostname = f"{self.subdomain}.{self.domain}"
        else:
            hostname = f"{self.subdomain}.{self.tunnel_name}.tunnel.example.com"
        
        try:
            print(f"Creating DNS record: {hostname}")
            
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'route', 'dns', self.tunnel_id, hostname],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.tunnel_url = f"https://{hostname}"
                print(f"DNS record created: {self.tunnel_url}")
                return True
            else:
                print(f"Failed to create DNS record: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error creating DNS record: {e}")
            return False
    
    def create_config_file(self) -> Path:
        """Create tunnel configuration file"""
        if not self.tunnel_id:
            raise ValueError("No tunnel ID available")
        
        # Configuration
        config = {
            'tunnel': self.tunnel_id,
            'credentials-file': self.credentials_file or f'{self.tunnel_id}.json',
            'ingress': [
                {
                    'hostname': self.tunnel_url.replace('https://', '') if self.tunnel_url else f"{self.subdomain}.{self.tunnel_name}.tunnel.example.com",
                    'service': f'http://localhost:{self.dashboard_port}'
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
        
        # Save config
        config_path = self.config_dir / 'cloudflare-config.yml'
        
        # Convert to YAML
        yaml_content = f"""tunnel: {self.tunnel_id}
credentials-file: {config['credentials-file']}

ingress:
  - hostname: {config['ingress'][0]['hostname']}
    service: {config['ingress'][0]['service']}
  - service: {config['ingress'][1]['service']}
"""
        
        with open(config_path, 'w') as f:
            f.write(yaml_content)
        
        return config_path
    
    def start_tunnel(self) -> bool:
        """Start Cloudflare tunnel"""
        if not self.check_cloudflared_installed():
            print("cloudflared not installed. Installing...")
            if not self.install_cloudflared():
                return False
        
        # Check if we need to create tunnel
        if not self.tunnel_id:
            if not self.login_cloudflare():
                return False
            
            if not self.create_tunnel():
                return False
            
            if not self.create_dns_record():
                return False
        
        # Create config file
        try:
            config_path = self.create_config_file()
        except Exception as e:
            print(f"Failed to create config: {e}")
            return False
        
        try:
            print(f"Starting Cloudflare tunnel...")
            
            # Start tunnel process
            self.tunnel_process = subprocess.Popen(
                ['cloudflared', 'tunnel', '--config', str(config_path), 'run'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(5)
            
            # Check if process is still running
            if self.tunnel_process.poll() is None:
                print(f"Tunnel started successfully!")
                print(f"Dashboard URL: {self.tunnel_url}")
                
                # Save tunnel info
                self.save_tunnel_info()
                
                # Play audio notification
                self.play_audio('tunnel_connected.wav')
                
                # Send notification
                self.send_notification()
                
                return True
            else:
                stdout, stderr = self.tunnel_process.communicate()
                print(f"Tunnel failed to start:")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"Failed to start tunnel: {e}")
            return False
    
    def stop_tunnel(self) -> bool:
        """Stop Cloudflare tunnel"""
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
    
    def list_tunnels(self) -> List[Dict]:
        """List existing tunnels"""
        try:
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                tunnels = []
                lines = result.stdout.strip().split('\\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            tunnels.append({
                                'id': parts[0],
                                'name': parts[1],
                                'created': ' '.join(parts[2:])
                            })
                
                return tunnels
            
            return []
            
        except Exception as e:
            print(f"Error listing tunnels: {e}")
            return []
    
    def delete_tunnel(self, tunnel_id: str = None) -> bool:
        """Delete tunnel"""
        tunnel_id = tunnel_id or self.tunnel_id
        
        if not tunnel_id:
            print("No tunnel ID provided")
            return False
        
        try:
            result = subprocess.run(
                ['cloudflared', 'tunnel', 'delete', tunnel_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Tunnel {tunnel_id} deleted")
                return True
            else:
                print(f"Failed to delete tunnel: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error deleting tunnel: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get tunnel status"""
        status = {
            'running': False,
            'url': self.tunnel_url,
            'process_running': False,
            'tunnel_id': self.tunnel_id
        }
        
        # Check if process is running
        if self.tunnel_process and self.tunnel_process.poll() is None:
            status['process_running'] = True
            status['running'] = True
        
        return status
    
    def save_tunnel_info(self):
        """Save tunnel information"""
        info_file = self.config_dir / 'cloudflare_tunnel_info.json'
        
        tunnel_data = {
            'id': self.tunnel_id,
            'name': self.tunnel_name,
            'url': self.tunnel_url,
            'port': self.dashboard_port,
            'started': time.time(),
            'credentials_file': self.credentials_file
        }
        
        try:
            with open(info_file, 'w') as f:
                json.dump(tunnel_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tunnel info: {e}")
    
    def load_tunnel_info(self) -> Optional[Dict]:
        """Load saved tunnel information"""
        info_file = self.config_dir / 'cloudflare_tunnel_info.json'
        
        if info_file.exists():
            try:
                with open(info_file, 'r') as f:
                    data = json.load(f)
                    self.tunnel_id = data.get('id')
                    self.tunnel_url = data.get('url')
                    self.credentials_file = data.get('credentials_file')
                    return data
            except Exception as e:
                print(f"Error loading tunnel info: {e}")
        
        return None
    
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
                "Cloudflare Tunnel Connected",
                f"Claude Code Dashboard accessible at:\\n{self.tunnel_url}",
                1
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

def main():
    """Main entry point"""
    tunnel_manager = CloudflareTunnelManager()
    
    if len(sys.argv) < 2:
        print("Usage: setup_cloudflare.py <action> [options]")
        print("Actions:")
        print("  start             - Start Cloudflare tunnel")
        print("  stop              - Stop Cloudflare tunnel")
        print("  status            - Check tunnel status")
        print("  install           - Install cloudflared")
        print("  login             - Login to Cloudflare")
        print("  create            - Create new tunnel")
        print("  list              - List existing tunnels")
        print("  delete [id]       - Delete tunnel")
        print("  url               - Get tunnel URL")
        sys.exit(1)
    
    action = sys.argv[1]
    
    # Load existing tunnel info
    tunnel_manager.load_tunnel_info()
    
    if action == 'start':
        success = tunnel_manager.start_tunnel()
        if success:
            print("\\nTunnel started successfully!")
            print(f"Access dashboard at: {tunnel_manager.tunnel_url}")
            
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
        success = tunnel_manager.install_cloudflared()
        sys.exit(0 if success else 1)
    
    elif action == 'login':
        success = tunnel_manager.login_cloudflare()
        sys.exit(0 if success else 1)
    
    elif action == 'create':
        if tunnel_manager.login_cloudflare():
            success = tunnel_manager.create_tunnel()
            sys.exit(0 if success else 1)
        sys.exit(1)
    
    elif action == 'list':
        tunnels = tunnel_manager.list_tunnels()
        if tunnels:
            print("Existing tunnels:")
            for tunnel in tunnels:
                print(f"  {tunnel['id']} - {tunnel['name']} ({tunnel['created']})")
        else:
            print("No tunnels found")
    
    elif action == 'delete':
        tunnel_id = sys.argv[2] if len(sys.argv) > 2 else None
        success = tunnel_manager.delete_tunnel(tunnel_id)
        sys.exit(0 if success else 1)
    
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