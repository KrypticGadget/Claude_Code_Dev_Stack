/**
 * Ultimate Statusline Integration for Claude Code Dev Stack v3.0
 * 
 * PERFORMANCE OPTIMIZED EDITION - 100ms Real-time Updates
 * 
 * Combines:
 * - Claude Powerline (@Owloops) for cost/git/themes/model tracking
 * - Dev Stack monitoring for agents/tasks/hooks/audio (original by Zach)
 * - Real-time dashboard integration
 * - Mobile app synchronization
 * - Browser extension bridge
 * 
 * Attribution: Extends @Owloops/claude-powerline with Dev Stack orchestration metrics
 * Original powerline by @Owloops: https://github.com/owloops/claude-powerline
 * Dev Stack orchestration by Zach
 */

import { EventEmitter } from 'events';
import { exec, spawn } from 'child_process';
import { promises as fs } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import WebSocket from 'ws';

interface PowerlineData {
  directory: string;
  git: {
    branch: string;
    dirty: boolean;
    ahead: number;
    behind: number;
    stash: number;
    operation?: string;
    upstreamBranch?: string;
  };
  model: {
    id: string;
    displayName: string;
    provider?: string;
    version?: string;
  };
  cost: {
    session: number;
    today: number;
    budget: number;
    remaining: number;
    percentage: number;
  };
  context: {
    tokens: number;
    maxTokens: number;
    percentage: number;
  };
  performance: {
    responseTime: number;
    throughput: number;
    avgResponseTime: number;
  };
}

interface DevStackMetrics {
  agents: {
    active: number;
    total: number;
    status: 'idle' | 'working' | 'error';
    byType: { [key: string]: number };
    performance: {
      avgResponseTime: number;
      successRate: number;
      errorCount: number;
    };
  };
  tasks: {
    active: number;
    completed: number;
    total: number;
    queued: number;
    failed: number;
    status: 'none' | 'running' | 'complete' | 'error';
    performance: {
      avgExecutionTime: number;
      throughput: number;
      queueDepth: number;
    };
  };
  hooks: {
    triggered: number;
    total: number;
    errors: number;
    active: number;
    status: 'ready' | 'busy' | 'error';
    performance: {
      avgLatency: number;
      successRate: number;
      concurrentHooks: number;
    };
  };
  audio: {
    enabled: boolean;
    volume: number;
    lastEvent: string;
    status: 'silent' | 'playing' | 'error';
    queue: number;
    performance: {
      latency: number;
      queuedEvents: number;
      eventRate: number;
    };
  };
  system: {
    cpu: number;
    memory: number;
    disk: number;
    network: {
      bytesIn: number;
      bytesOut: number;
      latency: number;
    };
  };
}

interface PerformanceMetrics {
  updateLatency: number;
  dataCollectionTime: number;
  renderTime: number;
  wsLatency: number;
  memoryUsage: number;
  cpuUsage: number;
}

interface UltimateStatuslineData {
  powerline: PowerlineData;
  devStack: DevStackMetrics;
  performance: PerformanceMetrics;
  timestamp: number;
  updateId: string;
  connectionId?: string;
}

interface StatuslineConfig {
  updateInterval: number;
  enablePerformanceMetrics: boolean;
  enableWebSocket: boolean;
  enableDashboardIntegration: boolean;
  enableMobileSync: boolean;
  theme: string;
  segments: {
    powerline: boolean;
    devStack: boolean;
    performance: boolean;
  };
  integrations: {
    dashboard: {
      url: string;
      port: number;
    };
    mobile: {
      url: string;
      port: number;
    };
    browser: {
      enabled: boolean;
      port: number;
    };
  };
}

export class UltimateStatuslineManager extends EventEmitter {
  private claudeStatusDir: string;
  private devStackStateDir: string;
  private config: StatuslineConfig;
  private intervalId?: NodeJS.Timeout;
  private isRunning: boolean = false;
  private performanceTracker: PerformanceTracker;
  private webSocketServer?: WebSocket.Server;
  private connectedClients: Set<WebSocket> = new Set();
  private dataCache: Map<string, any> = new Map();
  private lastUpdateId: string = '';
  private powerlineProcess?: any;

