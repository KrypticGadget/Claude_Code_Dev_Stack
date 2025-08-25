#!/usr/bin/env node
/**
 * Universal Hook Installer for Claude Code Dev Stack
 * Copies hooks to ~/.claude/hooks/ and ensures they work on any platform
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const PlatformDetector = require('./detect-platform.js');

class HookInstaller {
  constructor() {
    this.detector = new PlatformDetector();
    this.config = this.detector.getConfig();
    this.hooksDir = this.config.paths.hooksDir;
    
    // Find source hooks directory
    this.sourceHooksDir = this.findSourceHooks();
  }

  findSourceHooks() {
    // Try multiple possible locations for hooks
    const possiblePaths = [
      path.join(__dirname, '..', 'src', 'core', 'hooks'),
      path.join(__dirname, '..', 'core', 'hooks'),
      path.join(__dirname, '..', 'hooks'),
      path.join(process.cwd(), 'src', 'core', 'hooks'),
      path.join(process.cwd(), 'core', 'hooks')
    ];
    
    for (const hookPath of possiblePaths) {
      if (fs.existsSync(hookPath)) {
        return hookPath;
      }
    }
    
    console.error('❌ Could not find hooks source directory');
    return null;
  }

  ensureDirectories() {
    // Create necessary directories
    const claudeDir = path.dirname(this.hooksDir);
    
    if (!fs.existsSync(claudeDir)) {
      fs.mkdirSync(claudeDir, { recursive: true });
      console.log('✅ Created', claudeDir);
    }
    
    if (!fs.existsSync(this.hooksDir)) {
      fs.mkdirSync(this.hooksDir, { recursive: true });
      console.log('✅ Created', this.hooksDir);
    }
  }

  copyHooks() {
    if (!this.sourceHooksDir) return false;
    
    // Define core hooks to install
    const coreHooks = [
      // Statusline
      { name: 'claude_statusline.py', source: 'statusline/claude_statusline.py' },
      { name: 'test_statusline.py', source: 'statusline/test_statusline.py' },
      
      // Agent system
      { name: 'master_orchestrator.py', source: 'agent/master_orchestrator.py' },
      { name: 'smart_orchestrator.py', source: 'agent/smart_orchestrator.py' },
      { name: 'agent_mention_parser.py', source: 'agent/agent_mention_parser.py' },
      { name: 'agent_enhancer_v3.py', source: 'agent/agent_enhancer_v3.py' },
      
      // Context and session
      { name: 'context_manager.py', source: 'context/context_manager.py' },
      { name: 'session_loader.py', source: 'session/session_loader.py' },
      { name: 'session_saver.py', source: 'session/session_saver.py' },
      
      // Commands and routing
      { name: 'slash_command_router.py', source: 'commands/slash_command_router.py' },
      { name: 'parallel_execution_engine.py', source: 'execution/parallel_execution_engine.py' },
      
      // Monitoring
      { name: 'performance_monitor.py', source: 'monitoring/performance_monitor.py' },
      { name: 'model_tracker.py', source: 'monitoring/model_tracker.py' },
      { name: 'status_line_manager.py', source: 'monitoring/status_line_manager.py' },
      
      // Environment
      { name: 'venv_enforcer.py', source: 'environment/venv_enforcer.py' },
      { name: 'planning_trigger.py', source: 'planning/planning_trigger.py' },
      
      // Audio
      { name: 'audio_player.py', source: 'audio/audio_player_v3.py' },
      { name: 'audio_controller.py', source: 'audio/audio_controller.py' }
    ];
    
    let copiedCount = 0;
    let failedHooks = [];
    
    for (const hook of coreHooks) {
      const sourcePath = path.join(this.sourceHooksDir, hook.source);
      const destPath = path.join(this.hooksDir, hook.name);
      
      // Try alternate paths if primary doesn't exist
      let actualSource = sourcePath;
      if (!fs.existsSync(actualSource)) {
        // Try without subdirectory
        actualSource = path.join(this.sourceHooksDir, hook.name);
        
        if (!fs.existsSync(actualSource)) {
          // Try in root hooks dir
          actualSource = path.join(this.sourceHooksDir, 'hooks', hook.name);
        }
      }
      
      if (fs.existsSync(actualSource)) {
        try {
          fs.copyFileSync(actualSource, destPath);
          
          // Make executable on Unix systems
          if (!this.config.environment.isWindows) {
            fs.chmodSync(destPath, '755');
          }
          
          copiedCount++;
          console.log(`✅ Installed ${hook.name}`);
        } catch (error) {
          console.error(`❌ Failed to copy ${hook.name}:`, error.message);
          failedHooks.push(hook.name);
        }
      } else {
        // Create a placeholder hook that does nothing
        const placeholderContent = `#!/usr/bin/env python3
"""
Placeholder for ${hook.name}
This hook is not yet available in your installation.
"""
import sys
import json

if __name__ == "__main__":
    # Read input but do nothing
    try:
        input_data = sys.stdin.read()
        # Pass through without modification
        print(input_data, end='')
    except:
        pass
`;
        fs.writeFileSync(destPath, placeholderContent);
        console.log(`⚠️  Created placeholder for ${hook.name}`);
      }
    }
    
    console.log(`\n📦 Installed ${copiedCount} hooks to ${this.hooksDir}`);
    if (failedHooks.length > 0) {
      console.log(`⚠️  Failed hooks: ${failedHooks.join(', ')}`);
    }
    
    return copiedCount > 0;
  }

  validatePython() {
    console.log('\n🐍 Validating Python installation...');
    
    try {
      const version = execSync(`${this.config.python.command} --version`, { stdio: 'pipe' });
      console.log(`✅ Python found: ${version.toString().trim()}`);
      return true;
    } catch (error) {
      console.error('❌ Python not found or not working');
      console.log('   Please install Python 3.x to use hooks');
      return false;
    }
  }

  testHook(hookName) {
    const hookPath = path.join(this.hooksDir, hookName);
    
    if (!fs.existsSync(hookPath)) {
      return false;
    }
    
    try {
      // Test with empty input
      const testInput = JSON.stringify({ test: true });
      const command = `echo '${testInput}' | ${this.config.python.command} "${hookPath}"`;
      
      execSync(command, { stdio: 'pipe', timeout: 3000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  testHooks() {
    console.log('\n🧪 Testing installed hooks...');
    
    const criticalHooks = [
      'claude_statusline.py',
      'master_orchestrator.py',
      'smart_orchestrator.py'
    ];
    
    let workingCount = 0;
    for (const hook of criticalHooks) {
      if (this.testHook(hook)) {
        console.log(`✅ ${hook} is working`);
        workingCount++;
      } else {
        console.log(`⚠️  ${hook} failed test`);
      }
    }
    
    return workingCount === criticalHooks.length;
  }

  install() {
    console.log('🚀 Installing Claude Code Dev Stack Hooks\n');
    console.log(`Platform: ${this.config.platform}`);
    console.log(`Python: ${this.config.python.command}`);
    console.log(`Hooks directory: ${this.hooksDir}\n`);
    
    // Step 1: Ensure directories exist
    this.ensureDirectories();
    
    // Step 2: Validate Python
    if (!this.validatePython()) {
      console.error('\n❌ Installation failed: Python is required');
      process.exit(1);
    }
    
    // Step 3: Copy hooks
    if (!this.copyHooks()) {
      console.error('\n❌ Installation failed: Could not copy hooks');
      process.exit(1);
    }
    
    // Step 4: Test hooks
    this.testHooks();
    
    // Step 5: Fix settings.json paths
    const settingsPath = path.join(this.config.paths.claudeDir, 'settings.json');
    if (fs.existsSync(settingsPath)) {
      console.log('\n🔧 Fixing settings.json paths...');
      PlatformDetector.fixSettingsJson(settingsPath);
    }
    
    console.log('\n✨ Hook installation complete!');
    console.log('Run "ccds-setup" to configure Claude Code with these hooks');
  }
}

// Run installer if called directly
if (require.main === module) {
  const installer = new HookInstaller();
  installer.install();
}

module.exports = HookInstaller;