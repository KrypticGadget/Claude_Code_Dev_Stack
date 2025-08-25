# Claude Code Dev Stack - Statusline Fix Session Context

## Current Status
Working on fixing the statusline feature that isn't appearing when Claude Code launches. The statusline was successfully implemented but has a cross-platform path issue preventing it from working properly.

## Version Progress
- v3.7.0: Initial statusline implementation
- v3.7.1: Version bump for npm publish
- v3.7.2: Added cross-platform path support
- v3.7.3: Fixed duplicate variable declaration bug
- v3.7.4: (PENDING) Need to fix statusline path escaping issue

## The Problem
The statusline isn't appearing because:
1. The settings.json file contains Windows-specific paths even in Linux/Docker environments
2. The path escaping in `ccds-setup.cjs` line 267 is incorrect for cross-platform support
3. The command format differs between Windows and Unix systems

### Current Bug Location
File: `bin/ccds-setup.cjs`
Line: 267
Issue: `const escapedPath = statuslineScript.replace(/\\/g, '\\\\');` doesn't properly escape for JSON

### Correct Fix Needed
```javascript
// Line 267 should be:
const escapedPath = statuslineScript.replace(/\\/g, '\\\\');
// But the command formatting needs to be:
if (isWindows) {
    statuslineCommand = `${pythonCmdForStatusline} "${escapedPath}"`;
} else {
    // Linux/macOS should NOT use quotes
    statuslineCommand = `${pythonCmdForStatusline} ${statuslineScript}`;
}
```

## Files to Update

### 1. bin/ccds-setup.cjs
- Fix line 271: Remove quotes from Linux/macOS command
- Current: `statuslineCommand = \`${pythonCmdForStatusline} ${statuslineScript}\`;`
- Should be: Same (already correct)

### 2. bin/ccds-setup-statusline.js  
- Fix line 32: Remove quotes from Linux/macOS command
- Current: `statuslineCommand = \`${pythonCmd} '${statuslineScript}'\`;`
- Should be: `statuslineCommand = \`${pythonCmd} ${statuslineScript}\`;`

### 3. package.json
- Bump version from 3.7.3 to 3.7.4

## Testing Commands

### Local Testing
```bash
# Test the statusline setup
node bin/ccds-setup-statusline.js

# Check settings.json
cat ~/.claude/settings.json | grep statusLine

# Test statusline directly
echo '{"model":{"display_name":"Test"}}' | python3 ~/.claude/hooks/claude_statusline.py

# Run test suite
python ~/.claude/hooks/test_statusline.py
```

### Docker Testing
```bash
# In Docker container
npm install -g claude-code-dev-stack@latest
ccds-setup
claude --debug
```

## Git Workflow

1. Make the fixes to both files
2. Test locally
3. Commit to feature/v3-dev:
   ```bash
   git add -A
   git commit -m "fix: Remove quotes from Unix statusline commands for proper execution"
   ```
4. Push and create PR:
   ```bash
   git push origin feature/v3-dev
   gh pr create --title "fix: Statusline cross-platform path handling v3.7.4" --body "Fixes statusline not appearing on Unix systems"
   ```
5. Merge PR
6. NPM publish will run automatically via GitHub Actions

## Expected Outcome
After fixes, the statusline should:
- Automatically appear when Claude Code launches
- Work on Windows, Linux, and macOS
- Show: model name, git branch, phase, active agents, token count, and health status

## Debug Information
If statusline still doesn't work:
1. Check `~/.claude/settings.json` - statusLine.command should match the OS
2. Run `claude --debug` to see if statusline is being executed
3. Check if Python is accessible: `which python3` or `which python`
4. Verify hook exists: `ls ~/.claude/hooks/claude_statusline.py`
5. Test directly: `echo '{"model":{"display_name":"Test"}}' | [python-command] [path-to-script]`

## Repository Info
- GitHub: https://github.com/KrypticGadget/Claude_Code_Dev_Stack
- Branch: feature/v3-dev (development) → main (production)
- NPM Package: claude-code-dev-stack

## Next Session Instructions
1. Read this file for context
2. Apply the fixes mentioned above
3. Test the fixes
4. Commit, push, and publish v3.7.4
5. Verify statusline works in Docker/Linux environment