/**
 * LSP Event Triggers - V3.0 Event Management
 * Orchestrates LSP events and triggers appropriate hook responses
 */

import { EventEmitter } from 'events';
import { lspHookAdapter } from './adapter.js';
import { log } from '../logger.js';
import type { Diagnostic, HoverResult } from '../lsp/types.js';

interface EventTriggerRule {
  event: string;
  condition: (data: any) => boolean;
  throttle_ms?: number;
  priority: number;
  hooks: string[];
}

interface TriggerMetrics {
  total_triggered: number;
  last_triggered: string;
  average_response_time_ms: number;
  success_rate: number;
}

export class LSPEventTriggers extends EventEmitter {
  private rules: Map<string, EventTriggerRule> = new Map();
  private lastTriggerTimes: Map<string, number> = new Map();
  private metrics: Map<string, TriggerMetrics> = new Map();
  private enabled = true;

  constructor() {
    super();
    this.setupDefaultRules();
    this.setupTriggerHandlers();
  }

  private setupDefaultRules(): void {
    // Diagnostics-based triggers
    this.addRule('critical_errors', {
      event: 'diagnostics_received',
      condition: (data) => data.error_count > 0,
      throttle_ms: 1000,
      priority: 1,
      hooks: ['audio_player_v3', 'status_line_manager', 'quality_gate_hook']
    });

    this.addRule('many_warnings', {
      event: 'diagnostics_received',
      condition: (data) => data.warning_count > 5,
      throttle_ms: 2000,
      priority: 2,
      hooks: ['status_line_manager', 'quality_gate_hook']
    });

    this.addRule('clean_code', {
      event: 'diagnostics_received',
      condition: (data) => data.error_count === 0 && data.warning_count === 0,
      throttle_ms: 5000,
      priority: 3,
      hooks: ['audio_player_v3', 'status_line_manager']
    });

    // Server lifecycle triggers
    this.addRule('server_startup', {
      event: 'server_started',
      condition: () => true,
      priority: 1,
      hooks: ['audio_player_v3', 'status_line_manager', 'smart_orchestrator']
    });

    this.addRule('server_crash', {
      event: 'server_stopped',
      condition: (data) => data.unexpected === true,
      priority: 1,
      hooks: ['audio_player_v3', 'status_line_manager', 'smart_orchestrator']
    });

    // Code intelligence triggers
    this.addRule('symbol_documentation', {
      event: 'hover_received',
      condition: (data) => data.has_documentation && data.result_count > 0,
      throttle_ms: 1000,
      priority: 3,
      hooks: ['status_line_manager']
    });

    this.addRule('symbol_not_found', {
      event: 'hover_received',
      condition: (data) => data.result_count === 0,
      throttle_ms: 500,
      priority: 2,
      hooks: ['status_line_manager']
    });

    // Error triggers
    this.addRule('lsp_error', {
      event: 'error_occurred',
      condition: (data) => data.severity === 'error',
      priority: 1,
      hooks: ['audio_player_v3', 'status_line_manager', 'smart_orchestrator']
    });

    // File operation triggers
    this.addRule('file_analysis_complete', {
      event: 'diagnostics_received',
      condition: (data) => data.total_count > 0,
      throttle_ms: 3000,
      priority: 2,
      hooks: ['performance_monitor', 'auto_documentation']
    });

    // Quality triggers
    this.addRule('quality_improvement_needed', {
      event: 'diagnostics_received',
      condition: (data) => (data.error_count + data.warning_count) > 10,
      throttle_ms: 5000,
      priority: 2,
      hooks: ['quality_gate_hook', 'auto_formatter', 'smart_orchestrator']
    });

    // Performance triggers
    this.addRule('slow_analysis', {
      event: 'analysis_performance',
      condition: (data) => data.duration_ms > 5000,
      priority: 2,
      hooks: ['performance_monitor', 'status_line_manager']
    });
  }

