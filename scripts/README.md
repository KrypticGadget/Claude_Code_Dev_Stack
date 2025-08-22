# Repository Automation Scripts

This directory contains automation scripts for cleaning, organizing, and maintaining the Claude Code Agents V3.6.9 repository structure.

## Quick Start

### Windows
```cmd
cd scripts
organize-repository.bat
```

### Unix/Linux/macOS
```bash
cd scripts
./organize-repository.sh
```

## Scripts Overview

### 🔧 Main Organization Scripts

#### `automated-repository-organizer.py`
**Purpose**: Master orchestrator script that manages the complete repository cleanup and organization process.

**Features**:
- Creates automatic backups before making changes
- Orchestrates all cleanup and organization tasks
- Generates comprehensive reports
- Supports dry-run mode

**Usage**:
```bash
# Full organization with backup
python automated-repository-organizer.py

# Dry run (no changes made)
python automated-repository-organizer.py --dry-run

# Specify custom path
python automated-repository-organizer.py /path/to/repo
```

#### `repository-cleanup.py`
**Purpose**: Core cleanup script that implements the tier-based agent hierarchy organization.

**Features**:
- Organizes agents into proper tier structure
- Archives duplicate and old files
- Cleans cache directories
- Detects and handles file duplicates
- Organizes audio files and PWA components

**Usage**:
```bash
python repository-cleanup.py [repository_path]
```

### 🔄 Maintenance Scripts

#### `maintenance-cleanup.py`
**Purpose**: Ongoing maintenance script for regular repository upkeep.

**Features**:
- Removes old cache directories
- Cleans temporary files
- Archives old log files
- Validates agent hierarchy
- Configurable retention policies

**Usage**:
```bash
# Full maintenance
python maintenance-cleanup.py

# Light cleanup only
python maintenance-cleanup.py --light-cleanup

# Validation only
python maintenance-cleanup.py --validate-only
```

#### `weekly-maintenance.py`
**Purpose**: Automated weekly maintenance routine.

**Features**:
- Scheduled maintenance execution
- Comprehensive cleanup
- Report generation
- Minimal resource usage

### 🚀 Quick Scripts

#### `quick-clean.py`
**Purpose**: Fast cleanup for developers during active development.

**Features**:
- Removes common cache files
- Quick temporary file cleanup
- Minimal disruption to workflow

**Usage**:
```bash
python quick-clean.py
```

#### `validate-organization.py`
**Purpose**: Validates repository organization without making changes.

**Features**:
- Checks agent file placement
- Validates tier hierarchy
- Identifies organizational issues
- Git pre-commit hook compatible

**Usage**:
```bash
python validate-organization.py
```

### 📋 Platform-Specific Scripts

#### `organize-repository.bat` (Windows)
**Purpose**: Windows batch script for easy repository organization.

**Features**:
- User-friendly prompts
- Automatic Python detection
- Error handling and reporting

#### `organize-repository.sh` (Unix/Linux/macOS)
**Purpose**: Shell script for Unix-like systems.

**Features**:
- Cross-platform compatibility
- Command-line argument parsing
- Robust error handling

### ⚙️ Setup Scripts

#### `setup-windows-task.bat`
**Purpose**: Sets up Windows Task Scheduler for automated maintenance.

#### `setup-cron.sh`
**Purpose**: Configures cron jobs for Unix-like systems.

## Configuration

### `maintenance-config.json`
Central configuration file controlling all maintenance operations.

**Key Settings**:
- `cache_cleanup_days`: How old cache files must be before deletion
- `log_retention_days`: How long to keep log files
- `file_size_threshold_mb`: Size threshold for flagging large files
- `agent_hierarchy`: Defines the proper tier structure for agents

**Example Configuration**:
```json
{
  "cache_cleanup_days": 7,
  "log_retention_days": 30,
  "file_size_threshold_mb": 100,
  "temp_file_patterns": ["*.tmp", "*.temp", "*~"],
  "cache_directories": ["__pycache__", ".mypy_cache", "node_modules"]
}
```

