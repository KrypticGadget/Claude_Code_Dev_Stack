import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import io, { Socket } from 'socket.io-client';

// Types
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'user' | 'developer';
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ConnectionInfo {
  host: string;
  port: number;
  protocol: 'ws' | 'wss';
  lastConnected?: Date;
  retryCount: number;
  maxRetries: number;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    duration?: number;
  };
}

interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  autoSave: boolean;
  notifications: boolean;
  sound: boolean;
  fontSize: number;
  codeTheme: string;
  compactMode: boolean;
}

// Store interface
interface AppStore {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionInfo: ConnectionInfo;
  socket: Socket | null;

  // User state
  currentUser: User | null;
  isAuthenticated: boolean;

  // Chat state
  messages: ChatMessage[];
  isTyping: boolean;
  currentInput: string;

  // Notifications
  notifications: Notification[];
  unreadCount: number;

  // Settings
  settings: AppSettings;

  // UI state
  sidebarOpen: boolean;
  activeTab: string;
  loading: boolean;

  // Actions - Connection
  connect: (connectionInfo: Partial<ConnectionInfo>) => Promise<void>;
  disconnect: () => void;
  reconnect: () => Promise<void>;

  // Actions - User
  setUser: (user: User | null) => void;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;

  // Actions - Chat
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  setTyping: (isTyping: boolean) => void;
  setCurrentInput: (input: string) => void;

  // Actions - Notifications
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;

  // Actions - Settings
  updateSettings: (settings: Partial<AppSettings>) => void;

  // Actions - UI
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: string) => void;
  setLoading: (loading: boolean) => void;
}

// Default settings
const defaultSettings: AppSettings = {
  theme: 'dark',
  language: 'en',
  autoSave: true,
  notifications: true,
  sound: true,
  fontSize: 14,
  codeTheme: 'github-dark',
  compactMode: false,
};

// Default connection info
const defaultConnectionInfo: ConnectionInfo = {
  host: 'localhost',
  port: 8080,
  protocol: 'ws',
  retryCount: 0,
  maxRetries: 5,
};

