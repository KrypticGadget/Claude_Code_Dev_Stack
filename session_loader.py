#!/usr/bin/env python3
"""
Session Loader Hook - Restore context and state on Claude Code startup
Loads previous session data, project context, and agent history
"""

import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from base_hook import BaseHook


class SessionLoader(BaseHook):
    """Load and restore session context"""
    
    def __init__(self):
        super().__init__('session_loader')
        self.session_file = self.env.cache_dir / 'session_state.json'
        self.history_dir = self.env.cache_dir / 'session_history'
        self.history_dir.mkdir(exist_ok=True)
    
    def run(self) -> int:
        """Load session context on startup"""
        # Get current session ID or create new one
        session_id = os.environ.get('CLAUDE_SESSION_ID')
        if not session_id:
            session_id = self._generate_session_id()
            os.environ['CLAUDE_SESSION_ID'] = session_id
        
        # Load previous session if exists
        previous_session = self._load_previous_session()
        
        # Load project context
        project_context = self._load_project_context()
        
        # Load agent history
        agent_history = self._load_agent_history()
        
        # Prepare session data
        session_data = {
            'session_id': session_id,
            'started_at': datetime.now().isoformat(),
            'project_dir': str(self.env.project_dir),
            'previous_session': previous_session,
            'project_context': project_context,
            'agent_history': agent_history,
            'environment': self._get_environment_info()
        }
        
        # Save current session
        self._save_session(session_data)
        
        # Output session info for Claude Code
        output = self._prepare_session_output(session_data)
        self.write_stdout(json.dumps(output, indent=2))
        
        self.logger.info(f"Loaded session {session_id}", 
                        project=str(self.env.project_dir),
                        previous_session=bool(previous_session))
        
        return 0
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pid = os.getpid()
        return f"claude_session_{timestamp}_{pid}"
    
    def _load_previous_session(self) -> Optional[Dict[str, Any]]:
        """Load the most recent session data"""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            # Check if session is recent (within 24 hours)
            started_at = datetime.fromisoformat(session.get('started_at', ''))
            if datetime.now() - started_at < timedelta(hours=24):
                return session
            
        except Exception as e:
            self.logger.warning(f"Failed to load previous session: {e}")
        
        return None
    
    def _load_project_context(self) -> Dict[str, Any]:
        """Load project-specific context"""
        context = {
            'type': 'unknown',
            'framework': None,
            'dependencies': [],
            'configuration': {},
            'recent_files': []
        }
        
        # Detect project type
        project_files = {
            'package.json': 'node',
            'requirements.txt': 'python',
            'Gemfile': 'ruby',
            'pom.xml': 'java',
            'go.mod': 'go',
            'Cargo.toml': 'rust',
            'composer.json': 'php'
        }
        
        for file, project_type in project_files.items():
            if (self.env.project_dir / file).exists():
                context['type'] = project_type
                context.update(self._load_project_file(file))
                break
        
        # Load recent files
        context['recent_files'] = self._get_recent_files()
        
        # Load .claude configuration if exists
        claude_config = self.env.project_dir / '.claude' / 'project.json'
        if claude_config.exists():
            try:
                with open(claude_config, 'r', encoding='utf-8') as f:
                    context['configuration'] = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load .claude config: {e}")
        
        return context
    
    def _load_project_file(self, filename: str) -> Dict[str, Any]:
        """Load and parse project file"""
        file_path = self.env.project_dir / filename
        result = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if filename == 'package.json':
                data = json.loads(content)
                result['name'] = data.get('name', 'unknown')
                result['version'] = data.get('version', '0.0.0')
                result['dependencies'] = list(data.get('dependencies', {}).keys())
                result['scripts'] = list(data.get('scripts', {}).keys())
                
                # Detect framework
                deps = data.get('dependencies', {})
                if 'react' in deps:
                    result['framework'] = 'react'
                elif 'vue' in deps:
                    result['framework'] = 'vue'
                elif 'angular' in deps:
                    result['framework'] = 'angular'
                elif 'express' in deps:
                    result['framework'] = 'express'
            
            elif filename == 'requirements.txt':
                lines = content.strip().split('\n')
                result['dependencies'] = [l.split('==')[0] for l in lines if l and not l.startswith('#')]
                
                # Detect framework
                deps_lower = [d.lower() for d in result['dependencies']]
                if 'django' in deps_lower:
                    result['framework'] = 'django'
                elif 'flask' in deps_lower:
                    result['framework'] = 'flask'
                elif 'fastapi' in deps_lower:
                    result['framework'] = 'fastapi'
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {filename}: {e}")
        
        return result
    
    def _get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently modified files in project"""
        recent_files = []
        
        try:
            # Get all files modified in last 7 days
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for root, dirs, files in os.walk(self.env.project_dir):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]
                
                for file in files:
                    # Skip hidden files and common ignore patterns
                    if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.pyd', '.so', '.dll')):
                        continue
                    
                    file_path = Path(root) / file
                    try:
                        stat = file_path.stat()
                        if datetime.fromtimestamp(stat.st_mtime) > cutoff_time:
                            recent_files.append({
                                'path': str(file_path.relative_to(self.env.project_dir)),
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'size': stat.st_size
                            })
                    except:
                        continue
            
            # Sort by modification time and limit
            recent_files.sort(key=lambda x: x['modified'], reverse=True)
            return recent_files[:limit]
            
        except Exception as e:
            self.logger.warning(f"Failed to get recent files: {e}")
            return []
    
    def _load_agent_history(self) -> List[Dict[str, Any]]:
        """Load recent agent interactions"""
        history = []
        
        try:
            # Load last 10 agent interactions
            history_files = sorted(self.history_dir.glob('*.json'), reverse=True)[:10]
            
            for file in history_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        interaction = json.load(f)
                        history.append({
                            'timestamp': interaction.get('timestamp'),
                            'agent': interaction.get('agent'),
                            'action': interaction.get('action'),
                            'summary': interaction.get('summary', '')[:100]
                        })
                except:
                    continue
            
        except Exception as e:
            self.logger.warning(f"Failed to load agent history: {e}")
        
        return history
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        import platform
        
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'claude_home': str(self.env.claude_home),
            'working_directory': str(self.env.project_dir),
            'user': self.context.user,
            'is_wsl': self.env._is_wsl()
        }
    
    def _save_session(self, session_data: Dict[str, Any]):
        """Save current session data"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
            # Also save to history
            history_file = self.history_dir / f"{session_data['session_id']}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
    
    def _prepare_session_output(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare session data for Claude Code"""
        output = {
            'session_id': session_data['session_id'],
            'context_loaded': True,
            'project': {
                'path': session_data['project_dir'],
                'type': session_data['project_context']['type'],
                'framework': session_data['project_context'].get('framework')
            }
        }
        
        # Add continuation context if previous session exists
        if session_data['previous_session']:
            output['continuation'] = {
                'previous_session_id': session_data['previous_session']['session_id'],
                'last_activity': session_data['previous_session'].get('last_activity'),
                'agent_history': session_data['agent_history'][:3]  # Last 3 interactions
            }
        
        # Add relevant context messages
        messages = []
        
        if session_data['project_context']['type'] != 'unknown':
            messages.append(f"Detected {session_data['project_context']['type']} project")
        
        if session_data['project_context'].get('framework'):
            messages.append(f"Using {session_data['project_context']['framework']} framework")
        
        if session_data['previous_session']:
            messages.append("Resuming from previous session")
        
        if messages:
            output['messages'] = messages
        
        return output


def main():
    """Main entry point"""
    loader = SessionLoader()
    return loader.safe_run()


if __name__ == "__main__":
    sys.exit(main())