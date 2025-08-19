#!/usr/bin/env python3
"""
Claude Code Dev Stack V3.0 - Repository Cleanup Script
======================================================

This script safely cleans up cloned repositories after extraction is complete.
It performs backups, validates extractions, and documents all operations.

Author: Claude Code Script Automation Agent
Version: 3.0.0
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

class CleanupManager:
    """Manages the cleanup process for cloned repositories."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.clones_dir = self.project_root / "clones"
        self.backup_dir = self.project_root / "backups" / f"clones_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.manifest_file = self.project_root / "scripts" / "extraction_manifest.json"
        self.cleanup_log = self.project_root / "scripts" / "cleanup_log.json"
        
        # Initialize manifest data
        self.manifest = {
            "cleanup_date": datetime.now().isoformat(),
            "project_structure": {},
            "extracted_components": {},
            "backed_up_files": [],
            "deleted_repositories": [],
            "space_saved": {},
            "validation_results": {}
        }
    
    def analyze_project_structure(self) -> Dict[str, any]:
        """Analyze current project structure to document extractions."""
        print("📊 Analyzing project structure...")
        
        structure = {}
        key_directories = ["core", "integrations", "apps", "server", "ui", "platform-tools"]
        
        for dir_name in key_directories:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                structure[dir_name] = self._analyze_directory(dir_path)
        
        self.manifest["project_structure"] = structure
        return structure
    
    def _analyze_directory(self, directory: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, any]:
        """Recursively analyze directory structure."""
        if current_depth >= max_depth:
            return {"files": len(list(directory.glob("*")))}
        
        result = {
            "files": [],
            "subdirectories": {},
            "total_files": 0,
            "total_size": 0
        }
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    result["files"].append({
                        "name": item.name,
                        "size": size,
                        "type": item.suffix
                    })
                    result["total_size"] += size
                    result["total_files"] += 1
                elif item.is_dir() and not item.name.startswith('.'):
                    subdir_info = self._analyze_directory(item, max_depth, current_depth + 1)
                    result["subdirectories"][item.name] = subdir_info
                    result["total_files"] += subdir_info["total_files"]
                    result["total_size"] += subdir_info["total_size"]
        except PermissionError:
            result["error"] = "Permission denied"
        
        return result
    
    def identify_valuable_files(self) -> List[Tuple[Path, str]]:
        """Identify potentially valuable files in clones directory."""
        print("🔍 Identifying valuable files for backup...")
        
        valuable_files = []
        valuable_patterns = {
            "*.md": "documentation",
            "*.py": "python_code",
            "*.js": "javascript_code", 
            "*.ts": "typescript_code",
            "*.json": "configuration",
            "*.yaml": "configuration",
            "*.yml": "configuration",
            "*.toml": "configuration",
            "*.cfg": "configuration",
            "*.conf": "configuration",
            "LICENSE*": "license",
            "README*": "readme",
            "CHANGELOG*": "changelog",
            "*.sh": "scripts",
            "*.ps1": "scripts",
            "*.bat": "scripts",
            "Dockerfile*": "docker",
            "docker-compose*": "docker",
            "requirements.txt": "dependencies",
            "package.json": "dependencies",
            "Cargo.toml": "dependencies",
            "go.mod": "dependencies"
        }
        
        if not self.clones_dir.exists():
            print("⚠️  Clones directory not found")
            return valuable_files
        
        for repo_dir in self.clones_dir.iterdir():
            if not repo_dir.is_dir():
                continue
                
            print(f"  Scanning {repo_dir.name}...")
            
            for pattern, file_type in valuable_patterns.items():
                for file_path in repo_dir.rglob(pattern):
                    if file_path.is_file():
                        # Skip common build/cache directories
                        if any(part in str(file_path) for part in [
                            'node_modules', '.git', '__pycache__', '.pytest_cache',
                            'build', 'dist', 'target', '.venv', 'venv'
                        ]):
                            continue
                        
                        valuable_files.append((file_path, file_type))
        
        print(f"  Found {len(valuable_files)} valuable files")
        return valuable_files
    
    def create_backup(self, valuable_files: List[Tuple[Path, str]]) -> bool:
        """Create backup of valuable files."""
        if not valuable_files:
            print("ℹ️  No files to backup")
            return True
        
        print(f"💾 Creating backup of {len(valuable_files)} files...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create categorized backup structure
            categories = set(file_type for _, file_type in valuable_files)
            for category in categories:
                (self.backup_dir / category).mkdir(exist_ok=True)
            
            # Create ZIP archive for each repository
            repo_backups = {}
            for file_path, file_type in valuable_files:
                repo_name = None
                for part in file_path.parts:
                    if (self.clones_dir / part).exists():
                        repo_name = part
                        break
                
                if not repo_name:
                    continue
                
                if repo_name not in repo_backups:
                    repo_backups[repo_name] = zipfile.ZipFile(
                        self.backup_dir / f"{repo_name}_backup.zip", 'w', zipfile.ZIP_DEFLATED
                    )
                
                # Add file to ZIP with relative path
                rel_path = file_path.relative_to(self.clones_dir / repo_name)
                repo_backups[repo_name].write(file_path, rel_path)
                
                self.manifest["backed_up_files"].append({
                    "original_path": str(file_path),
                    "backup_path": f"{repo_name}_backup.zip/{rel_path}",
                    "type": file_type,
                    "size": file_path.stat().st_size,
                    "checksum": self._calculate_checksum(file_path)
                })
            
            # Close all ZIP files
            for zip_file in repo_backups.values():
                zip_file.close()
            
            print(f"✅ Backup created at {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "error"
    
    def validate_extractions(self) -> Dict[str, bool]:
        """Validate that key components have been properly extracted."""
        print("🔍 Validating extracted components...")
        
        validation_results = {}
        
        # Check for key extracted components
        expected_components = {
            "agents": self.project_root / "core" / "agents",
            "generators": self.project_root / "core" / "generators", 
            "mcp_integrations": self.project_root / "integrations",
            "web_app": self.project_root / "apps" / "web",
            "server": self.project_root / "server",
            "platform_tools": self.project_root / "platform-tools"
        }
        
        for component, path in expected_components.items():
            exists = path.exists()
            validation_results[component] = exists
            
            if exists:
                file_count = len(list(path.rglob("*"))) if path.is_dir() else 1
                print(f"  ✅ {component}: {file_count} items")
            else:
                print(f"  ❌ {component}: Missing")
        
        # Check for specific critical files
        critical_files = [
            "core/agents/agents/master-orchestrator.md",
            "integrations/mcp-manager/api/mcp_integration.py",
            "scripts/master-cleanup.js",
            "apps/web/package.json"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            validation_results[f"file_{file_path}"] = exists
            
            if exists:
                print(f"  ✅ {file_path}")
            else:
                print(f"  ⚠️  {file_path}: Missing")
        
        self.manifest["validation_results"] = validation_results
        return validation_results
    
    def calculate_space_savings(self) -> Dict[str, int]:
        """Calculate space that will be saved by cleanup."""
        print("📏 Calculating space savings...")
        
        space_info = {}
        
        if self.clones_dir.exists():
            total_size = 0
            repo_sizes = {}
            
            for repo_dir in self.clones_dir.iterdir():
                if repo_dir.is_dir():
                    repo_size = sum(f.stat().st_size for f in repo_dir.rglob('*') if f.is_file())
                    repo_sizes[repo_dir.name] = repo_size
                    total_size += repo_size
            
            space_info = {
                "total_bytes": total_size,
                "total_mb": round(total_size / (1024 * 1024), 2),
                "repository_sizes": repo_sizes
            }
            
            print(f"  Total space to be freed: {space_info['total_mb']} MB")
            for repo, size in repo_sizes.items():
                size_mb = round(size / (1024 * 1024), 2)
                print(f"    {repo}: {size_mb} MB")
        
        self.manifest["space_saved"] = space_info
        return space_info
    
    def perform_cleanup(self, force: bool = False) -> bool:
        """Perform the actual cleanup of clones directory."""
        if not self.clones_dir.exists():
            print("ℹ️  Clones directory not found, nothing to clean")
            return True
        
        if not force:
            print("\n🚨 CLEANUP CONFIRMATION")
            print(f"About to delete: {self.clones_dir}")
            print(f"Space to be freed: {self.manifest['space_saved'].get('total_mb', 0)} MB")
            print("This action cannot be undone!")
            
            response = input("\nProceed with cleanup? (yes/no): ").lower().strip()
            if response not in ['yes', 'y']:
                print("❌ Cleanup cancelled")
                return False
        
        print("🗑️  Performing cleanup...")
        
        try:
            # List repositories being deleted
            deleted_repos = []
            for repo_dir in self.clones_dir.iterdir():
                if repo_dir.is_dir():
                    deleted_repos.append({
                        "name": repo_dir.name,
                        "path": str(repo_dir),
                        "size": sum(f.stat().st_size for f in repo_dir.rglob('*') if f.is_file())
                    })
            
            self.manifest["deleted_repositories"] = deleted_repos
            
            # Remove the clones directory
            shutil.rmtree(self.clones_dir)
            
            print(f"✅ Successfully deleted {len(deleted_repos)} repositories")
            print(f"✅ Freed {self.manifest['space_saved'].get('total_mb', 0)} MB of space")
            
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files and build artifacts."""
        print("🧹 Cleaning up temporary files...")
        
        temp_patterns = [
            "**/.DS_Store",
            "**/*.tmp", 
            "**/*.temp",
            "**/*.log",
            "**/npm-debug.log*",
            "**/yarn-debug.log*",
            "**/yarn-error.log*",
            "**/.nyc_output",
            "**/coverage",
            "**/.pytest_cache",
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.sass-cache"
        ]
        
        deleted_count = 0
        deleted_size = 0
        
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern.split('/')[-1]):
                if any(part in str(file_path) for part in pattern.split('/')[:-1]):
                    try:
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            deleted_size += size
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                            deleted_count += 1
                    except Exception:
                        pass
        
        if deleted_count > 0:
            size_mb = round(deleted_size / (1024 * 1024), 2)
            print(f"  ✅ Deleted {deleted_count} temporary files ({size_mb} MB)")
        else:
            print("  ℹ️  No temporary files found")
    
    def optimize_project_structure(self) -> None:
        """Optimize project structure and permissions."""
        print("⚙️  Optimizing project structure...")
        
        # Ensure proper directory structure
        essential_dirs = [
            "core/agents",
            "core/generators", 
            "integrations",
            "apps/web",
            "server",
            "ui",
            "platform-tools",
            "tests",
            "docs",
            "scripts",
            "backups"
        ]
        
        for dir_path in essential_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  📁 Created directory: {dir_path}")
        
        # Set executable permissions on scripts
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.sh"):
                try:
                    script_file.chmod(0o755)
                except Exception:
                    pass
        
        print("  ✅ Project structure optimized")
    
    def save_manifest(self) -> bool:
        """Save the extraction manifest."""
        try:
            self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(self.manifest, f, indent=2, default=str)
            
            print(f"📋 Manifest saved to {self.manifest_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save manifest: {e}")
            return False
    
    def generate_cleanup_report(self) -> str:
        """Generate a comprehensive cleanup report."""
        report = f"""
# Claude Code Dev Stack V3.0 - Cleanup Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Repositories Deleted**: {len(self.manifest.get('deleted_repositories', []))}
- **Space Freed**: {self.manifest.get('space_saved', {}).get('total_mb', 0)} MB
- **Files Backed Up**: {len(self.manifest.get('backed_up_files', []))}
- **Backup Location**: {self.backup_dir}

## Deleted Repositories
"""
        
        for repo in self.manifest.get('deleted_repositories', []):
            size_mb = round(repo['size'] / (1024 * 1024), 2)
            report += f"- **{repo['name']}**: {size_mb} MB\n"
        
        report += f"""
## Validation Results
"""
        
        for component, valid in self.manifest.get('validation_results', {}).items():
            status = "✅" if valid else "❌"
            report += f"- {component}: {status}\n"
        
        report += f"""
## Project Structure
"""
        
        for dir_name, info in self.manifest.get('project_structure', {}).items():
            total_files = info.get('total_files', 0)
            total_size_mb = round(info.get('total_size', 0) / (1024 * 1024), 2)
            report += f"- **{dir_name}**: {total_files} files ({total_size_mb} MB)\n"
        
        return report
    
    def run_cleanup(self, force: bool = False) -> bool:
        """Run the complete cleanup process."""
        print("🚀 Starting Claude Code Dev Stack V3.0 Cleanup Process")
        print("=" * 60)
        
        # Step 1: Analyze current structure
        self.analyze_project_structure()
        
        # Step 2: Identify valuable files
        valuable_files = self.identify_valuable_files()
        
        # Step 3: Create backup
        if not self.create_backup(valuable_files):
            print("❌ Backup failed, aborting cleanup")
            return False
        
        # Step 4: Validate extractions
        validation_results = self.validate_extractions()
        failed_validations = [k for k, v in validation_results.items() if not v]
        
        if failed_validations and not force:
            print(f"⚠️  Warning: {len(failed_validations)} validation checks failed:")
            for failed in failed_validations:
                print(f"    - {failed}")
            
            response = input("\nContinue anyway? (yes/no): ").lower().strip()
            if response not in ['yes', 'y']:
                print("❌ Cleanup cancelled due to validation failures")
                return False
        
        # Step 5: Calculate space savings
        self.calculate_space_savings()
        
        # Step 6: Perform cleanup
        if not self.perform_cleanup(force):
            return False
        
        # Step 7: Clean temporary files
        self.cleanup_temp_files()
        
        # Step 8: Optimize project structure
        self.optimize_project_structure()
        
        # Step 9: Save manifest
        self.save_manifest()
        
        # Step 10: Generate report
        report = self.generate_cleanup_report()
        report_file = self.project_root / "scripts" / "cleanup_report.md"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Cleanup report saved to {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
        
        print("\n🎉 Cleanup Process Complete!")
        print("=" * 60)
        print(f"✅ Successfully freed {self.manifest['space_saved'].get('total_mb', 0)} MB")
        print(f"✅ Backup created at: {self.backup_dir}")
        print(f"✅ Manifest saved at: {self.manifest_file}")
        print(f"✅ Report saved at: {report_file}")
        
        return True

def main():
    """Main entry point for the cleanup script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude Code Dev Stack V3.0 - Repository Cleanup Script"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force cleanup without confirmation prompts"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to project root directory (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and report without performing actual cleanup"
    )
    
    args = parser.parse_args()
    
    # Resolve project root path
    project_root = Path(args.project_root).resolve()
    
    if not project_root.exists():
        print(f"❌ Project root not found: {project_root}")
        sys.exit(1)
    
    print(f"🏠 Project root: {project_root}")
    
    # Initialize cleanup manager
    cleanup_manager = CleanupManager(str(project_root))
    
    if args.dry_run:
        print("🔍 Running in dry-run mode (no actual cleanup)")
        cleanup_manager.analyze_project_structure()
        cleanup_manager.identify_valuable_files()
        cleanup_manager.validate_extractions()
        cleanup_manager.calculate_space_savings()
        cleanup_manager.save_manifest()
        
        report = cleanup_manager.generate_cleanup_report()
        print("\n" + "=" * 60)
        print("DRY RUN REPORT")
        print("=" * 60)
        print(report)
        
    else:
        # Run full cleanup
        success = cleanup_manager.run_cleanup(args.force)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()