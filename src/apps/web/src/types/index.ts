// Global type definitions for Claude Code Dev Stack UI

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'user' | 'developer';
  createdAt: Date;
  lastLoginAt?: Date;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    duration?: number;
    context?: string;
  };
}

export interface ConnectionInfo {
  host: string;
  port: number;
  protocol: 'ws' | 'wss' | 'http' | 'https';
  lastConnected?: Date;
  retryCount: number;
  maxRetries: number;
  timeout?: number;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  autoSave: boolean;
  notifications: boolean;
  sound: boolean;
  fontSize: number;
  codeTheme: string;
  compactMode: boolean;
  animationsEnabled: boolean;
  debugMode: boolean;
}

export interface ComponentDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  complexity: 'Simple' | 'Medium' | 'Complex';
  usage: string;
  props: PropDefinition[];
  examples: CodeExample[];
  dependencies: string[];
  version: string;
  lastUpdated: Date;
}

export interface PropDefinition {
  name: string;
  type: string;
  required: boolean;
  default?: string;
  description: string;
  examples?: string[];
}

export interface CodeExample {
  id: string;
  title: string;
  description: string;
  code: string;
  language: string;
  live?: boolean;
}

export interface DocumentationSection {
  id: string;
  title: string;
  description: string;
  content: string;
  category: string;
  tags: string[];
  lastUpdated: Date;
  author: string;
  readTime: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'archived';
  createdAt: Date;
  updatedAt: Date;
  owner: User;
  collaborators: User[];
  tags: string[];
  technologies: string[];
  repository?: {
    url: string;
    branch: string;
    provider: 'github' | 'gitlab' | 'bitbucket';
  };
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: Date;
    requestId: string;
    pagination?: {
      page: number;
      limit: number;
      total: number;
      hasNext: boolean;
      hasPrev: boolean;
    };
  };
}

export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: Date;
  id: string;
}

export interface Theme {
  name: string;
  displayName: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    error: string;
    warning: string;
    info: string;
    success: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      small: number;
      medium: number;
      large: number;
    };
  };
}

export interface SystemInfo {
  version: string;
  buildDate: Date;
  environment: 'development' | 'staging' | 'production';
  features: {
    [key: string]: boolean;
  };
  limits: {
    maxFileSize: number;
    maxConcurrentConnections: number;
    rateLimitRequests: number;
    rateLimitWindow: number;
  };
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type WithTimestamps<T> = T & {
  createdAt: Date;
  updatedAt: Date;
};

export type WithId<T> = T & {
  id: string;
};

export type WithOptionalId<T> = T & {
  id?: string;
};

// Event types
export interface AppEvent {
  type: string;
  timestamp: Date;
  data?: any;
}

export interface ConnectionEvent extends AppEvent {
  type: 'connection:established' | 'connection:lost' | 'connection:error';
  data: {
    connectionInfo: ConnectionInfo;
    error?: Error;
  };
}

export interface ChatEvent extends AppEvent {
  type: 'chat:message' | 'chat:typing' | 'chat:clear';
  data: {
    message?: ChatMessage;
    isTyping?: boolean;
  };
}

export interface NotificationEvent extends AppEvent {
  type: 'notification:new' | 'notification:read' | 'notification:clear';
  data: {
    notification?: Notification;
    notificationId?: string;
  };
}

// Component prop types
export interface BaseComponentProps {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  'data-testid'?: string;
}

export interface LoadingProps extends BaseComponentProps {
  loading: boolean;
  error?: Error | string;
  retry?: () => void;
}

export interface SearchableProps {
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  placeholder?: string;
}

export interface PaginatedProps {
  page: number;
  limit: number;
  total: number;
  onPageChange: (page: number) => void;
  onLimitChange?: (limit: number) => void;
}

export interface SortableProps<T = string> {
  sortBy?: T;
  sortOrder?: 'asc' | 'desc';
  onSortChange?: (sortBy: T, sortOrder: 'asc' | 'desc') => void;
}

// Hook return types
export interface UseLocalStorageReturn<T> {
  value: T;
  setValue: (value: T | ((prevValue: T) => T)) => void;
  removeValue: () => void;
}

export interface UseAsyncReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
}

// Error types
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public field: string, public value: any) {
    super(message, 'VALIDATION_ERROR', 400, { field, value });
    this.name = 'ValidationError';
  }
}

export class NetworkError extends AppError {
  constructor(message: string, public statusCode: number, public response?: any) {
    super(message, 'NETWORK_ERROR', statusCode, { response });
    this.name = 'NetworkError';
  }
}

// Constants
export const SUPPORTED_LANGUAGES = [
  'en', 'es', 'fr', 'de', 'ja', 'zh', 'ko', 'pt', 'ru', 'it'
] as const;

export const SUPPORTED_THEMES = [
  'light', 'dark', 'system'
] as const;

export const COMPONENT_CATEGORIES = [
  'Layout', 'Navigation', 'Data Display', 'Input', 'Feedback', 
  'Charts', 'Editor', 'Media', 'Utility'
] as const;

export const COMPLEXITY_LEVELS = [
  'Simple', 'Medium', 'Complex'
] as const;

