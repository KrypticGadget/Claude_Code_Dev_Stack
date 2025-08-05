#!/usr/bin/env python3
"""
Agent Mention Parser Hook - Parse @agent- mentions from Claude Code input
Detects and routes messages to appropriate specialized agents
"""

import sys
import re
import json
from typing import List, Dict, Tuple, Optional
from base_hook import BaseHook


class AgentMentionParser(BaseHook):
    """Parse @agent- mentions and prepare routing information"""
    
    # Map of agent mentions to their full names and capabilities
    AGENT_MAP = {
        '@agent-orchestrator': {
            'name': 'Master Orchestrator',
            'description': 'Project coordination and planning',
            'triggers': ['project setup', 'architecture', 'planning']
        },
        '@agent-frontend': {
            'name': 'Frontend Architect',
            'description': 'UI/UX implementation and React development',
            'triggers': ['ui', 'frontend', 'react', 'component']
        },
        '@agent-backend': {
            'name': 'Backend Services Engineer',
            'description': 'API development and server-side logic',
            'triggers': ['api', 'backend', 'server', 'endpoint']
        },
        '@agent-database': {
            'name': 'Database Architect',
            'description': 'Database design and optimization',
            'triggers': ['database', 'schema', 'query', 'migration']
        },
        '@agent-devops': {
            'name': 'DevOps Engineer',
            'description': 'Deployment and infrastructure',
            'triggers': ['deploy', 'docker', 'ci/cd', 'infrastructure']
        },
        '@agent-security': {
            'name': 'Security Specialist',
            'description': 'Security analysis and implementation',
            'triggers': ['security', 'auth', 'encryption', 'vulnerability']
        },
        '@agent-testing': {
            'name': 'Testing Specialist',
            'description': 'Test implementation and quality assurance',
            'triggers': ['test', 'testing', 'qa', 'quality']
        },
        '@agent-performance': {
            'name': 'Performance Engineer',
            'description': 'Performance optimization and monitoring',
            'triggers': ['performance', 'optimize', 'speed', 'benchmark']
        },
        '@agent-mobile': {
            'name': 'Mobile Developer',
            'description': 'Mobile app development',
            'triggers': ['mobile', 'ios', 'android', 'react native']
        },
        '@agent-ai': {
            'name': 'AI/ML Engineer',
            'description': 'AI integration and machine learning',
            'triggers': ['ai', 'ml', 'machine learning', 'neural']
        },
        '@agent-cloud': {
            'name': 'Cloud Architect',
            'description': 'Cloud services and architecture',
            'triggers': ['aws', 'azure', 'gcp', 'cloud']
        },
        '@agent-data': {
            'name': 'Data Engineer',
            'description': 'Data pipelines and analytics',
            'triggers': ['etl', 'data pipeline', 'analytics', 'warehouse']
        },
        '@agent-blockchain': {
            'name': 'Blockchain Developer',
            'description': 'Blockchain and smart contracts',
            'triggers': ['blockchain', 'smart contract', 'web3', 'crypto']
        },
        '@agent-game': {
            'name': 'Game Developer',
            'description': 'Game development and engines',
            'triggers': ['game', 'unity', 'unreal', 'gaming']
        },
        '@agent-iot': {
            'name': 'IoT Engineer',
            'description': 'IoT devices and embedded systems',
            'triggers': ['iot', 'embedded', 'sensor', 'device']
        },
        '@agent-ar': {
            'name': 'AR/VR Developer',
            'description': 'Augmented and Virtual Reality',
            'triggers': ['ar', 'vr', 'augmented', 'virtual reality']
        },
        '@agent-desktop': {
            'name': 'Desktop App Developer',
            'description': 'Desktop application development',
            'triggers': ['desktop', 'electron', 'native app']
        },
        '@agent-embedded': {
            'name': 'Embedded Systems Engineer',
            'description': 'Embedded systems and firmware',
            'triggers': ['embedded', 'firmware', 'microcontroller']
        },
        '@agent-network': {
            'name': 'Network Engineer',
            'description': 'Network architecture and protocols',
            'triggers': ['network', 'tcp/ip', 'routing', 'protocol']
        },
        '@agent-graphics': {
            'name': 'Graphics Programmer',
            'description': 'Graphics programming and shaders',
            'triggers': ['graphics', 'shader', 'opengl', 'rendering']
        },
        '@agent-audio': {
            'name': 'Audio Engineer',
            'description': 'Audio processing and synthesis',
            'triggers': ['audio', 'sound', 'music', 'synthesis']
        },
        '@agent-video': {
            'name': 'Video Engineer',
            'description': 'Video processing and streaming',
            'triggers': ['video', 'streaming', 'encoding', 'codec']
        },
        '@agent-compiler': {
            'name': 'Compiler Engineer',
            'description': 'Compiler design and optimization',
            'triggers': ['compiler', 'parser', 'ast', 'optimization']
        },
        '@agent-os': {
            'name': 'OS Developer',
            'description': 'Operating system development',
            'triggers': ['os', 'kernel', 'driver', 'system']
        },
        '@agent-quantum': {
            'name': 'Quantum Computing Engineer',
            'description': 'Quantum algorithms and computing',
            'triggers': ['quantum', 'qubit', 'quantum computing']
        },
        '@agent-robotics': {
            'name': 'Robotics Engineer',
            'description': 'Robotics and automation',
            'triggers': ['robot', 'robotics', 'automation', 'ros']
        },
        '@agent-bioinformatics': {
            'name': 'Bioinformatics Engineer',
            'description': 'Computational biology and genomics',
            'triggers': ['bioinformatics', 'genomics', 'dna', 'protein']
        },
        '@agent-fintech': {
            'name': 'FinTech Developer',
            'description': 'Financial technology and trading',
            'triggers': ['fintech', 'trading', 'payment', 'banking']
        }
    }
    
    def __init__(self):
        super().__init__('agent_mention_parser')
    
    def run(self) -> int:
        """Parse input for agent mentions"""
        # Read input from stdin
        input_text = self.read_stdin()
        
        if not input_text:
            self.logger.debug("No input received")
            return 0
        
        # Parse mentions
        mentions = self.parse_mentions(input_text)
        
        # Detect implicit routing if no explicit mentions
        if not mentions:
            mentions = self.detect_implicit_routing(input_text)
        
        # Prepare routing information
        routing_info = self.prepare_routing(mentions, input_text)
        
        # Save routing information
        self.save_cache('current_routing', routing_info)
        
        # Output routing information
        self.write_stdout(json.dumps(routing_info, indent=2))
        
        self.logger.info(f"Parsed {len(mentions)} agent mentions", 
                        agents=[m['agent'] for m in mentions])
        
        return 0
    
    def parse_mentions(self, text: str) -> List[Dict[str, any]]:
        """Extract explicit @agent- mentions from text"""
        mentions = []
        
        # Pattern to match @agent-xxx
        pattern = r'(@agent-[\w-]+)'
        
        for match in re.finditer(pattern, text):
            mention = match.group(1).lower()
            
            if mention in self.AGENT_MAP:
                mentions.append({
                    'agent': mention,
                    'position': match.start(),
                    'context': self._extract_context(text, match.start(), match.end())
                })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_mentions = []
        for m in mentions:
            if m['agent'] not in seen:
                seen.add(m['agent'])
                unique_mentions.append(m)
        
        return unique_mentions
    
    def detect_implicit_routing(self, text: str) -> List[Dict[str, any]]:
        """Detect which agents should handle request based on content"""
        text_lower = text.lower()
        detected = []
        
        # Check each agent's triggers
        for agent, info in self.AGENT_MAP.items():
            for trigger in info['triggers']:
                if trigger in text_lower:
                    detected.append({
                        'agent': agent,
                        'position': 0,
                        'context': text[:200],
                        'trigger': trigger,
                        'confidence': self._calculate_confidence(text_lower, info['triggers'])
                    })
                    break
        
        # Sort by confidence and take top matches
        detected.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # If multiple high-confidence matches, include orchestrator
        if len(detected) > 2 and not any(d['agent'] == '@agent-orchestrator' for d in detected):
            detected.insert(0, {
                'agent': '@agent-orchestrator',
                'position': 0,
                'context': 'Multiple agents needed',
                'confidence': 1.0
            })
        
        return detected[:3]  # Limit to top 3 agents
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 100) -> str:
        """Extract context around a mention"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        context = text[context_start:context_end]
        
        # Clean up context
        context = ' '.join(context.split())
        
        return context
    
    def _calculate_confidence(self, text: str, triggers: List[str]) -> float:
        """Calculate confidence score for implicit routing"""
        matches = sum(1 for trigger in triggers if trigger in text)
        return min(matches / len(triggers), 1.0)
    
    def prepare_routing(self, mentions: List[Dict[str, any]], full_text: str) -> Dict[str, any]:
        """Prepare complete routing information"""
        routing = {
            'timestamp': self.context.timestamp.isoformat(),
            'session_id': self.context.session_id,
            'input_length': len(full_text),
            'agents': [],
            'primary_agent': None,
            'execution_order': [],
            'metadata': {}
        }
        
        # Process each mention
        for mention in mentions:
            agent_info = self.AGENT_MAP.get(mention['agent'], {})
            
            agent_data = {
                'id': mention['agent'],
                'name': agent_info.get('name', 'Unknown Agent'),
                'description': agent_info.get('description', ''),
                'context': mention['context'],
                'confidence': mention.get('confidence', 1.0),
                'trigger': mention.get('trigger', 'explicit')
            }
            
            routing['agents'].append(agent_data)
        
        # Determine primary agent and execution order
        if routing['agents']:
            # Orchestrator always goes first if present
            if any(a['id'] == '@agent-orchestrator' for a in routing['agents']):
                routing['primary_agent'] = '@agent-orchestrator'
                routing['execution_order'] = ['@agent-orchestrator'] + [
                    a['id'] for a in routing['agents'] if a['id'] != '@agent-orchestrator'
                ]
            else:
                # Highest confidence agent is primary
                routing['agents'].sort(key=lambda x: x['confidence'], reverse=True)
                routing['primary_agent'] = routing['agents'][0]['id']
                routing['execution_order'] = [a['id'] for a in routing['agents']]
        
        # Add metadata
        routing['metadata'] = {
            'explicit_mentions': sum(1 for m in mentions if 'trigger' not in m),
            'implicit_routing': sum(1 for m in mentions if 'trigger' in m),
            'requires_orchestration': len(routing['agents']) > 1,
            'project_dir': str(self.env.project_dir),
            'hook_phase': self.context.hook_phase
        }
        
        return routing
    
    def validate_agent_availability(self, agent_id: str) -> bool:
        """Check if an agent is available and configured"""
        # Check if agent exists in map
        if agent_id not in self.AGENT_MAP:
            return False
        
        # Check if agent is enabled in config
        agent_config = self.config.get('agents', {}).get(agent_id, {})
        if not agent_config.get('enabled', True):
            return False
        
        # Additional validation could go here
        return True


def main():
    """Main entry point"""
    parser = AgentMentionParser()
    return parser.safe_run()


if __name__ == "__main__":
    sys.exit(main())