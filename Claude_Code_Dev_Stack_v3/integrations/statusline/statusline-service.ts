/**
 * Statusline Service for PWA Integration
 * Provides a bridge between the enhanced statusline backend and PWA frontend
 */

import { DevStackStatuslineIntegration } from './pwa-integration';
import type { ClaudeHookData } from './src/index';

export interface StatuslineServiceConfig {
  configPath?: string;
  projectDir?: string;
  updateInterval?: number;
}

export class StatuslineService {
  private integration: DevStackStatuslineIntegration;
  private updateInterval: number;
  private intervalId?: NodeJS.Timeout;
  private callbacks: Array<(data: any) => void> = [];

  constructor(config: StatuslineServiceConfig = {}) {
    this.integration = new DevStackStatuslineIntegration(
      config.configPath,
      config.projectDir
    );
    this.updateInterval = config.updateInterval || 1000; // 1 second default
  }

  /**
   * Start automatic updates
   */
  start(hookData: ClaudeHookData) {
    if (this.intervalId) {
      this.stop();
    }

    this.intervalId = setInterval(async () => {
      try {
        const [statuslineData, devStackMetrics] = await Promise.all([
          this.integration.generateForPWA(hookData),
          this.integration.getDevStackMetrics(hookData.workspace?.project_dir)
        ]);

        const combinedData = {
          statusline: statuslineData,
          metrics: devStackMetrics,
          timestamp: new Date()
        };

        this.callbacks.forEach(callback => {
          try {
            callback(combinedData);
          } catch (error) {
            console.error('Error in statusline callback:', error);
          }
        });
      } catch (error) {
        console.error('Error updating statusline:', error);
      }
    }, this.updateInterval);
  }

  /**
   * Stop automatic updates
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  /**
   * Subscribe to statusline updates
   */
  subscribe(callback: (data: any) => void): () => void {
    this.callbacks.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.callbacks.indexOf(callback);
      if (index > -1) {
        this.callbacks.splice(index, 1);
      }
    };
  }

  /**
   * Get current statusline data manually
   */
  async getCurrentData(hookData: ClaudeHookData) {
    const [statuslineData, devStackMetrics] = await Promise.all([
      this.integration.generateForPWA(hookData),
      this.integration.getDevStackMetrics(hookData.workspace?.project_dir)
    ]);

    return {
      statusline: statuslineData,
      metrics: devStackMetrics,
      timestamp: new Date()
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<any>) {
    this.integration.updateConfig(newConfig);
  }

  /**
   * Format data for React component
   */
  formatForReactComponent(data: any) {
    const { metrics } = data;
    
    return {
      agents: {
        active: metrics.agents.active,
        total: metrics.agents.total,
        status: metrics.agents.status
      },
      tasks: {
        active: metrics.tasks.active,
        completed: metrics.tasks.completed,
        total: metrics.tasks.total,
        status: metrics.tasks.status
      },
      hooks: {
        triggered: metrics.hooks.active,
        total: metrics.hooks.total,
        errors: metrics.hooks.errors,
        status: metrics.hooks.status
      },
      audioStatus: {
        enabled: metrics.audio.enabled,
        volume: metrics.audio.volume,
        queue: 0, // TODO: Add queue info to metrics
        status: metrics.audio.status
      },
      // TODO: Add git and cost info from statusline data
      gitInfo: {
        branch: 'main', // TODO: Extract from statusline
        dirty: false,
        ahead: 0,
        behind: 0
      },
      costInfo: {
        session: 0, // TODO: Extract from statusline
        today: 0,
        budget: 25
      },
      modelInfo: {
        id: 'claude-3-5-sonnet',
        displayName: 'Claude 3.5 Sonnet'
      }
    };
  }
}

// Export factory function
export function createStatuslineService(config?: StatuslineServiceConfig): StatuslineService {
  return new StatuslineService(config);
}

// Default export
export default StatuslineService;