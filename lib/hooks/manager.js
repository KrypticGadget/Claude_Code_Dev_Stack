/**
 * Hook Manager - Handles installation and management of the 37 intelligent hooks
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class HookManager {
  constructor(options = {}) {
    this.options = options;
    this.hooksPath = path.join(__dirname, '../../core/hooks/hooks');
    this.installedHooks = new Map();
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    
    console.log(chalk.blue('🪝 Initializing Hook Manager...'));
    
    // Load available hooks
    await this.loadAvailableHooks();
    
    this.initialized = true;
    console.log(chalk.green('✅ Hook Manager initialized'));
  }

  async loadAvailableHooks() {
    try {
      const hookFiles = await fs.readdir(this.hooksPath);
      const hooks = hookFiles
        .filter(file => file.endsWith('.py') && !file.startsWith('__'))
        .map(file => ({
          name: path.basename(file, '.py'),
          path: path.join(this.hooksPath, file),
          installed: false
        }));

      for (const hook of hooks) {
        this.installedHooks.set(hook.name, hook);
      }

      console.log(chalk.blue(`📋 Loaded ${hooks.length} available hooks`));
    } catch (error) {
      throw new Error(`Failed to load hooks: ${error.message}`);
    }
  }

  async install(targetPath = null) {
    console.log(chalk.blue('🚀 Installing all hooks...'));
    
    const claudeConfigPath = targetPath || await this.detectClaudeConfigPath();
    const hooksTargetPath = path.join(claudeConfigPath, 'hooks');
    
    // Ensure target directory exists
    await fs.ensureDir(hooksTargetPath);
    
    const results = {
      installed: 0,
      failed: 0,
      errors: []
    };

    for (const [hookName, hook] of this.installedHooks) {
      try {
        await this.installSingle(hookName, targetPath);
        results.installed++;
        console.log(chalk.green(`  ✅ ${hookName}`));
      } catch (error) {
        results.failed++;
        results.errors.push({ hook: hookName, error: error.message });
        console.log(chalk.red(`  ❌ ${hookName}: ${error.message}`));
      }
    }

    console.log(chalk.blue(`📊 Installation complete: ${results.installed} installed, ${results.failed} failed`));
    return results;
  }

  async installSingle(hookName, targetPath = null) {
    const hook = this.installedHooks.get(hookName);
    if (!hook) {
      throw new Error(`Hook "${hookName}" not found`);
    }

    const claudeConfigPath = targetPath || await this.detectClaudeConfigPath();
    const hooksTargetPath = path.join(claudeConfigPath, 'hooks');
    const targetFilePath = path.join(hooksTargetPath, `${hookName}.py`);

    // Ensure target directory exists
    await fs.ensureDir(hooksTargetPath);

    // Copy hook file
    await fs.copy(hook.path, targetFilePath);

    // Mark as installed
    hook.installed = true;
    hook.installedPath = targetFilePath;

    return {
      success: true,
      hook: hookName,
      path: targetFilePath
    };
  }

  async detectClaudeConfigPath() {
    const possiblePaths = [
      path.join(process.env.HOME || process.env.USERPROFILE, '.claude'),
      path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'claude'),
      path.join(process.cwd(), '.claude')
    ];

    for (const testPath of possiblePaths) {
      if (await fs.pathExists(testPath)) {
        return testPath;
      }
    }

    // Default to home directory
    const defaultPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude');
    await fs.ensureDir(defaultPath);
    return defaultPath;
  }

  getHookCount() {
    return this.installedHooks.size;
  }

  getStatus() {
    const installedCount = Array.from(this.installedHooks.values()).filter(h => h.installed).length;
    return {
      available: this.installedHooks.size,
      installed: installedCount,
      initialized: this.initialized
    };
  }

  async listAvailable() {
    const hooks = Array.from(this.installedHooks.values()).map(hook => ({
      name: hook.name,
      installed: hook.installed,
      path: hook.path,
      category: this.getHookCategory(hook.name),
      description: this.getHookDescription(hook.name),
      trigger: this.getHookTrigger(hook.name)
    }));

    return hooks.sort((a, b) => a.name.localeCompare(b.name));
  }

  getHookCategory(hookName) {
    const categories = {
      'Core Orchestration': [
        'master_orchestrator', 'smart_orchestrator', 'v3_orchestrator',
        'orchestration_enhancer', 'agent_enhancer_v3'
      ],
      'Audio & Feedback': [
        'audio_controller', 'audio_notifier', 'audio_player',
        'audio_player_v3', 'audio_player_fixed'
      ],
      'Communication & Routing': [
        'agent_mention_parser', 'chat_manager', 'chat_manager_v3',
        'slash_command_router', 'notification_sender'
      ],
      'Quality & Security': [
        'quality_gate_hook', 'security_scanner', 'code_linter',
        'git_quality_hooks', 'v3_validator'
      ],
      'Performance & Monitoring': [
        'performance_monitor', 'resource_monitor', 'status_line_manager',
        'model_tracker', 'context_manager'
      ],
      'Documentation & Automation': [
        'auto_documentation', 'auto_formatter', 'dependency_checker',
        'planning_trigger', 'session_loader', 'session_saver'
      ],
      'Development Tools': [
        'enhanced_bash_hook', 'parallel_execution_engine', 'ultimate_claude_hook',
        'venv_enforcer', 'migrate_to_v3_audio', 'v3_config'
      ]
    };

    for (const [category, hooks] of Object.entries(categories)) {
      if (hooks.includes(hookName)) {
        return category;
      }
    }

    return 'General';
  }

  getHookDescription(hookName) {
    const descriptions = {
      'master_orchestrator': 'Master orchestration and workflow management',
      'smart_orchestrator': 'Intelligent agent routing and task distribution',
      'v3_orchestrator': 'Version 3 orchestration engine',
      'orchestration_enhancer': 'Enhanced orchestration capabilities',
      'agent_enhancer_v3': 'Agent enhancement and optimization',
      'audio_controller': 'Audio feedback control system',
      'audio_notifier': 'Smart audio notification system',
      'audio_player': 'Core audio playback functionality',
      'audio_player_v3': 'Version 3 audio player',
      'audio_player_fixed': 'Fixed audio player implementation',
      'agent_mention_parser': 'Agent mention parsing and routing',
      'chat_manager': 'Chat session management',
      'chat_manager_v3': 'Version 3 chat management',
      'slash_command_router': 'Slash command routing and handling',
      'notification_sender': 'System notification dispatcher',
      'quality_gate_hook': 'Quality gate enforcement',
      'security_scanner': 'Security vulnerability scanning',
      'code_linter': 'Code quality linting',
      'git_quality_hooks': 'Git workflow quality checks',
      'v3_validator': 'Version 3 validation system',
      'performance_monitor': 'System performance monitoring',
      'resource_monitor': 'Resource usage tracking',
      'status_line_manager': 'Status line management',
      'model_tracker': 'Model usage tracking',
      'context_manager': 'Context and session management',
      'auto_documentation': 'Automatic documentation generation',
      'auto_formatter': 'Code formatting automation',
      'dependency_checker': 'Dependency validation and management',
      'planning_trigger': 'Planning and task trigger system',
      'session_loader': 'Session loading and restoration',
      'session_saver': 'Session saving and persistence',
      'enhanced_bash_hook': 'Enhanced bash command processing',
      'parallel_execution_engine': 'Parallel task execution',
      'ultimate_claude_hook': 'Ultimate Claude integration hook',
      'venv_enforcer': 'Virtual environment enforcement',
      'migrate_to_v3_audio': 'Audio system migration utility',
      'v3_config': 'Version 3 configuration management'
    };

    return descriptions[hookName] || 'Intelligent automation hook';
  }

  getHookTrigger(hookName) {
    const triggers = {
      'master_orchestrator': 'Agent coordination events',
      'smart_orchestrator': 'Task routing requests',
      'v3_orchestrator': 'Workflow orchestration events',
      'audio_controller': 'Audio system events',
      'audio_player': 'Audio playback requests',
      'agent_mention_parser': 'Agent mention detection',
      'chat_manager': 'Chat session events',
      'security_scanner': 'Code analysis triggers',
      'performance_monitor': 'Performance thresholds',
      'auto_documentation': 'Code change events',
      'git_quality_hooks': 'Git commit hooks',
      'enhanced_bash_hook': 'Bash command execution'
    };

    return triggers[hookName] || 'Various system events';
  }
}