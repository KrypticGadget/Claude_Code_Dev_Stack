/**
 * Agent Monitor Segment for Claude Code Dev Stack
 * Tracks active agents (0-28) and their status
 */

import fs from "node:fs";
import path from "node:path";

export interface AgentInfo {
  activeAgents: number;
  totalAgents: number;
  activeAgentList: string[];
  lastActivity: Date | null;
  status: "idle" | "active" | "error";
}

export interface AgentSegmentConfig {
  enabled: boolean;
  showCount?: boolean;
  showList?: boolean;
  showStatus?: boolean;
  maxDisplay?: number;
}

export class AgentMonitor {
  private readonly maxAgents = 28;
  private readonly agentDataPath: string;

  constructor(projectDir?: string) {
    // Look for agent data in the project directory or current working directory
    const baseDir = projectDir || process.cwd();
    this.agentDataPath = path.join(baseDir, ".claude", "agents");
  }

  async getAgentInfo(): Promise<AgentInfo> {
    try {
      // Check if agents directory exists
      if (!fs.existsSync(this.agentDataPath)) {
        return {
          activeAgents: 0,
          totalAgents: this.maxAgents,
          activeAgentList: [],
          lastActivity: null,
          status: "idle"
        };
      }

      // Read agent status files
      const agentFiles = fs.readdirSync(this.agentDataPath)
        .filter(file => file.endsWith('.json'));

      const activeAgents: string[] = [];
      let lastActivity: Date | null = null;
      let hasError = false;

      for (const file of agentFiles) {
        try {
          const filePath = path.join(this.agentDataPath, file);
          const stats = fs.statSync(filePath);
          const agentData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

          // Check if agent is active (modified within last 5 minutes)
          const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
          if (stats.mtime > fiveMinutesAgo) {
            const agentName = path.basename(file, '.json');
            activeAgents.push(agentName);

            // Track latest activity
            if (!lastActivity || stats.mtime > lastActivity) {
              lastActivity = stats.mtime;
            }
          }

          // Check for error status
          if (agentData.status === 'error') {
            hasError = true;
          }
        } catch (error) {
          // Skip invalid agent files
          hasError = true;
        }
      }

      return {
        activeAgents: activeAgents.length,
        totalAgents: this.maxAgents,
        activeAgentList: activeAgents,
        lastActivity,
        status: hasError ? "error" : (activeAgents.length > 0 ? "active" : "idle")
      };
    } catch (error) {
      return {
        activeAgents: 0,
        totalAgents: this.maxAgents,
        activeAgentList: [],
        lastActivity: null,
        status: "error"
      };
    }
  }

  formatAgentInfo(agentInfo: AgentInfo, config: AgentSegmentConfig): string {
    const parts: string[] = [];

    // Add agent count
    if (config.showCount !== false) {
      parts.push(`${agentInfo.activeAgents}/${agentInfo.totalAgents}`);
    }

    // Add status indicator
    if (config.showStatus !== false) {
      const statusSymbol = {
        idle: "○",
        active: "●", 
        error: "⚠"
      }[agentInfo.status];
      parts.push(statusSymbol);
    }

    // Add active agent list (limited)
    if (config.showList && agentInfo.activeAgentList.length > 0) {
      const maxDisplay = config.maxDisplay || 3;
      const displayList = agentInfo.activeAgentList.slice(0, maxDisplay);
      if (agentInfo.activeAgentList.length > maxDisplay) {
        displayList.push(`+${agentInfo.activeAgentList.length - maxDisplay}`);
      }
      parts.push(`[${displayList.join(",")}]`);
    }

    return parts.join(" ");
  }
}