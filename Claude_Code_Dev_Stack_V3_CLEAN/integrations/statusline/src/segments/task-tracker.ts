/**
 * Task Tracker Segment for Claude Code Dev Stack
 * Tracks active tasks and their completion status
 */

import fs from "node:fs";
import path from "node:path";

export interface TaskInfo {
  activeTasks: number;
  completedTasks: number;
  totalTasks: number;
  currentTask: string | null;
  lastUpdate: Date | null;
  status: "idle" | "active" | "error";
}

export interface TaskSegmentConfig {
  enabled: boolean;
  showCount?: boolean;
  showCurrent?: boolean;
  showProgress?: boolean;
  maxTaskLength?: number;
}

export class TaskTracker {
  private readonly taskDataPath: string;

  constructor(projectDir?: string) {
    // Look for task data in the project directory or current working directory
    const baseDir = projectDir || process.cwd();
    this.taskDataPath = path.join(baseDir, ".claude", "tasks");
  }

  async getTaskInfo(): Promise<TaskInfo> {
    try {
      // Check if tasks directory exists
      if (!fs.existsSync(this.taskDataPath)) {
        return {
          activeTasks: 0,
          completedTasks: 0,
          totalTasks: 0,
          currentTask: null,
          lastUpdate: null,
          status: "idle"
        };
      }

      // Look for task files
      const taskFiles = fs.readdirSync(this.taskDataPath)
        .filter(file => file.endsWith('.json'));

      let activeTasks = 0;
      let completedTasks = 0;
      let currentTask: string | null = null;
      let lastUpdate: Date | null = null;
      let hasError = false;

      for (const file of taskFiles) {
        try {
          const filePath = path.join(this.taskDataPath, file);
          const stats = fs.statSync(filePath);
          const taskData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

          // Track latest update
          if (!lastUpdate || stats.mtime > lastUpdate) {
            lastUpdate = stats.mtime;
          }

          // Count tasks by status
          if (taskData.status === 'active' || taskData.status === 'in_progress') {
            activeTasks++;
            
            // Get the most recent active task
            if (!currentTask || stats.mtime > lastUpdate) {
              currentTask = taskData.title || taskData.name || path.basename(file, '.json');
            }
          } else if (taskData.status === 'completed' || taskData.status === 'done') {
            completedTasks++;
          }

          // Check for errors
          if (taskData.status === 'error' || taskData.status === 'failed') {
            hasError = true;
          }
        } catch (error) {
          // Skip invalid task files
          hasError = true;
        }
      }

      const totalTasks = activeTasks + completedTasks;

      return {
        activeTasks,
        completedTasks,
        totalTasks,
        currentTask,
        lastUpdate,
        status: hasError ? "error" : (activeTasks > 0 ? "active" : "idle")
      };
    } catch (error) {
      return {
        activeTasks: 0,
        completedTasks: 0,
        totalTasks: 0,
        currentTask: null,
        lastUpdate: null,
        status: "error"
      };
    }
  }

  formatTaskInfo(taskInfo: TaskInfo, config: TaskSegmentConfig): string {
    const parts: string[] = [];

    // Add task count
    if (config.showCount !== false) {
      if (taskInfo.totalTasks > 0) {
        parts.push(`${taskInfo.activeTasks}/${taskInfo.totalTasks}`);
      } else {
        parts.push("0");
      }
    }

    // Add progress indicator
    if (config.showProgress && taskInfo.totalTasks > 0) {
      const percentage = Math.round((taskInfo.completedTasks / taskInfo.totalTasks) * 100);
      parts.push(`${percentage}%`);
    }

    // Add current task
    if (config.showCurrent && taskInfo.currentTask) {
      const maxLength = config.maxTaskLength || 20;
      let taskName = taskInfo.currentTask;
      if (taskName.length > maxLength) {
        taskName = taskName.substring(0, maxLength - 3) + "...";
      }
      parts.push(`[${taskName}]`);
    }

    // Add status indicator
    const statusSymbol = {
      idle: "⏸",
      active: "▶",
      error: "⚠"
    }[taskInfo.status];
    parts.push(statusSymbol);

    return parts.join(" ");
  }

  // Helper method to get task completion percentage
  getCompletionPercentage(taskInfo: TaskInfo): number {
    if (taskInfo.totalTasks === 0) return 0;
    return Math.round((taskInfo.completedTasks / taskInfo.totalTasks) * 100);
  }
}