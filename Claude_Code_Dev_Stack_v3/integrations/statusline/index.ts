/**
 * Claude Code Dev Stack - Enhanced Statusline Integration
 * Built on Claude Powerline by @Owloops
 */

// Core integration exports
export { DevStackStatuslineIntegration, createDevStackStatusline } from './pwa-integration';
export { StatuslineService, createStatuslineService } from './statusline-service';

// Core statusline exports
export { PowerlineRenderer } from './src/powerline';
export { loadConfigFromCLI } from './src/config/loader';

// Dev Stack segment exports
export { AgentMonitor } from './src/segments/agent-monitor';
export { TaskTracker } from './src/segments/task-tracker';
export { HookStatusMonitor } from './src/segments/hook-status';
export { AudioNotificationMonitor } from './src/segments/audio-notifications';

// Type exports
export type { ClaudeHookData } from './src/index';
export type { StatuslineData, StatuslineSegment } from './pwa-integration';
export type { StatuslineServiceConfig } from './statusline-service';
export type {
  AgentInfo,
  AgentSegmentConfig,
  TaskInfo,
  TaskSegmentConfig,
  HookInfo,
  HookSegmentConfig,
  AudioInfo,
  AudioSegmentConfig
} from './src/segments/index';

// Theme exports
export { getTheme } from './src/themes';
export type { ColorTheme, SegmentColor, PowerlineColors } from './src/themes';

// Re-export original powerline types for compatibility
export type {
  PowerlineConfig,
  LineConfig,
  DisplayConfig,
  BudgetConfig
} from './src/config/loader';

export type {
  SegmentConfig,
  DirectorySegmentConfig,
  GitSegmentConfig,
  UsageSegmentConfig,
  TmuxSegmentConfig,
  ContextSegmentConfig,
  MetricsSegmentConfig,
  BlockSegmentConfig,
  TodaySegmentConfig,
  VersionSegmentConfig
} from './src/segments/renderer';

// Default export for main integration
export { DevStackStatuslineIntegration as default } from './pwa-integration';