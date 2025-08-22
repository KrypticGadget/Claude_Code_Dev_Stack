import { TerminalSession, ProcessInfo } from '../types/terminal';

export interface TerminalMessage {
  type: 'create' | 'data' | 'resize' | 'exit' | 'error' | 'process-list' | 'kill';
  sessionId: string;
  data?: string;
  cols?: number;
  rows?: number;
  shell?: string;
  cwd?: string;
  env?: Record<string, string>;
  exitCode?: number;
  error?: string;
  processes?: ProcessInfo[];
  pid?: number;
}

export class TerminalService {
  private static instance: TerminalService;
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageQueue: TerminalMessage[] = [];
  private eventListeners: Map<string, Set<(message: TerminalMessage) => void>> = new Map();
  private isConnecting = false;
  private maxReconnectAttempts = 5;
  private reconnectAttempts = 0;
  private reconnectDelay = 1000;

  private constructor() {
    this.connect();
  }

  static getInstance(): TerminalService {
    if (!TerminalService.instance) {
      TerminalService.instance = new TerminalService();
    }
    return TerminalService.instance;
  }

  private connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    
    try {
      // Try to connect to the terminal WebSocket server
      const wsUrl = process.env.NODE_ENV === 'production' 
        ? `wss://${window.location.host}/terminal`
        : 'ws://localhost:3001/terminal';
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('Terminal WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // Send queued messages
        while (this.messageQueue.length > 0) {
          const message = this.messageQueue.shift();
          if (message) {
            this.sendMessage(message);
          }
        }

        this.emit('connection', { type: 'connection' as any, sessionId: 'system' });
      };

      this.ws.onmessage = (event) => {
        try {
          const message: TerminalMessage = JSON.parse(event.data);
          this.emit(message.sessionId, message);
          this.emit('*', message); // Emit to global listeners
        } catch (error) {
          console.error('Failed to parse terminal message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('Terminal WebSocket disconnected:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;

        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }

        this.emit('disconnection', { type: 'disconnection' as any, sessionId: 'system' });
      };

      this.ws.onerror = (error) => {
        console.error('Terminal WebSocket error:', error);
        this.isConnecting = false;
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private emit(event: string, message: TerminalMessage) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(message);
        } catch (error) {
          console.error('Error in terminal event listener:', error);
        }
      });
    }
  }

  public sendMessage(message: TerminalMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(message);
      
      // Try to reconnect if not already connecting
      if (!this.isConnecting) {
        this.connect();
      }
    }
  }

  public addEventListener(event: string, listener: (message: TerminalMessage) => void) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(listener);
  }

  public removeEventListener(event: string, listener: (message: TerminalMessage) => void) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.delete(listener);
      if (listeners.size === 0) {
        this.eventListeners.delete(event);
      }
    }
  }

  // Terminal operations
  public createSession(sessionId: string, options: {
    shell?: string;
    cwd?: string;
    env?: Record<string, string>;
    cols?: number;
    rows?: number;
  }) {
    this.sendMessage({
      type: 'create',
      sessionId,
      shell: options.shell || (process.platform === 'win32' ? 'powershell' : 'bash'),
      cwd: options.cwd || '/',
      env: options.env || {},
      cols: options.cols || 80,
      rows: options.rows || 24
    });
  }

  public sendData(sessionId: string, data: string) {
    this.sendMessage({
      type: 'data',
      sessionId,
      data
    });
  }

  public resizeTerminal(sessionId: string, cols: number, rows: number) {
    this.sendMessage({
      type: 'resize',
      sessionId,
      cols,
      rows
    });
  }

  public getProcesses(sessionId: string) {
    this.sendMessage({
      type: 'process-list',
      sessionId
    });
  }

  public killProcess(sessionId: string, pid: number) {
    this.sendMessage({
      type: 'kill',
      sessionId,
      pid
    });
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.eventListeners.clear();
    this.messageQueue.length = 0;
  }
}

// Command execution utilities
export class CommandExecutor {
  private terminalService: TerminalService;

  constructor() {
    this.terminalService = TerminalService.getInstance();
  }

  async executeCommand(
    sessionId: string, 
    command: string, 
    options: {
      timeout?: number;
      cwd?: string;
      env?: Record<string, string>;
    } = {}
  ): Promise<{ output: string; exitCode: number }> {
    return new Promise((resolve, reject) => {
      let output = '';
      let hasExited = false;
      
      const timeout = options.timeout || 30000; // 30 seconds default
      const timeoutId = setTimeout(() => {
        if (!hasExited) {
          hasExited = true;
          reject(new Error('Command execution timeout'));
        }
      }, timeout);

      const handleMessage = (message: TerminalMessage) => {
        if (message.sessionId !== sessionId) return;

        switch (message.type) {
          case 'data':
            if (message.data) {
              output += message.data;
            }
            break;
          
          case 'exit':
            if (!hasExited) {
              hasExited = true;
              clearTimeout(timeoutId);
              this.terminalService.removeEventListener(sessionId, handleMessage);
              resolve({
                output: output.trim(),
                exitCode: message.exitCode || 0
              });
            }
            break;
          
          case 'error':
            if (!hasExited) {
              hasExited = true;
              clearTimeout(timeoutId);
              this.terminalService.removeEventListener(sessionId, handleMessage);
              reject(new Error(message.error || 'Command execution failed'));
            }
            break;
        }
      };

      this.terminalService.addEventListener(sessionId, handleMessage);
      this.terminalService.sendData(sessionId, command + '\n');
    });
  }

