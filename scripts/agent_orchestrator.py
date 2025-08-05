#!/usr/bin/env python3
"""
Agent Orchestrator Hook - Route requests to appropriate specialized agents
Manages agent coordination and execution flow
"""

import sys
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from base_hook import BaseHook


class AgentOrchestrator(BaseHook):
    """Orchestrate and coordinate agent executions"""
    
    # Agent definitions with their capabilities and triggers
    AGENT_REGISTRY = {
        '@agent-orchestrator': {
            'name': 'Master Orchestrator',
            'prompt_file': 'agent_master_orchestrator.md',
            'capabilities': ['planning', 'coordination', 'architecture'],
            'cost_multiplier': 1.0
        },
        '@agent-frontend': {
            'name': 'Frontend Architect',
            'prompt_file': 'agent_frontend_architect.md',
            'capabilities': ['ui', 'react', 'vue', 'angular', 'components'],
            'cost_multiplier': 0.8
        },
        '@agent-backend': {
            'name': 'Backend Services Engineer',
            'prompt_file': 'agent_backend_engineer.md',
            'capabilities': ['api', 'server', 'microservices', 'integration'],
            'cost_multiplier': 0.8
        },
        '@agent-database': {
            'name': 'Database Architect',
            'prompt_file': 'agent_database_architect.md',
            'capabilities': ['schema', 'optimization', 'migrations', 'queries'],
            'cost_multiplier': 0.7
        },
        '@agent-devops': {
            'name': 'DevOps Engineer',
            'prompt_file': 'agent_devops_engineer.md',
            'capabilities': ['deployment', 'ci/cd', 'docker', 'kubernetes'],
            'cost_multiplier': 0.7
        },
        '@agent-security': {
            'name': 'Security Specialist',
            'prompt_file': 'agent_security_specialist.md',
            'capabilities': ['authentication', 'encryption', 'vulnerabilities'],
            'cost_multiplier': 0.9
        },
        '@agent-testing': {
            'name': 'Testing Specialist',
            'prompt_file': 'agent_testing_specialist.md',
            'capabilities': ['unit-tests', 'integration', 'e2e', 'tdd'],
            'cost_multiplier': 0.6
        },
        '@agent-performance': {
            'name': 'Performance Engineer',
            'prompt_file': 'agent_performance_engineer.md',
            'capabilities': ['optimization', 'profiling', 'caching', 'scaling'],
            'cost_multiplier': 0.8
        }
    }
    
    def __init__(self):
        super().__init__('agent_orchestrator')
        self.execution_history = []
    
    def run(self) -> int:
        """Main orchestration logic"""
        # Read routing information
        routing_data = self._load_routing_data()
        
        if not routing_data or not routing_data.get('agents'):
            self.logger.info("No agents to orchestrate")
            return 0
        
        # Load planning decision if available
        planning_decision = self.load_cache('planning_decision')
        
        # Create execution plan
        execution_plan = self._create_execution_plan(routing_data, planning_decision)
        
        # Execute agents according to plan
        results = self._execute_plan(execution_plan)
        
        # Aggregate results
        final_output = self._aggregate_results(results)
        
        # Save execution history
        self._save_execution_history(execution_plan, results)
        
        # Output final results
        self.write_stdout(json.dumps(final_output, indent=2))
        
        self.logger.info("Orchestration completed", 
                        agents_executed=len(results),
                        success=final_output['success'])
        
        return 0
    
    def _load_routing_data(self) -> Dict[str, Any]:
        """Load routing data from cache or stdin"""
        # Try cache first
        cached_routing = self.load_cache('current_routing')
        if cached_routing:
            return cached_routing
        
        # Otherwise read from stdin
        input_text = self.read_stdin()
        if input_text:
            try:
                return json.loads(input_text)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse routing data")
        
        return {}
    
    def _create_execution_plan(self, routing_data: Dict[str, Any], 
                              planning_decision: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed execution plan"""
        plan = {
            'session_id': routing_data.get('session_id', self.context.session_id),
            'timestamp': datetime.now().isoformat(),
            'agents': [],
            'execution_mode': 'sequential',  # or 'parallel'
            'dependencies': {},
            'context': {}
        }
        
        # Determine execution order
        execution_order = routing_data.get('execution_order', [])
        
        # If planning is needed, ensure orchestrator runs first
        if planning_decision and planning_decision.get('needs_planning'):
            if '@agent-orchestrator' not in execution_order:
                execution_order.insert(0, '@agent-orchestrator')
            plan['planning_type'] = planning_decision.get('planning_type')
        
        # Build agent execution entries
        for agent_id in execution_order:
            if agent_id not in self.AGENT_REGISTRY:
                self.logger.warning(f"Unknown agent: {agent_id}")
                continue
            
            agent_info = self.AGENT_REGISTRY[agent_id]
            agent_data = next((a for a in routing_data['agents'] if a['id'] == agent_id), {})
            
            plan['agents'].append({
                'id': agent_id,
                'name': agent_info['name'],
                'prompt_file': agent_info['prompt_file'],
                'context': agent_data.get('context', ''),
                'confidence': agent_data.get('confidence', 1.0),
                'cost_multiplier': agent_info['cost_multiplier'],
                'dependencies': self._get_agent_dependencies(agent_id, execution_order)
            })
        
        # Determine if parallel execution is possible
        if self._can_parallelize(plan['agents']):
            plan['execution_mode'] = 'parallel'
        
        return plan
    
    def _get_agent_dependencies(self, agent_id: str, execution_order: List[str]) -> List[str]:
        """Determine agent dependencies"""
        dependencies = []
        
        # Orchestrator has no dependencies
        if agent_id == '@agent-orchestrator':
            return []
        
        # If orchestrator is in the plan, all others depend on it
        if '@agent-orchestrator' in execution_order:
            dependencies.append('@agent-orchestrator')
        
        # Add specific dependencies based on agent type
        dependency_rules = {
            '@agent-frontend': ['@agent-backend'],  # Frontend may need API specs
            '@agent-testing': ['@agent-frontend', '@agent-backend'],  # Tests need implementation
            '@agent-devops': ['@agent-backend', '@agent-frontend'],  # Deploy needs code
            '@agent-performance': ['@agent-backend', '@agent-frontend']  # Optimize existing code
        }
        
        if agent_id in dependency_rules:
            for dep in dependency_rules[agent_id]:
                if dep in execution_order and dep not in dependencies:
                    dependencies.append(dep)
        
        return dependencies
    
    def _can_parallelize(self, agents: List[Dict[str, Any]]) -> bool:
        """Check if agents can run in parallel"""
        # Simple check: if no dependencies between agents, can parallelize
        for agent in agents:
            if agent['dependencies']:
                return False
        return len(agents) > 1
    
    def _execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute agents according to plan"""
        results = []
        context = {}
        
        if plan['execution_mode'] == 'parallel':
            # Execute agents in parallel
            results = self._execute_parallel(plan['agents'], context)
        else:
            # Execute agents sequentially
            for agent in plan['agents']:
                result = self._execute_agent(agent, context)
                results.append(result)
                
                # Update context with agent results
                if result['success']:
                    context[agent['id']] = result.get('output', {})
        
        return results
    
    def _execute_agent(self, agent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent"""
        start_time = datetime.now()
        
        result = {
            'agent_id': agent['id'],
            'agent_name': agent['name'],
            'started_at': start_time.isoformat(),
            'success': False,
            'error': None,
            'output': {},
            'metrics': {}
        }
        
        try:
            # Prepare agent prompt
            prompt = self._prepare_agent_prompt(agent, context)
            
            # Log agent execution
            self.logger.info(f"Executing agent: {agent['name']}")
            
            # Simulate agent execution (in real implementation, this would call Claude)
            # For now, we'll create a mock response
            agent_output = self._simulate_agent_execution(agent, prompt, context)
            
            # Parse agent output
            result['output'] = agent_output
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {agent['name']}", exc_info=True)
            result['error'] = str(e)
        
        # Calculate metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result['completed_at'] = end_time.isoformat()
        result['metrics'] = {
            'duration_seconds': duration,
            'estimated_cost': duration * agent['cost_multiplier'] * 0.001,  # Mock cost calculation
            'tokens_used': len(prompt.split()) * 4  # Rough estimate
        }
        
        return result
    
    def _prepare_agent_prompt(self, agent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Prepare prompt for agent execution"""
        # Load agent prompt template
        prompt_file = self.env.claude_home / 'prompts' / agent['prompt_file']
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        else:
            base_prompt = f"You are {agent['name']}. Please help with the following request:"
        
        # Add context from previous agents
        context_section = ""
        if context:
            context_section = "\n\n## Context from Previous Agents:\n"
            for agent_id, agent_context in context.items():
                context_section += f"\n### {agent_id}:\n{json.dumps(agent_context, indent=2)}\n"
        
        # Add specific request context
        request_section = f"\n\n## Request Context:\n{agent['context']}\n"
        
        # Combine all sections
        full_prompt = base_prompt + context_section + request_section
        
        return full_prompt
    
    def _simulate_agent_execution(self, agent: Dict[str, Any], prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent execution (placeholder for actual implementation)"""
        # In real implementation, this would:
        # 1. Call Claude API with the agent prompt
        # 2. Process the response
        # 3. Extract structured data
        
        # For now, return mock data based on agent type
        mock_responses = {
            '@agent-orchestrator': {
                'plan': 'Created comprehensive project plan',
                'architecture': 'Defined system architecture',
                'next_steps': ['Setup project structure', 'Define API contracts', 'Create database schema']
            },
            '@agent-frontend': {
                'components': ['Header', 'Dashboard', 'UserProfile'],
                'framework': 'React with TypeScript',
                'styling': 'Tailwind CSS'
            },
            '@agent-backend': {
                'api_endpoints': ['/api/users', '/api/auth', '/api/data'],
                'framework': 'Express.js',
                'database': 'PostgreSQL'
            },
            '@agent-database': {
                'tables': ['users', 'sessions', 'data'],
                'indexes': ['users_email_idx', 'sessions_user_id_idx'],
                'migrations': ['001_initial_schema.sql']
            }
        }
        
        return mock_responses.get(agent['id'], {'status': 'completed'})
    
    def _execute_parallel(self, agents: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute agents in parallel (placeholder)"""
        # In real implementation, this would use asyncio or threading
        # For now, just execute sequentially
        results = []
        for agent in agents:
            results.append(self._execute_agent(agent, context))
        return results
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from all agents"""
        aggregated = {
            'success': all(r['success'] for r in results),
            'timestamp': datetime.now().isoformat(),
            'session_id': self.context.session_id,
            'agents_executed': len(results),
            'total_duration': sum(r['metrics']['duration_seconds'] for r in results),
            'total_cost': sum(r['metrics']['estimated_cost'] for r in results),
            'results': results,
            'summary': self._generate_summary(results),
            'next_actions': self._determine_next_actions(results)
        }
        
        return aggregated
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution summary"""
        summary = {
            'successful_agents': [r['agent_name'] for r in results if r['success']],
            'failed_agents': [r['agent_name'] for r in results if not r['success']],
            'key_outputs': {}
        }
        
        # Extract key outputs from each agent
        for result in results:
            if result['success'] and result['output']:
                summary['key_outputs'][result['agent_id']] = self._extract_key_info(result['output'])
        
        return summary
    
    def _extract_key_info(self, output: Dict[str, Any]) -> Any:
        """Extract key information from agent output"""
        # Prioritize certain keys
        priority_keys = ['plan', 'architecture', 'components', 'api_endpoints', 'tables']
        
        for key in priority_keys:
            if key in output:
                return {key: output[key]}
        
        # Return first non-empty value
        for key, value in output.items():
            if value:
                return {key: value}
        
        return output
    
    def _determine_next_actions(self, results: List[Dict[str, Any]]) -> List[str]:
        """Determine recommended next actions"""
        actions = []
        
        # Check if all agents succeeded
        if all(r['success'] for r in results):
            actions.append("All agents completed successfully. Ready to proceed with implementation.")
        else:
            failed = [r['agent_name'] for r in results if not r['success']]
            actions.append(f"Retry failed agents: {', '.join(failed)}")
        
        # Add agent-specific recommendations
        for result in results:
            if result['success'] and result['agent_id'] == '@agent-orchestrator':
                if 'next_steps' in result.get('output', {}):
                    actions.extend(result['output']['next_steps'])
        
        return actions
    
    def _save_execution_history(self, plan: Dict[str, Any], results: List[Dict[str, Any]]):
        """Save execution history for analysis"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.context.session_id,
            'plan': plan,
            'results': results,
            'project_dir': str(self.env.project_dir)
        }
        
        # Save to history file
        history_file = self.env.cache_dir / 'orchestration_history.json'
        
        try:
            # Load existing history
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Append new entry
            history.append(history_entry)
            
            # Keep only last 100 entries
            history = history[-100:]
            
            # Save updated history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save execution history: {e}")


def main():
    """Main entry point"""
    orchestrator = AgentOrchestrator()
    return orchestrator.safe_run()


if __name__ == "__main__":
    sys.exit(main())