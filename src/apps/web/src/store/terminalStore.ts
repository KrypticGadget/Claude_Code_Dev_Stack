import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import {
  TerminalState,
  TerminalSession,
  TerminalWorkspace,
  TerminalTab,
  TerminalConfig,
  TerminalTheme,
  CommandHistory,
  ClaudeCodeCommand,
  TerminalShortcut
} from '../types/terminal';

// Default themes
const defaultThemes: Record<string, TerminalTheme> = {
  dark: {
    foreground: '#ffffff',
    background: '#1e1e1e',
    cursor: '#ffffff',
    cursorAccent: '#000000',
    selection: '#3f51b5',
    black: '#000000',
    red: '#cd3131',
    green: '#0dbc79',
    yellow: '#e5e510',
    blue: '#2472c8',
    magenta: '#bc3fbc',
    cyan: '#11a8cd',
    white: '#e5e5e5',
    brightBlack: '#666666',
    brightRed: '#f14c4c',
    brightGreen: '#23d18b',
    brightYellow: '#f5f543',
    brightBlue: '#3b8eea',
    brightMagenta: '#d670d6',
    brightCyan: '#29b8db',
    brightWhite: '#ffffff'
  },
  light: {
    foreground: '#333333',
    background: '#ffffff',
    cursor: '#000000',
    cursorAccent: '#ffffff',
    selection: '#add6ff',
    black: '#000000',
    red: '#cd3131',
    green: '#00bc00',
    yellow: '#949800',
    blue: '#0451a5',
    magenta: '#bc05bc',
    cyan: '#0598bc',
    white: '#555555',
    brightBlack: '#666666',
    brightRed: '#cd3131',
    brightGreen: '#14ce14',
    brightYellow: '#b5ba00',
    brightBlue: '#0451a5',
    brightMagenta: '#bc05bc',
    brightCyan: '#0598bc',
    brightWhite: '#a5a5a5'
  },
  monokai: {
    foreground: '#f8f8f2',
    background: '#272822',
    cursor: '#f8f8f0',
    cursorAccent: '#272822',
    selection: '#49483e',
    black: '#272822',
    red: '#f92672',
    green: '#a6e22e',
    yellow: '#f4bf75',
    blue: '#66d9ef',
    magenta: '#ae81ff',
    cyan: '#a1efe4',
    white: '#f8f8f2',
    brightBlack: '#75715e',
    brightRed: '#f92672',
    brightGreen: '#a6e22e',
    brightYellow: '#f4bf75',
    brightBlue: '#66d9ef',
    brightMagenta: '#ae81ff',
    brightCyan: '#a1efe4',
    brightWhite: '#f9f8f5'
  }
};

// Default configuration
const defaultConfig: TerminalConfig = {
  theme: defaultThemes.dark,
  fontSize: 14,
  fontFamily: 'Consolas, "Liberation Mono", Menlo, Courier, monospace',
  scrollback: 1000,
  cursorBlink: true,
  cursorStyle: 'block',
  bellSound: false,
  allowTransparency: false,
  fontWeight: 'normal',
  fontWeightBold: 'bold',
  lineHeight: 1.0,
  letterSpacing: 0,
  windowsMode: process.platform === 'win32',
  macOptionIsMeta: false,
  rightClickSelectsWord: true,
  rendererType: 'canvas',
  fastScrollModifier: 'alt',
  fastScrollSensitivity: 5,
  scrollSensitivity: 1
};

// Default keyboard shortcuts
const defaultShortcuts: TerminalShortcut[] = [
  { key: 't', ctrlKey: true, shiftKey: true, action: 'new-tab', description: 'New Terminal Tab' },
  { key: 'w', ctrlKey: true, shiftKey: true, action: 'close-tab', description: 'Close Terminal Tab' },
  { key: 'n', ctrlKey: true, shiftKey: true, action: 'new-window', description: 'New Terminal Window' },
  { key: 'f', ctrlKey: true, shiftKey: true, action: 'search', description: 'Search in Terminal' },
  { key: 'c', ctrlKey: true, shiftKey: true, action: 'copy', description: 'Copy Selection' },
  { key: 'v', ctrlKey: true, shiftKey: true, action: 'paste', description: 'Paste from Clipboard' },
  { key: '=', ctrlKey: true, action: 'zoom-in', description: 'Increase Font Size' },
  { key: '-', ctrlKey: true, action: 'zoom-out', description: 'Decrease Font Size' },
  { key: '0', ctrlKey: true, action: 'zoom-reset', description: 'Reset Font Size' },
  { key: 'k', ctrlKey: true, shiftKey: true, action: 'clear', description: 'Clear Terminal' },
  { key: 'Tab', ctrlKey: true, action: 'next-tab', description: 'Next Tab' },
  { key: 'Tab', ctrlKey: true, shiftKey: true, action: 'prev-tab', description: 'Previous Tab' },
  { key: 'd', ctrlKey: true, shiftKey: true, action: 'split-horizontal', description: 'Split Horizontally' },
  { key: 'd', ctrlKey: true, altKey: true, action: 'split-vertical', description: 'Split Vertically' }
];

