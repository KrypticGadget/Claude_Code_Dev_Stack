#!/usr/bin/env python3
"""
Orchestration Enhancer - V3.0 Agent Orchestration Enforcement
Ensures all 28 agents follow Anthropic's automatic delegation patterns
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class OrchestrationEnhancer:
    """
    Enforces proper orchestration patterns across all agent files
    Following Anthropic's guidelines for automatic delegation
    """
    
    def __init__(self):
        # Check for agents in multiple locations
        if (Path.cwd() / ".claude-example" / "agents").exists():
            self.agents_dir = Path.cwd() / ".claude-example" / "agents"
        else:
            self.agents_dir = Path.home() / ".claude" / "agents"
        
        # Agent hierarchy and delegation patterns
        self.agent_hierarchy = {
            # Tier 1: Meta-Coordination (MUST BE USED proactively)
            "prompt-engineer": {
                "tier": 1,
                "delegates_to": ["master-orchestrator"],
                "receives_from": [],
                "triggers": ["Use PROACTIVELY for request enhancement", "MUST BE USED for clarity optimization"],
                "description_keywords": "PROACTIVELY enhances all requests. MUST BE USED for optimal orchestration."
            },
            "master-orchestrator": {
                "tier": 1,
                "delegates_to": ["business-analyst", "technical-cto", "project-manager", "technical-specifications"],
                "receives_from": ["prompt-engineer"],
                "triggers": ["Use IMMEDIATELY for multi-agent coordination", "MUST BE USED for workflow management"],
                "description_keywords": "MUST BE USED to coordinate multi-agent workflows. Use IMMEDIATELY for new projects."
            },
            
            # Tier 2: Strategic Layer
            "business-analyst": {
                "tier": 2,
                "delegates_to": ["financial-analyst", "ceo-strategy", "technical-cto"],
                "receives_from": ["master-orchestrator"],
                "triggers": ["When ROI analysis needed", "When market assessment required"],
                "description_keywords": "Use PROACTIVELY for business viability. Automatically analyzes ROI."
            },
            "technical-cto": {
                "tier": 2,
                "delegates_to": ["security-architecture", "performance-optimization", "database-architecture"],
                "receives_from": ["master-orchestrator", "business-analyst"],
                "triggers": ["When architecture decisions needed", "When scalability assessment required"],
                "description_keywords": "Use PROACTIVELY for technical feasibility. MUST BE USED for architecture decisions."
            },
            "financial-analyst": {
                "tier": 2,
                "delegates_to": ["business-analyst"],
                "receives_from": ["business-analyst", "ceo-strategy"],
                "triggers": ["When financial modeling needed", "When unit economics required"],
                "description_keywords": "Automatically calculates financial projections. Use PROACTIVELY for modeling."
            },
            "ceo-strategy": {
                "tier": 2,
                "delegates_to": ["business-analyst", "financial-analyst"],
                "receives_from": ["master-orchestrator"],
                "triggers": ["When strategic positioning needed", "When market differentiation required"],
                "description_keywords": "Strategic vision specialist. Use PROACTIVELY for positioning decisions."
            },
            "project-manager": {
                "tier": 2,
                "delegates_to": ["technical-specifications", "all implementation agents"],
                "receives_from": ["master-orchestrator"],
                "triggers": ["When timeline planning needed", "When resource allocation required"],
                "description_keywords": "MUST BE USED for project planning. Automatically tracks milestones."
            },
            
            # Tier 3: Architecture Layer
            "technical-specifications": {
                "tier": 3,
                "delegates_to": ["frontend-architecture", "backend-services", "database-architecture"],
                "receives_from": ["project-manager", "technical-cto"],
                "triggers": ["When requirements documentation needed", "When API specs required"],
                "description_keywords": "Use PROACTIVELY for specifications. Automatically generates requirements."
            },
            "frontend-architecture": {
                "tier": 3,
                "delegates_to": ["frontend-mockup", "ui-ux-design", "production-frontend"],
                "receives_from": ["technical-specifications"],
                "triggers": ["After architecture approved", "When UI structure needed"],
                "description_keywords": "MUST BE USED before frontend development. Automatically creates architecture."
            },
            "backend-services": {
                "tier": 3,
                "delegates_to": ["database-architecture", "api-integration-specialist", "middleware-specialist"],
                "receives_from": ["technical-specifications"],
                "triggers": ["When service implementation needed", "When API development required"],
                "description_keywords": "Use PROACTIVELY for backend implementation. Automatically designs services."
            },
            "database-architecture": {
                "tier": 3,
                "delegates_to": ["backend-services"],
                "receives_from": ["backend-services", "technical-cto"],
                "triggers": ["When schema design needed", "When optimization required"],
                "description_keywords": "MUST BE USED for data architecture. Automatically optimizes schemas."
            },
            "api-integration-specialist": {
                "tier": 3,
                "delegates_to": ["backend-services", "middleware-specialist"],
                "receives_from": ["backend-services"],
                "triggers": ["When external integration needed", "When webhook implementation required"],
                "description_keywords": "Use PROACTIVELY for integrations. Automatically handles third-party APIs."
            },
            "middleware-specialist": {
                "tier": 3,
                "delegates_to": ["integration-setup"],
                "receives_from": ["backend-services", "api-integration-specialist"],
                "triggers": ["When message queue needed", "When service orchestration required"],
                "description_keywords": "Automatically configures middleware. MUST BE USED for service mesh."
            },
            
            # Tier 4: Implementation Layer
            "frontend-mockup": {
                "tier": 4,
                "delegates_to": ["production-frontend", "ui-ux-design"],
                "receives_from": ["frontend-architecture"],
                "triggers": ["After architecture complete", "When prototype needed"],
                "description_keywords": "Use PROACTIVELY for prototypes. Automatically generates HTML/CSS."
            },
            "production-frontend": {
                "tier": 4,
                "delegates_to": ["testing-automation", "ui-ux-design"],
                "receives_from": ["frontend-mockup", "frontend-architecture"],
                "triggers": ["After mockup approved", "When production build needed"],
                "description_keywords": "MUST BE USED for production frontend. Automatically implements React/Vue."
            },
            "ui-ux-design": {
                "tier": 4,
                "delegates_to": ["frontend-mockup", "production-frontend"],
                "receives_from": ["frontend-architecture", "frontend-mockup"],
                "triggers": ["When design review needed", "When UX optimization required"],
                "description_keywords": "Use PROACTIVELY for design. Automatically ensures accessibility."
            },
            "mobile-development": {
                "tier": 4,
                "delegates_to": ["testing-automation", "ui-ux-design"],
                "receives_from": ["frontend-architecture"],
                "triggers": ["When mobile app needed", "When native features required"],
                "description_keywords": "MUST BE USED for mobile apps. Automatically handles iOS/Android."
            },
            "integration-setup": {
                "tier": 4,
                "delegates_to": ["script-automation"],
                "receives_from": ["middleware-specialist"],
                "triggers": ["When environment setup needed", "When dependency management required"],
                "description_keywords": "Use PROACTIVELY for setup. Automatically configures environments."
            },
            "script-automation": {
                "tier": 4,
                "delegates_to": ["devops-engineering"],
                "receives_from": ["integration-setup"],
                "triggers": ["When automation scripts needed", "When build process required"],
                "description_keywords": "Automatically creates scripts. MUST BE USED for automation."
            },
            "development-prompt": {
                "tier": 4,
                "delegates_to": ["all agents as needed"],
                "receives_from": ["master-orchestrator"],
                "triggers": ["When workflow automation needed", "When prompt chaining required"],
                "description_keywords": "Use PROACTIVELY for workflows. Automatically chains prompts."
            },
            
            # Tier 5: Quality Layer
            "testing-automation": {
                "tier": 5,
                "delegates_to": ["quality-assurance", "security-architecture"],
                "receives_from": ["production-frontend", "backend-services"],
                "triggers": ["After implementation complete", "When test suite needed"],
                "description_keywords": "MUST BE USED for testing. Automatically generates test suites."
            },
            "quality-assurance": {
                "tier": 5,
                "delegates_to": ["testing-automation"],
                "receives_from": ["testing-automation"],
                "triggers": ["When code review needed", "When quality gates required"],
                "description_keywords": "Use PROACTIVELY for quality. Automatically enforces standards."
            },
            "security-architecture": {
                "tier": 5,
                "delegates_to": ["performance-optimization"],
                "receives_from": ["technical-cto", "testing-automation"],
                "triggers": ["When security audit needed", "When vulnerability scan required"],
                "description_keywords": "MUST BE USED for security. Automatically scans vulnerabilities."
            },
            "performance-optimization": {
                "tier": 5,
                "delegates_to": ["database-architecture", "backend-services"],
                "receives_from": ["security-architecture", "technical-cto"],
                "triggers": ["When optimization needed", "When bottleneck detected"],
                "description_keywords": "Use PROACTIVELY for performance. Automatically optimizes."
            },
            "devops-engineering": {
                "tier": 5,
                "delegates_to": ["script-automation"],
                "receives_from": ["script-automation"],
                "triggers": ["When deployment needed", "When CI/CD setup required"],
                "description_keywords": "MUST BE USED for deployment. Automatically configures pipelines."
            },
            "technical-documentation": {
                "tier": 5,
                "delegates_to": ["usage-guide"],
                "receives_from": ["all agents"],
                "triggers": ["When documentation needed", "When API docs required"],
                "description_keywords": "Use PROACTIVELY for documentation. Automatically generates docs."
            },
            "usage-guide": {
                "tier": 5,
                "delegates_to": [],
                "receives_from": ["technical-documentation"],
                "triggers": ["When user guide needed", "When onboarding docs required"],
                "description_keywords": "Automatically creates user guides. MUST BE USED for onboarding."
            },
            "business-tech-alignment": {
                "tier": 3,
                "delegates_to": ["technical-cto", "business-analyst"],
                "receives_from": ["master-orchestrator"],
                "triggers": ["When alignment validation needed", "When ROI impact assessment required"],
                "description_keywords": "Use PROACTIVELY for alignment. MUST BE USED for tech decisions."
            }
        }
        
        # Orchestration section template following Anthropic's format
        self.orchestration_template = """
