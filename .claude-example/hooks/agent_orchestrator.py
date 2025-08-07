#!/usr/bin/env python3
"""Enhanced agent orchestrator for integrated Claude Code Dev Stack"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

class AgentOrchestrator:
    def __init__(self):
        self.agent_keywords = {
    "system-architect": ["architecture", "system design", "scalability", "infrastructure"],
    "backend-services": ["api", "backend", "server", "endpoint", "database connection"],
    "frontend-architecture": ["ui", "frontend", "react", "vue", "user interface"],
    "database-architecture": ["schema", "database", "table", "query", "index"],
    "security-architecture": ["security", "authentication", "authorization", "encryption"],
    "devops-engineering": ["deploy", "ci/cd", "pipeline", "docker", "kubernetes"],
    "testing-automation": ["test", "qa", "quality", "coverage", "validation"],
    "business-analyst": ["roi", "business case", "market", "competitor"],
    "api-integration-specialist": ["integration", "webhook", "third-party", "external api"],
    "performance-optimization": ["performance", "optimization", "speed", "latency"],
    "technical-documentation": ["documentation", "readme", "guide", "manual"]
}

def extract_explicit_mentions(prompt):
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

def analyze_prompt(prompt):
    """Analyze prompt to determine relevant agents"""
    prompt_lower = prompt.lower()
    
    # First check for explicit @agent- mentions
    explicit_mentions = extract_explicit_mentions(prompt)
    if explicit_mentions:
        return explicit_mentions
    
    # Otherwise do keyword analysis
    relevant_agents = []
    confidence_scores = {}
    
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in prompt_lower)
        if score > 0:
            relevant_agents.append({
                "agent": agent,
                "model": "default",
                "explicit": False,
                "score": score
            })
            confidence_scores[agent] = score
    
    # Sort by confidence
    relevant_agents.sort(key=lambda a: a.get("score", 0), reverse=True)
    
    return relevant_agents[:3]  # Top 3 agents

def create_routing_suggestion(prompt, agents):
    """Create agent routing suggestion"""
    routing_data = {
        "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "timestamp": datetime.now().isoformat(),
        "suggested_agents": agents,
        "routing_confidence": "high" if agents and agents[0].get("explicit") else "medium"
    }
    
    # Save routing data
    routing_file = Path(".claude/state/agent_routing.json")
    routing_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing routings
    existing = []
    if routing_file.exists():
        with open(routing_file) as f:
            existing = json.load(f)
    
    # Add new routing (keep last 10)
    existing.append(routing_data)
    existing = existing[-10:]
    
    with open(routing_file, 'w') as f:
        json.dump(existing, f, indent=2)
    
    # Create visible suggestion if agents found
    if agents:
        with open("AGENT_SUGGESTION.md", 'w') as f:
            f.write(f"""# Agent Routing Suggestion

## Your Request
{prompt[:500]}...

## Suggested Agents
""")
            for i, agent in enumerate(agents):
                if agent.get("explicit"):
                    f.write(f"- **@agent-{agent['agent']}[{agent['model']}]** - Explicitly requested\n")
                else:
                    f.write(f"- **@agent-{agent['agent']}** - Keyword match (score: {agent.get('score', 0)})\n")
            
            f.write("""
## Quick Commands
- Use `@agent-{agents[0]['agent']}` to target specific agents
- Use `[opus]` or `[haiku]` to specify model
- Use `/new-project` to engage full orchestration

*Explicit @agent- mentions always take priority*
""")
        
        explicit_agents = [a for a in agents if a.get("explicit")]
        if explicit_agents:
            print(f"[ROUTING] Routing to explicit agents: {', '.join('@agent-' + a['agent'] for a in explicit_agents)}")
        else:
            print(f"[SUGGESTED] Suggested agents: {', '.join('@agent-' + a['agent'] for a in agents)}")

if __name__ == "__main__":
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")
        
        if prompt:
            agents = analyze_prompt(prompt)
            create_routing_suggestion(prompt, agents)
            
            # Output for Claude Code
            if agents:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": f"Suggested agents: {', '.join('@agent-' + a['agent'] for a in agents)}"
                    }
                }
                print(json.dumps(output))
        
        sys.exit(0)
    except Exception as e:
        print(f"Error in agent orchestrator: {e}", file=sys.stderr)
        sys.exit(1)