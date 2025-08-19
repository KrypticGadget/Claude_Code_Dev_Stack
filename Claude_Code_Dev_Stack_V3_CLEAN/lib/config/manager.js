/**
 * Configuration Manager - Handles Claude Code configuration generation and management
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import yaml from 'yaml';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class ConfigManager {
  constructor(options = {}) {
    this.options = options;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    
    console.log(chalk.blue('⚙️  Initializing Configuration Manager...'));
    
    this.initialized = true;
    console.log(chalk.green('✅ Configuration Manager initialized'));
  }

  async generate(options = {}) {
    console.log(chalk.blue('🚀 Generating Claude Code configuration...'));
    
    const configPath = options.path || await this.detectClaudeConfigPath();
    
    // Generate main Claude Code configuration
    await this.generateMainConfig(configPath, options);
    
    // Generate agent configuration
    await this.generateAgentConfig(configPath, options);
    
    // Generate hooks configuration
    await this.generateHooksConfig(configPath, options);
    
    // Generate audio configuration (if not already exists)
    await this.generateAudioConfigIfNeeded(configPath, options);
    
    console.log(chalk.green('✅ Configuration generation complete'));
    
    return {
      success: true,
      configPath,
      files: [
        'claude-code.config.json',
        'agents.config.json', 
        'hooks.config.json',
        'audio-config.json'
      ]
    };
  }

  async generateMainConfig(configPath, options = {}) {
    const mainConfig = {
      name: "Claude Code Dev Stack V3",
      version: "3.0.0",
      description: "AI-powered development environment with 28 specialized agents",
      
      features: {
        agents: {
          enabled: true,
          count: 28,
          autoLoad: true,
          categories: [
            "Architecture & Design",
            "Development & Engineering", 
            "DevOps & Infrastructure",
            "Quality & Management",
            "Leadership & Strategy",
            "User Experience & Design"
          ]
        },
        
        hooks: {
          enabled: true,
          count: 37,
          autoLoad: true,
          categories: [
            "Core Orchestration",
            "Audio & Feedback",
            "Communication & Routing",
            "Quality & Security",
            "Performance & Monitoring",
            "Documentation & Automation",
            "Development Tools"
          ]
        },
        
        audio: {
          enabled: true,
          fileCount: 90,
          volume: 0.7,
          categories: [
            "System Events",
            "Agent Events", 
            "File Operations",
            "Git Operations",
            "Build & Deploy",
            "Development",
            "Quality & Security",
            "Communication",
            "Warnings & Errors"
          ]
        },
        
        ui: {
          enabled: true,
          type: "react-pwa",
          port: 3000,
          features: [
            "agent-dashboard",
            "hook-management",
            "audio-controls",
            "performance-monitoring",
            "configuration-editor"
          ]
        }
      },
      
      orchestration: {
        enabled: true,
        engine: "smart-orchestrator-v3",
        parallelExecution: true,
        contextAware: true,
        autoHandoff: true,
        performanceTracking: true
      },
      
      development: {
        mode: options.devMode || false,
        debugging: options.devMode || false,
        verbose: options.devMode || false,
        hotReload: options.devMode || false
      },
      
      paths: {
        agents: path.join(configPath, 'agents'),
        hooks: path.join(configPath, 'hooks'),
        audio: path.join(configPath, 'audio'),
        ui: path.join(configPath, 'ui'),
        logs: path.join(configPath, 'logs'),
        cache: path.join(configPath, 'cache')
      },
      
      performance: {
        tokenTracking: true,
        resourceMonitoring: true,
        metricsCollection: true,
        alertThresholds: {
          tokenUsage: 80,
          memory: 85,
          cpu: 90
        }
      },
      
      security: {
        scanning: true,
        validation: true,
        safeMode: false,
        permissions: {
          fileAccess: "restricted",
          networkAccess: "allowed",
          systemCommands: "validated"
        }
      }
    };

    const configFilePath = path.join(configPath, 'claude-code.config.json');
    await fs.writeJSON(configFilePath, mainConfig, { spaces: 2 });
    console.log(chalk.green(`📄 Main configuration saved: ${configFilePath}`));
  }

  async generateAgentConfig(configPath, options = {}) {
    const agentConfig = {
      version: "3.0.0",
      enabled: true,
      autoLoad: true,
      
      routing: {
        smartRouting: true,
        contextAware: true,
        hierarchical: true,
        delegation: true
      },
      
      agents: {
        "backend-services": {
          tier: 3,
          category: "Architecture & Design",
          autoInvoke: ["service-implementation", "api-development"],
          delegates: ["database-architecture", "api-integration-specialist"],
          coordinates: ["frontend-architecture", "security-architecture"]
        },
        
        "frontend-architecture": {
          tier: 3,
          category: "Architecture & Design", 
          autoInvoke: ["ui-development", "component-design"],
          delegates: ["ui-ux-design", "production-frontend"],
          coordinates: ["backend-services", "mobile-development"]
        },
        
        "database-architecture": {
          tier: 3,
          category: "Architecture & Design",
          autoInvoke: ["schema-design", "optimization"],
          delegates: [],
          coordinates: ["backend-services", "performance-optimization"]
        },
        
        "master-orchestrator": {
          tier: 1,
          category: "Quality & Management",
          autoInvoke: ["workflow-coordination", "agent-management"],
          delegates: ["project-manager", "quality-assurance"],
          coordinates: ["all-agents"]
        }
      },
      
      delegation: {
        automatic: true,
        patterns: {
          "service-implementation": "backend-services",
          "database-design": "database-architecture",
          "ui-design": "ui-ux-design",
          "security-analysis": "security-architecture",
          "performance-optimization": "performance-optimization"
        }
      },
      
      handoff: {
        enabled: true,
        contextPreservation: true,
        documentationGeneration: true,
        metrics: true
      }
    };

    const configFilePath = path.join(configPath, 'agents.config.json');
    await fs.writeJSON(configFilePath, agentConfig, { spaces: 2 });
    console.log(chalk.green(`📄 Agent configuration saved: ${configFilePath}`));
  }

  async generateHooksConfig(configPath, options = {}) {
    const hooksConfig = {
      version: "3.0.0",
      enabled: true,
      autoLoad: true,
      
      execution: {
        parallel: true,
        timeout: 30000,
        retries: 3,
        gracefulErrors: true
      },
      
      categories: {
        "Core Orchestration": {
          priority: 1,
          hooks: [
            "master_orchestrator",
            "smart_orchestrator", 
            "v3_orchestrator",
            "orchestration_enhancer",
            "agent_enhancer_v3"
          ]
        },
        
        "Audio & Feedback": {
          priority: 3,
          hooks: [
            "audio_controller",
            "audio_notifier",
            "audio_player",
            "audio_player_v3"
          ]
        },
        
        "Quality & Security": {
          priority: 2,
          hooks: [
            "quality_gate_hook",
            "security_scanner",
            "code_linter",
            "git_quality_hooks",
            "v3_validator"
          ]
        },
        
        "Performance & Monitoring": {
          priority: 2,
          hooks: [
            "performance_monitor",
            "resource_monitor",
            "status_line_manager",
            "model_tracker"
          ]
        }
      },
      
      triggers: {
        "agent-activation": ["agent_enhancer_v3", "audio_controller"],
        "code-change": ["code_linter", "auto_formatter", "security_scanner"],
        "git-operation": ["git_quality_hooks", "auto_documentation"],
        "performance-threshold": ["performance_monitor", "resource_monitor"],
        "error-detected": ["notification_sender", "audio_notifier"]
      },
      
      monitoring: {
        execution: true,
        performance: true,
        errors: true,
        metrics: true
      }
    };

    const configFilePath = path.join(configPath, 'hooks.config.json');
    await fs.writeJSON(configFilePath, hooksConfig, { spaces: 2 });
    console.log(chalk.green(`📄 Hooks configuration saved: ${configFilePath}`));
  }

  async generateAudioConfigIfNeeded(configPath, options = {}) {
    const audioConfigPath = path.join(configPath, 'audio', 'audio-config.json');
    
    if (await fs.pathExists(audioConfigPath)) {
      console.log(chalk.yellow('⚠️  Audio configuration already exists, skipping...'));
      return;
    }

    // Basic audio configuration if audio manager hasn't created one
    const basicAudioConfig = {
      version: "3.0.0",
      enabled: true,
      volume: 0.7,
      audioPath: path.join(configPath, 'audio'),
      note: "This is a basic configuration. Run audio setup for full configuration."
    };

    await fs.ensureDir(path.dirname(audioConfigPath));
    await fs.writeJSON(audioConfigPath, basicAudioConfig, { spaces: 2 });
    console.log(chalk.green(`📄 Basic audio configuration saved: ${audioConfigPath}`));
  }

  async validate(configPath = null) {
    console.log(chalk.blue('🔍 Validating configuration...'));
    
    const targetPath = configPath || await this.detectClaudeConfigPath();
    const results = {
      valid: true,
      errors: [],
      warnings: [],
      files: {}
    };

    // Check main configuration
    const mainConfigPath = path.join(targetPath, 'claude-code.config.json');
    results.files.main = await this.validateConfigFile(mainConfigPath, 'main');

    // Check agent configuration  
    const agentConfigPath = path.join(targetPath, 'agents.config.json');
    results.files.agents = await this.validateConfigFile(agentConfigPath, 'agents');

    // Check hooks configuration
    const hooksConfigPath = path.join(targetPath, 'hooks.config.json');
    results.files.hooks = await this.validateConfigFile(hooksConfigPath, 'hooks');

    // Check audio configuration
    const audioConfigPath = path.join(targetPath, 'audio', 'audio-config.json');
    results.files.audio = await this.validateConfigFile(audioConfigPath, 'audio');

    // Summarize results
    const invalidFiles = Object.values(results.files).filter(f => !f.valid);
    results.valid = invalidFiles.length === 0;

    if (results.valid) {
      console.log(chalk.green('✅ Configuration validation passed'));
    } else {
      console.log(chalk.red(`❌ Configuration validation failed: ${invalidFiles.length} invalid files`));
      invalidFiles.forEach(file => {
        console.log(chalk.red(`  • ${file.path}: ${file.errors.join(', ')}`));
      });
    }

    return results;
  }

  async validateConfigFile(filePath, type) {
    const result = {
      path: filePath,
      valid: true,
      errors: [],
      warnings: []
    };

    try {
      if (!(await fs.pathExists(filePath))) {
        result.valid = false;
        result.errors.push('File does not exist');
        return result;
      }

      const config = await fs.readJSON(filePath);
      
      // Basic validation
      if (!config.version) {
        result.warnings.push('Version not specified');
      }

      // Type-specific validation
      switch (type) {
        case 'main':
          if (!config.features) result.errors.push('Missing features configuration');
          if (!config.paths) result.errors.push('Missing paths configuration');
          break;
          
        case 'agents':
          if (!config.agents) result.errors.push('Missing agents configuration');
          if (!config.routing) result.errors.push('Missing routing configuration');
          break;
          
        case 'hooks':
          if (!config.categories) result.errors.push('Missing categories configuration');
          if (!config.triggers) result.errors.push('Missing triggers configuration');
          break;
          
        case 'audio':
          if (!config.audioPath) result.errors.push('Missing audioPath configuration');
          break;
      }

      result.valid = result.errors.length === 0;

    } catch (error) {
      result.valid = false;
      result.errors.push(`JSON parse error: ${error.message}`);
    }

    return result;
  }

  async update(updates, configPath = null) {
    console.log(chalk.blue('🔄 Updating configuration...'));
    
    const targetPath = configPath || await this.detectClaudeConfigPath();
    const mainConfigPath = path.join(targetPath, 'claude-code.config.json');

    if (!(await fs.pathExists(mainConfigPath))) {
      throw new Error('Configuration not found. Run setup first.');
    }

    const currentConfig = await fs.readJSON(mainConfigPath);
    const updatedConfig = { ...currentConfig, ...updates };

    await fs.writeJSON(mainConfigPath, updatedConfig, { spaces: 2 });
    console.log(chalk.green('✅ Configuration updated successfully'));

    return updatedConfig;
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
}