  private setupTriggerHandlers(): void {
    // Listen for LSP events from the adapter
    lspHookAdapter.on('lsp_event_triggered', this.handleLSPEvent.bind(this));
  }

  private async handleLSPEvent(eventData: any): Promise<void> {
    if (!this.enabled) {
      return;
    }

    const { event, data } = eventData;
    log(`Processing LSP event triggers for: ${event}`);

    // Find matching rules
    const matchingRules = this.findMatchingRules(event, data);
    
    if (matchingRules.length === 0) {
      log(`No trigger rules matched for event: ${event}`);
      return;
    }

    // Sort by priority and execute
    matchingRules.sort((a, b) => a.priority - b.priority);

    for (const rule of matchingRules) {
      await this.executeRule(rule, data);
    }
  }

  private findMatchingRules(event: string, data: any): EventTriggerRule[] {
    const matchingRules: EventTriggerRule[] = [];

    for (const [ruleName, rule] of this.rules) {
      if (rule.event === event) {
        try {
          if (rule.condition(data)) {
            // Check throttling
            if (this.isThrottled(ruleName, rule.throttle_ms)) {
              log(`Rule ${ruleName} throttled, skipping`);
              continue;
            }

            matchingRules.push(rule);
            this.updateLastTriggerTime(ruleName);
          }
        } catch (error) {
          log(`Error evaluating rule condition for ${ruleName}: ${error}`);
        }
      }
    }

    return matchingRules;
  }

  private isThrottled(ruleName: string, throttleMs?: number): boolean {
    if (!throttleMs) {
      return false;
    }

    const lastTrigger = this.lastTriggerTimes.get(ruleName);
    if (!lastTrigger) {
      return false;
    }

    return Date.now() - lastTrigger < throttleMs;
  }

  private updateLastTriggerTime(ruleName: string): void {
    this.lastTriggerTimes.set(ruleName, Date.now());
  }

  private async executeRule(rule: EventTriggerRule, data: any): Promise<void> {
    const startTime = Date.now();
    const ruleName = this.getRuleName(rule);

    try {
      log(`Executing trigger rule: ${ruleName} with ${rule.hooks.length} hooks`);

      // Create enhanced trigger data
      const triggerData = {
        ...data,
        trigger_rule: ruleName,
        trigger_priority: rule.priority,
        timestamp: new Date().toISOString(),
        lsp_source: true
      };

      // Execute hooks in parallel for better performance
      const hookPromises = rule.hooks.map(async (hookName) => {
        try {
          await this.executeHookTrigger(hookName, triggerData);
          return { hook: hookName, success: true };
        } catch (error) {
          log(`Hook ${hookName} failed in rule ${ruleName}: ${error}`);
          return { hook: hookName, success: false, error };
        }
      });

      const results = await Promise.allSettled(hookPromises);
      const duration = Date.now() - startTime;

      // Update metrics
      this.updateMetrics(ruleName, duration, results);

      // Log execution summary
      const successCount = results.filter(r => r.status === 'fulfilled').length;
      log(`Rule ${ruleName} executed: ${successCount}/${rule.hooks.length} hooks successful in ${duration}ms`);

    } catch (error) {
      log(`Failed to execute rule ${ruleName}: ${error}`);
      this.updateMetrics(ruleName, Date.now() - startTime, [], false);
    }
  }

  private getRuleName(rule: EventTriggerRule): string {
    for (const [name, r] of this.rules) {
      if (r === rule) {
        return name;
      }
    }
    return 'unknown';
  }

  private async executeHookTrigger(hookName: string, data: any): Promise<void> {
    // Use the adapter to trigger the hook
    await lspHookAdapter.triggerLSPEvent(`hook_trigger_${hookName}`, data);
  }

