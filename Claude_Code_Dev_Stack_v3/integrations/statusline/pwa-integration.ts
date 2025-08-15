/**
 * PWA Integration for Dev Stack Statusline
 * Connects the Claude Powerline statusline with the PWA's statusline component
 */

import { PowerlineRenderer } from "./src/powerline";
import { loadConfigFromCLI } from "./src/config/loader";
import type { ClaudeHookData } from "./src/index";

export interface StatuslineData {
  segments: StatuslineSegment[];
  theme: string;
  timestamp: Date;
}

export interface StatuslineSegment {
  type: string;
  text: string;
  bgColor: string;
  fgColor: string;
  status?: "idle" | "active" | "error";
  data?: any;
}

export class DevStackStatuslineIntegration {
  private renderer: PowerlineRenderer;
  private config: any;

  constructor(configPath?: string, projectDir?: string) {
    // Load configuration with Dev Stack defaults
    const configArgs = configPath ? [`--config=${configPath}`] : [];
    this.config = loadConfigFromCLI(configArgs, projectDir);
    this.renderer = new PowerlineRenderer(this.config);
  }

  /**
   * Generate statusline for PWA display
   */
  async generateForPWA(hookData: ClaudeHookData): Promise<StatuslineData> {
    try {
      // Get the raw statusline from powerline renderer
      const rawStatusline = await this.renderer.generateStatusline(hookData);
      
      // Parse the statusline into structured data for PWA
      const segments = this.parseStatuslineToSegments(rawStatusline);
      
      return {
        segments,
        theme: this.config.theme || "dark",
        timestamp: new Date()
      };
    } catch (error) {
      console.error("Error generating statusline for PWA:", error);
      return {
        segments: [{
          type: "error",
          text: "Statusline Error",
          bgColor: "#dc2626",
          fgColor: "#ffffff",
          status: "error"
        }],
        theme: this.config.theme || "dark",
        timestamp: new Date()
      };
    }
  }

  /**
   * Generate statusline for terminal display
   */
  async generateForTerminal(hookData: ClaudeHookData): Promise<string> {
    return await this.renderer.generateStatusline(hookData);
  }

  /**
   * Get current Dev Stack metrics
   */
  async getDevStackMetrics(projectDir?: string): Promise<{
    agents: { active: number; total: number; status: string };
    tasks: { active: number; completed: number; total: number; status: string };
    hooks: { active: number; total: number; errors: number; status: string };
    audio: { enabled: boolean; volume: number; status: string };
  }> {
    try {
      // Import our monitors dynamically to get current status
      const { AgentMonitor } = await import("./src/segments/agent-monitor");
      const { TaskTracker } = await import("./src/segments/task-tracker");
      const { HookStatusMonitor } = await import("./src/segments/hook-status");
      const { AudioNotificationMonitor } = await import("./src/segments/audio-notifications");

      const agentMonitor = new AgentMonitor(projectDir);
      const taskTracker = new TaskTracker(projectDir);
      const hookMonitor = new HookStatusMonitor(projectDir);
      const audioMonitor = new AudioNotificationMonitor(projectDir);

      const [agentInfo, taskInfo, hookInfo, audioInfo] = await Promise.all([
        agentMonitor.getAgentInfo(),
        taskTracker.getTaskInfo(),
        hookMonitor.getHookInfo(),
        audioMonitor.getAudioInfo()
      ]);

      return {
        agents: {
          active: agentInfo.activeAgents,
          total: agentInfo.totalAgents,
          status: agentInfo.status
        },
        tasks: {
          active: taskInfo.activeTasks,
          completed: taskInfo.completedTasks,
          total: taskInfo.totalTasks,
          status: taskInfo.status
        },
        hooks: {
          active: hookInfo.activeHooks,
          total: hookInfo.totalHooks,
          errors: hookInfo.errorCount,
          status: hookInfo.status
        },
        audio: {
          enabled: audioInfo.isEnabled,
          volume: audioInfo.volume,
          status: audioInfo.status
        }
      };
    } catch (error) {
      console.error("Error getting Dev Stack metrics:", error);
      return {
        agents: { active: 0, total: 28, status: "error" },
        tasks: { active: 0, completed: 0, total: 0, status: "error" },
        hooks: { active: 0, total: 28, errors: 0, status: "error" },
        audio: { enabled: false, volume: 0, status: "error" }
      };
    }
  }

  private parseStatuslineToSegments(rawStatusline: string): StatuslineSegment[] {
    // This is a simplified parser - in a real implementation,
    // you'd want to parse the ANSI codes and extract segment information
    const lines = rawStatusline.split('\n');
    const segments: StatuslineSegment[] = [];

    lines.forEach((line, index) => {
      if (line.trim()) {
        // Remove ANSI codes for text extraction (simplified)
        const cleanText = line.replace(/\x1b\[[0-9;]*m/g, '');
        
        segments.push({
          type: `line_${index}`,
          text: cleanText,
          bgColor: "#2d2d2d", // Default background
          fgColor: "#ffffff", // Default foreground
          status: "active"
        });
      }
    });

    return segments;
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<any>) {
    this.config = { ...this.config, ...newConfig };
    this.renderer = new PowerlineRenderer(this.config);
  }

  /**
   * Get current configuration
   */
  getConfig() {
    return this.config;
  }
}

// Export a factory function for easy instantiation
export function createDevStackStatusline(configPath?: string, projectDir?: string): DevStackStatuslineIntegration {
  return new DevStackStatuslineIntegration(configPath, projectDir);
}

// Export for use in PWA
export default DevStackStatuslineIntegration;