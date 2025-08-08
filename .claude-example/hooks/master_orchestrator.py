#!/usr/bin/env python3
"""
Master Orchestrator Hook - The Brain of the Ultimate Claude Code Dev Stack
Coordinates all subsystems: audio, agents, MCP, meta-prompting, and phase detection
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import platform
import queue
import threading

class UltimateClaudeOrchestrator:
    """
    Complete orchestration system for Claude Code Dev Stack
    Combines audio, agents, MCP, and meta-prompting
    """
    
    def __init__(self):
        # System components
        self.audio_system = EnhancedAudioSystem()
        self.agent_router = SmartAgentRouter()
        self.mcp_orchestrator = MCPServiceOrchestrator()
        self.meta_prompter = MetaPromptTransformer()
        self.phase_detector = DevelopmentPhaseDetector()
        
        # State management (memory only, no persistence)
        self.current_phase = "initialization"
        self.active_agents = []
        self.pending_inputs = []
        self.execution_history = []  # Last 20 only
        self.last_response_type = None
        
    def process_hook_event(self, event_type: str, data: Dict) -> Dict:
        """
        Main hook entry point for all events
        """
        result = {
            'processed': True,
            'audio_triggers': [],
            'suggestions': [],
            'transformations': []
        }
        
        if event_type == 'user_prompt':
            return self.process_user_input(data.get('prompt', ''))
        elif event_type == 'claude_response':
            return self.process_claude_response(data.get('response', ''))
        elif event_type == 'agent_activation':
            return self.process_agent_activation(data.get('agent', ''))
        elif event_type == 'mcp_request':
            return self.process_mcp_request(data.get('service', ''))
        
        return result
    
    def process_user_input(self, user_input: str) -> Dict:
        """
        Process user input with complete orchestration
        """
        result = {
            'original_input': user_input,
            'transformed_prompt': None,
            'agents': [],
            'mcp_services': [],
            'audio_triggers': [],
            'execution_plan': [],
            'optimizations': [],
            'suggestions': []
        }
        
        # 1. Meta-prompting transformation
        if self.needs_meta_prompting(user_input):
            transformed = self.meta_prompter.transform(user_input)
            result['transformed_prompt'] = transformed['prompt']
            result['optimizations'].append("Meta-prompt transformation applied")
            self.audio_system.play("meta_prompt_transforming")
            result['audio_triggers'].append("meta_prompt_transforming")
            user_input = transformed['prompt']
        
        # 2. Phase detection
        phase = self.phase_detector.detect(user_input)
        if phase and phase != self.current_phase:
            result['audio_triggers'].append(phase)
            self.audio_system.play(phase)
            self.current_phase = phase
        
        # 3. Agent routing
        agent_result = self.agent_router.route(user_input)
        result['agents'] = agent_result['agents']
        
        if agent_result['team_suggested']:
            result['suggestions'].append({
                'type': 'team',
                'agents': agent_result['team'],
                'message': f"Consider adding: {', '.join(['@' + a for a in agent_result['team']])}"
            })
            self.audio_system.play("agent_team_suggested")
            result['audio_triggers'].append("agent_team_suggested")
        
        # 4. MCP service detection
        mcp_services = self.mcp_orchestrator.detect_services(user_input, result['agents'])
        result['mcp_services'] = mcp_services
        
        if mcp_services:
            self.audio_system.play("mcp_service_starting")
            result['audio_triggers'].append("mcp_service_starting")
        
        # 5. Execution planning
        execution_plan = self.create_execution_plan(result)
        result['execution_plan'] = execution_plan['steps']
        result['optimizations'].extend(execution_plan['optimizations'])
        
        # 6. Play orchestrator engaged if complex
        if len(result['agents']) > 2 or len(result['mcp_services']) > 0:
            self.audio_system.play("orchestrator_engaged")
            result['audio_triggers'].append("orchestrator_engaged")
        
        # 7. Track execution
        self.track_execution(result)
        
        return result
    
    def process_claude_response(self, response: str) -> Dict:
        """
        Process Claude's responses for triggers and state
        """
        result = {
            'audio_triggers': [],
            'detected_patterns': []
        }
        
        # Input detection
        input_type = self.detect_input_needed(response)
        if input_type and input_type != self.last_response_type:
            result['audio_triggers'].append(input_type)
            self.audio_system.play(input_type)
            self.pending_inputs.append(input_type)
            self.last_response_type = input_type
            result['detected_patterns'].append(f"Input needed: {input_type}")
        
        # Phase completion detection
        phase = self.phase_detector.detect(response)
        if phase and phase != self.current_phase:
            result['audio_triggers'].append(phase)
            self.audio_system.play(phase)
            self.current_phase = phase
            result['detected_patterns'].append(f"Phase: {phase}")
        
        # Agent handoff detection
        if self.detect_agent_handoff(response):
            result['audio_triggers'].append("handoff_occurring")
            self.audio_system.play("handoff_occurring")
            result['detected_patterns'].append("Agent handoff detected")
        
        # Success/completion patterns
        if self.detect_completion(response):
            result['audio_triggers'].append("pipeline_complete")
            self.audio_system.play("pipeline_complete")
            result['detected_patterns'].append("Task completed")
        
        return result
    
    def process_agent_activation(self, agent: str) -> Dict:
        """
        Process agent activation events
        """
        self.active_agents.append(agent)
        self.audio_system.play("agent_activated")
        
        return {
            'audio_triggers': ["agent_activated"],
            'active_agents': self.active_agents[-5:]  # Last 5
        }
    
    def process_mcp_request(self, service: str) -> Dict:
        """
        Process MCP service requests
        """
        self.audio_system.play("mcp_service_starting")
        
        return {
            'audio_triggers': ["mcp_service_starting"],
            'service': service
        }
    
    def needs_meta_prompting(self, user_input: str) -> bool:
        """
        Detect if input needs transformation
        """
        indicators = [
            r'build.*(?:app|system|feature)',
            r'create.*(?:application|project|component)',
            r'help.*(?:me|with|implement)',
            r'how.*(?:should|can|do).*i',
            r'design.*(?:architecture|system|database)',
            r'implement.*(?:feature|functionality|system)',
            r'optimize.*(?:performance|code|system)',
            r'set.*up.*(?:project|environment|system)',
            r'need.*(?:to|help|assistance)'
        ]
        
        input_lower = user_input.lower()
        
        # Check patterns
        for pattern in indicators:
            if re.search(pattern, input_lower):
                return True
        
        # Check if too vague
        word_count = len(user_input.split())
        if word_count < 5 and '?' in user_input:
            return True
        
        # Check if missing specifics
        if word_count < 10 and not any(c in user_input for c in ['@', '/', '#']):
            return True
            
        return False
    
    def create_execution_plan(self, result: Dict) -> Dict:
        """
        Create optimal execution plan
        """
        plan = {'steps': [], 'optimizations': []}
        
        # Phase 1: Research/Data gathering
        if result['mcp_services']:
            if 'brave_search' in result['mcp_services']:
                plan['steps'].append({
                    'phase': 1,
                    'type': 'mcp',
                    'service': 'brave_search',
                    'action': 'Research and gather information'
                })
        
        # Phase 2: Planning/Architecture
        architecture_agents = ['system-architect', 'frontend-architect', 'database-architect']
        arch_agents = [a for a in result['agents'] if a in architecture_agents]
        if arch_agents:
            plan['steps'].append({
                'phase': 2,
                'type': 'agents',
                'agents': arch_agents,
                'action': 'Design and architecture',
                'parallel': True
            })
            plan['optimizations'].append(f"Parallel architecture: {', '.join(arch_agents)}")
        
        # Phase 3: Implementation
        impl_agents = ['backend-engineer', 'frontend-engineer', 'api-integration']
        implementation = [a for a in result['agents'] if a in impl_agents]
        if implementation:
            plan['steps'].append({
                'phase': 3,
                'type': 'agents',
                'agents': implementation,
                'action': 'Implementation',
                'parallel': len(implementation) > 1
            })
            if len(implementation) > 1:
                plan['optimizations'].append("Parallel implementation")
                self.audio_system.play("parallel_execution")
        
        # Phase 4: Testing
        test_agents = ['testing-automation', 'quality-assurance']
        testing = [a for a in result['agents'] if a in test_agents]
        if testing:
            plan['steps'].append({
                'phase': 4,
                'type': 'agents',
                'agents': testing,
                'action': 'Testing and QA'
            })
        
        # Phase 5: Documentation
        if 'obsidian' in result['mcp_services'] or 'documentation' in result['agents']:
            plan['steps'].append({
                'phase': 5,
                'type': 'mixed',
                'action': 'Documentation and knowledge capture'
            })
        
        return plan
    
    def detect_input_needed(self, response: str) -> Optional[str]:
        """
        Detect type of input Claude needs
        """
        patterns = {
            'yes_no_question': [
                r'(?:would|should|shall|can|may).*\?',
                r'yes\s*(?:or|\/)\s*no',
                r'\(y\/n\)',
                r'confirm\?'
            ],
            'multiple_choice': [
                r'\b\d+\.\s+\w+',
                r'(?:choose|select).*(?:option|from)',
                r'which.*(?:one|option)',
                r'\[1\].*\[2\]'
            ],
            'awaiting_confirmation': [
                r'proceed\?',
                r'continue\?',
                r'shall i',
                r'is this (?:correct|ok|fine)'
            ],
            'clarification_needed': [
                r'(?:could|can) you (?:clarify|explain|provide)',
                r'not (?:clear|sure)',
                r'what (?:do you mean|exactly)',
                r'please (?:specify|elaborate)'
            ],
            'permission_required': [
                r'(?:may|can) i',
                r'permission to',
                r'allow me to',
                r'authorized to'
            ],
            'awaiting_details': [
                r'(?:provide|need|require).*(?:details|information|specifics)',
                r'what.*(?:specifically|exactly)',
                r'which.*(?:specific|particular)'
            ],
            'awaiting_selection': [
                r'please (?:select|choose|pick)',
                r'which.*would you (?:prefer|like)',
                r'make a selection'
            ]
        }
        
        response_lower = response.lower()
        
        for input_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, response_lower):
                    return input_type
        
        # Generic question detection
        if response.rstrip().endswith('?'):
            return 'awaiting_response'
        
        return None
    
    def detect_agent_handoff(self, response: str) -> bool:
        """
        Detect agent handoffs
        """
        patterns = [
            r'passing.*to.*@',
            r'transferring.*(?:to|control)',
            r'handing.*off',
            r'next.*agent',
            r'@\w+.*will.*(?:continue|handle|take)',
            r'switching.*to.*@'
        ]
        
        response_lower = response.lower()
        return any(re.search(pattern, response_lower) for pattern in patterns)
    
    def detect_completion(self, response: str) -> bool:
        """
        Detect task completion
        """
        patterns = [
            r'(?:task|implementation|setup|configuration).*complete',
            r'successfully.*(?:created|implemented|configured|deployed)',
            r'finished.*(?:setting up|implementing|creating)',
            r'all.*(?:done|complete|ready)',
            r'everything.*(?:set up|configured|ready)'
        ]
        
        response_lower = response.lower()
        return any(re.search(pattern, response_lower) for pattern in patterns)
    
    def track_execution(self, result: Dict):
        """
        Track execution history (bounded)
        """
        execution = {
            'timestamp': datetime.now().isoformat(),
            'agents': result['agents'][:3],
            'mcp': result['mcp_services'][:2],
            'optimizations': len(result['optimizations']),
            'phase': self.current_phase
        }
        
        self.execution_history.append(execution)
        self.execution_history = self.execution_history[-20:]  # Keep last 20


class EnhancedAudioSystem:
    """
    Audio playback system with queue and cooldown
    """
    
    def __init__(self):
        self.audio_dir = Path(__file__).parent.parent / "audio"
        self.play_queue = queue.Queue()
        self.cooldown = {}
        self.min_interval = 2.0  # seconds
        
        # Start player thread
        self.player_thread = threading.Thread(target=self._player_loop, daemon=True)
        self.player_thread.start()
    
    def play(self, sound_name: str):
        """
        Queue sound for playback
        """
        # Check cooldown
        now = time.time()
        if sound_name in self.cooldown:
            if now - self.cooldown[sound_name] < self.min_interval:
                return
        
        self.cooldown[sound_name] = now
        self.play_queue.put(sound_name)
    
    def _player_loop(self):
        """
        Background player thread
        """
        while True:
            try:
                sound_name = self.play_queue.get(timeout=1)
                self._play_sound(sound_name)
            except queue.Empty:
                continue
            except Exception:
                pass  # Fail silently
    
    def _play_sound(self, sound_name: str):
        """
        Play sound file
        """
        sound_file = self.audio_dir / f"{sound_name}.wav"
        if not sound_file.exists():
            return
        
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{sound_file}').PlaySync()"],
                    capture_output=True,
                    timeout=5
                )
            elif system == "Darwin":
                subprocess.run(["afplay", str(sound_file)], capture_output=True, timeout=5)
            else:
                subprocess.run(["paplay", str(sound_file)], capture_output=True, timeout=5)
        except:
            pass


class SmartAgentRouter:
    """
    Intelligent agent routing with team suggestions
    """
    
    def __init__(self):
        self.agent_matrix = {
            'master-orchestrator': {
                'triggers': ['orchestrate', 'coordinate', 'manage project'],
                'team': ['project-manager', 'system-architect']
            },
            'system-architect': {
                'triggers': ['architecture', 'system design', 'scalability', 'infrastructure'],
                'team': ['database-architect', 'security-architect', 'devops-engineer']
            },
            'backend-engineer': {
                'triggers': ['backend', 'api', 'server', 'endpoint', 'service'],
                'team': ['database-architect', 'api-integration-specialist']
            },
            'frontend-architect': {
                'triggers': ['frontend', 'ui', 'user interface', 'react', 'vue', 'angular'],
                'team': ['ui-ux-designer', 'frontend-mockup', 'production-frontend']
            },
            'database-architect': {
                'triggers': ['database', 'schema', 'sql', 'query', 'migration'],
                'team': ['backend-engineer', 'performance-optimization']
            },
            'security-architect': {
                'triggers': ['security', 'auth', 'authentication', 'encryption', 'oauth'],
                'team': ['backend-engineer', 'devops-engineer']
            },
            'devops-engineer': {
                'triggers': ['deploy', 'deployment', 'ci/cd', 'docker', 'kubernetes', 'pipeline'],
                'team': ['security-architect', 'script-automation']
            },
            'testing-automation': {
                'triggers': ['test', 'testing', 'qa', 'quality', 'coverage'],
                'team': ['quality-assurance-lead', 'performance-optimization']
            },
            'prompt-engineer': {
                'triggers': ['prompt', 'optimize prompt', 'prompt engineering', 'meta'],
                'team': ['development-prompt', 'business-analyst']
            },
            'ui-ux-designer': {
                'triggers': ['design', 'ux', 'ui design', 'wireframe', 'mockup', 'prototype'],
                'team': ['frontend-architect', 'frontend-mockup']
            },
            'api-integration-specialist': {
                'triggers': ['integration', 'webhook', 'third-party', 'external api'],
                'team': ['backend-services', 'middleware-specialist']
            },
            'mobile-developer': {
                'triggers': ['mobile', 'ios', 'android', 'react native', 'flutter'],
                'team': ['ui-ux-designer', 'backend-services']
            },
            'performance-optimization': {
                'triggers': ['performance', 'optimization', 'speed', 'profiling', 'caching'],
                'team': ['database-architect', 'devops-engineer']
            },
            'technical-documentation': {
                'triggers': ['documentation', 'docs', 'readme', 'guide', 'manual'],
                'team': ['technical-specifications', 'business-analyst']
            }
        }
    
    def route(self, user_input: str) -> Dict:
        """
        Route to appropriate agents with team suggestions
        """
        input_lower = user_input.lower()
        detected_agents = []
        suggested_team = set()
        
        # Check for explicit @ mentions
        explicit = re.findall(r'@([\w-]+)', user_input)
        if explicit:
            detected_agents.extend(explicit)
            # Add team for explicit agents
            for agent in explicit:
                if agent in self.agent_matrix:
                    suggested_team.update(self.agent_matrix[agent]['team'])
        
        # Auto-detect based on triggers
        for agent, config in self.agent_matrix.items():
            if agent not in detected_agents:
                for trigger in config['triggers']:
                    if trigger in input_lower:
                        detected_agents.append(agent)
                        suggested_team.update(config['team'])
                        break
        
        # Remove already selected from suggestions
        suggested_team = list(suggested_team - set(detected_agents))
        
        return {
            'agents': detected_agents[:5],  # Max 5 primary
            'team': suggested_team[:3],     # Max 3 suggestions
            'team_suggested': len(suggested_team) > 0
        }


class MCPServiceOrchestrator:
    """
    MCP service detection and orchestration
    """
    
    def detect_services(self, user_input: str, agents: List[str]) -> List[str]:
        """
        Detect needed MCP services
        """
        services = []
        input_lower = user_input.lower()
        
        # Direct keyword triggers
        service_triggers = {
            'brave_search': ['search', 'research', 'find', 'current', 'latest', 'trends'],
            'playwright': ['browser', 'automate', 'e2e', 'test browser', 'web scraping'],
            'obsidian': ['document', 'note', 'knowledge', 'wiki', 'markdown']
        }
        
        for service, triggers in service_triggers.items():
            if any(trigger in input_lower for trigger in triggers):
                services.append(service)
        
        # Agent-based triggers
        agent_services = {
            'testing-automation': 'playwright',
            'documentation-specialist': 'obsidian',
            'technical-documentation': 'obsidian',
            'business-analyst': 'brave_search',
            'prompt-engineer': 'brave_search'
        }
        
        for agent in agents:
            if agent in agent_services:
                services.append(agent_services[agent])
        
        return list(set(services))


class MetaPromptTransformer:
    """
    Transform vague prompts into actionable instructions
    """
    
    def transform(self, user_input: str) -> Dict:
        """
        Transform input using meta-prompting
        """
        is_question = '?' in user_input
        is_request = any(word in user_input.lower() for word in ['create', 'build', 'make', 'implement', 'add', 'setup'])
        is_vague = len(user_input.split()) < 10
        
        if is_vague and is_question:
            # Transform vague question
            enhanced = f"""
