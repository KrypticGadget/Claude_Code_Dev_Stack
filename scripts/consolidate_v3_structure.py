#!/usr/bin/env python3
"""
Claude Code Dev Stack v3 Consolidation Script
============================================

This script consolidates the Claude_Code_Dev_Stack_v3 structure into the root level
while maintaining all functionality and relationships.

CONSOLIDATION STRATEGY:
1. Move v3 core structure to root level
2. Preserve all file relationships
3. Update all path references
4. Maintain integration points
5. Create backup before migration
6. Validate after consolidation
"""

import os
import shutil
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import re

class V3Consolidator:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.v3_dir = self.root_dir / "Claude_Code_Dev_Stack_v3"
        self.backup_dir = self.root_dir / f"BACKUP_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.migration_log = []
        self.path_mappings = {}
        
    def log(self, message, level="INFO"):
        """Log migration progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def create_backup(self):
        """Create full backup before consolidation"""
        self.log("Creating backup of current structure...")
        try:
            # Backup root structure (excluding v3)
            backup_root = self.backup_dir / "root_structure"
            backup_root.mkdir(parents=True)
            
            for item in self.root_dir.iterdir():
                if item.name != "Claude_Code_Dev_Stack_v3" and not item.name.startswith("BACKUP_"):
                    if item.is_dir():
                        shutil.copytree(item, backup_root / item.name)
                    else:
                        shutil.copy2(item, backup_root / item.name)
            
            # Backup v3 structure
            backup_v3 = self.backup_dir / "v3_structure"
            shutil.copytree(self.v3_dir, backup_v3)
            
            self.log(f"Backup created at: {self.backup_dir}")
            return True
        except Exception as e:
            self.log(f"Backup failed: {e}", "ERROR")
            return False
    
    def analyze_structure(self):
        """Analyze current structure and plan migration"""
        self.log("Analyzing structure for consolidation...")
        
        analysis = {
            "v3_directories": [],
            "root_directories": [],
            "conflicts": [],
            "migration_plan": []
        }
        
        # Analyze v3 structure
        if self.v3_dir.exists():
            for item in self.v3_dir.iterdir():
                if item.is_dir():
                    analysis["v3_directories"].append(item.name)
        
        # Analyze root structure
        for item in self.root_dir.iterdir():
            if item.is_dir() and item.name != "Claude_Code_Dev_Stack_v3" and not item.name.startswith("BACKUP_"):
                analysis["root_directories"].append(item.name)
        
        # Identify conflicts
        for v3_dir in analysis["v3_directories"]:
            if v3_dir in analysis["root_directories"]:
                analysis["conflicts"].append(v3_dir)
        
        # Create migration plan
        analysis["migration_plan"] = self._create_migration_plan(analysis)
        
        return analysis
    
    def _create_migration_plan(self, analysis):
        """Create detailed migration plan"""
        plan = []
        
        # Core v3 directories to consolidate
        core_migrations = [
            {
                "source": "core/agents",
                "target": "agents",
                "action": "merge_with_existing",
                "priority": 1
            },
            {
                "source": "core/commands", 
                "target": "commands",
                "action": "merge_with_existing",
                "priority": 1
            },
            {
                "source": "core/hooks",
                "target": "hooks",
                "action": "replace_and_backup",
                "priority": 2
            },
            {
                "source": "core/audio",
                "target": "audio",
                "action": "move_new",
                "priority": 3
            },
            {
                "source": "core/orchestration",
                "target": "orchestration",
                "action": "move_new", 
                "priority": 3
            },
            {
                "source": "core/integrations",
                "target": "integrations",
                "action": "merge_with_existing",
                "priority": 4
            },
            {
                "source": "core/testing",
                "target": "testing",
                "action": "move_new",
                "priority": 4
            },
            {
                "source": "apps",
                "target": "apps",
                "action": "move_new",
                "priority": 5
            }
        ]
        
        # Root level files to consolidate
        file_migrations = [
            {
                "source": "MASTER_SPEC_V3.md",
                "target": "MASTER_SPEC_V3.md",
                "action": "move_new",
                "priority": 1
            },
            {
                "source": "requirements.txt",
                "target": "requirements_v3.txt",
                "action": "move_rename",
                "priority": 2
            },
            {
                "source": "setup_environment.py",
                "target": "setup_environment_v3.py", 
                "action": "move_rename",
                "priority": 2
            }
        ]
        
        plan.extend(core_migrations)
        plan.extend(file_migrations)
        
        return sorted(plan, key=lambda x: x["priority"])
    
    def execute_migration(self, migration_plan):
        """Execute the migration plan"""
        self.log("Starting migration execution...")
        
        for step in migration_plan:
            try:
                self._execute_migration_step(step)
            except Exception as e:
                self.log(f"Migration step failed: {step} - {e}", "ERROR")
                return False
        
        return True
    
    def _execute_migration_step(self, step):
        """Execute individual migration step"""
        source_path = self.v3_dir / step["source"]
        target_path = self.root_dir / step["target"]
        
        self.log(f"Migrating: {step['source']} -> {step['target']} ({step['action']})")
        
        if step["action"] == "merge_with_existing":
            self._merge_directories(source_path, target_path)
        elif step["action"] == "replace_and_backup":
            self._replace_with_backup(source_path, target_path)
        elif step["action"] == "move_new":
            self._move_new(source_path, target_path)
        elif step["action"] == "move_rename":
            self._move_rename(source_path, target_path)
        
        # Record path mapping
        self.path_mappings[str(source_path)] = str(target_path)
    
    def _merge_directories(self, source, target):
        """Merge source directory with existing target"""
        if not source.exists():
            return
            
        if not target.exists():
            target.mkdir(parents=True)
        
        for item in source.iterdir():
            target_item = target / item.name
            if item.is_dir():
                self._merge_directories(item, target_item)
            else:
                if target_item.exists():
                    # Create backup of existing file
                    backup_name = f"{target_item.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(target_item, target_item.parent / backup_name)
                shutil.copy2(item, target_item)
    
    def _replace_with_backup(self, source, target):
        """Replace target with source after backing up"""
        if target.exists():
            backup_name = f"{target.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(target, target.parent / backup_name)
        
        if source.exists():
            shutil.copytree(source, target)
    
    def _move_new(self, source, target):
        """Move source to target if target doesn't exist"""
        if source.exists() and not target.exists():
            shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)
    
    def _move_rename(self, source, target):
        """Move source to renamed target"""
        if source.exists():
            shutil.copy2(source, target)
    
    def update_path_references(self):
        """Update all path references in consolidated files"""
        self.log("Updating path references...")
        
        # Common files that may contain path references
        files_to_update = [
            "**/*.py",
            "**/*.md", 
            "**/*.json",
            "**/*.yaml",
            "**/*.yml",
            "**/*.sh",
            "**/*.bat",
            "**/*.ps1"
        ]
        
        for pattern in files_to_update:
            for file_path in self.root_dir.glob(pattern):
                if "Claude_Code_Dev_Stack_v3" not in str(file_path) and not str(file_path).startswith(str(self.backup_dir)):
                    self._update_file_references(file_path)
    
    def _update_file_references(self, file_path):
        """Update path references in a specific file"""
        try:
            if file_path.suffix in ['.exe', '.dll', '.so', '.dylib']:
                return  # Skip binary files
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Update v3 path references
            patterns = [
                (r'Claude_Code_Dev_Stack_v3/core/agents', 'agents'),
                (r'Claude_Code_Dev_Stack_v3/core/commands', 'commands'),
                (r'Claude_Code_Dev_Stack_v3/core/hooks', 'hooks'),
                (r'Claude_Code_Dev_Stack_v3/core/', ''),
                (r'Claude_Code_Dev_Stack_v3/', ''),
                (r'\.\.\/\.\.\/Claude_Code_Dev_Stack_v3\/', '../'),
                (r'\.\/Claude_Code_Dev_Stack_v3\/', './'),
            ]
            
            for old_pattern, new_pattern in patterns:
                content = re.sub(old_pattern, new_pattern, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Updated references in: {file_path}")
                
        except Exception as e:
            self.log(f"Failed to update {file_path}: {e}", "WARNING")
    
    def create_consolidation_validation(self):
        """Create validation scripts for consolidated structure"""
        self.log("Creating validation scripts...")
        
        validation_script = self.root_dir / "scripts" / "validate_consolidation.py"
        validation_script.parent.mkdir(exist_ok=True)
        
        validation_code = '''#!/usr/bin/env python3
"""
Post-Consolidation Validation Script
==================================
Validates that all v3 functionality is preserved after consolidation.
"""

import os
import json
from pathlib import Path

def validate_consolidation():
    """Validate consolidated structure"""
    root_dir = Path(__file__).parent.parent
    
    validation_results = {
        "structure_check": validate_structure(root_dir),
        "agents_check": validate_agents(root_dir),
        "commands_check": validate_commands(root_dir),
        "hooks_check": validate_hooks(root_dir),
        "integrations_check": validate_integrations(root_dir)
    }
    
    return validation_results

def validate_structure(root_dir):
    """Validate directory structure"""
    required_dirs = [
        "agents", "commands", "hooks", "audio", 
        "orchestration", "integrations", "testing", "apps"
    ]
    
    results = {}
    for dir_name in required_dirs:
        dir_path = root_dir / dir_name
        results[dir_name] = {
            "exists": dir_path.exists(),
            "file_count": len(list(dir_path.glob("**/*"))) if dir_path.exists() else 0
        }
    
    return results

def validate_agents(root_dir):
    """Validate agent files"""
    agents_dir = root_dir / "agents"
    if not agents_dir.exists():
        return {"status": "missing"}
    
    agent_files = list(agents_dir.glob("**/*.md"))
    return {
        "status": "found",
        "count": len(agent_files),
        "files": [f.name for f in agent_files]
    }

def validate_commands(root_dir):
    """Validate command files"""
    commands_dir = root_dir / "commands"
    if not commands_dir.exists():
        return {"status": "missing"}
    
    command_files = list(commands_dir.glob("**/*.md"))
    return {
        "status": "found", 
        "count": len(command_files),
        "files": [f.name for f in command_files]
    }

def validate_hooks(root_dir):
    """Validate hook files"""
    hooks_dir = root_dir / "hooks"
    if not hooks_dir.exists():
        return {"status": "missing"}
    
    hook_files = list(hooks_dir.glob("**/*.py"))
    return {
        "status": "found",
        "count": len(hook_files),
        "files": [f.name for f in hook_files]
    }

def validate_integrations(root_dir):
    """Validate integration files"""
    integrations_dir = root_dir / "integrations"
    if not integrations_dir.exists():
        return {"status": "missing"}
    
    integration_files = list(integrations_dir.glob("**/*"))
    return {
        "status": "found",
        "count": len(integration_files),
        "files": [f.name for f in integration_files]
    }

if __name__ == "__main__":
    results = validate_consolidation()
    print("Consolidation Validation Results:")
    print("=" * 40)
    for check, result in results.items():
        print(f"{check}: {result}")
'''
        
        with open(validation_script, 'w') as f:
            f.write(validation_code)
        
        validation_script.chmod(0o755)
        self.log(f"Created validation script: {validation_script}")
    
    def cleanup_v3_directory(self):
        """Clean up the original v3 directory after successful consolidation"""
        self.log("Cleaning up v3 directory...")
        
        try:
            if self.v3_dir.exists():
                # Keep only essential files for reference
                essential_files = [
                    "MASTER_SPEC_V3.md",
                    "README.md",
                    "VALIDATION_REPORT.md"
                ]
                
                cleanup_dir = self.root_dir / "v3_cleanup_temp"
                cleanup_dir.mkdir(exist_ok=True)
                
                for file_name in essential_files:
                    src_file = self.v3_dir / file_name
                    if src_file.exists():
                        shutil.copy2(src_file, cleanup_dir / file_name)
                
                # Remove v3 directory
                shutil.rmtree(self.v3_dir)
                
                # Move essential files back
                reference_dir = self.root_dir / "v3_reference"
                reference_dir.mkdir(exist_ok=True)
                
                for file_path in cleanup_dir.iterdir():
                    shutil.move(file_path, reference_dir / file_path.name)
                
                cleanup_dir.rmdir()
                
                self.log("v3 directory cleaned up, reference files preserved")
                
        except Exception as e:
            self.log(f"Cleanup failed: {e}", "WARNING")
    
    def generate_migration_report(self):
        """Generate comprehensive migration report"""
        report_path = self.root_dir / "CONSOLIDATION_REPORT.md"
        
        report_content = f"""# Claude Code Dev Stack v3 Consolidation Report

## Migration Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Backup Location**: {self.backup_dir}
- **Status**: Completed

## Path Mappings
```json
{json.dumps(self.path_mappings, indent=2)}
```

## Migration Log
```
{chr(10).join(self.migration_log)}
```

## Validation
Run the validation script to verify consolidation:
```bash
python scripts/validate_consolidation.py
```

## Rollback Instructions
If issues are found, restore from backup:
```bash
# Remove consolidated files
rm -rf agents commands hooks audio orchestration integrations testing apps

# Restore from backup
cp -r {self.backup_dir}/root_structure/* .
cp -r {self.backup_dir}/v3_structure ./Claude_Code_Dev_Stack_v3
```

## Next Steps
1. Run validation script
2. Test all functionality
3. Update documentation
4. Remove backup after verification
"""
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        self.log(f"Migration report generated: {report_path}")
    
    def consolidate(self):
        """Main consolidation process"""
        self.log("Starting Claude Code Dev Stack v3 Consolidation")
        
        # Step 1: Create backup
        if not self.create_backup():
            return False
        
        # Step 2: Analyze structure
        analysis = self.analyze_structure()
        self.log(f"Analysis complete. Found {len(analysis['conflicts'])} conflicts")
        
        # Step 3: Execute migration
        if not self.execute_migration(analysis['migration_plan']):
            self.log("Migration failed", "ERROR")
            return False
        
        # Step 4: Update path references
        self.update_path_references()
        
        # Step 5: Create validation
        self.create_consolidation_validation()
        
        # Step 6: Generate report
        self.generate_migration_report()
        
        # Step 7: Cleanup (optional)
        # self.cleanup_v3_directory()  # Uncomment after validation
        
        self.log("Consolidation completed successfully!")
        return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = Path(__file__).parent.parent
    
    consolidator = V3Consolidator(root_dir)
    success = consolidator.consolidate()
    
    if success:
        print("\n" + "="*50)
        print("CONSOLIDATION COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Backup created at: {consolidator.backup_dir}")
        print("Run validation script to verify consolidation")
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("CONSOLIDATION FAILED")
        print("="*50)
        print("Check logs and restore from backup if needed")
        sys.exit(1)

if __name__ == "__main__":
    main()