/**
 * LSP Hook Adapter - V3.0 Core Integration
 * Bidirectional communication bridge between LSP daemon and Python hooks system
 */

import { EventEmitter } from 'events';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile, readFile, access } from 'fs/promises';
import { log } from '../logger.js';
import type { Diagnostic, HoverResult } from '../lsp/types.js';

interface HookMessage {
  type: 'lsp_event' | 'hook_response' | 'hook_trigger';
  event: string;
  data: any;
  timestamp: string;
  source: 'lsp' | 'hooks';
}

interface LSPHookConfig {
  enabled: boolean;
  python_path: string;
  hooks_dir: string;
  audio_notifications: boolean;
  debounce_ms: number;
  max_diagnostics_per_event: number;
}

export class LSPHookAdapter extends EventEmitter {
  private config: LSPHookConfig;
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private hookProcesses: Map<string, any> = new Map();
  private readonly homeDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.claude');

  constructor() {
    super();
    this.config = {
      enabled: true,
      python_path: 'python',
      hooks_dir: path.resolve(process.cwd(), 'core/hooks/hooks'),
      audio_notifications: true,
      debounce_ms: 300,
      max_diagnostics_per_event: 50
    };
    
    this.loadConfiguration();
    this.setupEventHandlers();
  }

  private async loadConfiguration(): Promise<void> {
    try {
      const configPath = path.join(this.homeDir, 'lsp_hooks_config.json');
      await access(configPath);
      const configData = await readFile(configPath, 'utf-8');
      const userConfig = JSON.parse(configData);
      this.config = { ...this.config, ...userConfig };
      log(`LSP hooks configuration loaded from ${configPath}`);
    } catch (error) {
      log(`Using default LSP hooks configuration`);
      await this.saveConfiguration();
    }
  }

