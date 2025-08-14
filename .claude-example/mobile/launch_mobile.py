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
        
        # Processes
        self.dashboard_process = None
        self.tunnel_process = None
        
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
    
    def start_secure_dashboard(self) -> bool:
        """Start dashboard with authentication"""
        try:
            # Generate auth token
            auth_token = self.generate_auth_token()
            
            safe_safe_print("🔒 Starting secure dashboard with authentication...")
            
            # Set environment variable for dashboard authentication
            env = os.environ.copy()
            env['CLAUDE_MOBILE_AUTH_TOKEN'] = auth_token
            env['CLAUDE_MOBILE_AUTH_DIR'] = str(self.mobile_dir)
            
            # Start dashboard with authentication
            dashboard_script = self.claude_dir.parent / '.claude-example' / 'dashboard' / 'dashboard_server.py'
            
            self.dashboard_process = subprocess.Popen([
                sys.executable, str(dashboard_script),
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
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Error starting dashboard: {e}")
            return False
    
    def start_tunnel(self) -> Optional[str]:
        """Start tunnel and return public URL"""
        try:
            safe_print("🌐 Starting secure tunnel...")
            
            # Start tunnel manager
            tunnel_script = self.claude_dir.parent / '.claude-example' / 'tunnels' / 'tunnel_manager.py'
            
            # Start tunnel in background
            tunnel_cmd = [sys.executable, str(tunnel_script), 'start']
            
            result = subprocess.run(tunnel_cmd, capture_output=True, text=True, timeout=30)
            
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
            
            # Create QR code with URL and auth token
            qr_data = f"{url}?auth={auth_token}"
            
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
            qr_ascii.add_data(qr_data)
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
        """Display mobile access information"""
        print("\n" + "=" * 60)
        safe_print("🚀 CLAUDE CODE V3+ MOBILE ACCESS READY!")
        print("=" * 60)
        safe_print(f"📱 Mobile URL: {url}")
        safe_print(f"🔐 Auth Token: {auth_token}")
        safe_print(f"🌐 Quick Link: {url}?auth={auth_token}")
        print(f"⏰ Expires: {datetime.fromtimestamp(int(time.time()) + self.session_timeout).strftime('%Y-%m-%d %H:%M')}")
        print("")
        print("📋 To access on Samsung Galaxy S25 Edge:")
        print("1. Open Samsung Internet Browser")
        print("2. Navigate to the Quick Link above")
        print("3. Full V3+ dashboard access with authentication")
        print("")
        safe_print("🔒 Security Features:")
        safe_print("  ✅ HTTPS tunnel encryption (TLS 1.3)")
        safe_print("  ✅ Session-based authentication")
        safe_print("  ✅ Auto-expiring tokens (24 hours)")
        safe_print("  ✅ Secure token generation")
        print("=" * 60)
    
    def launch(self, send_to_phone: bool = True, generate_qr: bool = True) -> bool:
        """Main launch function - the one-liner entry point"""
        safe_safe_print("🚀 Starting Claude Code V3+ Secure Mobile Access...")
        safe_print("=" * 60)
        
        try:
            # Step 1: Start secure dashboard
            if not self.start_secure_dashboard():
                print("❌ Failed to start dashboard")
                return False
            
            # Step 2: Start tunnel
            tunnel_url = self.start_tunnel()
            if not tunnel_url:
                print("❌ Failed to start tunnel")
                self.cleanup()
                return False
            
            # Step 3: Generate QR code
            qr_file = ""
            if generate_qr:
                qr_file = self.generate_qr_code(tunnel_url, self.auth_token)
            
            # Step 4: Send to phone
            if send_to_phone:
                self.send_to_phone(tunnel_url, self.auth_token)
            
            # Step 5: Save access info
            self.save_mobile_access_info(tunnel_url, self.auth_token, qr_file)
            
            # Step 6: Display info
            self.display_access_info(tunnel_url, self.auth_token)
            
            # Success!
            safe_print("\n✅ Mobile access launched successfully!")
            print("🔄 Monitoring system... Press Ctrl+C to stop")
            
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
        """Monitor dashboard and tunnel"""
        try:
            while True:
                # Check dashboard
                if self.dashboard_process and self.dashboard_process.poll() is not None:
                    safe_print("⚠️  Dashboard process stopped")
                    break
                
                # Sleep and continue monitoring
                time.sleep(10)
                
        except KeyboardInterrupt:
            pass
    
    def cleanup(self):
        """Clean up processes"""
        print("🧹 Cleaning up...")
        
        # Stop dashboard
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
            tunnel_script = self.claude_dir.parent / '.claude-example' / 'tunnels' / 'tunnel_manager.py'
            subprocess.run([sys.executable, str(tunnel_script), 'stop'], timeout=10)
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
    
    args = parser.parse_args()
    
    launcher = SecureMobileLauncher()
    
    if args.port != 8080:
        launcher.dashboard_port = args.port
    
    success = launcher.launch(
        send_to_phone=not args.no_phone,
        generate_qr=not args.no_qr
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()