  private updateMetrics(ruleName: string, duration: number, results: any[], success: boolean = true): void {
    let metrics = this.metrics.get(ruleName);
    
    if (!metrics) {
      metrics = {
        total_triggered: 0,
        last_triggered: '',
        average_response_time_ms: 0,
        success_rate: 0
      };
    }

    metrics.total_triggered++;
    metrics.last_triggered = new Date().toISOString();
    
    // Update average response time
    const currentAvg = metrics.average_response_time_ms;
    const count = metrics.total_triggered;
    metrics.average_response_time_ms = ((currentAvg * (count - 1)) + duration) / count;

    // Update success rate
    const successfulResults = results.filter(r => r.status === 'fulfilled').length;
    const totalResults = Math.max(results.length, 1);
    const currentSuccessRate = successfulResults / totalResults;
    
    metrics.success_rate = ((metrics.success_rate * (count - 1)) + currentSuccessRate) / count;

    this.metrics.set(ruleName, metrics);
  }

  /**
   * Public API methods
   */
  public addRule(name: string, rule: EventTriggerRule): void {
    this.rules.set(name, rule);
    log(`Added trigger rule: ${name} for event ${rule.event}`);
  }

  public removeRule(name: string): boolean {
    const removed = this.rules.delete(name);
    if (removed) {
      log(`Removed trigger rule: ${name}`);
      this.metrics.delete(name);
      this.lastTriggerTimes.delete(name);
    }
    return removed;
  }

  public updateRule(name: string, updates: Partial<EventTriggerRule>): boolean {
    const rule = this.rules.get(name);
    if (!rule) {
      return false;
    }

    const updatedRule = { ...rule, ...updates };
    this.rules.set(name, updatedRule);
    log(`Updated trigger rule: ${name}`);
    return true;
  }

  public getRules(): Map<string, EventTriggerRule> {
    return new Map(this.rules);
  }

  public getMetrics(): Map<string, TriggerMetrics> {
    return new Map(this.metrics);
  }

  public enable(): void {
    this.enabled = true;
    log('LSP event triggers enabled');
  }

  public disable(): void {
    this.enabled = false;
    log('LSP event triggers disabled');
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * Special trigger methods for common scenarios
   */
  public async triggerDiagnosticsAnalysis(file: string, diagnostics: Diagnostic[]): Promise<void> {
    const data = {
      file,
      diagnostics,
      error_count: diagnostics.filter(d => d.severity === 1).length,
      warning_count: diagnostics.filter(d => d.severity === 2).length,
      total_count: diagnostics.length
    };

    await lspHookAdapter.triggerLSPEvent('diagnostics_received', data);
  }

  public async triggerHoverAnalysis(symbol: string, results: HoverResult[]): Promise<void> {
    const data = {
      symbol,
      results,
      result_count: results.length,
      has_documentation: results.some(r => r.hover.contents),
      locations: results.map(r => r.location)
    };

    await lspHookAdapter.triggerLSPEvent('hover_received', data);
  }

  public async triggerServerEvent(event: string, serverId: string, root: string, additionalData?: any): Promise<void> {
    const data = {
      server_id: serverId,
      root_path: root,
      timestamp: new Date().toISOString(),
      ...additionalData
    };

    await lspHookAdapter.triggerLSPEvent(event, data);
  }

  public async triggerError(error: string, context: any, severity: 'error' | 'warning' | 'info' = 'error'): Promise<void> {
    const data = {
      error_message: error,
      context,
      severity,
      timestamp: new Date().toISOString()
    };

    await lspHookAdapter.triggerLSPEvent('error_occurred', data);
  }

  /**
   * Performance monitoring
   */
  public async triggerPerformanceEvent(operation: string, duration: number, metadata?: any): Promise<void> {
    const data = {
      operation,
      duration_ms: duration,
      metadata: metadata || {},
      timestamp: new Date().toISOString()
    };

    await lspHookAdapter.triggerLSPEvent('analysis_performance', data);
  }

  /**
   * Cleanup
   */
  public shutdown(): void {
    this.enabled = false;
    this.rules.clear();
    this.lastTriggerTimes.clear();
    this.metrics.clear();
    this.removeAllListeners();
    log('LSP event triggers shutdown complete');
  }
}

// Export singleton instance
export const lspEventTriggers = new LSPEventTriggers();