// Built-in Claude Code commands
const claudeCommands: ClaudeCodeCommand[] = [
  {
    name: 'claude-help',
    description: 'Show Claude Code terminal commands',
    usage: 'claude-help [command]',
    examples: ['claude-help', 'claude-help agent-list'],
    handler: async (args: string[]) => {
      if (args.length > 0) {
        const command = claudeCommands.find(cmd => cmd.name === args[0]);
        if (command) {
          return `${command.name}: ${command.description}\nUsage: ${command.usage}\nExamples:\n${command.examples.map(ex => `  ${ex}`).join('\n')}`;
        }
        return `Command '${args[0]}' not found. Use 'claude-help' to see all commands.`;
      }
      return `Claude Code Terminal Commands:\n${claudeCommands.map(cmd => `  ${cmd.name.padEnd(20)} ${cmd.description}`).join('\n')}\n\nUse 'claude-help <command>' for detailed help.`;
    }
  },
  {
    name: 'claude-agent-list',
    description: 'List all available Claude Code agents',
    usage: 'claude-agent-list [--tier <tier>]',
    examples: ['claude-agent-list', 'claude-agent-list --tier 1'],
    handler: async (args: string[]) => {
      // This would integrate with the agent registry
      return 'Available Claude Code Agents:\n  - @agent-frontend-architecture\n  - @agent-backend-architecture\n  - @agent-testing-automation\n  - @agent-devops-engineering\n  - @agent-ui-ux-design\n  - ...and 23 more agents';
    }
  },
  {
    name: 'claude-invoke',
    description: 'Invoke a Claude Code agent',
    usage: 'claude-invoke <agent> <task>',
    examples: ['claude-invoke @agent-testing "Create unit tests for user service"'],
    handler: async (args: string[]) => {
      if (args.length < 2) {
        return 'Usage: claude-invoke <agent> <task>';
      }
      const [agent, ...taskArgs] = args;
      const task = taskArgs.join(' ');
      return `Invoking ${agent} with task: "${task}"\n[This would integrate with the Claude Code agent system]`;
    }
  }
];

interface TerminalActions {
  // Workspace management
  createWorkspace: (name: string) => string;
  deleteWorkspace: (id: string) => void;
  setActiveWorkspace: (id: string) => void;
  renameWorkspace: (id: string, name: string) => void;
  
  // Tab management
  createTab: (workspaceId: string, title?: string) => string;
  closeTab: (workspaceId: string, tabId: string) => void;
  setActiveTab: (workspaceId: string, tabId: string) => void;
  renameTab: (workspaceId: string, tabId: string, title: string) => void;
  
  // Session management
  createSession: (workspaceId: string, tabId: string, options?: Partial<TerminalSession>) => string;
  closeSession: (sessionId: string) => void;
  setActiveSession: (workspaceId: string, tabId: string, sessionId: string) => void;
  updateSession: (sessionId: string, updates: Partial<TerminalSession>) => void;
  
  // History management
  addToHistory: (sessionId: string, command: string) => void;
  clearHistory: (sessionId: string) => void;
  addCommandHistory: (history: CommandHistory) => void;
  clearCommandHistory: () => void;
  
  // Configuration
  updateConfig: (config: Partial<TerminalConfig>) => void;
  setTheme: (themeName: string) => void;
  addTheme: (name: string, theme: TerminalTheme) => void;
  
  // Utilities
  getActiveSession: () => TerminalSession | null;
  getSessionById: (id: string) => TerminalSession | null;
  getAllSessions: () => TerminalSession[];
  searchSessions: (query: string) => TerminalSession[];
  
  // Persistence
  saveState: () => void;
  loadState: () => void;
  exportConfig: () => string;
  importConfig: (config: string) => void;
}

