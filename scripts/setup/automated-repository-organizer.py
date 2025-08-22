#!/usr/bin/env python3
"""
Automated Repository Organizer for V3.6.9
Master script that orchestrates the complete repository cleanup and organization process.
"""

import os
import sys
import subprocess
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedRepositoryOrganizer:
    def __init__(self, base_path: str, dry_run: bool = False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.scripts_dir = self.base_path / "scripts"
        self.backup_dir = self.base_path / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure scripts directory exists
        self.scripts_dir.mkdir(exist_ok=True)
        
        self.execution_log = {
            "start_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "steps_completed": [],
            "errors": [],
            "warnings": [],
            "backup_created": False
        }
    
    def create_backup(self) -> bool:
        """Create a full backup before starting cleanup."""
        if self.dry_run:
            logger.info("DRY RUN: Would create backup of repository")
            return True
        
        try:
            logger.info(f"Creating backup at: {self.backup_dir}")
            
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy critical directories and files
            critical_paths = [
                "core/agents",
                "apps",
                "bin",
                "config",
                "lib",
                "integrations",
                "package.json",
                "index.js"
            ]
            
            for path in critical_paths:
                source_path = self.base_path / path
                if source_path.exists():
                    dest_path = self.backup_dir / path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_file():
                        shutil.copy2(source_path, dest_path)
                    else:
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    
                    logger.info(f"Backed up: {path}")
            
            self.execution_log["backup_created"] = True
            self.execution_log["backup_path"] = str(self.backup_dir)
            logger.info("Backup created successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def run_repository_cleanup(self) -> bool:
        """Run the main repository cleanup script."""
        try:
            cleanup_script = self.scripts_dir / "repository-cleanup.py"
            
            if self.dry_run:
                logger.info("DRY RUN: Would run repository cleanup")
                return True
            
            if not cleanup_script.exists():
                error_msg = "Repository cleanup script not found"
                logger.error(error_msg)
                self.execution_log["errors"].append(error_msg)
                return False
            
            logger.info("Running repository cleanup...")
            
            # Make script executable
            cleanup_script.chmod(0o755)
            
            # Run the cleanup script
            result = subprocess.run([
                sys.executable, str(cleanup_script), str(self.base_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Repository cleanup completed successfully")
                self.execution_log["steps_completed"].append("repository_cleanup")
                return True
            else:
                error_msg = f"Repository cleanup failed: {result.stderr}"
                logger.error(error_msg)
                self.execution_log["errors"].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error running repository cleanup: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def create_automation_scripts(self) -> bool:
        """Create additional automation scripts for ongoing maintenance."""
        try:
            if self.dry_run:
                logger.info("DRY RUN: Would create automation scripts")
                return True
            
            # Create git hooks for automatic organization
            self._create_git_hooks()
            
            # Create cron/scheduled task scripts
            self._create_scheduled_scripts()
            
            # Create developer workflow scripts
            self._create_workflow_scripts()
            
            logger.info("Automation scripts created successfully")
            self.execution_log["steps_completed"].append("automation_scripts")
            return True
            
        except Exception as e:
            error_msg = f"Error creating automation scripts: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def _create_git_hooks(self):
        """Create git hooks for automatic organization."""
        hooks_dir = self.base_path / ".git" / "hooks"
        
        if not hooks_dir.exists():
            logger.warning("Git hooks directory not found, skipping git hooks creation")
            return
        
        # Pre-commit hook to validate agent file placement
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# Pre-commit hook to validate agent file organization

echo "Validating agent file organization..."

# Check if any agent files are in wrong locations
python3 scripts/maintenance-cleanup.py validate-only

if [ $? -ne 0 ]; then
    echo "❌ Agent files are not properly organized!"
    echo "Run: python3 scripts/maintenance-cleanup.py"
    exit 1
fi

echo "✅ Agent organization validated"
"""
        
        with open(pre_commit_hook, 'w', encoding='utf-8') as f:
            f.write(pre_commit_content)
        pre_commit_hook.chmod(0o755)
        
        # Post-commit hook for cleanup
        post_commit_hook = hooks_dir / "post-commit"
        post_commit_content = """#!/bin/bash
# Post-commit hook for light cleanup

echo "Running post-commit cleanup..."
python3 scripts/maintenance-cleanup.py --light-cleanup
"""
        
        with open(post_commit_hook, 'w', encoding='utf-8') as f:
            f.write(post_commit_content)
        post_commit_hook.chmod(0o755)
        
        logger.info("Git hooks created")
    
    def _create_scheduled_scripts(self):
        """Create scripts for scheduled maintenance."""
        
        # Weekly maintenance script
        weekly_script = self.scripts_dir / "weekly-maintenance.py"
        weekly_content = """#!/usr/bin/env python3
\"\"\"Weekly maintenance script for repository cleanup.\"\"\"

import os
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from maintenance_cleanup import MaintenanceCleanup

def main():
    base_path = Path(__file__).parent.parent
    maintenance = MaintenanceCleanup(str(base_path))
    
    print("Running weekly maintenance...")
    report_path = maintenance.run_maintenance()
    print(f"Weekly maintenance completed. Report: {report_path}")

if __name__ == "__main__":
    main()
"""
        
        with open(weekly_script, 'w', encoding='utf-8') as f:
            f.write(weekly_content)
        weekly_script.chmod(0o755)
        
        # Create platform-specific scheduler files
        if os.name == 'nt':  # Windows
            self._create_windows_task()
        else:  # Unix-like
            self._create_cron_script()
    
    def _create_windows_task(self):
        """Create Windows Task Scheduler script."""
        task_script = self.scripts_dir / "setup-windows-task.bat"
        task_content = f"""@echo off
REM Setup Windows Task for weekly maintenance

schtasks /create /tn "Repository Maintenance" /tr "python {self.scripts_dir / 'weekly-maintenance.py'}" /sc weekly /d SUN /st 02:00 /f

echo Windows Task created for weekly repository maintenance
pause
"""
        
        with open(task_script, 'w', encoding='utf-8') as f:
            f.write(task_content)
    
    def _create_cron_script(self):
        """Create cron setup script for Unix-like systems."""
        cron_script = self.scripts_dir / "setup-cron.sh"
        cron_content = f"""#!/bin/bash
# Setup cron job for weekly maintenance

# Add cron job (runs every Sunday at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * 0 python3 {self.scripts_dir / 'weekly-maintenance.py'}") | crontab -

echo "Cron job setup for weekly repository maintenance"
"""
        
        with open(cron_script, 'w', encoding='utf-8') as f:
            f.write(cron_content)
        cron_script.chmod(0o755)
    
    def _create_workflow_scripts(self):
        """Create developer workflow scripts."""
        
        # Quick cleanup script for developers
        quick_clean = self.scripts_dir / "quick-clean.py"
        quick_content = """#!/usr/bin/env python3
\"\"\"Quick cleanup script for developers.\"\"\"

import os
import shutil
from pathlib import Path

def quick_clean():
    base_path = Path.cwd()
    
    # Quick cache cleanup
    cache_patterns = ["__pycache__", "*.pyc", ".mypy_cache", "node_modules/.cache"]
    
    print("Running quick cleanup...")
    
    for pattern in cache_patterns:
        for path in base_path.rglob(pattern):
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"Removed: {path}")
                except:
                    pass
            elif path.is_file():
                try:
                    path.unlink()
                    print(f"Removed: {path}")
                except:
                    pass
    
    print("Quick cleanup completed!")

if __name__ == "__main__":
    quick_clean()
"""
        
        with open(quick_clean, 'w', encoding='utf-8') as f:
            f.write(quick_content)
        quick_clean.chmod(0o755)
        
        # Agent organization validator
        validator_script = self.scripts_dir / "validate-organization.py"
        validator_content = """#!/usr/bin/env python3
\"\"\"Validate repository organization.\"\"\"

import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from maintenance_cleanup import MaintenanceCleanup

def main():
    base_path = Path(__file__).parent.parent
    maintenance = MaintenanceCleanup(str(base_path))
    
    validation = maintenance.validate_agent_hierarchy()
    
    issues_found = False
    
    if validation["orphaned_agents"]:
        print("❌ Orphaned agents found:")
        for agent in validation["orphaned_agents"]:
            print(f"  - {agent}")
        issues_found = True
    
    if validation["missing_agents"]:
        print("❌ Missing agents:")
        for agent in validation["missing_agents"]:
            print(f"  - {agent}")
        issues_found = True
    
    if not issues_found:
        print("✅ Repository organization is valid")
        sys.exit(0)
    else:
        print("\\n🔧 Run maintenance script to fix issues:")
        print("python scripts/maintenance-cleanup.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        with open(validator_script, 'w', encoding='utf-8') as f:
            f.write(validator_content)
        validator_script.chmod(0o755)
    
    def create_documentation(self) -> bool:
        """Create comprehensive documentation for the organized repository."""
        try:
            if self.dry_run:
                logger.info("DRY RUN: Would create documentation")
                return True
            
            # Create main organization guide
            org_guide = self.base_path / "ORGANIZATION_GUIDE.md"
            
            guide_content = """# Repository Organization Guide

## Overview
This repository follows a hierarchical tier-based structure for Claude Code Agents V3.6.9.

## Directory Structure

### Core Agent Hierarchy
```
core/agents/
├── tier0_coordination/     # Master Orchestration (Tier 0)
│   ├── master-orchestrator.md
│   └── ceo-strategy.md
├── tier1_orchestration/    # Strategic Management (Tier 1)
│   ├── technical-cto.md
│   ├── project-manager.md
│   └── business-tech-alignment.md
├── tier2_teams/           # Specialized Teams (Tier 2)
│   ├── analysis/
│   │   ├── business-analyst.md
│   │   └── financial-analyst.md
│   ├── design/
│   │   ├── ui-ux-design.md
│   │   ├── frontend-architecture.md
│   │   ├── database-architecture.md
│   │   └── security-architecture.md
│   ├── implementation/
│   │   ├── backend-services.md
│   │   ├── frontend-mockup.md
│   │   ├── production-frontend.md
│   │   ├── mobile-development.md
│   │   └── integration-setup.md
│   ├── operations/
│   │   ├── devops-engineering.md
│   │   ├── script-automation.md
│   │   └── performance-optimization.md
│   └── quality/
│       ├── quality-assurance.md
│       ├── testing-automation.md
│       └── technical-specifications.md
└── tier3_specialists/     # Individual Specialists (Tier 3)
    ├── analysis/
    │   └── prompt-engineer.md
    ├── design/
    │   └── middleware-specialist.md
    └── implementation/
        └── api-integration-specialist.md
```

### Other Key Directories
```
├── apps/                  # Application implementations
│   ├── web/              # Web application
│   ├── mobile/           # Mobile application
│   ├── backend/          # Backend services
│   └── pwa/              # Progressive Web App components
├── scripts/              # Automation and maintenance scripts
├── core/                 # Core framework components
│   ├── audio/            # Audio processing
│   ├── hooks/            # Git hooks and integrations
│   └── generators/       # Code generators
├── archive/              # Archived files and old versions
└── backup/               # Automatic backups
```

## Maintenance Scripts

### Daily Use
- `scripts/quick-clean.py` - Quick cache cleanup for developers
- `scripts/validate-organization.py` - Check repository organization

### Weekly Maintenance
- `scripts/weekly-maintenance.py` - Comprehensive cleanup
- `scripts/maintenance-cleanup.py` - Full maintenance routine

### Setup Scripts
- `scripts/repository-cleanup.py` - Initial organization (run once)
- `scripts/automated-repository-organizer.py` - Master orchestrator

## Git Hooks
Automatic hooks are installed for:
- **Pre-commit**: Validates agent file placement
- **Post-commit**: Runs light cleanup

## Scheduled Maintenance
- Weekly cleanup runs automatically (configured via cron/Task Scheduler)
- Large files and cache directories are monitored
- Old logs are automatically archived

## Best Practices

1. **Agent Files**: Always place agent files in their correct tier directory
2. **Temporary Files**: Use `.tmp` extension for temporary files
3. **Cache**: Let the system manage cache cleanup automatically
4. **Backups**: Automatic backups are created before major changes
5. **Validation**: Run `validate-organization.py` before committing

## Troubleshooting

### Orphaned Agent Files
If agents are in the wrong location, run:
```bash
python scripts/maintenance-cleanup.py
```

### Missing Dependencies
Ensure all required Python packages are installed:
```bash
pip install -r requirements.txt
```

### Permission Issues
Make scripts executable:
```bash
chmod +x scripts/*.py
```

## Archive Policy
- Old versions automatically moved to `archive/`
- Duplicates detected and archived
- Large files flagged for review
- Log retention: 30 days (configurable)
"""
            
            with open(org_guide, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            logger.info("Documentation created successfully")
            self.execution_log["steps_completed"].append("documentation")
            return True
            
        except Exception as e:
            error_msg = f"Error creating documentation: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def validate_final_state(self) -> bool:
        """Validate the final state of the organized repository."""
        try:
            validation_issues = []
            
            # Check critical directories exist
            critical_dirs = [
                "core/agents/tier0_coordination",
                "core/agents/tier1_orchestration", 
                "core/agents/tier2_teams",
                "core/agents/tier3_specialists",
                "scripts",
                "archive"
            ]
            
            for dir_path in critical_dirs:
                full_path = self.base_path / dir_path
                if not full_path.exists():
                    validation_issues.append(f"Missing directory: {dir_path}")
            
            # Check critical files exist
            critical_files = [
                "scripts/repository-cleanup.py",
                "scripts/maintenance-cleanup.py",
                "ORGANIZATION_GUIDE.md"
            ]
            
            for file_path in critical_files:
                full_path = self.base_path / file_path
                if not full_path.exists():
                    validation_issues.append(f"Missing file: {file_path}")
            
            if validation_issues:
                for issue in validation_issues:
                    logger.warning(issue)
                    self.execution_log["warnings"].extend(validation_issues)
                return False
            
            logger.info("Repository organization validation passed")
            self.execution_log["steps_completed"].append("validation")
            return True
            
        except Exception as e:
            error_msg = f"Error validating final state: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        self.execution_log["end_time"] = datetime.now().isoformat()
        
        # Save JSON report
        report_path = self.base_path / "organization_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.execution_log, f, indent=2)
        
        # Generate human-readable summary
        summary_path = self.base_path / "ORGANIZATION_COMPLETE.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Repository Organization Complete ✅\\n\\n")
            f.write(f"**Completion Time:** {self.execution_log['end_time']}\\n\\n")
            
            if self.dry_run:
                f.write("**Mode:** Dry Run (no changes made)\\n\\n")
            
            f.write("## Steps Completed\\n")
            for step in self.execution_log["steps_completed"]:
                f.write(f"- ✅ {step.replace('_', ' ').title()}\\n")
            
            if self.execution_log["warnings"]:
                f.write("\\n## Warnings\\n")
                for warning in self.execution_log["warnings"]:
                    f.write(f"- ⚠️ {warning}\\n")
            
            if self.execution_log["errors"]:
                f.write("\\n## Errors\\n")
                for error in self.execution_log["errors"]:
                    f.write(f"- ❌ {error}\\n")
            
            f.write("\\n## Next Steps\\n")
            f.write("1. Review the `ORGANIZATION_GUIDE.md` for usage instructions\\n")
            f.write("2. Set up scheduled maintenance (run setup scripts in `scripts/`)\\n")
            f.write("3. Validate organization with: `python scripts/validate-organization.py`\\n")
            f.write("4. Run weekly maintenance: `python scripts/weekly-maintenance.py`\\n")
            
            if self.execution_log["backup_created"]:
                f.write(f"\\n## Backup Location\\n")
                f.write(f"Full backup created at: `{self.execution_log.get('backup_path', 'N/A')}`\\n")
        
        logger.info(f"Organization report generated: {summary_path}")
    
    def run_complete_organization(self) -> bool:
        """Execute the complete repository organization process."""
        logger.info("Starting automated repository organization...")
        
        success = True
        
        # Step 1: Create backup
        if not self.create_backup():
            logger.error("Backup creation failed - aborting organization")
            return False
        
        # Step 2: Run repository cleanup
        if not self.run_repository_cleanup():
            logger.error("Repository cleanup failed")
            success = False
        
        # Step 3: Create automation scripts
        if not self.create_automation_scripts():
            logger.error("Automation scripts creation failed")
            success = False
        
        # Step 4: Create documentation
        if not self.create_documentation():
            logger.error("Documentation creation failed")
            success = False
        
        # Step 5: Validate final state
        if not self.validate_final_state():
            logger.warning("Final validation had issues")
        
        # Step 6: Generate final report
        self.generate_final_report()
        
        if success:
            logger.info("Repository organization completed successfully! 🎉")
        else:
            logger.warning("Repository organization completed with some issues")
        
        return success

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Repository Organizer for V3.6.9")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="Repository path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--backup", action="store_true", default=True, help="Create backup before organizing")
    
    args = parser.parse_args()
    
    organizer = AutomatedRepositoryOrganizer(args.path, args.dry_run)
    success = organizer.run_complete_organization()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()