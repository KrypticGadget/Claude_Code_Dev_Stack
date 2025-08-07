#!/usr/bin/env python3
"""Enhanced agent orchestrator for integrated Claude Code Dev Stack with MCP support"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

class AgentOrchestrator:
    def __init__(self):
        # Agent capabilities including MCP integration
        self.agent_capabilities = {
            "master-orchestrator": {
                "keywords": ["project", "orchestrate", "coordinate", "manage"],
                "capabilities": ["project-init", "coordination", "planning"],
                "mcp_services": []
            },
            "prompt-engineer": {
                "keywords": ["prompt", "optimize", "enhance", "improve"],
                "capabilities": ["prompt-optimization", "context-enhancement"],
                "mcp_services": []
            },
            "business-analyst": {
                "keywords": ["business", "market", "roi", "revenue", "cost"],
                "capabilities": ["market-analysis", "business-case", "roi-calculation"],
                "mcp_services": ["web-search"]
            },
            "technical-cto": {
                "keywords": ["technical", "architecture", "scalability", "infrastructure"],
                "capabilities": ["tech-assessment", "architecture-design", "scalability"],
                "mcp_services": ["web-search"]
            },
            "ceo-strategy": {
                "keywords": ["strategy", "vision", "positioning", "competitive"],
                "capabilities": ["strategic-planning", "market-positioning"],
                "mcp_services": ["web-search"]
            },
            "financial-analyst": {
                "keywords": ["financial", "budget", "cost", "profit", "revenue"],
                "capabilities": ["financial-modeling", "cost-analysis"],
                "mcp_services": []
            },
            "frontend-mockup": {
                "keywords": ["mockup", "prototype", "wireframe", "ui design"],
                "capabilities": ["html-css-mockup", "interactive-prototype"],
                "mcp_services": ["playwright"]
            },
            "frontend-architecture": {
                "keywords": ["frontend", "react", "vue", "angular", "component"],
                "capabilities": ["frontend-design", "component-architecture"],
                "mcp_services": ["playwright"]
            },
            "production-frontend": {
                "keywords": ["production frontend", "deploy frontend", "optimize frontend"],
                "capabilities": ["production-build", "optimization"],
                "mcp_services": ["playwright"]
            },
            "backend-services": {
                "keywords": ["backend", "api", "server", "endpoint", "service"],
                "capabilities": ["api-development", "server-architecture"],
                "mcp_services": ["web-search"]
            },
            "database-architecture": {
                "keywords": ["database", "schema", "query", "sql", "nosql"],
                "capabilities": ["schema-design", "query-optimization"],
                "mcp_services": ["obsidian"]
            },
            "api-integration-specialist": {
                "keywords": ["integration", "webhook", "third-party", "external api"],
                "capabilities": ["api-integration", "webhook-setup"],
                "mcp_services": ["web-search", "playwright"]
            },
            "middleware-specialist": {
                "keywords": ["middleware", "message queue", "event bus", "kafka"],
                "capabilities": ["middleware-design", "event-architecture"],
                "mcp_services": []
            },
            "testing-automation": {
                "keywords": ["test", "testing", "qa", "automation", "coverage"],
                "capabilities": ["test-generation", "automation-setup"],
                "mcp_services": ["playwright"]
            },
            "security-architecture": {
                "keywords": ["security", "authentication", "authorization", "encryption"],
                "capabilities": ["security-assessment", "auth-implementation"],
                "mcp_services": ["web-search"]
            },
            "performance-optimization": {
                "keywords": ["performance", "optimization", "speed", "latency"],
                "capabilities": ["performance-analysis", "optimization"],
                "mcp_services": ["playwright"]
            },
            "devops-engineering": {
                "keywords": ["deploy", "ci/cd", "docker", "kubernetes", "pipeline"],
                "capabilities": ["deployment-setup", "pipeline-creation"],
                "mcp_services": ["obsidian"]
            },
            "technical-documentation": {
                "keywords": ["documentation", "docs", "readme", "guide"],
                "capabilities": ["doc-generation", "api-docs"],
                "mcp_services": ["obsidian"]
            },
            "quality-assurance": {
                "keywords": ["quality", "review", "standards", "best practices"],
                "capabilities": ["code-review", "quality-gates"],
                "mcp_services": []
            },
            "mobile-development": {
                "keywords": ["mobile", "ios", "android", "react native", "flutter"],
                "capabilities": ["mobile-app", "cross-platform"],
                "mcp_services": []
            },
            "ui-ux-design": {
                "keywords": ["design", "ux", "user experience", "interface"],
                "capabilities": ["ui-design", "ux-optimization"],
                "mcp_services": ["playwright"]
            },
            "script-automation": {
                "keywords": ["script", "automate", "bash", "powershell"],
                "capabilities": ["script-generation", "automation"],
                "mcp_services": []
            },
            "integration-setup": {
                "keywords": ["setup", "install", "configure", "environment"],
                "capabilities": ["environment-setup", "dependency-management"],
                "mcp_services": []
            },
            "development-prompt": {
                "keywords": ["development", "workflow", "process"],
                "capabilities": ["workflow-design", "process-optimization"],
                "mcp_services": []
            },
            "project-manager": {
                "keywords": ["timeline", "milestone", "sprint", "deadline"],
                "capabilities": ["project-planning", "timeline-management"],
                "mcp_services": ["obsidian"]
            },
            "technical-specifications": {
                "keywords": ["specification", "requirements", "spec", "technical requirements"],
                "capabilities": ["spec-writing", "requirements-analysis"],
                "mcp_services": ["obsidian"]
            },
            "business-tech-alignment": {
                "keywords": ["alignment", "business value", "roi impact"],
                "capabilities": ["alignment-analysis", "value-assessment"],
                "mcp_services": []
            },
            "usage-guide-agent": {
                "keywords": ["guide", "tutorial", "how-to", "instructions"],
                "capabilities": ["guide-creation", "tutorial-writing"],
                "mcp_services": ["obsidian"]
            }
        }
        
        self.log_dir = Path.home() / ".claude" / "logs"
        self.state_dir = Path.home() / ".claude" / "state"
    
    def extract_explicit_mentions(self, prompt):
        """Extract explicit @agent- mentions from prompt"""
        pattern = r'@agent-([a-z-]+)(?:\[(opus|haiku)\])?'
        mentions = []
        for match in re.finditer(pattern, prompt):
            mentions.append({
                "agent": match.group(1),
                "model": match.group(2) or "default",
                "explicit": True
            })
        return mentions
    
    def analyze_prompt_keywords(self, prompt):
        """Analyze prompt for keyword matches to agents"""
        prompt_lower = prompt.lower()
        relevant_agents = []
        scores = {}
        
        for agent, info in self.agent_capabilities.items():
            score = 0
            for keyword in info["keywords"]:
                if keyword in prompt_lower:
                    score += 1
            
            if score > 0:
                relevant_agents.append({
                    "agent": agent,
                    "model": "default",
                    "explicit": False,
                    "score": score
                })
                scores[agent] = score
        
        # Sort by score
        relevant_agents.sort(key=lambda a: a.get("score", 0), reverse=True)
        return relevant_agents[:3]  # Top 3 agents
    
    def determine_mcp_services(self, agents):
        """Determine required MCP services for agents"""
        required_mcps = set()
        
        for agent_info in agents:
            agent_name = agent_info["agent"]
            if agent_name in self.agent_capabilities:
                mcps = self.agent_capabilities[agent_name].get("mcp_services", [])
                required_mcps.update(mcps)
        
        return list(required_mcps)
    
    def create_orchestration_plan(self, agents, mcps, task_description):
        """Create detailed orchestration plan"""
        plan = {
            "task": task_description,
            "agents": agents,
            "mcp_services": mcps,
            "execution_strategy": self.determine_execution_strategy(agents),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save plan to state
        self.save_orchestration_plan(plan)
        
        # Generate human-readable plan
        readable_plan = self.format_plan_for_output(plan)
        
        return readable_plan
    
    def determine_execution_strategy(self, agents):
        """Determine if agents can run in parallel or need sequencing"""
        # Define agent dependencies
        dependencies = {
            "frontend-mockup": ["ui-ux-design"],
            "production-frontend": ["frontend-mockup", "frontend-architecture"],
            "backend-services": ["database-architecture"],
            "testing-automation": ["frontend-architecture", "backend-services"],
            "deployment-setup": ["backend-services", "production-frontend"],
            "technical-documentation": ["*"]  # Runs after everything
        }
        
        strategy = {
            "parallel_groups": [],
            "sequential": []
        }
        
        agent_names = [a["agent"] for a in agents]
        
        # Group agents that can run in parallel
        parallel_group = []
        sequential = []
        
        for agent in agent_names:
            deps = dependencies.get(agent, [])
            if deps == ["*"] or any(dep in agent_names for dep in deps):
                sequential.append(agent)
            else:
                parallel_group.append(agent)
        
        if parallel_group:
            strategy["parallel_groups"].append(parallel_group)
        strategy["sequential"] = sequential
        
        return strategy
    
    def format_plan_for_output(self, plan):
        """Format orchestration plan for human readability"""
        output = "# Agent Orchestration Plan\n\n"
        
        output += f"**Task**: {plan['task']}\n"
        output += f"**Timestamp**: {plan['timestamp']}\n\n"
        
        # Agents section
        output += "## Agents to Invoke\n"
        for agent_info in plan['agents']:
            agent = agent_info['agent']
            model = agent_info.get('model', 'default')
            explicit = agent_info.get('explicit', False)
            
            if explicit:
                output += f"- **@agent-{agent}**[{model}] (explicitly requested)\n"
            else:
                score = agent_info.get('score', 0)
                output += f"- **@agent-{agent}** (keyword match, score: {score})\n"
            
            # Add capabilities
            if agent in self.agent_capabilities:
                caps = self.agent_capabilities[agent]['capabilities']
                output += f"  - Capabilities: {', '.join(caps)}\n"
        
        # MCP Services section
        if plan['mcp_services']:
            output += "\n## Required MCP Services\n"
            for mcp in plan['mcp_services']:
                output += f"- **{mcp}**\n"
                if mcp == "playwright":
                    output += "  - For: Browser automation, testing, visual validation\n"
                elif mcp == "obsidian":
                    output += "  - For: Documentation, note storage, knowledge management\n"
                elif mcp == "web-search":
                    output += "  - For: Research, competitive analysis, information gathering\n"
        
        # Execution strategy
        output += "\n## Execution Strategy\n"
        strategy = plan['execution_strategy']
        
        if strategy['parallel_groups']:
            output += "### Parallel Execution\n"
            for group in strategy['parallel_groups']:
                output += f"- Group: {', '.join(group)}\n"
        
        if strategy['sequential']:
            output += "### Sequential Execution\n"
            for agent in strategy['sequential']:
                output += f"- {agent}\n"
        
        # Integration points
        output += "\n## Integration Points\n"
        output += "- Session state will be preserved between agent calls\n"
        output += "- Results will be aggregated and formatted\n"
        output += "- Quality gates will validate outputs\n"
        
        return output
    
    def save_orchestration_plan(self, plan):
        """Save orchestration plan to state"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            plan_file = self.state_dir / "orchestration_plan.json"
            
            # Load existing plans
            existing_plans = []
            if plan_file.exists():
                with open(plan_file) as f:
                    existing_plans = json.load(f)
            
            # Add new plan
            existing_plans.append(plan)
            
            # Keep last 10 plans
            existing_plans = existing_plans[-10:]
            
            # Save
            with open(plan_file, 'w') as f:
                json.dump(existing_plans, f, indent=2)
        except:
            pass
    
    def log_orchestration(self, data):
        """Log orchestration events"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self.log_dir / "orchestration.jsonl"
            
            with open(log_file, 'a') as f:
                data["timestamp"] = datetime.now().isoformat()
                f.write(json.dumps(data) + "\n")
        except:
            pass

def main():
    """Main execution"""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Only process Task tool calls
        if tool_name != "Task":
            sys.exit(0)
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator()
        
        # Get task description
        task_description = tool_input.get("description", "")
        prompt = tool_input.get("prompt", task_description)
        
        # Extract explicit mentions first
        explicit_agents = orchestrator.extract_explicit_mentions(prompt)
        
        # If no explicit mentions, analyze keywords
        if not explicit_agents:
            keyword_agents = orchestrator.analyze_prompt_keywords(prompt)
            agents = keyword_agents
        else:
            agents = explicit_agents
        
        # Determine required MCP services
        mcps = orchestrator.determine_mcp_services(agents)
        
        # Create orchestration plan
        plan_output = orchestrator.create_orchestration_plan(agents, mcps, task_description)
        
        # Log the orchestration
        orchestrator.log_orchestration({
            "task": task_description,
            "agents": [a["agent"] for a in agents],
            "mcps": mcps
        })
        
        # Output for Claude Code
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": plan_output
            }
        }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error in agent orchestrator: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()