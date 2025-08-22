# Repository Organization Guide

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
