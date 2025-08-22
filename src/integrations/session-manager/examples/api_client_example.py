#!/usr/bin/env python3
"""
Session Management API Client Example
====================================

Demonstrates how to use the Claude Code Session Management API
for creating, managing, and monitoring sessions.
"""

import asyncio
import json
import aiohttp
from pathlib import Path


class SessionAPIClient:
    """Simple client for the Session Management API."""
    
    def __init__(self, base_url: str = "http://localhost:8082"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_session(self, name: str, working_directory: str, **kwargs):
        """Create a new session."""
        data = {
            'name': name,
            'working_directory': working_directory,
            **kwargs
        }
        
        async with self.session.post(f'{self.base_url}/api/claude/sessions', json=data) as resp:
            return await resp.json()
    
    async def list_sessions(self, **filters):
        """List sessions with optional filters."""
        async with self.session.get(f'{self.base_url}/api/claude/sessions', params=filters) as resp:
            return await resp.json()
    
    async def get_session(self, session_id: str):
        """Get session details."""
        async with self.session.get(f'{self.base_url}/api/claude/sessions/{session_id}') as resp:
            return await resp.json()
    
    async def update_session(self, session_id: str, **updates):
        """Update session configuration."""
        async with self.session.put(f'{self.base_url}/api/claude/sessions/{session_id}', json=updates) as resp:
            return await resp.json()
    
    async def navigate_session(self, session_id: str, path: str):
        """Navigate session to new path."""
        data = {'path': path}
        async with self.session.post(f'{self.base_url}/api/claude/sessions/{session_id}/navigate', json=data) as resp:
            return await resp.json()
    
    async def activate_agent(self, session_id: str, agent_name: str):
        """Activate an agent for a session."""
        async with self.session.post(f'{self.base_url}/api/claude/sessions/{session_id}/agents/{agent_name}/activate') as resp:
            return await resp.json()
    
    async def get_session_metrics(self, session_id: str, hours: int = 1):
        """Get session metrics."""
        params = {'hours': hours}
        async with self.session.get(f'{self.base_url}/api/claude/sessions/{session_id}/metrics', params=params) as resp:
            return await resp.json()
    
    async def validate_path(self, path: str):
        """Validate a path."""
        data = {'path': path}
        async with self.session.post(f'{self.base_url}/api/claude/validate-path', json=data) as resp:
            return await resp.json()
    
    async def get_agent_types(self):
        """Get available agent types."""
        async with self.session.get(f'{self.base_url}/api/claude/agent-types') as resp:
            return await resp.json()
    
    async def get_system_status(self):
        """Get system status."""
        async with self.session.get(f'{self.base_url}/api/claude/system-status') as resp:
            return await resp.json()
    
    async def clone_session(self, session_id: str, new_name: str, **kwargs):
        """Clone a session."""
        data = {'new_name': new_name, **kwargs}
        async with self.session.post(f'{self.base_url}/api/claude/sessions/{session_id}/clone', json=data) as resp:
            return await resp.json()
    
    async def terminate_session(self, session_id: str):
        """Terminate a session."""
        async with self.session.delete(f'{self.base_url}/api/claude/sessions/{session_id}') as resp:
            return await resp.json()


async def demo_session_lifecycle():
    """Demonstrate complete session lifecycle."""
    print("🚀 Claude Code Session Management API Demo")
    print("=" * 50)
    
    async with SessionAPIClient() as client:
        # 1. Check system status
        print("\n1. Checking system status...")
        status = await client.get_system_status()
        if status.get('success'):
            print(f"   ✅ System is healthy")
            print(f"   📊 Total sessions: {status['system_status']['sessions']['total_sessions']}")
        else:
            print(f"   ❌ System check failed: {status}")
            return
        
        # 2. Get available agent types
        print("\n2. Getting available agent types...")
        agent_types = await client.get_agent_types()
        if agent_types.get('success'):
            print(f"   ✅ Found {len(agent_types['agent_types'])} agent types")
            for name, details in list(agent_types['agent_types'].items())[:3]:
                print(f"      - {name}: {details['description']}")
        
        # 3. Validate a path
        print("\n3. Validating working directory...")
        test_path = str(Path.home() / "claude_demo_workspace")
        validation = await client.validate_path(test_path)
        if validation.get('success'):
            if validation['validation']['validation_errors']:
                print(f"   ⚠️  Path issues: {validation['validation']['validation_errors']}")
            else:
                print(f"   ✅ Path validated: {test_path}")
        
        # 4. Create a new session
        print("\n4. Creating new session...")
        session_data = await client.create_session(
            name="Demo Session",
            working_directory=test_path,
            description="API demonstration session",
            agents=[
                {
                    'agent_type': 'BACKEND',
                    'name': 'backend-services',
                    'enabled': True,
                    'priority': 2
                },
                {
                    'agent_type': 'FRONTEND', 
                    'name': 'frontend-architecture',
                    'enabled': True,
                    'priority': 2
                }
            ]
        )
        
        if session_data.get('success'):
            session_id = session_data['session']['id']
            print(f"   ✅ Session created: {session_id}")
            print(f"   📂 Working directory: {session_data['session']['configuration']['working_directory']}")
        else:
            print(f"   ❌ Session creation failed: {session_data}")
            return
        
        # 5. List sessions
        print("\n5. Listing sessions...")
        sessions = await client.list_sessions()
        if sessions.get('success'):
            print(f"   ✅ Found {sessions['total']} sessions")
            for session in sessions['sessions'][:2]:  # Show first 2
                print(f"      - {session['name']} ({session['status']})")
        
        # 6. Get session details
        print("\n6. Getting session details...")
        details = await client.get_session(session_id)
        if details.get('success'):
            session_info = details['session']
            print(f"   ✅ Session: {session_info['name']}")
            print(f"   📊 Status: {session_info['status']}")
            print(f"   🤖 Agents configured: {len(session_info['configuration']['agents'])}")
        
        # 7. Activate an agent
        print("\n7. Activating backend agent...")
        activation = await client.activate_agent(session_id, 'backend-services')
        if activation.get('success'):
            print(f"   ✅ Agent activated: {activation['agent_name']}")
        else:
            print(f"   ⚠️  Agent activation: {activation}")
        
        # 8. Update session
        print("\n8. Updating session description...")
        update = await client.update_session(
            session_id,
            description="Updated demo session with activated agents"
        )
        if update.get('success'):
            print(f"   ✅ Session updated")
        
        # 9. Clone session
        print("\n9. Cloning session...")
        clone = await client.clone_session(
            session_id,
            new_name="Demo Session Clone",
            copy_agents=True
        )
        if clone.get('success'):
            clone_id = clone['session']['id']
            print(f"   ✅ Session cloned: {clone_id}")
        
        # 10. Wait a moment for metrics
        print("\n10. Waiting for metrics collection...")
        await asyncio.sleep(2)
        
        # 11. Get session metrics
        print("\n11. Getting session metrics...")
        metrics = await client.get_session_metrics(session_id, hours=1)
        if metrics.get('success'):
            summary = metrics.get('summary', {})
            print(f"   ✅ Metrics collected")
            if 'duration_hours' in summary:
                print(f"   ⏱️  Duration: {summary['duration_hours']:.2f} hours")
            if 'total_data_points' in summary:
                print(f"   📊 Data points: {summary['total_data_points']}")
        
        # 12. Navigate session
        new_path = str(Path.home() / "claude_demo_workspace" / "subdir")
        print(f"\n12. Navigating to new path: {new_path}")
        navigation = await client.navigate_session(session_id, new_path)
        if navigation.get('success'):
            print(f"   ✅ Navigation successful")
        else:
            print(f"   ⚠️  Navigation: {navigation}")
        
        # 13. Cleanup - terminate sessions
        print("\n13. Cleaning up sessions...")
        for sid in [session_id, clone_id if 'clone_id' in locals() else None]:
            if sid:
                termination = await client.terminate_session(sid)
                if termination.get('success'):
                    print(f"   ✅ Session {sid} terminated")
        
        print("\n🎉 Demo completed successfully!")


async def demo_websocket_monitoring():
    """Demonstrate WebSocket real-time monitoring."""
    import websockets
    
    print("\n🔌 WebSocket Monitoring Demo")
    print("=" * 30)
    
    try:
        async with websockets.connect("ws://localhost:8082/ws/sessions") as websocket:
            print("   ✅ Connected to WebSocket")
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for a few messages
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"   📨 Received: {data['type']}")
                except asyncio.TimeoutError:
                    print(f"   ⏱️  No message received (attempt {i+1})")
                
    except Exception as e:
        print(f"   ❌ WebSocket demo failed: {e}")
        print("   💡 Make sure the session API server is running")


async def main():
    """Main demo function."""
    try:
        # Test basic API functionality
        await demo_session_lifecycle()
        
        # Test WebSocket monitoring
        await demo_websocket_monitoring()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\n💡 Make sure to start the session API server first:")
        print("   python integrations/session-manager/start_session_api.py")


if __name__ == "__main__":
    asyncio.run(main())