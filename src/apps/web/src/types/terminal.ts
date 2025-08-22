export interface TerminalSession {
  id: string;
  title: string;
  cwd: string;
  history: string[];
  output: string[];
  createdAt: Date;
  lastActiveAt: Date;
  isActive: boolean;
  pid?: number;
  shell: string;
  environment: Record<string, string>;
  scrollback: number;
  size: {
    cols: number;
    rows: number;
  };
}

export interface TerminalConfig {
  theme: TerminalTheme;
  fontSize: number;
  fontFamily: string;
  scrollback: number;
  cursorBlink: boolean;
  cursorStyle: 'block' | 'underline' | 'bar';
  bellSound: boolean;
  allowTransparency: boolean;
  fontWeight: 'normal' | 'bold' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900';
  fontWeightBold: 'normal' | 'bold' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900';
  lineHeight: number;
  letterSpacing: number;
  windowsMode: boolean;
  macOptionIsMeta: boolean;
  rightClickSelectsWord: boolean;
  rendererType: 'dom' | 'canvas' | 'webgl';
  fastScrollModifier: 'alt' | 'ctrl' | 'shift';
  fastScrollSensitivity: number;
  scrollSensitivity: number;
}

export interface TerminalTheme {
  foreground: string;
  background: string;
  cursor: string;
  cursorAccent: string;
  selection: string;
  black: string;
  red: string;
  green: string;
  yellow: string;
  blue: string;
  magenta: string;
  cyan: string;
  white: string;
  brightBlack: string;
  brightRed: string;
  brightGreen: string;
  brightYellow: string;
  brightBlue: string;
  brightMagenta: string;
  brightCyan: string;
  brightWhite: string;
}

export interface CommandHistory {
  command: string;
  timestamp: Date;
  exitCode?: number;
  duration?: number;
  cwd: string;
  sessionId: string;
}

export interface TerminalSearchResult {
  row: number;
  col: number;
  length: number;
  text: string;
}

export interface TerminalShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: string;
  description: string;
}

export interface TerminalPty {
  pid: number;
  process: string;
  fd: number;
  cols: number;
  rows: number;
  cwd: string;
  env: Record<string, string>;
}

export interface ClaudeCodeCommand {
  name: string;
  description: string;
  usage: string;
  examples: string[];
  handler: (args: string[], session: TerminalSession) => Promise<string>;
}

export interface TerminalSplit {
  id: string;
  type: 'horizontal' | 'vertical';
  size: number; // percentage
  sessions: TerminalSession[];
  activeSessionId: string;
}

export interface TerminalWorkspace {
  id: string;
  name: string;
  tabs: TerminalTab[];
  activeTabId: string;
  layout: 'single' | 'split';
  splits?: TerminalSplit[];
}

export interface TerminalTab {
  id: string;
  title: string;
  sessions: TerminalSession[];
  activeSessionId: string;
  isClosable: boolean;
  badge?: {
    count: number;
    type: 'info' | 'warning' | 'error';
  };
}

export interface TerminalState {
  workspaces: TerminalWorkspace[];
  activeWorkspaceId: string;
  config: TerminalConfig;
  themes: Record<string, TerminalTheme>;
  commandHistory: CommandHistory[];
  shortcuts: TerminalShortcut[];
  claudeCommands: ClaudeCodeCommand[];
}

export interface ProcessInfo {
  pid: number;
  command: string;
  args: string[];
  cwd: string;
  status: 'running' | 'stopped' | 'finished';
  startTime: Date;
  endTime?: Date;
  exitCode?: number;
}

export interface TerminalDragDropData {
  type: 'file' | 'directory' | 'text';
  path?: string;
  content?: string;
  mimeType?: string;
}