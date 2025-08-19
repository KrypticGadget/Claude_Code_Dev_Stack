/**
 * LSP-Hooks Integration Configuration - V3.0 
 * Centralized configuration management for LSP-hooks integration
 */

import { writeFile, readFile, access, mkdir } from 'fs/promises';
import path from 'path';
import { log } from '../logger.js';

export interface LSPHooksConfig {
  enabled: boolean;
  
  // Adapter configuration
  adapter: {
    debounce_ms: number;
    max_diagnostics_per_event: number;
    python_path: string;
    hooks_directory: string;
    audio_notifications: boolean;
    hook_timeout_ms: number;
  };
  
  // Trigger configuration
  triggers: {
    enabled: boolean;
    rules: TriggerRuleConfig[];
    performance_monitoring: boolean;
    error_reporting: boolean;
  };
  
  // Handler configuration
  handlers: {
    enabled: boolean;
    auto_apply_actions: boolean;
    max_queue_size: number;
    action_timeout_ms: number;
    audio_feedback: boolean;
  };
  
  // Hook-specific settings
  hooks: {
    [hookName: string]: {
      enabled: boolean;
      priority: number;
      events: string[];
      config?: any;
    };
  };
  
  // Integration settings
  integration: {
    status_line_updates: boolean;
    smart_orchestrator_integration: boolean;
    quality_gate_integration: boolean;
    audio_system_integration: boolean;
    performance_monitoring: boolean;
  };
  
  // Advanced settings
  advanced: {
    debug_mode: boolean;
    log_all_events: boolean;
    hook_response_logging: boolean;
    performance_metrics: boolean;
    experimental_features: boolean;
  };
}

export interface TriggerRuleConfig {
  name: string;
  event: string;
  condition: string; // JavaScript expression as string
  throttle_ms?: number;
  priority: number;
  hooks: string[];
  enabled: boolean;
}

export class LSPHooksConfigManager {
  private config: LSPHooksConfig;
  private readonly configDir: string;
  private readonly configFile: string;
  private readonly defaultConfigFile: string;

