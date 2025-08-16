#!/usr/bin/env python3
"""
Quality Configuration Manager - V3.0+
Easy configuration management for code quality tools and git hooks
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

class QualityConfigManager:
    """Manager for quality tools and git hooks configuration"""
    
    def __init__(self):
        self.settings_path = Path.home() / '.claude' / 'settings.json'
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load current settings"""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {}
        return {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def ensure_quality_config(self):
        """Ensure quality configuration exists"""
        if 'v3ExtendedFeatures' not in self.settings:
            self.settings['v3ExtendedFeatures'] = {}
        
        if 'qualityTools' not in self.settings['v3ExtendedFeatures']:
            self.settings['v3ExtendedFeatures']['qualityTools'] = {
                "enabled": True,
                "autoFormat": True,
                "lintOnSave": True,
                "strictness": "warning",
                "blockOnErrors": False,
                "blockOnWarnings": False,
                "showSuggestions": True
            }
        
        if 'gitHooks' not in self.settings['v3ExtendedFeatures']:
            self.settings['v3ExtendedFeatures']['gitHooks'] = {
                "enabled": True,
                "preCommitChecks": ["lint", "format"],
                "blockOnFailure": False,
                "autoFix": True,
                "strictness": "warning",
                "blockOnLintErrors": False,
                "blockOnLintWarnings": False,
                "allowWarningsCommit": True
            }
    
    def set_strictness_level(self, level: str):
        """Set global strictness level"""
        if level not in ['strict', 'warning', 'suggestion']:
            print(f"Invalid strictness level: {level}")
            print("Valid levels: strict, warning, suggestion")
            return False
        
        self.ensure_quality_config()
        
        # Update quality tools
        self.settings['v3ExtendedFeatures']['qualityTools']['strictness'] = level
        self.settings['v3ExtendedFeatures']['gitHooks']['strictness'] = level
        
        # Adjust blocking behavior based on level
        if level == 'strict':
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnErrors'] = True
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnWarnings'] = True
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintErrors'] = True
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintWarnings'] = True
            self.settings['v3ExtendedFeatures']['gitHooks']['allowWarningsCommit'] = False
        elif level == 'warning':
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnErrors'] = False
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnWarnings'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintErrors'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintWarnings'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['allowWarningsCommit'] = True
        else:  # suggestion
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnErrors'] = False
            self.settings['v3ExtendedFeatures']['qualityTools']['blockOnWarnings'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintErrors'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['blockOnLintWarnings'] = False
            self.settings['v3ExtendedFeatures']['gitHooks']['allowWarningsCommit'] = True
        
        print(f"Strictness level set to: {level}")
        return True
    
    def enable_quality_tools(self, enabled: bool = True):
        """Enable or disable quality tools"""
        self.ensure_quality_config()
        self.settings['v3ExtendedFeatures']['qualityTools']['enabled'] = enabled
        self.settings['v3ExtendedFeatures']['gitHooks']['enabled'] = enabled
        
        status = "enabled" if enabled else "disabled"
        print(f"Quality tools {status}")
    
    def set_auto_format(self, enabled: bool = True):
        """Enable or disable auto-formatting"""
        self.ensure_quality_config()
        self.settings['v3ExtendedFeatures']['qualityTools']['autoFormat'] = enabled
        self.settings['v3ExtendedFeatures']['gitHooks']['autoFix'] = enabled
        
        status = "enabled" if enabled else "disabled"
        print(f"Auto-formatting {status}")
    
    def show_current_config(self):
        """Display current configuration"""
        self.ensure_quality_config()
        
        quality_config = self.settings['v3ExtendedFeatures']['qualityTools']
        git_config = self.settings['v3ExtendedFeatures']['gitHooks']
        
        print("\n[CONFIG] Current Quality Configuration:")
        print("=" * 50)
        
        print(f"Quality Tools Enabled: {quality_config['enabled']}")
        print(f"Git Hooks Enabled: {git_config['enabled']}")
        print(f"Strictness Level: {quality_config['strictness']}")
        print(f"Auto-formatting: {quality_config['autoFormat']}")
        print(f"Lint on Save: {quality_config['lintOnSave']}")
        print(f"Show Suggestions: {quality_config['showSuggestions']}")
        
        print("\n[BLOCKING] Blocking Behavior:")
        print(f"Block on Errors: {quality_config['blockOnErrors']}")
        print(f"Block on Warnings: {quality_config['blockOnWarnings']}")
        print(f"Allow Warnings in Commits: {git_config['allowWarningsCommit']}")
        
        print("\n[HOOKS] Git Hook Checks:")
        checks = ", ".join(git_config['preCommitChecks'])
        print(f"Pre-commit Checks: {checks}")
        
        print("\n[GUIDE] Strictness Level Guide:")
        print("  * strict: Block commits on any issue (errors, warnings, suggestions)")
        print("  * warning: Show all issues but only block on actual errors")
        print("  * suggestion: Show issues but don't block commits (recommended)")
    
    def configure_audio_notifications(self, enabled: bool = True):
        """Configure audio notifications for quality events"""
        audio_config = self.settings.get('v3Features', {}).get('audioV3', {})
        audio_config['qualityGate'] = enabled
        
        # Ensure the path exists
        if 'v3Features' not in self.settings:
            self.settings['v3Features'] = {}
        if 'audioV3' not in self.settings['v3Features']:
            self.settings['v3Features']['audioV3'] = {}
        
        self.settings['v3Features']['audioV3']['qualityGate'] = enabled
        
        status = "enabled" if enabled else "disabled"
        print(f"Audio notifications for quality events {status}")

def main():
    """Command line interface for quality configuration"""
    manager = QualityConfigManager()
    
    if len(sys.argv) < 2:
        print("Claude Code Quality Configuration Manager")
        print("Usage: python quality_config.py <command> [options]")
        print("\nCommands:")
        print("  show                    - Show current configuration")
        print("  strictness <level>      - Set strictness level (strict/warning/suggestion)")
        print("  enable                  - Enable quality tools")
        print("  disable                 - Disable quality tools")
        print("  autoformat on|off       - Enable/disable auto-formatting")
        print("  audio on|off            - Enable/disable audio notifications")
        print("  reset                   - Reset to default configuration")
        print("\nExamples:")
        print("  python quality_config.py strictness suggestion")
        print("  python quality_config.py show")
        print("  python quality_config.py autoformat on")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'show':
        manager.show_current_config()
    
    elif command == 'strictness':
        if len(sys.argv) < 3:
            print("Please specify strictness level: strict, warning, or suggestion")
            sys.exit(1)
        
        level = sys.argv[2].lower()
        if manager.set_strictness_level(level):
            manager.save_settings()
    
    elif command == 'enable':
        manager.enable_quality_tools(True)
        manager.save_settings()
    
    elif command == 'disable':
        manager.enable_quality_tools(False)
        manager.save_settings()
    
    elif command == 'autoformat':
        if len(sys.argv) < 3:
            print("Please specify: on or off")
            sys.exit(1)
        
        enabled = sys.argv[2].lower() == 'on'
        manager.set_auto_format(enabled)
        manager.save_settings()
    
    elif command == 'audio':
        if len(sys.argv) < 3:
            print("Please specify: on or off")
            sys.exit(1)
        
        enabled = sys.argv[2].lower() == 'on'
        manager.configure_audio_notifications(enabled)
        manager.save_settings()
    
    elif command == 'reset':
        # Reset to defaults
        manager.settings['v3ExtendedFeatures'] = {
            "qualityTools": {
                "enabled": True,
                "autoFormat": True,
                "lintOnSave": True,
                "strictness": "warning",
                "blockOnErrors": False,
                "blockOnWarnings": False,
                "showSuggestions": True
            },
            "gitHooks": {
                "enabled": True,
                "preCommitChecks": ["lint", "format"],
                "blockOnFailure": False,
                "autoFix": True,
                "strictness": "warning",
                "blockOnLintErrors": False,
                "blockOnLintWarnings": False,
                "allowWarningsCommit": True
            }
        }
        manager.save_settings()
        print("Configuration reset to defaults")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()