# Claude Code Dev Stack - Hook Installation Issue Context

## Current Status (v3.7.10)
The hooks are triggering correctly but the Python files are not being installed properly during the npm package installation process.

## Problem Summary
When users run `npm install -g claude-code-dev-stack` followed by `ccds-setup`, the hook configuration is added to `~/.claude/settings.json` correctly, but the actual Python hook files are not being copied to `~/.claude/hooks/`. This causes hooks to fail with "file not found" errors.

## Root Cause Analysis

### 1. NPM Package Files Issue
The `package.json` "files" field doesn't include the actual hook Python source files:
```json
"files": [
  "core/hooks/",  // This directory structure doesn't exist in the package
]
```

The actual hook files are located in subdirectories like:
- `src/core/hooks/statusline/claude_statusline.py`
- `src/core/hooks/agent/master_orchestrator.py`
- `src/core/hooks/agent/smart_orchestrator.py`
- etc.

### 2. ccds-setup.cjs Hook Installation
Lines 211-256 attempt to copy hooks but fail because:
- The source directories don't exist in the npm package
- Fallback creates placeholder files that do nothing

## Required Fixes

### Fix 1: Update package.json
Add the actual hook source directories to the "files" field:
```json
"files": [
  "src/core/hooks/**/*.py",
  "src/core/hooks/**/*.json",
  // ... rest of files
]
```

### Fix 2: Create Hook Bundle Directory
Before publishing to npm, create a simplified hook structure:
```
hooks/
├── claude_statusline.py
├── master_orchestrator.py
├── smart_orchestrator.py
├── agent_mention_parser.py
├── status_line_manager.py
├── audio_controller.py
├── performance_monitor.py
└── (other hook files)
```

### Fix 3: Update ccds-setup.cjs
Modify the hook installation logic (lines 221-256) to:
1. Look for bundled hooks in the package
2. Copy them to ~/.claude/hooks/
3. Only create placeholders as last resort

## File Structure Needed

### Current (Not Working)
```
claude-code-dev-stack/
├── bin/
│   └── ccds-setup.cjs
├── package.json (files field incomplete)
└── src/core/hooks/ (not included in npm package)
```

### Required (Will Work)
```
claude-code-dev-stack/
├── bin/
│   └── ccds-setup.cjs
├── hooks/ (bundled flat directory)
│   ├── claude_statusline.py
│   ├── master_orchestrator.py
│   └── (all other hooks)
└── package.json (updated files field)
```

## Implementation Steps

1. **Create hooks bundle directory** at package root
2. **Copy all Python hooks** from src/core/hooks/*/*.py to hooks/
3. **Update package.json** to include "hooks/" in files field
4. **Update ccds-setup.cjs** to look for hooks in package hooks/ directory
5. **Test installation** in clean environment
6. **Bump version** to 3.7.11
7. **Publish to npm**

## Testing Commands
```bash
# In clean environment (Docker/WSL)
npm install -g claude-code-dev-stack@latest
ccds-setup
ls -la ~/.claude/hooks/
# Should show all Python hook files

# Test hook execution
echo '{"test": true}' | python3 ~/.claude/hooks/smart_orchestrator.py
```

## Critical Hook Files Required
These must be present in ~/.claude/hooks/ after installation:
- `claude_statusline.py`
- `master_orchestrator.py`
- `smart_orchestrator.py`
- `agent_mention_parser.py`
- `status_line_manager.py`
- `audio_controller.py`
- `performance_monitor.py`

## Version History
- v3.7.7: Fixed hooks format from array to object
- v3.7.8: Fixed undefined variable issue
- v3.7.9: Force replaced old hooks format
- v3.7.10: Current version (hooks trigger but files missing)
- v3.7.11: Next version (will include proper hook installation)

## User Requirements
- ONE command (`ccds-setup`) must work on ALL platforms
- No manual file creation required
- Hooks must be included in npm package
- Installation must be fully automated

## Reference This Document
In a new Claude Code session, reference this document to continue fixing the hook installation issue. The main task is to ensure hook Python files are bundled with the npm package and properly installed to ~/.claude/hooks/ during setup.