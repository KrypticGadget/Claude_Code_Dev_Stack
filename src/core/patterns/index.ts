// AI Bailout Detection Patterns
// Extracted from AicodeGuard repository

// Core Pattern Detection
export { PatternDetector, PatternMatch, QualityLevel, DetectionResult } from './PatternDetector';

// Analyzers
export { ConversationAnalyzer } from './analyzers/ConversationAnalyzer';
export { InterventionEngine } from './analyzers/InterventionEngine';
export { QualityAnalyzer } from './analyzers/QualityAnalyzer';

// Managers
export { ConfigManager, MonitoringMode, AggressivenessLevel, BailoutConfig, AggressivenessProfile } from './managers/ConfigManager';
export { NotificationManager, BailoutNotificationData } from './managers/NotificationManager';

// Types
export { 
  QualityLevel as QualityLevelType, 
  TriggerType, 
  InterventionLevel, 
  FileAnalysis, 
  QualityIssue, 
  QualityIssueReport 
} from './types/common';

// Pattern Configuration Files
// Located in ./config/patterns.json and ./config/conversation-patterns.json