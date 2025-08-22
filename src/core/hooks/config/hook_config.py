#!/usr/bin/env python3
"""
Hook Configuration System - V3.6.9
Manages configuration for all 38 Python hooks with automatic discovery and validation
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import ast
import importlib.util


@dataclass
class HookConfig:
    """Configuration for a single hook"""
    name: str
    enabled: bool = True
    priority: int = 5
    triggers: List[str] = None
    dependencies: List[str] = None
    provides: List[str] = None
    tags: List[str] = None
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    max_concurrent: int = 1
    hot_reload: bool = True
    lsp_enabled: bool = False
    custom_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
        if self.dependencies is None:
            self.dependencies = []
        if self.provides is None:
            self.provides = []
        if self.tags is None:
            self.tags = []
        if self.custom_config is None:
            self.custom_config = {}


class HookConfigManager:
    """Manages configuration for all hooks"""
    
    def __init__(self, hooks_directory: str = None, config_file: str = None):
        self.hooks_directory = Path(hooks_directory) if hooks_directory else Path(__file__).parent
        self.config_file = Path(config_file) if config_file else self.hooks_directory / "hooks_config.yaml"
        self.hook_configs: Dict[str, HookConfig] = {}
        self.discovered_hooks: Dict[str, Dict[str, Any]] = {}
        
        # System configuration
        self.system_config = {
            'max_concurrent_executions': 10,
            'default_timeout': 30.0,
            'hot_reload_enabled': True,
            'performance_monitoring': True,
            'lsp_bridge_enabled': True,
            'auto_discovery': True,
            'config_validation': True,
            'backup_configs': True
        }
        
        # Load existing configurations
        self._load_configurations()
        
        # Discover hooks if auto-discovery is enabled
        if self.system_config['auto_discovery']:
            self._discover_all_hooks()
    
    def _load_configurations(self):
        """Load hook configurations from file"""
        if not self.config_file.exists():
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Load system configuration
            if 'system' in config_data:
                self.system_config.update(config_data['system'])
            
            # Load hook configurations
            if 'hooks' in config_data:
                for hook_name, hook_data in config_data['hooks'].items():
                    self.hook_configs[hook_name] = HookConfig(name=hook_name, **hook_data)
            
            print(f"Loaded configurations for {len(self.hook_configs)} hooks")
            
        except Exception as e:
            print(f"Failed to load hook configurations: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'system': self.system_config,
            'hooks': {}
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            print(f"Created default configuration file: {self.config_file}")
            
        except Exception as e:
            print(f"Failed to create default configuration: {e}")
    
    def _discover_all_hooks(self):
        """Discover all hooks in the hooks directory"""
        print("Discovering hooks...")
        
        # Get all Python files in the hooks directory
        hook_files = [f for f in self.hooks_directory.glob("*.py") 
                     if not f.name.startswith('__') and 
                     f.name not in ['hook_registry.py', 'hook_registry_api.py', 'hook_config.py']]
        
        for hook_file in hook_files:
            try:
                hook_info = self._analyze_hook_file(hook_file)
                if hook_info:
                    self.discovered_hooks[hook_info['name']] = hook_info
                    
                    # Create default config if not exists
                    if hook_info['name'] not in self.hook_configs:
                        self._create_default_hook_config(hook_info)
                    
            except Exception as e:
                print(f"Failed to discover hook {hook_file.name}: {e}")
        
        print(f"Discovered {len(self.discovered_hooks)} hooks")
        
        # Save updated configurations
        self._save_configurations()
    
    def _analyze_hook_file(self, hook_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a hook file to extract metadata and configuration"""
        try:
            content = hook_file.read_text(encoding='utf-8')
            
            hook_info = {
                'name': hook_file.stem,
                'file_path': str(hook_file),
                'file_size': hook_file.stat().st_size,
                'last_modified': datetime.fromtimestamp(hook_file.stat().st_mtime),
                'description': '',
                'version': '1.0.0',
                'author': '',
                'triggers': [],
                'dependencies': [],
                'provides': [],
                'tags': [],
                'functions': [],
                'classes': [],
                'imports': [],
                'has_main': False,
                'has_process_hook': False,
                'is_async': False,
                'lsp_compatible': False
            }
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                hook_info = self._analyze_ast(tree, hook_info)
            except SyntaxError:
                print(f"Syntax error in {hook_file.name}, using regex analysis")
            
            # Extract docstring metadata
            hook_info = self._extract_docstring_metadata(content, hook_info)
            
            # Extract comment metadata
            hook_info = self._extract_comment_metadata(content, hook_info)
            
            # Analyze content patterns
            hook_info = self._analyze_content_patterns(content, hook_info)
            
            return hook_info
            
        except Exception as e:
            print(f"Failed to analyze {hook_file.name}: {e}")
            return None
    
    def _analyze_ast(self, tree: ast.AST, hook_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AST to extract detailed information"""
        
        class HookAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.classes = []
                self.imports = []
                self.has_async = False
            
            def visit_FunctionDef(self, node):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if node.returns else None,
                    'is_async': False,
                    'decorators': [ast.unparse(dec) for dec in node.decorator_list]
                }
                self.functions.append(func_info)
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if node.returns else None,
                    'is_async': True,
                    'decorators': [ast.unparse(dec) for dec in node.decorator_list]
                }
                self.functions.append(func_info)
                self.has_async = True
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                class_info = {
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'methods': []
                }
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        class_info['methods'].append(item.name)
                
                self.classes.append(class_info)
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'type': 'import'
                    })
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        self.imports.append({
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'type': 'from'
                        })
                self.generic_visit(node)
        
        analyzer = HookAnalyzer()
        analyzer.visit(tree)
        
        hook_info['functions'] = analyzer.functions
        hook_info['classes'] = analyzer.classes
        hook_info['imports'] = analyzer.imports
        hook_info['is_async'] = analyzer.has_async
        
        # Check for specific functions
        function_names = [f['name'] for f in analyzer.functions]
        hook_info['has_main'] = 'main' in function_names
        hook_info['has_process_hook'] = 'process_hook' in function_names
        
        return hook_info
    
    def _extract_docstring_metadata(self, content: str, hook_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from module docstring"""
        # Find module docstring
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if not docstring_match:
            docstring_match = re.search(r"'''(.*?)'''", content, re.DOTALL)
        
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            lines = docstring.split('\n')
            
            if lines:
                hook_info['description'] = lines[0].strip()
            
            # Look for structured metadata
            for line in lines:
                line = line.strip()
                if line.lower().startswith('author:'):
                    hook_info['author'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('version:'):
                    hook_info['version'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('tags:'):
                    tags = line.split(':', 1)[1].strip()
                    hook_info['tags'].extend([tag.strip() for tag in tags.split(',')])
        
        return hook_info
    
    def _extract_comment_metadata(self, content: str, hook_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from special comments"""
        metadata_patterns = {
            'priority': r'#\s*@priority:\s*(\d+)',
            'triggers': r'#\s*@triggers:\s*(.+)',
            'dependencies': r'#\s*@depends:\s*(.+)',
            'provides': r'#\s*@provides:\s*(.+)',
            'tags': r'#\s*@tags:\s*(.+)',
            'lsp': r'#\s*@lsp:\s*(true|false)',
            'timeout': r'#\s*@timeout:\s*(\d+(?:\.\d+)?)',
            'max_concurrent': r'#\s*@max_concurrent:\s*(\d+)'
        }
        
        for key, pattern in metadata_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                if key == 'priority':
                    # Priority will be handled in hook config creation
                    pass
                elif key in ['triggers', 'dependencies', 'provides', 'tags']:
                    items = [item.strip() for item in value.split(',')]
                    hook_info[key].extend(items)
                elif key == 'lsp':
                    hook_info['lsp_compatible'] = value.lower() == 'true'
                elif key in ['timeout']:
                    # Will be handled in config creation
                    pass
        
        return hook_info
    
    def _analyze_content_patterns(self, content: str, hook_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for common patterns"""
        content_lower = content.lower()
        
        # Trigger pattern detection
        trigger_patterns = {
            'user_prompt': ['user_prompt', 'user_input', 'prompt'],
            'claude_response': ['claude_response', 'ai_response', 'response'],
            'agent_activation': ['agent_activation', 'agent', '@agent'],
            'mcp_request': ['mcp_request', 'mcp', 'service'],
            'file_change': ['file_change', 'file_modified', 'watch', 'observer'],
            'system_event': ['system_event', 'system', 'event']
        }
        
        for trigger_type, keywords in trigger_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                if trigger_type not in hook_info['triggers']:
                    hook_info['triggers'].append(trigger_type)
        
        # LSP capability detection
        lsp_indicators = ['lsp', 'language_server', 'completion', 'hover', 'definition']
        if any(indicator in content_lower for indicator in lsp_indicators):
            hook_info['lsp_compatible'] = True
            hook_info['tags'].append('lsp')
        
        # Audio capability detection
        audio_indicators = ['audio', 'sound', 'play', 'speaker', 'wav', 'mp3']
        if any(indicator in content_lower for indicator in audio_indicators):
            hook_info['tags'].append('audio')
        
        # Orchestration capability detection
        orchestration_indicators = ['orchestrat', 'coordinat', 'manage', 'workflow']
        if any(indicator in content_lower for indicator in orchestration_indicators):
            hook_info['tags'].append('orchestration')
        
        # Performance monitoring detection
        performance_indicators = ['performance', 'monitor', 'metrics', 'stats', 'benchmark']
        if any(indicator in content_lower for indicator in performance_indicators):
            hook_info['tags'].append('monitoring')
        
        return hook_info
    
    def _create_default_hook_config(self, hook_info: Dict[str, Any]):
        """Create default configuration for a discovered hook"""
        # Extract priority from comments or set default
        priority = 5  # Normal priority
        if 'orchestrat' in hook_info['name'].lower():
            priority = 1  # Critical
        elif 'audio' in hook_info['name'].lower():
            priority = 2  # High
        elif any(tag in ['monitoring', 'performance'] for tag in hook_info['tags']):
            priority = 4  # Low
        
        # Determine timeout based on hook type
        timeout = 30.0
        if 'audio' in hook_info['tags']:
            timeout = 5.0  # Audio hooks should be fast
        elif 'orchestration' in hook_info['tags']:
            timeout = 60.0  # Orchestration may take longer
        
        # Create hook configuration
        config = HookConfig(
            name=hook_info['name'],
            enabled=True,
            priority=priority,
            triggers=hook_info['triggers'][:],  # Copy triggers
            dependencies=hook_info['dependencies'][:],  # Copy dependencies
            provides=hook_info['provides'][:],  # Copy provides
            tags=hook_info['tags'][:],  # Copy tags
            timeout=timeout,
            retry_count=3,
            retry_delay=1.0,
            max_concurrent=1,
            hot_reload=True,
            lsp_enabled=hook_info['lsp_compatible'],
            custom_config={
                'file_path': hook_info['file_path'],
                'version': hook_info['version'],
                'author': hook_info['author'],
                'description': hook_info['description']
            }
        )
        
        self.hook_configs[hook_info['name']] = config
        print(f"Created default configuration for hook: {hook_info['name']}")
    
    def get_hook_config(self, hook_name: str) -> Optional[HookConfig]:
        """Get configuration for a specific hook"""
        return self.hook_configs.get(hook_name)
    
    def set_hook_config(self, hook_name: str, config: HookConfig):
        """Set configuration for a specific hook"""
        self.hook_configs[hook_name] = config
        self._save_configurations()
    
    def update_hook_config(self, hook_name: str, updates: Dict[str, Any]):
        """Update configuration for a specific hook"""
        if hook_name not in self.hook_configs:
            print(f"Hook {hook_name} not found")
            return False
        
        config = self.hook_configs[hook_name]
        
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                config.custom_config[key] = value
        
        self._save_configurations()
        return True
    
    def get_enabled_hooks(self) -> List[str]:
        """Get list of enabled hook names"""
        return [name for name, config in self.hook_configs.items() if config.enabled]
    
    def get_hooks_by_trigger(self, trigger: str) -> List[str]:
        """Get hooks that respond to a specific trigger"""
        return [name for name, config in self.hook_configs.items() 
                if config.enabled and trigger in config.triggers]
    
    def get_hooks_by_tag(self, tag: str) -> List[str]:
        """Get hooks that have a specific tag"""
        return [name for name, config in self.hook_configs.items() 
                if config.enabled and tag in config.tags]
    
    def get_hooks_by_priority(self, priority: int) -> List[str]:
        """Get hooks with a specific priority"""
        return [name for name, config in self.hook_configs.items() 
                if config.enabled and config.priority == priority]
    
    def validate_configurations(self) -> List[str]:
        """Validate all hook configurations"""
        issues = []
        
        for hook_name, config in self.hook_configs.items():
            # Check if hook file exists
            if 'file_path' in config.custom_config:
                file_path = Path(config.custom_config['file_path'])
                if not file_path.exists():
                    issues.append(f"Hook {hook_name}: File not found at {file_path}")
            
            # Check dependencies
            for dep in config.dependencies:
                if dep not in self.hook_configs:
                    issues.append(f"Hook {hook_name}: Dependency '{dep}' not found")
            
            # Check for circular dependencies
            visited = set()
            def check_circular(current_hook, path):
                if current_hook in path:
                    issues.append(f"Circular dependency detected: {' -> '.join(path + [current_hook])}")
                    return
                
                if current_hook in visited:
                    return
                
                visited.add(current_hook)
                
                if current_hook in self.hook_configs:
                    for dep in self.hook_configs[current_hook].dependencies:
                        check_circular(dep, path + [current_hook])
            
            check_circular(hook_name, [])
        
        return issues
    
    def get_dependency_order(self, hook_names: List[str] = None) -> List[str]:
        """Get hooks in dependency order"""
        if hook_names is None:
            hook_names = list(self.hook_configs.keys())
        
        # Topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(hook_name):
            if hook_name in temp_visited:
                return  # Circular dependency - skip
            
            if hook_name in visited:
                return
            
            temp_visited.add(hook_name)
            
            if hook_name in self.hook_configs:
                for dep in self.hook_configs[hook_name].dependencies:
                    if dep in hook_names:
                        dfs(dep)
            
            temp_visited.remove(hook_name)
            visited.add(hook_name)
            result.append(hook_name)
        
        for hook_name in hook_names:
            dfs(hook_name)
        
        return result
    
    def export_configurations(self, export_file: str = None) -> str:
        """Export configurations to a file"""
        if export_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"hooks_config_export_{timestamp}.yaml"
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'system': self.system_config,
            'hooks': {name: asdict(config) for name, config in self.hook_configs.items()}
        }
        
        try:
            with open(export_file, 'w') as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2)
            
            print(f"Configurations exported to: {export_file}")
            return export_file
            
        except Exception as e:
            print(f"Failed to export configurations: {e}")
            return ""
    
    def import_configurations(self, import_file: str) -> bool:
        """Import configurations from a file"""
        try:
            with open(import_file, 'r') as f:
                import_data = yaml.safe_load(f)
            
            # Import system configuration
            if 'system' in import_data:
                self.system_config.update(import_data['system'])
            
            # Import hook configurations
            if 'hooks' in import_data:
                for hook_name, hook_data in import_data['hooks'].items():
                    self.hook_configs[hook_name] = HookConfig(name=hook_name, **hook_data)
            
            # Save imported configurations
            self._save_configurations()
            
            print(f"Configurations imported from: {import_file}")
            return True
            
        except Exception as e:
            print(f"Failed to import configurations: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        stats = {
            'total_hooks': len(self.hook_configs),
            'enabled_hooks': len(self.get_enabled_hooks()),
            'disabled_hooks': len(self.hook_configs) - len(self.get_enabled_hooks()),
            'discovered_hooks': len(self.discovered_hooks),
            'hooks_by_priority': {},
            'hooks_by_tag': {},
            'hooks_with_dependencies': 0,
            'hooks_providing_services': 0,
            'lsp_enabled_hooks': 0,
            'async_hooks': 0
        }
        
        # Count by priority
        for config in self.hook_configs.values():
            priority = config.priority
            stats['hooks_by_priority'][priority] = stats['hooks_by_priority'].get(priority, 0) + 1
        
        # Count by tags
        for config in self.hook_configs.values():
            for tag in config.tags:
                stats['hooks_by_tag'][tag] = stats['hooks_by_tag'].get(tag, 0) + 1
        
        # Count special cases
        for config in self.hook_configs.values():
            if config.dependencies:
                stats['hooks_with_dependencies'] += 1
            if config.provides:
                stats['hooks_providing_services'] += 1
            if config.lsp_enabled:
                stats['lsp_enabled_hooks'] += 1
        
        # Count async hooks from discovered info
        for hook_name, hook_info in self.discovered_hooks.items():
            if hook_info.get('is_async', False):
                stats['async_hooks'] += 1
        
        return stats
    
    def _save_configurations(self):
        """Save all configurations to file"""
        if self.system_config.get('backup_configs', True):
            self._backup_configurations()
        
        config_data = {
            'system': self.system_config,
            'hooks': {name: asdict(config) for name, config in self.hook_configs.items()}
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
        except Exception as e:
            print(f"Failed to save configurations: {e}")
    
    def _backup_configurations(self):
        """Create backup of current configurations"""
        if not self.config_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_file.with_suffix(f'.backup_{timestamp}.yaml')
        
        try:
            backup_file.write_text(self.config_file.read_text())
            
            # Keep only last 10 backups
            backup_files = sorted(self.hooks_directory.glob("hooks_config.backup_*.yaml"))
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    old_backup.unlink()
            
        except Exception as e:
            print(f"Failed to create backup: {e}")


# Global configuration manager instance
_config_manager_instance = None

def get_hook_config_manager(hooks_directory: str = None, config_file: str = None) -> HookConfigManager:
    """Get or create the global configuration manager instance"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = HookConfigManager(hooks_directory, config_file)
    return _config_manager_instance


# Command-line interface
def main():
    """Command-line interface for hook configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hook Configuration Manager")
    parser.add_argument('--hooks-dir', help='Directory containing hooks')
    parser.add_argument('--config-file', help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List hooks')
    list_parser.add_argument('--enabled-only', action='store_true', help='Show only enabled hooks')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--priority', type=int, help='Filter by priority')
    
    # Enable/disable commands
    subparsers.add_parser('enable', help='Enable hook').add_argument('hook_name')
    subparsers.add_parser('disable', help='Disable hook').add_argument('hook_name')
    
    # Validation command
    subparsers.add_parser('validate', help='Validate configurations')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show configuration statistics')
    
    # Export/import commands
    export_parser = subparsers.add_parser('export', help='Export configurations')
    export_parser.add_argument('--file', help='Export file path')
    
    import_parser = subparsers.add_parser('import', help='Import configurations')
    import_parser.add_argument('file', help='Import file path')
    
    # Discover command
    subparsers.add_parser('discover', help='Rediscover hooks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create configuration manager
    config_manager = get_hook_config_manager(args.hooks_dir, args.config_file)
    
    if args.command == 'list':
        hooks = config_manager.hook_configs
        
        if args.enabled_only:
            hooks = {name: config for name, config in hooks.items() if config.enabled}
        
        if args.tag:
            hooks = {name: config for name, config in hooks.items() if args.tag in config.tags}
        
        if args.priority is not None:
            hooks = {name: config for name, config in hooks.items() if config.priority == args.priority}
        
        print(f"Found {len(hooks)} hooks:")
        for name, config in sorted(hooks.items()):
            status = "✓" if config.enabled else "✗"
            print(f"  {status} {name} (priority: {config.priority}, tags: {', '.join(config.tags)})")
    
    elif args.command == 'enable':
        success = config_manager.update_hook_config(args.hook_name, {'enabled': True})
        print(f"Hook {args.hook_name} {'enabled' if success else 'not found'}")
    
    elif args.command == 'disable':
        success = config_manager.update_hook_config(args.hook_name, {'enabled': False})
        print(f"Hook {args.hook_name} {'disabled' if success else 'not found'}")
    
    elif args.command == 'validate':
        issues = config_manager.validate_configurations()
        if issues:
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"  ⚠️  {issue}")
        else:
            print("✓ All configurations are valid")
    
    elif args.command == 'stats':
        stats = config_manager.get_statistics()
        print("Configuration Statistics:")
        print(f"  Total hooks: {stats['total_hooks']}")
        print(f"  Enabled: {stats['enabled_hooks']}")
        print(f"  Disabled: {stats['disabled_hooks']}")
        print(f"  LSP enabled: {stats['lsp_enabled_hooks']}")
        print(f"  Async hooks: {stats['async_hooks']}")
        print("  Hooks by priority:")
        for priority, count in sorted(stats['hooks_by_priority'].items()):
            print(f"    Priority {priority}: {count}")
        if stats['hooks_by_tag']:
            print("  Top tags:")
            for tag, count in sorted(stats['hooks_by_tag'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {tag}: {count}")
    
    elif args.command == 'export':
        export_file = config_manager.export_configurations(args.file)
        if export_file:
            print(f"✓ Configurations exported to {export_file}")
    
    elif args.command == 'import':
        success = config_manager.import_configurations(args.file)
        print(f"{'✓' if success else '✗'} Import {'successful' if success else 'failed'}")
    
    elif args.command == 'discover':
        initial_count = len(config_manager.hook_configs)
        config_manager._discover_all_hooks()
        final_count = len(config_manager.hook_configs)
        print(f"Discovery complete. Found {final_count - initial_count} new hooks.")


if __name__ == '__main__':
    main()


# Export main classes and functions
__all__ = ['HookConfig', 'HookConfigManager', 'get_hook_config_manager']