  constructor() {
    this.configDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.claude');
    this.configFile = path.join(this.configDir, 'lsp_hooks_config.json');
    this.defaultConfigFile = path.join(this.configDir, 'lsp_hooks_defaults.json');
    
    this.config = this.getDefaultConfig();
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      await mkdir(this.configDir, { recursive: true });
      await this.loadConfiguration();
      await this.saveDefaultConfiguration();
    } catch (error) {
      log(`Failed to initialize LSP hooks configuration: ${error}`);
    }
  }

  private getDefaultConfig(): LSPHooksConfig {
    return {
      enabled: true,
      
      adapter: {
        debounce_ms: 300,
        max_diagnostics_per_event: 50,
        python_path: 'python',
        hooks_directory: path.resolve(process.cwd(), 'core/hooks/hooks'),
        audio_notifications: true,
        hook_timeout_ms: 5000
      },
      
      triggers: {
        enabled: true,
        performance_monitoring: true,
        error_reporting: true,
        rules: [
          {
            name: 'critical_errors',
            event: 'diagnostics_received',
            condition: 'data.error_count > 0',
            throttle_ms: 1000,
            priority: 1,
            hooks: ['audio_player_v3', 'status_line_manager', 'quality_gate_hook'],
            enabled: true
          },
          {
            name: 'many_warnings',
            event: 'diagnostics_received',
            condition: 'data.warning_count > 5',
            throttle_ms: 2000,
            priority: 2,
            hooks: ['status_line_manager', 'quality_gate_hook'],
            enabled: true
          },
          {
            name: 'clean_code',
            event: 'diagnostics_received',
            condition: 'data.error_count === 0 && data.warning_count === 0',
            throttle_ms: 5000,
            priority: 3,
            hooks: ['audio_player_v3', 'status_line_manager'],
            enabled: true
          },
          {
            name: 'server_startup',
            event: 'server_started',
            condition: 'true',
            priority: 1,
            hooks: ['audio_player_v3', 'status_line_manager', 'smart_orchestrator'],
            enabled: true
          },
          {
            name: 'quality_improvement_needed',
            event: 'diagnostics_received',
            condition: '(data.error_count + data.warning_count) > 10',
            throttle_ms: 5000,
            priority: 2,
            hooks: ['quality_gate_hook', 'auto_formatter', 'smart_orchestrator'],
            enabled: true
          }
        ]
      },
      
      handlers: {
        enabled: true,
        auto_apply_actions: true,
        max_queue_size: 100,
        action_timeout_ms: 5000,
        audio_feedback: true
      },
      
      hooks: {
        'audio_player_v3': {
          enabled: true,
          priority: 1,
          events: ['diagnostics_received', 'server_started', 'error_occurred'],
          config: {
            sounds: {
              error: 'error.wav',
              warning: 'warning.wav',
              success: 'success.wav',
              server_start: 'server_start.wav'
            }
          }
        },
        'status_line_manager': {
          enabled: true,
          priority: 1,
          events: ['*'], // Listen to all events
          config: {
            update_interval_ms: 100,
            display_lsp_status: true
          }
        },
        'smart_orchestrator': {
          enabled: true,
          priority: 2,
          events: ['server_started', 'error_occurred', 'quality_improvement_needed'],
          config: {
            auto_suggest_agents: true,
            error_threshold: 5
          }
        },
        'quality_gate_hook': {
          enabled: true,
          priority: 2,
          events: ['diagnostics_received'],
          config: {
            error_threshold: 0,
            warning_threshold: 10,
            auto_fix_suggestions: true
          }
        },
        'auto_formatter': {
          enabled: false, // Disabled by default
          priority: 3,
          events: ['quality_improvement_needed'],
          config: {
            languages: ['python', 'javascript', 'typescript'],
            auto_format: false
          }
        },
        'performance_monitor': {
          enabled: true,
          priority: 3,
          events: ['analysis_performance'],
          config: {
            slow_threshold_ms: 5000,
            track_all_operations: true
          }
        }
      },
      
      integration: {
        status_line_updates: true,
        smart_orchestrator_integration: true,
        quality_gate_integration: true,
        audio_system_integration: true,
        performance_monitoring: true
      },
      
      advanced: {
        debug_mode: false,
        log_all_events: false,
        hook_response_logging: true,
        performance_metrics: true,
        experimental_features: false
      }
    };
  }

  private async loadConfiguration(): Promise<void> {
    try {
      await access(this.configFile);
      const configData = await readFile(this.configFile, 'utf-8');
      const loadedConfig = JSON.parse(configData);
      
      // Merge with defaults to ensure all properties exist
      this.config = this.mergeConfigs(this.getDefaultConfig(), loadedConfig);
      log(`LSP hooks configuration loaded from ${this.configFile}`);
    } catch (error) {
      log(`Using default LSP hooks configuration (file not found or invalid)`);
      await this.saveConfiguration();
    }
  }

  private async saveConfiguration(): Promise<void> {
    try {
      await writeFile(this.configFile, JSON.stringify(this.config, null, 2));
      log(`LSP hooks configuration saved to ${this.configFile}`);
    } catch (error) {
      log(`Failed to save LSP hooks configuration: ${error}`);
    }
  }

  private async saveDefaultConfiguration(): Promise<void> {
    try {
      const defaultConfig = this.getDefaultConfig();
      await writeFile(this.defaultConfigFile, JSON.stringify(defaultConfig, null, 2));
    } catch (error) {
      log(`Failed to save default configuration: ${error}`);
    }
  }

  private mergeConfigs(defaultConfig: LSPHooksConfig, userConfig: any): LSPHooksConfig {
    const merged = { ...defaultConfig };
    
    // Deep merge sections
    if (userConfig.adapter) {
      merged.adapter = { ...defaultConfig.adapter, ...userConfig.adapter };
    }
    
    if (userConfig.triggers) {
      merged.triggers = { ...defaultConfig.triggers, ...userConfig.triggers };
      if (userConfig.triggers.rules) {
        merged.triggers.rules = userConfig.triggers.rules;
      }
    }
    
    if (userConfig.handlers) {
      merged.handlers = { ...defaultConfig.handlers, ...userConfig.handlers };
    }
    
    if (userConfig.hooks) {
      merged.hooks = { ...defaultConfig.hooks };
      for (const [hookName, hookConfig] of Object.entries(userConfig.hooks)) {
        if (defaultConfig.hooks[hookName]) {
          merged.hooks[hookName] = { ...defaultConfig.hooks[hookName], ...hookConfig as any };
        } else {
          merged.hooks[hookName] = hookConfig as any;
        }
      }
    }
    
    if (userConfig.integration) {
      merged.integration = { ...defaultConfig.integration, ...userConfig.integration };
    }
    
    if (userConfig.advanced) {
      merged.advanced = { ...defaultConfig.advanced, ...userConfig.advanced };
    }
    
    if (typeof userConfig.enabled === 'boolean') {
      merged.enabled = userConfig.enabled;
    }
    
    return merged;
  }

  /**
   * Public API methods
   */
  public getConfig(): LSPHooksConfig {
    return { ...this.config };
  }

  public async updateConfig(updates: Partial<LSPHooksConfig>): Promise<void> {
    this.config = this.mergeConfigs(this.config, updates);
    await this.saveConfiguration();
    log('LSP hooks configuration updated');
  }

  public async resetToDefaults(): Promise<void> {
    this.config = this.getDefaultConfig();
    await this.saveConfiguration();
    log('LSP hooks configuration reset to defaults');
  }

  // Specific getters for different components
  public getAdapterConfig() {
    return { ...this.config.adapter };
  }

  public getTriggersConfig() {
    return { ...this.config.triggers };
  }

  public getHandlersConfig() {
    return { ...this.config.handlers };
  }

  public getHookConfig(hookName: string) {
    return this.config.hooks[hookName] ? { ...this.config.hooks[hookName] } : null;
  }

  public getIntegrationConfig() {
    return { ...this.config.integration };
  }

  public getAdvancedConfig() {
    return { ...this.config.advanced };
  }

  // Specific setters
  public async setEnabled(enabled: boolean): Promise<void> {
    await this.updateConfig({ enabled });
  }

  public async setDebugMode(enabled: boolean): Promise<void> {
    await this.updateConfig({
      advanced: { ...this.config.advanced, debug_mode: enabled }
    });
  }

  public async updateHookConfig(hookName: string, config: Partial<typeof this.config.hooks[string]>): Promise<void> {
    const currentHookConfig = this.config.hooks[hookName] || {
      enabled: true,
      priority: 5,
      events: [],
      config: {}
    };

    const updatedHooks = {
      ...this.config.hooks,
      [hookName]: { ...currentHookConfig, ...config }
    };

    await this.updateConfig({ hooks: updatedHooks });
  }

  public async addTriggerRule(rule: TriggerRuleConfig): Promise<void> {
    const currentRules = [...this.config.triggers.rules];
    const existingIndex = currentRules.findIndex(r => r.name === rule.name);
    
    if (existingIndex >= 0) {
      currentRules[existingIndex] = rule;
    } else {
      currentRules.push(rule);
    }

    await this.updateConfig({
      triggers: { ...this.config.triggers, rules: currentRules }
    });
  }

  public async removeTriggerRule(ruleName: string): Promise<boolean> {
    const currentRules = this.config.triggers.rules.filter(r => r.name !== ruleName);
    
    if (currentRules.length !== this.config.triggers.rules.length) {
      await this.updateConfig({
        triggers: { ...this.config.triggers, rules: currentRules }
      });
      return true;
    }
    
    return false;
  }

  /**
   * Validation
   */
  public validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate adapter config
    if (this.config.adapter.debounce_ms < 0 || this.config.adapter.debounce_ms > 10000) {
      errors.push('Adapter debounce_ms must be between 0 and 10000');
    }

    if (this.config.adapter.max_diagnostics_per_event < 1) {
      errors.push('Adapter max_diagnostics_per_event must be at least 1');
    }

    // Validate trigger rules
    for (const rule of this.config.triggers.rules) {
      if (!rule.name || !rule.event || !rule.condition) {
        errors.push(`Trigger rule missing required fields: ${rule.name}`);
      }
      
      if (rule.priority < 1 || rule.priority > 10) {
        errors.push(`Trigger rule ${rule.name} priority must be between 1 and 10`);
      }
    }

    // Validate handler config
    if (this.config.handlers.max_queue_size < 1) {
      errors.push('Handlers max_queue_size must be at least 1');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Export/Import
   */
  public async exportConfig(filePath: string): Promise<void> {
    await writeFile(filePath, JSON.stringify(this.config, null, 2));
    log(`Configuration exported to ${filePath}`);
  }

  public async importConfig(filePath: string): Promise<void> {
    const configData = await readFile(filePath, 'utf-8');
    const importedConfig = JSON.parse(configData);
    
    this.config = this.mergeConfigs(this.getDefaultConfig(), importedConfig);
    await this.saveConfiguration();
    log(`Configuration imported from ${filePath}`);
  }

  /**
   * Get file paths
   */
  public getConfigFilePath(): string {
    return this.configFile;
  }

  public getDefaultConfigFilePath(): string {
    return this.defaultConfigFile;
  }
}

// Export singleton instance
export const lspHooksConfig = new LSPHooksConfigManager();