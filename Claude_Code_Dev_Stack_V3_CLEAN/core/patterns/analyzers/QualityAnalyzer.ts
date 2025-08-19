import * as vscode from 'vscode';
import { DetectionResult } from '../PatternDetector';
import { FileAnalysis, QualityIssue, QualityIssueReport } from '../types/common';

export class QualityAnalyzer {
  
  public generateQualityReport(analysis: FileAnalysis): QualityIssueReport {
    const fileName = analysis.filePath.split('/').pop() || 'Unknown';
    const issues = this.extractDetailedIssues(analysis);
    
    const criticalCount = issues.filter(i => i.severity === 'CRITICAL').length;
    const highCount = issues.filter(i => i.severity === 'HIGH').length;
    
    return {
      file: fileName,
      totalIssues: issues.length,
      criticalCount,
      highCount,
      issues,
      aiInstruction: this.buildAIInstruction(issues, fileName)
    };
  }

  public extractDetailedIssues(analysis: FileAnalysis): QualityIssue[] {
    const issues: QualityIssue[] = [];
    const content = vscode.window.activeTextEditor?.document.getText() || '';
    const lines = content.split('\n');
    
    analysis.detectionResult.patterns.forEach(pattern => {
      const lineIndex = lines.findIndex(line => line.includes(pattern.match));
      const line = lineIndex >= 0 ? lineIndex + 1 : 1;
      const column = lineIndex >= 0 ? lines[lineIndex]!.indexOf(pattern.match) + 1 : 1;
      
      const issue = this.createIssueFromPattern(pattern.category, pattern.match, line, column);
      issues.push(issue);
    });
    
    return issues;
  }

  private createIssueFromPattern(category: string, match: string, line: number, column: number): QualityIssue {
    const issueStrategies: Record<string, () => QualityIssue> = {
      'SECURITY_ISSUES': () => ({
        line, column,
        category: 'SECURITY',
        severity: 'CRITICAL',
        pattern: match,
        problem: 'Security vulnerability detected - code execution risk',
        instruction: 'Replace with secure alternative that validates and sanitizes input',
        example: {
          current: match,
          suggested: match.includes('eval') ? 'JSON.parse(validatedInput)' : 'Use parameterized queries'
        }
      }),
      
      'TYPESCRIPT_BAILOUTS': () => ({
        line, column,
        category: 'TYPE_SAFETY',
        severity: 'HIGH',
        pattern: match,
        problem: 'Type safety violation - bypasses TypeScript checking',
        instruction: 'Define proper interface and use specific typing instead of any',
        example: {
          current: match,
          suggested: 'Define: interface ApiResponse { data: T[]; status: string; }'
        }
      }),
      
      'PRODUCTION_ISSUES': () => ({
        line, column,
        category: 'PRODUCTION',
        severity: 'MEDIUM',
        pattern: match,
        problem: 'Debug code in production - not suitable for deployment',
        instruction: 'Remove debug statements and replace with proper logging',
        example: {
          current: match,
          suggested: match.includes('console') ? 'logger.debug(...)' : 'Remove debugger statements'
        }
      }),
      
      'CODE_QUALITY_ISSUES': () => ({
        line, column,
        category: 'IMPLEMENTATION',
        severity: 'MEDIUM',
        pattern: match,
        problem: 'Incomplete implementation - placeholder code detected',
        instruction: 'Complete the implementation with proper business logic and error handling',
        example: {
          current: match,
          suggested: 'Implement full functionality with try/catch error handling'
        }
      })
    };

    const strategy = issueStrategies[category];
    if (strategy) {
      return strategy();
    }

    return {
      line, column,
      category: 'GENERAL',
      severity: 'LOW',
      pattern: match,
      problem: 'Code quality issue detected',
      instruction: 'Review and improve following best practices'
    };
  }

  public buildAIInstruction(issues: QualityIssue[], fileName: string): string {
    const critical = issues.filter(i => i.severity === 'CRITICAL');
    const high = issues.filter(i => i.severity === 'HIGH');
    const medium = issues.filter(i => i.severity === 'MEDIUM');
    
    let instruction = `CODE QUALITY ISSUES DETECTED in ${fileName}:\n\n`;
    
    instruction += this.formatIssueSection('🚨 CRITICAL SECURITY ISSUES', critical, true);
    instruction += this.formatIssueSection('⚠️ HIGH PRIORITY ISSUES', high, false);
    instruction += this.formatIssueSection('📋 MEDIUM PRIORITY ISSUES', medium, false);
    
    instruction += 'Please rewrite the affected sections with production-ready code that follows security and quality best practices.';
    
    return instruction;
  }

  private formatIssueSection(title: string, issues: QualityIssue[], includeDetails: boolean): string {
    if (issues.length === 0) return '';
    
    let section = `${title} (${issues.length}):\n`;
    
    issues.forEach(issue => {
      section += `Line ${issue.line}: ${issue.problem}\n`;
      
      if (includeDetails) {
        section += `Required: ${issue.instruction}\n`;
        if (issue.example) {
          section += `Current: ${issue.example.current}\n`;
          section += `Suggested: ${issue.example.suggested}\n`;
        }
      } else {
        section += `${issue.category} - ${issue.instruction}\n`;
      }
    });
    
    return section + '\n';
  }
}