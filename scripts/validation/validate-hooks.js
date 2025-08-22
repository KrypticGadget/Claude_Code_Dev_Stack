#!/usr/bin/env node

/**
 * Hook Validation Script for Claude Code Dev Stack V3
 * Ensures all Python hooks are properly configured and executable
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn, execSync } = require('child_process');

const scriptDir = __dirname;
const packageRoot = path.dirname(scriptDir);
const coreHooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');

// Required hooks for V3 functionality
const REQUIRED_HOOKS = [
  {
    file: 'status_line_manager.py',
    pattern: '*',
    description: 'Status line updates and context tracking',
    critical: true
  },
  {
    file: 'smart_orchestrator.py', 
    pattern: '@*',
    description: 'Smart agent routing with @mentions',
    critical: true
  },
  {
    file: 'audio_controller.py',
    pattern: '*', 
    description: 'Audio feedback system',
    critical: false
  },
  {
    file: 'performance_monitor.py',
    pattern: '*',
    description: 'Performance monitoring',
    critical: false
  },
  {
    file: 'context_manager.py',
    pattern: '*',
    description: 'Context management',
    critical: false
  }
];

function checkPythonInstallation() {
  console.log('🐍 Checking Python installation...');
  
  const pythonCommands = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  
  for (const cmd of pythonCommands) {
    try {
      const result = execSync(`${cmd} --version`, { encoding: 'utf8', stdio: 'pipe' });
      console.log(`✅ Found Python: ${result.trim()}`);
      return cmd;
    } catch (error) {
      // Continue to next command
    }
  }
  
  console.log('❌ Python not found. Please install Python 3.7+');
  return null;
}

function validateHookFile(hookPath) {
  console.log(`\n🔍 Validating: ${path.basename(hookPath)}`);
  
  // Check if file exists
  if (!fs.existsSync(hookPath)) {
    console.log('❌ File not found');
    return false;
  }
  
  // Check if file is readable
  try {
    const content = fs.readFileSync(hookPath, 'utf8');
    
    // Basic Python syntax checks
    if (!content.includes('#!/usr/bin/env python3') && !content.includes('#!/usr/bin/env python')) {
      console.log('⚠️  Missing shebang line');
    }
    
    if (!content.includes('import ')) {
      console.log('⚠️  No import statements found');
    }
    
    console.log('✅ File structure looks valid');
    return true;
    
  } catch (error) {
    console.log(`❌ Cannot read file: ${error.message}`);
    return false;
  }
}

function testHookExecution(pythonCmd, hookPath) {
  return new Promise((resolve) => {
    console.log(`🧪 Testing execution...`);
    
    // Test with --help flag (most hooks should support this)
    const testProcess = spawn(pythonCmd, [hookPath, '--help'], {
      stdio: 'pipe',
      timeout: 10000
    });
    
    let output = '';
    let errorOutput = '';
    
    testProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    testProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    testProcess.on('close', (code) => {
      // Accept code 0 or any code if there's helpful output
      if (code === 0 || output.includes('usage') || output.includes('help') || 
          output.includes('Claude') || errorOutput.includes('usage')) {
        console.log('✅ Hook executes successfully');
        resolve(true);
      } else {
        console.log(`❌ Execution test failed (exit code: ${code})`);
        if (errorOutput && !errorOutput.includes('No module named')) {
          console.log(`   Error preview: ${errorOutput.substring(0, 200)}...`);
        }
        resolve(false);
      }
    });
    
    testProcess.on('error', (error) => {
      console.log(`❌ Process spawn error: ${error.message}`);
      resolve(false);
    });
    
    // Kill process if it hangs
    setTimeout(() => {
      if (!testProcess.killed) {
        testProcess.kill();
        console.log('⚠️  Process timeout - killed');
        resolve(false);
      }
    }, 8000);
  });
}

function generateClaudeConfig(pythonCmd) {
  const config = {
    devStack: {
      version: '3.0.0',
      enabled: true,
      hooksPath: coreHooksDir,
      pythonCommand: pythonCmd,
      validated: new Date().toISOString()
    },
    hooks: [],
    mcpServers: {
      github: {
        command: 'github-mcp-server',
        args: [],
        env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN || '' }
      }
    }
  };
  
  // Add validated hooks
  for (const hook of REQUIRED_HOOKS) {
    const hookPath = path.join(coreHooksDir, hook.file);
    if (fs.existsSync(hookPath)) {
      config.hooks.push({
        pattern: hook.pattern,
        command: `${pythonCmd} "${hookPath}"`,
        description: hook.description,
        critical: hook.critical
      });
    }
  }
  
  return config;
}

async function main() {
  console.log('🔧 Claude Code Dev Stack V3 - Hook Validator\n');
  
  // Step 1: Check Python
  const pythonCmd = checkPythonInstallation();
  if (!pythonCmd) {
    process.exit(1);
  }
  
  // Step 2: Check core hooks directory
  console.log(`\n📁 Checking hooks directory: ${coreHooksDir}`);
  if (!fs.existsSync(coreHooksDir)) {
    console.log('❌ Core hooks directory not found');
    console.log('   Expected location:', coreHooksDir);
    process.exit(1);
  }
  console.log('✅ Hooks directory found');
  
  // Step 3: Validate each required hook
  let validHooks = 0;
  let criticalHooksFailed = 0;
  
  for (const hook of REQUIRED_HOOKS) {
    const hookPath = path.join(coreHooksDir, hook.file);
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`📝 ${hook.description}`);
    console.log(`🎯 Pattern: ${hook.pattern} | Critical: ${hook.critical ? 'Yes' : 'No'}`);
    
    const fileValid = validateHookFile(hookPath);
    if (!fileValid) {
      if (hook.critical) criticalHooksFailed++;
      continue;
    }
    
    const execValid = await testHookExecution(pythonCmd, hookPath);
    if (execValid) {
      validHooks++;
      console.log(`✅ ${hook.file} - READY`);
    } else {
      if (hook.critical) criticalHooksFailed++;
      console.log(`❌ ${hook.file} - FAILED`);
    }
  }
  
  // Step 4: Generate/update Claude config
  console.log(`\n${'='.repeat(50)}`);
  console.log('📊 VALIDATION SUMMARY');
  console.log(`✅ Valid hooks: ${validHooks}/${REQUIRED_HOOKS.length}`);
  console.log(`❌ Critical failures: ${criticalHooksFailed}`);
  
  if (criticalHooksFailed > 0) {
    console.log('\n⚠️  CRITICAL HOOKS FAILED - System may not work properly');
    console.log('   Please check Python dependencies and file permissions');
    process.exit(1);
  }
  
  if (validHooks >= REQUIRED_HOOKS.length * 0.8) { // 80% success rate
    console.log('\n🎉 Hook validation PASSED');
    
    // Generate Claude config
    const claudeConfigPath = path.join(os.homedir(), '.claude.json');
    const config = generateClaudeConfig(pythonCmd);
    
    try {
      fs.writeFileSync(claudeConfigPath, JSON.stringify(config, null, 2));
      console.log(`✅ Updated ${claudeConfigPath}`);
      console.log(`📝 Configured ${config.hooks.length} hooks`);
    } catch (error) {
      console.log(`❌ Could not write config: ${error.message}`);
    }
    
    console.log('\n🚀 Ready to use Claude Code Dev Stack V3!');
    console.log('\nTest with: claude "help"');
    
  } else {
    console.log('\n❌ Hook validation FAILED');
    console.log('   Too many hooks failed validation');
    process.exit(1);
  }
}

// Run validation
main().catch(error => {
  console.error('\n💥 Validation crashed:', error);
  console.log('\nPlease report this issue with your system details:');
  console.log(`  OS: ${os.platform()} ${os.release()}`);
  console.log(`  Node: ${process.version}`);
  console.log(`  Arch: ${os.arch()}`);
  process.exit(1);
});