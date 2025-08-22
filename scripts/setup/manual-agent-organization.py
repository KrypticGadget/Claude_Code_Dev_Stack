#!/usr/bin/env python3
"""
Manual Agent Organization Script
Manually organizes agent files into the correct tier hierarchy without complex duplicate detection.
"""

import os
import shutil
from pathlib import Path

def organize_agents():
    """Manually organize agents into proper tier structure."""
    base_path = Path(__file__).parent.parent
    agents_path = base_path / "core" / "agents"
    
    # Restore agents from backup first
    backup_agents = base_path / "backup" / "20250820_130833" / "core" / "agents"
    
    if backup_agents.exists():
        print("Restoring agents from backup...")
        for agent_file in backup_agents.glob("*.md"):
            target = agents_path / agent_file.name
            if not target.exists():
                shutil.copy2(agent_file, target)
                print(f"Restored: {agent_file.name}")
    
    # Define hierarchy
    hierarchy = {
        "tier0_coordination": [
            "master-orchestrator.md",
            "ceo-strategy.md"
        ],
        "tier1_orchestration": [
            "technical-cto.md",
            "project-manager.md",
            "business-tech-alignment.md"
        ],
        "tier2_teams/analysis": [
            "business-analyst.md",
            "financial-analyst.md"
        ],
        "tier2_teams/design": [
            "ui-ux-design.md",
            "frontend-architecture.md",
            "database-architecture.md",
            "security-architecture.md"
        ],
        "tier2_teams/implementation": [
            "backend-services.md",
            "frontend-mockup.md",
            "production-frontend.md",
            "mobile-development.md",
            "integration-setup.md"
        ],
        "tier2_teams/operations": [
            "devops-engineering.md",
            "script-automation.md",
            "performance-optimization.md"
        ],
        "tier2_teams/quality": [
            "quality-assurance.md",
            "testing-automation.md",
            "technical-specifications.md"
        ],
        "tier3_specialists/analysis": [
            "prompt-engineer.md"
        ],
        "tier3_specialists/design": [
            "middleware-specialist.md"
        ],
        "tier3_specialists/implementation": [
            "api-integration-specialist.md"
        ]
    }
    
    # Create directories and move files
    for tier_path, agent_files in hierarchy.items():
        tier_dir = agents_path / tier_path
        tier_dir.mkdir(parents=True, exist_ok=True)
        
        for agent_file in agent_files:
            source = agents_path / agent_file
            target = tier_dir / agent_file
            
            if source.exists() and not target.exists():
                shutil.move(str(source), str(target))
                print(f"Moved {agent_file} to {tier_path}")
            elif target.exists():
                print(f"Already exists: {tier_path}/{agent_file}")
            else:
                print(f"Not found: {agent_file}")
    
    # Archive unclassified agents
    archive_dir = base_path / "archive" / "agents"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for agent_file in agents_path.glob("*.md"):
        if agent_file.name not in ["agent-registry.json"]:
            target = archive_dir / agent_file.name
            shutil.move(str(agent_file), str(target))
            print(f"Archived: {agent_file.name}")
    
    print("\\nAgent organization complete!")
    print("\\nFinal structure:")
    for tier_path in hierarchy.keys():
        tier_dir = agents_path / tier_path
        if tier_dir.exists():
            files = list(tier_dir.glob("*.md"))
            print(f"  {tier_path}: {len(files)} agents")

if __name__ == "__main__":
    organize_agents()