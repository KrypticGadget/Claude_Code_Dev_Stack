/**
 * LSP Hook Handlers - V3.0 Hook Response Processing
 * Processes responses from Python hooks and applies them to LSP operations
 */

import { EventEmitter } from 'events';
import { writeFile, readFile, access } from 'fs/promises';
import path from 'path';
import { log } from '../logger.js';
import { lspManager } from '../lsp/manager.js';

interface HookResponse {
  hook_name: string;
  event: string;
  response_type: 'action' | 'data' | 'notification' | 'config';
  data: any;
  timestamp: string;
  success: boolean;
}

interface LSPAction {
  type: 'refresh_diagnostics' | 'configure_server' | 'notify_user' | 'update_config' | 'trigger_analysis';
  target?: string;
  parameters?: any;
  priority: number;
}

interface HandlerConfig {
  enabled: boolean;
  auto_apply_actions: boolean;
  max_queue_size: number;
  action_timeout_ms: number;
  audio_feedback: boolean;
}

export class LSPHookHandlers extends EventEmitter {
  private config: HandlerConfig;
  private actionQueue: LSPAction[] = [];
  private responseHistory: HookResponse[] = [];
  private readonly homeDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.claude');
  private processing = false;

  constructor() {
    super();
    this.config = {
      enabled: true,
      auto_apply_actions: true,
      max_queue_size: 100,
      action_timeout_ms: 5000,
      audio_feedback: true
    };
    
    this.loadConfiguration();
    this.setupHandlers();
    this.startActionProcessor();
  }

  private async loadConfiguration(): Promise<void> {
    try {
      const configPath = path.join(this.homeDir, 'lsp_handlers_config.json');
      await access(configPath);
      const configData = await readFile(configPath, 'utf-8');
      const userConfig = JSON.parse(configData);
      this.config = { ...this.config, ...userConfig };
      log(`LSP handlers configuration loaded`);
    } catch (error) {
      log(`Using default LSP handlers configuration`);
      await this.saveConfiguration();
    }
  }