  constructor(config?: Partial<StatuslineConfig>) {
    super();
    
    this.claudeStatusDir = join(homedir(), '.claude', 'status');
    this.devStackStateDir = join(homedir(), '.claude', 'dev-stack');
    
    this.config = {
      updateInterval: 100, // 100ms for real-time
      enablePerformanceMetrics: true,
      enableWebSocket: true,
      enableDashboardIntegration: true,
      enableMobileSync: true,
      theme: 'tokyo-night',
      segments: {
        powerline: true,
        devStack: true,
        performance: true,
      },
      integrations: {
        dashboard: {
          url: 'http://localhost:8080',
          port: 8080,
        },
        mobile: {
          url: 'http://localhost:8086',
          port: 8086,
        },
        browser: {
          enabled: true,
          port: 8087,
        },
      },
      ...config,
    };
    
    this.performanceTracker = new PerformanceTracker();
    this.ensureDirectories();
    this.setupWebSocketServer();
    this.setupPowerlineIntegration();
  }

  private async ensureDirectories(): Promise<void> {
    try {
      await Promise.all([
        fs.mkdir(this.claudeStatusDir, { recursive: true }),
        fs.mkdir(this.devStackStateDir, { recursive: true }),
        fs.mkdir(join(this.devStackStateDir, 'agents'), { recursive: true }),
        fs.mkdir(join(this.devStackStateDir, 'tasks'), { recursive: true }),
        fs.mkdir(join(this.devStackStateDir, 'hooks'), { recursive: true }),
        fs.mkdir(join(this.devStackStateDir, 'audio'), { recursive: true }),
      ]);
    } catch (error) {
      console.error('Failed to create directories:', error);
    }
  }

  private setupWebSocketServer(): void {
    if (!this.config.enableWebSocket) return;

    try {
      this.webSocketServer = new WebSocket.Server({
        port: this.config.integrations.browser.port,
        perMessageDeflate: false, // Optimize for low latency
      });

      this.webSocketServer.on('connection', (ws) => {
        this.connectedClients.add(ws);
        console.log(`New statusline client connected. Total: ${this.connectedClients.size}`);

        // Send initial data immediately
        this.sendDataToClient(ws);

        ws.on('close', () => {
          this.connectedClients.delete(ws);
          console.log(`Statusline client disconnected. Total: ${this.connectedClients.size}`);
        });

        ws.on('message', (data) => {
          try {
            const message = JSON.parse(data.toString());
            this.handleClientMessage(ws, message);
          } catch (error) {
            console.error('Invalid message from client:', error);
          }
        });
      });

      console.log(`StatusLine WebSocket server running on port ${this.config.integrations.browser.port}`);
    } catch (error) {
      console.error('Failed to setup WebSocket server:', error);
    }
  }

  private setupPowerlineIntegration(): void {
    // Setup integration with @Owloops/claude-powerline
    // This will spawn the powerline process and capture its output
    try {
      this.powerlineProcess = spawn('npx', ['@owloops/claude-powerline', '--json'], {
        stdio: 'pipe',
        shell: true,
      });

      this.powerlineProcess.stdout?.on('data', (data: Buffer) => {
        try {
          const powerlineData = JSON.parse(data.toString());
          this.dataCache.set('powerline', powerlineData);
        } catch (error) {
          // Fallback for non-JSON output
          console.debug('Powerline non-JSON output:', data.toString());
        }
      });

      this.powerlineProcess.stderr?.on('data', (data: Buffer) => {
        console.debug('Powerline stderr:', data.toString());
      });
    } catch (error) {
      console.warn('Could not setup powerline integration:', error);
    }
  }

  /**
   * Start real-time statusline monitoring with 100ms precision
   */
  async start(): Promise<void> {
    if (this.isRunning) return;
    
    console.log('🚀 Starting Ultimate Statusline Manager...');
    this.isRunning = true;
    
    // High-precision interval for 100ms updates
    this.intervalId = setInterval(async () => {
      const startTime = Date.now();
      
      try {
        // Gather all data in parallel for maximum performance
        const data = await this.gatherStatuslineDataOptimized();
        
        // Track performance
        const dataCollectionTime = Date.now() - startTime;
        data.performance.dataCollectionTime = dataCollectionTime;
        
        // Emit to event listeners
        this.emit('update', data);
        
        // Broadcast to WebSocket clients
        await this.broadcastToClients(data);
        
        // Write status files for terminal integration
        await this.writeStatusFilesOptimized(data);
        
        // Update dashboard integration
        if (this.config.enableDashboardIntegration) {
          await this.updateDashboard(data);
        }
        
        // Update mobile app
        if (this.config.enableMobileSync) {
          await this.updateMobile(data);
        }
        
        // Track total update latency
        data.performance.updateLatency = Date.now() - startTime;
        
      } catch (error) {
        console.error('❌ Statusline update error:', error);
        this.emit('error', error);
      }
    }, this.config.updateInterval);
    
    console.log(`✅ Ultimate Statusline started with ${this.config.updateInterval}ms intervals`);
    this.emit('started');
  }