  async getWorkingDirectory(sessionId: string): Promise<string> {
    try {
      const result = await this.executeCommand(sessionId, 'pwd', { timeout: 5000 });
      return result.output.trim();
    } catch (error) {
      console.error('Failed to get working directory:', error);
      return '/';
    }
  }

  async listFiles(sessionId: string, path?: string): Promise<string[]> {
    try {
      const command = path ? `ls "${path}"` : 'ls';
      const result = await this.executeCommand(sessionId, command, { timeout: 10000 });
      return result.output.split('\n').filter(line => line.trim());
    } catch (error) {
      console.error('Failed to list files:', error);
      return [];
    }
  }

  async changeDirectory(sessionId: string, path: string): Promise<boolean> {
    try {
      const result = await this.executeCommand(sessionId, `cd "${path}"`, { timeout: 5000 });
      return result.exitCode === 0;
    } catch (error) {
      console.error('Failed to change directory:', error);
      return false;
    }
  }
}

// Claude Code integration
export class ClaudeCodeIntegration {
  private commandExecutor: CommandExecutor;

  constructor() {
    this.commandExecutor = new CommandExecutor();
  }

  async executeClaudeCommand(
    sessionId: string,
    command: string,
    args: string[]
  ): Promise<string> {
    try {
      switch (command) {
        case 'claude-help':
          return this.getHelpText(args[0]);
        
        case 'claude-agent-list':
          return this.listAgents(args);
        
        case 'claude-invoke':
          return this.invokeAgent(args);
        
        case 'claude-status':
          return this.getSystemStatus();
        
        case 'claude-config':
          return this.manageConfig(args);
        
        default:
          return `Unknown Claude Code command: ${command}`;
      }
    } catch (error) {
      return `Error executing Claude Code command: ${error}`;
    }
  }

  private getHelpText(command?: string): string {
    const commands = {
      'claude-help': 'Show Claude Code terminal commands',
      'claude-agent-list': 'List all available Claude Code agents',
      'claude-invoke': 'Invoke a Claude Code agent',
      'claude-status': 'Show system status',
      'claude-config': 'Manage Claude Code configuration'
    };

    if (command && commands[command as keyof typeof commands]) {
      return `${command}: ${commands[command as keyof typeof commands]}`;
    }

    return `Claude Code Terminal Commands:\n${Object.entries(commands)
      .map(([cmd, desc]) => `  ${cmd.padEnd(20)} ${desc}`)
      .join('\n')}\n\nUse 'claude-help <command>' for detailed help.`;
  }

  private listAgents(args: string[]): string {
    // This would integrate with the actual agent registry
    const agents = [
      '@agent-frontend-architecture',
      '@agent-backend-architecture', 
      '@agent-testing-automation',
      '@agent-devops-engineering',
      '@agent-ui-ux-design',
      '@agent-database-design',
      '@agent-api-integration',
      '@agent-security-audit',
      '@agent-performance-optimization',
      '@agent-documentation-generator'
    ];

    const tierFilter = args.find(arg => arg.startsWith('--tier='));
    let filteredAgents = agents;

    if (tierFilter) {
      const tier = tierFilter.split('=')[1];
      // Filter by tier (this would use the actual agent registry)
      filteredAgents = agents.filter(agent => {
        // Mock tier filtering logic
        return true;
      });
    }

    return `Available Claude Code Agents (${filteredAgents.length}):\n${filteredAgents
      .map(agent => `  ${agent}`)
      .join('\n')}`;
  }

  private invokeAgent(args: string[]): string {
    if (args.length < 2) {
      return 'Usage: claude-invoke <agent> <task>';
    }

    const [agent, ...taskArgs] = args;
    const task = taskArgs.join(' ');

    // This would integrate with the actual agent invocation system
    return `Invoking ${agent} with task: "${task}"\n[Integration with Claude Code agent system would happen here]`;
  }

  private getSystemStatus(): string {
    return `Claude Code Terminal Status:
  Version: 3.6.9
  Active Sessions: ${TerminalService.getInstance().isConnected() ? 'Connected' : 'Disconnected'}
  WebSocket: ${TerminalService.getInstance().isConnected() ? 'Online' : 'Offline'}
  Platform: ${navigator.platform}
  User Agent: ${navigator.userAgent.split(' ')[0]}`;
  }

  private manageConfig(args: string[]): string {
    if (args.length === 0) {
      return 'Usage: claude-config <get|set|list> [key] [value]';
    }

    const [action, key, value] = args;

    switch (action) {
      case 'list':
        return 'Configuration keys:\n  theme\n  fontSize\n  shell\n  shortcuts';
      
      case 'get':
        if (!key) return 'Usage: claude-config get <key>';
        return `${key}: [value would be retrieved from store]`;
      
      case 'set':
        if (!key || !value) return 'Usage: claude-config set <key> <value>';
        return `Set ${key} = ${value}`;
      
      default:
        return `Unknown config action: ${action}`;
    }
  }
}

export default TerminalService;