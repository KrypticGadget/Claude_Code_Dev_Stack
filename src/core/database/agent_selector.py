#!/usr/bin/env python3
"""
Intelligent Agent Selection Engine
High-performance agent recommendation system with machine learning capabilities
"""

import asyncio
import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import math

from .agent_metadata_db import (
    AsyncAgentMetadataDB, AgentMetadataDB, DatabaseConfig,
    Agent, AgentRecommendation, create_database_manager
)


# ========== SELECTION CONTEXT ==========

@dataclass
class SelectionContext:
    """Context information for agent selection"""
    user_query: str
    keywords: List[str]
    file_types: List[str]
    project_phase: str
    time_context: Dict[str, Any]
    session_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    performance_requirements: Dict[str, Any]
    
    def to_fingerprint(self) -> str:
        """Generate unique fingerprint for this context"""
        context_data = {
            'keywords': sorted(self.keywords),
            'file_types': sorted(self.file_types),
            'project_phase': self.project_phase,
            'hour': self.time_context.get('hour'),
            'day_of_week': self.time_context.get('day_of_week')
        }
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()


@dataclass
class AgentScore:
    """Detailed scoring breakdown for an agent"""
    agent_id: str
    agent_name: str
    total_score: float
    
    # Individual score components
    keyword_match_score: float
    phase_alignment_score: float
    recent_success_score: float
    domain_expertise_score: float
    availability_score: float
    collaboration_score: float
    user_preference_score: float
    
    # Additional metrics
    confidence_level: float
    reasoning: List[str]
    estimated_duration_ms: int
    estimated_success_probability: float


# ========== KEYWORD EXTRACTION ==========

