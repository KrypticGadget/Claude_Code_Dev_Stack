#!/usr/bin/env python3
"""
Claude Code Dev Stack - Cleanup Automation Script
Comprehensive archive and cleanup automation for legacy files and test results.

Generated: August 16, 2025
Version: 1.0
"""

import os
import shutil
import json
import glob
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CleanupAutomation:
    """Automated cleanup and archival system for Claude Code Dev Stack."""
    
    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.archive_root = self.project_root / "ARCHIVE"
        self.dry_run = dry_run
        self.cleanup_report = {
            "execution_date": datetime.now().isoformat(),
            "dry_run": dry_run,
            "files_processed": 0,
            "files_archived": 0,
            "files_deleted": 0,
            "space_recovered": 0,
            "errors": [],
            "operations": []
        }
        
        # Define file patterns for cleanup
        self.cleanup_patterns = {
            "test_results": {
                "patterns": ["*test*results*.json", "*_test_*.json", "validation_results.json"],
                "archive_path": "test-results",
                "action": "archive",
                "description": "Test result JSON files"
            },
            "log_files": {
                "patterns": ["*.log"],
                "archive_path": "logs",
                "action": "archive_if_not_empty",
                "description": "Log files"
            },
            "cache_dirs": {
                "patterns": ["__pycache__"],
                "archive_path": None,
                "action": "delete",
                "description": "Python cache directories"
            },
            "node_modules": {
                "patterns": ["node_modules"],
                "archive_path": None,
                "action": "skip",  # Too large, handled separately
                "description": "Node.js dependencies"
            },
            "venv_dirs": {
                "patterns": [".venv", "venv"],
                "archive_path": None,
                "action": "validate_and_skip",  # Need manual review
                "description": "Python virtual environments"
            },
            "legacy_scripts": {
                "patterns": [
                    "launch_mobile.bat", "launch_mobile.sh", "LAUNCH_MOBILE_NOW.ps1",
                    "setup_ngrok.ps1", "cleanup_audio.ps1", "remove_duplicates.ps1"
                ],
                "archive_path": "legacy-scripts",
                "action": "archive",
                "description": "Legacy launcher and setup scripts"
            },
            "development_tests": {
                "patterns": [
                    "test_agents_simple.py", "test_all_agents_v3.py", "test_agent_routing.py",
                    "test_audio_system.py", "test_error_handling.py", 
                    "comprehensive_hook_test_framework.py", "test-installer.ps1"
                ],
                "archive_path": "development-tests",
                "action": "archive",
                "description": "Development and testing scripts"
            },
            "validation_scripts": {
                "patterns": [
                    "platform_validator.py", "validate_audio_system.py", 
                    "validate_system_demo.py", "final_demo.py",
                    "final_security_assessment.py", "validate-installers.sh"
                ],
                "archive_path": "validation-scripts",
                "action": "archive",
                "description": "System validation and demo scripts"
            },
            "legacy_docs": {
                "patterns": [
                    "test_orchestration_command.md", "V3_TEST_PROMPTS.md",
                    "V3_COMPLETE_SYSTEM_TEST.md", "COMPLETE_TODO_LIST_V3_PHASES_3-10.md"
                ],
                "archive_path": "documentation/development-notes",
                "action": "archive",
                "description": "Legacy development documentation"
            }
        }
    
    def ensure_archive_structure(self) -> bool:
        """Create archive directory structure if it doesn't exist."""
        try:
            archive_dirs = [
                "test-results",
                "logs", 
                "legacy-scripts",
                "development-tests/agent-testing",
                "development-tests/system-validation",
                "validation-scripts",
                "documentation/development-notes",
                "documentation/v2-era",
                "documentation/completed-todos"
            ]
            
            for dir_path in archive_dirs:
                full_path = self.archive_root / dir_path
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created archive directory: {full_path}")
                else:
                    logger.info(f"[DRY RUN] Would create: {full_path}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create archive structure: {e}")
            return False
    
    def generate_metadata(self, file_path: Path, category: str) -> Dict:
        """Generate metadata for archived file."""
        try:
            stat = file_path.stat()
            return {
                "archive_date": datetime.now().isoformat(),
                "original_location": str(file_path.relative_to(self.project_root)),
                "category": category,
                "file_info": {
                    "size_bytes": stat.st_size,
                    "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "format": file_path.suffix.upper().lstrip('.') or "UNKNOWN"
                },
                "preservation_reason": self.cleanup_patterns[category]["description"]
            }
        except Exception as e:
            logger.error(f"Failed to generate metadata for {file_path}: {e}")
            return {}
    
    def archive_file(self, file_path: Path, category: str) -> bool:
        """Archive a single file with metadata."""
        try:
            archive_subdir = self.cleanup_patterns[category]["archive_path"]
            if not archive_subdir:
                return False
            
            # Determine archive location
            archive_dir = self.archive_root / archive_subdir
            
            # Add date subdirectory for test results
            if category == "test_results":
                date_str = datetime.now().strftime("%Y-%m-%d")
                archive_dir = archive_dir / date_str
            
            # Create target path
            target_path = archive_dir / file_path.name
            
            if not self.dry_run:
                # Ensure directory exists
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(file_path), str(target_path))
                
                # Generate and save metadata
                metadata = self.generate_metadata(file_path, category)
                metadata_path = target_path.with_suffix(target_path.suffix + '.metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Archived: {file_path} -> {target_path}")
            else:
                logger.info(f"[DRY RUN] Would archive: {file_path} -> {target_path}")
            
            self.cleanup_report["files_archived"] += 1
            self.cleanup_report["operations"].append({
                "action": "archive",
                "source": str(file_path),
                "target": str(target_path) if not self.dry_run else "DRY_RUN",
                "category": category
            })
            
            return True
        except Exception as e:
            error_msg = f"Failed to archive {file_path}: {e}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)
            return False
    
    def delete_file_or_dir(self, path: Path, category: str) -> bool:
        """Delete a file or directory."""
        try:
            size = self.get_size(path)
            
            if not self.dry_run:
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Deleted directory: {path}")
                else:
                    path.unlink()
                    logger.info(f"Deleted file: {path}")
            else:
                logger.info(f"[DRY RUN] Would delete: {path}")
            
            self.cleanup_report["files_deleted"] += 1
            self.cleanup_report["space_recovered"] += size
            self.cleanup_report["operations"].append({
                "action": "delete",
                "target": str(path),
                "category": category,
                "size_recovered": size
            })
            
            return True
        except Exception as e:
            error_msg = f"Failed to delete {path}: {e}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)
            return False
    
    def get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                total = 0
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
                return total
            return 0
        except Exception:
            return 0
    
    def find_files_by_patterns(self, patterns: List[str], search_dir: Path = None) -> List[Path]:
        """Find files matching given patterns."""
        if search_dir is None:
            search_dir = self.project_root
        
        found_files = []
        for pattern in patterns:
            # Search in root directory only (not recursively for now)
            matches = list(search_dir.glob(pattern))
            found_files.extend(matches)
        
        return found_files
    
    def validate_virtual_environments(self) -> List[Path]:
        """Identify and validate virtual environment directories."""
        venv_dirs = []
        
        # Find potential venv directories
        for pattern in ["venv", ".venv"]:
            matches = list(self.project_root.rglob(pattern))
            venv_dirs.extend(matches)
        
        # Report findings
        logger.info(f"Found {len(venv_dirs)} virtual environment directories:")
        for venv_dir in venv_dirs:
            size = self.get_size(venv_dir)
            logger.info(f"  {venv_dir} ({size / (1024*1024):.1f} MB)")
        
        return venv_dirs
    
    def clean_cache_directories(self) -> bool:
        """Clean Python cache directories."""
        cache_dirs = list(self.project_root.rglob("__pycache__"))
        
        logger.info(f"Found {len(cache_dirs)} cache directories")
        
        for cache_dir in cache_dirs:
            self.delete_file_or_dir(cache_dir, "cache_dirs")
        
        return True
    
    def process_category(self, category: str, config: Dict) -> bool:
        """Process files for a specific category."""
        logger.info(f"Processing category: {category}")
        
        files = self.find_files_by_patterns(config["patterns"])
        logger.info(f"Found {len(files)} files for {category}")
        
        for file_path in files:
            self.cleanup_report["files_processed"] += 1
            
            if config["action"] == "archive":
                self.archive_file(file_path, category)
            elif config["action"] == "delete":
                self.delete_file_or_dir(file_path, category)
            elif config["action"] == "archive_if_not_empty":
                if file_path.stat().st_size > 0:
                    self.archive_file(file_path, category)
                else:
                    self.delete_file_or_dir(file_path, category)
            elif config["action"] == "skip":
                logger.info(f"Skipping {file_path} (requires manual handling)")
            elif config["action"] == "validate_and_skip":
                logger.info(f"Virtual environment found: {file_path} (requires manual review)")
        
        return True
    
    def create_readme_files(self) -> bool:
        """Create README files for archive directories."""
        readme_content = {
            "test-results": """# Test Results Archive

This directory contains archived test results from Claude Code Dev Stack development.

## Organization
- Files are organized by date of execution
- Each test result file has accompanying metadata
- Results are preserved for debugging and regression analysis

## File Types
- `*test*results*.json`: Comprehensive test execution results
- `*.metadata.json`: File metadata and context information

## Usage
To reference historical test results:
1. Check the date-based subdirectories
2. Review metadata files for context
3. Use results for debugging or comparison with current tests
""",
            "legacy-scripts": """# Legacy Scripts Archive

This directory contains deprecated scripts and tools that have been replaced or are no longer actively used.

## Categories
- Mobile launchers: Old mobile app launch scripts
- Setup tools: Development environment setup utilities
- Cleanup scripts: File management and cleanup tools

## Important Notes
- These scripts are preserved for reference only
- Check DEPRECATION_NOTES.md for replacement information
- Do not use these scripts in current development
""",
            "development-tests": """# Development Tests Archive

This directory contains test scripts and frameworks used during development phases.

## Categories
- agent-testing/: Agent functionality testing scripts
- system-validation/: System-wide validation and testing
- platform-validation/: Cross-platform compatibility tests

## Usage Notes
- These scripts may be useful for reference when creating new tests
- Check metadata for dependencies and requirements
- Some scripts may need updates to work with current system
""",
            "documentation": """# Documentation Archive

This directory contains historical documentation and development notes.

## Organization
- development-notes/: Notes from development phases
- v2-era/: Documentation from V2 system
- completed-todos/: Archived TODO lists and task tracking

## Preservation Purpose
- Historical context for system evolution
- Reference for design decisions
- Debugging and troubleshooting context
"""
        }
        
        for dir_name, content in readme_content.items():
            readme_path = self.archive_root / dir_name / "README.md"
            
            if not self.dry_run:
                readme_path.parent.mkdir(parents=True, exist_ok=True)
                with open(readme_path, 'w') as f:
                    f.write(content)
                logger.info(f"Created README: {readme_path}")
            else:
                logger.info(f"[DRY RUN] Would create README: {readme_path}")
        
        return True
    
    def generate_cleanup_report(self) -> str:
        """Generate comprehensive cleanup report."""
        report_path = self.project_root / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add summary statistics
        self.cleanup_report["summary"] = {
            "total_files_processed": self.cleanup_report["files_processed"],
            "files_archived": self.cleanup_report["files_archived"],
            "files_deleted": self.cleanup_report["files_deleted"],
            "space_recovered_mb": round(self.cleanup_report["space_recovered"] / (1024*1024), 2),
            "errors_count": len(self.cleanup_report["errors"]),
            "success_rate": round(
                (self.cleanup_report["files_processed"] - len(self.cleanup_report["errors"])) 
                / max(self.cleanup_report["files_processed"], 1) * 100, 2
            ) if self.cleanup_report["files_processed"] > 0 else 100
        }
        
        if not self.dry_run:
            with open(report_path, 'w') as f:
                json.dump(self.cleanup_report, f, indent=2)
            logger.info(f"Cleanup report saved: {report_path}")
        else:
            logger.info(f"[DRY RUN] Would save report: {report_path}")
        
        return str(report_path)
    
    def run_cleanup(self, categories: List[str] = None) -> bool:
        """Run the complete cleanup process."""
        logger.info("Starting Claude Code Dev Stack cleanup automation")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Dry run mode: {self.dry_run}")
        
        try:
            # Ensure archive structure exists
            if not self.ensure_archive_structure():
                return False
            
            # Create README files
            self.create_readme_files()
            
            # Process each category
            categories_to_process = categories or list(self.cleanup_patterns.keys())
            
            for category in categories_to_process:
                if category in self.cleanup_patterns:
                    self.process_category(category, self.cleanup_patterns[category])
                else:
                    logger.warning(f"Unknown category: {category}")
            
            # Special handling for cache directories
            if "cache_dirs" in categories_to_process:
                self.clean_cache_directories()
            
            # Special handling for virtual environments (validation only)
            if "venv_dirs" in categories_to_process:
                self.validate_virtual_environments()
            
            # Generate cleanup report
            report_path = self.generate_cleanup_report()
            
            # Summary
            logger.info("Cleanup automation completed successfully")
            logger.info(f"Files processed: {self.cleanup_report['files_processed']}")
            logger.info(f"Files archived: {self.cleanup_report['files_archived']}")
            logger.info(f"Files deleted: {self.cleanup_report['files_deleted']}")
            logger.info(f"Space recovered: {self.cleanup_report['space_recovered'] / (1024*1024):.2f} MB")
            logger.info(f"Errors: {len(self.cleanup_report['errors'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"Cleanup automation failed: {e}")
            return False

def main():
    """Main entry point for cleanup automation."""
    parser = argparse.ArgumentParser(description="Claude Code Dev Stack Cleanup Automation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--categories", nargs="+", help="Specific categories to process")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize cleanup automation
    cleanup = CleanupAutomation(
        project_root=args.project_root,
        dry_run=args.dry_run
    )
    
    # Run cleanup
    success = cleanup.run_cleanup(categories=args.categories)
    
    if success:
        print("\nCleanup automation completed successfully!")
        if args.dry_run:
            print("This was a dry run - no files were actually moved or deleted.")
            print("Run without --dry-run to execute the cleanup.")
    else:
        print("Cleanup automation failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())