[ENHANCED REQUEST]
Original: {user_input}

@prompt-engineer @business-analyst
Analyze this request and provide:
1. Clarified requirements
2. Suggested technical approach
3. Required agents and tools
4. Implementation steps
"""
        elif is_request:
            # Transform request to action plan
            project_name = self.extract_project_context(user_input)
            enhanced = f"""
[PROJECT: {project_name}]
REQUEST: {user_input}

@master-orchestrator @system-architect
Execute comprehensive development plan:
- Define clear phases
- Identify required agents
- Create execution timeline
- Specify success criteria
"""
        else:
            enhanced = user_input
        
        return {'prompt': enhanced, 'type': 'meta-prompted'}
    
    def extract_project_context(self, user_input: str) -> str:
        """
        Extract project name/context
        """
        words = user_input.split()
        
        # Look for key verbs and their objects
        key_verbs = ['build', 'create', 'make', 'implement', 'add', 'develop']
        for i, word in enumerate(words):
            if word.lower() in key_verbs and i + 1 < len(words):
                # Take next 2-3 words as project name
                end = min(i + 4, len(words))
                return ' '.join(words[i+1:end]).strip('.,!?')
        
        return "Development Task"


class DevelopmentPhaseDetector:
    """
    Detect current development phase from text
    """
    
    def detect(self, text: str) -> Optional[str]:
        """
        Detect development phase
        """
        phases = {
            'project_created': [r'project.*(?:created|initialized)', r'initialized.*project', r'created.*structure'],
            'dependencies_installed': [r'dependencies.*installed', r'packages.*installed', r'npm install.*complete'],
            'environment_ready': [r'environment.*(?:ready|setup|configured)', r'setup.*complete'],
            'requirements_gathered': [r'requirements.*(?:complete|gathered|analyzed)', r'specs.*ready'],
            'architecture_designed': [r'architecture.*(?:designed|complete)', r'system.*design.*complete'],
            'database_modeled': [r'database.*(?:schema|model).*(?:created|designed|complete)'],
            'backend_complete': [r'backend.*(?:complete|ready|implemented)', r'api.*(?:ready|complete)'],
            'frontend_complete': [r'frontend.*(?:complete|ready|implemented)', r'ui.*(?:ready|complete)'],
            'api_integrated': [r'api.*integrated', r'integration.*(?:complete|successful)'],
            'auth_implemented': [r'auth(?:entication)?.*(?:implemented|complete|ready)'],
            'unit_tests_pass': [r'unit tests.*pass', r'tests.*passing', r'all tests.*pass'],
            'build_successful': [r'build.*(?:successful|complete)', r'compilation.*complete'],
            'deploy_complete': [r'deploy.*(?:complete|successful)', r'deployment.*(?:complete|successful)'],
            'milestone_complete': [r'milestone.*(?:achieved|complete)', r'phase.*complete']
        }
        
        text_lower = text.lower()
        
        for phase, patterns in phases.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return phase
        
        return None


# Hook integration function
def process_hook(event_type: str, data: Dict) -> Dict:
    """
    Main hook entry point
    """
    global orchestrator
    
    try:
        if 'orchestrator' not in globals():
            orchestrator = UltimateClaudeOrchestrator()
        
        return orchestrator.process_hook_event(event_type, data)
    except Exception:
        # Fail silently
        return {'processed': False}


# Export for hook system
__all__ = ['process_hook', 'UltimateClaudeOrchestrator']