## Agent Hierarchy Structure

The scripts organize agents according to this hierarchy:

```
core/agents/
├── tier0_coordination/     # Master Orchestration
│   ├── master-orchestrator.md
│   └── ceo-strategy.md
├── tier1_orchestration/    # Strategic Management  
│   ├── technical-cto.md
│   ├── project-manager.md
│   └── business-tech-alignment.md
├── tier2_teams/           # Specialized Teams
│   ├── analysis/          # Business & Financial Analysis
│   ├── design/            # UI/UX, Architecture, Security
│   ├── implementation/    # Frontend, Backend, Mobile
│   ├── operations/        # DevOps, Automation, Performance
│   └── quality/           # QA, Testing, Specifications
└── tier3_specialists/     # Individual Specialists
    ├── analysis/
    ├── design/ 
    ├── implementation/
    ├── operations/
    └── quality/
```

## Automation Features

### Git Hooks
- **Pre-commit**: Validates agent organization before commits
- **Post-commit**: Runs light cleanup after commits

### Scheduled Maintenance
- **Weekly**: Comprehensive cleanup and organization validation
- **Daily**: Quick cache cleanup (optional)

### Backup Strategy
- Automatic backups before major changes
- Configurable retention policies
- Incremental backup support

## Usage Patterns

### Daily Development
```bash
# Quick cleanup during development
python scripts/quick-clean.py

# Validate before committing  
python scripts/validate-organization.py
```

### Weekly Maintenance
```bash
# Manual weekly maintenance
python scripts/weekly-maintenance.py

# Or set up automatic scheduling
bash scripts/setup-cron.sh  # Unix
scripts/setup-windows-task.bat  # Windows
```

### Initial Setup/Reorganization
```bash
# First-time organization
./scripts/organize-repository.sh

# Or preview changes first
./scripts/organize-repository.sh --dry-run
```

## Troubleshooting

### Common Issues

#### "Permission Denied" Errors
```bash
# Make scripts executable (Unix)
chmod +x scripts/*.sh scripts/*.py

# Or run with Python explicitly
python scripts/script-name.py
```

#### "Python Not Found" Errors
- Ensure Python 3.7+ is installed
- Check Python is in system PATH
- Use `python3` instead of `python` on some systems

#### "Agent Files Not Found"
- Run validation to check organization: `python scripts/validate-organization.py`
- Re-run organization: `python scripts/repository-cleanup.py`

### Recovery Procedures

#### Restore from Backup
```bash
# Backups are automatically created in backup/ directory
cp -r backup/YYYYMMDD_HHMMSS/core/agents/* core/agents/
```

#### Reset Organization
```bash
# Move all agents back to root and re-organize
python scripts/repository-cleanup.py --reset
```

## Development

### Adding New Scripts
1. Place scripts in the `scripts/` directory
2. Follow naming convention: `purpose-action.py`
3. Add to this README
4. Update `maintenance-config.json` if needed

### Modifying Agent Hierarchy
1. Update `agent_hierarchy` in `maintenance-config.json`
2. Run organization script to apply changes
3. Validate with `validate-organization.py`

### Custom Maintenance Rules
Edit `maintenance-config.json` to customize:
- File patterns to clean
- Cache directories
- Retention policies
- Excluded paths

## Reporting

All scripts generate reports in various formats:

- **JSON**: Machine-readable execution logs
- **Markdown**: Human-readable summaries  
- **Console**: Real-time progress updates

Reports are saved in the repository root and include:
- Actions performed
- Files processed
- Errors encountered
- Validation results

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review generated reports for error details
3. Run validation scripts to identify issues
4. Ensure configuration files are properly formatted

## Version History

- **v1.0**: Initial release with tier-based organization
- **v1.1**: Added automation and scheduling features
- **v1.2**: Enhanced backup and recovery capabilities