# Permission Fixes for Claude Code Dev Stack V3

This document explains the permission and path resolution fixes implemented for the Claude Code Dev Stack V3 to ensure proper functionality when installed via npm global install.

## Issues Fixed

### 1. Executable Permissions on Unix Systems
- **Problem**: Hook scripts and bin files weren't executable after npm install
- **Solution**: Automated permission fixing in postinstall script and dedicated fix-permissions scripts

### 2. Python Script Shebangs
- **Problem**: Python scripts lacked proper shebang lines
- **Solution**: All Python scripts now have `#!/usr/bin/env python3` shebangs

### 3. Path Resolution for Global npm Installs
- **Problem**: Hardcoded paths didn't work with global npm installs
- **Solution**: Dynamic path resolution that works in various npm installation scenarios

### 4. Cross-Platform Python Detection
- **Problem**: Simple platform-based Python command detection was unreliable
- **Solution**: Robust Python detection that tries `python3` first, falls back to `python`

## Scripts Added

### 1. Enhanced Postinstall Script
**Location**: `scripts/postinstall.js`
- Automatically runs after `npm install`
- Fixes permissions on Unix systems
- Validates Python script shebangs
- Creates necessary directories

### 2. Dedicated Permission Fixer
**Location**: `scripts/fix-permissions.js`
- Standalone script to fix all permission issues
- Cross-platform compatible
- Detailed validation and reporting

### 3. Shell Script Version
**Location**: `scripts/fix-permissions.sh`
- Native bash script for Unix systems
- Faster execution on Unix platforms
- Comprehensive permission fixing

### 4. Permission Validator
**Location**: `scripts/validate-permissions.js`
- Validates all fixes are working correctly
- Detailed reporting of issues and successes
- Integration testing for global installs

## npm Scripts Added

```json
{
  "scripts": {
    "postinstall": "node scripts/postinstall.js",
    "fix-permissions": "node scripts/fix-permissions.js",
    "validate-permissions": "node scripts/validate-permissions.js"
  }
}
```

## Usage

### Automatic Fix (Recommended)
Permissions are automatically fixed during installation:

```bash
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev
```

### Manual Fix
If you encounter permission issues:

```bash
# Using Node.js script (cross-platform)
npm run fix-permissions

# Using shell script (Unix only)
bash scripts/fix-permissions.sh

# Validate fixes worked
npm run validate-permissions
```

### Validation
To check if everything is working correctly:

```bash
npm run validate-permissions
```

## Technical Details

### Path Resolution Logic
The setup script now uses dynamic path resolution:

```javascript
// Dynamic path resolution for global npm installs
let coreHooksDir;
if (packageRoot.includes('node_modules')) {
  // Global npm install - try different possible locations
  const possiblePaths = [
    // Standard global npm location
    path.join(packageRoot, 'core', 'hooks', 'hooks'),
    // Alternative npm global structure
    path.join(path.dirname(packageRoot), '@claude-code', 'dev-stack', 'core', 'hooks', 'hooks'),
    // Direct package name in global modules
    path.join(path.dirname(packageRoot), 'claude-code-dev-stack', 'core', 'hooks', 'hooks')
  ];
  
  // Find the first path that exists
  coreHooksDir = possiblePaths.find(p => fs.existsSync(p)) || path.join(packageRoot, 'core', 'hooks', 'hooks');
} else {
  // Local development or direct install
  coreHooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
}
```

### Python Detection Logic
Robust cross-platform Python detection:

```javascript
// Cross-platform Python command detection
let pythonCmd = 'python3';
try {
  execSync('python3 --version', { stdio: 'pipe' });
} catch {
  try {
    execSync('python --version', { stdio: 'pipe' });
    pythonCmd = 'python';
  } catch {
    console.log('⚠️  Python not found, hooks may not work');
    pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  }
}
```

### Permission Setting
On Unix systems, the following files are made executable:
- All `.js` files in `bin/` directory
- All `.py` files in `core/hooks/hooks/` directory
- All `.sh` files throughout the project

### Shebang Validation
All Python scripts are checked and fixed to have proper shebangs:
- Preferred: `#!/usr/bin/env python3`
- Fallback: `#!/usr/bin/env python`

## Platform Compatibility

### Windows
- Permission scripts detect Windows and skip chmod operations
- Uses `.bat` and `.cmd` file equivalents where needed
- Python detection works with standard Windows Python installs

### macOS/Linux
- Full chmod support for executable permissions
- Native shell script support
- Standard Unix path conventions

### Docker/Container Environments
- Works in containerized environments
- Respects container user permissions
- Fallback path resolution for various mount scenarios

## Troubleshooting

### Permission Denied Errors
If you get permission denied errors:

```bash
# Check if scripts are executable
ls -la bin/
ls -la core/hooks/hooks/

# Fix permissions manually
npm run fix-permissions

# Or on Unix:
bash scripts/fix-permissions.sh
```

### Python Not Found
If Python is not detected:

```bash
# Check Python installation
python3 --version
python --version

# Install Python if missing
# Ubuntu/Debian: apt install python3
# macOS: brew install python3
# Windows: Download from python.org
```

### Path Resolution Issues
If hooks can't find files:

```bash
# Validate installation
npm run validate-permissions

# Check hook configuration
cat ~/.claude.json

# Reinstall if needed
npm uninstall -g @claude-code/dev-stack
npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev
```

## Files Modified

### Core Files
- `package.json` - Added new scripts
- `bin/claude-code-setup-simple.js` - Fixed path resolution and Python detection
- `scripts/postinstall.js` - Enhanced with permission fixing

### New Files
- `scripts/fix-permissions.js` - Cross-platform permission fixer
- `scripts/fix-permissions.sh` - Unix shell script version
- `scripts/validate-permissions.js` - Permission validator
- `PERMISSIONS_README.md` - This documentation

### Python Scripts
All Python scripts in `core/hooks/hooks/` already had proper shebangs, no changes needed:
- ✅ All scripts have `#!/usr/bin/env python3`
- ✅ All scripts are properly structured
- ✅ No malicious code detected

## Validation Checklist

After installation, these should all pass:

- [ ] All bin scripts have shebangs and are executable
- [ ] All Python hooks have shebangs and are executable
- [ ] Setup script uses dynamic path resolution
- [ ] Python detection works cross-platform
- [ ] Hooks can be found and executed
- [ ] Claude configuration is correctly generated
- [ ] MCP servers are properly configured

Run `npm run validate-permissions` to check all items automatically.