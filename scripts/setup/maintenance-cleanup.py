#!/usr/bin/env python3
"""
Ongoing Maintenance Cleanup Script for V3.6.9
Performs regular maintenance tasks to keep the repository organized.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaintenanceCleanup:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.config_file = self.base_path / "scripts" / "maintenance-config.json"
        self.load_config()
        
    def load_config(self):
        """Load maintenance configuration."""
        default_config = {
            "cache_cleanup_days": 7,
            "log_retention_days": 30,
            "temp_file_patterns": ["*.tmp", "*.temp", "*~", ".DS_Store"],
            "cache_directories": ["__pycache__", ".mypy_cache", "node_modules", ".vite", "dist"],
            "excluded_paths": ["archive", ".git", "node_modules"],
            "auto_archive_patterns": ["*-old.*", "*-backup.*", "*.bak"],
            "file_size_threshold_mb": 100
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                logger.warning(f"Error loading config, using defaults: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def clean_cache_directories(self) -> List[str]:
        """Remove old cache directories."""
        removed_dirs = []
        cutoff_date = datetime.now() - timedelta(days=self.config["cache_cleanup_days"])
        
        for cache_pattern in self.config["cache_directories"]:
            for cache_dir in self.base_path.rglob(cache_pattern):
                if self._should_exclude_path(cache_dir):
                    continue
                    
                if cache_dir.is_dir():
                    try:
                        # Check if directory is old enough
                        mod_time = datetime.fromtimestamp(cache_dir.stat().st_mtime)
                        if mod_time < cutoff_date:
                            shutil.rmtree(str(cache_dir))
                            removed_dirs.append(str(cache_dir))
                            logger.info(f"Removed old cache directory: {cache_dir}")
                    except Exception as e:
                        logger.warning(f"Could not remove cache directory {cache_dir}: {e}")
        
        return removed_dirs
    
    def clean_temporary_files(self) -> List[str]:
        """Remove temporary files."""
        removed_files = []
        
        for pattern in self.config["temp_file_patterns"]:
            for temp_file in self.base_path.rglob(pattern):
                if self._should_exclude_path(temp_file) or not temp_file.is_file():
                    continue
                
                try:
                    temp_file.unlink()
                    removed_files.append(str(temp_file))
                    logger.info(f"Removed temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_file}: {e}")
        
        return removed_files
    
    def clean_old_logs(self) -> List[str]:
        """Remove old log files."""
        removed_logs = []
        cutoff_date = datetime.now() - timedelta(days=self.config["log_retention_days"])
        
        # Look for log files
        for log_file in self.base_path.rglob("*.log"):
            if self._should_exclude_path(log_file):
                continue
                
            try:
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mod_time < cutoff_date:
                    log_file.unlink()
                    removed_logs.append(str(log_file))
                    logger.info(f"Removed old log file: {log_file}")
            except Exception as e:
                logger.warning(f"Could not remove log file {log_file}: {e}")
        
        return removed_logs
    
    def auto_archive_files(self) -> List[str]:
        """Automatically archive files matching certain patterns."""
        archived_files = []
        archive_path = self.base_path / "archive" / "auto-archived" / datetime.now().strftime("%Y-%m")
        archive_path.mkdir(parents=True, exist_ok=True)
        
        for pattern in self.config["auto_archive_patterns"]:
            for file_path in self.base_path.rglob(pattern):
                if self._should_exclude_path(file_path) or not file_path.is_file():
                    continue
                
                try:
                    relative_path = file_path.relative_to(self.base_path)
                    archive_file_path = archive_path / relative_path
                    archive_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(file_path), str(archive_file_path))
                    archived_files.append(str(file_path))
                    logger.info(f"Auto-archived file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not archive file {file_path}: {e}")
        
        return archived_files
    
    def check_large_files(self) -> List[Dict]:
        """Identify files larger than threshold."""
        large_files = []
        threshold_bytes = self.config["file_size_threshold_mb"] * 1024 * 1024
        
        for file_path in self.base_path.rglob("*"):
            if self._should_exclude_path(file_path) or not file_path.is_file():
                continue
            
            try:
                file_size = file_path.stat().st_size
                if file_size > threshold_bytes:
                    large_files.append({
                        "path": str(file_path),
                        "size_mb": round(file_size / (1024 * 1024), 2)
                    })
            except Exception:
                continue
        
        return large_files
    
    def validate_agent_hierarchy(self) -> Dict:
        """Validate that agent files are in correct tier locations."""
        validation_report = {
            "misplaced_agents": [],
            "missing_agents": [],
            "orphaned_agents": []
        }
        
        # Expected structure
        expected_structure = {
            "tier0_coordination": ["master-orchestrator.md", "ceo-strategy.md"],
            "tier1_orchestration": ["technical-cto.md", "project-manager.md", "business-tech-alignment.md"],
            "tier2_teams": {
                "analysis": ["business-analyst.md", "financial-analyst.md"],
                "design": ["ui-ux-design.md", "frontend-architecture.md", "database-architecture.md", "security-architecture.md"],
                "implementation": ["backend-services.md", "frontend-mockup.md", "production-frontend.md", "mobile-development.md", "integration-setup.md"],
                "operations": ["devops-engineering.md", "script-automation.md", "performance-optimization.md"],
                "quality": ["quality-assurance.md", "testing-automation.md", "technical-specifications.md"]
            }
        }
        
        core_agents = self.base_path / "core" / "agents"
        
        # Check for misplaced agents in root
        for agent_file in core_agents.glob("*.md"):
            validation_report["orphaned_agents"].append(str(agent_file))
        
        # Check tier structure
        for tier, agents in expected_structure.items():
            if isinstance(agents, list):
                tier_path = core_agents / tier
                for agent in agents:
                    agent_path = tier_path / agent
                    if not agent_path.exists():
                        validation_report["missing_agents"].append(f"{tier}/{agent}")
            elif isinstance(agents, dict):
                for team, team_agents in agents.items():
                    team_path = core_agents / tier / team
                    for agent in team_agents:
                        agent_path = team_path / agent
                        if not agent_path.exists():
                            validation_report["missing_agents"].append(f"{tier}/{team}/{agent}")
        
        return validation_report
    
    def _should_exclude_path(self, path: Path) -> bool:
        """Check if path should be excluded from cleanup."""
        path_str = str(path)
        for excluded in self.config["excluded_paths"]:
            if excluded in path_str:
                return True
        return False
    
    def generate_maintenance_report(self, results: Dict) -> str:
        """Generate maintenance report."""
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_path = self.base_path / f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# Maintenance Report - {report_time}\n\n")
            
            f.write("## Cache Cleanup\n")
            if results["cache_dirs"]:
                f.write(f"Removed {len(results['cache_dirs'])} cache directories:\n")
                for cache_dir in results["cache_dirs"]:
                    f.write(f"- {cache_dir}\n")
            else:
                f.write("No cache directories to clean.\n")
            f.write("\n")
            
            f.write("## Temporary Files\n")
            if results["temp_files"]:
                f.write(f"Removed {len(results['temp_files'])} temporary files:\n")
                for temp_file in results["temp_files"]:
                    f.write(f"- {temp_file}\n")
            else:
                f.write("No temporary files to clean.\n")
            f.write("\n")
            
            f.write("## Log Files\n")
            if results["log_files"]:
                f.write(f"Removed {len(results['log_files'])} old log files:\n")
                for log_file in results["log_files"]:
                    f.write(f"- {log_file}\n")
            else:
                f.write("No old log files to clean.\n")
            f.write("\n")
            
            f.write("## Auto-Archived Files\n")
            if results["archived_files"]:
                f.write(f"Archived {len(results['archived_files'])} files:\n")
                for archived_file in results["archived_files"]:
                    f.write(f"- {archived_file}\n")
            else:
                f.write("No files auto-archived.\n")
            f.write("\n")
            
            f.write("## Large Files\n")
            if results["large_files"]:
                f.write("Files larger than threshold:\n")
                for large_file in results["large_files"]:
                    f.write(f"- {large_file['path']} ({large_file['size_mb']} MB)\n")
            else:
                f.write("No large files found.\n")
            f.write("\n")
            
            f.write("## Agent Hierarchy Validation\n")
            validation = results["validation"]
            if validation["orphaned_agents"]:
                f.write("Orphaned agents (should be moved to proper tier):\n")
                for orphan in validation["orphaned_agents"]:
                    f.write(f"- {orphan}\n")
            
            if validation["missing_agents"]:
                f.write("Missing agents from expected locations:\n")
                for missing in validation["missing_agents"]:
                    f.write(f"- {missing}\n")
            
            if not validation["orphaned_agents"] and not validation["missing_agents"]:
                f.write("Agent hierarchy is properly organized.\n")
        
        return str(report_path)
    
    def run_maintenance(self) -> str:
        """Run all maintenance tasks."""
        logger.info("Starting maintenance cleanup...")
        
        results = {
            "cache_dirs": self.clean_cache_directories(),
            "temp_files": self.clean_temporary_files(),
            "log_files": self.clean_old_logs(),
            "archived_files": self.auto_archive_files(),
            "large_files": self.check_large_files(),
            "validation": self.validate_agent_hierarchy()
        }
        
        report_path = self.generate_maintenance_report(results)
        logger.info(f"Maintenance completed. Report: {report_path}")
        
        return report_path

def main():
    """Main entry point for maintenance script."""
    import sys
    
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.getcwd()
    
    maintenance = MaintenanceCleanup(base_path)
    report_path = maintenance.run_maintenance()
    print(f"Maintenance report generated: {report_path}")

if __name__ == "__main__":
    main()