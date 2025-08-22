"""
Agent Status Segment

Displays information about active Claude Code agents, their status,
and current activities.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils
from ..themes import Theme


class AgentStatusSegment(BaseSegment):
    """Segment that displays Claude Code agent status information"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.show_active_agents = config.get('show_active_agents', True)
        self.show_agent_count = config.get('show_agent_count', True)
        self.show_current_agent = config.get('show_current_agent', False)
        self.max_agents_shown = config.get('max_agents_shown', 3)
        self.compact_display = config.get('compact_display', True)
        self.show_icons = config.get('show_icons', True)
        self.show_tier_info = config.get('show_tier_info', False)
        
        # Agent registry paths
        self.agent_registry_paths = self._find_agent_registry_paths()
        
        # Cache for agent data
        self._agent_cache = {}
        self._last_agent_check = 0
        self._agent_cache_timeout = 5.0  # 5 seconds
    
    def _find_agent_registry_paths(self) -> List[str]:
        """Find possible paths for agent registry files"""
        base_path = os.getcwd()
        
        possible_paths = [
            os.path.join(base_path, "agent-registry.json"),
            os.path.join(base_path, "config", "agent-registry.json"),
            os.path.join(base_path, "core", "agents", "registry.json"),
            os.path.join(base_path, ".claude", "agents.json"),
            os.path.expanduser("~/.config/claude-code/agents.json"),
            os.path.expanduser("~/.claude/agents.json")
        ]
        
        return [path for path in possible_paths if os.path.exists(path)]
    
    def _collect_data(self) -> SegmentData:
        """Collect agent status information"""
        agent_data = self._get_agent_data()
        
        if not agent_data:
            return SegmentData(
                content="",
                status="no_agents",
                tooltip="No agent information available"
            )
        
        content_parts = []
        
        # Active agent count
        if self.show_agent_count:
            active_count = len(agent_data.get('active_agents', []))
            total_count = len(agent_data.get('all_agents', []))
            
            if self.compact_display:
                content_parts.append(f"{active_count}/{total_count}")
            else:
                agent_icon = self._get_agent_icon()
                if agent_icon:
                    content_parts.append(f"{agent_icon} {active_count}/{total_count}")
                else:
                    content_parts.append(f"Agents: {active_count}/{total_count}")
        
        # Current active agent
        if self.show_current_agent:
            current_agent = agent_data.get('current_agent')
            if current_agent:
                agent_name = self._format_agent_name(current_agent.get('name', 'Unknown'))
                content_parts.append(f"[{agent_name}]")
        
        # List of active agents
        if self.show_active_agents:
            active_agents = agent_data.get('active_agents', [])
            if active_agents:
                agent_names = []
                for i, agent in enumerate(active_agents[:self.max_agents_shown]):
                    name = self._format_agent_name(agent.get('name', f'Agent{i+1}'))
                    status = agent.get('status', 'unknown')
                    
                    if status == 'busy':
                        name = f"{name}*"
                    elif status == 'error':
                        name = f"{name}!"
                    
                    agent_names.append(name)
                
                if len(active_agents) > self.max_agents_shown:
                    agent_names.append(f"+{len(active_agents) - self.max_agents_shown}")
                
                if self.compact_display:
                    content_parts.append(','.join(agent_names))
                else:
                    content_parts.append(f"Active: {', '.join(agent_names)}")
        
        # Tier information
        if self.show_tier_info:
            tier_info = self._get_tier_distribution(agent_data)
            if tier_info:
                content_parts.append(tier_info)
        
        content = ' '.join(content_parts) if content_parts else "No agents"
        
        # Determine status
        status = self._determine_status(agent_data)
        
        # Generate tooltip
        tooltip = self._generate_tooltip(agent_data)
        
        return SegmentData(
            content=content,
            status=status,
            icon=self._get_agent_icon(),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format agent status data for display"""
        return data.content
    
    def _get_agent_data(self) -> Dict[str, Any]:
        """Get agent information from registry and runtime data"""
        current_time = time.time()
        
        # Use cache if recent
        if (current_time - self._last_agent_check) < self._agent_cache_timeout and self._agent_cache:
            return self._agent_cache
        
        agent_data = {
            'all_agents': [],
            'active_agents': [],
            'current_agent': None,
            'tier_distribution': {}
        }
        
        try:
            # Load agent registry
            registry_data = self._load_agent_registry()
            if registry_data:
                agent_data['all_agents'] = registry_data.get('agents', [])
                agent_data['tier_distribution'] = self._calculate_tier_distribution(agent_data['all_agents'])
            
            # Get active agents from runtime data
            active_agents = self._get_active_agents()
            agent_data['active_agents'] = active_agents
            
            # Get current agent (if any)
            current_agent = self._get_current_agent()
            agent_data['current_agent'] = current_agent
            
        except Exception as e:
            # If there's an error, return minimal data
            agent_data['error'] = str(e)
        
        # Cache the result
        self._agent_cache = agent_data
        self._last_agent_check = current_time
        
        return agent_data
    
    def _load_agent_registry(self) -> Optional[Dict[str, Any]]:
        """Load agent registry from file"""
        for registry_path in self.agent_registry_paths:
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                    return registry_data
            except Exception:
                continue
        
        return None
    
    def _get_active_agents(self) -> List[Dict[str, Any]]:
        """Get list of currently active agents"""
        active_agents = []
        
        try:
            # Check for agent status files
            status_paths = [
                os.path.join(os.getcwd(), ".claude", "agent_status.json"),
                os.path.join(os.getcwd(), "logs", "agent_status.json"),
                "/tmp/claude_agent_status.json"
            ]
            
            for status_path in status_paths:
                if os.path.exists(status_path):
                    try:
                        with open(status_path, 'r') as f:
                            status_data = json.load(f)
                            agents = status_data.get('active_agents', [])
                            active_agents.extend(agents)
                    except Exception:
                        continue
            
            # Remove duplicates based on agent name
            seen_names = set()
            unique_agents = []
            for agent in active_agents:
                name = agent.get('name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_agents.append(agent)
            
            return unique_agents
            
        except Exception:
            return []
    
    def _get_current_agent(self) -> Optional[Dict[str, Any]]:
        """Get currently executing agent"""
        try:
            # Check environment variable
            current_agent_name = os.getenv('CLAUDE_CURRENT_AGENT')
            if current_agent_name:
                return {
                    'name': current_agent_name,
                    'source': 'environment'
                }
            
            # Check status files
            status_paths = [
                os.path.join(os.getcwd(), ".claude", "current_agent.json"),
                "/tmp/claude_current_agent.json"
            ]
            
            for status_path in status_paths:
                if os.path.exists(status_path):
                    try:
                        with open(status_path, 'r') as f:
                            current_data = json.load(f)
                            return current_data
                    except Exception:
                        continue
            
        except Exception:
            pass
        
        return None
    
    def _calculate_tier_distribution(self, agents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of agents across tiers"""
        tier_counts = {}
        
        for agent in agents:
            tier = agent.get('tier', 'unknown')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        return tier_counts
    
    def _get_tier_distribution(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Format tier distribution for display"""
        tier_dist = agent_data.get('tier_distribution', {})
        if not tier_dist:
            return None
        
        # Format as T0:2 T1:5 T2:3 etc.
        tier_parts = []
        for tier in sorted(tier_dist.keys()):
            if tier != 'unknown':
                count = tier_dist[tier]
                tier_parts.append(f"T{tier}:{count}")
        
        return ' '.join(tier_parts) if tier_parts else None
    
    def _format_agent_name(self, name: str) -> str:
        """Format agent name for display"""
        # Remove common prefixes/suffixes
        name = name.replace('agent-', '').replace('-agent', '')
        name = name.replace('Agent', '').replace('AGENT', '')
        
        # Capitalize first letter
        if name:
            name = name[0].upper() + name[1:]
        
        # Truncate if too long
        if len(name) > 10:
            name = name[:8] + '..'
        
        return name
    
    def _determine_status(self, agent_data: Dict[str, Any]) -> str:
        """Determine overall agent status"""
        if 'error' in agent_data:
            return 'error'
        
        active_agents = agent_data.get('active_agents', [])
        
        if not active_agents:
            return 'idle'
        
        # Check for any agents with error status
        for agent in active_agents:
            if agent.get('status') == 'error':
                return 'error'
        
        # Check for busy agents
        for agent in active_agents:
            if agent.get('status') == 'busy':
                return 'busy'
        
        return 'active'
    
    def _get_agent_icon(self) -> Optional[str]:
        """Get agent icon from theme"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('agent', '🤖')
        
        return '🤖'
    
    def _generate_tooltip(self, agent_data: Dict[str, Any]) -> str:
        """Generate detailed tooltip for agent status"""
        lines = []
        
        if 'error' in agent_data:
            lines.append(f"Error: {agent_data['error']}")
            return '\n'.join(lines)
        
        # Total agent count
        all_agents = agent_data.get('all_agents', [])
        active_agents = agent_data.get('active_agents', [])
        
        lines.append(f"Total agents: {len(all_agents)}")
        lines.append(f"Active agents: {len(active_agents)}")
        
        # Current agent
        current_agent = agent_data.get('current_agent')
        if current_agent:
            lines.append(f"Current: {current_agent.get('name', 'Unknown')}")
        
        # Active agent details
        if active_agents:
            lines.append("\nActive agents:")
            for agent in active_agents[:5]:  # Show up to 5 in tooltip
                name = agent.get('name', 'Unknown')
                status = agent.get('status', 'unknown')
                tier = agent.get('tier', '?')
                lines.append(f"  • {name} (T{tier}, {status})")
            
            if len(active_agents) > 5:
                lines.append(f"  ... and {len(active_agents) - 5} more")
        
        # Tier distribution
        tier_dist = agent_data.get('tier_distribution', {})
        if tier_dist:
            lines.append("\nTier distribution:")
            for tier in sorted(tier_dist.keys()):
                count = tier_dist[tier]
                lines.append(f"  Tier {tier}: {count} agents")
        
        return '\n'.join(lines)
    
    def get_agent_details(self) -> Dict[str, Any]:
        """Get detailed agent information"""
        return self._get_agent_data()
    
    def get_active_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of active agents with full details"""
        agent_data = self._get_agent_data()
        return agent_data.get('active_agents', [])
    
    def is_agent_active(self, agent_name: str) -> bool:
        """Check if a specific agent is active"""
        active_agents = self.get_active_agent_list()
        return any(agent.get('name') == agent_name for agent in active_agents)
    
    def get_agent_status(self, agent_name: str) -> Optional[str]:
        """Get status of a specific agent"""
        active_agents = self.get_active_agent_list()
        for agent in active_agents:
            if agent.get('name') == agent_name:
                return agent.get('status', 'unknown')
        return None
    
    def refresh_agent_data(self):
        """Force refresh of agent data"""
        self._agent_cache.clear()
        self._last_agent_check = 0
        self.clear_cache()
    
    def get_agent_registry_info(self) -> Dict[str, Any]:
        """Get information about the agent registry"""
        registry_data = self._load_agent_registry()
        if not registry_data:
            return {'error': 'No agent registry found'}
        
        agents = registry_data.get('agents', [])
        
        info = {
            'total_agents': len(agents),
            'registry_paths': self.agent_registry_paths,
            'tier_distribution': self._calculate_tier_distribution(agents),
            'agent_types': {},
            'last_updated': registry_data.get('last_updated', 'Unknown')
        }
        
        # Count agent types
        for agent in agents:
            agent_type = agent.get('type', 'unknown')
            info['agent_types'][agent_type] = info['agent_types'].get(agent_type, 0) + 1
        
        return info
    
    def export_agent_status(self) -> Dict[str, Any]:
        """Export current agent status for external use"""
        agent_data = self._get_agent_data()
        
        return {
            'timestamp': time.time(),
            'agent_data': agent_data,
            'config': self.config,
            'registry_info': self.get_agent_registry_info()
        }