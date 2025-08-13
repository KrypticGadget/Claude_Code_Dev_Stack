#!/usr/bin/env python3
"""
Status Line Manager v3.0 - Real-time system status tracking and management
Provides WebSocket support, persistence, and intelligent status routing
"""

import json
import time
import sqlite3
import threading
import asyncio
import websockets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import psutil
import subprocess
import re

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

@dataclass
class StatusUpdate:
    """Status update data structure"""
    timestamp: str
    component: str
    status: str  # active|idle|error|complete
    metadata: Dict
    progress_percentage: int = 0
    estimated_completion: Optional[str] = None
    resource_usage: Optional[Dict] = None

class StatusLineCore:
    """
    Core status management system with real-time updates
    """
    
    def __init__(self):
        self.update_frequency = 100  # ms
        self.protocol = "websocket_with_polling_fallback"
        
        # Initialize data structures
        self.current_status = {
            "model": "claude-3-opus-20240229",
            "git": {"branch": "", "status": "", "ahead": 0},
            "phase": "initialization",
            "agent": "system",
            "tokens": {"used": 0, "limit": 8000}
        }
        
        # Setup persistence
        self.setup_persistence()
        
        # WebSocket server setup
        self.websocket_clients = set()
        self.server = None
        
        # Status listeners
        self.listeners = []
        
        # Background tasks
        self.update_thread = None
        self.running = False
        
        # Initialize git tracking
        self.update_git_status()
        
    def setup_persistence(self):
        """Setup SQLite and Redis persistence"""
        # SQLite setup
        self.db_path = Path.home() / ".claude" / "v3" / "status_history.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_conn.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                progress_percentage INTEGER DEFAULT 0,
                estimated_completion TEXT,
                resource_usage TEXT
            )
        """)
        self.db_conn.commit()
        
        # Redis setup (optional)
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                self.redis_client.ping()
            except:
                self.redis_client = None
    
    def start(self):
        """Start the status line system"""
        self.running = True
        
        # Start background update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Start WebSocket server
        asyncio.create_task(self._start_websocket_server())
    
    def stop(self):
        """Stop the status line system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        if self.db_conn:
            self.db_conn.close()
    
    def update_status(self, component: str, status: str, metadata: Dict = None, 
                     progress: int = 0, estimated_completion: str = None):
        """Update component status and notify listeners"""
        if metadata is None:
            metadata = {}
        
        # Get resource usage
        resource_usage = self.get_resource_usage()
        
        status_update = StatusUpdate(
            timestamp=datetime.utcnow().isoformat(),
            component=component,
            status=status,
            metadata=metadata,
            progress_percentage=progress,
            estimated_completion=estimated_completion,
            resource_usage=resource_usage
        )
        
        # Update current status
        self.current_status[component] = {
            'status': status,
            'timestamp': status_update.timestamp,
            'metadata': metadata,
            'progress': progress,
            'resource_usage': resource_usage
        }
        
        # Persist to SQLite
        self._persist_to_sqlite(status_update)
        
        # Cache in Redis if available
        if self.redis_client:
            self._cache_in_redis(status_update)
        
        # Notify listeners
        self._notify_listeners(status_update)
        
        # Send to WebSocket clients
        asyncio.create_task(self._broadcast_to_websockets(status_update))
    
    def get_current_status(self) -> Dict:
        """Get current system status"""
        # Update dynamic components
        self.update_git_status()
        self.update_resource_status()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.current_status,
            "system_health": self.get_system_health()
        }
    
    def get_status_history(self, timeframe: str = "1h", component: str = None) -> List[Dict]:
        """Get status history within timeframe"""
        # Parse timeframe
        hours = self._parse_timeframe(timeframe)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = """
            SELECT * FROM status_history 
            WHERE timestamp > ? 
        """
        params = [since.isoformat()]
        
        if component:
            query += " AND component = ?"
            params.append(component)
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        cursor = self.db_conn.execute(query, params)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def add_listener(self, event: str, callback: Callable):
        """Add status change listener"""
        self.listeners.append((event, callback))
    
    def get_intelligent_routing(self) -> Dict:
        """Determine optimal agent routing based on current status"""
        routing_suggestions = {
            "recommended_agents": [],
            "reasoning": [],
            "resource_constraints": [],
            "parallel_opportunities": []
        }
        
        # Analyze current system state
        current_phase = self.current_status.get("phase", "unknown")
        active_agents = self.current_status.get("active_agents", [])
        resource_usage = self.get_resource_usage()
        
        # Resource-based routing
        if resource_usage["cpu_percent"] > 80:
            routing_suggestions["resource_constraints"].append("High CPU usage - consider lighter agents")
        
        if resource_usage["memory_percent"] > 85:
            routing_suggestions["resource_constraints"].append("High memory usage - avoid memory-intensive agents")
        
        # Phase-based routing
        phase_agents = {
            "initialization": ["system-architect", "project-manager"],
            "development": ["backend-engineer", "frontend-architect"],
            "testing": ["testing-automation", "quality-assurance"],
            "deployment": ["devops-engineer", "deployment-orchestrator"]
        }
        
        if current_phase in phase_agents:
            routing_suggestions["recommended_agents"].extend(phase_agents[current_phase])
            routing_suggestions["reasoning"].append(f"Phase '{current_phase}' suggests these agents")
        
        # Parallel execution opportunities
        if resource_usage["cpu_percent"] < 50 and resource_usage["memory_percent"] < 60:
            routing_suggestions["parallel_opportunities"].append("System resources allow parallel agent execution")
        
        return routing_suggestions
    
    def update_git_status(self):
        """Update Git repository status"""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, text=True, timeout=5
            )
            branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, timeout=5
            )
            status = "clean" if not result.stdout.strip() else "modified"
            
            # Get ahead/behind count
            result = subprocess.run(
                ["git", "rev-list", "--count", "--left-right", f"HEAD...origin/{branch}"],
                capture_output=True, text=True, timeout=5
            )
            ahead = 0
            if result.returncode == 0 and result.stdout.strip():
                counts = result.stdout.strip().split('\t')
                ahead = int(counts[0]) if len(counts) > 0 else 0
            
            self.current_status["git"] = {
                "branch": branch,
                "status": status,
                "ahead": ahead
            }
            
        except Exception:
            self.current_status["git"] = {
                "branch": "unknown",
                "status": "unknown", 
                "ahead": 0
            }
    
    def update_resource_status(self):
        """Update system resource status"""
        resource_usage = self.get_resource_usage()
        self.current_status["resources"] = resource_usage
    
    def get_resource_usage(self) -> Dict:
        """Get current system resource usage"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            }
        except Exception:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "network_io": {"bytes_sent": 0, "bytes_recv": 0}
            }
    
    def get_system_health(self) -> Dict:
        """Get overall system health assessment"""
        resource_usage = self.get_resource_usage()
        
        health_score = 100
        issues = []
        
        # CPU health
        if resource_usage["cpu_percent"] > 90:
            health_score -= 30
            issues.append("High CPU usage")
        elif resource_usage["cpu_percent"] > 70:
            health_score -= 15
        
        # Memory health
        if resource_usage["memory_percent"] > 90:
            health_score -= 25
            issues.append("High memory usage")
        elif resource_usage["memory_percent"] > 80:
            health_score -= 10
        
        # Disk health
        if resource_usage["disk_percent"] > 90:
            health_score -= 20
            issues.append("Low disk space")
        
        health_status = "excellent" if health_score >= 90 else \
                       "good" if health_score >= 70 else \
                       "warning" if health_score >= 50 else "critical"
        
        return {
            "score": max(0, health_score),
            "status": health_status,
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                # Update dynamic status
                self.update_resource_status()
                
                # Check for system events
                self._check_system_events()
                
                time.sleep(self.update_frequency / 1000.0)  # Convert ms to seconds
            except Exception:
                pass  # Continue running even if update fails
    
    def _check_system_events(self):
        """Check for system events that need status updates"""
        # This could check for file changes, process events, etc.
        pass
    
    def _persist_to_sqlite(self, status_update: StatusUpdate):
        """Persist status update to SQLite"""
        try:
            self.db_conn.execute("""
                INSERT INTO status_history 
                (timestamp, component, status, metadata, progress_percentage, estimated_completion, resource_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                status_update.timestamp,
                status_update.component,
                status_update.status,
                json.dumps(status_update.metadata),
                status_update.progress_percentage,
                status_update.estimated_completion,
                json.dumps(status_update.resource_usage) if status_update.resource_usage else None
            ))
            self.db_conn.commit()
        except Exception:
            pass  # Fail silently to avoid breaking status updates
    
    def _cache_in_redis(self, status_update: StatusUpdate):
        """Cache status update in Redis"""
        if not self.redis_client:
            return
        
        try:
            # Store current status
            self.redis_client.hset(
                "claude_status:current",
                status_update.component,
                json.dumps(asdict(status_update))
            )
            
            # Store in time-series for history
            self.redis_client.zadd(
                f"claude_status:history:{status_update.component}",
                {json.dumps(asdict(status_update)): time.time()}
            )
            
            # Expire old entries (keep 24 hours)
            cutoff = time.time() - (24 * 60 * 60)
            self.redis_client.zremrangebyscore(
                f"claude_status:history:{status_update.component}",
                0, cutoff
            )
            
        except Exception:
            pass  # Fail silently
    
    def _notify_listeners(self, status_update: StatusUpdate):
        """Notify registered listeners"""
        for event, callback in self.listeners:
            try:
                if event == "status_change" or event == status_update.component:
                    callback(status_update)
            except Exception:
                pass  # Don't let listener errors break status updates
    
    async def _broadcast_to_websockets(self, status_update: StatusUpdate):
        """Broadcast status update to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = json.dumps({
            "type": "status_update",
            "data": asdict(status_update)
        })
        
        # Remove disconnected clients
        disconnected = set()
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except:
                disconnected.add(client)
        
        self.websocket_clients -= disconnected
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                # Send current status immediately
                current_status = self.get_current_status()
                await websocket.send(json.dumps({
                    "type": "current_status",
                    "data": current_status
                }))
                
                # Keep connection alive
                await websocket.wait_closed()
            finally:
                self.websocket_clients.discard(websocket)
        
        try:
            self.server = await websockets.serve(handle_client, "localhost", 8080)
        except Exception:
            pass  # Fail silently if WebSocket server can't start
    
    def _parse_timeframe(self, timeframe: str) -> float:
        """Parse timeframe string to hours"""
        timeframe = timeframe.lower()
        if timeframe.endswith('m'):
            return float(timeframe[:-1]) / 60
        elif timeframe.endswith('h'):
            return float(timeframe[:-1])
        elif timeframe.endswith('d'):
            return float(timeframe[:-1]) * 24
        else:
            return 1.0  # Default to 1 hour


# Global instance
status_line = None

def get_status_line():
    """Get or create status line instance"""
    global status_line
    if status_line is None:
        status_line = StatusLineCore()
        status_line.start()
    return status_line

def process_hook(event_type: str, data: Dict) -> Dict:
    """Hook entry point for status line integration"""
    status_line = get_status_line()
    
    try:
        if event_type == 'agent_activated':
            agent = data.get('agent', 'unknown')
            status_line.update_status(
                'agent', 
                'active', 
                {'current_agent': agent}
            )
            return {'status_updated': True, 'agent': agent}
        
        elif event_type == 'phase_transition':
            phase = data.get('phase', 'unknown')
            status_line.update_status(
                'phase',
                'active',
                {'current_phase': phase}
            )
            return {'status_updated': True, 'phase': phase}
        
        elif event_type == 'token_usage':
            tokens = data.get('tokens', {})
            status_line.current_status['tokens'] = tokens
            return {'status_updated': True, 'tokens': tokens}
        
        elif event_type == 'get_status':
            return status_line.get_current_status()
        
        elif event_type == 'get_routing':
            return status_line.get_intelligent_routing()
        
        return {'processed': True}
        
    except Exception as e:
        return {'error': str(e), 'processed': False}


# Export for hook system
__all__ = ['process_hook', 'StatusLineCore', 'get_status_line']