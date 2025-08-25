#!/usr/bin/env node
/**
 * Platform Detection Utility for Claude Code Dev Stack
 * Detects OS, environment, and returns appropriate configurations
 */

const os = require('os');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class PlatformDetector {
  constructor() {
    this.platform = process.platform;
    this.homeDir = os.homedir();
    this.isWindows = this.platform === 'win32';
    this.isLinux = this.platform === 'linux';
    this.isMac = this.platform === 'darwin';
    this.isDocker = this.detectDocker();
    this.isWSL = this.detectWSL();
    this.pythonCmd = this.detectPython();
  }

  detectDocker() {
    // Check if running in Docker
    if (fs.existsSync('/.dockerenv')) return true;
    
    try {
      const cgroup = fs.readFileSync('/proc/1/cgroup', 'utf8');
      return cgroup.includes('docker') || cgroup.includes('containerd');
    } catch {
      return false;
    }
  }

  detectWSL() {
    // Check if running in WSL
    if (!this.isLinux) return false;
    
    try {
      const version = fs.readFileSync('/proc/version', 'utf8').toLowerCase();
      return version.includes('microsoft') || version.includes('wsl');
    } catch {
      return false;
    }
  }

  detectPython() {
    // Try different Python commands
    const commands = ['python3', 'python', 'py'];
    
    for (const cmd of commands) {
      try {
        execSync(`${cmd} --version`, { stdio: 'pipe' });
        return cmd;
      } catch {
        continue;
      }
    }
    
    // Default based on platform
    return this.isWindows ? 'python' : 'python3';
  }

  getHooksDir() {
    return path.join(this.homeDir, '.claude', 'hooks');
  }

  formatPath(filePath) {
    // Convert path to platform-specific format
    if (this.isWindows && !this.isWSL) {
      // Windows: Use backslashes
      return filePath.replace(/\//g, '\\');
    } else {
      // Unix: Use forward slashes
      return filePath.replace(/\\/g, '/');
    }
  }

  formatCommand(scriptPath) {
    // Format command for settings.json
    const normalizedPath = this.formatPath(scriptPath);
    
    if (this.isWindows && !this.isWSL) {
      // Windows: Need to escape backslashes for JSON
      const escapedPath = normalizedPath.replace(/\\/g, '\\\\');
      return `${this.pythonCmd} "${escapedPath}"`;
    } else {
      // Unix: Direct path, no quotes needed
      return `${this.pythonCmd} ${normalizedPath}`;
    }
  }

  getConfig() {
    return {
      platform: this.platform,
      os: {
        type: os.type(),
        release: os.release(),
        arch: os.arch()
      },
      environment: {
        isWindows: this.isWindows,
        isLinux: this.isLinux,
        isMac: this.isMac,
        isDocker: this.isDocker,
        isWSL: this.isWSL
      },
      paths: {
        home: this.homeDir,
        claudeDir: path.join(this.homeDir, '.claude'),
        hooksDir: this.getHooksDir(),
        separator: path.sep
      },
      python: {
        command: this.pythonCmd,
        version: this.getPythonVersion()
      }
    };
  }

  getPythonVersion() {
    try {
      const output = execSync(`${this.pythonCmd} --version`, { stdio: 'pipe' });
      return output.toString().trim();
    } catch {
      return 'Unknown';
    }
  }

  static fixSettingsJson(settingsPath) {
    // Fix paths in existing settings.json
    const detector = new PlatformDetector();
    
    if (!fs.existsSync(settingsPath)) {
      console.log('Settings file not found:', settingsPath);
      return false;
    }
    
    try {
      const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
      
      // Fix statusLine command
      if (settings.statusLine && settings.statusLine.command) {
        const statuslineScript = path.join(detector.getHooksDir(), 'claude_statusline.py');
        settings.statusLine.command = detector.formatCommand(statuslineScript);
      }
      
      // Fix all hook commands
      if (settings.hooks) {
        Object.keys(settings.hooks).forEach(hookType => {
          const hookList = settings.hooks[hookType];
          if (Array.isArray(hookList)) {
            hookList.forEach(hookConfig => {
              if (hookConfig.hooks && Array.isArray(hookConfig.hooks)) {
                hookConfig.hooks.forEach(hook => {
                  if (hook.command && hook.command.includes('.py')) {
                    // Extract script name from command
                    const scriptMatch = hook.command.match(/([a-zA-Z_]+\.py)/);
                    if (scriptMatch) {
                      const scriptName = scriptMatch[1];
                      const scriptPath = path.join(detector.getHooksDir(), scriptName);
                      hook.command = detector.formatCommand(scriptPath);
                    }
                  }
                });
              }
            });
          }
        });
      }
      
      // Write fixed settings
      fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
      console.log('✅ Settings.json paths fixed for', detector.platform);
      return true;
      
    } catch (error) {
      console.error('Error fixing settings:', error.message);
      return false;
    }
  }
}

// Export for use in other scripts
module.exports = PlatformDetector;

// If run directly, show platform info and optionally fix settings
if (require.main === module) {
  const detector = new PlatformDetector();
  const config = detector.getConfig();
  
  console.log('\n🔍 Platform Detection Results:\n');
  console.log(JSON.stringify(config, null, 2));
  
  // Check for --fix flag to fix settings.json
  if (process.argv.includes('--fix')) {
    const settingsPath = path.join(config.paths.claudeDir, 'settings.json');
    console.log('\n🔧 Fixing settings.json paths...');
    PlatformDetector.fixSettingsJson(settingsPath);
  }
}