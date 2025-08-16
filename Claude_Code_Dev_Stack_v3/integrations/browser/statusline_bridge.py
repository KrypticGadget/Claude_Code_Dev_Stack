#!/usr/bin/env python3
"""
Statusline Bridge for Claude Code Browser Integration

Extends @zainhoda/claude-code-browser with v3.0 statusline integration
- Real-time agent/task/hook monitoring
- Ultimate statusline data streaming
- WebSocket integration for PWA

Original browser by @zainhoda: https://github.com/zainhoda/claude-code-browser
Extended for Dev Stack v3.0 by Zach
"""

import asyncio
import json
import websockets
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Import our ultimate statusline
import sys
sys.path.append(str(Path(__file__).parent.parent / 'statusline'))

try:
    from ultimate_statusline import UltimateStatuslineManager
except ImportError:
    print("Warning: Ultimate statusline not available, using fallback")
    UltimateStatuslineManager = None

logger = logging.getLogger(__name__)

class StatuslineBridge:
    """Bridge between browser and statusline systems"""
    
    def __init__(self):
        self.statusline_manager = UltimateStatuslineManager() if UltimateStatuslineManager else None
        self.connected_clients = set()
        self.last_data = None
        self.update_interval = 0.1  # 100ms updates
        
    async def start_statusline_monitoring(self):
        """Start the statusline monitoring system"""
        if self.statusline_manager:
            # Start the statusline manager
            await self.statusline_manager.start()
            
            # Listen for updates
            self.statusline_manager.on('update', self.on_statusline_update)
            self.statusline_manager.on('error', self.on_statusline_error)
            
        # Start the update loop regardless
        asyncio.create_task(self.update_loop())
        
    async def update_loop(self):
        """Main update loop for statusline data"""
        while True:
            try:
                # Get current statusline data
                data = await self.get_current_statusline_data()
                
                # Broadcast to all connected clients
                if data != self.last_data:
                    await self.broadcast_update(data)
                    self.last_data = data
                    
            except Exception as e:
                logger.error(f"Error in statusline update loop: {e}")
                
            await asyncio.sleep(self.update_interval)
    
    async def get_current_statusline_data(self) -> Dict[str, Any]:
        """Get current statusline data"""
        if self.statusline_manager:
            try:
                data = await self.statusline_manager.getCurrentData()
                return self.format_for_browser(data)
            except Exception as e:
                logger.error(f"Error getting statusline data: {e}")
        
        # Fallback data structure
        return {
            'powerline': {
                'directory': 'unknown',
                'git': {'branch': 'main', 'dirty': False},
                'model': {'displayName': 'Claude 3.5 Sonnet'},
                'cost': {'session': 0, 'today': 0, 'budget': 25}
            },
            'devStack': {
                'agents': {'active': 0, 'total': 28, 'status': 'idle'},
                'tasks': {'active': 0, 'completed': 0, 'total': 0, 'status': 'none'},
                'hooks': {'triggered': 0, 'total': 28, 'errors': 0, 'status': 'ready'},
                'audio': {'enabled': False, 'lastEvent': 'none', 'status': 'silent'}
            },
            'timestamp': int(time.time() * 1000)
        }
    
    def format_for_browser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format statusline data for browser consumption"""
        return {
            'type': 'statusline_update',
            'data': data,
            'attribution': {
                'powerline': '@Owloops/claude-powerline',
                'devStack': 'Dev Stack monitoring by Zach',
                'browser': '@zainhoda/claude-code-browser'
            },
            'timestamp': data.get('timestamp', int(time.time() * 1000))
        }
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        if not self.connected_clients:
            return
            
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.connected_clients:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        self.connected_clients.add(websocket)
        logger.info(f"New statusline client connected: {websocket.remote_address}")
        
        try:
            # Send initial data
            initial_data = await self.get_current_statusline_data()
            await websocket.send(json.dumps(initial_data))
            
            # Keep connection alive
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling websocket connection: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Statusline client disconnected: {websocket.remote_address}")
    
    async def handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle message from client"""
        message_type = data.get('type')
        
        if message_type == 'get_current_data':
            # Send current statusline data
            current_data = await self.get_current_statusline_data()
            await websocket.send(json.dumps(current_data))
            
        elif message_type == 'update_config':
            # Update statusline configuration
            config = data.get('config', {})
            if self.statusline_manager:
                self.statusline_manager.updateConfig(config)
                
        elif message_type == 'trigger_audio':
            # Trigger audio notification
            audio_event = data.get('event', 'notification')
            # TODO: Implement audio triggering
            
    def on_statusline_update(self, data):
        """Handle statusline update event"""
        # This will be called by the statusline manager
        # The main update loop will handle broadcasting
        pass
        
    def on_statusline_error(self, error):
        """Handle statusline error event"""
        logger.error(f"Statusline error: {error}")

# WebSocket server for statusline bridge
async def start_statusline_websocket_server(host='localhost', port=8086):
    """Start the statusline WebSocket server"""
    bridge = StatuslineBridge()
    
    # Start statusline monitoring
    await bridge.start_statusline_monitoring()
    
    # Start WebSocket server
    logger.info(f"Starting statusline bridge WebSocket server on {host}:{port}")
    server = await websockets.serve(
        bridge.handle_websocket_connection,
        host,
        port
    )
    
    logger.info("Statusline bridge WebSocket server started")
    return server, bridge

# HTTP endpoint for statusline data
def create_statusline_endpoints():
    """Create HTTP endpoints for statusline data"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    bridge = StatuslineBridge()
    
    @app.route('/api/statusline/current', methods=['GET'])
    async def get_current_statusline():
        """Get current statusline data"""
        try:
            data = await bridge.get_current_statusline_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/statusline/config', methods=['POST'])
    async def update_statusline_config():
        """Update statusline configuration"""
        try:
            config = request.json
            if bridge.statusline_manager:
                bridge.statusline_manager.updateConfig(config)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/statusline/health', methods=['GET'])
    def statusline_health():
        """Health check for statusline bridge"""
        return jsonify({
            'status': 'healthy',
            'components': {
                'statusline_manager': bridge.statusline_manager is not None,
                'connected_clients': len(bridge.connected_clients)
            },
            'attribution': {
                'powerline': '@Owloops/claude-powerline',
                'devStack': 'Dev Stack monitoring by Zach',
                'browser': '@zainhoda/claude-code-browser'
            }
        })
    
    return app

# Main entry point
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Statusline Bridge for Claude Code Browser')
    parser.add_argument('--mode', choices=['websocket', 'http', 'both'], default='both',
                       help='Run mode: websocket, http, or both')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--websocket-port', type=int, default=8086, help='WebSocket port')
    parser.add_argument('--http-port', type=int, default=8087, help='HTTP port')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    async def main():
        servers = []
        
        if args.mode in ['websocket', 'both']:
            # Start WebSocket server
            ws_server, bridge = await start_statusline_websocket_server(args.host, args.websocket_port)
            servers.append(ws_server)
            
        if args.mode in ['http', 'both']:
            # Start HTTP server
            app = create_statusline_endpoints()
            # Note: In production, use proper ASGI server
            print(f"HTTP server would start on {args.host}:{args.http_port}")
            
        # Keep running
        if servers:
            await asyncio.gather(*[server.wait_closed() for server in servers])
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStatusline bridge shutting down...")