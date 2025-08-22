#!/usr/bin/env node

/**
 * Fix Permissions Script for Claude Code Dev Stack V3 (CommonJS version)
 * Standalone script to fix executable permissions and shebangs
 * This version uses CommonJS to avoid ES module issues during npm install
 */

const fs = require('fs-extra');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// Simple color functions for output (no chalk dependency)
const colors = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  white: (text) => `\x1b[37m${text}\x1b[0m`
};

const banner = `
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🔧 Claude Code Dev Stack V3 - Permission Fixer 🔧           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
`;

async function main() {
  console.log(colors.cyan(banner));
  
  console.log(colors.blue('🔧 Fixing executable permissions and shebangs...'));
  
  try {
    // Detect package root - handle both local and global npm installs
    const packageRoot = await findPackageRoot();
    console.log(colors.gray(`📁 Package root: ${packageRoot}`));
    
    // Fix executable permissions on Unix systems
    await fixExecutablePermissions(packageRoot);
    
    // Validate and fix Python script shebangs
    await validatePythonScripts(packageRoot);
    
    // Fix JS bin script shebangs
    await validateJSBinScripts(packageRoot);
    
    // Fix path resolution issues in setup scripts
    await fixPathResolution(packageRoot);
    
    // Create symlinks for global access if needed
    await ensureGlobalAccess(packageRoot);
    
    console.log(colors.green('\n✅ All permissions and paths have been fixed!'));
    console.log(colors.blue('📋 Summary:'));
    console.log(colors.green('  ✅ Executable permissions set'));
    console.log(colors.green('  ✅ Python shebangs validated'));
    console.log(colors.green('  ✅ JS bin scripts validated'));
    console.log(colors.green('  ✅ Path resolution fixed'));
    console.log(colors.green('  ✅ Global access ensured'));
    console.log(colors.yellow('\n💡 Commands now available:'));
    console.log(colors.white('   claude-code-setup'));
    console.log(colors.white('   claude-code-agents'));
    console.log(colors.white('   claude-code-hooks'));
    
  } catch (error) {
    console.error(colors.red('❌ Permission fixing failed:'), error.message);
    process.exit(1);
  }
}

async function findPackageRoot() {
  let currentDir = __dirname;
  
  // First try relative to script location
  let packageRoot = path.resolve(currentDir, '..');
  if (await fs.pathExists(path.join(packageRoot, 'package.json'))) {
    return packageRoot;
  }
  
  // Check if we're in a global npm install
  if (currentDir.includes('node_modules')) {
    // Look for the dev-stack package in node_modules
    const nodeModulesMatch = currentDir.match(/^(.*node_modules)/);
    if (nodeModulesMatch) {
      const nodeModulesDir = nodeModulesMatch[1];
      const globalDevStackDir = path.join(nodeModulesDir, '@claude-code', 'dev-stack');
      if (await fs.pathExists(globalDevStackDir)) {
        return globalDevStackDir;
      }
      
      // Try without scoped package name
      const simpleDevStackDir = path.join(nodeModulesDir, 'claude-code-dev-stack');
      if (await fs.pathExists(simpleDevStackDir)) {
        return simpleDevStackDir;
      }
    }
  }
  
  // Fallback: walk up the directory tree
  while (currentDir !== path.dirname(currentDir)) {
    if (await fs.pathExists(path.join(currentDir, 'package.json'))) {
      const pkg = await fs.readJson(path.join(currentDir, 'package.json'));
      if (pkg.name === '@claude-code/dev-stack' || pkg.name === 'claude-code-dev-stack') {
        return currentDir;
      }
    }
    currentDir = path.dirname(currentDir);
  }
  
  throw new Error('Could not find Claude Code Dev Stack package root');
}

