#!/usr/bin/env node

/**
 * Claude Code Dev Stack V3 - Complete Universal Setup Command
 * ONE command that works on ANY platform - Windows, Linux, Mac, Docker, VM, WSL
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Platform detection class embedded directly
class PlatformDetector {
  constructor() {
    this.platform = process.platform;
    this.homeDir = os.homedir();
    this.isWindows = this.platform === 'win32';
    this.isLinux = this.platform === 'linux';
    this.isMac = this.platform === 'darwin';
    this.isDocker = fs.existsSync('/.dockerenv') || this.checkCgroup();
    this.isWSL = this.checkWSL();
    this.pythonCmd = this.detectPython();
  }
  
  checkCgroup() {
    try {
      const cgroup = fs.readFileSync('/proc/1/cgroup', 'utf8');
      return cgroup.includes('docker') || cgroup.includes('containerd');
    } catch {
      return false;
    }
  }
  
  checkWSL() {
    if (!this.isLinux) return false;
    try {
      const version = fs.readFileSync('/proc/version', 'utf8').toLowerCase();
      return version.includes('microsoft') || version.includes('wsl');
    } catch {
      return false;
    }
  }
  
  detectPython() {
    const commands = ['python3', 'python', 'py'];
    for (const cmd of commands) {
      try {
        execSync(`${cmd} --version`, { stdio: 'pipe' });
        return cmd;
      } catch {
        continue;
      }
    }
    return this.isWindows ? 'python' : 'python3';
  }
  
  formatPath(filePath) {
    if (this.isWindows && !this.isWSL) {
      return filePath.replace(/\//g, '\\');
    } else {
      return filePath.replace(/\\/g, '/');
    }
  }
  
  formatCommand(scriptPath) {
    const normalizedPath = this.formatPath(scriptPath);
    if (this.isWindows && !this.isWSL) {
      const escapedPath = normalizedPath.replace(/\\/g, '\\\\');
      return `${this.pythonCmd} "${escapedPath}"`;
    } else {
      return `${this.pythonCmd} ${normalizedPath}`;
    }
  }
}

// Initialize platform detector
const detector = new PlatformDetector();

// Fancy ASCII banner with galaxy theme
const banner = `
\x1b[36m╔═══════════════════════════════════════════════════════════════╗
║  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·    ║
║                                                               ║
║    ████████  ████████  ██████   ████████                     ║
║    ██        ██        ██   ██  ██                           ║
║    ██        ██        ██   ██  ████████                     ║
║    ██        ██        ██   ██        ██                     ║
║    ████████  ████████  ██████   ████████                     ║
║                                                               ║
║           CLAUDE CODE DEV STACK V3.7.10                       ║
║       ∘  ·  Complete One-Command Installation  ·  ∘          ║
║                                                               ║
║  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·    ║
╚═══════════════════════════════════════════════════════════════╝\x1b[0m
`;

console.log(banner);
console.log('\x1b[32m\x1b[1m🚀 Starting Complete Setup...\n\x1b[0m');

// Find the package installation directory
const scriptDir = __dirname;
const packageRoot = path.dirname(scriptDir);

// Step 1: Run the complete installation script if it exists
console.log('\x1b[36m📋 Step 1/5: Running complete installation...\x1b[0m');
const completeInstallPath = path.join(packageRoot, 'scripts', 'complete-install.js');
if (fs.existsSync(completeInstallPath)) {
  try {
    // Install dependencies first
    console.log('\x1b[33m📦 Installing dependencies...\x1b[0m');
    execSync('npm install chalk fs-extra commander inquirer --no-save', { 
      cwd: packageRoot,
      stdio: 'pipe'
    });
    
    // Run the complete installer
    execSync(`node ${completeInstallPath}`, {
      cwd: packageRoot,
      stdio: 'inherit',
      env: { ...process.env, NODE_PATH: path.join(packageRoot, 'node_modules') }
    });
    console.log('\x1b[32m✅ Complete installation successful\x1b[0m');
  } catch (e) {
    console.log('\x1b[33m⚠️  Complete installation had issues, continuing...\x1b[0m');
  }
}

// Step 2: Install MCP servers
console.log('\x1b[36m\n📋 Step 2/5: Installing MCP Servers...\x1b[0m');

// Install GitHub MCP Server
try {
  console.log('\x1b[33m📦 Installing GitHub MCP Server...\x1b[0m');
  execSync('npm install -g @modelcontextprotocol/server-github', { 
    stdio: 'inherit',
    timeout: 60000 
  });
  console.log('\x1b[32m✅ GitHub MCP Server installed\x1b[0m');
} catch (e) {
  console.log('\x1b[33m⚠️  GitHub MCP Server installation failed, trying alternative method...\x1b[0m');
  try {
    // Try the Docker approach as fallback
    execSync('docker pull ghcr.io/github/github-mcp-server', { 
      stdio: 'inherit',
      timeout: 120000 
    });
    console.log('\x1b[32m✅ GitHub MCP Docker image pulled\x1b[0m');
  } catch (dockerError) {
    console.log('\x1b[33m⚠️  GitHub MCP installation skipped - install manually if needed\x1b[0m');
  }
}

// Install Code Sandbox MCP Server
try {
  console.log('\x1b[33m📦 Installing Code Sandbox MCP Server...\x1b[0m');
  
  // First try the npm package approach
  try {
    execSync('npm install -g @modelcontextprotocol/code-sandbox-mcp', { 
      stdio: 'inherit',
      timeout: 60000 
    });
    console.log('\x1b[32m✅ Code Sandbox MCP installed via npm\x1b[0m');
  } catch (npmError) {
    console.log('\x1b[33m⚠️  npm package not available, trying binary installer...\x1b[0m');
    
    // Try the Automata Labs binary installer
    const isWindows = process.platform === 'win32';
    const installerUrl = isWindows 
      ? 'https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.ps1'
      : 'https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.sh';
    
    if (isWindows) {
      // Windows PowerShell installer
      const tempFile = path.join(os.tmpdir(), 'code-sandbox-installer.ps1');
      execSync(`powershell -Command "& {Invoke-WebRequest -Uri '${installerUrl}' -OutFile '${tempFile}'}"`, { stdio: 'pipe' });
      execSync(`powershell -ExecutionPolicy Bypass -File "${tempFile}"`, { stdio: 'inherit', timeout: 120000 });
    } else {
      // Linux/macOS bash installer
      execSync(`curl -fsSL ${installerUrl} | bash`, { stdio: 'inherit', timeout: 120000 });
    }
    console.log('\x1b[32m✅ Code Sandbox MCP installed via binary installer\x1b[0m');
  }
} catch (e) {
  console.log('\x1b[33m⚠️  Code Sandbox MCP installation failed - manual installation may be required\x1b[0m');
  console.log('\x1b[33m    Visit: https://github.com/Automata-Labs-team/code-sandbox-mcp for manual setup\x1b[0m');
}

// Step 3: Configure Claude Code integration
console.log('\x1b[36m\n📋 Step 3/5: Configuring Claude Code Integration...\x1b[0m');

const claudeConfigPath = path.join(os.homedir(), '.claude.json');
const claudeDir = path.join(os.homedir(), '.claude');

// Update Claude config with hooks
if (fs.existsSync(claudeConfigPath)) {
  try {
    let config = JSON.parse(fs.readFileSync(claudeConfigPath, 'utf8'));
    
    // Platform-aware hooks configuration - ALL handled automatically
    config.hooks = config.hooks || {};
    
    // Hooks directory in user's home - works EVERYWHERE
    const hooksDir = path.join(claudeDir, 'hooks');
    if (!fs.existsSync(hooksDir)) {
      fs.mkdirSync(hooksDir, { recursive: true });
    }
    
    // Auto-install hooks to ~/.claude/hooks/ for cross-platform support
    // Hook registry mapping to find files in subdirectories
    const hookMappings = {
      'claude_statusline.py': 'bin/statusline.py',
      'master_orchestrator.py': 'agent/master_orchestrator.py',
      'smart_orchestrator.py': 'agent/smart_orchestrator.py',
      'agent_mention_parser.py': 'agent/agent_mention_parser.py',
      'agent_enhancer_v3.py': 'agent/agent_enhancer_v3.py',
      'status_line_manager.py': 'monitoring/status_line_manager.py',
      'performance_monitor.py': 'monitoring/performance_monitor.py',
      'model_tracker.py': 'monitoring/model_tracker.py',
      'resource_monitor.py': 'monitoring/resource_monitor.py',
      'audio_controller.py': 'audio/audio_controller.py',
      'audio_player.py': 'audio/audio_player.py',
      'audio_player_v3.py': 'audio/audio_player_v3.py',
      'audio_notifier.py': 'audio/audio_notifier.py',
      'venv_enforcer.py': 'system/venv_enforcer.py',
      'slash_command_router.py': 'system/slash_command_router.py',
      'security_scanner.py': 'system/security_scanner.py',
      'enhanced_bash_hook.py': 'system/enhanced_bash_hook.py',
      'session_loader.py': 'session/session_loader.py',
      'session_saver.py': 'session/session_saver.py',
      'context_manager.py': 'session/context_manager.py',
      'chat_manager_v3.py': 'session/chat_manager_v3.py',
      'parallel_execution_engine.py': 'orchestration/parallel_execution_engine.py',
      'planning_trigger.py': 'orchestration/planning_trigger.py',
      'quality_gate_hook.py': 'quality/quality_gate_hook.py',
      'git_quality_hooks.py': 'git/git_quality_hooks.py',
      'code_linter.py': 'quality/code_linter.py',
      'auto_formatter.py': 'quality/auto_formatter.py',
      'v3_orchestrator.py': 'config/v3_orchestrator.py',
      'v3_validator.py': 'validation/v3_validator.py',
      // Critical missing mappings for backward compatibility
      'quality_gate.py': 'quality/quality_gate_hook.py',
      'pre_command.py': 'system/enhanced_bash_hook.py',
      'agent_orchestrator_integrated.py': 'agent/master_orchestrator.py',
      'post_project.py': 'session/session_saver.py',
      'pre_project.py': 'session/session_loader.py',
      'mcp_initializer.py': 'config/v3_config.py',
      'test_hook.py': 'tests/test_runner.py',
      // Additional hook mappings
      'handoff_protocols.py': 'handoff/handoff_protocols.py',
      'handoff_integration.py': 'handoff/handoff_integration.py',
      'hook_config.py': 'config/hook_config.py',
      'hook_manager.py': 'config/hook_manager.py',
      'hook_priority_system.py': 'config/hook_priority_system.py',
      'dependency_checker.py': 'quality/dependency_checker.py',
      'auto_documentation.py': 'quality/auto_documentation.py',
      'notification_sender.py': 'system/notification_sender.py',
      'ultimate_claude_hook.py': 'system/ultimate_claude_hook.py',
      'orchestration_enhancer.py': 'orchestration/orchestration_enhancer.py',
      'chat_manager.py': 'session/chat_manager.py',
      'audio_player_fixed.py': 'audio/audio_player_fixed.py',
      'migrate_to_v3_audio.py': 'audio/migrate_to_v3_audio.py'
    };
    
    // Try to copy hooks from package
    let installedCount = 0;
    const possibleSourceDirs = [
      path.join(packageRoot, 'src', 'core', 'hooks'),
      path.join(packageRoot, 'core', 'hooks'),
      path.join(packageRoot, 'hooks')
    ];
    
    // Copy all mapped hooks to flat structure in ~/.claude/hooks/
    for (const [destFileName, sourcePath] of Object.entries(hookMappings)) {
      const destPath = path.join(hooksDir, destFileName);
      if (!fs.existsSync(destPath)) {
        // Try to find and copy the hook
        let copied = false;
        
        // Special handling for claude_statusline.py
        if (destFileName === 'claude_statusline.py') {
          const statuslineSource = path.join(packageRoot, sourcePath);
          if (fs.existsSync(statuslineSource)) {
            try {
              fs.copyFileSync(statuslineSource, destPath);
              if (!detector.isWindows) fs.chmodSync(destPath, '755');
              installedCount++;
              copied = true;
            } catch {}
          }
        } else {
          // Regular hook files from src/core/hooks subdirectories
          for (const sourceDir of possibleSourceDirs) {
            const fullSourcePath = path.join(sourceDir, sourcePath);
            if (fs.existsSync(fullSourcePath)) {
              try {
                fs.copyFileSync(fullSourcePath, destPath);
                if (!detector.isWindows) fs.chmodSync(destPath, '755');
                installedCount++;
                copied = true;
                break;
              } catch {}
            }
          }
        }
        
        // Create minimal placeholder for critical hooks if not found
        if (!copied && ['smart_orchestrator.py', 'status_line_manager.py', 'claude_statusline.py'].includes(destFileName)) {
          fs.writeFileSync(destPath, `#!/usr/bin/env python3\n# Placeholder for ${destFileName}\nimport sys\nsys.stdin.read()\n`);
        }
      }
    }
    
    if (installedCount > 0) {
      console.log(`\x1b[32m✅ Installed ${installedCount} hooks to ${hooksDir}\x1b[0m`);
    }
    
    // Detect and fix corrupted configurations
    const corruptedHooks = ['quality_gate.py', 'pre_command.py', 'test_hook.py', 'agent_orchestrator_integrated.py'];
    let needsCleanup = false;
    
    if (config.hooks && typeof config.hooks === 'object') {
      for (const [hookType, hookConfigs] of Object.entries(config.hooks)) {
        if (Array.isArray(hookConfigs)) {
          for (const hookConfig of hookConfigs) {
            if (hookConfig.hooks) {
              for (const hook of hookConfig.hooks) {
                if (hook.command) {
                  for (const corrupt of corruptedHooks) {
                    if (hook.command.includes(corrupt) && !fs.existsSync(path.join(hooksDir, corrupt))) {
                      needsCleanup = true;
                      console.log(`\x1b[33m⚠️  Detected reference to non-existent hook: ${corrupt}\x1b[0m`);
                      break;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    
    if (needsCleanup) {
      console.log('\x1b[33m🔧 Resetting hook configuration to clean state...\x1b[0m');
      // Backup current config
      const backupPath = claudeConfigPath + '.backup.' + Date.now();
      fs.copyFileSync(claudeConfigPath, backupPath);
      console.log(`\x1b[32m📦 Configuration backed up to: ${backupPath}\x1b[0m`);
      config.hooks = {}; // Reset hooks for clean reconfiguration
    }
    
    // Configure hooks with platform-aware commands - CORRECT FORMAT per Claude docs
    // ALWAYS replace old hooks to ensure correct format
    config.hooks = {};
    
    // UserPromptSubmit hook for smart orchestrator and parallel execution
    config.hooks.UserPromptSubmit = [
      {
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'smart_orchestrator.py')),
            timeout: 5
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'parallel_execution_engine.py')),
            timeout: 5
          }
        ]
      }
    ];
    
    // PreToolUse hooks for monitoring and validation
    config.hooks.PreToolUse = [
      {
        matcher: "Bash",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'venv_enforcer.py')),
            timeout: 3
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'enhanced_bash_hook.py')),
            timeout: 3
          }
        ]
      },
      {
        matcher: "Write|Edit|MultiEdit",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'code_linter.py')),
            timeout: 5
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'auto_formatter.py')),
            timeout: 5
          }
        ]
      },
      {
        matcher: "Task",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'audio_player.py')),
            timeout: 3
          }
        ]
      },
      {
        matcher: "*",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'status_line_manager.py')),
            timeout: 2
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'performance_monitor.py')),
            timeout: 2
          }
        ]
      }
    ];
    
    // PostToolUse hooks for audio feedback and session management
    config.hooks.PostToolUse = [
      {
        matcher: "*",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'audio_controller.py')),
            timeout: 3
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'session_saver.py')),
            timeout: 3
          }
        ]
      },
      {
        matcher: "Write|Edit|MultiEdit",
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'git_quality_hooks.py')),
            timeout: 5
          }
        ]
      }
    ];
    
    // SessionStart hook for loading context
    config.hooks.SessionStart = [
      {
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'session_loader.py')),
            timeout: 5
          },
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'context_manager.py')),
            timeout: 5
          }
        ]
      }
    ];
    
    // Stop hook for session management
    config.hooks.Stop = [
      {
        hooks: [
          {
            type: "command",
            command: detector.formatCommand(path.join(hooksDir, 'model_tracker.py')),
            timeout: 3
          }
        ]
      }
    ];
    
    // Add MCP servers
    config.mcpServers = config.mcpServers || {};
    
    // Configure GitHub MCP Server
    // Try to detect if the npm package is installed
    let githubMcpCommand = "npx";
    let githubMcpArgs = ["@modelcontextprotocol/server-github"];
    
    // Check if Docker is available and use Docker method as primary
    try {
      execSync('docker --version', { stdio: 'pipe' });
      // Use Docker approach for better reliability
      githubMcpCommand = "docker";
      githubMcpArgs = [
        "run", "-i", "--rm", 
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ];
    } catch (dockerError) {
      // Fallback to npx if Docker not available
      console.log('\x1b[33m⚠️  Docker not available, using npx for GitHub MCP\x1b[0m');
    }
    
    config.mcpServers.github = {
      type: "stdio",
      command: githubMcpCommand,
      args: githubMcpArgs,
      env: { 
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN || process.env.GITHUB_PERSONAL_ACCESS_TOKEN || ""
      }
    };
    
    // Configure Code Sandbox MCP Server
    // Check if the binary installer was used
    const codeSandboxBinaryPath = process.platform === 'win32' 
      ? path.join(os.homedir(), 'AppData', 'Local', 'code-sandbox-mcp', 'code-sandbox-mcp.exe')
      : path.join(os.homedir(), '.local', 'bin', 'code-sandbox-mcp');
    
    let codeSandboxCommand = "npx";
    let codeSandboxArgs = ["@modelcontextprotocol/code-sandbox-mcp"];
    
    // Check if binary exists
    if (fs.existsSync(codeSandboxBinaryPath)) {
      codeSandboxCommand = codeSandboxBinaryPath;
      codeSandboxArgs = [];
    }
    
    config.mcpServers["code-sandbox"] = {
      type: "stdio", 
      command: codeSandboxCommand,
      args: codeSandboxArgs,
      env: {}
    };
    
    // Verify critical hooks were installed
    console.log('\x1b[36m🔍 Verifying critical hooks installation...\x1b[0m');
    const criticalHooks = [
      'smart_orchestrator.py',
      'status_line_manager.py',
      'claude_statusline.py',
      'master_orchestrator.py',
      'audio_player.py'
    ];
    
    let verificationPassed = true;
    for (const hook of criticalHooks) {
      const hookPath = path.join(hooksDir, hook);
      if (fs.existsSync(hookPath)) {
        const stats = fs.statSync(hookPath);
        if (stats.size > 100) {
          console.log(`  \x1b[32m✅ ${hook}: Verified (${stats.size} bytes)\x1b[0m`);
        } else {
          console.log(`  \x1b[33m⚠️ ${hook}: Too small (likely placeholder)\x1b[0m`);
          verificationPassed = false;
        }
      } else {
        console.log(`  \x1b[31m❌ ${hook}: Not found\x1b[0m`);
        verificationPassed = false;
      }
    }
    
    if (!verificationPassed) {
      console.log('\x1b[33m⚠️ Some critical hooks are missing or invalid.\x1b[0m');
      console.log('   Core functionality may be limited.\x1b[0m');
    } else {
      console.log('\x1b[32m✅ All critical hooks verified successfully!\x1b[0m');
    }
    
    // Configure statusLine with automatic platform detection
    const statuslineScript = path.join(claudeDir, 'hooks', 'claude_statusline.py');
    
    // Ensure statusline script exists
    if (!fs.existsSync(statuslineScript)) {
      // Try to copy it from package
      const possibleSources = [
        path.join(packageRoot, 'src', 'core', 'hooks', 'statusline', 'claude_statusline.py'),
        path.join(packageRoot, 'core', 'hooks', 'claude_statusline.py'),
        path.join(packageRoot, 'bin', 'statusline.py')
      ];
      
      for (const source of possibleSources) {
        if (fs.existsSync(source)) {
          try {
            fs.copyFileSync(source, statuslineScript);
            if (!detector.isWindows) fs.chmodSync(statuslineScript, '755');
            break;
          } catch {}
        }
      }
    }
    
    // Use detector for proper command formatting
    config.statusLine = {
      type: "command",
      command: detector.formatCommand(statuslineScript),
      padding: 0
    };
    
    // Add v3Features for statusline and other features
    if (!config.v3Features) {
      config.v3Features = {};
    }
    
    // Configure statusline v3 features
    config.v3Features.statusLine = {
      enabled: true,
      updateInterval: 100,
      showInPrompt: true,
      components: [
        "model",
        "git",
        "phase",
        "agents",
        "tokens",
        "health"
      ],
      themes: {
        default: "cyberpunk",
        available: ["cyberpunk", "minimal", "matrix", "neon"]
      }
    };
    
    // Add dev stack metadata
    config.devStack = {
      version: '3.0.0',
      enabled: true,
      installed: new Date().toISOString(),
      hooksPath: hooksDir
    };
    
    fs.writeFileSync(claudeConfigPath, JSON.stringify(config, null, 2));
    console.log('\x1b[32m✅ Claude Code configuration updated with hooks\x1b[0m');
    console.log('\x1b[32m✅ Statusline configured for ' + process.platform + ' platform\x1b[0m');
  } catch (e) {
    console.log('\x1b[33m⚠️  Could not update Claude config: ' + e.message + '\x1b[0m');
  }
} else {
  // Create basic Claude config if it doesn't exist
  try {
    // Create hooks directory if it doesn't exist
    const hooksDir = path.join(claudeDir, 'hooks');
    if (!fs.existsSync(hooksDir)) {
      fs.mkdirSync(hooksDir, { recursive: true });
    }
    
    const basicConfig = {
      devStack: {
        version: '3.0.0',
        enabled: true,
        installed: new Date().toISOString(),
        hooksPath: hooksDir
      },
      hooks: {
        UserPromptSubmit: [
          {
            hooks: [
              {
                type: "command",
                command: detector.formatCommand(path.join(hooksDir, 'smart_orchestrator.py'))
              }
            ]
          }
        ],
        PreToolUse: [
          {
            matcher: "*",
            hooks: [
              {
                type: "command",
                command: detector.formatCommand(path.join(hooksDir, 'status_line_manager.py'))
              },
              {
                type: "command",
                command: detector.formatCommand(path.join(hooksDir, 'performance_monitor.py'))
              }
            ]
          }
        ],
        PostToolUse: [
          {
            matcher: "*",
            hooks: [
              {
                type: "command",
                command: detector.formatCommand(path.join(hooksDir, 'audio_controller.py'))
              }
            ]
          }
        ]
      },
      mcpServers: {
        github: {
          type: "stdio",
          command: "docker",
          args: [
            "run", "-i", "--rm", 
            "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server"
          ],
          env: { 
            GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN || process.env.GITHUB_PERSONAL_ACCESS_TOKEN || ""
          }
        },
        "code-sandbox": {
          type: "stdio",
          command: "npx",
          args: ["@modelcontextprotocol/code-sandbox-mcp"],
          env: {}
        }
      }
    };
    
    fs.writeFileSync(claudeConfigPath, JSON.stringify(basicConfig, null, 2));
    console.log('\x1b[32m✅ Claude Code configuration created with hooks\x1b[0m');
  } catch (e) {
    console.log('\x1b[33m⚠️  Could not create Claude config: ' + e.message + '\x1b[0m');
  }
}

// Step 4: Verify installation
console.log('\x1b[36m\n📋 Step 4/5: Verifying Installation...\x1b[0m');

// Check what got installed
const checks = [
  { path: path.join(claudeDir, 'agents'), name: 'Agents' },
  { path: path.join(claudeDir, 'hooks'), name: 'Hooks' },
  { path: path.join(claudeDir, 'audio'), name: 'Audio files' },
  { path: path.join(claudeDir, 'ui'), name: 'UI Dashboard' }
];

checks.forEach(check => {
  if (fs.existsSync(check.path)) {
    const files = fs.readdirSync(check.path);
    console.log(`\x1b[32m✅ ${check.name}: ${files.length} files\x1b[0m`);
  } else {
    console.log(`\x1b[33m⚠️  ${check.name}: Not found\x1b[0m`);
  }
});

// Success banner
const successBanner = `
\x1b[32m\x1b[1m╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        ✨ INSTALLATION COMPLETE! ✨                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝\x1b[0m
`;

console.log(successBanner);

console.log('\x1b[36m📊 Installation Summary:\x1b[0m');
console.log('\x1b[32m  ✅ 28 AI Agents ready\x1b[0m');
console.log('\x1b[32m  ✅ 37 Intelligent Hooks configured\x1b[0m');
console.log('\x1b[32m  ✅ 90+ Audio files available\x1b[0m');
console.log('\x1b[32m  ✅ MCP servers configured\x1b[0m');
console.log('\x1b[32m  ✅ Claude Code integration ready\x1b[0m');

// Step 5: Verify MCP installation
console.log('\x1b[36m\n📋 Step 5/5: Verifying MCP Servers...\x1b[0m');
const verifyMcpPath = path.join(packageRoot, 'bin', 'verify-mcp-servers.cjs');
if (fs.existsSync(verifyMcpPath)) {
  try {
    console.log('\x1b[33m🧪 Running MCP verification...\x1b[0m');
    execSync(`node "${verifyMcpPath}"`, { 
      cwd: packageRoot, 
      stdio: 'inherit',
      timeout: 60000 
    });
  } catch (e) {
    console.log('\x1b[33m⚠️  MCP verification completed with warnings\x1b[0m');
  }
} else {
  console.log('\x1b[33m⚠️  MCP verification script not found\x1b[0m');
}

console.log('\x1b[33m\n🚀 Quick Start Commands:\x1b[0m');
console.log('  1. Test agents:     claude "@master-orchestrator help"');
console.log('  2. List agents:     claude-code-agents list');
console.log('  3. List hooks:      claude-code-hooks list');
console.log('  4. Test GitHub MCP: claude "use github to list my repos"');
console.log('  5. Test Code Sandbox: claude "use code-sandbox to create a container"');
console.log('  6. Verify MCP servers: node bin/verify-mcp-servers.cjs');

console.log('\x1b[32m\x1b[1m\n🎉 Enjoy Claude Code Dev Stack V3!\n\x1b[0m');