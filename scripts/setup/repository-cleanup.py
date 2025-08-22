#!/usr/bin/env python3
"""
Repository Cleanup and Organization Script for V3.6.9
Cleans and organizes the repository according to tier0-3 agent hierarchy structure.
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepositoryCleanup:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.archive_path = self.base_path / "archive"
        self.cleanup_report = {
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "duplicates_found": [],
            "files_archived": [],
            "directories_created": [],
            "errors": []
        }
        
        # Define agent hierarchy structure
        self.agent_hierarchy = {
            "tier0_coordination": [
                "master-orchestrator.md",
                "ceo-strategy.md"
            ],
            "tier1_orchestration": [
                "technical-cto.md",
                "project-manager.md",
                "business-tech-alignment.md"
            ],
            "tier2_teams": {
                "analysis": [
                    "business-analyst.md",
                    "financial-analyst.md"
                ],
                "design": [
                    "ui-ux-design.md",
                    "frontend-architecture.md",
                    "database-architecture.md",
                    "security-architecture.md"
                ],
                "implementation": [
                    "backend-services.md",
                    "frontend-mockup.md",
                    "production-frontend.md",
                    "mobile-development.md",
                    "integration-setup.md"
                ],
                "operations": [
                    "devops-engineering.md",
                    "script-automation.md",
                    "performance-optimization.md"
                ],
                "quality": [
                    "quality-assurance.md",
                    "testing-automation.md",
                    "technical-specifications.md"
                ]
            },
            "tier3_specialists": {
                "analysis": [
                    "prompt-engineer.md"
                ],
                "design": [
                    "middleware-specialist.md"
                ],
                "implementation": [
                    "api-integration-specialist.md"
                ],
                "operations": [],
                "quality": []
            }
        }
        
        # Define directories to clean
        self.cache_dirs = [
            "__pycache__",
            ".mypy_cache", 
            "node_modules",
            ".vite",
            "dist",
            "deps_temp_*"
        ]
        
        # Files to archive (v3 docs, duplicates, etc.)
        self.archive_patterns = [
            "v3-*.md",
            "*-copy.*",
            "*-old.*",
            "*-backup.*",
            "*.bak"
        ]

    def create_directory_structure(self):
        """Create the proper tier-based directory structure."""
        logger.info("Creating tier-based directory structure...")
        
        try:
            # Create archive directory
            self.archive_path.mkdir(exist_ok=True)
            self.cleanup_report["directories_created"].append(str(self.archive_path))
            
            # Create core agent structure
            core_agents = self.base_path / "core" / "agents"
            
            # Tier 0 - Coordination
            tier0_path = core_agents / "tier0_coordination"
            tier0_path.mkdir(parents=True, exist_ok=True)
            self.cleanup_report["directories_created"].append(str(tier0_path))
            
            # Tier 1 - Orchestration  
            tier1_path = core_agents / "tier1_orchestration"
            tier1_path.mkdir(parents=True, exist_ok=True)
            self.cleanup_report["directories_created"].append(str(tier1_path))
            
            # Tier 2 - Teams
            tier2_path = core_agents / "tier2_teams"
            for team in self.agent_hierarchy["tier2_teams"].keys():
                team_path = tier2_path / team
                team_path.mkdir(parents=True, exist_ok=True)
                self.cleanup_report["directories_created"].append(str(team_path))
            
            # Tier 3 - Specialists (already exists, ensure structure)
            tier3_path = core_agents / "tier3_specialists"
            for specialization in self.agent_hierarchy["tier3_specialists"].keys():
                spec_path = tier3_path / specialization
                spec_path.mkdir(parents=True, exist_ok=True)
                self.cleanup_report["directories_created"].append(str(spec_path))
            
            # Create organized structure for other components
            components = {
                "core/audio": ["recordings", "processors", "tts"],
                "core/hooks": ["git", "pre-commit", "post-commit"],
                "apps/pwa": ["components", "assets", "service-workers"],
                "automation": ["scripts", "pipelines", "monitors"]
            }
            
            for base_dir, subdirs in components.items():
                for subdir in subdirs:
                    dir_path = self.base_path / base_dir / subdir
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.cleanup_report["directories_created"].append(str(dir_path))
            
            logger.info("Directory structure created successfully")
            self.cleanup_report["actions"].append("Created tier-based directory structure")
            
        except Exception as e:
            error_msg = f"Error creating directory structure: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def organize_agent_files(self):
        """Move agent files to their proper tier-based locations."""
        logger.info("Organizing agent files by tier hierarchy...")
        
        try:
            core_agents = self.base_path / "core" / "agents"
            
            # Find all agent files in the root agents directory
            agent_files = list(core_agents.glob("*.md"))
            
            for agent_file in agent_files:
                target_location = self._get_agent_target_location(agent_file.name)
                
                if target_location:
                    target_path = core_agents / target_location / agent_file.name
                    
                    # Move the file if it's not already in the right place
                    if agent_file.parent != target_path.parent:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(agent_file), str(target_path))
                        logger.info(f"Moved {agent_file.name} to {target_location}")
                        self.cleanup_report["actions"].append(f"Moved {agent_file.name} to {target_location}")
                else:
                    # Archive unclassified agents
                    archive_agent_path = self.archive_path / "agents" / agent_file.name
                    archive_agent_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(agent_file), str(archive_agent_path))
                    logger.info(f"Archived unclassified agent: {agent_file.name}")
                    self.cleanup_report["files_archived"].append(str(agent_file))
            
        except Exception as e:
            error_msg = f"Error organizing agent files: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def _get_agent_target_location(self, filename: str) -> str:
        """Determine the target location for an agent file based on hierarchy."""
        
        # Check tier 0
        if filename in self.agent_hierarchy["tier0_coordination"]:
            return "tier0_coordination"
        
        # Check tier 1
        if filename in self.agent_hierarchy["tier1_orchestration"]:
            return "tier1_orchestration"
        
        # Check tier 2
        for team, agents in self.agent_hierarchy["tier2_teams"].items():
            if filename in agents:
                return f"tier2_teams/{team}"
        
        # Check tier 3
        for specialization, agents in self.agent_hierarchy["tier3_specialists"].items():
            if filename in agents:
                return f"tier3_specialists/{specialization}"
        
        return None

    def archive_duplicates_and_old_files(self):
        """Archive duplicate files and old documentation."""
        logger.info("Archiving duplicate and old files...")
        
        try:
            # Archive v3 documentation files
            v3_docs = list(self.base_path.glob("v3-*.md"))
            
            for doc in v3_docs:
                archive_doc_path = self.archive_path / "documentation" / doc.name
                archive_doc_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(doc), str(archive_doc_path))
                logger.info(f"Archived documentation: {doc.name}")
                self.cleanup_report["files_archived"].append(str(doc))
            
            # Archive other patterns
            for pattern in self.archive_patterns:
                for file_path in self.base_path.rglob(pattern):
                    if file_path.is_file() and "archive" not in str(file_path):
                        relative_path = file_path.relative_to(self.base_path)
                        archive_file_path = self.archive_path / relative_path
                        archive_file_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(archive_file_path))
                        logger.info(f"Archived file: {relative_path}")
                        self.cleanup_report["files_archived"].append(str(file_path))
            
        except Exception as e:
            error_msg = f"Error archiving files: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def clean_cache_directories(self):
        """Remove cache and temporary directories."""
        logger.info("Cleaning cache and temporary directories...")
        
        try:
            for cache_pattern in self.cache_dirs:
                for cache_dir in self.base_path.rglob(cache_pattern):
                    if cache_dir.is_dir() and "archive" not in str(cache_dir):
                        shutil.rmtree(str(cache_dir))
                        logger.info(f"Removed cache directory: {cache_dir}")
                        self.cleanup_report["actions"].append(f"Removed cache directory: {cache_dir}")
            
        except Exception as e:
            error_msg = f"Error cleaning cache directories: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def detect_and_handle_duplicates(self):
        """Detect and handle duplicate files."""
        logger.info("Detecting duplicate files...")
        
        try:
            file_hashes = {}
            duplicates = []
            
            # Scan for files and calculate hashes
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file() and "archive" not in str(file_path):
                    try:
                        import hashlib
                        hasher = hashlib.md5()
                        with open(file_path, 'rb') as f:
                            hasher.update(f.read())
                        file_hash = hasher.hexdigest()
                        
                        if file_hash in file_hashes:
                            duplicates.append((file_path, file_hashes[file_hash]))
                        else:
                            file_hashes[file_hash] = file_path
                    except Exception:
                        continue  # Skip files that can't be read
            
            # Handle duplicates
            for duplicate, original in duplicates:
                archive_dup_path = self.archive_path / "duplicates" / duplicate.name
                archive_dup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Add timestamp to avoid naming conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_dup_path = archive_dup_path.with_name(f"{duplicate.stem}_{timestamp}{duplicate.suffix}")
                
                shutil.move(str(duplicate), str(archive_dup_path))
                logger.info(f"Archived duplicate: {duplicate} (original: {original})")
                self.cleanup_report["duplicates_found"].append({
                    "duplicate": str(duplicate),
                    "original": str(original),
                    "archived_to": str(archive_dup_path)
                })
            
        except Exception as e:
            error_msg = f"Error detecting duplicates: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def organize_special_directories(self):
        """Organize audio files, PWA components, and other special directories."""
        logger.info("Organizing special directories...")
        
        try:
            # Organize audio files
            audio_source = self.base_path / "core" / "audio"
            if audio_source.exists():
                for audio_file in audio_source.glob("*.py"):
                    if "processor" in audio_file.name.lower():
                        target_dir = audio_source / "processors"
                    elif "tts" in audio_file.name.lower() or "speech" in audio_file.name.lower():
                        target_dir = audio_source / "tts"
                    else:
                        target_dir = audio_source / "recordings"
                    
                    target_dir.mkdir(exist_ok=True)
                    if audio_file.parent != target_dir:
                        shutil.move(str(audio_file), str(target_dir / audio_file.name))
                        self.cleanup_report["actions"].append(f"Organized audio file: {audio_file.name}")
            
            # Organize PWA components
            web_app = self.base_path / "apps" / "web"
            if web_app.exists():
                pwa_dir = self.base_path / "apps" / "pwa"
                pwa_dir.mkdir(exist_ok=True)
                
                # Move PWA-specific files
                pwa_files = ["manifest.json", "sw.js", "workbox-*.js"]
                for pattern in pwa_files:
                    for pwa_file in web_app.rglob(pattern):
                        target_path = pwa_dir / "service-workers" / pwa_file.name
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        if pwa_file.exists():
                            shutil.copy2(str(pwa_file), str(target_path))
                            self.cleanup_report["actions"].append(f"Organized PWA file: {pwa_file.name}")
            
        except Exception as e:
            error_msg = f"Error organizing special directories: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def generate_cleanup_report(self):
        """Generate a comprehensive cleanup report."""
        logger.info("Generating cleanup report...")
        
        self.cleanup_report["end_time"] = datetime.now().isoformat()
        
        report_path = self.base_path / "cleanup_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        # Generate human-readable summary
        summary_path = self.base_path / "CLEANUP_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Repository Cleanup Summary\n\n")
            f.write(f"**Cleanup Date:** {self.cleanup_report['start_time']}\n\n")
            f.write(f"## Actions Performed\n")
            for action in self.cleanup_report["actions"]:
                f.write(f"- {action}\n")
            
            f.write(f"\n## Files Archived ({len(self.cleanup_report['files_archived'])})\n")
            for archived in self.cleanup_report["files_archived"]:
                f.write(f"- {archived}\n")
            
            f.write(f"\n## Duplicates Found ({len(self.cleanup_report['duplicates_found'])})\n")
            for dup in self.cleanup_report["duplicates_found"]:
                f.write(f"- {dup['duplicate']} → {dup['archived_to']}\n")
            
            f.write(f"\n## New Directory Structure\n")
            f.write("```\n")
            f.write("core/\n")
            f.write("├── agents/\n")
            f.write("│   ├── tier0_coordination/    # Master orchestration\n")
            f.write("│   ├── tier1_orchestration/   # Strategic management\n")
            f.write("│   ├── tier2_teams/          # Specialized teams\n")
            f.write("│   │   ├── analysis/\n")
            f.write("│   │   ├── design/\n")
            f.write("│   │   ├── implementation/\n")
            f.write("│   │   ├── operations/\n")
            f.write("│   │   └── quality/\n")
            f.write("│   └── tier3_specialists/    # Individual specialists\n")
            f.write("├── audio/\n")
            f.write("│   ├── recordings/\n")
            f.write("│   ├── processors/\n")
            f.write("│   └── tts/\n")
            f.write("└── hooks/\n")
            f.write("    ├── git/\n")
            f.write("    ├── pre-commit/\n")
            f.write("    └── post-commit/\n")
            f.write("```\n")
            
            if self.cleanup_report["errors"]:
                f.write(f"\n## Errors Encountered\n")
                for error in self.cleanup_report["errors"]:
                    f.write(f"- {error}\n")
        
        logger.info(f"Cleanup report generated: {summary_path}")

    def run_cleanup(self):
        """Execute the complete cleanup process."""
        logger.info("Starting repository cleanup and organization...")
        
        try:
            self.create_directory_structure()
            self.organize_agent_files()
            self.archive_duplicates_and_old_files()
            self.clean_cache_directories()
            self.detect_and_handle_duplicates()
            self.organize_special_directories()
            self.generate_cleanup_report()
            
            logger.info("Repository cleanup completed successfully!")
            
        except Exception as e:
            error_msg = f"Critical error during cleanup: {str(e)}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)
            self.generate_cleanup_report()

def main():
    """Main entry point for the cleanup script."""
    import sys
    
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        # Use current directory
        base_path = os.getcwd()
    
    cleanup = RepositoryCleanup(base_path)
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()