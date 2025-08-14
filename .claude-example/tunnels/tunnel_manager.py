#!/usr/bin/env python3
"""
Universal Tunnel Manager - V3.0+ Remote Access
Manages multiple tunnel providers (ngrok, Cloudflare, custom) with unified interface
"""

import os
import json
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

# Import tunnel providers
try:
    from setup_ngrok import NgrokTunnelManager
    from setup_cloudflare import CloudflareTunnelManager
except ImportError as e:
    print(f"Warning: Could not import tunnel providers: {e}")
    NgrokTunnelManager = None
    CloudflareTunnelManager = None

class UniversalTunnelManager:
    """Universal tunnel manager supporting multiple providers"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        self.config_dir = self.claude_dir / 'tunnels'
        self.config_dir.mkdir(exist_ok=True)
        
        # Tunnel providers
        self.providers = {}
        self.active_provider = None
        self.active_tunnel = None
        
        # Settings
        tunnel_settings = self.settings.get('v3ExtendedFeatures', {}).get('tunnels', {})
        self.preferred_provider = tunnel_settings.get('preferredProvider', 'ngrok')
        self.auto_fallback = tunnel_settings.get('autoFallback', True)
        self.dashboard_port = tunnel_settings.get('dashboardPort', 8080)
        
        # Initialize providers
        self.init_providers()
        
        # Monitoring
        self.monitoring = False
        self.monitor_thread = None
    
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
    
    def init_providers(self):
        """Initialize available tunnel providers"""
        # ngrok provider
        if NgrokTunnelManager:
            try:
                self.providers['ngrok'] = NgrokTunnelManager()
                print("ngrok provider initialized")
            except Exception as e:
                print(f"Failed to initialize ngrok: {e}")
        
        # Cloudflare provider
        if CloudflareTunnelManager:
            try:
                self.providers['cloudflare'] = CloudflareTunnelManager()
                print("Cloudflare provider initialized")
            except Exception as e:
                print(f"Failed to initialize Cloudflare: {e}")
        
        print(f"Initialized {len(self.providers)} tunnel providers: {list(self.providers.keys())}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        
        for provider_name, provider in self.providers.items():
            if provider_name == 'ngrok':
                if provider.check_ngrok_installed():
                    available.append(provider_name)
            elif provider_name == 'cloudflare':
                if provider.check_cloudflared_installed():
                    available.append(provider_name)
        
        return available
    
    def get_provider_status(self, provider_name: str) -> Dict:
        """Get status of specific provider"""
        if provider_name not in self.providers:
            return {'error': 'Provider not available'}
        
        provider = self.providers[provider_name]
        
        try:
            if hasattr(provider, 'get_status'):
                return provider.get_status()
            else:
                return {'error': 'Status not supported by provider'}
        except Exception as e:
            return {'error': f'Error getting status: {str(e)}'}
    
    def start_tunnel(self, provider_name: str = None) -> Dict:
        """Start tunnel with specified or preferred provider"""
        provider_name = provider_name or self.preferred_provider
        
        if provider_name not in self.providers:
            if self.auto_fallback:
                # Try available providers
                available = self.get_available_providers()
                if available:
                    provider_name = available[0]
                    print(f"Preferred provider not available, using {provider_name}")
                else:
                    return {
                        'success': False,
                        'error': 'No tunnel providers available',
                        'available_providers': list(self.providers.keys())
                    }
            else:
                return {
                    'success': False,
                    'error': f'Provider {provider_name} not available'
                }
        
        provider = self.providers[provider_name]
        
        try:
            # Play startup audio
            self.play_audio('tunnel_connected.wav')
            
            print(f"Starting tunnel with {provider_name}...")
            success = provider.start_tunnel()
            
            if success:
                self.active_provider = provider_name
                self.active_tunnel = provider
                
                # Get tunnel info
                status = provider.get_status() if hasattr(provider, 'get_status') else {}
                
                # Save active tunnel info
                self.save_active_tunnel_info(provider_name, status)
                
                # Start monitoring
                self.start_monitoring()
                
                result = {
                    'success': True,
                    'provider': provider_name,
                    'url': status.get('url') or getattr(provider, 'tunnel_url', None),
                    'status': status
                }
                
                print(f"Tunnel started successfully with {provider_name}")
                if result['url']:
                    print(f"Access dashboard at: {result['url']}")
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'Failed to start tunnel with {provider_name}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error starting tunnel: {str(e)}'
            }
    
    def stop_tunnel(self) -> Dict:
        """Stop active tunnel"""
        if not self.active_tunnel:
            return {'success': True, 'message': 'No active tunnel'}
        
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Stop tunnel
            success = self.active_tunnel.stop_tunnel()
            
            if success:
                # Play stop audio
                self.play_audio('tunnel_disconnected.wav')
                
                provider_name = self.active_provider
                self.active_provider = None
                self.active_tunnel = None
                
                # Clear saved info
                self.clear_active_tunnel_info()
                
                return {
                    'success': True,
                    'message': f'Tunnel stopped ({provider_name})'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to stop tunnel'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error stopping tunnel: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """Get overall tunnel status"""
        status = {
            'active': False,
            'provider': None,
            'url': None,
            'providers': {}
        }
        
        # Get status from all providers
        for provider_name in self.providers:
            status['providers'][provider_name] = self.get_provider_status(provider_name)
        
        # Check active tunnel
        if self.active_tunnel and self.active_provider:
            active_status = self.get_provider_status(self.active_provider)
            
            if active_status.get('running'):
                status['active'] = True
                status['provider'] = self.active_provider
                status['url'] = active_status.get('url')
            else:
                # Tunnel stopped
                self.active_provider = None
                self.active_tunnel = None
        
        # Add provider availability
        status['available_providers'] = self.get_available_providers()
        
        return status
    
    def restart_tunnel(self) -> Dict:
        """Restart active tunnel"""
        if self.active_provider:
            provider_name = self.active_provider
            stop_result = self.stop_tunnel()
            
            if stop_result['success']:
                time.sleep(2)  # Brief pause
                return self.start_tunnel(provider_name)
            else:
                return stop_result
        else:
            return self.start_tunnel()
    
    def switch_provider(self, new_provider: str) -> Dict:
        """Switch to different tunnel provider"""
        if new_provider not in self.providers:
            return {
                'success': False,
                'error': f'Provider {new_provider} not available'
            }
        
        # Stop current tunnel
        if self.active_tunnel:
            stop_result = self.stop_tunnel()
            if not stop_result['success']:
                return stop_result
        
        # Start with new provider
        return self.start_tunnel(new_provider)
    
    def monitor_tunnels(self):
        """Monitor tunnel status and handle failures"""
        self.monitoring = True
        
        while self.monitoring:
            try:
                if self.active_tunnel and self.active_provider:
                    status = self.get_provider_status(self.active_provider)
                    
                    if not status.get('running'):
                        print(f"Tunnel {self.active_provider} disconnected, attempting restart...")
                        
                        # Try to restart
                        restart_result = self.restart_tunnel()
                        
                        if not restart_result['success'] and self.auto_fallback:
                            # Try fallback provider
                            available = self.get_available_providers()
                            for provider_name in available:
                                if provider_name != self.active_provider:
                                    print(f"Trying fallback provider: {provider_name}")
                                    fallback_result = self.start_tunnel(provider_name)
                                    if fallback_result['success']:
                                        break
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer on errors
    
    def start_monitoring(self):
        """Start tunnel monitoring"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_tunnels, daemon=True)
            self.monitor_thread.start()
            print("Tunnel monitoring started")
    
    def stop_monitoring(self):
        """Stop tunnel monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        print("Tunnel monitoring stopped")
    
    def save_active_tunnel_info(self, provider: str, status: Dict):
        """Save active tunnel information"""
        info_file = self.config_dir / 'active_tunnel.json'
        
        tunnel_data = {
            'provider': provider,
            'started': time.time(),
            'status': status,
            'dashboard_port': self.dashboard_port
        }
        
        try:
            with open(info_file, 'w') as f:
                json.dump(tunnel_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tunnel info: {e}")
    
    def load_active_tunnel_info(self) -> Optional[Dict]:
        """Load active tunnel information"""
        info_file = self.config_dir / 'active_tunnel.json'
        
        if info_file.exists():
            try:
                with open(info_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tunnel info: {e}")
        
        return None
    
    def clear_active_tunnel_info(self):
        """Clear saved tunnel information"""
        info_file = self.config_dir / 'active_tunnel.json'
        
        if info_file.exists():
            try:
                info_file.unlink()
            except Exception as e:
                print(f"Error clearing tunnel info: {e}")
    
    def get_tunnel_history(self) -> List[Dict]:
        """Get tunnel usage history"""
        history_file = self.config_dir / 'tunnel_history.json'
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def add_to_history(self, provider: str, action: str, success: bool, details: Dict = None):
        """Add entry to tunnel history"""
        history = self.get_tunnel_history()
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'action': action,
            'success': success,
            'details': details or {}
        }
        
        history.append(entry)
        
        # Keep only last 100 entries
        if len(history) > 100:
            history = history[-100:]
        
        # Save history
        history_file = self.config_dir / 'tunnel_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

def main():
    """Main entry point"""
    tunnel_manager = UniversalTunnelManager()
    
    if len(sys.argv) < 2:
        print("Usage: tunnel_manager.py <action> [options]")
        print("Actions:")
        print("  start [provider]     - Start tunnel with optional provider")
        print("  stop                 - Stop active tunnel")
        print("  restart              - Restart active tunnel")
        print("  status               - Get tunnel status")
        print("  switch <provider>    - Switch to different provider")
        print("  providers            - List available providers")
        print("  url                  - Get active tunnel URL")
        print("  history              - Show tunnel history")
        print("  monitor              - Start monitoring mode")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'start':
        provider = sys.argv[2] if len(sys.argv) > 2 else None
        result = tunnel_manager.start_tunnel(provider)
        print(json.dumps(result, indent=2))
        
        if result['success']:
            # Keep tunnel running
            try:
                while tunnel_manager.get_status()['active']:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\\nStopping tunnel...")
                tunnel_manager.stop_tunnel()
        
        sys.exit(0 if result['success'] else 1)
    
    elif action == 'stop':
        result = tunnel_manager.stop_tunnel()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    elif action == 'restart':
        result = tunnel_manager.restart_tunnel()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    elif action == 'status':
        status = tunnel_manager.get_status()
        print(json.dumps(status, indent=2))
        sys.exit(0 if status['active'] else 1)
    
    elif action == 'switch' and len(sys.argv) > 2:
        provider = sys.argv[2]
        result = tunnel_manager.switch_provider(provider)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    elif action == 'providers':
        available = tunnel_manager.get_available_providers()
        all_providers = list(tunnel_manager.providers.keys())
        
        print("Available providers:")
        for provider in available:
            print(f"  ✓ {provider}")
        
        unavailable = set(all_providers) - set(available)
        if unavailable:
            print("\\nUnavailable providers:")
            for provider in unavailable:
                print(f"  ✗ {provider}")
    
    elif action == 'url':
        status = tunnel_manager.get_status()
        if status['url']:
            print(status['url'])
        else:
            print("No active tunnel")
            sys.exit(1)
    
    elif action == 'history':
        history = tunnel_manager.get_tunnel_history()
        if history:
            print("Tunnel History:")
            for entry in history[-10:]:  # Last 10 entries
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                status = "✓" if entry['success'] else "✗"
                print(f"  {timestamp} {status} {entry['provider']} {entry['action']}")
        else:
            print("No tunnel history")
    
    elif action == 'monitor':
        print("Starting tunnel monitoring...")
        tunnel_manager.start_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\nStopping monitoring...")
            tunnel_manager.stop_monitoring()
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()