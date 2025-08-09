#!/usr/bin/env python3
"""Routes slash commands to appropriate agents and workflows"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

COMMAND_MAPPINGS = {
    "/new-project": {
        "agents": ["prompt-engineer", "master-orchestrator", "business-analyst", "technical-cto"],
        "mcps": ["web-search"],
        "description": "Initialize new project with full analysis"
    },
    "/resume-project": {
        "agents": ["master-orchestrator"],
        "mcps": [],
        "description": "Continue existing project from saved state"
    },
    "/business-analysis": {
        "agents": ["business-analyst", "financial-analyst", "ceo-strategy"],
        "mcps": ["web-search"],
        "description": "Comprehensive business and market analysis"
    },
    "/technical-feasibility": {
        "agents": ["technical-cto", "security-architecture", "performance-optimization"],
        "mcps": ["web-search"],
        "description": "Technical viability and architecture assessment"
    },
    "/architecture-design": {
        "agents": ["technical-specifications", "database-architecture", "api-integration-specialist"],
        "mcps": ["obsidian"],
        "description": "System architecture and design documentation"
    },
    "/database-design": {
        "agents": ["database-architecture", "backend-services"],
        "mcps": ["obsidian"],
        "description": "Database schema and optimization"
    },
    "/api-design": {
        "agents": ["api-integration-specialist", "backend-services", "technical-documentation"],
        "mcps": ["obsidian"],
        "description": "API specification and documentation"
    },
    "/frontend-mockup": {
        "agents": ["frontend-mockup", "ui-ux-design", "frontend-architecture"],
        "mcps": ["playwright"],
        "description": "HTML/CSS mockup with interactive preview"
    },
    "/backend-implementation": {
        "agents": ["backend-services", "api-integration-specialist", "middleware-specialist"],
        "mcps": [],
        "description": "Backend service implementation"
    },
    "/full-stack-app": {
        "agents": ["prompt-engineer", "master-orchestrator", "frontend-architecture", "backend-services", "database-architecture", "api-integration-specialist"],
        "mcps": ["playwright", "obsidian"],
        "description": "Complete full-stack application"
    },
    "/test-suite": {
        "agents": ["testing-automation", "quality-assurance"],
        "mcps": ["playwright"],
        "description": "Comprehensive test suite generation"
    },
    "/code-review": {
        "agents": ["quality-assurance", "security-architecture", "performance-optimization"],
        "mcps": [],
        "description": "Code quality and security review"
    },
    "/deployment-setup": {
        "agents": ["devops-engineering", "script-automation", "security-architecture"],
        "mcps": ["obsidian"],
        "description": "Deployment configuration and CI/CD"
    },
    "/docker-setup": {
        "agents": ["devops-engineering", "script-automation"],
        "mcps": ["obsidian"],
        "description": "Docker containerization setup"
    },
    "/documentation": {
        "agents": ["technical-documentation", "usage-guide-agent"],
        "mcps": ["obsidian"],
        "description": "Generate comprehensive documentation"
    },
    "/prompt-enhance": {
        "agents": ["prompt-engineer", "development-prompt"],
        "mcps": [],
        "description": "Optimize and enhance prompts"
    },
    "/security-audit": {
        "agents": ["security-architecture", "quality-assurance"],
        "mcps": ["web-search"],
        "description": "Security vulnerability assessment"
    },
    "/performance-optimization": {
        "agents": ["performance-optimization", "database-architecture", "backend-services"],
        "mcps": ["playwright"],
        "description": "Performance analysis and optimization"
    },
    "/auto-enhance": {
        "agents": ["prompt-engineer", "master-orchestrator"],
        "mcps": [],
        "description": "Auto-enhance prompt then orchestrate execution"
    },
    "/quick-app": {
        "agents": ["prompt-engineer", "master-orchestrator", "frontend-mockup", "backend-services"],
        "mcps": [],
        "description": "Quick app with auto-enhancement"
    },
    "/smart-build": {
        "agents": ["prompt-engineer", "master-orchestrator", "usage-guide-agent"],
        "mcps": ["web-search"],
        "description": "Smart build with best practices research"
    },
    # MCP-specific commands
    "/mcp-search": {
        "agents": ["master-orchestrator"],
        "mcps": ["web-search"],
        "description": "Intelligent web search via MCP"
    },
    "/mcp-obsidian": {
        "agents": ["technical-documentation"],
        "mcps": ["obsidian"],
        "description": "Note and documentation management via Obsidian"
    },
    "/mcp-playwright": {
        "agents": ["testing-automation"],
        "mcps": ["playwright"],
        "description": "Browser automation and testing via Playwright"
    },
    "/mcp-status": {
        "agents": [],
        "mcps": ["web-search", "obsidian", "playwright"],
        "description": "Check status of all MCP services"
    }
}

def parse_slash_command(prompt):
    """Extract slash command and parameters from prompt"""
    match = re.match(r'^(/\w+[-\w]*)\s*(.*)', prompt)
    if match:
        command = match.group(1)
        params = match.group(2)
        return command, params
    return None, None

def route_to_agents(command, params):
    """Route command to appropriate agents and services with proper hierarchy"""
    if command not in COMMAND_MAPPINGS:
        return None
    
    mapping = COMMAND_MAPPINGS[command]
    agents = mapping["agents"]
    mcps = mapping["mcps"]
    description = mapping["description"]
    
    # Build execution context
    context = f"# Executing: {command}\n"
    context += f"Description: {description}\n"
    context += f"Parameters: {params}\n\n"
    
    # Special handling for MCP status command
    if command == "/mcp-status":
        context += "## MCP Service Status Check:\n\n"
        context += "Checking status of all MCP services:\n"
        for mcp in mcps:
            context += f"- {mcp}: Checking connection and capabilities\n"
        context += "\nUse appropriate MCP tools to verify service health.\n"
        return context
    
    # Add hierarchical agent invocations
    context += "## Agent Execution Hierarchy:\n\n"
    
    # ENFORCED HIERARCHY: Always go through proper chain
    # Phase 1: Prompt Enhancement (if not already enhanced)
    if "prompt-engineer" in agents:
        context += "### Phase 1: Prompt Enhancement\n"
        context += f"@agent-prompt-engineer enhance and structure: {params}\n"
        context += "Output: Enhanced prompt for orchestration\n\n"
    
    # Phase 2: Master Orchestration (REQUIRED for multi-agent workflows)
    if "master-orchestrator" in agents or len(agents) > 2:
        context += "### Phase 2: Master Orchestration\n"
        if "prompt-engineer" in agents:
            context += "@agent-master-orchestrator coordinate execution with ENHANCED prompt from Phase 1\n"
        else:
            context += f"@agent-master-orchestrator coordinate execution: {params}\n"
        context += "Responsibilities:\n"
        context += "- Delegate to type leaders\n"
        context += "- Coordinate parallel execution\n"
        context += "- Manage dependencies\n"
        context += "- Aggregate results\n\n"
    
    # Phase 3: Type Leader Coordination
    remaining = [a for a in agents if a not in ["prompt-engineer", "master-orchestrator"]]
    if remaining:
        context += "### Phase 3: Type Leader Coordination\n\n"
        
        # Group by type with leaders
        frontend = [a for a in remaining if a in ["frontend-architecture", "frontend-mockup", "production-frontend", "ui-ux-design"]]
        backend = [a for a in remaining if a in ["backend-services", "database-architecture", "api-integration-specialist", "middleware-specialist"]]
        quality = [a for a in remaining if a in ["testing-automation", "quality-assurance", "security-architecture", "performance-optimization"]]
        business = [a for a in remaining if a in ["business-analyst", "financial-analyst", "ceo-strategy", "technical-cto"]]
        devops = [a for a in remaining if a in ["devops-engineering", "script-automation", "integration-setup"]]
        other = [a for a in remaining if a not in frontend + backend + quality + business + devops]
        
        if frontend:
            context += "**Frontend Team (Lead: frontend-architecture):**\n"
            context += "  Leader: @agent-frontend-architecture (coordinates UI/UX work)\n"
            context += "  Members: " + " ".join(f"@agent-{a}" for a in frontend if a != "frontend-architecture") + "\n\n"
        
        if backend:
            context += "**Backend Team (Lead: backend-services):**\n"
            context += "  Leader: @agent-backend-services (coordinates API/DB work)\n"
            context += "  Members: " + " ".join(f"@agent-{a}" for a in backend if a != "backend-services") + "\n\n"
        
        if quality:
            context += "**Quality Team (Lead: quality-assurance):**\n"
            context += "  Leader: @agent-quality-assurance (coordinates testing/security)\n"
            context += "  Members: " + " ".join(f"@agent-{a}" for a in quality if a != "quality-assurance") + "\n\n"
        
        if business:
            context += "**Business Team (Lead: business-analyst):**\n"
            context += "  Leader: @agent-business-analyst (coordinates strategy/analysis)\n"
            context += "  Members: " + " ".join(f"@agent-{a}" for a in business if a != "business-analyst") + "\n\n"
        
        if devops:
            context += "**DevOps Team (Lead: devops-engineering):**\n"
            context += "  Leader: @agent-devops-engineering (coordinates deployment/automation)\n"
            context += "  Members: " + " ".join(f"@agent-{a}" for a in devops if a != "devops-engineering") + "\n\n"
        
        if other:
            context += "**Support Team:** " + " ".join(f"@agent-{a}" for a in other) + "\n\n"
    
    # Add MCP services if needed
    if mcps:
        context += "\n## MCP services required:\n"
        for mcp in mcps:
            context += f"- {mcp}\n"
    
    # Add execution plan with hierarchy emphasis
    context += "\n## Execution Plan (HIERARCHICAL):\n"
    context += "1. Prompt Enhancement (if applicable)\n"
    context += "2. Master Orchestration (delegates to teams)\n"
    context += "3. Type Leaders coordinate their teams\n"
    context += "4. Teams execute in parallel where possible\n"
    context += "5. Results aggregated by type leaders\n"
    context += "6. Master orchestrator compiles final output\n"
    context += "\n**IMPORTANT**: Follow the hierarchy! Don't skip orchestration levels.\n"
    
    # Log the routing
    log_routing(command, agents, mcps, params)
    
    return context

def log_routing(command, agents, mcps, params):
    """Log command routing for audit and optimization"""
    log_dir = Path.home() / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "agents": agents,
        "mcps": mcps,
        "params": params
    }
    
    log_file = log_dir / "slash_commands.jsonl"
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass

def main():
    """Main execution"""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")
        
        # Parse command
        command, params = parse_slash_command(prompt)
        
        if command:
            # Route to agents
            routing_context = route_to_agents(command, params)
            
            if routing_context:
                # Output routing information
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": routing_context
                    }
                }
                print(json.dumps(output))
                sys.exit(0)
        
        # No slash command found or not recognized
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block execution
        print(f"Error in slash command router: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()