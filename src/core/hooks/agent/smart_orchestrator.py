#!/usr/bin/env python3
"""
Smart Orchestrator - V3.0 Context-Aware Agent Selection
Intelligently selects and coordinates agents based on context
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class SmartOrchestrator:
    """
    Context-aware orchestrator that intelligently selects agents
    based on user request, current context, and system state
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.config_file = self.home_dir / "orchestrator_config.json"
        self.history_file = self.home_dir / "orchestration_history.json"
        
        # Load agent definitions
        self.agents = self.load_agent_definitions()
        
        # Load orchestration patterns
        self.patterns = self.load_orchestration_patterns()
        
        # Context weights for agent selection
        self.CONTEXT_WEIGHTS = {
            "keyword_match": 0.35,
            "phase_alignment": 0.25,
            "recent_success": 0.20,
            "domain_expertise": 0.15,
            "dependency_chain": 0.05
        }
        
        # Agent categories for parallel execution
        self.AGENT_CATEGORIES = {
            "analysis": ["business-analyst", "technical-cto", "financial-analyst", "ceo-strategy", "business-tech-alignment"],
            "design": ["ui-ux-designer", "frontend-architecture", "database-architecture", "frontend-mockup", "technical-specifications"],
            "implementation": ["backend-services", "production-frontend", "mobile-developer", "middleware-specialist", "api-integration-specialist"],
            "quality": ["testing-automation", "security-architecture", "performance-optimization", "quality-assurance-lead"],
            "management": ["project-manager", "prompt-engineer", "technical-documentation", "master-orchestrator", "development-prompt"],
            "setup": ["integration-setup", "script-automation", "devops-engineer", "usage-guide-agent"]
        }
    
    def load_agent_definitions(self) -> Dict[str, Any]:
        """Load agent capabilities and metadata"""
        return {
            "prompt-engineer": {
                "keywords": ["enhance", "improve", "optimize", "clarify", "refine"],
                "domains": ["prompting", "context", "requirements"],
                "phases": ["exploration", "requirements"],
                "priority": 1
            },
            "master-orchestrator": {
                "keywords": ["orchestrate", "coordinate", "manage", "execute", "workflow"],
                "domains": ["coordination", "workflow", "management"],
                "phases": ["all"],
                "priority": 2
            },
            "business-analyst": {
                "keywords": ["roi", "market", "revenue", "cost", "profit", "viability"],
                "domains": ["business", "finance", "market"],
                "phases": ["exploration", "requirements"],
                "priority": 3
            },
            "technical-cto": {
                "keywords": ["feasibility", "scalability", "architecture", "tech stack"],
                "domains": ["technical", "architecture", "infrastructure"],
                "phases": ["design", "requirements"],
                "priority": 3
            },
            "ceo-strategy": {
                "keywords": ["strategy", "vision", "positioning", "differentiation"],
                "domains": ["strategy", "market", "positioning"],
                "phases": ["exploration"],
                "priority": 3
            },
            "financial-analyst": {
                "keywords": ["financial", "model", "economics", "burn", "runway"],
                "domains": ["finance", "modeling", "economics"],
                "phases": ["exploration", "requirements"],
                "priority": 3
            },
            "project-manager": {
                "keywords": ["timeline", "sprint", "milestone", "deadline", "resources"],
                "domains": ["project", "planning", "management"],
                "phases": ["all"],
                "priority": 3
            },
            "technical-specifications": {
                "keywords": ["requirements", "specifications", "api", "data model"],
                "domains": ["technical", "documentation", "specifications"],
                "phases": ["requirements", "design"],
                "priority": 4
            },
            "business-tech-alignment": {
                "keywords": ["alignment", "roi impact", "business value", "trade-offs"],
                "domains": ["business", "technical", "alignment"],
                "phases": ["requirements", "design"],
                "priority": 4
            },
            "technical-documentation": {
                "keywords": ["documentation", "readme", "guide", "manual", "reference"],
                "domains": ["documentation", "technical writing"],
                "phases": ["all"],
                "priority": 5
            },
            "api-integration-specialist": {
                "keywords": ["integration", "webhook", "third-party", "external api"],
                "domains": ["integration", "api", "services"],
                "phases": ["implementation", "design"],
                "priority": 5
            },
            "frontend-architecture": {
                "keywords": ["site map", "user flow", "navigation", "information architecture"],
                "domains": ["frontend", "architecture", "ux"],
                "phases": ["design"],
                "priority": 5
            },
            "frontend-mockup": {
                "keywords": ["mockup", "prototype", "wireframe", "html mockup"],
                "domains": ["frontend", "design", "prototyping"],
                "phases": ["design"],
                "priority": 5
            },
            "production-frontend": {
                "keywords": ["react app", "vue app", "frontend deployment", "component"],
                "domains": ["frontend", "react", "vue", "angular"],
                "phases": ["implementation"],
                "priority": 6
            },
            "backend-services": {
                "keywords": ["backend", "api", "service", "server", "microservice"],
                "domains": ["backend", "services", "api"],
                "phases": ["implementation"],
                "priority": 6
            },
            "database-architecture": {
                "keywords": ["database", "schema", "query", "migration", "sql"],
                "domains": ["database", "data", "architecture"],
                "phases": ["design", "implementation"],
                "priority": 6
            },
            "middleware-specialist": {
                "keywords": ["middleware", "message queue", "event bus", "cache"],
                "domains": ["middleware", "integration", "messaging"],
                "phases": ["implementation", "design"],
                "priority": 7
            },
            "testing-automation": {
                "keywords": ["test", "testing", "coverage", "unit test", "e2e"],
                "domains": ["testing", "qa", "automation"],
                "phases": ["testing", "implementation"],
                "priority": 7
            },
            "development-prompt": {
                "keywords": ["prompt", "workflow", "phase", "context", "chain"],
                "domains": ["prompting", "workflow", "development"],
                "phases": ["all"],
                "priority": 7
            },
            "script-automation": {
                "keywords": ["script", "setup", "build", "deploy", "automation"],
                "domains": ["scripting", "automation", "devops"],
                "phases": ["implementation", "deployment"],
                "priority": 8
            },
            "integration-setup": {
                "keywords": ["install", "dependency", "package", "environment", "setup"],
                "domains": ["setup", "integration", "environment"],
                "phases": ["implementation"],
                "priority": 8
            },
            "security-architecture": {
                "keywords": ["security", "vulnerability", "threat", "encryption", "auth"],
                "domains": ["security", "compliance", "authentication"],
                "phases": ["all"],
                "priority": 8
            },
            "performance-optimization": {
                "keywords": ["performance", "optimization", "profiling", "caching", "scalability"],
                "domains": ["performance", "optimization", "scalability"],
                "phases": ["testing", "deployment"],
                "priority": 9
            },
            "devops-engineer": {
                "keywords": ["deploy", "ci/cd", "pipeline", "container", "kubernetes"],
                "domains": ["devops", "deployment", "infrastructure"],
                "phases": ["deployment"],
                "priority": 9
            },
            "quality-assurance-lead": {
                "keywords": ["qa", "quality", "test coverage", "bug", "defect"],
                "domains": ["qa", "testing", "quality"],
                "phases": ["testing"],
                "priority": 9
            },
            "mobile-developer": {
                "keywords": ["mobile", "ios", "android", "react native", "flutter"],
                "domains": ["mobile", "ios", "android"],
                "phases": ["implementation"],
                "priority": 10
            },
            "ui-ux-designer": {
                "keywords": ["ui", "ux", "design", "wireframe", "mockup", "prototype"],
                "domains": ["design", "ui", "ux"],
                "phases": ["design"],
                "priority": 10
            },
            "usage-guide-agent": {
                "keywords": ["guide", "usage", "meta", "configuration", "workflow"],
                "domains": ["configuration", "workflow", "meta"],
                "phases": ["exploration"],
                "priority": 1
            }
        }
    
    def load_orchestration_patterns(self) -> Dict[str, Any]:
        """Load common orchestration patterns"""
        return {
            "new_project": [
                "usage-guide-agent",
                "prompt-engineer",
                "business-analyst",
                "technical-cto",
                "master-orchestrator"
            ],
            "feature_development": [
                "prompt-engineer",
                "technical-specifications",
                "frontend-architecture",
                "backend-services",
                "testing-automation"
            ],
            "bug_fix": [
                "testing-automation",
                "security-architecture",
                "backend-services",
                "production-frontend"
            ],
            "optimization": [
                "performance-optimization",
                "database-architecture",
                "middleware-specialist"
            ],
            "deployment": [
                "devops-engineer",
                "script-automation",
                "technical-documentation"
            ]
        }
    
    def analyze_request(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze user request to determine intent and requirements"""
        prompt_lower = user_prompt.lower()
        
        analysis = {
            "intent": self.detect_intent(prompt_lower),
            "domains": self.detect_domains(prompt_lower),
            "complexity": self.assess_complexity(prompt_lower),
            "keywords": self.extract_keywords(prompt_lower),
            "pattern_match": self.match_pattern(prompt_lower)
        }
        
        return analysis
    
    def detect_intent(self, prompt: str) -> str:
        """Detect primary intent from prompt"""
        intents = {
            "create": ["create", "build", "make", "generate", "develop"],
            "fix": ["fix", "repair", "debug", "solve", "issue"],
            "optimize": ["optimize", "improve", "enhance", "speed up"],
            "analyze": ["analyze", "review", "assess", "evaluate"],
            "deploy": ["deploy", "release", "publish", "launch"],
            "document": ["document", "explain", "describe", "write"]
        }
        
        for intent, keywords in intents.items():
            if any(kw in prompt for kw in keywords):
                return intent
        
        return "general"
    
    def detect_domains(self, prompt: str) -> List[str]:
        """Detect technical domains mentioned"""
        domains = []
        
        domain_keywords = {
            "frontend": ["ui", "react", "vue", "angular", "frontend", "component"],
            "backend": ["api", "backend", "service", "server", "endpoint"],
            "database": ["database", "sql", "query", "schema", "migration"],
            "mobile": ["mobile", "ios", "android", "app"],
            "security": ["security", "auth", "encryption", "vulnerability"],
            "devops": ["deploy", "ci/cd", "docker", "kubernetes"],
            "testing": ["test", "testing", "coverage", "qa"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in prompt for kw in keywords):
                domains.append(domain)
        
        return domains if domains else ["general"]
    
    def assess_complexity(self, prompt: str) -> str:
        """Assess request complexity"""
        word_count = len(prompt.split())
        
        # Check for complex indicators
        complex_indicators = [
            "full", "complete", "entire", "comprehensive",
            "production", "scalable", "enterprise"
        ]
        
        simple_indicators = [
            "simple", "basic", "quick", "small",
            "test", "example", "demo"
        ]
        
        if any(ind in prompt for ind in complex_indicators) or word_count > 50:
            return "high"
        elif any(ind in prompt for ind in simple_indicators) or word_count < 20:
            return "low"
        else:
            return "medium"
    
    def extract_keywords(self, prompt: str) -> List[str]:
        """Extract relevant keywords from prompt"""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "as", "is", "was",
            "are", "were", "been", "be", "have", "has", "had", "do",
            "does", "did", "will", "would", "should", "could", "may",
            "might", "must", "can", "need", "want", "please", "help"
        }
        
        words = prompt.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def match_pattern(self, prompt: str) -> Optional[str]:
        """Match prompt to known orchestration patterns"""
        for pattern_name, pattern_keywords in {
            "new_project": ["new project", "start project", "create app"],
            "feature_development": ["add feature", "implement", "create functionality"],
            "bug_fix": ["fix bug", "debug", "issue", "error"],
            "optimization": ["optimize", "improve performance", "speed up"],
            "deployment": ["deploy", "release", "publish", "go live"]
        }.items():
            if any(kw in prompt for kw in pattern_keywords):
                return pattern_name
        return None
    
    def calculate_agent_scores(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate relevance scores for each agent"""
        scores = {}
        current_phase = context.get("phase", "exploration")
        
        for agent_name, agent_def in self.agents.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for kw in analysis["keywords"] 
                                if any(akw in kw for akw in agent_def["keywords"]))
            score += keyword_matches * self.CONTEXT_WEIGHTS["keyword_match"]
            
            # Phase alignment
            if current_phase in agent_def["phases"] or "all" in agent_def["phases"]:
                score += self.CONTEXT_WEIGHTS["phase_alignment"]
            
            # Domain expertise
            domain_matches = sum(1 for domain in analysis["domains"]
                               if domain in agent_def["domains"])
            score += domain_matches * self.CONTEXT_WEIGHTS["domain_expertise"]
            
            # Recent success (check history)
            recent_success = self.get_agent_success_rate(agent_name)
            score += recent_success * self.CONTEXT_WEIGHTS["recent_success"]
            
            # Apply priority modifier
            priority = agent_def.get("priority", 10)
            score *= (11 - priority) / 10  # Higher priority = higher multiplier
            
            scores[agent_name] = score
        
        return scores
    
    def get_agent_success_rate(self, agent_name: str) -> float:
        """Get recent success rate for an agent"""
        if not self.history_file.exists():
            return 0.5  # Default neutral score
        
        try:
            history = json.loads(self.history_file.read_text())
            agent_history = history.get(agent_name, {})
            
            if not agent_history:
                return 0.5
            
            recent = agent_history.get("recent_executions", [])[-10:]  # Last 10 executions
            if not recent:
                return 0.5
            
            successes = sum(1 for exec in recent if exec.get("success", False))
            return successes / len(recent)
        except:
            return 0.5
    
    def select_agents(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Select optimal agents based on analysis and context"""
        # Calculate scores
        scores = self.calculate_agent_scores(analysis, context)
        
        # Sort agents by score
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Determine selection strategy
        complexity = analysis["complexity"]
        
        if complexity == "high":
            # Complex task - use more agents
            threshold = 0.3
            max_agents = 8
        elif complexity == "medium":
            # Medium task - moderate agents
            threshold = 0.4
            max_agents = 5
        else:
            # Simple task - minimal agents
            threshold = 0.5
            max_agents = 3
        
        # Check for pattern match
        if analysis["pattern_match"]:
            pattern_agents = self.patterns[analysis["pattern_match"]]
            # Boost scores for pattern agents
            for agent in pattern_agents:
                if agent in scores:
                    scores[agent] *= 1.5
            
            # Re-sort with boosted scores
            sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select agents above threshold
        selected = []
        for agent_name, score in sorted_agents:
            if score >= threshold and len(selected) < max_agents:
                selected.append(agent_name)
        
        # Always include prompt-engineer for complex tasks
        if complexity == "high" and "prompt-engineer" not in selected:
            selected.insert(0, "prompt-engineer")
        
        # Always include master-orchestrator if multiple agents selected
        if len(selected) > 2 and "master-orchestrator" not in selected:
            selected.insert(1, "master-orchestrator")
        
        return selected
    
    def create_execution_plan(self, agents: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for selected agents"""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "agents": agents,
            "execution_groups": [],
            "dependencies": {},
            "estimated_time_ms": 0
        }
        
        # Group agents by priority for parallel execution
        priority_groups = {}
        for agent in agents:
            priority = self.agents[agent].get("priority", 10)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(agent)
        
        # Create execution groups (agents with same priority run in parallel)
        for priority in sorted(priority_groups.keys()):
            plan["execution_groups"].append({
                "priority": priority,
                "agents": priority_groups[priority],
                "parallel": True
            })
        
        # Estimate execution time
        base_time = 500  # Base time per agent in ms
        plan["estimated_time_ms"] = len(agents) * base_time
        
        # Add dependencies
        if "prompt-engineer" in agents:
            for agent in agents:
                if agent != "prompt-engineer":
                    plan["dependencies"][agent] = ["prompt-engineer"]
        
        if "master-orchestrator" in agents:
            for agent in agents:
                if agent not in ["prompt-engineer", "master-orchestrator"]:
                    if agent not in plan["dependencies"]:
                        plan["dependencies"][agent] = []
                    plan["dependencies"][agent].append("master-orchestrator")
        
        return plan
    
    def optimize_execution(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize execution plan for efficiency"""
        # Identify agents that can be run in parallel
        parallel_categories = {
            "analysis": [],
            "design": [],
            "implementation": [],
            "quality": [],
            "management": [],
            "setup": []
        }
        
        for group in plan["execution_groups"]:
            for agent in group["agents"]:
                for category, category_agents in self.AGENT_CATEGORIES.items():
                    if agent in category_agents:
                        parallel_categories[category].append(agent)
                        break
        
        # Reorganize for maximum parallelization
        optimized_groups = []
        priority_counter = 1
        
        # Order of execution by category
        category_order = ["management", "analysis", "design", "implementation", "quality", "setup"]
        
        for category in category_order:
            if parallel_categories[category]:
                optimized_groups.append({
                    "priority": priority_counter,
                    "agents": parallel_categories[category],
                    "parallel": True,
                    "category": category
                })
                priority_counter += 1
        
        # Add any remaining agents
        categorized_agents = set()
        for category_agents in parallel_categories.values():
            categorized_agents.update(category_agents)
        
        remaining = [a for a in plan["agents"] if a not in categorized_agents]
        if remaining:
            optimized_groups.append({
                "priority": 4,
                "agents": remaining,
                "parallel": False,
                "category": "other"
            })
        
        plan["execution_groups"] = optimized_groups
        plan["optimized"] = True
        
        return plan
    
    def execute_orchestration(self, user_prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Main orchestration execution"""
        # Get current context
        if not context:
            context = self.get_current_context()
        
        # Analyze request
        analysis = self.analyze_request(user_prompt)
        
        # Select agents
        selected_agents = self.select_agents(analysis, context)
        
        # Create execution plan
        plan = self.create_execution_plan(selected_agents, analysis)
        
        # Optimize execution
        plan = self.optimize_execution(plan)
        
        # Log orchestration
        self.log_orchestration(user_prompt, plan)
        
        return {
            "success": True,
            "plan": plan,
            "selected_agents": selected_agents,
            "analysis": analysis,
            "recommendation": self.generate_recommendation(plan)
        }
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current system context"""
        context = {"phase": "exploration"}
        
        # Try to load from status line
        status_file = self.home_dir / "status.json"
        if status_file.exists():
            try:
                status = json.loads(status_file.read_text())
                context["phase"] = status.get("phase", "exploration")
                context["tokens"] = status.get("tokens", {})
                context["agents"] = status.get("agents", [])
            except:
                pass
        
        return context
    
    def generate_recommendation(self, plan: Dict[str, Any]) -> str:
        """Generate execution recommendation"""
        agent_count = len(plan["agents"])
        group_count = len(plan["execution_groups"])
        
        if agent_count == 0:
            return "No specific agents needed - Claude can handle this directly"
        elif agent_count == 1:
            return f"Single agent execution: {plan['agents'][0]}"
        elif group_count == 1:
            return f"Parallel execution of {agent_count} agents"
        else:
            return f"Multi-phase execution: {group_count} groups, {agent_count} total agents"
    
    def log_orchestration(self, prompt: str, plan: Dict[str, Any]):
        """Log orchestration decision for learning"""
        try:
            history = {}
            if self.history_file.exists():
                history = json.loads(self.history_file.read_text())
            
            # Add new orchestration
            orchestration_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            history[orchestration_id] = {
                "prompt": prompt[:200],  # Truncate long prompts
                "agents": plan["agents"],
                "timestamp": plan["timestamp"],
                "complexity": plan["analysis"]["complexity"]
            }
            
            # Keep only last 100 orchestrations
            if len(history) > 100:
                # Sort by timestamp and keep most recent
                sorted_items = sorted(history.items(), 
                                    key=lambda x: x[1]["timestamp"], 
                                    reverse=True)
                history = dict(sorted_items[:100])
            
            self.history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            print(f"Failed to log orchestration: {e}", file=sys.stderr)

def handle_agent_mentions(user_prompt: str) -> Optional[List[str]]:
    """Parse @agent- mentions from prompt"""
    import re
    
    agent_pattern = r'@agent-([a-z-]+)(?:\[(opus|haiku|sonnet)\])?'
    mentions = []
    
    for match in re.finditer(agent_pattern, user_prompt):
        agent_name = match.group(1)
        model = match.group(2) or "default"
        mentions.append({
            "agent": agent_name,
            "model": model,
            "mention": match.group(0)
        })
    
    if mentions:
        return [m["agent"] for m in mentions]
    return None

def main():
    """Main entry point for smart orchestration"""
    orchestrator = SmartOrchestrator()
    
    if len(sys.argv) < 2:
        print("Usage: smart_orchestrator.py <user_prompt>")
        sys.exit(1)
    
    user_prompt = " ".join(sys.argv[1:])
    
    # Check for explicit @agent mentions first
    mentioned_agents = handle_agent_mentions(user_prompt)
    
    if mentioned_agents:
        # User explicitly mentioned agents - prioritize those
        result = {
            "success": True,
            "selected_agents": mentioned_agents,
            "plan": {"execution_groups": [{"priority": 1, "agents": mentioned_agents, "parallel": True}]},
            "recommendation": f"Explicit agent routing: {', '.join(mentioned_agents)}",
            "routing_type": "explicit_mention"
        }
    else:
        # Execute smart orchestration
        result = orchestrator.execute_orchestration(user_prompt)
        result["routing_type"] = "smart_selection"
    
    # Output result
    if result["success"]:
        print(json.dumps({
            "agents": result["selected_agents"],
            "execution_plan": result["plan"]["execution_groups"],
            "recommendation": result["recommendation"],
            "routing_type": result.get("routing_type", "smart_selection")
        }, indent=2))
    else:
        print(json.dumps({"error": "Orchestration failed"}, indent=2))

if __name__ == "__main__":
    main()