  /**
   * Stop statusline monitoring
   */
  stop(): void {
    console.log('🛑 Stopping Ultimate Statusline Manager...');
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
    
    // Close WebSocket server
    if (this.webSocketServer) {
      this.webSocketServer.close();
      this.connectedClients.clear();
    }
    
    // Stop powerline process
    if (this.powerlineProcess) {
      this.powerlineProcess.kill();
    }
    
    this.isRunning = false;
    console.log('✅ Ultimate Statusline stopped');
    this.emit('stopped');
  }

  /**
   * Optimized data gathering with parallel execution
   */
  private async gatherStatuslineDataOptimized(): Promise<UltimateStatuslineData> {
    const updateId = this.generateUpdateId();
    const timestamp = Date.now();
    
    // Gather all data sources in parallel for maximum performance
    const [powerlineData, devStackMetrics, performanceMetrics] = await Promise.all([
      this.getPowerlineDataOptimized(),
      this.getDevStackMetricsOptimized(),
      this.getPerformanceMetrics(),
    ]);

    const data: UltimateStatuslineData = {
      powerline: powerlineData,
      devStack: devStackMetrics,
      performance: performanceMetrics,
      timestamp,
      updateId,
    };

    // Cache the data for quick access
    this.dataCache.set('latest', data);
    this.lastUpdateId = updateId;

    return data;
  }

  /**
   * Optimized Powerline data collection with fallback
   */
  private async getPowerlineDataOptimized(): Promise<PowerlineData> {
    const startTime = Date.now();
    
    // Try to get cached powerline data first
    const cachedData = this.dataCache.get('powerline');
    if (cachedData && (Date.now() - cachedData.timestamp) < 1000) {
      return this.enhancePowerlineData(cachedData);
    }

    // Fallback to manual collection
    try {
      const [gitData, modelData, costData, contextData] = await Promise.all([
        this.getGitDataFast(),
        this.getModelDataFast(),
        this.getCostDataFast(),
        this.getContextDataFast(),
      ]);

      const powerlineData: PowerlineData = {
        directory: process.cwd().split(/[/\\]/).pop() || 'unknown',
        git: gitData,
        model: modelData,
        cost: costData,
        context: contextData,
        performance: {
          responseTime: Date.now() - startTime,
          throughput: 0, // Will be calculated
          avgResponseTime: 0, // Will be calculated
        },
      };

      return powerlineData;
    } catch (error) {
      console.error('Error getting powerline data:', error);
      return this.getFallbackPowerlineData();
    }
  }

  /**
   * Optimized Dev Stack metrics with caching
   */
  private async getDevStackMetricsOptimized(): Promise<DevStackMetrics> {
    const [agentMetrics, taskMetrics, hookMetrics, audioMetrics, systemMetrics] = await Promise.all([
      this.getAgentMetricsOptimized(),
      this.getTaskMetricsOptimized(),
      this.getHookMetricsOptimized(),
      this.getAudioMetricsOptimized(),
      this.getSystemMetricsOptimized(),
    ]);

    return {
      agents: agentMetrics,
      tasks: taskMetrics,
      hooks: hookMetrics,
      audio: audioMetrics,
      system: systemMetrics,
    };
  }

