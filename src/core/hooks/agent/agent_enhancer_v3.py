#!/usr/bin/env python3
"""
Agent Enhancer V3.0 - Upgrades all agents with V3 capabilities
Adds context awareness, parallel execution, and smart coordination
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

class AgentEnhancerV3:
    """Enhances agents with V3 capabilities"""
    
    def __init__(self):
        self.agents_dir = Path.home() / ".claude" / "agents"
        self.enhancements = {
            "context_awareness": True,
            "parallel_execution": True,
            "smart_handoffs": True,
            "performance_tracking": True,
            "mcp_integration": True,
            "v3_orchestration": True
        }
        
        # V3 Enhancement template to append to agents
        self.v3_template = """

## V3.0 Enhanced Capabilities

### Context Awareness
- Real-time access to status line information
- Token usage monitoring and optimization
- Phase-aware execution strategies
- Git context integration
- Active agent coordination

### Parallel Execution
- Supports concurrent execution with related agents
- Non-blocking operations where applicable
- Shared context management
- Resource optimization

### Smart Handoffs
- Automatic documentation generation at transition points
- Context preservation between agents
- Intelligent next-agent suggestions
- Handoff metrics tracking

### Performance Tracking
- Execution time monitoring
- Success rate tracking
- Resource usage optimization
- Learning from execution patterns

### MCP Integration
When applicable, this agent integrates with:
- **Playwright**: For browser automation and testing
- **Web Search**: For real-time information gathering
- **Obsidian**: For knowledge management

### V3 Orchestration Compatibility
- Compatible with smart_orchestrator.py
- Supports context-based selection
- Priority-based execution
- Pattern matching optimization

### Status Line Integration
This agent reports to the status line:
- Current operation status
- Progress indicators
- Resource consumption
- Completion metrics

### Error Recovery
- Graceful error handling
- Automatic retry mechanisms
- Fallback strategies
- Error pattern learning
"""

    def enhance_agent(self, agent_file: Path) -> bool:
        """Enhance a single agent with V3 capabilities"""
        try:
            content = agent_file.read_text()
            
            # Check if already enhanced
            if "V3.0 Enhanced Capabilities" in content:
                print(f"  [SKIP] {agent_file.name} - Already enhanced")
                return True
            
            # Add V3 enhancements
            enhanced_content = content + self.v3_template
            
            # Add agent-specific enhancements
            agent_name = agent_file.stem
            specific_enhancements = self.get_specific_enhancements(agent_name)
            if specific_enhancements:
                enhanced_content += f"\n### Agent-Specific V3 Features\n{specific_enhancements}\n"
            
            # Write enhanced version
            agent_file.write_text(enhanced_content)
            print(f"  [ENHANCED] {agent_file.name}")
            return True
            
        except Exception as e:
            print(f"  [ERROR] {agent_file.name} - {e}")
            return False
    
    def get_specific_enhancements(self, agent_name: str) -> str:
        """Get agent-specific enhancements"""
        specific = {
            "master-orchestrator": """
- Central coordination hub for all V3 agents
- Real-time orchestration decisions
- Dynamic agent selection based on context
- Execution plan optimization
""",
            "prompt-engineer": """
- Context injection for enhanced prompts
- Token optimization strategies
- Phase-specific prompt templates
- Learning from successful patterns
""",
            "testing-automation": """
- Parallel test execution
- Smart test selection based on changes
- Performance benchmarking
- Coverage optimization
""",
            "backend-services": """
- Microservice orchestration
- API versioning awareness
- Database connection pooling
- Caching strategy implementation
""",
            "frontend-architecture": """
- Component hierarchy optimization
- State management patterns
- Performance budgeting
- Accessibility compliance tracking
""",
            "security-architecture": """
- Real-time vulnerability scanning
- Security gate integration
- Compliance verification
- Threat model updates
""",
            "devops-engineering": """
- Pipeline parallelization
- Resource optimization
- Deployment strategy selection
- Rollback automation
"""
        }
        return specific.get(agent_name, "")
    
    def enhance_all_agents(self) -> Dict[str, bool]:
        """Enhance all agents in the directory"""
        results = {}
        
        if not self.agents_dir.exists():
            print(f"Agents directory not found: {self.agents_dir}")
            return results
        
        agent_files = list(self.agents_dir.glob("*.md"))
        print(f"Found {len(agent_files)} agents to enhance")
        
        for agent_file in agent_files:
            results[agent_file.name] = self.enhance_agent(agent_file)
        
        return results
    
    def create_agent_registry(self):
        """Create a V3 agent registry with metadata"""
        registry = {
            "version": "3.0",
            "agents": {},
            "categories": {
                "analysis": [],
                "design": [],
                "implementation": [],
                "quality": [],
                "management": [],
                "setup": []
            }
        }
        
        # Map agents to categories
        category_mappings = {
            "analysis": ["business-analyst", "technical-cto", "financial-analyst", "ceo-strategy"],
            "design": ["ui-ux-design", "frontend-architecture", "database-architecture"],
            "implementation": ["backend-services", "production-frontend", "mobile-development"],
            "quality": ["testing-automation", "security-architecture", "performance-optimization"],
            "management": ["project-manager", "prompt-engineer", "technical-documentation"],
            "setup": ["integration-setup", "script-automation", "devops-engineering"]
        }
        
        for category, agents in category_mappings.items():
            registry["categories"][category] = agents
        
        # Add agent metadata
        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            registry["agents"][agent_name] = {
                "file": agent_file.name,
                "v3_enhanced": "V3.0 Enhanced Capabilities" in agent_file.read_text(),
                "category": self.get_agent_category(agent_name, category_mappings),
                "priority": self.get_agent_priority(agent_name)
            }
        
        # Save registry
        registry_file = self.agents_dir / "v3_agent_registry.json"
        registry_file.write_text(json.dumps(registry, indent=2))
        
        return registry
    
    def get_agent_category(self, agent_name: str, mappings: Dict) -> str:
        """Get category for an agent"""
        for category, agents in mappings.items():
            if agent_name in agents:
                return category
        return "general"
    
    def get_agent_priority(self, agent_name: str) -> int:
        """Get priority for an agent"""
        priorities = {
            "prompt-engineer": 1,
            "master-orchestrator": 2,
            "business-analyst": 3,
            "technical-cto": 3,
            "project-manager": 3,
            "technical-specifications": 4,
            "frontend-architecture": 5,
            "backend-services": 6,
            "testing-automation": 7,
            "security-architecture": 8,
            "devops-engineering": 9
        }
        return priorities.get(agent_name, 10)

def main():
    """Main enhancement process"""
    print("=" * 60)
    print("Agent Enhancement V3.0")
    print("=" * 60)
    
    enhancer = AgentEnhancerV3()
    
    # Enhance all agents
    print("\nEnhancing agents...")
    results = enhancer.enhance_all_agents()
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nEnhancement complete: {successful}/{total} agents enhanced")
    
    # Create registry
    print("\nCreating V3 agent registry...")
    registry = enhancer.create_agent_registry()
    print(f"Registry created with {len(registry['agents'])} agents")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())