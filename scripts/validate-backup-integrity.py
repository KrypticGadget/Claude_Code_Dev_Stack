#!/usr/bin/env python3
"""
Backup Integrity Validation Script for Claude Code Dev Stack
Comprehensive validation of the safety backup branch
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class BackupValidator:
    def __init__(self, backup_branch: str = "safety/pre-reorganization-backup"):
        self.backup_branch = backup_branch
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "backup_branch": backup_branch,
            "tests": [],
            "overall_status": "unknown",
            "errors": [],
            "warnings": []
        }
    
    def log_test(self, name: str, status: str, details: Optional[str] = None):
        """Log a test result"""
        test_result = {
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.validation_results["tests"].append(test_result)
        
        # Color coding for output
        color_map = {
            "PASS": "\033[92m[PASS]",
            "FAIL": "\033[91m[FAIL]", 
            "WARN": "\033[93m[WARN]",
            "INFO": "\033[94m[INFO]"
        }
        reset = "\033[0m"
        
        print(f"{color_map.get(status, '')} {name}: {status}{reset}")
        if details:
            print(f"   {details}")
    
    def run_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_git_repository(self) -> bool:
        """Verify we're in a git repository"""
        if not os.path.exists(".git"):
            self.log_test("Git Repository Check", "FAIL", "Not in a git repository")
            return False
        
        self.log_test("Git Repository Check", "PASS", "Valid git repository detected")
        return True
    
    def check_backup_branch_exists(self) -> bool:
        """Verify the backup branch exists"""
        success, stdout, stderr = self.run_command([
            "git", "show-ref", "--verify", "--quiet", f"refs/heads/{self.backup_branch}"
        ])
        
        if not success:
            self.log_test("Backup Branch Existence", "FAIL", 
                         f"Branch '{self.backup_branch}' does not exist")
            return False
        
        self.log_test("Backup Branch Existence", "PASS", 
                     f"Branch '{self.backup_branch}' found")
        return True
    
    def check_backup_commit_integrity(self) -> bool:
        """Verify the backup commit is valid and accessible"""
        success, stdout, stderr = self.run_command([
            "git", "log", "-1", "--format=%H %s", self.backup_branch
        ])
        
        if not success:
            self.log_test("Backup Commit Integrity", "FAIL", 
                         f"Cannot access commit on {self.backup_branch}")
            return False
        
        commit_info = stdout.strip()
        self.log_test("Backup Commit Integrity", "PASS", 
                     f"Latest commit: {commit_info[:50]}...")
        return True
    
    def check_critical_files(self) -> bool:
        """Verify critical files exist in the backup"""
        critical_files = [
            "Claude_Code_Dev_Stack_v3/apps/web/package.json",
            ".claude-example/settings.json", 
            "install.ps1",
            "install.sh",
            "docs/README_V3.md",
            "Claude_Code_Dev_Stack_v3/core/hooks/hooks/__init__.py",
            ".github/workflows/main-pipeline.yml",
            "REPOSITORY_SAFETY_BACKUP_STRATEGY.md"
        ]
        
        missing_files = []
        for file_path in critical_files:
            success, stdout, stderr = self.run_command([
                "git", "cat-file", "-e", f"{self.backup_branch}:{file_path}"
            ])
            
            if not success:
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("Critical Files Check", "FAIL", 
                         f"Missing files: {', '.join(missing_files)}")
            return False
        
        self.log_test("Critical Files Check", "PASS", 
                     f"All {len(critical_files)} critical files present")
        return True
    
    def check_directory_structure(self) -> bool:
        """Verify key directory structure in backup"""
        key_directories = [
            "Claude_Code_Dev_Stack_v3/",
            "Claude_Code_Dev_Stack_v3/apps/",
            "Claude_Code_Dev_Stack_v3/core/",
            "Claude_Code_Dev_Stack_v3/integrations/",
            ".claude-example/",
            ".github/workflows/",
            "docs/",
            "scripts/"
        ]
        
        missing_dirs = []
        for directory in key_directories:
            success, stdout, stderr = self.run_command([
                "git", "ls-tree", "-d", self.backup_branch, directory
            ])
            
            if not success or not stdout.strip():
                missing_dirs.append(directory)
        
        if missing_dirs:
            self.log_test("Directory Structure Check", "WARN", 
                         f"Missing directories: {', '.join(missing_dirs)}")
            self.validation_results["warnings"].append(f"Missing directories: {missing_dirs}")
        else:
            self.log_test("Directory Structure Check", "PASS", 
                         f"All {len(key_directories)} key directories present")
        
        return len(missing_dirs) == 0
    
    def check_file_count(self) -> bool:
        """Verify reasonable file count in backup"""
        success, stdout, stderr = self.run_command([
            "git", "ls-tree", "-r", self.backup_branch
        ])
        
        if not success:
            self.log_test("File Count Check", "FAIL", "Cannot list files in backup")
            return False
        
        file_count = len(stdout.strip().split('\n')) if stdout.strip() else 0
        
        # Expect at least 100 files for a complete backup
        if file_count < 100:
            self.log_test("File Count Check", "WARN", 
                         f"Only {file_count} files in backup (expected >100)")
            self.validation_results["warnings"].append(f"Low file count: {file_count}")
            return False
        
        self.log_test("File Count Check", "PASS", 
                     f"{file_count} files in backup")
        return True
    
    def check_backup_size(self) -> bool:
        """Check backup branch size reasonableness"""
        success, stdout, stderr = self.run_command([
            "git", "rev-list", "--count", self.backup_branch
        ])
        
        if success:
            commit_count = int(stdout.strip())
            self.log_test("Backup Size Check", "INFO", 
                         f"{commit_count} commits in backup branch")
        
        return True
    
    def check_diff_from_main(self) -> bool:
        """Show differences between backup and main branch"""
        success, stdout, stderr = self.run_command([
            "git", "diff", "--name-status", "main", self.backup_branch
        ])
        
        if success and stdout.strip():
            changes = len(stdout.strip().split('\n'))
            self.log_test("Diff from Main", "INFO", 
                         f"{changes} files differ from main branch")
        else:
            self.log_test("Diff from Main", "INFO", "No differences from main branch")
        
        return True
    
    def run_validation(self) -> Dict:
        """Run complete backup validation"""
        print("BACKUP INTEGRITY VALIDATION")
        print("=" * 50)
        
        # Run all validation tests
        tests = [
            self.check_git_repository,
            self.check_backup_branch_exists, 
            self.check_backup_commit_integrity,
            self.check_critical_files,
            self.check_directory_structure,
            self.check_file_count,
            self.check_backup_size,
            self.check_diff_from_main
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                else:
                    failed_tests += 1
            except Exception as e:
                failed_tests += 1
                self.validation_results["errors"].append(str(e))
                self.log_test(test.__name__, "FAIL", f"Exception: {e}")
        
        # Determine overall status
        if failed_tests == 0:
            self.validation_results["overall_status"] = "PASS"
            status_message = f"ALL TESTS PASSED ({passed_tests}/{passed_tests})"
            color = "\033[92m"
        elif failed_tests <= 2:
            self.validation_results["overall_status"] = "WARN"
            status_message = f"WARNINGS DETECTED ({passed_tests}/{passed_tests + failed_tests})"
            color = "\033[93m"
        else:
            self.validation_results["overall_status"] = "FAIL"
            status_message = f"VALIDATION FAILED ({passed_tests}/{passed_tests + failed_tests})"
            color = "\033[91m"
        
        print(f"\n{color}{status_message}\033[0m")
        
        return self.validation_results
    
    def save_results(self, filename: str = "backup_validation_results.json"):
        """Save validation results to file"""
        with open(filename, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"Results saved to: {filename}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate backup integrity")
    parser.add_argument("--branch", default="safety/pre-reorganization-backup",
                       help="Backup branch to validate")
    parser.add_argument("--output", default="backup_validation_results.json",
                       help="Output file for results")
    parser.add_argument("--quiet", action="store_true", 
                       help="Suppress detailed output")
    
    args = parser.parse_args()
    
    validator = BackupValidator(args.branch)
    results = validator.run_validation()
    validator.save_results(args.output)
    
    # Exit with appropriate code
    if results["overall_status"] == "PASS":
        sys.exit(0)
    elif results["overall_status"] == "WARN":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()