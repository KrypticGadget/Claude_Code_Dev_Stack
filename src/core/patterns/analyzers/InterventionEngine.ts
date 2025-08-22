import * as vscode from 'vscode';
import { FileAnalysis, QualityIssueReport } from '../types/common';
import { QualityAnalyzer } from './QualityAnalyzer';

export class InterventionEngine {
  private qualityAnalyzer: QualityAnalyzer;
  private outputChannel: vscode.OutputChannel;
  private aiInterventionActive: boolean = false;
  private lastAIInterventionTime: number = 0;

  constructor(outputChannel: vscode.OutputChannel) {
    this.outputChannel = outputChannel;
    this.qualityAnalyzer = new QualityAnalyzer();
  }

  public shouldTriggerAIIntervention(analysis: FileAnalysis): boolean {
    if (this.aiInterventionActive) {
      return false;
    }

    const cooldownPeriod = 30000; // 30 seconds
    if (Date.now() - this.lastAIInterventionTime < cooldownPeriod) {
      return false;
    }
    
    if (!vscode.window.activeTerminal) {
      return false;
    }
    
    return analysis.detectionResult.qualityLevel === 'CRITICAL';
  }

  public async performAutomaticAIIntervention(analysis: FileAnalysis): Promise<void> {
    this.aiInterventionActive = true;
    this.lastAIInterventionTime = Date.now();
    
    try {
      const report = this.qualityAnalyzer.generateQualityReport(analysis);
      await this.sendAICorrection(report);
      
      setTimeout(() => {
        this.aiInterventionActive = false;
      }, 5000);
    } catch (error) {
      this.outputChannel.appendLine(`❌ AI intervention failed: ${error}`);
      this.aiInterventionActive = false;
    }
  }

  public async requestUserApprovedAIFix(analysis: FileAnalysis): Promise<void> {
    const report = this.qualityAnalyzer.generateQualityReport(analysis);
    
    const action = await vscode.window.showWarningMessage(
      `🔍 ${report.totalIssues} quality issues found in ${report.file}`,
      'Request AI Fix',
      'Show Details',
      'Ignore'
    );
    
    switch (action) {
      case 'Request AI Fix':
        await this.sendAICorrection(report);
        break;
        
      case 'Show Details':
        await this.showDetailedQualityReport(report);
        break;
        
      default:
        this.outputChannel.appendLine(`⏭️ User ignored ${report.totalIssues} quality issues`);
    }
  }

  public async showCriticalIssuesBlock(report: QualityIssueReport): Promise<void> {
    const message = `🚨 CRITICAL CODE ISSUES (${report.criticalCount}) - Save blocked until fixed`;
    
    const action = await vscode.window.showErrorMessage(
      message,
      { modal: true },
      'Request AI Fix',
      'Show Details'
    );
    
    if (action === 'Request AI Fix') {
      await this.sendAICorrection(report);
    } else if (action === 'Show Details') {
      await this.showDetailedQualityReport(report);
    }
  }

  private async sendAICorrection(report: QualityIssueReport): Promise<void> {
    this.outputChannel.appendLine(`🤖 SENDING AI CORRECTION REQUEST for ${report.file}`);
    this.outputChannel.appendLine(report.aiInstruction);
    
    const terminal = vscode.window.activeTerminal;
    if (terminal) {
      terminal.sendText(`# AI Quality Issue Report for ${report.file}`, true);
      terminal.sendText(`echo "${report.aiInstruction.replace(/"/g, '\\"')}"`, true);
      terminal.show();
    }
    
    vscode.window.showInformationMessage(`🤖 AI correction requested for ${report.totalIssues} issues`);
  }

  private async showDetailedQualityReport(report: QualityIssueReport): Promise<void> {
    const panel = vscode.window.createWebviewPanel(
      'qualityReport',
      `Quality Report: ${report.file}`,
      vscode.ViewColumn.Beside,
      { enableScripts: false }
    );

    panel.webview.html = this.generateDetailedReportMarkdown(report);
  }

  private generateDetailedReportMarkdown(report: QualityIssueReport): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
        .critical { background: #ffe6e6; border-left: 4px solid #ff4444; }
        .high { background: #fff4e6; border-left: 4px solid #ff8800; }
        .medium { background: #e6f3ff; border-left: 4px solid #0088ff; }
        .issue { margin: 10px 0; padding: 15px; border-radius: 5px; }
        .line { font-weight: bold; color: #666; }
    </style>
</head>
<body>
    <h1>🔍 Quality Report: ${report.file}</h1>
    <p><strong>Total Issues:</strong> ${report.totalIssues} (Critical: ${report.criticalCount}, High: ${report.highCount})</p>
    
    ${report.issues.map(issue => `
        <div class="issue ${issue.severity.toLowerCase()}">
            <div class="line">Line ${issue.line}: ${issue.category}</div>
            <p><strong>Problem:</strong> ${issue.problem}</p>
            <p><strong>Solution:</strong> ${issue.instruction}</p>
            ${issue.example ? `
                <p><strong>Current:</strong> <code>${issue.example.current}</code></p>
                <p><strong>Suggested:</strong> <code>${issue.example.suggested}</code></p>
            ` : ''}
        </div>
    `).join('')}
</body>
</html>`;
  }
}