export type SupportedLanguage = typeof SUPPORTED_LANGUAGES[number];
export type SupportedTheme = typeof SUPPORTED_THEMES[number];
export type ComponentCategory = typeof COMPONENT_CATEGORIES[number];
export type ComplexityLevel = typeof COMPLEXITY_LEVELS[number];

// File Explorer Types
export interface FileSystemNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  extension?: string;
  mimeType?: string;
  created: Date;
  modified: Date;
  accessed?: Date;
  permissions: {
    read: boolean;
    write: boolean;
    execute: boolean;
  };
  parent?: string;
  children?: string[];
  isExpanded?: boolean;
  isLoading?: boolean;
  isSelected?: boolean;
  metadata?: {
    [key: string]: any;
  };
}

export interface FileExplorerState {
  nodes: Record<string, FileSystemNode>;
  rootNodes: string[];
  selectedNodes: string[];
  expandedNodes: Set<string>;
  currentPath: string;
  searchQuery: string;
  searchResults: string[];
  clipboard: {
    operation: 'copy' | 'cut' | null;
    nodes: string[];
  };
  dragState: {
    isDragging: boolean;
    draggedNodes: string[];
    dropTarget?: string;
  };
  viewMode: 'tree' | 'list' | 'grid';
  sortBy: 'name' | 'size' | 'modified' | 'type';
  sortOrder: 'asc' | 'desc';
  showHidden: boolean;
  loading: boolean;
  error?: string;
}

export interface FileOperation {
  id: string;
  type: 'create' | 'delete' | 'move' | 'copy' | 'rename';
  source: string[];
  target?: string;
  newName?: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  progress?: number;
  error?: string;
  timestamp: Date;
}

export interface FileWatchEvent {
  type: 'created' | 'modified' | 'deleted' | 'moved';
  path: string;
  oldPath?: string;
  stats?: {
    size: number;
    modified: Date;
    isDirectory: boolean;
  };
  timestamp: Date;
}

export interface FileSearchOptions {
  query: string;
  caseSensitive: boolean;
  regex: boolean;
  includeContent: boolean;
  fileTypes: string[];
  excludePatterns: string[];
  maxResults: number;
}

export interface FilePreview {
  path: string;
  type: 'text' | 'image' | 'video' | 'audio' | 'binary' | 'archive';
  content?: string;
  metadata?: {
    encoding?: string;
    lineCount?: number;
    wordCount?: number;
    dimensions?: { width: number; height: number };
    duration?: number;
    [key: string]: any;
  };
}

export interface ContextMenuAction {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  disabled?: boolean;
  separator?: boolean;
  submenu?: ContextMenuAction[];
  action: (nodes: string[]) => void;
}

export interface FileIconMapping {
  extension: string;
  icon: string;
  color?: string;
}

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: string;
  description: string;
}

export interface VirtualizedTreeProps {
  height: number;
  width: number;
  itemHeight: number;
  overscan?: number;
}

export interface FileExplorerProps extends BaseComponentProps {
  rootPath?: string;
  height?: number;
  width?: number;
  showSearch?: boolean;
  showContextMenu?: boolean;
  enableDragDrop?: boolean;
  enableKeyboardNavigation?: boolean;
  enableVirtualization?: boolean;
  multiSelect?: boolean;
  customActions?: ContextMenuAction[];
  onFileSelect?: (nodes: FileSystemNode[]) => void;
  onFileOpen?: (node: FileSystemNode) => void;
  onFileOperation?: (operation: FileOperation) => void;
  onError?: (error: string) => void;
}

export interface UseFileExplorerReturn {
  state: FileExplorerState;
  actions: {
    loadDirectory: (path: string) => Promise<void>;
    createNode: (parentPath: string, name: string, type: 'file' | 'directory') => Promise<void>;
    deleteNodes: (paths: string[]) => Promise<void>;
    moveNodes: (sources: string[], target: string) => Promise<void>;
    copyNodes: (sources: string[], target: string) => Promise<void>;
    renameNode: (path: string, newName: string) => Promise<void>;
    expandNode: (path: string) => void;
    collapseNode: (path: string) => void;
    selectNode: (path: string, multiSelect?: boolean) => void;
    searchFiles: (query: string, options?: Partial<FileSearchOptions>) => Promise<void>;
    clearSearch: () => void;
    copyToClipboard: (paths: string[]) => void;
    cutToClipboard: (paths: string[]) => void;
    pasteFromClipboard: (targetPath: string) => Promise<void>;
    refreshDirectory: (path?: string) => Promise<void>;
    setViewMode: (mode: FileExplorerState['viewMode']) => void;
    setSortOptions: (sortBy: FileExplorerState['sortBy'], sortOrder: FileExplorerState['sortOrder']) => void;
    toggleHidden: () => void;
  };
  utils: {
    getNodeIcon: (node: FileSystemNode) => string;
    getNodeColor: (node: FileSystemNode) => string;
    formatFileSize: (bytes: number) => string;
    formatDate: (date: Date) => string;
    isValidFileName: (name: string) => boolean;
    getRelativePath: (fullPath: string, basePath: string) => string;
  };
}