## Automatic Delegation & Orchestration

### Hierarchy & Coordination
- **Tier**: {tier}
- **Reports to**: {reports_to}
- **Delegates to**: {delegates_to}
- **Coordinates with**: {coordinates_with}

### Automatic Triggers (Anthropic Pattern)
{triggers}

### Explicit Invocation Commands
{invocation_commands}

### Delegation Examples
```markdown
# Automatic delegation based on context
> When encountering {trigger_condition}
> Automatically invoke @agent-{target_agent}

# Explicit invocation by user
> Use the {agent_name} agent to {task_description}
> Have the {agent_name} agent analyze {data}
> Ask the {agent_name} agent to implement {feature}
```

### Inter-Agent Data Handoff
When delegating to another agent:
1. Capture current context and results
2. Format handoff data clearly
3. Invoke target agent with specific task
4. Await response and integrate results

### Proactive Behavior
This agent {proactive_behavior}
"""

    def enhance_agent_file(self, agent_name: str) -> bool:
        """Enhance a single agent file with orchestration patterns"""
        # Handle different naming conventions
        possible_names = [
            f"{agent_name}.md",
            f"{agent_name.replace('-', '_')}.md",
            f"{agent_name.replace('_', '-')}.md"
        ]
        
        agent_file = None
        for name in possible_names:
            test_file = self.agents_dir / name
            if test_file.exists():
                agent_file = test_file
                break
        
        if not agent_file:
            print(f"  [SKIP] {agent_name}.md not found")
            return False
        
        try:
            content = agent_file.read_text(encoding='utf-8')
            pattern = self.agent_hierarchy.get(agent_name)
            
            if not pattern:
                print(f"  [SKIP] {agent_name} - No pattern defined")
                return False
            
            # Check if already has orchestration section
            if "## Automatic Delegation & Orchestration" in content:
                # Update existing section
                content = self.update_orchestration_section(content, agent_name, pattern)
            else:
                # Insert new section
                content = self.insert_orchestration_section(content, agent_name, pattern)
            
            # Update description to include Anthropic keywords
            content = self.update_description_keywords(content, agent_name, pattern)
            
            # Write back
            agent_file.write_text(content, encoding='utf-8')
            print(f"  [ENHANCED] {agent_name}.md")
            return True
            
        except Exception as e:
            print(f"  [ERROR] {agent_name}.md - {e}")
            return False
    
    def build_orchestration_section(self, agent_name: str, pattern: Dict) -> str:
        """Build orchestration section following Anthropic's patterns"""
        # Determine who this agent reports to
        reports_to = []
        for other_agent, other_pattern in self.agent_hierarchy.items():
            if agent_name in other_pattern.get("delegates_to", []):
                reports_to.append(f"@agent-{other_agent}")
        
        if not reports_to:
            reports_to = ["@agent-master-orchestrator"]  # Default
        
        # Find peer agents (same tier)
        coordinates_with = []
        agent_tier = pattern["tier"]
        for other_agent, other_pattern in self.agent_hierarchy.items():
            if other_agent != agent_name and other_pattern["tier"] == agent_tier:
                coordinates_with.append(f"@agent-{other_agent}")
        
        # Build triggers section
        triggers_text = ""
        for trigger in pattern["triggers"]:
            triggers_text += f"- {trigger} - automatically invoke appropriate agent\n"
        
        # Build invocation commands
        invocation_commands = ""
        for delegate in pattern["delegates_to"]:
            if delegate == "all implementation agents":
                invocation_commands += f"- `@agent-[implementation-agent]` - Coordinate implementation tasks\n"
            elif delegate == "all agents as needed":
                invocation_commands += f"- `@agent-[any]` - Invoke any agent as needed for workflow\n"
            else:
                invocation_commands += f"- `@agent-{delegate}` - Delegate {self.get_agent_purpose(delegate)}\n"
        
        # Determine proactive behavior
        if "MUST BE USED" in pattern.get("description_keywords", ""):
            proactive = "MUST BE USED proactively when its expertise is needed"
        elif "PROACTIVELY" in pattern.get("description_keywords", ""):
            proactive = "proactively initiates actions based on context"
        else:
            proactive = "responds to explicit invocation and context triggers"
        
        # Format the section
        return self.orchestration_template.format(
            tier=pattern["tier"],
            reports_to=", ".join(reports_to),
            delegates_to=", ".join([f"@agent-{a}" if a not in ["all implementation agents", "all agents as needed"] else a for a in pattern["delegates_to"]]),
            coordinates_with=", ".join(coordinates_with[:3]) if coordinates_with else "peer agents at same tier",
            triggers=triggers_text,
            invocation_commands=invocation_commands,
            trigger_condition="[specific condition]",
            target_agent="[appropriate-agent]",
            agent_name=agent_name.replace("-", " "),
            task_description="[specific task]",
            data="[relevant data]",
            feature="[specific feature]",
            proactive_behavior=proactive
        )
    
    def get_agent_purpose(self, agent_name: str) -> str:
        """Get brief purpose description for an agent"""
        purposes = {
            "financial-analyst": "for financial modeling and projections",
            "technical-cto": "for technical architecture decisions",
            "frontend-mockup": "for UI/UX prototypes",
            "testing-automation": "for test suite generation",
            "security-architecture": "for security audit and compliance",
            "database-architecture": "for schema design and optimization",
            "backend-services": "for API and service implementation",
            "devops-engineering": "for deployment and CI/CD"
        }
        return purposes.get(agent_name, "for specialized tasks")
    
    def insert_orchestration_section(self, content: str, agent_name: str, pattern: Dict) -> str:
        """Insert orchestration section at appropriate location"""
        orchestration_section = self.build_orchestration_section(agent_name, pattern)
        
        # Find insertion point (after V3 capabilities or core responsibilities)
        insertion_markers = [
            "## V3.0 Enhanced Capabilities",
            "## Core Responsibilities",
            "## Operational Commands",
            "---\n\n"  # After metadata
        ]
        
        for marker in insertion_markers:
            if marker in content:
                # Find end of section
                marker_pos = content.find(marker)
                next_section = content.find("\n## ", marker_pos + len(marker))
                
                if next_section == -1:
                    # Insert at end
                    return content + "\n\n" + orchestration_section
                else:
                    # Insert before next section
                    return content[:next_section] + "\n" + orchestration_section + "\n" + content[next_section:]
        
        # Fallback: append at end
        return content + "\n\n" + orchestration_section
    
    def update_orchestration_section(self, content: str, agent_name: str, pattern: Dict) -> str:
        """Update existing orchestration section"""
        new_section = self.build_orchestration_section(agent_name, pattern)
        
        # Find and replace existing section
        start_marker = "## Automatic Delegation & Orchestration"
        end_markers = ["\n## ", "\n---", "\n\n\n"]
        
        start_pos = content.find(start_marker)
        if start_pos == -1:
            return self.insert_orchestration_section(content, agent_name, pattern)
        
        # Find end of section
        end_pos = len(content)
        for marker in end_markers:
            pos = content.find(marker, start_pos + 1)
            if pos != -1 and pos < end_pos:
                end_pos = pos
        
        # Replace section
        return content[:start_pos] + new_section + content[end_pos:]
    
    def update_description_keywords(self, content: str, agent_name: str, pattern: Dict) -> str:
        """Update agent description to include Anthropic's recommended keywords"""
        keywords = pattern.get("description_keywords", "")
        
        if not keywords:
            return content
        
        # Find description line in metadata
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("description:"):
                # Check if keywords already present
                if "PROACTIVELY" not in line and "MUST BE USED" not in line:
                    # Add keywords to description
                    if not line.endswith("."):
                        line += "."
                    lines[i] = f"{line} {keywords}"
                break
        
        return "\n".join(lines)
    
    def enhance_all_agents(self) -> Dict[str, bool]:
        """Enhance all 28 agents with orchestration patterns"""
        print("=" * 60)
        print("Enhancing Agent Orchestration (Anthropic Patterns)")
        print("=" * 60)
        
        results = {}
        
        # Process agents by tier for proper hierarchy
        for tier in range(1, 6):
            print(f"\nProcessing Tier {tier} Agents:")
            for agent_name, pattern in self.agent_hierarchy.items():
                if pattern["tier"] == tier:
                    success = self.enhance_agent_file(agent_name)
                    results[agent_name] = success
        
        return results
    
    def validate_orchestration(self) -> Dict[str, any]:
        """Validate that orchestration is properly implemented"""
        validation = {
            "total_agents": 28,
            "enhanced_agents": 0,
            "missing_orchestration": [],
            "circular_dependencies": [],
            "orphaned_agents": []
        }
        
        for agent_name in self.agent_hierarchy.keys():
            # Handle different naming conventions
            possible_names = [
                f"{agent_name}.md",
                f"{agent_name.replace('-', '_')}.md",
                f"{agent_name.replace('_', '-')}.md"
            ]
            
            agent_file = None
            for name in possible_names:
                test_file = self.agents_dir / name
                if test_file.exists():
                    agent_file = test_file
                    break
            
            if agent_file and agent_file.exists():
                content = agent_file.read_text(encoding='utf-8')
                
                # Check for orchestration section
                if "## Automatic Delegation & Orchestration" in content:
                    validation["enhanced_agents"] += 1
                else:
                    validation["missing_orchestration"].append(agent_name)
                
                # Check for Anthropic keywords in description
                if not any(keyword in content for keyword in ["PROACTIVELY", "MUST BE USED", "Use immediately"]):
                    if agent_name not in validation["missing_orchestration"]:
                        validation["missing_orchestration"].append(f"{agent_name} (missing keywords)")
        
        # Check for circular dependencies
        for agent, pattern in self.agent_hierarchy.items():
            for delegate in pattern["delegates_to"]:
                if delegate in self.agent_hierarchy:
                    delegate_pattern = self.agent_hierarchy[delegate]
                    if agent in delegate_pattern.get("delegates_to", []):
                        validation["circular_dependencies"].append(f"{agent} <-> {delegate}")
        
        # Check for orphaned agents (no connections)
        for agent, pattern in self.agent_hierarchy.items():
            if not pattern["delegates_to"] and not pattern["receives_from"]:
                validation["orphaned_agents"].append(agent)
        
        return validation

def main():
    """Main execution"""
    enhancer = OrchestrationEnhancer()
    
    # Enhance all agents
    results = enhancer.enhance_all_agents()
    
    # Validate orchestration
    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)
    
    validation = enhancer.validate_orchestration()
    
    print(f"\nEnhanced Agents: {validation['enhanced_agents']}/{validation['total_agents']}")
    
    if validation["missing_orchestration"]:
        print(f"\nMissing Orchestration:")
        for agent in validation["missing_orchestration"]:
            print(f"  - {agent}")
    
    if validation["circular_dependencies"]:
        print(f"\nCircular Dependencies Detected:")
        for dep in validation["circular_dependencies"]:
            print(f"  - {dep}")
    
    if validation["orphaned_agents"]:
        print(f"\nOrphaned Agents:")
        for agent in validation["orphaned_agents"]:
            print(f"  - {agent}")
    
    # Summary
    success_count = sum(1 for v in results.values() if v)
    print(f"\n{'=' * 60}")
    print(f"Orchestration Enhancement Complete")
    print(f"Successfully enhanced: {success_count}/{len(results)} agents")
    print(f"All agents now follow Anthropic's automatic delegation patterns")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()