"""
Session Management API
=====================

Comprehensive REST API for Claude Code session management.
Provides all endpoints for session lifecycle, monitoring, and analytics.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from aiohttp import web, WSMsgType
import aiofiles

import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.session_manager import SessionManager, SessionNotFoundError, SessionValidationError
from services.path_validator import PathValidator
from services.agent_initializer import AgentInitializer
from services.session_monitor import SessionMonitor
from models.session_models import (
    SessionCreateRequest, SessionUpdateRequest, SessionNavigateRequest,
    SessionCloneRequest, SessionImportRequest, SessionListFilter,
    SessionStatus, AgentType
)


class SessionAPI:
    """
    Main session management API providing comprehensive session control
    and monitoring capabilities.
    """
    
    def __init__(self, port: int = 8082):
        self.port = port
        self.app = web.Application()
        self.websocket_clients = set()
        
        # Core services
        self.session_manager = SessionManager()
        self.path_validator = PathValidator()
        self.agent_initializer = AgentInitializer()
        self.session_monitor = SessionMonitor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
        
        # Setup WebSocket broadcasting
        self.session_monitor.add_alert_callback(self._broadcast_alert)
    
    def _setup_routes(self):
        """Setup API routes."""
        # Session CRUD operations
        self.app.router.add_post('/api/claude/sessions', self.create_session)
        self.app.router.add_get('/api/claude/sessions', self.list_sessions)
        self.app.router.add_get('/api/claude/sessions/{session_id}', self.get_session)
        self.app.router.add_put('/api/claude/sessions/{session_id}', self.update_session)
        self.app.router.add_delete('/api/claude/sessions/{session_id}', self.terminate_session)
        
        # Session operations
        self.app.router.add_post('/api/claude/sessions/{session_id}/navigate', self.navigate_session)
        self.app.router.add_post('/api/claude/sessions/{session_id}/clone', self.clone_session)
        self.app.router.add_post('/api/claude/sessions/{session_id}/export', self.export_session)
        self.app.router.add_post('/api/claude/sessions/import', self.import_session)
        
        # Agent management
        self.app.router.add_get('/api/claude/sessions/{session_id}/agents', self.get_session_agents)
        self.app.router.add_post('/api/claude/sessions/{session_id}/agents/{agent_name}/activate', self.activate_agent)
        self.app.router.add_post('/api/claude/sessions/{session_id}/agents/{agent_name}/deactivate', self.deactivate_agent)
        self.app.router.add_post('/api/claude/sessions/{session_id}/agents/{agent_name}/restart', self.restart_agent)
        
        # Monitoring and analytics
        self.app.router.add_get('/api/claude/sessions/{session_id}/metrics', self.get_session_metrics)
        self.app.router.add_get('/api/claude/sessions/{session_id}/status', self.get_session_status)
        self.app.router.add_get('/api/claude/analytics', self.get_analytics)
        
        # Path validation
        self.app.router.add_post('/api/claude/validate-path', self.validate_path)
        self.app.router.add_post('/api/claude/validate-paths', self.validate_paths)
        
        # Agent types and capabilities
        self.app.router.add_get('/api/claude/agent-types', self.get_agent_types)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws/sessions', self.websocket_handler)
        
        # Health and system status
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/api/claude/system-status', self.get_system_status)
        
        # CORS support
        self.app.router.add_options('/{path:.*}', self.options_handler)
        
        # Add CORS middleware
        self.app.middlewares.append(self._cors_middleware)
    
    @web.middleware
    async def _cors_middleware(self, request, handler):
        """CORS middleware for cross-origin requests."""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    async def options_handler(self, request):
        """Handle CORS preflight requests."""
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        })
    
    # Session CRUD Operations
    
    async def create_session(self, request):
        """Create a new session."""
        try:
            data = await request.json()
            
            # Validate required fields
            if 'name' not in data or 'working_directory' not in data:
                return web.json_response(
                    {'error': 'name and working_directory are required'},
                    status=400
                )
            
            # Create request object
            create_request = SessionCreateRequest(
                name=data['name'],
                working_directory=data['working_directory'],
                description=data.get('description', ''),
                git_enabled=data.get('git_enabled', True),
                auto_save=data.get('auto_save', True),
                agents=data.get('agents', []),
                environment_variables=data.get('environment_variables', {}),
                custom_settings=data.get('custom_settings', {})
            )
            
            # Create session
            session = await self.session_manager.create_session(create_request)
            
            # Add to monitoring
            self.session_monitor.add_session(session)
            
            # Broadcast session creation
            await self._broadcast_session_update('session_created', session.to_dict())
            
            return web.json_response({
                'success': True,
                'session': session.to_dict()
            })
            
        except SessionValidationError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def list_sessions(self, request):
        """List sessions with optional filtering."""
        try:
            # Parse query parameters
            status = request.query.get('status')
            name_pattern = request.query.get('name_pattern')
            created_after = request.query.get('created_after')
            created_before = request.query.get('created_before')
            has_agents = request.query.get('has_agents')
            working_directory_pattern = request.query.get('working_directory_pattern')
            limit = int(request.query.get('limit', 100))
            offset = int(request.query.get('offset', 0))
            
            # Create filter
            filter_options = SessionListFilter(
                status=SessionStatus(status) if status else None,
                name_pattern=name_pattern,
                created_after=float(created_after) if created_after else None,
                created_before=float(created_before) if created_before else None,
                has_agents=bool(has_agents) if has_agents is not None else None,
                working_directory_pattern=working_directory_pattern,
                limit=limit,
                offset=offset
            )
            
            # Get sessions
            sessions = self.session_manager.list_sessions(filter_options)
            
            return web.json_response({
                'success': True,
                'sessions': [session.to_dict() for session in sessions],
                'total': len(sessions),
                'filter': {
                    'limit': limit,
                    'offset': offset,
                    'status': status,
                    'name_pattern': name_pattern
                }
            })
            
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def get_session(self, request):
        """Get session details by ID."""
        try:
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            # Get additional monitoring data
            metrics_summary = self.session_monitor.get_session_summary(session_id)
            agent_statuses = self.agent_initializer.get_all_agent_statuses()
            
            return web.json_response({
                'success': True,
                'session': session.to_dict(),
                'monitoring': metrics_summary,
                'agent_statuses': agent_statuses
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def update_session(self, request):
        """Update session configuration."""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            
            # Create update request
            update_request = SessionUpdateRequest(
                name=data.get('name'),
                description=data.get('description'),
                auto_save=data.get('auto_save'),
                save_interval_seconds=data.get('save_interval_seconds'),
                max_memory_mb=data.get('max_memory_mb'),
                max_agents=data.get('max_agents'),
                environment_variables=data.get('environment_variables'),
                custom_settings=data.get('custom_settings')
            )
            
            # Update session
            session = await self.session_manager.update_session(session_id, update_request)
            
            # Broadcast update
            await self._broadcast_session_update('session_updated', session.to_dict())
            
            return web.json_response({
                'success': True,
                'session': session.to_dict()
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to update session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def terminate_session(self, request):
        """Terminate a session."""
        try:
            session_id = request.match_info['session_id']
            
            # Terminate session
            session = await self.session_manager.terminate_session(session_id)
            
            # Remove from monitoring
            self.session_monitor.remove_session(session_id)
            
            # Broadcast termination
            await self._broadcast_session_update('session_terminated', session.to_dict())
            
            return web.json_response({
                'success': True,
                'session': session.to_dict()
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to terminate session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # Session Operations
    
    async def navigate_session(self, request):
        """Navigate session to new path."""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            
            if 'path' not in data:
                return web.json_response({'error': 'path is required'}, status=400)
            
            # Create navigate request
            navigate_request = SessionNavigateRequest(
                path=data['path'],
                validate_permissions=data.get('validate_permissions', True),
                update_git_state=data.get('update_git_state', True)
            )
            
            # Navigate session
            session = await self.session_manager.navigate_session(session_id, navigate_request)
            
            # Broadcast navigation
            await self._broadcast_session_update('session_navigated', {
                'session_id': session_id,
                'new_path': data['path'],
                'session': session.to_dict()
            })
            
            return web.json_response({
                'success': True,
                'session': session.to_dict()
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except SessionValidationError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            self.logger.error(f"Failed to navigate session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def clone_session(self, request):
        """Clone an existing session."""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            
            if 'new_name' not in data:
                return web.json_response({'error': 'new_name is required'}, status=400)
            
            # Create clone request
            clone_request = SessionCloneRequest(
                source_session_id=session_id,
                new_name=data['new_name'],
                new_working_directory=data.get('new_working_directory'),
                copy_agents=data.get('copy_agents', True),
                copy_environment=data.get('copy_environment', True)
            )
            
            # Clone session
            new_session = await self.session_manager.clone_session(clone_request)
            
            # Add to monitoring
            self.session_monitor.add_session(new_session)
            
            # Broadcast clone
            await self._broadcast_session_update('session_cloned', {
                'source_session_id': session_id,
                'new_session': new_session.to_dict()
            })
            
            return web.json_response({
                'success': True,
                'session': new_session.to_dict()
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to clone session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def export_session(self, request):
        """Export session data."""
        try:
            session_id = request.match_info['session_id']
            
            # Export session
            snapshot = self.session_manager.export_session(session_id)
            
            return web.json_response({
                'success': True,
                'snapshot': snapshot.__dict__
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to export session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def import_session(self, request):
        """Import session data."""
        try:
            data = await request.json()
            
            if 'session_data' not in data:
                return web.json_response({'error': 'session_data is required'}, status=400)
            
            # Create import request
            import_request = SessionImportRequest(
                session_data=data['session_data'],
                merge_with_existing=data.get('merge_with_existing', False),
                update_paths=data.get('update_paths', True)
            )
            
            # Import session
            session = await self.session_manager.import_session(import_request)
            
            # Add to monitoring
            self.session_monitor.add_session(session)
            
            # Broadcast import
            await self._broadcast_session_update('session_imported', session.to_dict())
            
            return web.json_response({
                'success': True,
                'session': session.to_dict()
            })
            
        except Exception as e:
            self.logger.error(f"Failed to import session: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # Agent Management
    
    async def get_session_agents(self, request):
        """Get agents for a session."""
        try:
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            # Get agent statuses
            agent_statuses = self.agent_initializer.get_all_agent_statuses()
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'configured_agents': [agent.__dict__ for agent in session.configuration.agents],
                'active_agents': session.context.active_agents,
                'agent_statuses': agent_statuses
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to get session agents: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def activate_agent(self, request):
        """Activate an agent for a session."""
        try:
            session_id = request.match_info['session_id']
            agent_name = request.match_info['agent_name']
            
            session = self.session_manager.get_session(session_id)
            
            # Activate agent
            success = await self.agent_initializer.activate_agent(agent_name, session.context)
            
            if success:
                # Broadcast activation
                await self._broadcast_session_update('agent_activated', {
                    'session_id': session_id,
                    'agent_name': agent_name
                })
                
                return web.json_response({
                    'success': True,
                    'agent_name': agent_name,
                    'status': 'activated'
                })
            else:
                return web.json_response({
                    'error': f'Failed to activate agent {agent_name}'
                }, status=500)
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to activate agent: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def deactivate_agent(self, request):
        """Deactivate an agent for a session."""
        try:
            session_id = request.match_info['session_id']
            agent_name = request.match_info['agent_name']
            
            session = self.session_manager.get_session(session_id)
            
            # Deactivate agent
            success = await self.agent_initializer.deactivate_agent(agent_name, session.context)
            
            if success:
                # Broadcast deactivation
                await self._broadcast_session_update('agent_deactivated', {
                    'session_id': session_id,
                    'agent_name': agent_name
                })
                
                return web.json_response({
                    'success': True,
                    'agent_name': agent_name,
                    'status': 'deactivated'
                })
            else:
                return web.json_response({
                    'error': f'Failed to deactivate agent {agent_name}'
                }, status=500)
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to deactivate agent: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def restart_agent(self, request):
        """Restart an agent for a session."""
        try:
            session_id = request.match_info['session_id']
            agent_name = request.match_info['agent_name']
            
            session = self.session_manager.get_session(session_id)
            
            # Restart agent
            success = await self.agent_initializer.restart_agent(
                agent_name, session.configuration, session.context
            )
            
            if success:
                # Broadcast restart
                await self._broadcast_session_update('agent_restarted', {
                    'session_id': session_id,
                    'agent_name': agent_name
                })
                
                return web.json_response({
                    'success': True,
                    'agent_name': agent_name,
                    'status': 'restarted'
                })
            else:
                return web.json_response({
                    'error': f'Failed to restart agent {agent_name}'
                }, status=500)
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to restart agent: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # Monitoring and Analytics
    
    async def get_session_metrics(self, request):
        """Get session metrics and monitoring data."""
        try:
            session_id = request.match_info['session_id']
            hours = int(request.query.get('hours', 1))
            
            # Get session to verify it exists
            session = self.session_manager.get_session(session_id)
            
            # Get metrics
            metrics = self.session_monitor.get_session_metrics(session_id, hours)
            summary = self.session_monitor.get_session_summary(session_id)
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'metrics': metrics,
                'summary': summary,
                'hours': hours
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to get session metrics: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def get_session_status(self, request):
        """Get current session status."""
        try:
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            # Get real-time status
            agent_statuses = self.agent_initializer.get_all_agent_statuses()
            metrics_summary = self.session_monitor.get_session_summary(session_id)
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'status': session.status.value,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'working_directory': session.configuration.working_directory,
                'active_agents': session.context.active_agents,
                'agent_statuses': agent_statuses,
                'metrics': metrics_summary
            })
            
        except SessionNotFoundError as e:
            return web.json_response({'error': str(e)}, status=404)
        except Exception as e:
            self.logger.error(f"Failed to get session status: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def get_analytics(self, request):
        """Get system-wide analytics."""
        try:
            analytics = self.session_manager.get_session_analytics()
            
            return web.json_response({
                'success': True,
                'analytics': analytics
            })
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # Path Validation
    
    async def validate_path(self, request):
        """Validate a single path."""
        try:
            data = await request.json()
            
            if 'path' not in data:
                return web.json_response({'error': 'path is required'}, status=400)
            
            validation = self.path_validator.validate_path(
                data['path'],
                create_if_missing=data.get('create_if_missing', True)
            )
            
            # Get suggestions if validation failed
            suggestions = []
            if validation.validation_errors:
                suggestions = self.path_validator.suggest_alternative_paths(data['path'])
            
            return web.json_response({
                'success': True,
                'validation': validation.__dict__,
                'suggestions': suggestions
            })
            
        except Exception as e:
            self.logger.error(f"Failed to validate path: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def validate_paths(self, request):
        """Validate multiple paths."""
        try:
            data = await request.json()
            
            if 'paths' not in data or not isinstance(data['paths'], list):
                return web.json_response({'error': 'paths array is required'}, status=400)
            
            validations = self.path_validator.validate_multiple_paths(data['paths'])
            
            # Convert to serializable format
            results = {}
            for path, validation in validations.items():
                results[path] = validation.__dict__
            
            return web.json_response({
                'success': True,
                'validations': results
            })
            
        except Exception as e:
            self.logger.error(f"Failed to validate paths: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # Agent Types
    
    async def get_agent_types(self, request):
        """Get available agent types and capabilities."""
        try:
            agent_types = self.agent_initializer.get_available_agents()
            
            return web.json_response({
                'success': True,
                'agent_types': agent_types
            })
            
        except Exception as e:
            self.logger.error(f"Failed to get agent types: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    # WebSocket and Broadcasting
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_clients.add(ws)
        self.logger.info(f"WebSocket client connected ({len(self.websocket_clients)} total)")
        
        try:
            # Send initial state
            await ws.send_str(json.dumps({
                'type': 'connected',
                'timestamp': time.time(),
                'session_count': len(self.session_manager.sessions),
                'active_sessions': len(self.session_manager.active_sessions)
            }))
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle incoming messages if needed
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_clients.discard(ws)
            self.logger.info(f"WebSocket client disconnected ({len(self.websocket_clients)} total)")
        
        return ws
    
    async def _handle_websocket_message(self, ws, data):
        """Handle incoming WebSocket messages."""
        message_type = data.get('type')
        
        if message_type == 'subscribe_session':
            session_id = data.get('session_id')
            if session_id:
                # Send current session status
                try:
                    session = self.session_manager.get_session(session_id)
                    await ws.send_str(json.dumps({
                        'type': 'session_status',
                        'session': session.to_dict()
                    }))
                except SessionNotFoundError:
                    await ws.send_str(json.dumps({
                        'type': 'error',
                        'message': f'Session {session_id} not found'
                    }))
        
        elif message_type == 'ping':
            await ws.send_str(json.dumps({
                'type': 'pong',
                'timestamp': time.time()
            }))
    
    async def _broadcast_session_update(self, update_type: str, data: Any):
        """Broadcast session updates to WebSocket clients."""
        if not self.websocket_clients:
            return
        
        message = json.dumps({
            'type': update_type,
            'data': data,
            'timestamp': time.time()
        })
        
        disconnected = set()
        for client in self.websocket_clients:
            try:
                await client.send_str(message)
            except:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected
    
    async def _broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast alerts to WebSocket clients."""
        await self._broadcast_session_update('alert', alert)
    
    # System Status
    
    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'services': {
                'session_manager': 'running',
                'path_validator': 'running',
                'agent_initializer': 'running',
                'session_monitor': 'running' if self.session_monitor.monitoring_active else 'idle'
            }
        })
    
    async def get_system_status(self, request):
        """Get detailed system status."""
        try:
            analytics = self.session_manager.get_session_analytics()
            
            return web.json_response({
                'success': True,
                'system_status': {
                    'timestamp': time.time(),
                    'uptime_seconds': time.time() - getattr(self, 'start_time', time.time()),
                    'sessions': analytics,
                    'monitoring': {
                        'active': self.session_monitor.monitoring_active,
                        'monitored_sessions': len(self.session_monitor.monitored_sessions),
                        'websocket_clients': len(self.websocket_clients)
                    },
                    'agents': {
                        'available_types': len(self.agent_initializer.get_available_agents()),
                        'active_agents': len(self.agent_initializer.active_agents)
                    }
                }
            })
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)
    
    async def start(self):
        """Start the API server."""
        self.start_time = time.time()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        self.logger.info(f"Session Management API started on http://localhost:{self.port}")
        self.logger.info(f"WebSocket endpoint: ws://localhost:{self.port}/ws/sessions")
        
        print(f"🚀 Claude Code Session Management API")
        print(f"   Server: http://localhost:{self.port}")
        print(f"   WebSocket: ws://localhost:{self.port}/ws/sessions")
        print(f"   Health: http://localhost:{self.port}/health")
    
    async def stop(self):
        """Stop the API server."""
        # Cleanup monitoring
        self.session_monitor.cleanup()
        
        # Close WebSocket connections
        for client in self.websocket_clients:
            await client.close()
        
        await self.app.shutdown()
        await self.app.cleanup()
        
        self.logger.info("Session Management API stopped")