  private async getAgentMetricsOptimized() {
    try {
      // Read all agent state files in parallel
      const agentFiles = ['active_agents.json', 'agent_performance.json', 'agent_types.json'];
      const agentData = await Promise.all(
        agentFiles.map(async (file) => {
          try {
            const filePath = join(this.devStackStateDir, 'agents', file);
            const data = await fs.readFile(filePath, 'utf-8');
            return JSON.parse(data);
          } catch {
            return {};
          }
        })
      );

      const [activeAgents, performance, types] = agentData;
      
      const active = Object.keys(activeAgents).filter(key => activeAgents[key]?.active).length;
      const total = 28; // Total agents in Dev Stack v3
      
      let status: 'idle' | 'working' | 'error' = 'idle';
      if (active > 0) status = 'working';
      if (Object.values(activeAgents).some((agent: any) => agent?.error)) status = 'error';

      return {
        active,
        total,
        status,
        byType: types || {},
        performance: {
          avgResponseTime: performance?.avgResponseTime || 0,
          successRate: performance?.successRate || 100,
          errorCount: performance?.errorCount || 0,
        },
      };
    } catch {
      return {
        active: 0,
        total: 28,
        status: 'idle' as const,
        byType: {},
        performance: { avgResponseTime: 0, successRate: 100, errorCount: 0 },
      };
    }
  }

  private async getTaskMetricsOptimized() {
    try {
      const taskData = await this.readStateFile('tasks', 'task_progress.json');
      
      return {
        active: taskData.active || 0,
        completed: taskData.completed || 0,
        total: taskData.total || 0,
        queued: taskData.queued || 0,
        failed: taskData.failed || 0,
        status: this.determineTaskStatus(taskData),
        performance: {
          avgExecutionTime: taskData.performance?.avgExecutionTime || 0,
          throughput: taskData.performance?.throughput || 0,
          queueDepth: taskData.performance?.queueDepth || 0,
        },
      };
    } catch {
      return {
        active: 0, completed: 0, total: 0, queued: 0, failed: 0,
        status: 'none' as const,
        performance: { avgExecutionTime: 0, throughput: 0, queueDepth: 0 },
      };
    }
  }

  private async getHookMetricsOptimized() {
    try {
      const hookData = await this.readStateFile('hooks', 'hook_status.json');
      
      return {
        triggered: hookData.triggered || 0,
        total: 28, // Total hooks in Dev Stack v3
        errors: hookData.errors || 0,
        active: hookData.active || 0,
        status: this.determineHookStatus(hookData),
        performance: {
          avgLatency: hookData.performance?.avgLatency || 0,
          successRate: hookData.performance?.successRate || 100,
          concurrentHooks: hookData.performance?.concurrentHooks || 0,
        },
      };
    } catch {
      return {
        triggered: 0, total: 28, errors: 0, active: 0,
        status: 'ready' as const,
        performance: { avgLatency: 0, successRate: 100, concurrentHooks: 0 },
      };
    }
  }

  private async getAudioMetricsOptimized() {
    try {
      const audioData = await this.readStateFile('audio', 'audio_status.json');
      
      return {
        enabled: audioData.enabled || false,
        volume: audioData.volume || 0.5,
        lastEvent: audioData.lastEvent || 'none',
        status: audioData.status || 'silent',
        queue: audioData.queue || 0,
        performance: {
          latency: audioData.performance?.latency || 0,
          queuedEvents: audioData.performance?.queuedEvents || 0,
          eventRate: audioData.performance?.eventRate || 0,
        },
      };
    } catch {
      return {
        enabled: false, volume: 0.5, lastEvent: 'none',
        status: 'silent' as const, queue: 0,
        performance: { latency: 0, queuedEvents: 0, eventRate: 0 },
      };
    }
  }

  private async getSystemMetricsOptimized() {
    try {
      // Use system monitoring if available
      const cpuUsage = process.cpuUsage();
      const memUsage = process.memoryUsage();
      
      return {
        cpu: (cpuUsage.user + cpuUsage.system) / 1000000, // Convert to percentage approximation
        memory: (memUsage.heapUsed / memUsage.heapTotal) * 100,
        disk: 50, // Placeholder - would need proper disk monitoring
        network: {
          bytesIn: 0, // Would need network monitoring
          bytesOut: 0,
          latency: 0,
        },
      };
    } catch {
      return {
        cpu: 0, memory: 0, disk: 0,
        network: { bytesIn: 0, bytesOut: 0, latency: 0 },
      };
    }
  }

  // Utility methods for performance and integration
  
