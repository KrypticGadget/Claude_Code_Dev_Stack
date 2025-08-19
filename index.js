#!/usr/bin/env node

/**
 * Claude Code Dev Stack V3 - Main Entry Point
 * 
 * AI-powered development environment with 28 specialized agents,
 * intelligent hooks, and unified tooling.
 * 
 * @version 3.0.0
 * @author Claude Code Team
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs-extra';
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Core modules
import { AgentManager } from './lib/agents/manager.js';
import { HookManager } from './lib/hooks/manager.js';
import { AudioManager } from './lib/audio/manager.js';
import { ConfigManager } from './lib/config/manager.js';
import { OrchestrationEngine } from './lib/orchestration/engine.js';
import { UIManager } from './lib/ui/manager.js';

/**
 * Main Claude Code Dev Stack class
 */
export class ClaudeCodeDevStack {
  constructor(options = {}) {
    this.version = '3.0.0';
    this.agentManager = new AgentManager(options.agents);
    this.hookManager = new HookManager(options.hooks);
    this.audioManager = new AudioManager(options.audio);
    this.configManager = new ConfigManager(options.config);
    this.orchestrationEngine = new OrchestrationEngine(options.orchestration);
    this.uiManager = new UIManager(options.ui);
    
    this.initialized = false;
    this.rootPath = __dirname;
  }

  /**
   * Initialize the entire dev stack
   */
  async initialize() {
    if (this.initialized) return;

    console.log(chalk.blue('🚀 Initializing Claude Code Dev Stack V3...'));

    try {
      // Initialize core managers
      await this.configManager.initialize();
      await this.agentManager.initialize();
      await this.hookManager.initialize();
      await this.audioManager.initialize();
      await this.orchestrationEngine.initialize();
      await this.uiManager.initialize();

      this.initialized = true;
      console.log(chalk.green('✅ Claude Code Dev Stack V3 initialized successfully!'));
      
      return {
        success: true,
        version: this.version,
        agents: this.agentManager.getAgentCount(),
        hooks: this.hookManager.getHookCount(),
        audioFiles: this.audioManager.getAudioFileCount()
      };
    } catch (error) {
      console.error(chalk.red('❌ Failed to initialize Claude Code Dev Stack:'), error.message);
      throw error;
    }
  }

  /**
   * Get system status
   */
  getStatus() {
    return {
      version: this.version,
      initialized: this.initialized,
      agents: this.agentManager.getStatus(),
      hooks: this.hookManager.getStatus(),
      audio: this.audioManager.getStatus(),
      orchestration: this.orchestrationEngine.getStatus(),
      ui: this.uiManager.getStatus()
    };
  }

  /**
   * Install agents to Claude Code environment
   */
  async installAgents(targetPath = null) {
    if (!this.initialized) await this.initialize();
    return await this.agentManager.install(targetPath);
  }

  /**
   * Install hooks to Claude Code environment
   */
  async installHooks(targetPath = null) {
    if (!this.initialized) await this.initialize();
    return await this.hookManager.install(targetPath);
  }

  /**
   * Setup audio system
   */
  async setupAudio(targetPath = null) {
    if (!this.initialized) await this.initialize();
    return await this.audioManager.setup(targetPath);
  }

  /**
   * Start the unified PWA
   */
  async startUI(options = {}) {
    if (!this.initialized) await this.initialize();
    return await this.uiManager.start(options);
  }

  /**
   * Run the orchestration engine
   */
  async orchestrate(task, options = {}) {
    if (!this.initialized) await this.initialize();
    return await this.orchestrationEngine.execute(task, options);
  }
}

// Export convenience functions
export const agentInstaller = {
  /**
   * Install all agents to Claude Code
   */
  async installAll(targetPath = null) {
    const stack = new ClaudeCodeDevStack();
    return await stack.installAgents(targetPath);
  },

  /**
   * Install specific agent
   */
  async installAgent(agentName, targetPath = null) {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.agentManager.installSingle(agentName, targetPath);
  },

  /**
   * List available agents
   */
  async listAgents() {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return stack.agentManager.listAvailable();
  }
};

export const hookInstaller = {
  /**
   * Install all hooks to Claude Code
   */
  async installAll(targetPath = null) {
    const stack = new ClaudeCodeDevStack();
    return await stack.installHooks(targetPath);
  },

  /**
   * Install specific hook
   */
  async installHook(hookName, targetPath = null) {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.hookManager.installSingle(hookName, targetPath);
  },

  /**
   * List available hooks
   */
  async listHooks() {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return stack.hookManager.listAvailable();
  }
};

export const audioSetup = {
  /**
   * Setup complete audio system
   */
  async setupAll(targetPath = null) {
    const stack = new ClaudeCodeDevStack();
    return await stack.setupAudio(targetPath);
  },

  /**
   * Test audio system
   */
  async test() {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.audioManager.test();
  }
};

export const configHelpers = {
  /**
   * Generate Claude Code configuration
   */
  async generateConfig(options = {}) {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.configManager.generate(options);
  },

  /**
   * Validate existing configuration
   */
  async validateConfig(configPath = null) {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.configManager.validate(configPath);
  },

  /**
   * Update configuration
   */
  async updateConfig(updates, configPath = null) {
    const stack = new ClaudeCodeDevStack();
    await stack.initialize();
    return await stack.configManager.update(updates, configPath);
  }
};

// Default export
export default ClaudeCodeDevStack;

// Version info
export const version = '3.0.0';
export const name = '@claude-code/dev-stack';

// Package metadata
export const metadata = {
  name: '@claude-code/dev-stack',
  version: '3.0.0',
  description: 'AI-powered development environment with 28 specialized agents',
  agents: 28,
  hooks: 37,
  audioFiles: 90,
  features: [
    'agent-orchestration',
    'smart-routing', 
    'audio-feedback',
    'unified-pwa',
    'performance-monitoring',
    'security-scanning',
    'auto-documentation',
    'quality-gates'
  ]
};