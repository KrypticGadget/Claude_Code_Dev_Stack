/**
 * App state context for React Native
 * Ported from Flutter AppState provider (@9cat) - MIT License
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { ConnectionConfig } from '../models/ConnectionConfig';
import { ChatMessage, ChatMessageImpl, MessageType } from '../models/ChatMessage';
import { WebSocketService, WebSocketMessage } from '../services/WebSocketService';
import { VoiceService } from '../services/VoiceService';

// State interface
interface AppState {
  messages: ChatMessage[];
  currentConnection: ConnectionConfig | null;
  isConnecting: boolean;
  isConnected: boolean;
  isVoiceEnabled: boolean;
  isListening: boolean;
  currentInput: string;
}

// Action types
type AppAction =
  | { type: 'SET_CONNECTING'; payload: boolean }
  | { type: 'SET_CONNECTION'; payload: ConnectionConfig | null }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_VOICE_ENABLED'; payload: boolean }
  | { type: 'SET_LISTENING'; payload: boolean }
  | { type: 'SET_CURRENT_INPUT'; payload: string };

// Initial state
const initialState: AppState = {
  messages: [],
  currentConnection: null,
  isConnecting: false,
  isConnected: false,
  isVoiceEnabled: false,
  isListening: false,
  currentInput: '',
};

// Reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_CONNECTING':
      return { ...state, isConnecting: action.payload };
    case 'SET_CONNECTION':
      return { ...state, currentConnection: action.payload };
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    case 'SET_VOICE_ENABLED':
      return { ...state, isVoiceEnabled: action.payload };
    case 'SET_LISTENING':
      return { ...state, isListening: action.payload };
    case 'SET_CURRENT_INPUT':
      return { ...state, currentInput: action.payload };
    default:
      return state;
  }
};

// Context interface
interface AppStateContextType {
  state: AppState;
  connectToServer: (connection: ConnectionConfig) => Promise<boolean>;
  disconnect: () => void;
  sendCommand: (command: string) => Promise<void>;
  startClaudeSession: () => Promise<void>;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  updateCurrentInput: (input: string) => void;
  startVoiceInput: () => Promise<void>;
  stopVoiceInput: () => Promise<void>;
}

// Create context
const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

// Provider component
interface AppStateProviderProps {
  children: ReactNode;
  socket?: any; // Socket.IO connection (optional)
}

export const AppStateProvider: React.FC<AppStateProviderProps> = ({ 
  children, 
  socket 
}) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const wsService = WebSocketService.getInstance();
  const voiceService = VoiceService.getInstance();

  // Initialize services
  useEffect(() => {
    const initializeServices = async () => {
      console.log('🔧 AppStateProvider: Initializing services...');
      
      // Initialize voice service
      const voiceEnabled = await voiceService.initialize();
      dispatch({ type: 'SET_VOICE_ENABLED', payload: voiceEnabled });

      // Set up WebSocket message listener
      const messageListener = (message: WebSocketMessage) => {
        console.log('🎯 AppStateProvider: Received WebSocket message:', message);
        handleWebSocketMessage(message);
      };

      const connectionListener = (connected: boolean) => {
        console.log('🔗 AppStateProvider: Connection status changed:', connected);
        dispatch({ type: 'SET_CONNECTED', payload: connected });
      };

      wsService.addMessageListener(messageListener);
      wsService.addConnectionListener(connectionListener);

      // Socket.IO integration for backend monitoring
      if (socket) {
        socket.on('agent-update', (data: any) => {
          console.log('📡 Received agent update:', data);
          addMessage(new ChatMessageImpl({
            id: Date.now().toString(),
            content: `Agent Update: ${data.message || JSON.stringify(data)}`,
            type: MessageType.SYSTEM,
            timestamp: new Date(),
          }));
        });
      }

      return () => {
        wsService.removeMessageListener(messageListener);
        wsService.removeConnectionListener(connectionListener);
        voiceService.destroy();
      };
    };

    initializeServices();
  }, [socket]);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    const type = message.type;
    const content = message.message || message.data || '';

    let messageType: MessageType;
    switch (type) {
      case 'claude-output':
        messageType = MessageType.ASSISTANT;
        break;
      case 'user-input':
        messageType = MessageType.USER;
        break;
      case 'output':
      case 'system':
      case 'auth-success':
      case 'claude-started':
      case 'command-complete':
      case 'claude-session-ended':
        messageType = MessageType.SYSTEM;
        break;
      case 'error':
        messageType = MessageType.ERROR;
        break;
      default:
        messageType = MessageType.SYSTEM;
    }

    // Don't add empty messages
    if (!content.toString().trim()) {
      console.log('⚠️ AppStateProvider: Skipping empty message of type:', type);
      return;
    }

    const chatMessage = new ChatMessageImpl({
      id: Date.now().toString(),
      content: content.toString(),
      type: messageType,
      timestamp: new Date(),
    });

    addMessage(chatMessage);
  };

  const connectToServer = async (connection: ConnectionConfig): Promise<boolean> => {
    dispatch({ type: 'SET_CONNECTING', payload: true });

    addMessage(new ChatMessageImpl({
      id: Date.now().toString(),
      content: `Connecting to ${connection.serverUrl}...`,
      type: MessageType.SYSTEM,
      timestamp: new Date(),
    }));

    try {
      const success = await wsService.connect(connection);
      
      if (success) {
        dispatch({ type: 'SET_CONNECTION', payload: connection });
        addMessage(new ChatMessageImpl({
          id: Date.now().toString(),
          content: 'Connected successfully! Ready to interact with Claude-Code.',
          type: MessageType.SYSTEM,
          timestamp: new Date(),
        }));
      } else {
        addMessage(new ChatMessageImpl({
          id: Date.now().toString(),
          content: 'Connection failed. Please check your server URL and credentials.',
          type: MessageType.ERROR,
          timestamp: new Date(),
        }));
      }

      dispatch({ type: 'SET_CONNECTING', payload: false });
      return success;
    } catch (error) {
      console.error('Connection error:', error);
      addMessage(new ChatMessageImpl({
        id: Date.now().toString(),
        content: `Connection error: ${error}`,
        type: MessageType.ERROR,
        timestamp: new Date(),
      }));
      dispatch({ type: 'SET_CONNECTING', payload: false });
      return false;
    }
  };

  const disconnect = () => {
    wsService.disconnect();
    dispatch({ type: 'SET_CONNECTION', payload: null });
    addMessage(new ChatMessageImpl({
      id: Date.now().toString(),
      content: 'Disconnected from server.',
      type: MessageType.SYSTEM,
      timestamp: new Date(),
    }));
  };

  const sendCommand = async (command: string): Promise<void> => {
    addMessage(new ChatMessageImpl({
      id: Date.now().toString(),
      content: command,
      type: MessageType.USER,
      timestamp: new Date(),
    }));

    try {
      await wsService.sendCommand(command);
    } catch (error) {
      addMessage(new ChatMessageImpl({
        id: Date.now().toString(),
        content: `Error sending command: ${error}`,
        type: MessageType.ERROR,
        timestamp: new Date(),
      }));
    }

    dispatch({ type: 'SET_CURRENT_INPUT', payload: '' });
  };

  const startClaudeSession = async (): Promise<void> => {
    try {
      await wsService.startClaudeSession();
      addMessage(new ChatMessageImpl({
        id: Date.now().toString(),
        content: 'Starting Claude interactive session...',
        type: MessageType.SYSTEM,
        timestamp: new Date(),
      }));
    } catch (error) {
      addMessage(new ChatMessageImpl({
        id: Date.now().toString(),
        content: `Error starting Claude session: ${error}`,
        type: MessageType.ERROR,
        timestamp: new Date(),
      }));
    }
  };

  const addMessage = (message: ChatMessage) => {
    console.log('💬 AppStateProvider: Adding message:', message.content);
    dispatch({ type: 'ADD_MESSAGE', payload: message });
  };

  const clearMessages = () => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  };

  const updateCurrentInput = (input: string) => {
    dispatch({ type: 'SET_CURRENT_INPUT', payload: input });
  };

  const startVoiceInput = async (): Promise<void> => {
    if (!state.isVoiceEnabled) return;

    dispatch({ type: 'SET_LISTENING', payload: true });
    
    await voiceService.startListening((text: string) => {
      updateCurrentInput(text);
      dispatch({ type: 'SET_LISTENING', payload: false });
    });
  };

  const stopVoiceInput = async (): Promise<void> => {
    await voiceService.stopListening();
    dispatch({ type: 'SET_LISTENING', payload: false });
  };

  const contextValue: AppStateContextType = {
    state,
    connectToServer,
    disconnect,
    sendCommand,
    startClaudeSession,
    addMessage,
    clearMessages,
    updateCurrentInput,
    startVoiceInput,
    stopVoiceInput,
  };

  return (
    <AppStateContext.Provider value={contextValue}>
      {children}
    </AppStateContext.Provider>
  );
};

// Hook for using the context
export const useAppState = (): AppStateContextType => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};