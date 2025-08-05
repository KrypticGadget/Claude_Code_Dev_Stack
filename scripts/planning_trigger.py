#!/usr/bin/env python3
"""
Planning Trigger Hook - Detect when planning or architectural decisions are needed
Analyzes requests to determine if Master Orchestrator should be engaged
"""

import sys
import json
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from base_hook import BaseHook


class PlanningTrigger(BaseHook):
    """Detect planning and architectural needs"""
    
    # Keywords that indicate planning is needed
    PLANNING_INDICATORS = {
        'architecture': {
            'keywords': ['architecture', 'design', 'structure', 'organize', 'scaffold'],
            'weight': 0.9
        },
        'project_setup': {
            'keywords': ['create project', 'new project', 'setup', 'initialize', 'bootstrap'],
            'weight': 0.95
        },
        'integration': {
            'keywords': ['integrate', 'connect', 'combine', 'merge', 'unify'],
            'weight': 0.7
        },
        'refactoring': {
            'keywords': ['refactor', 'restructure', 'reorganize', 'migrate', 'modernize'],
            'weight': 0.8
        },
        'scaling': {
            'keywords': ['scale', 'performance', 'optimize', 'distributed', 'microservices'],
            'weight': 0.75
        },
        'complexity': {
            'keywords': ['complex', 'enterprise', 'large-scale', 'multi-tenant', 'saas'],
            'weight': 0.85
        },
        'planning': {
            'keywords': ['plan', 'roadmap', 'strategy', 'approach', 'methodology'],
            'weight': 0.8
        },
        'multiple_components': {
            'keywords': ['frontend and backend', 'full stack', 'end to end', 'entire', 'whole'],
            'weight': 0.85
        }
    }
    
    # Phrases that indicate immediate action without planning
    DIRECT_ACTION_INDICATORS = [
        'fix bug', 'add button', 'change color', 'update text', 'correct typo',
        'small change', 'quick fix', 'minor update', 'simple'
    ]
    
    def __init__(self):
        super().__init__('planning_trigger')
        self.threshold = self.config.get('planning_threshold', 0.6)
    
    def run(self) -> int:
        """Analyze request to determine if planning is needed"""
        # Read input from stdin
        input_text = self.read_stdin()
        
        if not input_text:
            self.logger.debug("No input received")
            return 0
        
        # Analyze the request
        analysis = self.analyze_request(input_text)
        
        # Make planning decision
        decision = self.make_planning_decision(analysis)
        
        # Save decision
        self.save_cache('planning_decision', decision)
        
        # Output decision
        self.write_stdout(json.dumps(decision, indent=2))
        
        self.logger.info("Planning analysis completed", 
                        needs_planning=decision['needs_planning'],
                        confidence=decision['confidence'])
        
        return 0
    
    def analyze_request(self, text: str) -> Dict[str, Any]:
        """Analyze request for planning indicators"""
        text_lower = text.lower()
        
        analysis = {
            'text_length': len(text),
            'indicators_found': [],
            'direct_action_found': False,
            'complexity_score': 0,
            'scope_score': 0,
            'questions_count': 0,
            'components_mentioned': []
        }
        
        # Check for planning indicators
        for category, config in self.PLANNING_INDICATORS.items():
            for keyword in config['keywords']:
                if keyword in text_lower:
                    analysis['indicators_found'].append({
                        'category': category,
                        'keyword': keyword,
                        'weight': config['weight']
                    })
        
        # Check for direct action indicators
        for phrase in self.DIRECT_ACTION_INDICATORS:
            if phrase in text_lower:
                analysis['direct_action_found'] = True
                break
        
        # Analyze complexity
        analysis['complexity_score'] = self._calculate_complexity_score(text)
        
        # Analyze scope
        analysis['scope_score'] = self._calculate_scope_score(text)
        
        # Count questions
        analysis['questions_count'] = len(re.findall(r'\?', text))
        
        # Detect components mentioned
        analysis['components_mentioned'] = self._detect_components(text_lower)
        
        # Check for specific patterns
        analysis['patterns'] = self._detect_patterns(text_lower)
        
        return analysis
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score based on various factors"""
        score = 0.0
        
        # Length indicates complexity
        if len(text) > 500:
            score += 0.2
        if len(text) > 1000:
            score += 0.3
        
        # Multiple requirements
        requirements = len(re.findall(r'(?:should|must|need to|want to|have to)', text, re.IGNORECASE))
        score += min(requirements * 0.1, 0.5)
        
        # Technical terms
        tech_terms = ['api', 'database', 'authentication', 'deployment', 'integration', 
                     'microservice', 'container', 'kubernetes', 'aws', 'cloud']
        tech_count = sum(1 for term in tech_terms if term in text.lower())
        score += min(tech_count * 0.1, 0.4)
        
        # Lists or multiple items
        if re.search(r'(?:\d+\.|[-*]|\n\s*\n)', text):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_scope_score(self, text: str) -> float:
        """Calculate scope score based on breadth of request"""
        score = 0.0
        text_lower = text.lower()
        
        # Multiple system components
        components = ['frontend', 'backend', 'database', 'api', 'ui', 'server', 
                     'client', 'mobile', 'web', 'desktop']
        component_count = sum(1 for comp in components if comp in text_lower)
        score += min(component_count * 0.2, 0.6)
        
        # Time-related words indicate larger scope
        if re.search(r'\b(project|application|system|platform|solution)\b', text_lower):
            score += 0.3
        
        # Multiple user types
        if re.search(r'\b(admin|user|customer|client|staff|employee)\b.*\b(admin|user|customer|client|staff|employee)\b', text_lower):
            score += 0.2
        
        return min(score, 1.0)
    
    def _detect_components(self, text: str) -> List[str]:
        """Detect which system components are mentioned"""
        components = []
        
        component_patterns = {
            'frontend': r'\b(frontend|ui|user interface|react|vue|angular|web app)\b',
            'backend': r'\b(backend|api|server|rest|graphql|microservice)\b',
            'database': r'\b(database|db|sql|mongodb|postgres|mysql|redis)\b',
            'authentication': r'\b(auth|authentication|login|jwt|oauth|security)\b',
            'deployment': r'\b(deploy|deployment|docker|kubernetes|ci/cd|devops)\b',
            'testing': r'\b(test|testing|jest|pytest|unit test|integration)\b',
            'mobile': r'\b(mobile|ios|android|react native|flutter)\b'
        }
        
        for component, pattern in component_patterns.items():
            if re.search(pattern, text):
                components.append(component)
        
        return components
    
    def _detect_patterns(self, text: str) -> Dict[str, bool]:
        """Detect specific request patterns"""
        patterns = {
            'new_project': bool(re.search(r'\b(create|build|develop|make)\s+(?:a\s+)?(?:new\s+)?(?:project|app|application|system)\b', text)),
            'architecture_question': bool(re.search(r'\b(?:how|what|which|should)\s+.*\b(?:architecture|design|structure|organize)\b', text)),
            'technology_choice': bool(re.search(r'\b(?:which|what|should)\s+.*\b(?:technology|framework|library|tool|stack)\b', text)),
            'best_practices': bool(re.search(r'\b(?:best practice|recommended|standard|convention|pattern)\b', text)),
            'migration': bool(re.search(r'\b(?:migrate|upgrade|modernize|refactor|transform)\b', text)),
            'integration': bool(re.search(r'\b(?:integrate|connect|combine|interface with|work with)\b', text))
        }
        
        return patterns
    
    def make_planning_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision about whether planning is needed"""
        # Calculate overall planning score
        planning_score = 0.0
        
        # Weight from indicators
        for indicator in analysis['indicators_found']:
            planning_score += indicator['weight'] * 0.3
        
        # Add complexity and scope scores
        planning_score += analysis['complexity_score'] * 0.25
        planning_score += analysis['scope_score'] * 0.25
        
        # Pattern bonuses
        pattern_bonus = sum(0.1 for pattern, found in analysis['patterns'].items() if found)
        planning_score += min(pattern_bonus, 0.3)
        
        # Multiple components bonus
        if len(analysis['components_mentioned']) >= 3:
            planning_score += 0.2
        
        # Direct action penalty
        if analysis['direct_action_found']:
            planning_score *= 0.5
        
        # Normalize score
        planning_score = min(planning_score, 1.0)
        
        # Determine if planning is needed
        needs_planning = planning_score >= self.threshold
        
        # Determine planning type
        planning_type = self._determine_planning_type(analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, planning_score)
        
        decision = {
            'needs_planning': needs_planning,
            'confidence': planning_score,
            'planning_type': planning_type,
            'reasons': self._generate_reasons(analysis),
            'recommendations': recommendations,
            'suggested_agents': self._suggest_agents(analysis),
            'analysis_summary': {
                'complexity_score': analysis['complexity_score'],
                'scope_score': analysis['scope_score'],
                'components': analysis['components_mentioned'],
                'indicators_count': len(analysis['indicators_found'])
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return decision
    
    def _determine_planning_type(self, analysis: Dict[str, Any]) -> str:
        """Determine what type of planning is needed"""
        if analysis['patterns']['new_project']:
            return 'project_initialization'
        elif analysis['patterns']['architecture_question']:
            return 'architecture_design'
        elif analysis['patterns']['migration']:
            return 'migration_planning'
        elif analysis['patterns']['integration']:
            return 'integration_planning'
        elif len(analysis['components_mentioned']) >= 3:
            return 'multi_component_coordination'
        else:
            return 'general_planning'
    
    def _generate_reasons(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate human-readable reasons for the decision"""
        reasons = []
        
        if analysis['complexity_score'] > 0.6:
            reasons.append("Request involves complex requirements")
        
        if analysis['scope_score'] > 0.6:
            reasons.append("Request spans multiple system components")
        
        if len(analysis['components_mentioned']) >= 3:
            reasons.append(f"Involves {len(analysis['components_mentioned'])} different components")
        
        if analysis['patterns']['new_project']:
            reasons.append("Creating a new project requires architectural planning")
        
        if analysis['patterns']['technology_choice']:
            reasons.append("Technology selection requires careful consideration")
        
        if analysis['indicators_found']:
            categories = list(set(ind['category'] for ind in analysis['indicators_found']))
            reasons.append(f"Contains planning indicators: {', '.join(categories)}")
        
        return reasons
    
    def _generate_recommendations(self, analysis: Dict[str, Any], score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if score >= self.threshold:
            recommendations.append("Engage @agent-orchestrator for comprehensive planning")
            
            if analysis['patterns']['new_project']:
                recommendations.append("Define project structure and technology stack first")
            
            if len(analysis['components_mentioned']) >= 3:
                recommendations.append("Create component interaction diagrams")
            
            if analysis['patterns']['technology_choice']:
                recommendations.append("Evaluate technology options against requirements")
        else:
            recommendations.append("Proceed with direct implementation")
            
            if analysis['components_mentioned']:
                agent = self._get_primary_agent(analysis['components_mentioned'])
                recommendations.append(f"Route directly to {agent}")
        
        return recommendations
    
    def _suggest_agents(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest which agents should be involved"""
        agents = []
        
        # Always include orchestrator for planning
        if analysis['patterns']['new_project'] or len(analysis['components_mentioned']) >= 3:
            agents.append('@agent-orchestrator')
        
        # Add component-specific agents
        component_agent_map = {
            'frontend': '@agent-frontend',
            'backend': '@agent-backend',
            'database': '@agent-database',
            'authentication': '@agent-security',
            'deployment': '@agent-devops',
            'testing': '@agent-testing',
            'mobile': '@agent-mobile'
        }
        
        for component in analysis['components_mentioned']:
            if component in component_agent_map:
                agent = component_agent_map[component]
                if agent not in agents:
                    agents.append(agent)
        
        return agents
    
    def _get_primary_agent(self, components: List[str]) -> str:
        """Get primary agent for direct routing"""
        if 'frontend' in components:
            return '@agent-frontend'
        elif 'backend' in components:
            return '@agent-backend'
        elif 'database' in components:
            return '@agent-database'
        else:
            return '@agent-orchestrator'


def main():
    """Main entry point"""
    trigger = PlanningTrigger()
    return trigger.safe_run()


if __name__ == "__main__":
    sys.exit(main())