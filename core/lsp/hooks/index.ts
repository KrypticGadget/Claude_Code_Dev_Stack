/**
 * LSP Hooks Integration - V3.0 Main Export
 * Central entry point for LSP-hooks bidirectional integration
 */

// Core integration components
export { lspHookAdapter } from './adapter.js';
export { lspEventTriggers } from './triggers.js';
export { lspHookHandlers } from './handlers.js';
export { lspHooksConfig } from './config.js';

// Type definitions
export type {
  LSPHooksConfig,
  TriggerRuleConfig
} from './config.js';

// Main integration class
import { EventEmitter } from 'events';
import { lspHookAdapter } from './adapter.js';
import { lspEventTriggers } from './triggers.js';
import { lspHookHandlers } from './handlers.js';
import { lspHooksConfig } from './config.js';
import { log } from '../logger.js';

export class LSPHooksIntegration extends EventEmitter {
  private initialized = false;

  constructor() {
    super();
    this.setupIntegration();
  }

  private setupIntegration(): void {
    // Connect adapter events to handlers
    lspHookAdapter.on('hook_response', (response) => {
      lspHookHandlers.processHookResponse({
        hook_name: response.hook,
        event: response.event,
        response_type: 'data',
        data: response.response,
        timestamp: new Date().toISOString(),
        success: true
      });
    });

    // Connect handler actions back to triggers
    lspHookHandlers.on('refresh_diagnostics_requested', async (data) => {
      this.emit('diagnostics_refresh_requested', data);
    });

    lspHookHandlers.on('config_updated', (data) => {
      this.emit('configuration_changed', data);
    });

    lspHookHandlers.on('user_notification', (notification) => {
      this.emit('user_notification', notification);
    });

    // Forward significant events
    lspEventTriggers.on('rule_executed', (data) => {
      this.emit('trigger_rule_executed', data);
    });
  }

  /**
   * Initialize the complete LSP-hooks integration system
   */
  public async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      log('Initializing LSP-hooks integration system...');

      // Load configuration
      const config = lspHooksConfig.getConfig();
      if (!config.enabled) {
        log('LSP-hooks integration disabled in configuration');
        return;
      }

      // Initialize components in order
      await this.initializeAdapter();
      await this.initializeTriggers();
      await this.initializeHandlers();

      this.initialized = true;
      log('LSP-hooks integration system initialized successfully');

      // Emit initialization complete event
      this.emit('initialized', {
        config,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      log(`Failed to initialize LSP-hooks integration: ${error}`);
      this.emit('initialization_failed', error);
      throw error;
    }
  }

  private async initializeAdapter(): Promise<void> {
    // Adapter is already initialized via import, just configure it
    const adapterConfig = lspHooksConfig.getAdapterConfig();
    await lspHookAdapter.updateConfiguration(adapterConfig);
  }

  private async initializeTriggers(): Promise<void> {
    // Configure triggers with rules from config
    const triggersConfig = lspHooksConfig.getTriggersConfig();
    
    if (!triggersConfig.enabled) {
      lspEventTriggers.disable();
      return;
    }

    // Add configured rules
    for (const rule of triggersConfig.rules) {
      if (rule.enabled) {
        try {
          // Convert string condition to function
          const conditionFn = new Function('data', `return ${rule.condition}`);
          
          lspEventTriggers.addRule(rule.name, {
            event: rule.event,
            condition: conditionFn,
            throttle_ms: rule.throttle_ms,
            priority: rule.priority,
            hooks: rule.hooks
          });
        } catch (error) {
          log(`Failed to add trigger rule ${rule.name}: ${error}`);
        }
      }
    }
  }

  private async initializeHandlers(): Promise<void> {
    // Configure handlers
    const handlersConfig = lspHooksConfig.getHandlersConfig();
    await lspHookHandlers.updateConfiguration(handlersConfig);

    if (!handlersConfig.enabled) {
      lspHookHandlers.disable();
    }
  }

  /**
   * Trigger an LSP event through the integration system
   */
  public async triggerEvent(event: string, data: any): Promise<void> {
    if (!this.initialized) {
      await this.initialize();
    }

    await lspHookAdapter.triggerLSPEvent(event, data);
  }

  /**
   * Get integration status
   */
  public getStatus(): {
    initialized: boolean;
    config: any;
    adapter_status: any;
    triggers_enabled: boolean;
    handlers_enabled: boolean;
  } {
    return {
      initialized: this.initialized,
      config: lspHooksConfig.getConfig(),
      adapter_status: lspHookAdapter.getConfiguration(),
      triggers_enabled: lspEventTriggers.isEnabled(),
      handlers_enabled: lspHookHandlers.getConfiguration().enabled
    };
  }

  /**
   * Update configuration at runtime
   */
  public async updateConfiguration(updates: any): Promise<void> {
    await lspHooksConfig.updateConfig(updates);
    
    // Reinitialize components with new configuration
    if (this.initialized) {
      await this.initializeAdapter();
      await this.initializeTriggers();
      await this.initializeHandlers();
    }
  }

  /**
   * Enable/disable the entire integration
   */
  public async setEnabled(enabled: boolean): Promise<void> {
    await lspHooksConfig.setEnabled(enabled);
    
    if (enabled && !this.initialized) {
      await this.initialize();
    } else if (!enabled) {
      await this.shutdown();
    }
  }

  /**
   * Shutdown the integration system
   */
  public async shutdown(): Promise<void> {
    if (!this.initialized) {
      return;
    }

    log('Shutting down LSP-hooks integration system...');

    try {
      await lspHookAdapter.shutdown();
      lspEventTriggers.shutdown();
      lspHookHandlers.shutdown();

      this.initialized = false;
      this.removeAllListeners();

      log('LSP-hooks integration system shutdown complete');
    } catch (error) {
      log(`Error during LSP-hooks integration shutdown: ${error}`);
    }
  }

  /**
   * Diagnostic methods for troubleshooting
   */
  public getDiagnosticInfo(): any {
    return {
      status: this.getStatus(),
      adapter_metrics: {
        config: lspHookAdapter.getConfiguration()
      },
      trigger_metrics: {
        enabled: lspEventTriggers.isEnabled(),
        rules: Array.from(lspEventTriggers.getRules().keys()),
        metrics: Object.fromEntries(lspEventTriggers.getMetrics())
      },
      handler_metrics: {
        config: lspHookHandlers.getConfiguration(),
        queue_status: lspHookHandlers.getQueueStatus(),
        recent_responses: lspHookHandlers.getResponseHistory(10)
      },
      configuration: lspHooksConfig.getConfig()
    };
  }

  /**
   * Test the integration with a sample event
   */
  public async testIntegration(): Promise<{ success: boolean; details: any }> {
    try {
      const testEvent = 'integration_test';
      const testData = {
        test: true,
        timestamp: new Date().toISOString(),
        source: 'integration_test'
      };

      await this.triggerEvent(testEvent, testData);
      
      return {
        success: true,
        details: {
          message: 'Integration test completed successfully',
          test_event: testEvent,
          test_data: testData
        }
      };
    } catch (error) {
      return {
        success: false,
        details: {
          message: 'Integration test failed',
          error: error instanceof Error ? error.message : String(error)
        }
      };
    }
  }
}

// Export singleton instance
export const lspHooksIntegration = new LSPHooksIntegration();