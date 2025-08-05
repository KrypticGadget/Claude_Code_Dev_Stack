#!/usr/bin/env python3
"""
MCP Gateway Hook - Validate and manage Model Context Protocol usage
Ensures MCP servers are available and properly configured
"""

import sys
import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from base_hook import BaseHook


class MCPGateway(BaseHook):
    """Manage MCP server connections and validate usage"""
    
    # Known MCP server configurations
    MCP_SERVERS = {
        'filesystem': {
            'name': 'Filesystem MCP Server',
            'command': ['npx', '@modelcontextprotocol/server-filesystem'],
            'default_port': 3000,
            'capabilities': ['read', 'write', 'list', 'search']
        },
        'git': {
            'name': 'Git MCP Server',
            'command': ['npx', '@modelcontextprotocol/server-git'],
            'default_port': 3001,
            'capabilities': ['status', 'diff', 'commit', 'branch']
        },
        'github': {
            'name': 'GitHub MCP Server',
            'command': ['npx', '@modelcontextprotocol/server-github'],
            'default_port': 3002,
            'capabilities': ['issues', 'pulls', 'repos', 'actions']
        },
        'database': {
            'name': 'Database MCP Server',
            'command': ['npx', '@modelcontextprotocol/server-database'],
            'default_port': 3003,
            'capabilities': ['query', 'schema', 'migrate']
        },
        'shell': {
            'name': 'Shell MCP Server',
            'command': ['npx', '@modelcontextprotocol/server-shell'],
            'default_port': 3004,
            'capabilities': ['execute', 'environment']
        }
    }
    
    def __init__(self):
        super().__init__('mcp_gateway')
        self.mcp_config_file = self.env.config_dir / 'mcp_config.json'
        self.mcp_status_file = self.env.cache_dir / 'mcp_status.json'
    
    def run(self) -> int:
        """Validate MCP usage and server availability"""
        # Read MCP request from stdin
        request_data = self._read_mcp_request()
        
        # Load MCP configuration
        mcp_config = self._load_mcp_config()
        
        # Validate requested MCP usage
        validation_result = self._validate_request(request_data, mcp_config)
        
        if not validation_result['valid']:
            self.logger.warning(f"Invalid MCP request: {validation_result['reason']}")
            self.write_stdout(json.dumps(validation_result, indent=2))
            return 1
        
        # Check server availability
        server_status = self._check_server_status(request_data['server'])
        
        # Start server if needed
        if not server_status['available'] and mcp_config.get('auto_start', True):
            server_status = self._start_mcp_server(request_data['server'])
        
        # Prepare gateway response
        response = self._prepare_gateway_response(request_data, server_status)
        
        # Log MCP usage
        self._log_mcp_usage(request_data, response)
        
        # Output response
        self.write_stdout(json.dumps(response, indent=2))
        
        self.logger.info("MCP gateway processed request", 
                        server=request_data.get('server'),
                        operation=request_data.get('operation'))
        
        return 0
    
    def _read_mcp_request(self) -> Dict[str, Any]:
        """Read MCP request from stdin"""
        input_text = self.read_stdin()
        
        if not input_text:
            return {
                'server': 'filesystem',
                'operation': 'check',
                'parameters': {}
            }
        
        try:
            data = json.loads(input_text)
            
            # Ensure required fields
            if 'server' not in data:
                data['server'] = 'filesystem'
            if 'operation' not in data:
                data['operation'] = 'unknown'
            if 'parameters' not in data:
                data['parameters'] = {}
            
            return data
            
        except json.JSONDecodeError:
            # Parse as text command
            return self._parse_text_command(input_text)
    
    def _parse_text_command(self, text: str) -> Dict[str, Any]:
        """Parse text command to MCP request"""
        text_lower = text.lower()
        
        # Detect server type
        server = 'filesystem'  # default
        if 'git' in text_lower:
            server = 'git'
        elif 'github' in text_lower:
            server = 'github'
        elif 'database' in text_lower or 'sql' in text_lower:
            server = 'database'
        elif 'shell' in text_lower or 'command' in text_lower:
            server = 'shell'
        
        # Detect operation
        operation = 'unknown'
        if 'read' in text_lower or 'get' in text_lower:
            operation = 'read'
        elif 'write' in text_lower or 'save' in text_lower:
            operation = 'write'
        elif 'list' in text_lower or 'show' in text_lower:
            operation = 'list'
        elif 'search' in text_lower or 'find' in text_lower:
            operation = 'search'
        elif 'execute' in text_lower or 'run' in text_lower:
            operation = 'execute'
        
        return {
            'server': server,
            'operation': operation,
            'parameters': {'raw_command': text}
        }
    
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        default_config = {
            'enabled_servers': ['filesystem', 'git'],
            'auto_start': True,
            'timeout': 30,
            'max_retries': 3,
            'security': {
                'allow_shell': False,
                'allowed_paths': [str(self.env.project_dir)],
                'blocked_commands': ['rm -rf', 'format', 'dd']
            },
            'server_configs': {}
        }
        
        if self.mcp_config_file.exists():
            try:
                with open(self.mcp_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load MCP config: {e}")
        
        return default_config
    
    def _validate_request(self, request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MCP request against configuration"""
        result = {
            'valid': True,
            'reason': None,
            'warnings': []
        }
        
        # Check if server is enabled
        if request['server'] not in config['enabled_servers']:
            result['valid'] = False
            result['reason'] = f"MCP server '{request['server']}' is not enabled"
            return result
        
        # Security checks for shell server
        if request['server'] == 'shell':
            if not config['security']['allow_shell']:
                result['valid'] = False
                result['reason'] = "Shell MCP server is disabled for security"
                return result
            
            # Check for blocked commands
            command = request['parameters'].get('command', '')
            for blocked in config['security']['blocked_commands']:
                if blocked in command:
                    result['valid'] = False
                    result['reason'] = f"Blocked command pattern: {blocked}"
                    return result
        
        # Path validation for filesystem server
        if request['server'] == 'filesystem':
            path = request['parameters'].get('path', '')
            if path:
                # Check if path is within allowed paths
                allowed = False
                for allowed_path in config['security']['allowed_paths']:
                    try:
                        if Path(path).resolve().is_relative_to(Path(allowed_path).resolve()):
                            allowed = True
                            break
                    except:
                        continue
                
                if not allowed:
                    result['valid'] = False
                    result['reason'] = f"Path '{path}' is outside allowed directories"
                    return result
        
        # Check capabilities
        if request['operation'] != 'check':
            server_info = self.MCP_SERVERS.get(request['server'], {})
            capabilities = server_info.get('capabilities', [])
            
            if request['operation'] not in capabilities:
                result['warnings'].append(
                    f"Operation '{request['operation']}' may not be supported by {request['server']} server"
                )
        
        return result
    
    def _check_server_status(self, server_name: str) -> Dict[str, Any]:
        """Check if MCP server is running"""
        server_info = self.MCP_SERVERS.get(server_name, {})
        port = server_info.get('default_port', 3000)
        
        status = {
            'server': server_name,
            'available': False,
            'port': port,
            'pid': None,
            'version': None,
            'error': None
        }
        
        # Try to connect to server port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                status['available'] = True
                
                # Try to get server info
                status.update(self._get_server_info(server_name, port))
            else:
                status['error'] = 'Server not responding on expected port'
                
        except Exception as e:
            status['error'] = f"Failed to check server: {str(e)}"
        
        # Save status
        self._save_server_status(server_name, status)
        
        return status
    
    def _get_server_info(self, server_name: str, port: int) -> Dict[str, Any]:
        """Get detailed server information"""
        info = {}
        
        # Try to get process info (platform-specific)
        try:
            if sys.platform == 'win32':
                # Windows: use netstat
                result = subprocess.run(
                    ['netstat', '-ano'], 
                    capture_output=True, 
                    text=True
                )
                
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            info['pid'] = int(parts[-1])
                            break
            else:
                # Unix-like: use lsof
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'], 
                    capture_output=True, 
                    text=True
                )
                
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) > 1:
                        info['pid'] = int(parts[1])
        except:
            pass
        
        # Try to get version via MCP protocol
        # (This would require actual MCP client implementation)
        info['version'] = 'unknown'
        
        return info
    
    def _start_mcp_server(self, server_name: str) -> Dict[str, Any]:
        """Start an MCP server"""
        server_info = self.MCP_SERVERS.get(server_name, {})
        
        if not server_info:
            return {
                'server': server_name,
                'available': False,
                'error': 'Unknown server type'
            }
        
        try:
            # Prepare command
            command = server_info['command'].copy()
            port = server_info['default_port']
            
            # Add port argument if supported
            command.extend(['--port', str(port)])
            
            # Start server process
            self.logger.info(f"Starting MCP server: {server_name}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.env.project_dir
            )
            
            # Wait a moment for server to start
            import time
            time.sleep(2)
            
            # Check if started successfully
            if process.poll() is None:
                # Process is still running
                return self._check_server_status(server_name)
            else:
                # Process exited
                stderr = process.stderr.read().decode('utf-8') if process.stderr else ''
                return {
                    'server': server_name,
                    'available': False,
                    'error': f"Server failed to start: {stderr}"
                }
                
        except Exception as e:
            return {
                'server': server_name,
                'available': False,
                'error': f"Failed to start server: {str(e)}"
            }
    
    def _prepare_gateway_response(self, request: Dict[str, Any], 
                                 server_status: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare gateway response with connection details"""
        response = {
            'request': request,
            'server_status': server_status,
            'timestamp': datetime.now().isoformat()
        }
        
        if server_status['available']:
            # Add connection details
            response['connection'] = {
                'host': 'localhost',
                'port': server_status['port'],
                'protocol': 'mcp',
                'timeout': 30
            }
            
            # Add usage instructions
            response['usage'] = self._get_usage_instructions(request['server'], request['operation'])
            
            # Add security context
            response['security_context'] = {
                'allowed_paths': self.config.get('security', {}).get('allowed_paths', []),
                'restricted_operations': self._get_restricted_operations(request['server'])
            }
        else:
            response['error'] = server_status.get('error', 'Server unavailable')
            response['suggestions'] = [
                f"Ensure {request['server']} MCP server is installed",
                f"Try: npm install -g @modelcontextprotocol/server-{request['server']}",
                "Check if another process is using the port",
                "Review MCP server logs for errors"
            ]
        
        return response
    
    def _get_usage_instructions(self, server: str, operation: str) -> Dict[str, Any]:
        """Get usage instructions for specific operation"""
        instructions = {
            'filesystem': {
                'read': {
                    'description': 'Read file contents',
                    'parameters': ['path'],
                    'example': {'path': '/path/to/file.txt'}
                },
                'write': {
                    'description': 'Write content to file',
                    'parameters': ['path', 'content'],
                    'example': {'path': '/path/to/file.txt', 'content': 'File content'}
                },
                'list': {
                    'description': 'List directory contents',
                    'parameters': ['path', 'recursive'],
                    'example': {'path': '/path/to/dir', 'recursive': False}
                }
            },
            'git': {
                'status': {
                    'description': 'Get git repository status',
                    'parameters': ['repo_path'],
                    'example': {'repo_path': '.'}
                },
                'diff': {
                    'description': 'Get git diff',
                    'parameters': ['repo_path', 'staged'],
                    'example': {'repo_path': '.', 'staged': False}
                },
                'commit': {
                    'description': 'Create git commit',
                    'parameters': ['repo_path', 'message', 'files'],
                    'example': {'repo_path': '.', 'message': 'Update files', 'files': ['*']}
                }
            }
        }
        
        server_instructions = instructions.get(server, {})
        return server_instructions.get(operation, {
            'description': f'{operation} operation for {server} server',
            'parameters': [],
            'example': {}
        })
    
    def _get_restricted_operations(self, server: str) -> List[str]:
        """Get list of restricted operations for a server"""
        restrictions = {
            'filesystem': ['delete_recursive', 'format'],
            'shell': ['sudo', 'su', 'chmod_system'],
            'database': ['drop_database', 'truncate_all'],
            'git': ['force_push', 'reset_hard']
        }
        
        return restrictions.get(server, [])
    
    def _save_server_status(self, server_name: str, status: Dict[str, Any]):
        """Save server status to cache"""
        try:
            # Load existing status
            all_status = {}
            if self.mcp_status_file.exists():
                with open(self.mcp_status_file, 'r', encoding='utf-8') as f:
                    all_status = json.load(f)
            
            # Update status
            all_status[server_name] = {
                **status,
                'last_checked': datetime.now().isoformat()
            }
            
            # Save updated status
            with open(self.mcp_status_file, 'w', encoding='utf-8') as f:
                json.dump(all_status, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save server status: {e}")
    
    def _log_mcp_usage(self, request: Dict[str, Any], response: Dict[str, Any]):
        """Log MCP usage for monitoring"""
        usage_log = {
            'timestamp': datetime.now().isoformat(),
            'server': request['server'],
            'operation': request['operation'],
            'success': response.get('server_status', {}).get('available', False),
            'error': response.get('error'),
            'session_id': self.context.session_id,
            'project_dir': str(self.env.project_dir)
        }
        
        # Save to usage log
        usage_file = self.env.logs_dir / 'mcp_usage.jsonl'
        
        try:
            with open(usage_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(usage_log) + '\n')
        except Exception as e:
            self.logger.warning(f"Failed to log MCP usage: {e}")


def main():
    """Main entry point"""
    gateway = MCPGateway()
    return gateway.safe_run()


if __name__ == "__main__":
    sys.exit(main())