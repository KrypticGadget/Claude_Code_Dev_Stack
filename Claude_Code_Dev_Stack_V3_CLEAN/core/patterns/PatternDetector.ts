import * as fs from 'fs';
import * as path from 'path';

export interface PatternMatch {
  category: string;
  pattern: string;
  match: string;
  weight: number;
  source: 'code' | 'terminal';
}

export type QualityLevel = 'EXCELLENT' | 'GOOD' | 'ACCEPTABLE' | 'POOR' | 'CRITICAL';

export interface DetectionResult {
  patterns: PatternMatch[];
  severityScore: number;
  qualityLevel: QualityLevel;
  hasDirectRefusal: boolean;
  hasEducationalDeflection: boolean;
  terminalPatterns: PatternMatch[];
  codePatterns: PatternMatch[];
}

interface PatternConfig {
  terminal: Record<string, string[]>;
  code: Record<string, string[]>;
  weights: Record<string, number>;
}

export class PatternDetector {
  private patternConfig: PatternConfig;
  private terminalPatterns: Record<string, RegExp[]>;
  private codePatterns: Record<string, RegExp[]>;
  
  constructor() {
    this.patternConfig = this.loadPatterns();
    this.terminalPatterns = this.createRegexPatterns('terminal');
    this.codePatterns = this.createRegexPatterns('code');
  }
  
  private loadPatterns(): PatternConfig {
    try {
      const configPath = path.join(__dirname, '..', 'config', 'patterns.json');
      const configData = fs.readFileSync(configPath, 'utf8');
      return JSON.parse(configData);
    } catch (error) {
      console.error('Failed to load pattern configuration:', error);
      return { 
        terminal: {
          DIRECT_REFUSAL: ['I cannot generate code for you'],
          EDUCATIONAL_POSITIONING: ['this will help you learn']
        }, 
        code: {
          SECURITY_ISSUES: ['eval\\s*\\('],
          TYPESCRIPT_BAILOUTS: [':\\s*any']
        }, 
        weights: {
          DIRECT_REFUSAL: 20,
          EDUCATIONAL_POSITIONING: 15,
          SECURITY_ISSUES: 25,
          TYPESCRIPT_BAILOUTS: 15
        }
      };
    }
  }
  
  private createRegexPatterns(category: 'terminal' | 'code'): Record<string, RegExp[]> {
    const patterns: Record<string, RegExp[]> = {};
    const categoryPatterns = this.patternConfig[category];
    
    for (const [key, stringPatterns] of Object.entries(categoryPatterns)) {
      patterns[key] = stringPatterns.map(pattern => new RegExp(pattern, 'i'));
    }
    
    return patterns;
  }

  public analyzeText(text: string): DetectionResult {
    const allPatterns: PatternMatch[] = [];
    
    // Analyze terminal patterns
    for (const [category, regexArray] of Object.entries(this.terminalPatterns)) {
      for (const regex of regexArray) {
        const match = text.match(regex);
        if (match) {
          allPatterns.push({
            category,
            pattern: regex.source,
            match: match[0],
            weight: this.patternConfig.weights[category] || 1,
            source: 'terminal'
          });
        }
      }
    }
    
    // Analyze code patterns
    for (const [category, regexArray] of Object.entries(this.codePatterns)) {
      for (const regex of regexArray) {
        const match = text.match(regex);
        if (match) {
          allPatterns.push({
            category,
            pattern: regex.source,
            match: match[0],
            weight: this.patternConfig.weights[category] || 1,
            source: 'code'
          });
        }
      }
    }

    return this.buildDetectionResult(allPatterns);
  }

  public analyzeCode(code: string): DetectionResult {
    const codePatterns: PatternMatch[] = [];
    
    for (const [category, regexArray] of Object.entries(this.codePatterns)) {
      for (const regex of regexArray) {
        const match = code.match(regex);
        if (match) {
          codePatterns.push({
            category,
            pattern: regex.source,
            match: match[0],
            weight: this.patternConfig.weights[category] || 1,
            source: 'code'
          });
        }
      }
    }

    return this.buildDetectionResult(codePatterns);
  }

  private buildDetectionResult(patterns: PatternMatch[]): DetectionResult {
    const severityScore = patterns.reduce((sum, p) => sum + p.weight, 0);
    
    const terminalPatterns = patterns.filter(p => p.source === 'terminal');
    const codePatterns = patterns.filter(p => p.source === 'code');
    
    const hasDirectRefusal = terminalPatterns.some(p => p.category === 'DIRECT_REFUSAL');
    const hasEducationalDeflection = terminalPatterns.some(p => 
      p.category === 'EDUCATIONAL_POSITIONING'
    );
    
    let qualityLevel: DetectionResult['qualityLevel'];
    if (severityScore >= 50) {
      qualityLevel = 'CRITICAL';
    } else if (severityScore >= 30) {
      qualityLevel = 'POOR';
    } else if (severityScore >= 15) {
      qualityLevel = 'ACCEPTABLE';
    } else if (severityScore >= 5) {
      qualityLevel = 'GOOD';
    } else {
      qualityLevel = 'EXCELLENT';
    }

    return {
      patterns,
      severityScore,
      qualityLevel,
      hasDirectRefusal,
      hasEducationalDeflection,
      terminalPatterns,
      codePatterns
    };
  }
}