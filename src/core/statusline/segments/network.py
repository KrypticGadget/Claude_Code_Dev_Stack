"""
Network Segment

Displays network connectivity status, tunnel information, and 
connection health indicators.
"""

import os
import socket
import subprocess
import time
import json
from typing import Dict, Any, Optional, List

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils
from ..themes import Theme


class NetworkSegment(BaseSegment):
    """Segment that displays network connectivity and tunnel status"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.show_connectivity = config.get('show_connectivity', True)
        self.show_tunnel_status = config.get('show_tunnel_status', True)
        self.show_ping_time = config.get('show_ping_time', False)
        self.show_ip_address = config.get('show_ip_address', False)
        self.compact_display = config.get('compact_display', True)
        self.show_icons = config.get('show_icons', True)
        
        # Network test configuration
        self.connectivity_hosts = config.get('connectivity_hosts', ['8.8.8.8', 'cloudflare.com'])
        self.connectivity_timeout = config.get('connectivity_timeout', 3)
        self.connectivity_port = config.get('connectivity_port', 53)  # DNS port
        
        # Tunnel configuration
        self.tunnel_types = config.get('tunnel_types', ['ngrok', 'cloudflare', 'ssh'])
        self.tunnel_status_paths = config.get('tunnel_status_paths', [
            os.path.join(os.getcwd(), '.ngrok', 'status.json'),
            os.path.join(os.getcwd(), 'logs', 'tunnel_status.json'),
            '/tmp/tunnel_status.json'
        ])
        
        # Cache for network data
        self._network_cache = {}
        self._last_network_check = 0
        self._network_cache_timeout = 10.0  # 10 seconds
    
    def _collect_data(self) -> SegmentData:
        """Collect network status information"""
        network_data = self._get_network_data()
        
        content_parts = []
        overall_status = 'unknown'
        
        # Connectivity status
        if self.show_connectivity:
            connectivity_info = network_data.get('connectivity', {})
            if connectivity_info:
                if self.compact_display:
                    if connectivity_info['connected']:
                        content_parts.append('🌐' if self.show_icons else 'NET')
                    else:
                        content_parts.append('❌' if self.show_icons else 'NO-NET')
                else:
                    status_text = 'Connected' if connectivity_info['connected'] else 'Disconnected'
                    icon = '🌐' if connectivity_info['connected'] else '❌'
                    if self.show_icons:
                        content_parts.append(f"{icon} {status_text}")
                    else:
                        content_parts.append(status_text)
                
                overall_status = 'connected' if connectivity_info['connected'] else 'disconnected'
        
        # Ping time
        if self.show_ping_time and overall_status == 'connected':
            ping_time = network_data.get('ping_time')
            if ping_time is not None:
                content_parts.append(f"{ping_time:.0f}ms")
        
        # IP address
        if self.show_ip_address:
            ip_info = network_data.get('ip_address')
            if ip_info:
                content_parts.append(ip_info)
        
        # Tunnel status
        if self.show_tunnel_status:
            tunnel_info = network_data.get('tunnels', {})
            if tunnel_info:
                tunnel_text = self._format_tunnel_status(tunnel_info)
                if tunnel_text:
                    content_parts.append(tunnel_text)
                    
                    # Update overall status if tunnels are active
                    if any(t.get('active', False) for t in tunnel_info.values()):
                        if overall_status == 'connected':
                            overall_status = 'tunnel_active'
        
        content = ' '.join(content_parts) if content_parts else "No connection"
        
        # Generate tooltip
        tooltip = self._generate_tooltip(network_data)
        
        return SegmentData(
            content=content,
            status=overall_status,
            icon=self._get_network_icon(overall_status),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format network data for display"""
        return data.content
    
    def _get_network_data(self) -> Dict[str, Any]:
        """Get comprehensive network information"""
        current_time = time.time()
        
        # Use cache if recent
        if (current_time - self._last_network_check) < self._network_cache_timeout and self._network_cache:
            return self._network_cache
        
        network_data = {}
        
        try:
            # Test connectivity
            connectivity_result = self._test_connectivity()
            network_data['connectivity'] = connectivity_result
            
            # Get ping time if connected
            if connectivity_result.get('connected', False):
                ping_time = self._get_ping_time()
                if ping_time is not None:
                    network_data['ping_time'] = ping_time
            
            # Get IP address
            ip_address = self._get_ip_address()
            if ip_address:
                network_data['ip_address'] = ip_address
            
            # Get tunnel status
            tunnel_status = self._get_tunnel_status()
            if tunnel_status:
                network_data['tunnels'] = tunnel_status
                
        except Exception as e:
            network_data['error'] = str(e)
        
        # Cache the result
        self._network_cache = network_data
        self._last_network_check = current_time
        
        return network_data
    
    def _test_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity to external hosts"""
        connectivity_results = {
            'connected': False,
            'tested_hosts': [],
            'successful_hosts': [],
            'failed_hosts': []
        }
        
        for host in self.connectivity_hosts:
            try:
                # Try to connect to the host
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.connectivity_timeout)
                
                # Resolve host if it's a domain name
                if not self._is_ip_address(host):
                    host_ip = socket.gethostbyname(host)
                else:
                    host_ip = host
                
                result = sock.connect_ex((host_ip, self.connectivity_port))
                sock.close()
                
                connectivity_results['tested_hosts'].append(host)
                
                if result == 0:
                    connectivity_results['successful_hosts'].append(host)
                    connectivity_results['connected'] = True
                else:
                    connectivity_results['failed_hosts'].append(host)
                    
            except Exception as e:
                connectivity_results['tested_hosts'].append(host)
                connectivity_results['failed_hosts'].append(host)
        
        return connectivity_results
    
    def _get_ping_time(self) -> Optional[float]:
        """Get ping time to a test server"""
        try:
            # Use first successful host from connectivity test
            target_host = '8.8.8.8'  # Google DNS as fallback
            
            # Platform-specific ping command
            import platform
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', target_host]
            else:
                cmd = ['ping', '-c', '1', target_host]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse ping time from output
                import re
                
                if platform.system().lower() == 'windows':
                    # Windows format: "time=123ms" or "time<1ms"
                    match = re.search(r'time[<=](\d+)ms', result.stdout)
                else:
                    # Unix format: "time=123.456 ms"
                    match = re.search(r'time=(\d+\.?\d*)\s*ms', result.stdout)
                
                if match:
                    return float(match.group(1))
            
        except Exception:
            pass
        
        return None
    
    def _get_ip_address(self) -> Optional[str]:
        """Get current external IP address"""
        try:
            # Try to get external IP using various methods
            methods = [
                self._get_ip_from_socket,
                self._get_ip_from_interface,
                self._get_ip_from_env
            ]
            
            for method in methods:
                try:
                    ip = method()
                    if ip and self._is_valid_ip(ip):
                        return ip
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return None
    
    def _get_ip_from_socket(self) -> Optional[str]:
        """Get IP address by connecting to external host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return None
    
    def _get_ip_from_interface(self) -> Optional[str]:
        """Get IP address from network interface"""
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip != '127.0.0.1':
                return ip
        except Exception:
            pass
        
        return None
    
    def _get_ip_from_env(self) -> Optional[str]:
        """Get IP address from environment variables"""
        ip_vars = ['LOCAL_IP', 'HOST_IP', 'SERVER_IP']
        for var in ip_vars:
            ip = os.getenv(var)
            if ip and self._is_valid_ip(ip):
                return ip
        
        return None
    
    def _get_tunnel_status(self) -> Dict[str, Any]:
        """Get status of active tunnels"""
        tunnel_status = {}
        
        # Check ngrok tunnels
        ngrok_status = self._check_ngrok_tunnels()
        if ngrok_status:
            tunnel_status['ngrok'] = ngrok_status
        
        # Check SSH tunnels
        ssh_status = self._check_ssh_tunnels()
        if ssh_status:
            tunnel_status['ssh'] = ssh_status
        
        # Check CloudFlare tunnels
        cf_status = self._check_cloudflare_tunnels()
        if cf_status:
            tunnel_status['cloudflare'] = cf_status
        
        # Check from status files
        file_status = self._check_tunnel_status_files()
        if file_status:
            tunnel_status.update(file_status)
        
        return tunnel_status
    
    def _check_ngrok_tunnels(self) -> Optional[Dict[str, Any]]:
        """Check ngrok tunnel status"""
        try:
            # Try ngrok API
            import urllib.request
            import urllib.error
            
            try:
                response = urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels', timeout=2)
                data = json.loads(response.read().decode())
                
                tunnels = data.get('tunnels', [])
                if tunnels:
                    return {
                        'active': True,
                        'count': len(tunnels),
                        'tunnels': [
                            {
                                'name': t.get('name', 'unknown'),
                                'public_url': t.get('public_url', ''),
                                'protocol': t.get('proto', 'unknown')
                            }
                            for t in tunnels
                        ]
                    }
            except (urllib.error.URLError, socket.timeout):
                pass
            
            # Check if ngrok process is running
            try:
                result = subprocess.run(
                    ['pgrep', 'ngrok'] if os.name != 'nt' else ['tasklist', '/FI', 'IMAGENAME eq ngrok.exe'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    return {
                        'active': True,
                        'count': 'unknown',
                        'status': 'process_detected'
                    }
            except Exception:
                pass
                
        except Exception:
            pass
        
        return None
    
    def _check_ssh_tunnels(self) -> Optional[Dict[str, Any]]:
        """Check SSH tunnel status"""
        try:
            # Look for SSH processes with tunnel flags
            if os.name != 'nt':  # Unix-like systems
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    ssh_tunnels = []
                    for line in result.stdout.split('\n'):
                        if 'ssh' in line and ('-L' in line or '-R' in line or '-D' in line):
                            ssh_tunnels.append(line.strip())
                    
                    if ssh_tunnels:
                        return {
                            'active': True,
                            'count': len(ssh_tunnels),
                            'processes': ssh_tunnels[:3]  # Limit for display
                        }
            
        except Exception:
            pass
        
        return None
    
    def _check_cloudflare_tunnels(self) -> Optional[Dict[str, Any]]:
        """Check CloudFlare tunnel status"""
        try:
            # Check for cloudflared process
            if os.name != 'nt':
                result = subprocess.run(
                    ['pgrep', 'cloudflared'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            else:
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq cloudflared.exe'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            
            if result.returncode == 0 and result.stdout.strip():
                return {
                    'active': True,
                    'status': 'process_detected'
                }
                
        except Exception:
            pass
        
        return None
    
    def _check_tunnel_status_files(self) -> Dict[str, Any]:
        """Check tunnel status from files"""
        tunnel_status = {}
        
        for status_path in self.tunnel_status_paths:
            if os.path.exists(status_path):
                try:
                    with open(status_path, 'r') as f:
                        status_data = json.load(f)
                        
                    # Parse different status file formats
                    if 'tunnels' in status_data:
                        tunnel_status.update(status_data['tunnels'])
                    elif 'ngrok' in status_data:
                        tunnel_status['ngrok'] = status_data['ngrok']
                        
                except Exception:
                    continue
        
        return tunnel_status
    
    def _format_tunnel_status(self, tunnel_info: Dict[str, Any]) -> str:
        """Format tunnel status for display"""
        active_tunnels = []
        
        for tunnel_type, info in tunnel_info.items():
            if info.get('active', False):
                if self.compact_display:
                    count = info.get('count', 1)
                    if isinstance(count, int) and count > 1:
                        active_tunnels.append(f"{tunnel_type}:{count}")
                    else:
                        active_tunnels.append(tunnel_type)
                else:
                    active_tunnels.append(f"{tunnel_type.title()} Active")
        
        if active_tunnels:
            tunnel_icon = '🚇' if self.show_icons else 'TUN'
            if self.compact_display:
                return f"{tunnel_icon}({','.join(active_tunnels)})"
            else:
                return f"{tunnel_icon} {', '.join(active_tunnels)}"
        
        return ""
    
    def _is_ip_address(self, host: str) -> bool:
        """Check if string is an IP address"""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            socket.inet_aton(ip)
            return ip != '127.0.0.1' and ip != '0.0.0.0'
        except socket.error:
            return False
    
    def _get_network_icon(self, status: str) -> Optional[str]:
        """Get appropriate network icon based on status"""
        if not self.show_icons:
            return None
        
        icon_map = {
            'connected': '🌐',
            'disconnected': '❌',
            'tunnel_active': '🚇',
            'unknown': '❓'
        }
        
        if hasattr(self.theme, 'unicode_symbols'):
            theme_icon = self.theme.unicode_symbols.get('network')
            if theme_icon:
                return theme_icon
        
        return icon_map.get(status, '🌐')
    
    def _generate_tooltip(self, network_data: Dict[str, Any]) -> str:
        """Generate detailed tooltip for network status"""
        lines = []
        
        if 'error' in network_data:
            lines.append(f"Error: {network_data['error']}")
            return '\n'.join(lines)
        
        # Connectivity info
        connectivity = network_data.get('connectivity', {})
        if connectivity:
            status = "Connected" if connectivity.get('connected', False) else "Disconnected"
            lines.append(f"Network Status: {status}")
            
            successful_hosts = connectivity.get('successful_hosts', [])
            if successful_hosts:
                lines.append(f"Reachable hosts: {', '.join(successful_hosts)}")
            
            failed_hosts = connectivity.get('failed_hosts', [])
            if failed_hosts:
                lines.append(f"Failed hosts: {', '.join(failed_hosts)}")
        
        # Ping time
        ping_time = network_data.get('ping_time')
        if ping_time is not None:
            lines.append(f"Ping time: {ping_time:.1f}ms")
        
        # IP address
        ip_address = network_data.get('ip_address')
        if ip_address:
            lines.append(f"Local IP: {ip_address}")
        
        # Tunnel information
        tunnels = network_data.get('tunnels', {})
        if tunnels:
            lines.append("\nActive tunnels:")
            for tunnel_type, info in tunnels.items():
                if info.get('active', False):
                    count = info.get('count', 'unknown')
                    lines.append(f"  • {tunnel_type.title()}: {count} tunnel(s)")
                    
                    # Add specific tunnel details
                    if 'tunnels' in info:
                        for tunnel in info['tunnels'][:3]:  # Show first 3
                            name = tunnel.get('name', 'unnamed')
                            url = tunnel.get('public_url', '')
                            if url:
                                lines.append(f"    - {name}: {url}")
        
        return '\n'.join(lines)
    
    def get_network_details(self) -> Dict[str, Any]:
        """Get detailed network information"""
        return self._get_network_data()
    
    def test_connection(self, host: str = None, port: int = None) -> Dict[str, Any]:
        """Test connection to specific host"""
        test_host = host or self.connectivity_hosts[0]
        test_port = port or self.connectivity_port
        
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connectivity_timeout)
            
            result = sock.connect_ex((test_host, test_port))
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            sock.close()
            
            return {
                'host': test_host,
                'port': test_port,
                'connected': result == 0,
                'response_time_ms': response_time,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'host': test_host,
                'port': test_port,
                'connected': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def refresh_network_data(self):
        """Force refresh of network data"""
        self._network_cache.clear()
        self._last_network_check = 0
        self.clear_cache()
    
    def get_tunnel_details(self) -> Dict[str, Any]:
        """Get detailed tunnel information"""
        network_data = self._get_network_data()
        return network_data.get('tunnels', {})
    
    def is_connected(self) -> bool:
        """Check if network is connected"""
        network_data = self._get_network_data()
        connectivity = network_data.get('connectivity', {})
        return connectivity.get('connected', False)
    
    def has_active_tunnels(self) -> bool:
        """Check if any tunnels are active"""
        tunnel_data = self.get_tunnel_details()
        return any(info.get('active', False) for info in tunnel_data.values())