  private async saveConfiguration(): Promise<void> {
    try {
      const configPath = path.join(this.homeDir, 'lsp_hooks_config.json');
      await writeFile(configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      log(`Failed to save LSP hooks configuration: ${error}`);
    }
  }

  private setupEventHandlers(): void {
    // LSP to Hooks events
    this.on('diagnostics_received', this.handleDiagnosticsEvent.bind(this));
    this.on('hover_received', this.handleHoverEvent.bind(this));
    this.on('server_started', this.handleServerStartedEvent.bind(this));
    this.on('server_stopped', this.handleServerStoppedEvent.bind(this));
    this.on('error_occurred', this.handleErrorEvent.bind(this));

    // Hooks to LSP events (responses)
    this.on('hook_response', this.handleHookResponse.bind(this));
  }

  /**
   * Trigger LSP event to hooks system
   */
  public async triggerLSPEvent(event: string, data: any): Promise<void> {
    if (!this.config.enabled) {
      return;
    }

    const eventKey = `${event}_${JSON.stringify(data).substring(0, 50)}`;
    
    // Debounce rapid events
    if (this.debounceTimers.has(eventKey)) {
      clearTimeout(this.debounceTimers.get(eventKey)!);
    }

    this.debounceTimers.set(eventKey, setTimeout(async () => {
      await this.executeLSPEvent(event, data);
      this.debounceTimers.delete(eventKey);
    }, this.config.debounce_ms));
  }

  private async executeLSPEvent(event: string, data: any): Promise<void> {
    const hookMessage: HookMessage = {
      type: 'lsp_event',
      event,
      data,
      timestamp: new Date().toISOString(),
      source: 'lsp'
    };

    log(`Triggering LSP event: ${event}`);

    // Send to status line manager for real-time context
    await this.triggerHook('status_line_manager', hookMessage);

    // Send to smart orchestrator if significant event
    if (this.isSignificantEvent(event)) {
      await this.triggerHook('smart_orchestrator', hookMessage);
    }

    // Send to audio player for notifications
    if (this.config.audio_notifications) {
      await this.triggerHook('audio_player_v3', hookMessage);
    }

    // Send to quality gate for code events
    if (this.isCodeQualityEvent(event)) {
      await this.triggerHook('quality_gate_hook', hookMessage);
    }

    // Emit for external listeners
    this.emit('lsp_event_triggered', hookMessage);
  }

  private async triggerHook(hookName: string, message: HookMessage): Promise<void> {
    try {
      const hookScript = path.join(this.config.hooks_dir, `${hookName}.py`);
      
      // Check if hook exists
      try {
        await access(hookScript);
      } catch {
        log(`Hook script not found: ${hookScript}`);
        return;
      }

      const process = spawn(this.config.python_path, [hookScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          CLAUDE_LSP_EVENT: message.event,
          CLAUDE_LSP_DATA: JSON.stringify(message.data),
          CLAUDE_TOOL_NAME: 'LSP'
        }
      });

      // Send message data to hook via stdin
      process.stdin.write(JSON.stringify(message));
      process.stdin.end();

      // Collect response
      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          if (stdout.trim()) {
            try {
              const response = JSON.parse(stdout.trim());
              this.emit('hook_response', {
                hook: hookName,
                response,
                event: message.event
              });
            } catch {
              // Non-JSON response is fine
            }
          }
        } else {
          log(`Hook ${hookName} failed with code ${code}: ${stderr}`);
        }
      });

      // Store process reference
      this.hookProcesses.set(`${hookName}_${Date.now()}`, process);

      // Clean up after timeout
      setTimeout(() => {
        if (!process.killed) {
          process.kill();
          log(`Hook ${hookName} timeout, killed process`);
        }
      }, 5000);

    } catch (error) {
      log(`Error triggering hook ${hookName}: ${error}`);
    }
  }

  private handleDiagnosticsEvent(data: { file: string; diagnostics: Diagnostic[] }): void {
    // Limit diagnostics to prevent overwhelming hooks
    const limitedDiagnostics = data.diagnostics.slice(0, this.config.max_diagnostics_per_event);
    
    this.triggerLSPEvent('diagnostics_received', {
      file: data.file,
      diagnostics: limitedDiagnostics,
      error_count: limitedDiagnostics.filter(d => d.severity === 1).length,
      warning_count: limitedDiagnostics.filter(d => d.severity === 2).length,
      total_count: data.diagnostics.length
    });
  }

  private handleHoverEvent(data: { symbol: string; results: HoverResult[] }): void {
    this.triggerLSPEvent('hover_received', {
      symbol: data.symbol,
      result_count: data.results.length,
      has_documentation: data.results.some(r => r.hover.contents),
      locations: data.results.map(r => r.location)
    });
  }

  private handleServerStartedEvent(data: { serverId: string; root: string }): void {
    this.triggerLSPEvent('server_started', {
      server_id: data.serverId,
      root_path: data.root,
      timestamp: new Date().toISOString()
    });
  }

  private handleServerStoppedEvent(data: { serverId: string; root: string }): void {
    this.triggerLSPEvent('server_stopped', {
      server_id: data.serverId,
      root_path: data.root,
      timestamp: new Date().toISOString()
    });
  }

  private handleErrorEvent(data: { error: string; context: any }): void {
    this.triggerLSPEvent('error_occurred', {
      error_message: data.error,
      context: data.context,
      severity: 'error',
      timestamp: new Date().toISOString()
    });
  }

  private handleHookResponse(data: { hook: string; response: any; event: string }): void {
    log(`Hook response from ${data.hook} for event ${data.event}: ${JSON.stringify(data.response)}`);
    
    // Process hook responses that should influence LSP behavior
    if (data.response && data.response.lsp_action) {
      this.processLSPAction(data.response.lsp_action);
    }
  }

  private async processLSPAction(action: any): Promise<void> {
    // Hooks can request LSP actions like:
    // - Trigger diagnostics refresh
    // - Change server configuration
    // - Enable/disable features
    
    switch (action.type) {
      case 'refresh_diagnostics':
        this.emit('refresh_diagnostics_requested', action.data);
        break;
      case 'configure_server':
        this.emit('configure_server_requested', action.data);
        break;
      case 'disable_notifications':
        this.config.audio_notifications = false;
        await this.saveConfiguration();
        break;
      case 'enable_notifications':
        this.config.audio_notifications = true;
        await this.saveConfiguration();
        break;
      default:
        log(`Unknown LSP action type: ${action.type}`);
    }
  }

  private isSignificantEvent(event: string): boolean {
    const significantEvents = [
      'server_started',
      'server_stopped',
      'error_occurred',
      'diagnostics_received'
    ];
    return significantEvents.includes(event);
  }

  private isCodeQualityEvent(event: string): boolean {
    const qualityEvents = [
      'diagnostics_received',
      'hover_received'
    ];
    return qualityEvents.includes(event);
  }

  /**
   * Public API for external integration
   */
  public async enableHooks(): Promise<void> {
    this.config.enabled = true;
    await this.saveConfiguration();
    log('LSP hooks enabled');
  }

  public async disableHooks(): Promise<void> {
    this.config.enabled = false;
    await this.saveConfiguration();
    log('LSP hooks disabled');
  }

  public async setDebounceTime(ms: number): Promise<void> {
    this.config.debounce_ms = Math.max(100, Math.min(5000, ms));
    await this.saveConfiguration();
    log(`LSP hooks debounce time set to ${this.config.debounce_ms}ms`);
  }

  public getConfiguration(): LSPHookConfig {
    return { ...this.config };
  }

  public async updateConfiguration(updates: Partial<LSPHookConfig>): Promise<void> {
    this.config = { ...this.config, ...updates };
    await this.saveConfiguration();
    log('LSP hooks configuration updated');
  }

  /**
   * Shutdown and cleanup
   */
  public async shutdown(): Promise<void> {
    log('Shutting down LSP hook adapter...');
    
    // Clear all debounce timers
    for (const timer of this.debounceTimers.values()) {
      clearTimeout(timer);
    }
    this.debounceTimers.clear();

    // Kill any running hook processes
    for (const process of this.hookProcesses.values()) {
      if (!process.killed) {
        process.kill();
      }
    }
    this.hookProcesses.clear();

    this.removeAllListeners();
    log('LSP hook adapter shutdown complete');
  }
}

// Singleton instance for daemon use
export const lspHookAdapter = new LSPHookAdapter();