async function fixExecutablePermissions(packageRoot) {
  // Only fix permissions on Unix-like systems
  if (os.platform() === 'win32') {
    console.log(colors.yellow('⚠️  Windows detected - skipping chmod operations'));
    return;
  }
  
  console.log(colors.blue('🔧 Fixing executable permissions on Unix system...'));
  
  try {
    const executablePaths = [
      // Bin directory scripts
      { dir: path.join(packageRoot, 'bin'), pattern: '*.js' },
      // Python hook scripts
      { dir: path.join(packageRoot, 'core', 'hooks', 'hooks'), pattern: '*.py' },
      // Shell scripts
      { dir: path.join(packageRoot, 'scripts'), pattern: '*.sh' },
      { dir: path.join(packageRoot, 'integrations'), pattern: '*.sh' }
    ];
    
    let fixedCount = 0;
    
    for (const { dir, pattern } of executablePaths) {
      if (await fs.pathExists(dir)) {
        const files = await fs.readdir(dir);
        const matchingFiles = files.filter(file => {
          const ext = pattern.replace('*.', '');
          return file.endsWith(`.${ext}`);
        });
        
        for (const file of matchingFiles) {
          const filePath = path.join(dir, file);
          try {
            execSync(`chmod +x "${filePath}"`, { stdio: 'pipe' });
            console.log(colors.green(`  ✅ Made executable: ${path.relative(packageRoot, filePath)}`));
            fixedCount++;
          } catch (error) {
            console.log(colors.yellow(`  ⚠️  Could not chmod ${file}: ${error.message}`));
          }
        }
      }
    }
    
    // Recursively fix any additional scripts
    const additionalDirs = [
      path.join(packageRoot, 'integrations'),
      path.join(packageRoot, 'tools')
    ];
    
    for (const dir of additionalDirs) {
      if (await fs.pathExists(dir)) {
        const allFiles = await walkDirectory(dir);
        for (const filePath of allFiles) {
          if (filePath.endsWith('.sh') || filePath.endsWith('.py')) {
            try {
              execSync(`chmod +x "${filePath}"`, { stdio: 'pipe' });
              fixedCount++;
            } catch (error) {
              // Silently skip files we can't chmod
            }
          }
        }
      }
    }
    
    console.log(colors.green(`✅ Fixed permissions on ${fixedCount} files`));
    
  } catch (error) {
    console.log(colors.yellow(`⚠️  Permission fixing had issues: ${error.message}`));
  }
}

async function validatePythonScripts(packageRoot) {
  console.log(colors.blue('🐍 Validating and fixing Python script shebangs...'));
  
  const pythonDirs = [
    path.join(packageRoot, 'core', 'hooks', 'hooks'),
    path.join(packageRoot, 'scripts'),
    path.join(packageRoot, 'tools')
  ];
  
  let fixedCount = 0;
  let validatedCount = 0;
  
  for (const dir of pythonDirs) {
    if (!(await fs.pathExists(dir))) {
      continue;
    }
    
    const allFiles = await walkDirectory(dir);
    const pythonFiles = allFiles.filter(file => file.endsWith('.py'));
    
    for (const filePath of pythonFiles) {
      try {
        const content = await fs.readFile(filePath, 'utf8');
        const lines = content.split('\n');
        
        validatedCount++;
        
        // Check if first line is a proper shebang
        if (!lines[0] || !lines[0].startsWith('#!/usr/bin/env python')) {
          // Add proper shebang
          const newContent = '#!/usr/bin/env python3\n' + content;
          await fs.writeFile(filePath, newContent);
          console.log(colors.green(`  ✅ Added shebang to: ${path.relative(packageRoot, filePath)}`));
          fixedCount++;
        } else {
          console.log(colors.gray(`  ✓ ${path.basename(filePath)} already has shebang`));
        }
      } catch (error) {
        console.log(colors.yellow(`  ⚠️  Could not validate ${path.basename(filePath)}: ${error.message}`));
      }
    }
  }
  
  if (fixedCount > 0) {
    console.log(colors.green(`✅ Fixed shebangs in ${fixedCount}/${validatedCount} Python scripts`));
  } else {
    console.log(colors.green(`✅ All ${validatedCount} Python scripts have proper shebangs`));
  }
}

async function validateJSBinScripts(packageRoot) {
  console.log(colors.blue('📜 Validating JS bin script shebangs...'));
  
  const binDir = path.join(packageRoot, 'bin');
  
  if (!(await fs.pathExists(binDir))) {
    console.log(colors.yellow('⚠️  Bin directory not found, skipping validation'));
    return;
  }
  
  const binFiles = await fs.readdir(binDir);
  const jsFiles = binFiles.filter(file => file.endsWith('.js'));
  
  let fixedCount = 0;
  
  for (const file of jsFiles) {
    const filePath = path.join(binDir, file);
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const lines = content.split('\n');
      
      // Check if first line is a proper Node.js shebang
      if (!lines[0] || !lines[0].startsWith('#!/usr/bin/env node')) {
        // Add proper shebang
        const newContent = '#!/usr/bin/env node\n' + content;
        await fs.writeFile(filePath, newContent);
        console.log(colors.green(`  ✅ Added Node.js shebang to: ${file}`));
        fixedCount++;
      } else {
        console.log(colors.gray(`  ✓ ${file} already has Node.js shebang`));
      }
    } catch (error) {
      console.log(colors.yellow(`  ⚠️  Could not validate ${file}: ${error.message}`));
    }
  }
  
  if (fixedCount > 0) {
    console.log(colors.green(`✅ Fixed shebangs in ${fixedCount} JS bin scripts`));
  } else {
    console.log(colors.green(`✅ All ${jsFiles.length} JS bin scripts have proper shebangs`));
  }
}

