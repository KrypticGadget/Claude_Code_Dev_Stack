/**
 * Hook Status Segment for Claude Code Dev Stack
 * Tracks hook status (0-28 hooks) and their activity
 */

import fs from "node:fs";
import path from "node:path";

export interface HookInfo {
  activeHooks: number;
  totalHooks: number;
  hookTypes: string[];
  lastTrigger: Date | null;
  errorCount: number;
  status: "idle" | "active" | "error";
}

export interface HookSegmentConfig {
  enabled: boolean;
  showCount?: boolean;
  showTypes?: boolean;
  showErrors?: boolean;
  showLastTrigger?: boolean;
  maxTypes?: number;
}

export class HookStatusMonitor {
  private readonly maxHooks = 28;
  private readonly hookDataPath: string;

  constructor(projectDir?: string) {
    // Look for hook data in the project directory or current working directory
    const baseDir = projectDir || process.cwd();
    this.hookDataPath = path.join(baseDir, ".claude", "hooks");
  }

  async getHookInfo(): Promise<HookInfo> {
    try {
      // Check if hooks directory exists
      if (!fs.existsSync(this.hookDataPath)) {
        return {
          activeHooks: 0,
          totalHooks: this.maxHooks,
          hookTypes: [],
          lastTrigger: null,
          errorCount: 0,
          status: "idle"
        };
      }

      // Read hook status files
      const hookFiles = fs.readdirSync(this.hookDataPath)
        .filter(file => file.endsWith('.json'));

      const activeHookTypes: string[] = [];
      let lastTrigger: Date | null = null;
      let errorCount = 0;
      let activeCount = 0;

      for (const file of hookFiles) {
        try {
          const filePath = path.join(this.hookDataPath, file);
          const stats = fs.statSync(filePath);
          const hookData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

          // Check if hook is active (triggered within last 10 minutes)
          const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);
          const isRecentlyActive = stats.mtime > tenMinutesAgo;

          if (isRecentlyActive) {
            activeCount++;
            
            // Track hook type
            const hookType = hookData.type || path.basename(file, '.json');
            if (!activeHookTypes.includes(hookType)) {
              activeHookTypes.push(hookType);
            }

            // Track latest trigger
            if (!lastTrigger || stats.mtime > lastTrigger) {
              lastTrigger = stats.mtime;
            }
          }

          // Count errors
          if (hookData.status === 'error' || hookData.error) {
            errorCount++;
          }
        } catch (error) {
          // Skip invalid hook files but count as error
          errorCount++;
        }
      }

      return {
        activeHooks: activeCount,
        totalHooks: this.maxHooks,
        hookTypes: activeHookTypes,
        lastTrigger,
        errorCount,
        status: errorCount > 0 ? "error" : (activeCount > 0 ? "active" : "idle")
      };
    } catch (error) {
      return {
        activeHooks: 0,
        totalHooks: this.maxHooks,
        hookTypes: [],
        lastTrigger: null,
        errorCount: 1,
        status: "error"
      };
    }
  }

  formatHookInfo(hookInfo: HookInfo, config: HookSegmentConfig): string {
    const parts: string[] = [];

    // Add hook count
    if (config.showCount !== false) {
      parts.push(`${hookInfo.activeHooks}/${hookInfo.totalHooks}`);
    }

    // Add hook types
    if (config.showTypes && hookInfo.hookTypes.length > 0) {
      const maxTypes = config.maxTypes || 2;
      const displayTypes = hookInfo.hookTypes.slice(0, maxTypes);
      if (hookInfo.hookTypes.length > maxTypes) {
        displayTypes.push(`+${hookInfo.hookTypes.length - maxTypes}`);
      }
      parts.push(`[${displayTypes.join(",")}]`);
    }

    // Add error count
    if (config.showErrors && hookInfo.errorCount > 0) {
      parts.push(`⚠${hookInfo.errorCount}`);
    }

    // Add last trigger time
    if (config.showLastTrigger && hookInfo.lastTrigger) {
      const now = new Date();
      const diffMinutes = Math.floor((now.getTime() - hookInfo.lastTrigger.getTime()) / (1000 * 60));
      if (diffMinutes < 1) {
        parts.push("now");
      } else if (diffMinutes < 60) {
        parts.push(`${diffMinutes}m`);
      } else {
        const diffHours = Math.floor(diffMinutes / 60);
        parts.push(`${diffHours}h`);
      }
    }

    // Add status indicator
    const statusSymbol = {
      idle: "○",
      active: "◉",
      error: "⚠"
    }[hookInfo.status];
    parts.push(statusSymbol);

    return parts.join(" ");
  }

  // Helper method to get hook activity level
  getActivityLevel(hookInfo: HookInfo): "low" | "medium" | "high" {
    const ratio = hookInfo.activeHooks / hookInfo.totalHooks;
    if (ratio > 0.7) return "high";
    if (ratio > 0.3) return "medium";
    return "low";
  }

  // Helper method to check if hooks are healthy
  isHealthy(hookInfo: HookInfo): boolean {
    return hookInfo.errorCount === 0 && hookInfo.status !== "error";
  }
}