export const useTerminalStore = create<TerminalState & TerminalActions>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        // Initial state
        workspaces: [],
        activeWorkspaceId: '',
        config: defaultConfig,
        themes: defaultThemes,
        commandHistory: [],
        shortcuts: defaultShortcuts,
        claudeCommands,

        // Workspace actions
        createWorkspace: (name: string) => {
          const id = uuidv4();
          const workspace: TerminalWorkspace = {
            id,
            name,
            tabs: [],
            activeTabId: '',
            layout: 'single'
          };
          
          set(state => {
            const newWorkspaces = [...state.workspaces, workspace];
            return {
              workspaces: newWorkspaces,
              activeWorkspaceId: state.workspaces.length === 0 ? id : state.activeWorkspaceId
            };
          });
          
          return id;
        },

        deleteWorkspace: (id: string) => {
          set(state => {
            const newWorkspaces = state.workspaces.filter(w => w.id !== id);
            const newActiveId = state.activeWorkspaceId === id 
              ? (newWorkspaces.length > 0 ? newWorkspaces[0].id : '')
              : state.activeWorkspaceId;
            
            return {
              workspaces: newWorkspaces,
              activeWorkspaceId: newActiveId
            };
          });
        },

        setActiveWorkspace: (id: string) => {
          set({ activeWorkspaceId: id });
        },

        renameWorkspace: (id: string, name: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w => 
              w.id === id ? { ...w, name } : w
            )
          }));
        },

        // Tab actions
        createTab: (workspaceId: string, title = 'Terminal') => {
          const id = uuidv4();
          const tab: TerminalTab = {
            id,
            title,
            sessions: [],
            activeSessionId: '',
            isClosable: true
          };

          set(state => ({
            workspaces: state.workspaces.map(w => 
              w.id === workspaceId 
                ? { 
                    ...w, 
                    tabs: [...w.tabs, tab],
                    activeTabId: w.tabs.length === 0 ? id : w.activeTabId
                  }
                : w
            )
          }));

          return id;
        },

        closeTab: (workspaceId: string, tabId: string) => {
          set(state => {
            const workspace = state.workspaces.find(w => w.id === workspaceId);
            if (!workspace) return state;

            const newTabs = workspace.tabs.filter(t => t.id !== tabId);
            const newActiveTabId = workspace.activeTabId === tabId
              ? (newTabs.length > 0 ? newTabs[0].id : '')
              : workspace.activeTabId;

            return {
              workspaces: state.workspaces.map(w =>
                w.id === workspaceId
                  ? { ...w, tabs: newTabs, activeTabId: newActiveTabId }
                  : w
              )
            };
          });
        },

        setActiveTab: (workspaceId: string, tabId: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w =>
              w.id === workspaceId ? { ...w, activeTabId: tabId } : w
            )
          }));
        },

        renameTab: (workspaceId: string, tabId: string, title: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w =>
              w.id === workspaceId
                ? {
                    ...w,
                    tabs: w.tabs.map(t => t.id === tabId ? { ...t, title } : t)
                  }
                : w
            )
          }));
        },

        // Session actions
        createSession: (workspaceId: string, tabId: string, options = {}) => {
          const id = uuidv4();
          const session: TerminalSession = {
            id,
            title: 'Terminal',
            cwd: process.cwd?.() || '/',
            history: [],
            output: [],
            createdAt: new Date(),
            lastActiveAt: new Date(),
            isActive: true,
            shell: process.platform === 'win32' ? 'powershell' : 'bash',
            environment: { ...process.env },
            scrollback: 1000,
            size: { cols: 80, rows: 24 },
            ...options
          };

          set(state => ({
            workspaces: state.workspaces.map(w =>
              w.id === workspaceId
                ? {
                    ...w,
                    tabs: w.tabs.map(t =>
                      t.id === tabId
                        ? {
                            ...t,
                            sessions: [...t.sessions, session],
                            activeSessionId: t.sessions.length === 0 ? id : t.activeSessionId
                          }
                        : t
                    )
                  }
                : w
            )
          }));

          return id;
        },

        closeSession: (sessionId: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w => ({
              ...w,
              tabs: w.tabs.map(t => {
                const newSessions = t.sessions.filter(s => s.id !== sessionId);
                const newActiveSessionId = t.activeSessionId === sessionId
                  ? (newSessions.length > 0 ? newSessions[0].id : '')
                  : t.activeSessionId;

                return {
                  ...t,
                  sessions: newSessions,
                  activeSessionId: newActiveSessionId
                };
              })
            }))
          }));
        },

        setActiveSession: (workspaceId: string, tabId: string, sessionId: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w =>
              w.id === workspaceId
                ? {
                    ...w,
                    tabs: w.tabs.map(t =>
                      t.id === tabId ? { ...t, activeSessionId: sessionId } : t
                    )
                  }
                : w
            )
          }));
        },

        updateSession: (sessionId: string, updates: Partial<TerminalSession>) => {
          set(state => ({
            workspaces: state.workspaces.map(w => ({
              ...w,
              tabs: w.tabs.map(t => ({
                ...t,
                sessions: t.sessions.map(s =>
                  s.id === sessionId
                    ? { ...s, ...updates, lastActiveAt: new Date() }
                    : s
                )
              }))
            }))
          }));
        },

        // History actions
        addToHistory: (sessionId: string, command: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w => ({
              ...w,
              tabs: w.tabs.map(t => ({
                ...t,
                sessions: t.sessions.map(s =>
                  s.id === sessionId
                    ? { ...s, history: [...s.history, command] }
                    : s
                )
              }))
            }))
          }));
        },

        clearHistory: (sessionId: string) => {
          set(state => ({
            workspaces: state.workspaces.map(w => ({
              ...w,
              tabs: w.tabs.map(t => ({
                ...t,
                sessions: t.sessions.map(s =>
                  s.id === sessionId ? { ...s, history: [] } : s
                )
              }))
            }))
          }));
        },

        addCommandHistory: (history: CommandHistory) => {
          set(state => ({
            commandHistory: [...state.commandHistory, history].slice(-1000) // Keep last 1000 commands
          }));
        },

        clearCommandHistory: () => {
          set({ commandHistory: [] });
        },

        // Configuration actions
        updateConfig: (config: Partial<TerminalConfig>) => {
          set(state => ({
            config: { ...state.config, ...config }
          }));
        },

        setTheme: (themeName: string) => {
          set(state => {
            const theme = state.themes[themeName];
            if (theme) {
              return {
                config: { ...state.config, theme }
              };
            }
            return state;
          });
        },

        addTheme: (name: string, theme: TerminalTheme) => {
          set(state => ({
            themes: { ...state.themes, [name]: theme }
          }));
        },

        // Utility functions
        getActiveSession: () => {
          const state = get();
          const workspace = state.workspaces.find(w => w.id === state.activeWorkspaceId);
          if (!workspace) return null;

          const tab = workspace.tabs.find(t => t.id === workspace.activeTabId);
          if (!tab) return null;

          return tab.sessions.find(s => s.id === tab.activeSessionId) || null;
        },

        getSessionById: (id: string) => {
          const state = get();
          for (const workspace of state.workspaces) {
            for (const tab of workspace.tabs) {
              const session = tab.sessions.find(s => s.id === id);
              if (session) return session;
            }
          }
          return null;
        },

        getAllSessions: () => {
          const state = get();
          const sessions: TerminalSession[] = [];
          for (const workspace of state.workspaces) {
            for (const tab of workspace.tabs) {
              sessions.push(...tab.sessions);
            }
          }
          return sessions;
        },

        searchSessions: (query: string) => {
          const sessions = get().getAllSessions();
          return sessions.filter(session =>
            session.title.toLowerCase().includes(query.toLowerCase()) ||
            session.cwd.toLowerCase().includes(query.toLowerCase()) ||
            session.history.some(cmd => cmd.toLowerCase().includes(query.toLowerCase()))
          );
        },

        // Persistence
        saveState: () => {
          // This is handled by the persist middleware
        },

        loadState: () => {
          // This is handled by the persist middleware
        },

        exportConfig: () => {
          const state = get();
          return JSON.stringify({
            config: state.config,
            themes: state.themes,
            shortcuts: state.shortcuts
          }, null, 2);
        },

        importConfig: (configStr: string) => {
          try {
            const config = JSON.parse(configStr);
            set(state => ({
              ...state,
              ...config
            }));
          } catch (error) {
            console.error('Failed to import config:', error);
          }
        }
      }),
      {
        name: 'claude-terminal-store',
        partialize: (state) => ({
          workspaces: state.workspaces,
          activeWorkspaceId: state.activeWorkspaceId,
          config: state.config,
          themes: state.themes,
          commandHistory: state.commandHistory.slice(-100), // Only persist last 100 commands
          shortcuts: state.shortcuts
        })
      }
    )
  )
);

// Initialize default workspace and tab if none exist
const initializeDefaultWorkspace = () => {
  const store = useTerminalStore.getState();
  if (store.workspaces.length === 0) {
    const workspaceId = store.createWorkspace('Default');
    const tabId = store.createTab(workspaceId);
    store.createSession(workspaceId, tabId);
  }
};

// Auto-initialize on store creation
setTimeout(initializeDefaultWorkspace, 0);