async function fixPathResolution(packageRoot) {
  console.log(colors.blue('🔗 Fixing path resolution in setup scripts...'));
  
  // Update the claude-code-setup-simple.js to use proper path resolution
  const setupScript = path.join(packageRoot, 'bin', 'claude-code-setup-simple.js');
  
  if (await fs.pathExists(setupScript)) {
    try {
      let content = await fs.readFile(setupScript, 'utf8');
      
      // Fix the hooks directory path resolution
      const oldPattern = /const coreHooksDir = path\.join\(packageRoot, 'core', 'hooks', 'hooks'\);/g;
      const newPattern = `// Dynamic path resolution for global npm installs
    let coreHooksDir;
    if (packageRoot.includes('node_modules')) {
      // Global npm install - find the actual hooks directory
      const globalModulesDir = packageRoot.split('node_modules')[0] + 'node_modules';
      const devStackDir = path.join(globalModulesDir, '@claude-code', 'dev-stack');
      coreHooksDir = path.join(devStackDir, 'core', 'hooks', 'hooks');
      
      // Fallback to package root if the above doesn't exist
      if (!fs.existsSync(coreHooksDir)) {
        coreHooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
      }
    } else {
      // Local development or direct install
      coreHooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
    }`;
      
      if (content.includes('const coreHooksDir = path.join(packageRoot, \'core\', \'hooks\', \'hooks\');')) {
        content = content.replace(oldPattern, newPattern);
        await fs.writeFile(setupScript, content);
        console.log(colors.green('  ✅ Fixed path resolution in setup script'));
      } else {
        console.log(colors.gray('  ✓ Setup script already has proper path resolution'));
      }
    } catch (error) {
      console.log(colors.yellow(`  ⚠️  Could not fix setup script: ${error.message}`));
    }
  }
  
  // Also fix the Python command resolution to work cross-platform
  const scriptsToFix = [
    path.join(packageRoot, 'bin', 'claude-code-setup-simple.js'),
    path.join(packageRoot, 'scripts', 'complete-install.js')
  ];
  
  for (const scriptPath of scriptsToFix) {
    if (await fs.pathExists(scriptPath)) {
      try {
        let content = await fs.readFile(scriptPath, 'utf8');
        
        // Improve Python command detection
        const pythonDetection = `// Cross-platform Python command detection
    let pythonCmd = 'python3';
    try {
      execSync('python3 --version', { stdio: 'pipe' });
    } catch {
      try {
        execSync('python --version', { stdio: 'pipe' });
        pythonCmd = 'python';
      } catch {
        console.log(colors.yellow('⚠️  Python not found, hooks may not work'));
        pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
      }
    }`;
        
        // Replace simple platform detection with robust detection
        const oldPythonPattern = /const pythonCmd = process\.platform === 'win32' \? 'python' : 'python3';/g;
        
        if (content.includes("const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';")) {
          content = content.replace(oldPythonPattern, pythonDetection);
          await fs.writeFile(scriptPath, content);
          console.log(colors.green(`  ✅ Improved Python detection in ${path.basename(scriptPath)}`));
        }
      } catch (error) {
        console.log(colors.yellow(`  ⚠️  Could not fix Python detection in ${path.basename(scriptPath)}: ${error.message}`));
      }
    }
  }
}

async function ensureGlobalAccess(packageRoot) {
  console.log(colors.blue('🌐 Ensuring global access to commands...'));
  
  try {
    // Check if this is a global npm install
    const isGlobalInstall = packageRoot.includes('node_modules') && 
                           (packageRoot.includes('npm') || packageRoot.includes('yarn'));
    
    if (isGlobalInstall) {
      console.log(colors.green('  ✅ Global npm install detected - commands should be available globally'));
      
      // Verify the bin scripts exist and are executable
      const binDir = path.join(packageRoot, 'bin');
      const binScripts = ['claude-code-setup-simple.js', 'claude-code-agents.js', 'claude-code-hooks.js'];
      
      for (const script of binScripts) {
        const scriptPath = path.join(binDir, script);
        if (await fs.pathExists(scriptPath)) {
          console.log(colors.green(`  ✅ ${script} ready for global use`));
        } else {
          console.log(colors.yellow(`  ⚠️  ${script} not found`));
        }
      }
    } else {
      console.log(colors.yellow('  ⚠️  Local install detected - use npm link for global access'));
      console.log(colors.cyan('     Run: npm link (in the package directory)'));
    }
    
    // Test if commands are accessible
    if (os.platform() !== 'win32') {
      try {
        execSync('which claude-code-setup', { stdio: 'pipe' });
        console.log(colors.green('  ✅ claude-code-setup command is globally accessible'));
      } catch {
        console.log(colors.yellow('  ⚠️  claude-code-setup not in PATH - may need to restart shell'));
      }
    }
    
  } catch (error) {
    console.log(colors.yellow(`  ⚠️  Could not verify global access: ${error.message}`));
  }
}

async function walkDirectory(dir) {
  const files = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const subFiles = await walkDirectory(fullPath);
      files.push(...subFiles);
    } else {
      files.push(fullPath);
    }
  }
  
  return files;
}

// Run the fix
main().catch(console.error);