class KeywordExtractor:
    """Extract relevant keywords and context from user queries"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Domain-specific keyword patterns
        self.domain_patterns = {
            'database': r'\b(database|db|sql|postgres|mysql|mongodb|redis|schema|table|query|index)\b',
            'frontend': r'\b(frontend|ui|ux|react|vue|angular|html|css|javascript|component)\b',
            'backend': r'\b(backend|api|server|service|endpoint|rest|graphql|microservice)\b',
            'testing': r'\b(test|testing|unit|integration|e2e|automation|pytest|jest)\b',
            'deployment': r'\b(deploy|deployment|docker|kubernetes|aws|cloud|ci/cd|pipeline)\b',
            'performance': r'\b(performance|optimization|speed|latency|throughput|caching)\b',
            'security': r'\b(security|authentication|authorization|encryption|vulnerability)\b',
            'design': r'\b(design|architecture|pattern|structure|modeling|diagram)\b'
        }
        
        # Programming language patterns
        self.language_patterns = {
            'python': r'\b(python|py|django|flask|fastapi|pandas|numpy)\b',
            'javascript': r'\b(javascript|js|node|npm|yarn|express|nextjs)\b',
            'typescript': r'\b(typescript|ts|types|interface|generic)\b',
            'java': r'\b(java|spring|maven|gradle|jvm)\b',
            'go': r'\b(go|golang|goroutine|channel)\b',
            'rust': r'\b(rust|cargo|crate|lifetime)\b',
            'sql': r'\b(sql|select|insert|update|delete|join|where)\b'
        }
        
        # Phase detection patterns
        self.phase_patterns = {
            'planning': r'\b(plan|planning|design|architect|strategy|requirement)\b',
            'design': r'\b(design|model|schema|structure|pattern|diagram)\b',
            'implementation': r'\b(implement|code|build|develop|create|write)\b',
            'testing': r'\b(test|testing|verify|validate|debug|fix)\b',
            'deployment': r'\b(deploy|release|publish|launch|production)\b',
            'optimization': r'\b(optimize|improve|performance|speed|efficiency)\b',
            'maintenance': r'\b(maintain|update|refactor|cleanup|monitor)\b'
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Count frequency and take most common
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]
    
    def detect_domains(self, text: str) -> List[str]:
        """Detect technical domains mentioned in text"""
        domains = []
        text_lower = text.lower()
        
        for domain, pattern in self.domain_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                domains.append(domain)
        
        return domains
    
    def detect_languages(self, text: str) -> List[str]:
        """Detect programming languages mentioned in text"""
        languages = []
        text_lower = text.lower()
        
        for lang, pattern in self.language_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                languages.append(lang)
        
        return languages
    
    def detect_phase(self, text: str) -> str:
        """Detect project phase from text"""
        text_lower = text.lower()
        phase_scores = {}
        
        for phase, pattern in self.phase_patterns.items():
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            if matches > 0:
                phase_scores[phase] = matches
        
        if phase_scores:
            return max(phase_scores.items(), key=lambda x: x[1])[0]
        
        return 'implementation'  # Default phase
    
    def extract_file_types(self, text: str) -> List[str]:
        """Extract file type mentions from text"""
        file_patterns = r'\b(\w+\.(py|js|ts|java|go|rs|sql|html|css|json|yaml|yml|md|txt))\b|\b(\.py|\.js|\.ts|\.java|\.go|\.rs|\.sql|\.html|\.css)\b'
        matches = re.findall(file_patterns, text.lower())
        
        file_types = set()
        for match in matches:
            if isinstance(match, tuple):
                for item in match:
                    if item and item.startswith('.'):
                        file_types.add(item[1:])  # Remove the dot
                    elif '.' in item:
                        file_types.add(item.split('.')[-1])
            else:
                if '.' in match:
                    file_types.add(match.split('.')[-1])
        
        return list(file_types)


# ========== AGENT SELECTION ENGINE ==========

class AgentSelectionEngine:
    """
    Intelligent agent selection engine with machine learning capabilities
    """
    
    def __init__(self, db: AsyncAgentMetadataDB):
        self.db = db
        self.keyword_extractor = KeywordExtractor()
        self.logger = logging.getLogger(__name__)
        
        # Selection weights (can be tuned based on performance)
        self.weights = {
            'keyword_match': 0.25,
            'phase_alignment': 0.20,
            'recent_success': 0.15,
            'domain_expertise': 0.15,
            'availability': 0.10,
            'collaboration': 0.10,
            'user_preference': 0.05
        }
        
        # Cache for recent selections
        self._selection_cache = {}
        self._cache_duration = timedelta(minutes=15)
    
    async def select_best_agent(self, 
                               user_query: str,
                               session_history: List[Dict[str, Any]] = None,
                               user_preferences: Dict[str, Any] = None,
                               performance_requirements: Dict[str, Any] = None) -> Optional[AgentScore]:
        """Select the best agent for a given query"""
        
        context = await self._build_selection_context(
            user_query, session_history, user_preferences, performance_requirements
        )
        
        # Check cache first
        cache_key = context.to_fingerprint()
        if cache_key in self._selection_cache:
            cached_result, timestamp = self._selection_cache[cache_key]
            if datetime.now() - timestamp < self._cache_duration:
                return cached_result
        
        # Get candidate agents
        candidates = await self._get_candidate_agents(context)
        if not candidates:
            return None
        
        # Score all candidates
        scored_agents = await self._score_agents(candidates, context)
        
        # Select best agent
        best_agent = max(scored_agents, key=lambda x: x.total_score) if scored_agents else None
        
        # Cache result
        if best_agent:
            self._selection_cache[cache_key] = (best_agent, datetime.now())
            
            # Record selection pattern for learning
            await self._record_selection_pattern(context, best_agent)
        
        return best_agent
    
    async def get_top_recommendations(self,
                                    user_query: str,
                                    count: int = 5,
                                    session_history: List[Dict[str, Any]] = None,
                                    user_preferences: Dict[str, Any] = None) -> List[AgentScore]:
        """Get top N agent recommendations"""
        
        context = await self._build_selection_context(
            user_query, session_history, user_preferences
        )
        
        # Get candidate agents
        candidates = await self._get_candidate_agents(context, limit=count * 2)
        
        # Score all candidates
        scored_agents = await self._score_agents(candidates, context)
        
        # Return top recommendations
        return sorted(scored_agents, key=lambda x: x.total_score, reverse=True)[:count]
    
    async def _build_selection_context(self,
                                     user_query: str,
                                     session_history: List[Dict[str, Any]] = None,
                                     user_preferences: Dict[str, Any] = None,
                                     performance_requirements: Dict[str, Any] = None) -> SelectionContext:
        """Build comprehensive selection context"""
        
        # Extract query features
        keywords = self.keyword_extractor.extract_keywords(user_query)
        domains = self.keyword_extractor.detect_domains(user_query)
        languages = self.keyword_extractor.detect_languages(user_query)
        phase = self.keyword_extractor.detect_phase(user_query)
        file_types = self.keyword_extractor.extract_file_types(user_query)
        
        # Combine all extracted features
        all_keywords = keywords + domains + languages
        
        # Time context
        now = datetime.now()
        time_context = {
            'hour': now.hour,
            'day_of_week': now.weekday() + 1,
            'timestamp': now.isoformat()
        }
        
        return SelectionContext(
            user_query=user_query,
            keywords=all_keywords,
            file_types=file_types,
            project_phase=phase,
            time_context=time_context,
            session_history=session_history or [],
            user_preferences=user_preferences or {},
            performance_requirements=performance_requirements or {}
        )
    
    async def _get_candidate_agents(self, 
                                  context: SelectionContext,
                                  limit: int = 10) -> List[Agent]:
        """Get candidate agents for selection"""
        
        # Start with text search if we have keywords
        if context.keywords:
            candidates = await self.db.search_agents(
                query_text=' '.join(context.keywords[:5]),  # Top 5 keywords
                limit=limit
            )
        else:
            # Fallback to getting active agents
            candidates = await self.db.search_agents(limit=limit)
        
        # Filter by specialization if we detected specific domains
        if context.keywords:
            specialized_candidates = []
            for agent in candidates:
                # Check if agent specializations overlap with context keywords
                specialization_overlap = set(agent.specializations) & set(context.keywords)
                keyword_overlap = set(agent.keywords) & set(context.keywords)
                
                if specialization_overlap or keyword_overlap:
                    specialized_candidates.append(agent)
            
            # Use specialized candidates if we found any, otherwise use all
            if specialized_candidates:
                candidates = specialized_candidates
        
        return candidates
    
    async def _score_agents(self, 
                           candidates: List[Agent],
                           context: SelectionContext) -> List[AgentScore]:
        """Score agents based on selection context"""
        
        scored_agents = []
        
        for agent in candidates:
            # Calculate individual scores
            keyword_score = self._calculate_keyword_score(agent, context)
            phase_score = self._calculate_phase_score(agent, context)
            success_score = self._calculate_success_score(agent)
            expertise_score = self._calculate_expertise_score(agent, context)
            availability_score = await self._calculate_availability_score(agent)
            collaboration_score = await self._calculate_collaboration_score(agent, context)
            preference_score = self._calculate_user_preference_score(agent, context)
            
            # Calculate total weighted score
            total_score = (
                keyword_score * self.weights['keyword_match'] +
                phase_score * self.weights['phase_alignment'] +
                success_score * self.weights['recent_success'] +
                expertise_score * self.weights['domain_expertise'] +
                availability_score * self.weights['availability'] +
                collaboration_score * self.weights['collaboration'] +
                preference_score * self.weights['user_preference']
            )
            
            # Calculate confidence and estimates
            confidence = self._calculate_confidence(agent, context, total_score)
            estimated_duration = self._estimate_duration(agent, context)
            success_probability = self._estimate_success_probability(agent, context)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(agent, context, {
                'keyword_score': keyword_score,
                'phase_score': phase_score,
                'success_score': success_score,
                'expertise_score': expertise_score
            })
            
            agent_score = AgentScore(
                agent_id=agent.id,
                agent_name=agent.name,
                total_score=total_score,
                keyword_match_score=keyword_score,
                phase_alignment_score=phase_score,
                recent_success_score=success_score,
                domain_expertise_score=expertise_score,
                availability_score=availability_score,
                collaboration_score=collaboration_score,
                user_preference_score=preference_score,
                confidence_level=confidence,
                reasoning=reasoning,
                estimated_duration_ms=estimated_duration,
                estimated_success_probability=success_probability
            )
            
            scored_agents.append(agent_score)
        
        return scored_agents
    
    def _calculate_keyword_score(self, agent: Agent, context: SelectionContext) -> float:
        """Calculate keyword matching score"""
        if not context.keywords:
            return 0.5  # Neutral score if no keywords
        
        # Check overlap between context keywords and agent keywords/specializations
        context_keywords = set(context.keywords)
        agent_keywords = set(agent.keywords + agent.specializations)
        
        if not agent_keywords:
            return 0.3  # Low score if agent has no keywords
        
        # Calculate Jaccard similarity
        intersection = len(context_keywords & agent_keywords)
        union = len(context_keywords | agent_keywords)
        
        if union == 0:
            return 0.5
        
        jaccard_score = intersection / union
        
        # Boost score for exact matches in specializations
        specialization_matches = len(set(context.keywords) & set(agent.specializations))
        specialization_boost = min(0.3, specialization_matches * 0.1)
        
        return min(1.0, jaccard_score + specialization_boost)
    
    def _calculate_phase_score(self, agent: Agent, context: SelectionContext) -> float:
        """Calculate phase alignment score"""
        if not context.project_phase:
            return 0.5
        
        # Phase mapping to agent specializations
        phase_specializations = {
            'planning': ['analysis', 'strategy', 'requirements', 'business-analyst'],
            'design': ['architecture', 'design', 'modeling', 'ui-ux'],
            'implementation': ['development', 'coding', 'backend', 'frontend'],
            'testing': ['testing', 'qa', 'automation', 'validation'],
            'deployment': ['devops', 'deployment', 'infrastructure', 'ci-cd'],
            'optimization': ['performance', 'optimization', 'monitoring'],
            'maintenance': ['maintenance', 'monitoring', 'support']
        }
        
        relevant_specializations = phase_specializations.get(context.project_phase, [])
        
        # Check if agent has relevant specializations for this phase
        agent_specializations = set(agent.specializations)
        phase_specializations_set = set(relevant_specializations)
        
        overlap = len(agent_specializations & phase_specializations_set)
        
        if overlap > 0:
            return min(1.0, overlap * 0.4 + 0.6)  # 0.6 base + up to 0.4 bonus
        
        return 0.4  # Lower score if no phase alignment
    
    def _calculate_success_score(self, agent: Agent) -> float:
        """Calculate recent success score"""
        if agent.total_executions == 0:
            return 0.6  # Neutral score for new agents
        
        success_rate = agent.success_count / agent.total_executions
        
        # Apply sigmoid function to smooth the score
        return 1 / (1 + math.exp(-10 * (success_rate - 0.5)))
    
    def _calculate_expertise_score(self, agent: Agent, context: SelectionContext) -> float:
        """Calculate domain expertise score"""
        base_expertise = min(1.0, agent.total_executions / 100)  # Scale up to 100 executions
        
        # Boost for relevant experience
        relevant_keywords = set(context.keywords) & set(agent.keywords + agent.specializations)
        relevance_boost = min(0.3, len(relevant_keywords) * 0.1)
        
        return min(1.0, base_expertise + relevance_boost)
    
    async def _calculate_availability_score(self, agent: Agent) -> float:
        """Calculate agent availability score"""
        if not agent.last_active_at:
            return 1.0  # Assume available if never used
        
        hours_since_active = (datetime.now() - agent.last_active_at.replace(tzinfo=None)).total_seconds() / 3600
        
        # Score based on time since last activity
        if hours_since_active < 1:
            return 0.7  # Recently used, might be busy
        elif hours_since_active < 24:
            return 0.9  # Used recently but likely available
        else:
            return 1.0  # Not used recently, fully available
    
    async def _calculate_collaboration_score(self, agent: Agent, context: SelectionContext) -> float:
        """Calculate collaboration effectiveness score"""
        # This would require querying collaboration patterns from the database
        # For now, return a base score
        return 0.8  # Placeholder - implement based on collaboration_patterns table
    
    def _calculate_user_preference_score(self, agent: Agent, context: SelectionContext) -> float:
        """Calculate user preference score"""
        preferences = context.user_preferences
        
        if not preferences:
            return 0.5
        
        score = 0.5
        
        # Check preferred models
        if 'preferred_models' in preferences:
            if agent.preferred_model in preferences['preferred_models']:
                score += 0.3
        
        # Check preferred agents
        if 'preferred_agents' in preferences:
            if agent.name in preferences['preferred_agents']:
                score += 0.4
        
        # Check avoided agents
        if 'avoided_agents' in preferences:
            if agent.name in preferences['avoided_agents']:
                score -= 0.5
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence(self, agent: Agent, context: SelectionContext, total_score: float) -> float:
        """Calculate confidence level for this selection"""
        # Base confidence on score
        base_confidence = total_score
        
        # Adjust based on agent experience
        experience_factor = min(1.0, agent.total_executions / 50)
        
        # Adjust based on keyword match quality
        keyword_factor = len(set(context.keywords) & set(agent.keywords)) / max(len(context.keywords), 1)
        
        return (base_confidence + experience_factor + keyword_factor) / 3
    
    def _estimate_duration(self, agent: Agent, context: SelectionContext) -> int:
        """Estimate execution duration in milliseconds"""
        if agent.avg_execution_time_ms > 0:
            # Use historical average with some variance based on query complexity
            base_duration = agent.avg_execution_time_ms
            
            # Adjust based on query complexity (rough heuristic)
            complexity_factor = 1.0 + (len(context.user_query) / 1000)  # Longer queries might take more time
            
            return int(base_duration * complexity_factor)
        
        # Default estimate for new agents
        return 30000  # 30 seconds default
    
    def _estimate_success_probability(self, agent: Agent, context: SelectionContext) -> float:
        """Estimate probability of successful execution"""
        if agent.total_executions > 0:
            historical_success = agent.success_count / agent.total_executions
        else:
            historical_success = 0.8  # Optimistic default for new agents
        
        # Adjust based on keyword match (better match = higher success probability)
        keyword_match = len(set(context.keywords) & set(agent.keywords + agent.specializations))
        keyword_boost = min(0.2, keyword_match * 0.05)
        
        return min(1.0, historical_success + keyword_boost)
    
    def _generate_reasoning(self, 
                          agent: Agent, 
                          context: SelectionContext,
                          scores: Dict[str, float]) -> List[str]:
        """Generate human-readable reasoning for agent selection"""
        reasoning = []
        
        # Keyword matching
        if scores['keyword_score'] > 0.7:
            keyword_matches = set(context.keywords) & set(agent.keywords + agent.specializations)
            reasoning.append(f"Strong keyword match: {', '.join(list(keyword_matches)[:3])}")
        elif scores['keyword_score'] > 0.5:
            reasoning.append("Moderate keyword alignment with query")
        else:
            reasoning.append("Limited keyword match")
        
        # Phase alignment
        if scores['phase_score'] > 0.7:
            reasoning.append(f"Well-suited for {context.project_phase} phase")
        
        # Success rate
        if agent.total_executions > 0:
            success_rate = agent.success_count / agent.total_executions
            if success_rate > 0.8:
                reasoning.append(f"High success rate: {success_rate:.1%}")
            elif success_rate < 0.6:
                reasoning.append(f"Lower success rate: {success_rate:.1%}")
        else:
            reasoning.append("New agent with no execution history")
        
        # Experience
        if agent.total_executions > 50:
            reasoning.append(f"Experienced agent with {agent.total_executions} executions")
        elif agent.total_executions > 10:
            reasoning.append(f"Moderate experience with {agent.total_executions} executions")
        
        # Specializations
        relevant_specializations = set(agent.specializations) & set(context.keywords)
        if relevant_specializations:
            reasoning.append(f"Specialized in: {', '.join(list(relevant_specializations)[:2])}")
        
        return reasoning
    
    async def _record_selection_pattern(self, context: SelectionContext, selected_agent: AgentScore):
        """Record selection pattern for machine learning"""
        try:
            # This would be used to improve future selections
            pattern_data = {
                'request_keywords': context.keywords,
                'file_types': context.file_types,
                'project_phase': context.project_phase,
                'time_of_day': context.time_context['hour'],
                'day_of_week': context.time_context['day_of_week'],
                'selected_agent_id': selected_agent.agent_id,
                'selection_reason': f"Score: {selected_agent.total_score:.2f}",
                'confidence_score': selected_agent.confidence_level
            }
            
            # Insert into agent_selection_patterns table
            # This could be used later for ML model training
            
        except Exception as e:
            self.logger.warning(f"Failed to record selection pattern: {e}")


# ========== FACTORY FUNCTIONS ==========

async def create_agent_selector() -> AgentSelectionEngine:
    """Create and initialize agent selection engine"""
    db = create_database_manager(async_mode=True)
    await db.initialize()
    return AgentSelectionEngine(db)


# ========== EXAMPLE USAGE ==========

async def example_agent_selection():
    """Example usage of agent selection engine"""
    
    # Create selector
    selector = await create_agent_selector()
    
    try:
        # Example 1: Simple query
        best_agent = await selector.select_best_agent(
            "I need help optimizing a PostgreSQL database schema for better performance"
        )
        
        if best_agent:
            print(f"Selected agent: {best_agent.agent_name}")
            print(f"Score: {best_agent.total_score:.2f}")
            print(f"Reasoning: {', '.join(best_agent.reasoning)}")
            print(f"Estimated duration: {best_agent.estimated_duration_ms}ms")
            print(f"Success probability: {best_agent.estimated_success_probability:.1%}")
        
        # Example 2: Get top recommendations
        recommendations = await selector.get_top_recommendations(
            "Create a React frontend component with TypeScript",
            count=3
        )
        
        print(f"\nTop {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.agent_name} (Score: {rec.total_score:.2f})")
        
    finally:
        await selector.db.close()


if __name__ == "__main__":
    asyncio.run(example_agent_selection())