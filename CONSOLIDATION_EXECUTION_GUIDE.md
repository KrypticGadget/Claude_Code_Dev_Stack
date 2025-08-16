# Claude Code Dev Stack v3 Consolidation - Execution Guide

## Quick Start

### Windows Users
```bat
# Run the quick consolidation script
scripts\quick_consolidate.bat

# Or run PowerShell directly
.\scripts\consolidate_v3_structure.ps1

# Validate after consolidation
.\scripts\validate_consolidation.ps1
```

### Unix/Linux/macOS Users
```bash
# Run the quick consolidation script
./scripts/quick_consolidate.sh

# Or run Python directly
python3 scripts/consolidate_v3_structure.py

# Validate after consolidation
python3 scripts/validate_consolidation.py
```

## Complete Execution Summary

### Pre-Execution Checklist
- [ ] Git repository is clean (`git status` shows no uncommitted changes)
- [ ] All running processes stopped (especially web dev servers)
- [ ] At least 2GB free disk space available
- [ ] Python 3.x or PowerShell 5.0+ available
- [ ] Located in the Claude_Code_Dev_Stack root directory
- [ ] Claude_Code_Dev_Stack_v3 directory exists

### Execution Process

#### Step 1: Choose Your Method

**Option A: Quick Script (Recommended)**
- Windows: Double-click `scripts\quick_consolidate.bat`
- Unix/Linux/macOS: `./scripts/quick_consolidate.sh`

**Option B: Direct Script Execution**
- Python: `python scripts/consolidate_v3_structure.py`
- PowerShell: `.\scripts\consolidate_v3_structure.ps1`

**Option C: Dry Run (Preview Changes)**
- Python: `python scripts/consolidate_v3_structure.py --dry-run`
- PowerShell: `.\scripts\consolidate_v3_structure.ps1 -DryRun`

#### Step 2: Monitor Progress
The script will:
1. **Create Backup** - Full backup of current structure
2. **Analyze Structure** - Identify conflicts and plan migration
3. **Execute Migration** - Move files according to plan
4. **Update References** - Fix all path references
5. **Create Validation** - Generate validation scripts
6. **Generate Report** - Create consolidation report

#### Step 3: Immediate Validation
```bash
# Run validation script
python scripts/validate_consolidation.py
# OR
.\scripts\validate_consolidation.ps1

# Check directory structure
ls -la agents/ commands/ hooks/ audio/ orchestration/ apps/

# Verify file counts
find agents/ -name "*.md" | wc -l    # Should be ~28
find hooks/ -name "*.py" | wc -l     # Should be ~28+
```

#### Step 4: Functionality Testing
```bash
# Test Python imports
python -c "import sys; sys.path.append('.'); import hooks; print('Hooks OK')"

# Test web application
cd apps/web && npm install && npm run build

# Test mobile application
cd apps/mobile && npm install && npm test
```

### Post-Consolidation Structure

After successful consolidation, your structure will be:
```
Claude_Code_Dev_Stack/
├── agents/                 # 28 AI agents (consolidated)
├── commands/               # 18 slash commands (consolidated)
├── hooks/                  # 28+ Python hooks (from v3)
├── audio/                  # 102 audio files (from v3)
├── orchestration/          # MCP orchestration (from v3)
├── integrations/           # Browser/platform integrations (consolidated)
├── testing/                # Testing framework (from v3)
├── apps/                   # Applications (from v3)
│   ├── web/                # React PWA
│   ├── mobile/             # React Native
│   ├── backend/            # Backend services
│   └── shared/             # Shared components
├── docs/                   # Documentation (consolidated)
├── scripts/                # Scripts (consolidated)
├── MASTER_SPEC_V3.md       # v3 specification (moved)
├── requirements_v3.txt     # v3 Python dependencies (renamed)
├── setup_environment_v3.py # v3 setup script (renamed)
├── CONSOLIDATION_REPORT.md # Migration report
└── BACKUP_v3_[timestamp]/  # Backup of original structure
```

## Validation Checkpoints