  private async saveConfiguration(): Promise<void> {
    try {
      const configPath = path.join(this.homeDir, 'lsp_handlers_config.json');
      await writeFile(configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      log(`Failed to save LSP handlers configuration: ${error}`);
    }
  }

  private setupHandlers(): void {
    // Register for hook responses from the adapter
    this.on('hook_response_received', this.processHookResponse.bind(this));
  }

  private startActionProcessor(): void {
    // Process action queue every 100ms
    setInterval(() => {
      if (!this.processing && this.actionQueue.length > 0) {
        this.processNextAction();
      }
    }, 100);
  }

  /**
   * Main hook response processing
   */
  public async processHookResponse(hookResponse: HookResponse): Promise<void> {
    if (!this.config.enabled) {
      return;
    }

    log(`Processing hook response from ${hookResponse.hook_name} for event ${hookResponse.event}`);

    // Store response in history
    this.addToHistory(hookResponse);

    // Process based on response type
    switch (hookResponse.response_type) {
      case 'action':
        await this.handleActionResponse(hookResponse);
        break;
      case 'data':
        await this.handleDataResponse(hookResponse);
        break;
      case 'notification':
        await this.handleNotificationResponse(hookResponse);
        break;
      case 'config':
        await this.handleConfigResponse(hookResponse);
        break;
      default:
        log(`Unknown response type: ${hookResponse.response_type}`);
    }

    // Emit for external listeners
    this.emit('response_processed', hookResponse);
  }

  private async handleActionResponse(response: HookResponse): Promise<void> {
    const actions = Array.isArray(response.data) ? response.data : [response.data];

    for (const actionData of actions) {
      const action: LSPAction = {
        type: actionData.type,
        target: actionData.target,
        parameters: actionData.parameters || {},
        priority: actionData.priority || 5
      };

      await this.queueAction(action);
    }
  }

  private async handleDataResponse(response: HookResponse): Promise<void> {
    // Data responses typically contain information for other hooks or UI updates
    log(`Data response from ${response.hook_name}: ${JSON.stringify(response.data)}`);

    // Update status files if the response contains status information
    if (response.data.status_update) {
      await this.updateStatusFiles(response.data.status_update);
    }

    // Trigger cascading hook events if specified
    if (response.data.trigger_hooks) {
      for (const hookName of response.data.trigger_hooks) {
        this.emit('trigger_hook', {
          hook: hookName,
          data: response.data,
          source: response.hook_name
        });
      }
    }
  }

  private async handleNotificationResponse(response: HookResponse): Promise<void> {
    const notification = response.data;

    log(`Notification from ${response.hook_name}: ${notification.message}`);

    // Audio feedback if enabled
    if (this.config.audio_feedback && notification.audio) {
      this.emit('play_audio', {
        sound: notification.audio,
        context: response.event
      });
    }

    // Update status line if notification affects status
    if (notification.affects_status) {
      this.emit('update_status', {
        source: response.hook_name,
        message: notification.message,
        type: notification.type || 'info'
      });
    }

    // Show user notification if required
    if (notification.show_user) {
      this.emit('user_notification', {
        title: notification.title || 'LSP Notification',
        message: notification.message,
        type: notification.type || 'info',
        duration: notification.duration || 3000
      });
    }
  }

  private async handleConfigResponse(response: HookResponse): Promise<void> {
    const configUpdate = response.data;

    log(`Config update from ${response.hook_name}: ${JSON.stringify(configUpdate)}`);

    // Apply configuration changes
    if (configUpdate.lsp_config) {
      await this.applyLSPConfigChanges(configUpdate.lsp_config);
    }

    if (configUpdate.handler_config) {
      await this.applyHandlerConfigChanges(configUpdate.handler_config);
    }

    // Restart components if needed
    if (configUpdate.restart_required) {
      this.emit('restart_required', {
        components: configUpdate.restart_components || ['lsp'],
        reason: 'Config update from ' + response.hook_name
      });
    }
  }

  private async queueAction(action: LSPAction): Promise<void> {
    // Prevent queue overflow
    if (this.actionQueue.length >= this.config.max_queue_size) {
      log(`Action queue full, removing oldest action`);
      this.actionQueue.shift();
    }

    // Insert action in priority order
    let insertIndex = this.actionQueue.length;
    for (let i = 0; i < this.actionQueue.length; i++) {
      if (this.actionQueue[i].priority > action.priority) {
        insertIndex = i;
        break;
      }
    }

    this.actionQueue.splice(insertIndex, 0, action);
    log(`Queued LSP action: ${action.type} (priority ${action.priority})`);
  }

  private async processNextAction(): Promise<void> {
    if (this.actionQueue.length === 0) {
      return;
    }

    this.processing = true;
    const action = this.actionQueue.shift()!;

    try {
      log(`Processing LSP action: ${action.type}`);
      await this.executeAction(action);
    } catch (error) {
      log(`Failed to execute action ${action.type}: ${error}`);
    } finally {
      this.processing = false;
    }
  }

  private async executeAction(action: LSPAction): Promise<void> {
    const startTime = Date.now();

    try {
      switch (action.type) {
        case 'refresh_diagnostics':
          await this.executeRefreshDiagnostics(action);
          break;
        case 'configure_server':
          await this.executeConfigureServer(action);
          break;
        case 'notify_user':
          await this.executeNotifyUser(action);
          break;
        case 'update_config':
          await this.executeUpdateConfig(action);
          break;
        case 'trigger_analysis':
          await this.executeTriggerAnalysis(action);
          break;
        default:
          log(`Unknown action type: ${action.type}`);
      }

      const duration = Date.now() - startTime;
      log(`Action ${action.type} completed in ${duration}ms`);

    } catch (error) {
      const duration = Date.now() - startTime;
      log(`Action ${action.type} failed after ${duration}ms: ${error}`);
      
      // Emit failure event
      this.emit('action_failed', {
        action,
        error: error instanceof Error ? error.message : String(error),
        duration
      });
    }
  }

  private async executeRefreshDiagnostics(action: LSPAction): Promise<void> {
    const filePath = action.target;
    if (!filePath) {
      throw new Error('No file path specified for diagnostics refresh');
    }

    log(`Refreshing diagnostics for: ${filePath}`);
    const diagnostics = await lspManager.getDiagnostics(filePath);
    
    this.emit('diagnostics_refreshed', {
      file: filePath,
      diagnostics,
      count: diagnostics.length,
      triggered_by: 'hook_action'
    });
  }

  private async executeConfigureServer(action: LSPAction): Promise<void> {
    const { server_id, configuration } = action.parameters;
    
    log(`Configuring server ${server_id} with new settings`);
    
    // This would need to be implemented in the LSP manager
    // For now, just emit the configuration request
    this.emit('server_configuration_requested', {
      server_id,
      configuration,
      source: 'hook_action'
    });
  }

  private async executeNotifyUser(action: LSPAction): Promise<void> {
    const { message, type, duration } = action.parameters;
    
    this.emit('user_notification', {
      title: 'LSP System',
      message,
      type: type || 'info',
      duration: duration || 3000,
      source: 'hook_action'
    });
  }

  private async executeUpdateConfig(action: LSPAction): Promise<void> {
    const { config_updates } = action.parameters;
    
    if (config_updates.handlers) {
      await this.applyHandlerConfigChanges(config_updates.handlers);
    }
    
    this.emit('config_updated', {
      updates: config_updates,
      source: 'hook_action'
    });
  }

  private async executeTriggerAnalysis(action: LSPAction): Promise<void> {
    const { analysis_type, target_files } = action.parameters;
    
    log(`Triggering ${analysis_type} analysis for ${target_files?.length || 0} files`);
    
    if (target_files && Array.isArray(target_files)) {
      for (const file of target_files) {
        // Trigger appropriate analysis based on type
        switch (analysis_type) {
          case 'diagnostics':
            await lspManager.getDiagnostics(file);
            break;
          case 'hover':
            // This would need more parameters for symbol analysis
            break;
          default:
            log(`Unknown analysis type: ${analysis_type}`);
        }
      }
    }
  }

  private async updateStatusFiles(statusUpdate: any): Promise<void> {
    try {
      const statusFile = path.join(this.homeDir, 'lsp_status.json');
      let currentStatus = {};
      
      try {
        const statusData = await readFile(statusFile, 'utf-8');
        currentStatus = JSON.parse(statusData);
      } catch {
        // File doesn't exist, start with empty object
      }

      const updatedStatus = {
        ...currentStatus,
        ...statusUpdate,
        last_updated: new Date().toISOString()
      };

      await writeFile(statusFile, JSON.stringify(updatedStatus, null, 2));
      log(`Status file updated with data from hook`);
    } catch (error) {
      log(`Failed to update status file: ${error}`);
    }
  }

  private async applyLSPConfigChanges(configChanges: any): Promise<void> {
    // Apply LSP-specific configuration changes
    log(`Applying LSP config changes: ${JSON.stringify(configChanges)}`);
    
    // This would involve updating LSP server configurations
    // For now, just emit the changes for the LSP manager to handle
    this.emit('lsp_config_changed', configChanges);
  }

  private async applyHandlerConfigChanges(configChanges: any): Promise<void> {
    this.config = { ...this.config, ...configChanges };
    await this.saveConfiguration();
    log(`Handler configuration updated`);
  }

  private addToHistory(response: HookResponse): void {
    this.responseHistory.push(response);
    
    // Keep only last 1000 responses
    if (this.responseHistory.length > 1000) {
      this.responseHistory = this.responseHistory.slice(-1000);
    }
  }

  /**
   * Public API methods
   */
  public getConfiguration(): HandlerConfig {
    return { ...this.config };
  }

  public async updateConfiguration(updates: Partial<HandlerConfig>): Promise<void> {
    this.config = { ...this.config, ...updates };
    await this.saveConfiguration();
    log('LSP handlers configuration updated');
  }

  public getQueueStatus(): { length: number; processing: boolean } {
    return {
      length: this.actionQueue.length,
      processing: this.processing
    };
  }

  public getResponseHistory(limit?: number): HookResponse[] {
    if (limit) {
      return this.responseHistory.slice(-limit);
    }
    return [...this.responseHistory];
  }

  public clearActionQueue(): void {
    this.actionQueue.length = 0;
    log('Action queue cleared');
  }

  public enable(): void {
    this.config.enabled = true;
    this.saveConfiguration();
    log('LSP hook handlers enabled');
  }

  public disable(): void {
    this.config.enabled = false;
    this.saveConfiguration();
    log('LSP hook handlers disabled');
  }

  /**
   * Cleanup
   */
  public shutdown(): void {
    this.config.enabled = false;
    this.actionQueue.length = 0;
    this.responseHistory.length = 0;
    this.removeAllListeners();
    log('LSP hook handlers shutdown complete');
  }
}

// Export singleton instance
export const lspHookHandlers = new LSPHookHandlers();