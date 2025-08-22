import * as vscode from 'vscode';

export interface BailoutNotificationData {
  type: 'tool_bailout' | 'todo_bailout' | 'intervention_complete';
  patterns: string[];
  tool?: string;
  confidence?: string;
  severity?: string;
  description?: string;
  messageNum?: number;
}

export class NotificationManager {
  private static instance: NotificationManager;
  private notificationQueue: Array<{data: BailoutNotificationData, delay: number}> = [];
  private isProcessing: boolean = false;
  
  // Configuration
  private readonly NOTIFICATION_DELAYS = {
    intervention_complete: 1000,   // 1 second - Critical interventions (immediate feedback)
    tool_bailout: 3000,           // 3 seconds - Medium issues  
    todo_bailout: 5000            // 5 seconds - Low priority
  };
  
  private readonly NOTIFICATIONS_ENABLED = true; // Master switch - ENABLED for production
  
  public static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager();
    }
    return NotificationManager.instance;
  }
  
  public queueNotification(data: BailoutNotificationData): void {
    if (!this.NOTIFICATIONS_ENABLED) {
      console.log(`📢 NOTIFICATION DISABLED: ${data.type} - ${data.patterns.join(', ')}`);
      return;
    }
    
    const delay = this.NOTIFICATION_DELAYS[data.type] || 15000;
    this.notificationQueue.push({ data, delay });
    console.log(`📢 NOTIFICATION QUEUED: ${data.type} (delay: ${delay}ms)`);
    
    if (!this.isProcessing) {
      this.processQueue();
    }
  }
  
  private async processQueue(): Promise<void> {
    this.isProcessing = true;
    
    while (this.notificationQueue.length > 0) {
      const { data, delay } = this.notificationQueue.shift()!;
      
      await new Promise(resolve => {
        setTimeout(() => {
          this.showNotification(data);
          resolve(void 0);
        }, delay);
      });
    }
    
    this.isProcessing = false;
  }
  
  private showNotification(data: BailoutNotificationData): void {
    console.log(`📢 SHOWING NOTIFICATION: ${data.type}`);
    
    switch (data.type) {
      case 'intervention_complete':
        this.showInterventionComplete(data);
        break;
        
      case 'tool_bailout':
        this.showToolBailout(data);
        break;
        
      case 'todo_bailout':
        this.showTodoBailout(data);
        break;
    }
  }
  
  private showInterventionComplete(data: BailoutNotificationData): void {
    vscode.window.showInformationMessage(
      `🛡️ Quality Issue Addressed! Patterns: ${data.patterns.slice(0, 2).join(', ')}`,
      'Show Details'
    ).then(selection => {
      if (selection === 'Show Details') {
        vscode.window.showInformationMessage(
          `Quality Issue Details:\n\nDetected patterns: ${data.patterns.join(', ')}\n\nCorrective action taken: Interrupted AI and requested complete implementation.`
        );
      }
    });
  }
  
  private showToolBailout(data: BailoutNotificationData): void {
    const icon = data.severity === 'HIGH' || data.severity === 'CRITICAL' ? '🚨' : '⚠️';
    vscode.window.showWarningMessage(
      `${icon} Quality Issue! ${data.tool || 'Implementation gap'} detected`,
      'Show Details',
      'Quality Enforcement',
      'Ignore'
    ).then(selection => {
      if (selection === 'Show Details') {
        vscode.window.showInformationMessage(
          `Quality Issue Details:\n\nTool: ${data.tool}\nConfidence: ${data.confidence}\nSeverity: ${data.severity}\n\n${data.description}`
        );
      } else if (selection === 'Quality Enforcement') {
        vscode.commands.executeCommand('ai-code-guard.enforceQuality');
      }
    });
  }
  
  private showTodoBailout(data: BailoutNotificationData): void {
    vscode.window.showWarningMessage(
      `🎯 Implementation Issue Detected! Patterns: ${data.patterns.join(', ')}`,
      'Request Complete Implementation'
    ).then(selection => {
      if (selection === 'Request Complete Implementation') {
        vscode.commands.executeCommand('ai-code-guard.enforceQuality');
      }
    });
  }
  
  public clearQueue(): void {
    this.notificationQueue = [];
    console.log(`📢 NOTIFICATION QUEUE CLEARED`);
  }
  
  public disableNotifications(): void {
    // This would require making NOTIFICATIONS_ENABLED mutable
    console.log(`📢 NOTIFICATIONS DISABLED`);
  }
}