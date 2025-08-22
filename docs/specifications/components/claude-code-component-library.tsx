/**
 * Claude Code IDE - React Component Library
 * Implementation examples for the PWA wireframe components
 * 
 * This file demonstrates how to implement the key components
 * from the wireframes using React with TypeScript and proper
 * accessibility features.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';

// ================================
// TYPE DEFINITIONS
// ================================

interface FileTreeItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileTreeItem[];
  expanded?: boolean;
  modified?: boolean;
}

interface ClaudeSession {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'error';
  createdAt: Date;
  lastActivity: Date;
  messageCount: number;
}

interface EditorTab {
  id: string;
  title: string;
  filePath: string;
  content: string;
  modified: boolean;
  language: string;
}

interface TerminalSession {
  id: string;
  name: string;
  cwd: string;
  history: TerminalLine[];
}

interface TerminalLine {
  id: string;
  type: 'command' | 'output' | 'error';
  content: string;
  timestamp: Date;
}

// ================================
// FILE EXPLORER COMPONENT
// ================================

interface FileExplorerProps {
  items: FileTreeItem[];
  selectedId?: string;
  onItemSelect: (item: FileTreeItem) => void;
  onItemCreate: (parentId: string, type: 'file' | 'folder', name: string) => void;
  onItemDelete: (item: FileTreeItem) => void;
  onItemRename: (item: FileTreeItem, newName: string) => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  items,
  selectedId,
  onItemSelect,
  onItemCreate,
  onItemDelete,
  onItemRename,
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    item: FileTreeItem;
  } | null>(null);

  const toggleExpanded = useCallback((itemId: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  }, []);

  const handleContextMenu = useCallback((e: React.MouseEvent, item: FileTreeItem) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      item,
    });
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent, item: FileTreeItem) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        if (item.type === 'folder') {
          toggleExpanded(item.id);
        } else {
          onItemSelect(item);
        }
        break;
      case 'ArrowRight':
        if (item.type === 'folder' && !expandedItems.has(item.id)) {
          toggleExpanded(item.id);
        }
        break;
      case 'ArrowLeft':
        if (item.type === 'folder' && expandedItems.has(item.id)) {
          toggleExpanded(item.id);
        }
        break;
      case 'F2':
        // Trigger rename
        break;
      case 'Delete':
        onItemDelete(item);
        break;
    }
  }, [expandedItems, toggleExpanded, onItemSelect, onItemDelete]);

  const renderItem = (item: FileTreeItem, level: number = 0): React.ReactNode => {
    const isExpanded = expandedItems.has(item.id);
    const isSelected = selectedId === item.id;
    const hasChildren = item.children && item.children.length > 0;

    return (
      <div key={item.id} role="treeitem" aria-expanded={item.type === 'folder' ? isExpanded : undefined}>
        <div
          className={`file-tree-item ${item.type} ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 1.5 + 0.5}rem` }}
          onClick={() => {
            if (item.type === 'folder') {
              toggleExpanded(item.id);
            } else {
              onItemSelect(item);
            }
          }}
          onContextMenu={(e) => handleContextMenu(e, item)}
          onKeyDown={(e) => handleKeyDown(e, item)}
          tabIndex={0}
          aria-selected={isSelected}
          aria-label={`${item.type} ${item.name}${item.modified ? ' (modified)' : ''}`}
        >
          <span className="icon" aria-hidden="true">
            {item.type === 'folder' ? (
              isExpanded ? '📂' : '📁'
            ) : (
              getFileIcon(item.name)
            )}
          </span>
          <span className="name">{item.name}</span>
          {item.modified && <span className="modified-indicator" aria-label="modified">●</span>}
        </div>
        
        {item.type === 'folder' && isExpanded && hasChildren && (
          <div role="group">
            {item.children!.map(child => renderItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="file-explorer" role="tree" aria-label="File explorer">
      <div className="sidebar-header">
        <span>Explorer</span>
        <div className="header-actions">
          <button
            className="btn-icon btn-icon-sm"
            onClick={() => onItemCreate('root', 'file', 'new-file.txt')}
            aria-label="New file"
            title="New file"
          >
            📄
          </button>
          <button
            className="btn-icon btn-icon-sm"
            onClick={() => onItemCreate('root', 'folder', 'new-folder')}
            aria-label="New folder"
            title="New folder"
          >
            📁
          </button>
        </div>
      </div>
      <div className="sidebar-content">
        {items.map(item => renderItem(item))}
      </div>
      
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onClose={() => setContextMenu(null)}
          items={[
            { label: 'Open', action: () => onItemSelect(contextMenu.item) },
            { separator: true },
            { label: 'New File', action: () => onItemCreate(contextMenu.item.id, 'file', 'new-file.txt') },
            { label: 'New Folder', action: () => onItemCreate(contextMenu.item.id, 'folder', 'new-folder') },
            { separator: true },
            { label: 'Rename', action: () => {} },
            { label: 'Delete', action: () => onItemDelete(contextMenu.item) },
          ]}
        />
      )}
    </div>
  );
};

// Helper function to get file icon based on extension
const getFileIcon = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase();
  const iconMap: Record<string, string> = {
    'ts': '🔷',
    'tsx': '⚛️',
    'js': '💛',
    'jsx': '⚛️',
    'html': '🌐',
    'css': '🎨',
    'scss': '💅',
    'json': '📦',
    'md': '📝',
    'png': '🖼️',
    'jpg': '🖼️',
    'svg': '🎯',
    'default': '📄'
  };
  return iconMap[ext || 'default'] || iconMap.default;
};

// ================================
// CONTEXT MENU COMPONENT
// ================================

interface ContextMenuItem {
  label?: string;
  action?: () => void;
  separator?: boolean;
  disabled?: boolean;
}

interface ContextMenuProps {
  x: number;
  y: number;
  items: ContextMenuItem[];
  onClose: () => void;
}

const ContextMenu: React.FC<ContextMenuProps> = ({ x, y, items, onClose }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      className="dropdown-menu"
      style={{
        position: 'fixed',
        top: y,
        left: x,
        opacity: 1,
        visibility: 'visible',
        transform: 'translateY(0)',
      }}
      role="menu"
      aria-label="Context menu"
    >
      {items.map((item, index) => (
        item.separator ? (
          <div key={index} className="dropdown-separator" role="separator" />
        ) : (
          <button
            key={index}
            className="dropdown-item"
            onClick={() => {
              item.action?.();
              onClose();
            }}
            disabled={item.disabled}
            role="menuitem"
          >
            {item.label}
          </button>
        )
      ))}
    </div>
  );
};

// ================================
// EDITOR TABS COMPONENT
// ================================

interface EditorTabsProps {
  tabs: EditorTab[];
  activeTabId: string;
  onTabSelect: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
  onTabMove: (fromIndex: number, toIndex: number) => void;
}

export const EditorTabs: React.FC<EditorTabsProps> = ({
  tabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onTabMove,
}) => {
  const tabsRef = useRef<HTMLDivElement>(null);

  const handleKeyDown = useCallback((e: React.KeyboardEvent, tabId: string) => {
    const currentIndex = tabs.findIndex(tab => tab.id === tabId);
    
    switch (e.key) {
      case 'ArrowLeft':
        if (currentIndex > 0) {
          onTabSelect(tabs[currentIndex - 1].id);
        }
        break;
      case 'ArrowRight':
        if (currentIndex < tabs.length - 1) {
          onTabSelect(tabs[currentIndex + 1].id);
        }
        break;
      case 'Delete':
      case 'Backspace':
        onTabClose(tabId);
        break;
    }
  }, [tabs, onTabSelect, onTabClose]);

  return (
    <div className="editor-tabs" role="tablist" ref={tabsRef}>
      {tabs.map((tab, index) => (
        <button
          key={tab.id}
          className={`editor-tab ${tab.id === activeTabId ? 'active' : ''} ${tab.modified ? 'modified' : ''}`}
          role="tab"
          aria-selected={tab.id === activeTabId}
          aria-controls={`editor-content-${tab.id}`}
          tabIndex={tab.id === activeTabId ? 0 : -1}
          onClick={() => onTabSelect(tab.id)}
          onKeyDown={(e) => handleKeyDown(e, tab.id)}
          title={`${tab.filePath}${tab.modified ? ' (modified)' : ''}`}
        >
          <span className="icon" aria-hidden="true">
            {getFileIcon(tab.title)}
          </span>
          <span className="title">{tab.title}</span>
          <button
            className="close-button"
            onClick={(e) => {
              e.stopPropagation();
              onTabClose(tab.id);
            }}
            aria-label={`Close ${tab.title}`}
            title="Close tab"
          >
            ×
          </button>
        </button>
      ))}
    </div>
  );
};

// ================================
// CLAUDE SESSION MANAGER
// ================================

interface ClaudeSessionManagerProps {
  sessions: ClaudeSession[];
  activeSessionId?: string;
  onSessionCreate: (name: string) => void;
  onSessionSelect: (sessionId: string) => void;
  onSessionDelete: (sessionId: string) => void;
}

export const ClaudeSessionManager: React.FC<ClaudeSessionManagerProps> = ({
  sessions,
  activeSessionId,
  onSessionCreate,
  onSessionSelect,
  onSessionDelete,
}) => {
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');

  const handleCreateSession = useCallback(() => {
    if (newSessionName.trim()) {
      onSessionCreate(newSessionName.trim());
      setNewSessionName('');
      setIsCreatingSession(false);
    }
  }, [newSessionName, onSessionCreate]);

  const getStatusIcon = (status: ClaudeSession['status']) => {
    switch (status) {
      case 'active':
        return '🟢';
      case 'paused':
        return '🟡';
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const formatLastActivity = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="claude-session-manager">
      <div className="sidebar-header">
        <span>Claude Sessions</span>
        <button
          className="btn-icon btn-icon-sm"
          onClick={() => setIsCreatingSession(true)}
          aria-label="Create new session"
          title="New session"
        >
          ➕
        </button>
      </div>
      
      <div className="sidebar-content">
        {isCreatingSession && (
          <div className="session-item" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <input
              type="text"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder="Session name..."
              className="form-input"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateSession();
                if (e.key === 'Escape') setIsCreatingSession(false);
              }}
              aria-label="New session name"
            />
            <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
              <button
                className="btn btn-primary btn-sm"
                onClick={handleCreateSession}
                disabled={!newSessionName.trim()}
              >
                Create
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setIsCreatingSession(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
        
        <div className="session-list" role="list">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => onSessionSelect(session.id)}
              role="listitem button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  onSessionSelect(session.id);
                }
              }}
              aria-selected={session.id === activeSessionId}
              title={`Session: ${session.name} - ${session.status}`}
            >
              <div className="session-info">
                <div className="session-name">{session.name}</div>
                <div className="session-status">
                  {session.status} • {formatLastActivity(session.lastActivity)}
                </div>
                <div className="session-meta">
                  {session.messageCount} messages
                </div>
              </div>
              <div className="session-actions">
                <span
                  className={`session-indicator ${session.status}`}
                  aria-label={`Status: ${session.status}`}
                  role="img"
                >
                  {getStatusIcon(session.status)}
                </span>
                {session.id !== activeSessionId && (
                  <button
                    className="btn-icon btn-icon-sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSessionDelete(session.id);
                    }}
                    aria-label={`Delete session ${session.name}`}
                    title="Delete session"
                  >
                    🗑️
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ================================
// TERMINAL COMPONENT
// ================================

interface TerminalProps {
  session: TerminalSession;
  onCommand: (command: string) => void;
  onClear: () => void;
}

export const Terminal: React.FC<TerminalProps> = ({ session, onCommand, onClear }) => {
  const [currentCommand, setCurrentCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new content is added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [session.history]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (currentCommand.trim()) {
      onCommand(currentCommand);
      setCommandHistory(prev => [...prev, currentCommand]);
      setCurrentCommand('');
      setHistoryIndex(-1);
    }
  }, [currentCommand, onCommand]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
          const newIndex = historyIndex + 1;
          setHistoryIndex(newIndex);
          setCurrentCommand(commandHistory[commandHistory.length - 1 - newIndex]);
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          setCurrentCommand(commandHistory[commandHistory.length - 1 - newIndex]);
        } else if (historyIndex === 0) {
          setHistoryIndex(-1);
          setCurrentCommand('');
        }
        break;
      case 'Tab':
        e.preventDefault();
        // TODO: Implement command completion
        break;
    }
  }, [historyIndex, commandHistory]);

  const renderLine = (line: TerminalLine) => (
    <div key={line.id} className="terminal-line">
      {line.type === 'command' && (
        <>
          <span className="terminal-prompt" aria-label="Command prompt">
            $ 
          </span>
          <span className="terminal-command">{line.content}</span>
        </>
      )}
      {line.type === 'output' && (
        <span className="terminal-output">{line.content}</span>
      )}
      {line.type === 'error' && (
        <span className="terminal-error">{line.content}</span>
      )}
    </div>
  );

  return (
    <div className="ide-terminal">
      <div className="terminal-header">
        <span>Terminal - {session.name}</span>
        <div className="header-actions">
          <button
            className="btn-icon btn-icon-sm"
            onClick={onClear}
            aria-label="Clear terminal"
            title="Clear terminal"
          >
            🗑️
          </button>
          <button
            className="btn-icon btn-icon-sm"
            onClick={() => inputRef.current?.focus()}
            aria-label="Focus terminal input"
            title="Focus input"
          >
            ⌨️
          </button>
        </div>
      </div>
      
      <div
        className="terminal-content"
        ref={terminalRef}
        onClick={() => inputRef.current?.focus()}
        role="log"
        aria-label="Terminal output"
        aria-live="polite"
      >
        {session.history.map(renderLine)}
        
        <form onSubmit={handleSubmit} className="terminal-line">
          <span className="terminal-prompt" aria-hidden="true">$ </span>
          <input
            ref={inputRef}
            type="text"
            value={currentCommand}
            onChange={(e) => setCurrentCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            className="terminal-input"
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'inherit',
              font: 'inherit',
              flex: 1,
            }}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
            aria-label="Terminal command input"
            placeholder="Enter command..."
          />
          <span className="terminal-cursor">█</span>
        </form>
      </div>
    </div>
  );
};

// ================================
// MOBILE NAVIGATION COMPONENT
// ================================

interface MobileNavItem {
  id: string;
  label: string;
  icon: string;
  href: string;
  badge?: string | number;
}

interface MobileNavigationProps {
  items: MobileNavItem[];
  activeItemId: string;
  onItemSelect: (itemId: string) => void;
}

export const MobileNavigation: React.FC<MobileNavigationProps> = ({
  items,
  activeItemId,
  onItemSelect,
}) => {
  return (
    <nav className="mobile-nav" role="navigation" aria-label="Main navigation">
      {items.map((item) => (
        <button
          key={item.id}
          className={`mobile-nav-item ${item.id === activeItemId ? 'active' : ''}`}
          onClick={() => onItemSelect(item.id)}
          aria-label={item.label}
          aria-current={item.id === activeItemId ? 'page' : undefined}
        >
          <div className="mobile-nav-icon" aria-hidden="true">
            {item.icon}
          </div>
          <span>{item.label}</span>
          {item.badge && (
            <span className="mobile-nav-badge" aria-label={`${item.badge} notifications`}>
              {item.badge}
            </span>
          )}
        </button>
      ))}
    </nav>
  );
};

// ================================
// ACCESSIBLE MODAL COMPONENT
// ================================

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Focus management
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousActiveElement.current?.focus();
    }
  }, [isOpen]);

  // Trap focus within modal
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }

      if (e.key === 'Tab') {
        const modal = modalRef.current;
        if (!modal) return;

        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className={`modal modal-${size}`}
        tabIndex={-1}
      >
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">
            {title}
          </h2>
          <button
            className="modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            ×
          </button>
        </div>
        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>
  );
};

// ================================
// USAGE EXAMPLES
// ================================

export const ClaudeCodeIDE: React.FC = () => {
  // State management would typically be handled by a global state manager
  const [fileTreeItems] = useState<FileTreeItem[]>([
    {
      id: '1',
      name: 'claude-code-project',
      type: 'folder',
      path: '/claude-code-project',
      children: [
        {
          id: '2',
          name: 'src',
          type: 'folder',
          path: '/claude-code-project/src',
          children: [
            {
              id: '3',
              name: 'App.tsx',
              type: 'file',
              path: '/claude-code-project/src/App.tsx',
              modified: true,
            },
            {
              id: '4',
              name: 'index.tsx',
              type: 'file',
              path: '/claude-code-project/src/index.tsx',
            },
          ],
        },
        {
          id: '5',
          name: 'package.json',
          type: 'file',
          path: '/claude-code-project/package.json',
        },
      ],
    },
  ]);

  const [sessions] = useState<ClaudeSession[]>([
    {
      id: '1',
      name: 'Main Development',
      status: 'active',
      createdAt: new Date(Date.now() - 7200000), // 2 hours ago
      lastActivity: new Date(Date.now() - 300000), // 5 minutes ago
      messageCount: 24,
    },
    {
      id: '2',
      name: 'Testing Branch',
      status: 'paused',
      createdAt: new Date(Date.now() - 14400000), // 4 hours ago
      lastActivity: new Date(Date.now() - 2700000), // 45 minutes ago
      messageCount: 12,
    },
  ]);

  const [editorTabs] = useState<EditorTab[]>([
    {
      id: '1',
      title: 'App.tsx',
      filePath: '/claude-code-project/src/App.tsx',
      content: 'import React from "react";\n\nfunction App() {\n  return <div>Hello World</div>;\n}',
      modified: true,
      language: 'typescript',
    },
    {
      id: '2',
      title: 'package.json',
      filePath: '/claude-code-project/package.json',
      content: '{\n  "name": "claude-code-project",\n  "version": "1.0.0"\n}',
      modified: false,
      language: 'json',
    },
  ]);

  const [terminalSession] = useState<TerminalSession>({
    id: '1',
    name: 'main',
    cwd: '/claude-code-project',
    history: [
      {
        id: '1',
        type: 'command',
        content: 'npm install',
        timestamp: new Date(Date.now() - 300000),
      },
      {
        id: '2',
        type: 'output',
        content: '✓ Installed 1,234 packages in 45s',
        timestamp: new Date(Date.now() - 295000),
      },
      {
        id: '3',
        type: 'command',
        content: 'npm run dev',
        timestamp: new Date(Date.now() - 180000),
      },
      {
        id: '4',
        type: 'output',
        content: 'Server running on http://localhost:3000',
        timestamp: new Date(Date.now() - 175000),
      },
    ],
  });

  return (
    <div className="ide-layout">
      {/* Header would include menu bar, search, etc. */}
      
      {/* Sidebar with file explorer and session manager */}
      <aside className="ide-sidebar">
        <FileExplorer
          items={fileTreeItems}
          selectedId="3"
          onItemSelect={(item) => console.log('Selected:', item)}
          onItemCreate={(parentId, type, name) => console.log('Create:', { parentId, type, name })}
          onItemDelete={(item) => console.log('Delete:', item)}
          onItemRename={(item, newName) => console.log('Rename:', { item, newName })}
        />
        
        <ClaudeSessionManager
          sessions={sessions}
          activeSessionId="1"
          onSessionCreate={(name) => console.log('Create session:', name)}
          onSessionSelect={(sessionId) => console.log('Select session:', sessionId)}
          onSessionDelete={(sessionId) => console.log('Delete session:', sessionId)}
        />
      </aside>

      {/* Main editor area */}
      <main className="ide-editor">
        <EditorTabs
          tabs={editorTabs}
          activeTabId="1"
          onTabSelect={(tabId) => console.log('Select tab:', tabId)}
          onTabClose={(tabId) => console.log('Close tab:', tabId)}
          onTabMove={(fromIndex, toIndex) => console.log('Move tab:', { fromIndex, toIndex })}
        />
        
        <div className="editor-content" id="editor-content-1" role="tabpanel">
          {/* Monaco Editor would be rendered here */}
          <div style={{ padding: 'var(--space-4)', fontFamily: 'var(--font-family-mono)' }}>
            <pre>{editorTabs.find(tab => tab.id === '1')?.content}</pre>
          </div>
        </div>
      </main>

      {/* Terminal panel */}
      <Terminal
        session={terminalSession}
        onCommand={(command) => console.log('Execute command:', command)}
        onClear={() => console.log('Clear terminal')}
      />
    </div>
  );
};

export default ClaudeCodeIDE;