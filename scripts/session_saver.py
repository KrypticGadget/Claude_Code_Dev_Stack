#!/usr/bin/env python3
"""
Session Saver Hook - Persist context and state when Claude Code operations complete
Saves session data, agent interactions, and project state
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from base_hook import BaseHook


class SessionSaver(BaseHook):
    """Save session context and state"""
    
    def __init__(self):
        super().__init__('session_saver')
        self.session_file = self.env.cache_dir / 'session_state.json'
        self.history_dir = self.env.cache_dir / 'session_history'
        self.history_dir.mkdir(exist_ok=True)
        self.interactions_dir = self.env.cache_dir / 'interactions'
        self.interactions_dir.mkdir(exist_ok=True)
    
    def run(self) -> int:
        """Save session context on completion"""
        # Read operation data from stdin
        operation_data = self._read_operation_data()
        
        # Load current session
        session_data = self._load_current_session()
        
        # Update session with operation results
        self._update_session(session_data, operation_data)
        
        # Save agent interaction if applicable
        if operation_data.get('agent_interaction'):
            self._save_agent_interaction(operation_data['agent_interaction'])
        
        # Save file changes
        self._track_file_changes(operation_data.get('file_changes', []))
        
        # Update project metrics
        self._update_project_metrics(session_data, operation_data)
        
        # Save updated session
        self._save_session(session_data)
        
        # Clean up old data
        self._cleanup_old_data()
        
        self.logger.info("Session saved successfully", 
                        session_id=session_data['session_id'],
                        operations_count=session_data.get('operations_count', 0))
        
        return 0
    
    def _read_operation_data(self) -> Dict[str, Any]:
        """Read operation data from stdin"""
        input_text = self.read_stdin()
        
        if not input_text:
            return {}
        
        try:
            # Try to parse as JSON
            return json.loads(input_text)
        except json.JSONDecodeError:
            # If not JSON, create basic operation data
            return {
                'type': 'text_operation',
                'content': input_text,
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_current_session(self) -> Dict[str, Any]:
        """Load current session data"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load session: {e}")
        
        # Create new session if none exists
        return {
            'session_id': os.environ.get('CLAUDE_SESSION_ID', 'unknown'),
            'started_at': datetime.now().isoformat(),
            'project_dir': str(self.env.project_dir),
            'operations_count': 0,
            'agents_used': {},
            'files_modified': [],
            'metrics': {}
        }
    
    def _update_session(self, session_data: Dict[str, Any], operation_data: Dict[str, Any]):
        """Update session with operation results"""
        # Update timestamp
        session_data['last_activity'] = datetime.now().isoformat()
        
        # Increment operations count
        session_data['operations_count'] = session_data.get('operations_count', 0) + 1
        
        # Track agent usage
        if operation_data.get('agent'):
            agent = operation_data['agent']
            if agent not in session_data['agents_used']:
                session_data['agents_used'][agent] = 0
            session_data['agents_used'][agent] += 1
        
        # Add operation to history
        if 'operations_history' not in session_data:
            session_data['operations_history'] = []
        
        session_data['operations_history'].append({
            'timestamp': datetime.now().isoformat(),
            'type': operation_data.get('type', 'unknown'),
            'agent': operation_data.get('agent'),
            'summary': self._create_operation_summary(operation_data)
        })
        
        # Keep only last 100 operations
        session_data['operations_history'] = session_data['operations_history'][-100:]
    
    def _save_agent_interaction(self, interaction_data: Dict[str, Any]):
        """Save detailed agent interaction"""
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{interaction_data.get('agent', 'unknown')}.json"
        interaction_file = self.interactions_dir / filename
        
        try:
            # Enhance interaction data
            interaction_data.update({
                'timestamp': timestamp.isoformat(),
                'session_id': self.context.session_id,
                'project_dir': str(self.env.project_dir),
                'duration': interaction_data.get('duration'),
                'success': interaction_data.get('success', True)
            })
            
            with open(interaction_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_data, f, indent=2)
            
            # Also save to history for quick access
            history_file = self.history_dir / f"{interaction_data['agent']}_{timestamp.strftime('%Y%m%d')}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save agent interaction: {e}")
    
    def _track_file_changes(self, file_changes: List[Dict[str, Any]]):
        """Track file modifications"""
        if not file_changes:
            return
        
        changes_file = self.env.cache_dir / 'file_changes.json'
        
        try:
            # Load existing changes
            existing_changes = {}
            if changes_file.exists():
                with open(changes_file, 'r', encoding='utf-8') as f:
                    existing_changes = json.load(f)
            
            # Update with new changes
            for change in file_changes:
                file_path = change.get('path', '')
                if not file_path:
                    continue
                
                if file_path not in existing_changes:
                    existing_changes[file_path] = {
                        'first_modified': datetime.now().isoformat(),
                        'modifications': []
                    }
                
                existing_changes[file_path]['last_modified'] = datetime.now().isoformat()
                existing_changes[file_path]['modifications'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': change.get('type', 'modify'),
                    'agent': change.get('agent'),
                    'description': change.get('description', '')
                })
                
                # Keep only last 50 modifications per file
                existing_changes[file_path]['modifications'] = existing_changes[file_path]['modifications'][-50:]
            
            # Save updated changes
            with open(changes_file, 'w', encoding='utf-8') as f:
                json.dump(existing_changes, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to track file changes: {e}")
    
    def _update_project_metrics(self, session_data: Dict[str, Any], operation_data: Dict[str, Any]):
        """Update project-level metrics"""
        if 'metrics' not in session_data:
            session_data['metrics'] = {}
        
        metrics = session_data['metrics']
        
        # Update operation counts
        operation_type = operation_data.get('type', 'unknown')
        if 'operation_types' not in metrics:
            metrics['operation_types'] = {}
        metrics['operation_types'][operation_type] = metrics['operation_types'].get(operation_type, 0) + 1
        
        # Update success/failure rates
        if operation_data.get('success') is not None:
            if 'success_rate' not in metrics:
                metrics['success_rate'] = {'success': 0, 'failure': 0}
            
            if operation_data['success']:
                metrics['success_rate']['success'] += 1
            else:
                metrics['success_rate']['failure'] += 1
        
        # Update timing metrics
        if operation_data.get('duration'):
            if 'durations' not in metrics:
                metrics['durations'] = []
            metrics['durations'].append(operation_data['duration'])
            
            # Keep only last 100 durations
            metrics['durations'] = metrics['durations'][-100:]
            
            # Calculate average
            metrics['average_duration'] = sum(metrics['durations']) / len(metrics['durations'])
    
    def _create_operation_summary(self, operation_data: Dict[str, Any]) -> str:
        """Create a brief summary of the operation"""
        operation_type = operation_data.get('type', 'unknown')
        
        if operation_type == 'text_operation':
            # Summarize text content
            content = operation_data.get('content', '')
            return content[:100] + '...' if len(content) > 100 else content
        
        elif operation_type == 'file_operation':
            files = operation_data.get('files', [])
            return f"Modified {len(files)} file(s)"
        
        elif operation_type == 'agent_operation':
            agent = operation_data.get('agent', 'unknown')
            action = operation_data.get('action', 'unknown')
            return f"{agent}: {action}"
        
        else:
            # Generic summary
            return f"{operation_type} operation"
    
    def _save_session(self, session_data: Dict[str, Any]):
        """Save session data to file"""
        try:
            # Save main session file
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
            # Create backup in history
            backup_file = self.history_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old session data and logs"""
        try:
            cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days
            
            # Clean up old interaction files
            for file in self.interactions_dir.glob('*.json'):
                if file.stat().st_mtime < cutoff_date:
                    file.unlink()
            
            # Clean up old history files
            for file in self.history_dir.glob('*.json'):
                if file.stat().st_mtime < cutoff_date:
                    file.unlink()
            
            # Clean up old log files
            for file in self.env.logs_dir.glob('*.log'):
                if file.stat().st_mtime < cutoff_date:
                    file.unlink()
                    
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")


def main():
    """Main entry point"""
    saver = SessionSaver()
    return saver.safe_run()


if __name__ == "__main__":
    sys.exit(main())