  private generateUpdateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private async readStateFile(category: string, filename: string): Promise<any> {
    try {
      const filePath = join(this.devStackStateDir, category, filename);
      const data = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  private determineTaskStatus(taskData: any): 'none' | 'running' | 'complete' | 'error' {
    if (taskData.failed > 0) return 'error';
    if (taskData.active > 0) return 'running';
    if (taskData.completed === taskData.total && taskData.total > 0) return 'complete';
    return 'none';
  }

  private determineHookStatus(hookData: any): 'ready' | 'busy' | 'error' {
    if (hookData.errors > 0) return 'error';
    if (hookData.active > 0) return 'busy';
    return 'ready';
  }

  private async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    if (!this.config.enablePerformanceMetrics) {
      return { updateLatency: 0, dataCollectionTime: 0, renderTime: 0, wsLatency: 0, memoryUsage: 0, cpuUsage: 0 };
    }

    return this.performanceTracker.getMetrics();
  }

  // Integration methods

  private async broadcastToClients(data: UltimateStatuslineData): Promise<void> {
    if (this.connectedClients.size === 0) return;

    const message = JSON.stringify({
      type: 'statusline_update',
      data,
      attribution: {
        powerline: '@Owloops/claude-powerline',
        devStack: 'Dev Stack monitoring by Zach',
        browser: 'Ultimate Statusline Integration'
      }
    });

    const disconnectedClients = new Set<WebSocket>();

    for (const client of this.connectedClients) {
      try {
        if (client.readyState === WebSocket.OPEN) {
          client.send(message);
        } else {
          disconnectedClients.add(client);
        }
      } catch (error) {
        disconnectedClients.add(client);
      }
    }

    // Remove disconnected clients
    for (const client of disconnectedClients) {
      this.connectedClients.delete(client);
    }
  }

  private async sendDataToClient(client: WebSocket): Promise<void> {
    const latestData = this.dataCache.get('latest');
    if (latestData) {
      try {
        client.send(JSON.stringify({
          type: 'statusline_initial',
          data: latestData
        }));
      } catch (error) {
        console.error('Error sending initial data to client:', error);
      }
    }
  }

  private handleClientMessage(client: WebSocket, message: any): void {
    switch (message.type) {
      case 'request_update':
        this.sendDataToClient(client);
        break;
      case 'update_config':
        this.updateConfig(message.config);
        break;
      case 'trigger_audio':
        this.triggerAudioEvent(message.event);
        break;
    }
  }

  private async updateDashboard(data: UltimateStatuslineData): Promise<void> {
    try {
      const response = await fetch(`${this.config.integrations.dashboard.url}/api/statusline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      // Dashboard integration is optional, don't throw
      console.debug('Dashboard update failed:', error);
    }
  }

  private async updateMobile(data: UltimateStatuslineData): Promise<void> {
    try {
      const response = await fetch(`${this.config.integrations.mobile.url}/api/statusline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      // Mobile integration is optional, don't throw
      console.debug('Mobile update failed:', error);
    }
  }

  private async writeStatusFilesOptimized(data: UltimateStatuslineData): Promise<void> {
    const statusFiles = {
      'latest.json': JSON.stringify(data, null, 2),
      'agent-count': `${data.devStack.agents.active}/${data.devStack.agents.total}`,
      'task-count': `${data.devStack.tasks.completed}/${data.devStack.tasks.total}`,
      'hook-count': `${data.devStack.hooks.triggered}/${data.devStack.hooks.total}`,
      'audio-status': data.devStack.audio.lastEvent,
      'git-branch': data.powerline.git.branch,
      'cost-session': data.powerline.cost.session.toFixed(2),
      'cost-today': data.powerline.cost.today.toFixed(2),
      'last-update': data.timestamp.toString(),
      'update-id': data.updateId,
      'performance': JSON.stringify(data.performance),
    };

    // Write all files in parallel for performance
    const writePromises = Object.entries(statusFiles).map(([filename, content]) =>
      fs.writeFile(join(this.claudeStatusDir, filename), content).catch(() => {
        // Ignore write errors for status files
      })
    );

    await Promise.all(writePromises);
  }

  private triggerAudioEvent(event: string): void {
    // Implement audio event triggering
    this.emit('audio_event', { event, timestamp: Date.now() });
  }

  // Fast data collection methods

  private async getGitDataFast() {
    return new Promise<any>((resolve) => {
      exec('git branch --show-current && git status --porcelain', { timeout: 500 }, (error, stdout) => {
        if (error) {
          resolve({ branch: 'main', dirty: false, ahead: 0, behind: 0, stash: 0 });
        } else {
          const lines = stdout.trim().split('\n');
          const branch = lines[0] || 'main';
          const dirty = lines.slice(1).some(line => line.trim().length > 0);
          resolve({ branch, dirty, ahead: 0, behind: 0, stash: 0 });
        }
      });
    });
  }

  private async getModelDataFast() {
    // Try to detect current Claude model
    return {
      id: 'claude-3-5-sonnet',
      displayName: 'Claude 3.5 Sonnet',
      provider: 'Anthropic',
      version: '20241022',
    };
  }

  private async getCostDataFast() {
    // Placeholder - would integrate with actual cost tracking
    return {
      session: 2.45,
      today: 8.32,
      budget: 25.00,
      remaining: 16.68,
      percentage: 33.28,
    };
  }

  private async getContextDataFast() {
    // Placeholder - would integrate with actual context tracking
    return {
      tokens: 45000,
      maxTokens: 200000,
      percentage: 22.5,
    };
  }

  private getFallbackPowerlineData(): PowerlineData {
    return {
      directory: 'unknown',
      git: { branch: 'main', dirty: false, ahead: 0, behind: 0, stash: 0 },
      model: { id: 'claude-3-5-sonnet', displayName: 'Claude 3.5 Sonnet' },
      cost: { session: 0, today: 0, budget: 25, remaining: 25, percentage: 0 },
      context: { tokens: 0, maxTokens: 200000, percentage: 0 },
      performance: { responseTime: 0, throughput: 0, avgResponseTime: 0 },
    };
  }

  private enhancePowerlineData(cachedData: any): PowerlineData {
    // Enhance cached powerline data with additional metrics
    return {
      ...cachedData,
      performance: {
        responseTime: Date.now() - cachedData.timestamp,
        throughput: 0,
        avgResponseTime: 0,
      },
    };
  }

  // Public API methods

  /**
   * Get current statusline data
   */
  async getCurrentData(): Promise<UltimateStatuslineData> {
    return this.gatherStatuslineDataOptimized();
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<StatuslineConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Restart if update interval changed
    if (newConfig.updateInterval && this.isRunning) {
      this.stop();
      setTimeout(() => this.start(), 100);
    }
    
    this.emit('config_updated', this.config);
  }

  /**
   * Format data for terminal display
   */
  formatForTerminal(data: UltimateStatuslineData): string {
    const { powerline, devStack } = data;
    
    // Line 1: Powerline (@Owloops) data
    const line1 = [
      `📁 ${powerline.directory}`,
      `🌿 ${powerline.git.branch}${powerline.git.dirty ? '*' : ''}`,
      `🤖 ${powerline.model.displayName}`,
      `💵 $${powerline.cost.session.toFixed(2)}`,
      `📊 ${powerline.context.tokens}k tokens`
    ].join(' | ');

    // Line 2: Dev Stack (Zach) monitoring
    const agentColor = devStack.agents.status === 'working' ? '🟢' : 
                      devStack.agents.status === 'error' ? '🔴' : '⚪';
    const taskColor = devStack.tasks.status === 'running' ? '🟡' : 
                     devStack.tasks.status === 'error' ? '🔴' : '⚪';
    const hookColor = devStack.hooks.status === 'busy' ? '🔵' : 
                     devStack.hooks.status === 'error' ? '🔴' : '⚪';
    const audioIcon = devStack.audio.enabled ? '🔊' : '🔇';

    const line2 = [
      `${agentColor} ${devStack.agents.active}/${devStack.agents.total}`,
      `${taskColor} ${devStack.tasks.completed}/${devStack.tasks.total}`,
      `${hookColor} ${devStack.hooks.triggered}/${devStack.hooks.total}`,
      `${audioIcon} ${devStack.audio.lastEvent}`,
      `⚡ ${data.performance.updateLatency}ms`
    ].join(' | ');

    return `${line1}\n${line2}`;
  }

  /**
   * Format for React PWA component
   */
  formatForReact(data: UltimateStatuslineData) {
    return {
      ...data,
      formatted: {
        terminal: this.formatForTerminal(data),
        powerlineCredit: '@Owloops/claude-powerline',
        devStackCredit: 'Dev Stack monitoring by Zach',
        performance: `${data.performance.updateLatency}ms latency, ${this.connectedClients.size} clients`
      }
    };
  }

  /**
   * Get connection statistics
   */
  getConnectionStats() {
    return {
      connectedClients: this.connectedClients.size,
      isRunning: this.isRunning,
      lastUpdateId: this.lastUpdateId,
      config: this.config,
      cacheSize: this.dataCache.size,
    };
  }
}

/**
 * Performance Tracker for monitoring system performance
 */
class PerformanceTracker {
  private metrics: PerformanceMetrics;
  private history: PerformanceMetrics[];
  private maxHistory: number = 100;

  constructor() {
    this.metrics = {
      updateLatency: 0,
      dataCollectionTime: 0,
      renderTime: 0,
      wsLatency: 0,
      memoryUsage: 0,
      cpuUsage: 0,
    };
    this.history = [];
  }

  getMetrics(): PerformanceMetrics {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    this.metrics.memoryUsage = memUsage.heapUsed / 1024 / 1024; // MB
    this.metrics.cpuUsage = (cpuUsage.user + cpuUsage.system) / 1000000; // Convert to percentage approximation
    
    // Add to history
    this.history.push({ ...this.metrics });
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
    
    return { ...this.metrics };
  }

  updateLatency(latency: number): void {
    this.metrics.updateLatency = latency;
  }

  updateDataCollectionTime(time: number): void {
    this.metrics.dataCollectionTime = time;
  }

  updateRenderTime(time: number): void {
    this.metrics.renderTime = time;
  }

  updateWSLatency(latency: number): void {
    this.metrics.wsLatency = latency;
  }

  getAverageMetrics(): PerformanceMetrics {
    if (this.history.length === 0) return this.metrics;
    
    const avg = this.history.reduce((acc, curr) => ({
      updateLatency: acc.updateLatency + curr.updateLatency,
      dataCollectionTime: acc.dataCollectionTime + curr.dataCollectionTime,
      renderTime: acc.renderTime + curr.renderTime,
      wsLatency: acc.wsLatency + curr.wsLatency,
      memoryUsage: acc.memoryUsage + curr.memoryUsage,
      cpuUsage: acc.cpuUsage + curr.cpuUsage,
    }), {
      updateLatency: 0,
      dataCollectionTime: 0,
      renderTime: 0,
      wsLatency: 0,
      memoryUsage: 0,
      cpuUsage: 0,
    });

    const count = this.history.length;
    return {
      updateLatency: avg.updateLatency / count,
      dataCollectionTime: avg.dataCollectionTime / count,
      renderTime: avg.renderTime / count,
      wsLatency: avg.wsLatency / count,
      memoryUsage: avg.memoryUsage / count,
      cpuUsage: avg.cpuUsage / count,
    };
  }
}

// Factory function for creating Ultimate Statusline Manager
export function createUltimateStatusline(config?: Partial<StatuslineConfig>): UltimateStatuslineManager {
  return new UltimateStatuslineManager(config);
}

// Export singleton instance for global use
export const ultimateStatusline = new UltimateStatuslineManager();

// CLI interface for terminal usage
export async function startStatuslineCLI() {
  const statusline = createUltimateStatusline({
    updateInterval: 100,
    enableWebSocket: true,
    enablePerformanceMetrics: true,
  });

  await statusline.start();

  console.log('🎯 Ultimate Statusline CLI started!');
  console.log('📊 Real-time updates every 100ms');
  console.log('🌐 WebSocket server on port 8087');
  console.log('📱 Dashboard integration enabled');
  console.log('');
  console.log('Attribution:');
  console.log('  - Powerline: @Owloops/claude-powerline');
  console.log('  - Dev Stack: Monitoring by Zach');
  console.log('  - Integration: Ultimate Statusline v3.0');
  console.log('');

  // Display updates in CLI
  statusline.on('update', (data) => {
    console.clear();
    console.log('🚀 Ultimate Statusline - Live Updates');
    console.log('=====================================');
    console.log('');
    console.log(statusline.formatForTerminal(data));
    console.log('');
    console.log(`⚡ Performance: ${data.performance.updateLatency}ms | 📡 Clients: ${statusline.getConnectionStats().connectedClients}`);
    console.log(`🔄 Update ID: ${data.updateId}`);
  });

  // Handle shutdown gracefully
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down Ultimate Statusline...');
    statusline.stop();
    process.exit(0);
  });

  return statusline;
}

// Export all types for TypeScript consumers
export type { 
  UltimateStatuslineData, 
  PowerlineData, 
  DevStackMetrics, 
  PerformanceMetrics,
  StatuslineConfig 
};

// CLI entry point for direct execution
if (require.main === module) {
  startStatuslineCLI().catch(console.error);
}