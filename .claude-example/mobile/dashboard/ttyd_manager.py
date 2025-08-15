#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ttyd Terminal Manager - Browser-based terminal access
Provides terminal access through web browser using ttyd
"""

import os
import sys
import subprocess
import requests
import secrets
from pathlib import Path
import time

# Fix Windows Unicode encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class TerminalManager:
    """Manage ttyd terminal server for browser access"""
    
    def __init__(self):
        self.ttyd_dir = Path.home() / '.claude' / 'bin'
        self.ttyd_path = self.ttyd_dir / ('ttyd.exe' if sys.platform == 'win32' else 'ttyd')
        self.port = 7681
        self.username = "admin"
        self.password = secrets.token_urlsafe(12)
        self.process = None
        
    def download_ttyd(self):
        """Download ttyd binary for the current platform"""
        if self.ttyd_path.exists():
            print(f"ttyd already exists at {self.ttyd_path}")
            return True
            
        print("Downloading ttyd terminal server...")
        self.ttyd_dir.mkdir(parents=True, exist_ok=True)
        
        # Platform-specific URLs for ttyd v1.7.4
        urls = {
            'win32': 'https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.win32.exe',
            'darwin': 'https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64.darwin',
            'linux': 'https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64'
        }
        
        platform = sys.platform
        if platform.startswith('linux'):
            platform = 'linux'
            
        url = urls.get(platform)
        if not url:
            print(f"Unsupported platform: {platform}")
            return False
        
        try:
            # Download with progress
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.ttyd_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading ttyd: {percent:.1f}%", end='')
            
            print("\nDownload complete!")
            
            # Make executable on Unix systems
            if sys.platform != 'win32':
                os.chmod(self.ttyd_path, 0o755)
                
            return True
            
        except Exception as e:
            print(f"Error downloading ttyd: {e}")
            if self.ttyd_path.exists():
                self.ttyd_path.unlink()
            return False
    
    def start_terminal(self):
        """Start ttyd terminal server"""
        if not self.ttyd_path.exists():
            if not self.download_ttyd():
                print("Failed to download ttyd")
                return False
        
        # Determine shell command based on platform
        if sys.platform == 'win32':
            shell_cmd = 'cmd.exe'
        else:
            shell_cmd = 'bash'
        
        # Build ttyd command
        cmd = [
            str(self.ttyd_path),
            '-p', str(self.port),
            '-c', f'{self.username}:{self.password}',
            '-t', 'titleFixed=Claude Code Terminal',
            '-t', 'fontSize=14',
            '-t', 'theme={"background":"#1e1e1e","foreground":"#cccccc","cursor":"#ffffff","black":"#000000","red":"#cd3131","green":"#0dbc79","yellow":"#e5e510","blue":"#2472c8","magenta":"#bc3fbc","cyan":"#11a8cd","white":"#e5e5e5","brightBlack":"#666666","brightRed":"#f14c4c","brightGreen":"#23d18b","brightYellow":"#f5f543","brightBlue":"#3b8eea","brightMagenta":"#d670d6","brightCyan":"#29b8db","brightWhite":"#e5e5e5"}',
            '-W',  # Writable (allow input)
            shell_cmd
        ]
        
        print(f"Starting ttyd terminal server on port {self.port}...")
        print(f"Credentials - Username: {self.username}, Password: {self.password}")
        
        try:
            # Start ttyd process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(2)
            
            # Check if process is running
            if self.process.poll() is None:
                print(f"Terminal server started successfully!")
                print(f"Access at: http://localhost:{self.port}")
                print(f"Login with - Username: {self.username}, Password: {self.password}")
                return True
            else:
                # Process failed to start
                stdout, stderr = self.process.communicate()
                print(f"Failed to start ttyd:")
                if stdout:
                    print(f"stdout: {stdout}")
                if stderr:
                    print(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"Error starting ttyd: {e}")
            return False
    
    def stop_terminal(self):
        """Stop ttyd terminal server"""
        if self.process:
            print("Stopping ttyd terminal server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("Terminal server stopped")
    
    def get_credentials(self):
        """Get terminal access credentials"""
        return {
            'url': f'http://localhost:{self.port}',
            'username': self.username,
            'password': self.password
        }

def main():
    """Main entry point for standalone execution"""
    manager = TerminalManager()
    
    try:
        # Start terminal server
        if manager.start_terminal():
            print("\n" + "="*60)
            print("Terminal server is running!")
            print("="*60)
            
            # Keep running
            while True:
                time.sleep(1)
                # Check if process is still running
                if manager.process and manager.process.poll() is not None:
                    print("Terminal server stopped unexpectedly")
                    break
                    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        manager.stop_terminal()

if __name__ == '__main__':
    main()