export const useAppStore = create<AppStore>()(
  devtools(
    subscribeWithSelector(
      immer((set, get) => ({
        // Initial state
        isConnected: false,
        isConnecting: false,
        connectionInfo: defaultConnectionInfo,
        socket: null,
        currentUser: null,
        isAuthenticated: false,
        messages: [],
        isTyping: false,
        currentInput: '',
        notifications: [],
        unreadCount: 0,
        settings: defaultSettings,
        sidebarOpen: true,
        activeTab: 'dashboard',
        loading: false,

        // Connection actions
        connect: async (newConnectionInfo) => {
          set((state) => {
            state.isConnecting = true;
            state.connectionInfo = { ...state.connectionInfo, ...newConnectionInfo };
          });

          try {
            const { host, port, protocol } = get().connectionInfo;
            const url = `${protocol === 'wss' ? 'https' : 'http'}://${host}:${port}`;
            
            const socket = io(url, {
              transports: ['websocket'],
              timeout: 10000,
              retries: 3,
            });

            // Socket event handlers
            socket.on('connect', () => {
              set((state) => {
                state.isConnected = true;
                state.isConnecting = false;
                state.connectionInfo.lastConnected = new Date();
                state.connectionInfo.retryCount = 0;
                state.socket = socket;
              });

              get().addNotification({
                type: 'success',
                title: 'Connected',
                message: 'Successfully connected to Claude Code server',
                read: false,
              });
            });

            socket.on('disconnect', () => {
              set((state) => {
                state.isConnected = false;
                state.isConnecting = false;
              });

              get().addNotification({
                type: 'warning',
                title: 'Disconnected',
                message: 'Connection to server lost',
                read: false,
              });
            });

            socket.on('connect_error', (error) => {
              set((state) => {
                state.isConnected = false;
                state.isConnecting = false;
                state.connectionInfo.retryCount++;
              });

              get().addNotification({
                type: 'error',
                title: 'Connection Error',
                message: `Failed to connect: ${error.message}`,
                read: false,
              });
            });

            socket.on('message', (data) => {
              get().addMessage({
                type: 'assistant',
                content: data.content,
                metadata: data.metadata,
              });
            });

            socket.on('typing', (isTyping: boolean) => {
              get().setTyping(isTyping);
            });

          } catch (error) {
            set((state) => {
              state.isConnecting = false;
            });
            
            get().addNotification({
              type: 'error',
              title: 'Connection Failed',
              message: error instanceof Error ? error.message : 'Unknown error',
              read: false,
            });
          }
        },

        disconnect: () => {
          const { socket } = get();
          if (socket) {
            socket.disconnect();
          }
          
          set((state) => {
            state.isConnected = false;
            state.isConnecting = false;
            state.socket = null;
          });
        },

        reconnect: async () => {
          get().disconnect();
          await new Promise(resolve => setTimeout(resolve, 1000));
          await get().connect({});
        },

        // User actions
        setUser: (user) => {
          set((state) => {
            state.currentUser = user;
            state.isAuthenticated = !!user;
          });
        },

        login: async (credentials) => {
          set((state) => {
            state.loading = true;
          });

          try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const user: User = {
              id: '1',
              name: 'Claude Developer',
              email: credentials.email,
              role: 'developer',
            };

            get().setUser(user);
            
            get().addNotification({
              type: 'success',
              title: 'Welcome!',
              message: `Successfully logged in as ${user.name}`,
              read: false,
            });

          } catch (error) {
            get().addNotification({
              type: 'error',
              title: 'Login Failed',
              message: error instanceof Error ? error.message : 'Login failed',
              read: false,
            });
          } finally {
            set((state) => {
              state.loading = false;
            });
          }
        },

        logout: () => {
          get().setUser(null);
          get().disconnect();
          get().clearMessages();
          
          get().addNotification({
            type: 'info',
            title: 'Logged Out',
            message: 'You have been logged out successfully',
            read: false,
          });
        },

        // Chat actions
        sendMessage: async (content) => {
          const { socket, isConnected } = get();
          
          if (!isConnected || !socket) {
            throw new Error('Not connected to server');
          }

          // Add user message
          get().addMessage({
            type: 'user',
            content,
          });

          // Clear input
          get().setCurrentInput('');

          // Send to server
          socket.emit('message', { content });
        },

        addMessage: (message) => {
          set((state) => {
            const newMessage: ChatMessage = {
              ...message,
              id: crypto.randomUUID(),
              timestamp: new Date(),
            };
            state.messages.push(newMessage);
          });
        },

        clearMessages: () => {
          set((state) => {
            state.messages = [];
          });
        },

        setTyping: (isTyping) => {
          set((state) => {
            state.isTyping = isTyping;
          });
        },

        setCurrentInput: (input) => {
          set((state) => {
            state.currentInput = input;
          });
        },

        // Notification actions
        addNotification: (notification) => {
          set((state) => {
            const newNotification: Notification = {
              ...notification,
              id: crypto.randomUUID(),
              timestamp: new Date(),
            };
            state.notifications.unshift(newNotification);
            if (!newNotification.read) {
              state.unreadCount++;
            }
          });
        },

        markNotificationRead: (id) => {
          set((state) => {
            const notification = state.notifications.find(n => n.id === id);
            if (notification && !notification.read) {
              notification.read = true;
              state.unreadCount = Math.max(0, state.unreadCount - 1);
            }
          });
        },

        clearNotifications: () => {
          set((state) => {
            state.notifications = [];
            state.unreadCount = 0;
          });
        },

        // Settings actions
        updateSettings: (newSettings) => {
          set((state) => {
            state.settings = { ...state.settings, ...newSettings };
          });
        },

        // UI actions
        setSidebarOpen: (open) => {
          set((state) => {
            state.sidebarOpen = open;
          });
        },

        setActiveTab: (tab) => {
          set((state) => {
            state.activeTab = tab;
          });
        },

        setLoading: (loading) => {
          set((state) => {
            state.loading = loading;
          });
        },
      })),
      {
        name: 'claude-code-app-store',
      }
    )
  )
);

// Persist settings to localStorage
useAppStore.subscribe(
  (state) => state.settings,
  (settings) => {
    localStorage.setItem('claude-code-settings', JSON.stringify(settings));
  }
);

// Load settings from localStorage on initialization
const savedSettings = localStorage.getItem('claude-code-settings');
if (savedSettings) {
  try {
    const parsedSettings = JSON.parse(savedSettings);
    useAppStore.getState().updateSettings(parsedSettings);
  } catch (error) {
    console.warn('Failed to load settings from localStorage:', error);
  }
}