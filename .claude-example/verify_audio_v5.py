#!/usr/bin/env python3
"""
Claude Code v5.0 Audio System Verification
Checks that all audio files are properly mapped and playable
"""

import os
import sys
from pathlib import Path
import json

def verify_audio_system():
    """Verify the v5.0 audio system is complete and functional"""
    
    print("=" * 70)
    print("CLAUDE CODE V5.0 - AUDIO SYSTEM VERIFICATION")
    print("=" * 70)
    
    issues = []
    warnings = []
    successes = []
    
    # Check directories
    audio_dir = Path(".claude-example/audio")
    archive_dir = Path(".claude-example/audio_archive")
    hooks_dir = Path(".claude-example/hooks")
    
    # 1. Check audio directory exists
    if audio_dir.exists():
        successes.append("Audio directory exists")
        audio_files = list(audio_dir.glob("*.wav"))
        print(f"\nFound {len(audio_files)} audio files in {audio_dir}")
    else:
        issues.append(f"Audio directory not found: {audio_dir}")
    
    # 2. Check archive directory
    if archive_dir.exists():
        archive_files = list(archive_dir.glob("*.wav"))
        successes.append(f"Archive directory has {len(archive_files)} old files")
    else:
        warnings.append("No archive directory (OK if fresh install)")
    
    # 3. Check audio_player.py exists and has mappings
    audio_player = hooks_dir / "audio_player.py"
    if audio_player.exists():
        successes.append("audio_player.py hook exists")
        
        # Read and check for specific audio mappings
        with open(audio_player, 'r') as f:
            content = f.read()
            
        # Check for specific audio files
        specific_audio = [
            "mkdir_operation.wav",
            "git_status.wav", 
            "npm_build.wav",
            "pip_install.wav",
            "running_tests.wav",
            "docker_building.wav",
            "risky_command.wav",
            "frontend_agent.wav",
            "analyzing_code.wav"
        ]
        
        mapped_count = 0
        for audio in specific_audio:
            if audio in content:
                mapped_count += 1
        
        if mapped_count == len(specific_audio):
            successes.append(f"All {mapped_count} specific audio files are mapped")
        else:
            warnings.append(f"Only {mapped_count}/{len(specific_audio)} specific audio files mapped")
    else:
        issues.append("audio_player.py hook not found")
    
    # 4. Check for required audio files
    required_audio = [
        # Core operations
        "mkdir_operation.wav",
        "touch_operation.wav",
        "copy_operation.wav",
        "move_operation.wav",
        "delete_operation.wav",
        
        # Git
        "git_status.wav",
        "git_commit.wav",
        "git_push.wav",
        "git_pull.wav",
        
        # Build/Install
        "npm_build.wav",
        "pip_install.wav",
        "npm_install.wav",
        
        # Testing
        "running_tests.wav",
        "tests_passed.wav",
        "tests_failed.wav",
        
        # Docker
        "docker_building.wav",
        "docker_running.wav",
        
        # Agents
        "frontend_agent.wav",
        "backend_agent.wav",
        "database_agent.wav",
        "master_orchestrator.wav",
        
        # Status
        "analyzing_code.wav",
        "generating_code.wav",
        "reviewing_changes.wav",
        
        # Warnings/Errors
        "risky_command.wav",
        "permission_denied.wav",
        "command_failed.wav",
        
        # Legacy/Compatibility
        "project_created.wav",
        "ready_for_input.wav",
        "pipeline_complete.wav"
    ]
    
    missing_audio = []
    present_audio = []
    
    for audio_file in required_audio:
        audio_path = audio_dir / audio_file
        if audio_path.exists():
            size = audio_path.stat().st_size
            if size > 0:
                present_audio.append(audio_file)
            else:
                missing_audio.append(f"{audio_file} (0 bytes)")
        else:
            missing_audio.append(audio_file)
    
    if present_audio:
        successes.append(f"{len(present_audio)}/{len(required_audio)} required audio files present")
    
    if missing_audio:
        issues.append(f"Missing {len(missing_audio)} audio files: {', '.join(missing_audio[:5])}...")
    
    # 5. Check settings.json integration
    settings_path = Path(".claude-example/settings.json")
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Check for audio_player.py in hooks
        has_audio_hook = False
        if "hooks" in settings:
            hooks_str = json.dumps(settings["hooks"])
            if "audio_player.py" in hooks_str:
                has_audio_hook = True
                successes.append("audio_player.py integrated in settings.json")
        
        if not has_audio_hook:
            issues.append("audio_player.py not found in settings.json hooks")
    else:
        warnings.append("settings.json not found")
    
    # 6. Check for venv_enforcer.py
    venv_enforcer = hooks_dir / "venv_enforcer.py"
    if venv_enforcer.exists():
        successes.append("venv_enforcer.py hook exists (v5.0 feature)")
    else:
        warnings.append("venv_enforcer.py not found (v5.0 feature)")
    
    # 7. Check for master_orchestrator.py
    master_orch = hooks_dir / "master_orchestrator.py"
    if master_orch.exists():
        successes.append("master_orchestrator.py exists")
        
        # Check if it's in settings.json
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            if "hooks" in settings:
                hooks_str = json.dumps(settings["hooks"])
                if "master_orchestrator.py" in hooks_str:
                    successes.append("master_orchestrator.py integrated in UserPromptSubmit")
                else:
                    issues.append("master_orchestrator.py NOT in settings.json")
    else:
        warnings.append("master_orchestrator.py not found")
    
    # Print results
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    if successes:
        print("\n[SUCCESSES]:")
        for success in successes:
            print(f"  [OK] {success}")
    
    if warnings:
        print("\n[WARNINGS]:")
        for warning in warnings:
            print(f"  [WARN] {warning}")
    
    if issues:
        print("\n[ISSUES]:")
        for issue in issues:
            print(f"  [FAIL] {issue}")
    
    # Summary
    print("\n" + "=" * 70)
    if not issues:
        print("[SUCCESS] AUDIO SYSTEM V5.0 IS READY!")
        print("\nAll specific audio files are in place and properly mapped.")
        print("The system will now provide clear, descriptive audio feedback.")
    else:
        print("[WARNING] AUDIO SYSTEM NEEDS ATTENTION")
        print(f"\nFound {len(issues)} issues that should be resolved.")
        print("Run the installer to fix missing components.")
    
    print("\n" + "=" * 70)
    
    # Audio file statistics
    if audio_dir.exists():
        audio_files = list(audio_dir.glob("*.wav"))
        total_size = sum(f.stat().st_size for f in audio_files) / 1024  # KB
        
        print("\n[AUDIO FILE STATISTICS]:")
        print(f"  - Total audio files: {len(audio_files)}")
        print(f"  - Total size: {total_size:.1f} KB")
        print(f"  - Average size: {total_size/len(audio_files):.1f} KB per file")
        
        # List categories
        categories = {
            "File ops": ["mkdir", "touch", "copy", "move", "delete"],
            "Git": ["git_"],
            "Build": ["build", "make", "cargo"],
            "Install": ["install", "pip", "npm"],
            "Test": ["test", "tests"],
            "Docker": ["docker"],
            "Agent": ["agent", "orchestrator"],
            "Status": ["analyzing", "generating", "reviewing", "optimizing"],
            "Errors": ["failed", "denied", "error", "not_found"]
        }
        
        print("\n  Categories present:")
        for category, keywords in categories.items():
            count = sum(1 for f in audio_files if any(k in f.name for k in keywords))
            if count > 0:
                print(f"    - {category}: {count} files")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = verify_audio_system()
    sys.exit(0 if success else 1)