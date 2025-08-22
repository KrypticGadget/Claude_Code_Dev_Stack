import React, { useState, useEffect, useCallback } from 'react';
import { 
  Folder, 
  File, 
  ChevronRight, 
  ChevronDown, 
  Search, 
  Filter, 
  Plus, 
  Edit3, 
  Trash2, 
  Copy, 
  Move,
  Eye,
  Code,
  Image,
  FileText,
  Database,
  Archive,
  Settings
} from 'lucide-react';
import './SessionFileExplorer.css';

// Types for file system navigation
interface FileSystemItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: Date;
  children?: FileSystemItem[];
  isExpanded?: boolean;
  isLoaded?: boolean;
  fileType?: string;
  encoding?: string;
  permissions?: string;
}

interface SessionFileExplorerProps {
  sessionId: string;
  sessionPath: string;
  onFileSelect?: (file: FileSystemItem) => void;
  onPathChange?: (path: string) => void;
  onCreateSession?: (path: string) => void;
  className?: string;
}

export const SessionFileExplorer: React.FC<SessionFileExplorerProps> = ({
  sessionId,
  sessionPath,
  onFileSelect,
  onPathChange,
  onCreateSession,
  className
}) => {
  const [fileTree, setFileTree] = useState<FileSystemItem[]>([]);
  const [currentPath, setCurrentPath] = useState(sessionPath);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFile, setSelectedFile] = useState<FileSystemItem | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showHidden, setShowHidden] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'files' | 'directories'>('all');
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    item: FileSystemItem;
  } | null>(null);

  // Simulate file system API calls
  const loadDirectory = useCallback(async (path: string): Promise<FileSystemItem[]> => {
    setIsLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Mock file system data
    const mockFiles: FileSystemItem[] = [
      {
        name: 'src',
        path: `${path}\\src`,
        type: 'directory',
        modified: new Date('2024-01-15'),
        children: [
          {
            name: 'components',
            path: `${path}\\src\\components`,
            type: 'directory',
            modified: new Date('2024-01-14'),
            children: [
              {
                name: 'SessionManager.tsx',
                path: `${path}\\src\\components\\SessionManager.tsx`,
                type: 'file',
                size: 15420,
                modified: new Date('2024-01-15'),
                fileType: 'typescript',
                encoding: 'utf-8'
              },
              {
                name: 'FileExplorer.tsx',
                path: `${path}\\src\\components\\FileExplorer.tsx`,
                type: 'file',
                size: 8930,
                modified: new Date('2024-01-14'),
                fileType: 'typescript',
                encoding: 'utf-8'
              }
            ]
          },
          {
            name: 'hooks',
            path: `${path}\\src\\hooks`,
            type: 'directory',
            modified: new Date('2024-01-13'),
            children: [
              {
                name: 'useLocalStorage.ts',
                path: `${path}\\src\\hooks\\useLocalStorage.ts`,
                type: 'file',
                size: 2450,
                modified: new Date('2024-01-13'),
                fileType: 'typescript',
                encoding: 'utf-8'
              }
            ]
          },
          {
            name: 'App.tsx',
            path: `${path}\\src\\App.tsx`,
            type: 'file',
            size: 3250,
            modified: new Date('2024-01-15'),
            fileType: 'typescript',
            encoding: 'utf-8'
          },
          {
            name: 'index.css',
            path: `${path}\\src\\index.css`,
            type: 'file',
            size: 12500,
            modified: new Date('2024-01-12'),
            fileType: 'css',
            encoding: 'utf-8'
          }
        ]
      },
      {
        name: 'public',
        path: `${path}\\public`,
        type: 'directory',
        modified: new Date('2024-01-10'),
        children: [
          {
            name: 'index.html',
            path: `${path}\\public\\index.html`,
            type: 'file',
            size: 2100,
            modified: new Date('2024-01-10'),
            fileType: 'html',
            encoding: 'utf-8'
          },
          {
            name: 'manifest.json',
            path: `${path}\\public\\manifest.json`,
            type: 'file',
            size: 890,
            modified: new Date('2024-01-08'),
            fileType: 'json',
            encoding: 'utf-8'
          }
        ]
      },
      {
        name: 'package.json',
        path: `${path}\\package.json`,
        type: 'file',
        size: 1500,
        modified: new Date('2024-01-15'),
        fileType: 'json',
        encoding: 'utf-8'
      },
      {
        name: 'README.md',
        path: `${path}\\README.md`,
        type: 'file',
        size: 3400,
        modified: new Date('2024-01-12'),
        fileType: 'markdown',
        encoding: 'utf-8'
      },
      {
        name: '.gitignore',
        path: `${path}\\.gitignore`,
        type: 'file',
        size: 650,
        modified: new Date('2024-01-08'),
        fileType: 'text',
        encoding: 'utf-8'
      },
      {
        name: 'node_modules',
        path: `${path}\\node_modules`,
        type: 'directory',
        modified: new Date('2024-01-15'),
        children: [] // Would be populated on expand
      }
    ];

    setIsLoading(false);
    return mockFiles;
  }, []);

  // Load initial directory
  useEffect(() => {
    loadDirectory(currentPath).then(setFileTree);
  }, [currentPath, loadDirectory]);

  // Toggle directory expansion
  const toggleDirectory = useCallback(async (item: FileSystemItem) => {
    if (item.type !== 'directory') return;

    const updateTree = (items: FileSystemItem[]): FileSystemItem[] => {
      return items.map(node => {
        if (node.path === item.path) {
          const isExpanding = !node.isExpanded;
          return {
            ...node,
            isExpanded: isExpanding,
            children: isExpanding && !node.isLoaded 
              ? [] // Will be loaded async
              : node.children,
            isLoaded: node.isLoaded || !isExpanding
          };
        }
        if (node.children) {
          return {
            ...node,
            children: updateTree(node.children)
          };
        }
        return node;
      });
    };

    setFileTree(updateTree);

    // Load children if expanding and not loaded
    if (!item.isExpanded && !item.isLoaded) {
      const children = await loadDirectory(item.path);
      setFileTree(prev => {
        const updateWithChildren = (items: FileSystemItem[]): FileSystemItem[] => {
          return items.map(node => {
            if (node.path === item.path) {
              return {
                ...node,
                children,
                isLoaded: true
              };
            }
            if (node.children) {
              return {
                ...node,
                children: updateWithChildren(node.children)
              };
            }
            return node;
          });
        };
        return updateWithChildren(prev);
      });
    }
  }, [loadDirectory]);

  // Handle file selection
  const handleFileSelect = useCallback((item: FileSystemItem) => {
    setSelectedFile(item);
    onFileSelect?.(item);
  }, [onFileSelect]);

  // Navigate to path
  const navigateToPath = useCallback((path: string) => {
    setCurrentPath(path);
    onPathChange?.(path);
  }, [onPathChange]);

  // Get file icon based on file type
  const getFileIcon = (item: FileSystemItem) => {
    if (item.type === 'directory') {
      return item.isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />;
    }

    const { fileType } = item;
    switch (fileType) {
      case 'typescript':
      case 'javascript':
      case 'jsx':
      case 'tsx':
        return <Code size={16} className="file-icon code" />;
      case 'css':
      case 'scss':
      case 'less':
        return <Code size={16} className="file-icon style" />;
      case 'html':
      case 'xml':
        return <Code size={16} className="file-icon markup" />;
      case 'json':
      case 'yaml':
      case 'yml':
        return <Database size={16} className="file-icon data" />;
      case 'markdown':
      case 'md':
        return <FileText size={16} className="file-icon text" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
      case 'webp':
        return <Image size={16} className="file-icon image" />;
      case 'zip':
      case 'tar':
      case 'gz':
      case 'rar':
        return <Archive size={16} className="file-icon archive" />;
      default:
        return <File size={16} className="file-icon default" />;
    }
  };

  // Context menu handling
  const handleContextMenu = useCallback((e: React.MouseEvent, item: FileSystemItem) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      item
    });
  }, []);

  const closeContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  // Context menu actions
  const contextMenuActions = [
    {
      label: 'Open',
      icon: <Eye size={14} />,
      action: (item: FileSystemItem) => handleFileSelect(item)
    },
    {
      label: 'Create Session Here',
      icon: <Plus size={14} />,
      action: (item: FileSystemItem) => {
        const path = item.type === 'directory' ? item.path : item.path.split('\\').slice(0, -1).join('\\');
        onCreateSession?.(path);
      }
    },
    {
      label: 'Copy Path',
      icon: <Copy size={14} />,
      action: (item: FileSystemItem) => {
        navigator.clipboard.writeText(item.path);
      }
    },
    {
      label: 'Rename',
      icon: <Edit3 size={14} />,
      action: (item: FileSystemItem) => {
        // Would open rename dialog
        console.log('Rename:', item.path);
      }
    },
    {
      label: 'Delete',
      icon: <Trash2 size={14} />,
      action: (item: FileSystemItem) => {
        // Would confirm and delete
        console.log('Delete:', item.path);
      },
      destructive: true
    }
  ];

  // Filter files based on search and settings
  const filterItems = useCallback((items: FileSystemItem[]): FileSystemItem[] => {
    return items.filter(item => {
      // Hide hidden files unless enabled
      if (!showHidden && item.name.startsWith('.')) {
        return false;
      }

      // Filter by type
      if (filterType !== 'all') {
        if (filterType === 'files' && item.type !== 'file') return false;
        if (filterType === 'directories' && item.type !== 'directory') return false;
      }

      // Search filter
      if (searchTerm) {
        return item.name.toLowerCase().includes(searchTerm.toLowerCase());
      }

      return true;
    }).map(item => ({
      ...item,
      children: item.children ? filterItems(item.children) : undefined
    }));
  }, [showHidden, filterType, searchTerm]);

  const filteredFileTree = filterItems(fileTree);

  // Render file tree recursively
  const renderFileTree = (items: FileSystemItem[], depth = 0) => {
    return items.map(item => (
      <div key={item.path} className="file-tree-item">
        <div
          className={`file-item ${selectedFile?.path === item.path ? 'selected' : ''} ${item.type}`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
          onClick={() => {
            if (item.type === 'directory') {
              toggleDirectory(item);
            } else {
              handleFileSelect(item);
            }
          }}
          onContextMenu={(e) => handleContextMenu(e, item)}
        >
          <div className="file-item-content">
            <div className="file-icon-container">
              {item.type === 'directory' && <Folder size={16} className="folder-icon" />}
              {getFileIcon(item)}
            </div>
            
            <span className="file-name">{item.name}</span>
            
            {item.type === 'file' && (
              <span className="file-size">
                {item.size ? formatFileSize(item.size) : ''}
              </span>
            )}
          </div>
        </div>
        
        {item.type === 'directory' && item.isExpanded && item.children && (
          <div className="file-children">
            {renderFileTree(item.children, depth + 1)}
          </div>
        )}
      </div>
    ));
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className={`session-file-explorer ${className || ''}`}>
      {/* Header */}
      <div className="file-explorer-header">
        <div className="path-breadcrumb">
          <span className="path-label">Path:</span>
          <div className="breadcrumb-items">
            {currentPath.split('\\').map((segment, index, array) => {
              const path = array.slice(0, index + 1).join('\\');
              return (
                <span key={index} className="breadcrumb-item">
                  <button
                    onClick={() => navigateToPath(path)}
                    className="breadcrumb-button"
                  >
                    {segment || 'Root'}
                  </button>
                  {index < array.length - 1 && <span className="breadcrumb-separator">\\</span>}
                </span>
              );
            })}
          </div>
        </div>

        <button
          className="btn btn-primary btn-sm"
          onClick={() => onCreateSession?.(currentPath)}
          title="Create session at current path"
        >
          <Plus size={14} />
          Session
        </button>
      </div>

      {/* Controls */}
      <div className="file-explorer-controls">
        <div className="search-input-wrapper">
          <Search size={14} />
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-controls">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="filter-select"
          >
            <option value="all">All</option>
            <option value="files">Files</option>
            <option value="directories">Folders</option>
          </select>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={showHidden}
              onChange={(e) => setShowHidden(e.target.checked)}
            />
            <span>Hidden</span>
          </label>
        </div>
      </div>

      {/* File Tree */}
      <div className="file-tree-container">
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-spinner" />
            <span>Loading...</span>
          </div>
        )}
        
        <div className="file-tree">
          {renderFileTree(filteredFileTree)}
        </div>
        
        {filteredFileTree.length === 0 && !isLoading && (
          <div className="empty-directory">
            <Folder size={32} className="empty-icon" />
            <p>No files found</p>
          </div>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <>
          <div className="context-menu-overlay" onClick={closeContextMenu} />
          <div
            className="context-menu"
            style={{
              left: contextMenu.x,
              top: contextMenu.y
            }}
          >
            {contextMenuActions.map((action, index) => (
              <button
                key={index}
                className={`context-menu-item ${action.destructive ? 'destructive' : ''}`}
                onClick={() => {
                  action.action(contextMenu.item);
                  closeContextMenu();
                }}
              >
                {action.icon}
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </>
      )}

      {/* Selected File Info */}
      {selectedFile && (
        <div className="selected-file-info">
          <div className="selected-file-header">
            <h4>File Details</h4>
            <button
              onClick={() => setSelectedFile(null)}
              className="close-btn"
            >
              ×
            </button>
          </div>
          
          <div className="file-details">
            <div className="detail-item">
              <span className="detail-label">Name:</span>
              <span className="detail-value">{selectedFile.name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Path:</span>
              <span className="detail-value" title={selectedFile.path}>
                {selectedFile.path}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Type:</span>
              <span className="detail-value">{selectedFile.type}</span>
            </div>
            {selectedFile.size && (
              <div className="detail-item">
                <span className="detail-label">Size:</span>
                <span className="detail-value">{formatFileSize(selectedFile.size)}</span>
              </div>
            )}
            {selectedFile.modified && (
              <div className="detail-item">
                <span className="detail-label">Modified:</span>
                <span className="detail-value">
                  {selectedFile.modified.toLocaleString()}
                </span>
              </div>
            )}
            {selectedFile.fileType && (
              <div className="detail-item">
                <span className="detail-label">File Type:</span>
                <span className="detail-value">{selectedFile.fileType}</span>
              </div>
            )}
          </div>

          <div className="file-actions">
            <button className="btn btn-primary btn-sm">
              <Eye size={14} />
              Preview
            </button>
            <button className="btn btn-secondary btn-sm">
              <Edit3 size={14} />
              Edit
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionFileExplorer;