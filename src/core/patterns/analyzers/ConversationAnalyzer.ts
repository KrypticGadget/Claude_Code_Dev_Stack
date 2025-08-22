import * as fs from 'fs';
import * as path from 'path';

interface TodoBailoutAnalysis {
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  bailoutPatterns: string[];
  score: number;
}

interface ConversationPatterns {
  implementationAvoidance: {
    HIGH: string[];
    MEDIUM: string[];
    LOW: string[];
  };
  weights: {
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  interventionThreshold: number;
}

export class ConversationAnalyzer {
  private patterns: ConversationPatterns;
  
  constructor() {
    this.patterns = this.loadPatterns();
  }
  
  private loadPatterns(): ConversationPatterns {
    try {
      const configPath = path.join(__dirname, '..', 'config', 'conversation-patterns.json');
      const configData = fs.readFileSync(configPath, 'utf8');
      return JSON.parse(configData);
    } catch (error) {
      console.error('Failed to load conversation patterns:', error);
      return {
        implementationAvoidance: {
          HIGH: ['analyze existing', 'create mock', 'for now'],
          MEDIUM: ['add proper error handling', 'enhance for production'],
          LOW: ['basic implementation', 'simple approach']
        },
        weights: { HIGH: 15, MEDIUM: 10, LOW: 5 },
        interventionThreshold: 25
      };
    }
  }

  public analyzeTodoBailoutPatterns(todoContent: string): TodoBailoutAnalysis {
    const content = todoContent.toLowerCase();
    let score = 0;
    const detectedPatterns: string[] = [];
    
    // Check each severity level
    for (const [severity, patterns] of Object.entries(this.patterns.implementationAvoidance)) {
      for (const pattern of patterns) {
        if (content.includes(pattern.toLowerCase())) {
          score += this.patterns.weights[severity as keyof typeof this.patterns.weights];
          detectedPatterns.push(`${severity}: ${pattern}`);
        }
      }
    }
    
    let finalSeverity: TodoBailoutAnalysis['severity'];
    if (score >= this.patterns.interventionThreshold) {
      finalSeverity = 'HIGH';
    } else if (score >= 15) {
      finalSeverity = 'MEDIUM';
    } else {
      finalSeverity = 'LOW';
    }
    
    return {
      severity: finalSeverity,
      bailoutPatterns: detectedPatterns,
      score
    };
  }

  public shouldTriggerIntervention(analysis: TodoBailoutAnalysis): boolean {
    return analysis.severity === 'HIGH' && analysis.score >= this.patterns.interventionThreshold;
  }
}