### Checkpoint 1: Structure Integrity
**Script**: `scripts/validate_consolidation.py`
**Checks**:
- All required directories exist
- File counts match expected values
- No broken symlinks
- Proper file permissions

### Checkpoint 2: Path References
**Method**: Automated scanning in validation script
**Checks**:
- No remaining v3 path references
- All imports resolve correctly
- Configuration files updated
- Documentation links valid

### Checkpoint 3: Functionality Validation
**Method**: Manual testing
**Checks**:
- Agent system operational
- Command system functional
- Hook system active
- Integration points working
- Applications buildable/runnable

## Troubleshooting

### Common Issues

#### Issue: "v3 directory not found"
**Solution**: Ensure you're in the correct directory and `Claude_Code_Dev_Stack_v3` exists

#### Issue: "Insufficient permissions"
**Solution**: Run script with elevated privileges (admin on Windows, sudo on Unix)

#### Issue: "Python/PowerShell not found"
**Solution**: Install Python 3.x or enable PowerShell execution

#### Issue: "Migration failed"
**Solutions**:
1. Check the error logs in `consolidation_log.txt`
2. Ensure no files are in use (close editors, stop servers)
3. Run with elevated permissions if needed
4. Restore from backup if necessary

### Rollback Procedures

#### Automatic Rollback
```bash
# Python
python scripts/consolidate_v3_structure.py --rollback

# PowerShell
.\scripts\consolidate_v3_structure.ps1 -Rollback
```

#### Manual Rollback
```bash
# Remove consolidated files
rm -rf agents commands hooks audio orchestration integrations testing apps
rm -f MASTER_SPEC_V3.md requirements_v3.txt setup_environment_v3.py

# Restore from backup (replace timestamp with actual backup directory)
cp -r BACKUP_v3_*/root_structure/* .
cp -r BACKUP_v3_*/v3_structure ./Claude_Code_Dev_Stack_v3
```

## Success Indicators

### ✅ Consolidation Successful
- Script completes without errors
- All validation checkpoints pass
- Backup directory created
- Consolidation report generated
- No functionality loss

### ❌ Consolidation Failed
- Script exits with error
- Validation failures detected
- Missing directories or files
- Broken imports or references
- Applications won't build/run

## Next Steps After Consolidation

### Immediate Tasks
1. **Run Full Validation**
   ```bash
   python scripts/validate_consolidation.py
   ```

2. **Test Core Functionality**
   ```bash
   # Test applications
   cd apps/web && npm run dev
   cd apps/mobile && npm start
   ```

3. **Update Development Environment**
   ```bash
   # Update paths in IDE/editor configurations
   # Update any local scripts or aliases
   # Verify git hooks still work
   ```

### Long-term Tasks
1. **Update Documentation**
   - Revise README files
   - Update installation guides
   - Fix any broken links

2. **CI/CD Pipeline Updates**
   - Update build scripts
   - Modify deployment configurations
   - Test automation pipelines

3. **Team Communication**
   - Notify team members of structure change
   - Update onboarding documentation
   - Share new development workflows

## Support and Recovery

### Backup Information
- **Location**: `BACKUP_v3_[timestamp]/`
- **Contents**: Complete original structure
- **Retention**: Keep until validation complete
- **Size**: Varies (typically 100-500MB)

### Recovery Options
1. **Partial Recovery**: Restore specific components from backup
2. **Full Recovery**: Complete rollback to original state
3. **Git Recovery**: Use git reset if repository was clean
4. **Manual Recovery**: Selective file restoration

### Getting Help
- Review `CONSOLIDATION_REPORT.md` for detailed logs
- Check `consolidation_log.txt` for error messages
- Run validation script for diagnostic information
- Examine backup contents to understand original state

---

## Summary

This consolidation process is designed to be safe, automated, and reversible. The combination of comprehensive backups, validation scripts, and rollback procedures ensures that you can safely consolidate the v3 structure while maintaining all functionality.

**Remember**: The consolidation creates a complete backup before making any changes, so you can always restore the original state if needed.