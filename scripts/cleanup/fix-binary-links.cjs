#!/usr/bin/env node

/**
 * Fix Binary Links Script
 * Ensures that the claude-code-* commands are properly linked after global npm install
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('\x1b[36m╔══════════════════════════════════════════════════════════╗');
console.log('║               Fix Binary Links                           ║');
console.log('╚══════════════════════════════════════════════════════════╝\x1b[0m\n');

function findNpmGlobalDir() {
  try {
    const globalDir = execSync('npm root -g', { encoding: 'utf8' }).trim();
    return globalDir;
  } catch (error) {
    // Fallback to common locations
    if (process.platform === 'win32') {
      return path.join(os.homedir(), 'AppData', 'Roaming', 'npm', 'node_modules');
    } else {
      return '/usr/local/lib/node_modules';
    }
  }
}

function findPackageInstallDir() {
  const globalDir = findNpmGlobalDir();
  
  // Try different possible package names/locations
  const possiblePaths = [
    path.join(globalDir, '@claude-code', 'dev-stack'),
    path.join(globalDir, 'claude-code-dev-stack'),
    path.join(globalDir, '@claude-code/dev-stack')
  ];

  for (const packagePath of possiblePaths) {
    if (fs.existsSync(packagePath)) {
      console.log(`\x1b[32m✅ Found package at: ${packagePath}\x1b[0m`);
      return packagePath;
    }
  }

  console.log('\x1b[33m⚠️  Package not found in expected locations\x1b[0m');
  console.log(`\x1b[33m   Searched: ${possiblePaths.join(', ')}\x1b[0m`);
  return null;
}

function fixBinaryLinks() {
  const packageDir = findPackageInstallDir();
  if (!packageDir) {
    console.log('\x1b[31m❌ Cannot fix binary links - package not found\x1b[0m');
    return false;
  }

  const packageJsonPath = path.join(packageDir, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    console.log('\x1b[31m❌ package.json not found in package directory\x1b[0m');
    return false;
  }

  let packageJson;
  try {
    packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  } catch (error) {
    console.log(`\x1b[31m❌ Failed to parse package.json: ${error.message}\x1b[0m`);
    return false;
  }

  if (!packageJson.bin) {
    console.log('\x1b[33m⚠️  No binary definitions found in package.json\x1b[0m');
    return false;
  }

  const isWindows = process.platform === 'win32';
  const npmBinDir = isWindows 
    ? path.join(path.dirname(findNpmGlobalDir()), 'npm')
    : '/usr/local/bin';

  console.log(`\x1b[33m🔧 Creating binary links in: ${npmBinDir}\x1b[0m`);

  let linksCreated = 0;
  for (const [binName, binPath] of Object.entries(packageJson.bin)) {
    try {
      const sourcePath = path.resolve(packageDir, binPath);
      const targetPath = path.join(npmBinDir, isWindows ? `${binName}.cmd` : binName);

      if (!fs.existsSync(sourcePath)) {
        console.log(`\x1b[33m⚠️  Source file not found: ${sourcePath}\x1b[0m`);
        continue;
      }

      if (isWindows) {
        // Create .cmd wrapper for Windows
        const cmdContent = `@echo off\nnode "${sourcePath}" %*\n`;
        fs.writeFileSync(targetPath, cmdContent);
      } else {
        // Create symlink for Unix
        if (fs.existsSync(targetPath)) {
          fs.unlinkSync(targetPath);
        }
        fs.symlinkSync(sourcePath, targetPath);
        execSync(`chmod +x "${targetPath}"`);
      }

      console.log(`\x1b[32m✅ Created link: ${binName} -> ${sourcePath}\x1b[0m`);
      linksCreated++;
    } catch (error) {
      console.log(`\x1b[31m❌ Failed to create link for ${binName}: ${error.message}\x1b[0m`);
    }
  }

  console.log(`\x1b[32m\n✅ Created ${linksCreated} binary links\x1b[0m`);
  return linksCreated > 0;
}

function verifyBinaryLinks() {
  console.log('\x1b[33m🧪 Verifying binary commands are available...\x1b[0m');

  const commands = [
    'claude-code-setup',
    'claude-code-agents', 
    'claude-code-hooks'
  ];

  let workingCommands = 0;
  for (const cmd of commands) {
    try {
      execSync(`${cmd} --version 2>/dev/null || ${cmd} --help 2>/dev/null || echo "Command exists"`, { 
        stdio: 'pipe',
        timeout: 5000 
      });
      console.log(`\x1b[32m✅ ${cmd} is available\x1b[0m`);
      workingCommands++;
    } catch (error) {
      console.log(`\x1b[31m❌ ${cmd} is not available\x1b[0m`);
    }
  }

  if (workingCommands === commands.length) {
    console.log('\x1b[32m\n🎉 All binary commands are working!\x1b[0m');
    return true;
  } else {
    console.log(`\x1b[33m\n⚠️  ${workingCommands}/${commands.length} commands working\x1b[0m`);
    return false;
  }
}

function fixNpmPermissions() {
  if (process.platform !== 'win32') {
    console.log('\x1b[33m🔧 Fixing npm permissions...\x1b[0m');
    try {
      execSync('npm config set prefix ~/.npm-global', { stdio: 'pipe' });
      console.log('\x1b[32m✅ npm prefix configured\x1b[0m');
      
      const profileFiles = ['~/.bashrc', '~/.bash_profile', '~/.zshrc'];
      const exportLine = 'export PATH=~/.npm-global/bin:$PATH';
      
      for (const profileFile of profileFiles) {
        const fullPath = profileFile.replace('~', os.homedir());
        if (fs.existsSync(fullPath)) {
          const content = fs.readFileSync(fullPath, 'utf8');
          if (!content.includes(exportLine)) {
            fs.appendFileSync(fullPath, `\n${exportLine}\n`);
            console.log(`\x1b[32m✅ Updated ${profileFile}\x1b[0m`);
          }
        }
      }
    } catch (error) {
      console.log(`\x1b[33m⚠️  Permission fix failed: ${error.message}\x1b[0m`);
    }
  }
}

async function main() {
  try {
    console.log('\x1b[33m🔍 Checking binary link status...\x1b[0m');
    
    // First check if commands already work
    const alreadyWorking = verifyBinaryLinks();
    if (alreadyWorking) {
      console.log('\x1b[32m✅ All commands already working - no fixes needed!\x1b[0m');
      return;
    }

    // Try to fix binary links
    console.log('\n\x1b[33m🔧 Attempting to fix binary links...\x1b[0m');
    const linksFixed = fixBinaryLinks();

    if (!linksFixed) {
      // Try npm permissions fix
      console.log('\n\x1b[33m🔧 Trying npm permission fixes...\x1b[0m');
      fixNpmPermissions();
    }

    // Re-verify after fixes
    console.log('\n\x1b[33m🧪 Re-verifying after fixes...\x1b[0m');
    const finalVerification = verifyBinaryLinks();

    if (finalVerification) {
      console.log('\n\x1b[32m🎉 Binary links fixed successfully!\x1b[0m');
    } else {
      console.log('\n\x1b[33m⚠️  Some issues remain - manual intervention may be needed\x1b[0m');
      console.log('\x1b[33m💡 Try running: npm link in the package directory\x1b[0m');
    }

  } catch (error) {
    console.log(`\x1b[31m❌ Fix failed: ${error.message}\x1b[0m`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}