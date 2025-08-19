import { DetectionResult, QualityLevel } from '../PatternDetector';

export { QualityLevel };

export type TriggerType = 'SAVE' | 'TYPE' | 'FOCUS' | 'MANUAL';
export type InterventionLevel = 'NONE' | 'WARNING' | 'SIGNAL_AI' | 'BLOCK';

export interface FileAnalysis {
  filePath: string;
  timestamp: number;
  detectionResult: DetectionResult;
  triggerType: TriggerType;
  interventionLevel: InterventionLevel;
}

export interface QualityIssue {
  line: number;
  column: number;
  category: 'SECURITY' | 'TYPE_SAFETY' | 'PRODUCTION' | 'IMPLEMENTATION' | 'GENERAL';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  pattern: string;
  problem: string;
  instruction: string;
  example?: {
    current: string;
    suggested: string;
  };
}

export interface QualityIssueReport {
  file: string;
  totalIssues: number;
  criticalCount: number;
  highCount: number;
  issues: QualityIssue[];
  aiInstruction: string;
}