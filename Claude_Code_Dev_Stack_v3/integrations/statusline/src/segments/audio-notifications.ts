/**
 * Audio Notifications Segment for Claude Code Dev Stack
 * Tracks audio notification system status and recent activity
 */

import fs from "node:fs";
import path from "node:path";

export interface AudioInfo {
  isEnabled: boolean;
  volume: number;
  lastNotification: Date | null;
  notificationCount: number;
  queueSize: number;
  status: "muted" | "active" | "error";
}

export interface AudioSegmentConfig {
  enabled: boolean;
  showVolume?: boolean;
  showQueue?: boolean;
  showCount?: boolean;
  showLastActivity?: boolean;
}

export class AudioNotificationMonitor {
  private readonly audioDataPath: string;
  private readonly audioConfigPath: string;

  constructor(projectDir?: string) {
    // Look for audio data in the project directory or current working directory
    const baseDir = projectDir || process.cwd();
    this.audioDataPath = path.join(baseDir, ".claude", "audio");
    this.audioConfigPath = path.join(this.audioDataPath, "config.json");
  }

  async getAudioInfo(): Promise<AudioInfo> {
    try {
      // Default values
      let isEnabled = false;
      let volume = 50;
      let lastNotification: Date | null = null;
      let notificationCount = 0;
      let queueSize = 0;
      let status: "muted" | "active" | "error" = "muted";

      // Check if audio directory exists
      if (!fs.existsSync(this.audioDataPath)) {
        return {
          isEnabled,
          volume,
          lastNotification,
          notificationCount,
          queueSize,
          status
        };
      }

      // Read audio configuration
      if (fs.existsSync(this.audioConfigPath)) {
        try {
          const configData = JSON.parse(fs.readFileSync(this.audioConfigPath, 'utf8'));
          isEnabled = configData.enabled || false;
          volume = configData.volume || 50;
          
          if (configData.error) {
            status = "error";
          } else if (isEnabled && volume > 0) {
            status = "active";
          } else {
            status = "muted";
          }
        } catch (error) {
          status = "error";
        }
      }

      // Check for recent notifications
      const notificationLogPath = path.join(this.audioDataPath, "notifications.log");
      if (fs.existsSync(notificationLogPath)) {
        try {
          const logContent = fs.readFileSync(notificationLogPath, 'utf8');
          const lines = logContent.trim().split('\n').filter(line => line.length > 0);
          
          notificationCount = lines.length;
          
          // Get last notification time
          if (lines.length > 0) {
            const lastLine = lines[lines.length - 1];
            const timestampMatch = lastLine.match(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
            if (timestampMatch) {
              lastNotification = new Date(timestampMatch[1]);
            }
          }
        } catch (error) {
          // Failed to read log, but not critical
        }
      }

      // Check audio queue
      const queuePath = path.join(this.audioDataPath, "queue.json");
      if (fs.existsSync(queuePath)) {
        try {
          const queueData = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
          queueSize = queueData.items ? queueData.items.length : 0;
        } catch (error) {
          // Failed to read queue, not critical
        }
      }

      return {
        isEnabled,
        volume,
        lastNotification,
        notificationCount,
        queueSize,
        status
      };
    } catch (error) {
      return {
        isEnabled: false,
        volume: 0,
        lastNotification: null,
        notificationCount: 0,
        queueSize: 0,
        status: "error"
      };
    }
  }

  formatAudioInfo(audioInfo: AudioInfo, config: AudioSegmentConfig): string {
    const parts: string[] = [];

    // Add status symbol
    const statusSymbol = {
      muted: "🔇",
      active: "🔊", 
      error: "⚠"
    }[audioInfo.status];
    parts.push(statusSymbol);

    // Add volume level
    if (config.showVolume && audioInfo.isEnabled) {
      parts.push(`${audioInfo.volume}%`);
    }

    // Add queue size
    if (config.showQueue && audioInfo.queueSize > 0) {
      parts.push(`Q:${audioInfo.queueSize}`);
    }

    // Add notification count (recent)
    if (config.showCount && audioInfo.notificationCount > 0) {
      // Only show count if there have been notifications today
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (audioInfo.lastNotification && audioInfo.lastNotification >= today) {
        parts.push(`${audioInfo.notificationCount}`);
      }
    }

    // Add last activity
    if (config.showLastActivity && audioInfo.lastNotification) {
      const now = new Date();
      const diffMinutes = Math.floor((now.getTime() - audioInfo.lastNotification.getTime()) / (1000 * 60));
      
      if (diffMinutes < 1) {
        parts.push("now");
      } else if (diffMinutes < 60) {
        parts.push(`${diffMinutes}m`);
      } else {
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) {
          parts.push(`${diffHours}h`);
        }
      }
    }

    return parts.join(" ");
  }

  // Helper method to get volume icon
  getVolumeIcon(volume: number): string {
    if (volume === 0) return "🔇";
    if (volume < 30) return "🔈";
    if (volume < 70) return "🔉";
    return "🔊";
  }

  // Helper method to check if audio system is healthy
  isHealthy(audioInfo: AudioInfo): boolean {
    return audioInfo.status !== "error";
  }
}