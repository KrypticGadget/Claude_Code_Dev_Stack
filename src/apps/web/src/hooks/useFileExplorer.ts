import { useState, useCallback, useEffect, useRef } from 'react';
import Fuse from 'fuse.js';
import { 
  FileSystemNode, 
  FileExplorerState, 
  FileOperation, 
  FileSearchOptions, 
  UseFileExplorerReturn,
  FileWatchEvent
} from '../types';
import {
  getNodeIcon,
  getNodeColor,
  formatFileSize,
  formatDate,
  isValidFileName,
  getRelativePath,
  sortNodes,
  filterNodes,
  isHiddenNode,
  generateNodeId,
  getParentPath,
  getFileExtension,
  getMimeType,
  debounce
} from '../utils/fileExplorerUtils';

// Mock file system service - in real implementation, this would be an API
class FileSystemService {
  private nodes: Map<string, FileSystemNode> = new Map();
  private watchers: Set<(event: FileWatchEvent) => void> = new Set();

  // Initialize with some mock data
  constructor() {
    this.initializeMockData();
  }

  private initializeMockData() {
    const mockNodes: FileSystemNode[] = [
      {
        id: 'root',
        name: 'Project Root',
        path: '/',
        type: 'directory',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-20'),
        permissions: { read: true, write: true, execute: true },
        children: ['src', 'public', 'package.json', 'README.md'],
        isExpanded: true
      },
      {
        id: 'src',
        name: 'src',
        path: '/src',
        type: 'directory',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-20'),
        permissions: { read: true, write: true, execute: true },
        parent: 'root',
        children: ['components', 'hooks', 'utils', 'App.tsx', 'main.tsx'],
        isExpanded: false
      },
      {
        id: 'components',
        name: 'components',
        path: '/src/components',
        type: 'directory',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-19'),
        permissions: { read: true, write: true, execute: true },
        parent: 'src',
        children: ['ui', 'layout', 'Button.tsx', 'Modal.tsx'],
        isExpanded: false
      },
      {
        id: 'ui',
        name: 'ui',
        path: '/src/components/ui',
        type: 'directory',
        created: new Date('2024-01-02'),
        modified: new Date('2024-08-18'),
        permissions: { read: true, write: true, execute: true },
        parent: 'components',
        children: ['Input.tsx', 'Card.tsx', 'LoadingSpinner.tsx'],
        isExpanded: false
      },
      {
        id: 'layout',
        name: 'layout',
        path: '/src/components/layout',
        type: 'directory',
        created: new Date('2024-01-02'),
        modified: new Date('2024-08-17'),
        permissions: { read: true, write: true, execute: true },
        parent: 'components',
        children: ['Header.tsx', 'Sidebar.tsx', 'Footer.tsx'],
        isExpanded: false
      },
      {
        id: 'hooks',
        name: 'hooks',
        path: '/src/hooks',
        type: 'directory',
        created: new Date('2024-01-03'),
        modified: new Date('2024-08-16'),
        permissions: { read: true, write: true, execute: true },
        parent: 'src',
        children: ['useFileExplorer.ts', 'useWebSocket.ts'],
        isExpanded: false
      },
      {
        id: 'utils',
        name: 'utils',
        path: '/src/utils',
        type: 'directory',
        created: new Date('2024-01-04'),
        modified: new Date('2024-08-15'),
        permissions: { read: true, write: true, execute: true },
        parent: 'src',
        children: ['fileExplorerUtils.ts', 'apiUtils.ts'],
        isExpanded: false
      },
      {
        id: 'public',
        name: 'public',
        path: '/public',
        type: 'directory',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-14'),
        permissions: { read: true, write: true, execute: true },
        parent: 'root',
        children: ['index.html', 'favicon.ico', 'manifest.json'],
        isExpanded: false
      },
      // Files
      {
        id: 'package-json',
        name: 'package.json',
        path: '/package.json',
        type: 'file',
        size: 2048,
        extension: 'json',
        mimeType: 'application/json',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-13'),
        permissions: { read: true, write: true, execute: false },
        parent: 'root'
      },
      {
        id: 'readme',
        name: 'README.md',
        path: '/README.md',
        type: 'file',
        size: 1024,
        extension: 'md',
        mimeType: 'text/markdown',
        created: new Date('2024-01-01'),
        modified: new Date('2024-08-12'),
        permissions: { read: true, write: true, execute: false },
        parent: 'root'
      },
      {
        id: 'app-tsx',
        name: 'App.tsx',
        path: '/src/App.tsx',
        type: 'file',
        size: 4096,
        extension: 'tsx',
        mimeType: 'text/typescript',
        created: new Date('2024-01-02'),
        modified: new Date('2024-08-11'),
        permissions: { read: true, write: true, execute: false },
        parent: 'src'
      },
      {
        id: 'main-tsx',
        name: 'main.tsx',
        path: '/src/main.tsx',
        type: 'file',
        size: 512,
        extension: 'tsx',
        mimeType: 'text/typescript',
        created: new Date('2024-01-02'),
        modified: new Date('2024-08-10'),
        permissions: { read: true, write: true, execute: false },
        parent: 'src'
      }
    ];

    mockNodes.forEach(node => {
      this.nodes.set(node.id, node);
    });
  }

  async getNode(id: string): Promise<FileSystemNode | null> {
    return this.nodes.get(id) || null;
  }

  async getChildren(parentId: string): Promise<FileSystemNode[]> {
    const parent = this.nodes.get(parentId);
    if (!parent || !parent.children) return [];

    return parent.children
      .map(childId => this.nodes.get(childId))
      .filter((node): node is FileSystemNode => node !== undefined);
  }

  async createNode(parentPath: string, name: string, type: 'file' | 'directory'): Promise<FileSystemNode> {
    const id = generateNodeId(`${parentPath}/${name}`);
    const path = `${parentPath}/${name}`;
    const extension = type === 'file' ? getFileExtension(name) : undefined;
    
    const newNode: FileSystemNode = {
      id,
      name,
      path,
      type,
      size: type === 'file' ? 0 : undefined,
      extension,
      mimeType: extension ? getMimeType(extension) : undefined,
      created: new Date(),
      modified: new Date(),
      permissions: { read: true, write: true, execute: type === 'directory' },
      parent: generateNodeId(parentPath),
      children: type === 'directory' ? [] : undefined
    };

    this.nodes.set(id, newNode);

    // Update parent
    const parent = this.nodes.get(generateNodeId(parentPath));
    if (parent && parent.children) {
      parent.children.push(id);
      parent.modified = new Date();
    }

    this.notifyWatchers({
      type: 'created',
      path,
      stats: {
        size: newNode.size || 0,
        modified: newNode.modified,
        isDirectory: type === 'directory'
      },
      timestamp: new Date()
    });

    return newNode;
  }

  async deleteNode(id: string): Promise<void> {
    const node = this.nodes.get(id);
    if (!node) return;

    // Remove from parent
    if (node.parent) {
      const parent = this.nodes.get(node.parent);
      if (parent && parent.children) {
        parent.children = parent.children.filter(childId => childId !== id);
        parent.modified = new Date();
      }
    }

    // Recursively delete children
    if (node.children) {
      for (const childId of node.children) {
        await this.deleteNode(childId);
      }
    }

    this.nodes.delete(id);

    this.notifyWatchers({
      type: 'deleted',
      path: node.path,
      timestamp: new Date()
    });
  }

  async moveNode(id: string, newParentPath: string): Promise<FileSystemNode> {
    const node = this.nodes.get(id);
    if (!node) throw new Error('Node not found');

    const oldPath = node.path;
    const newPath = `${newParentPath}/${node.name}`;

    // Update node
    node.path = newPath;
    node.parent = generateNodeId(newParentPath);
    node.modified = new Date();

    // Remove from old parent
    if (node.parent) {
      const oldParent = this.nodes.get(node.parent);
      if (oldParent && oldParent.children) {
        oldParent.children = oldParent.children.filter(childId => childId !== id);
      }
    }

    // Add to new parent
    const newParent = this.nodes.get(generateNodeId(newParentPath));
    if (newParent && newParent.children) {
      newParent.children.push(id);
      newParent.modified = new Date();
    }

    this.notifyWatchers({
      type: 'moved',
      path: newPath,
      oldPath,
      timestamp: new Date()
    });

    return node;
  }

  async renameNode(id: string, newName: string): Promise<FileSystemNode> {
    const node = this.nodes.get(id);
    if (!node) throw new Error('Node not found');

    const oldPath = node.path;
    const pathParts = node.path.split('/');
    pathParts[pathParts.length - 1] = newName;
    const newPath = pathParts.join('/');

    node.name = newName;
    node.path = newPath;
    node.modified = new Date();

    if (node.type === 'file') {
      const extension = getFileExtension(newName);
      node.extension = extension;
      node.mimeType = extension ? getMimeType(extension) : undefined;
    }

    this.notifyWatchers({
      type: 'moved',
      path: newPath,
      oldPath,
      timestamp: new Date()
    });

    return node;
  }

  addWatcher(callback: (event: FileWatchEvent) => void): () => void {
    this.watchers.add(callback);
    return () => this.watchers.delete(callback);
  }

  private notifyWatchers(event: FileWatchEvent): void {
    this.watchers.forEach(callback => callback(event));
  }

  async searchFiles(query: string, options: Partial<FileSearchOptions> = {}): Promise<FileSystemNode[]> {
    const allNodes = Array.from(this.nodes.values());
    const searchOptions: FileSearchOptions = {
      query,
      caseSensitive: false,
      regex: false,
      includeContent: false,
      fileTypes: [],
      excludePatterns: [],
      maxResults: 100,
      ...options
    };

    let results = allNodes;

    // Filter by file types
    if (searchOptions.fileTypes.length > 0) {
      results = results.filter(node => 
        node.type === 'directory' || 
        (node.extension && searchOptions.fileTypes.includes(node.extension))
      );
    }

    // Exclude patterns
    if (searchOptions.excludePatterns.length > 0) {
      results = results.filter(node => 
        !searchOptions.excludePatterns.some(pattern => 
          node.path.includes(pattern) || node.name.includes(pattern)
        )
      );
    }

    // Use Fuse.js for fuzzy search
    const fuse = new Fuse(results, {
      keys: ['name', 'path'],
      threshold: 0.4,
      includeScore: true,
      ignoreCase: !searchOptions.caseSensitive
    });

    const fuseResults = fuse.search(searchOptions.query);
    return fuseResults
      .slice(0, searchOptions.maxResults)
      .map(result => result.item);
  }
}

const fileSystemService = new FileSystemService();

export function useFileExplorer(rootPath: string = '/'): UseFileExplorerReturn {
  const [state, setState] = useState<FileExplorerState>({
    nodes: {},
    rootNodes: [],
    selectedNodes: [],
    expandedNodes: new Set(),
    currentPath: rootPath,
    searchQuery: '',
    searchResults: [],
    clipboard: {
      operation: null,
      nodes: []
    },
    dragState: {
      isDragging: false,
      draggedNodes: []
    },
    viewMode: 'tree',
    sortBy: 'name',
    sortOrder: 'asc',
    showHidden: false,
    loading: false
  });

  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Initialize file system
  useEffect(() => {
    loadDirectory(rootPath);
  }, [rootPath]);

  // Set up file system watcher
  useEffect(() => {
    const unwatch = fileSystemService.addWatcher((event: FileWatchEvent) => {
      // Handle file system changes
      switch (event.type) {
        case 'created':
        case 'modified':
          refreshDirectory(getParentPath(event.path));
          break;
        case 'deleted':
          setState(prev => {
            const newNodes = { ...prev.nodes };
            const nodeId = generateNodeId(event.path);
            delete newNodes[nodeId];
            
            return {
              ...prev,
              nodes: newNodes,
              selectedNodes: prev.selectedNodes.filter(id => id !== nodeId)
            };
          });
          break;
        case 'moved':
          if (event.oldPath) {
            refreshDirectory(getParentPath(event.oldPath));
          }
          refreshDirectory(getParentPath(event.path));
          break;
      }
    });

    return unwatch;
  }, []);

  const loadDirectory = useCallback(async (path: string) => {
    setState(prev => ({ ...prev, loading: true, error: undefined }));

    try {
      const nodeId = generateNodeId(path);
      const node = await fileSystemService.getNode(nodeId);
      
      if (!node) {
        throw new Error(`Directory not found: ${path}`);
      }

      const children = await fileSystemService.getChildren(nodeId);
      
      setState(prev => {
        const newNodes = { ...prev.nodes };
        newNodes[nodeId] = { ...node, isExpanded: true };
        
        children.forEach(child => {
          newNodes[child.id] = child;
        });

        const newExpandedNodes = new Set(prev.expandedNodes);
        newExpandedNodes.add(nodeId);

        return {
          ...prev,
          nodes: newNodes,
          expandedNodes: newExpandedNodes,
          currentPath: path,
          loading: false
        };
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load directory'
      }));
    }
  }, []);

  const createNode = useCallback(async (parentPath: string, name: string, type: 'file' | 'directory') => {
    if (!isValidFileName(name)) {
      throw new Error('Invalid file name');
    }

    try {
      const newNode = await fileSystemService.createNode(parentPath, name, type);
      
      setState(prev => {
        const newNodes = { ...prev.nodes };
        newNodes[newNode.id] = newNode;
        
        // Update parent node
        const parentId = generateNodeId(parentPath);
        if (newNodes[parentId]) {
          newNodes[parentId] = {
            ...newNodes[parentId],
            children: [...(newNodes[parentId].children || []), newNode.id],
            modified: new Date()
          };
        }

        return { ...prev, nodes: newNodes };
      });

      return newNode;
    } catch (error) {
      throw new Error(`Failed to create ${type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, []);

  const deleteNodes = useCallback(async (paths: string[]) => {
    try {
      for (const path of paths) {
        const nodeId = generateNodeId(path);
        await fileSystemService.deleteNode(nodeId);
      }

      setState(prev => {
        const newNodes = { ...prev.nodes };
        const deletedIds = paths.map(path => generateNodeId(path));
        
        deletedIds.forEach(id => {
          delete newNodes[id];
        });

        return {
          ...prev,
          nodes: newNodes,
          selectedNodes: prev.selectedNodes.filter(id => !deletedIds.includes(id))
        };
      });
    } catch (error) {
      throw new Error(`Failed to delete files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, []);

  const moveNodes = useCallback(async (sources: string[], target: string) => {
    try {
      for (const source of sources) {
        const nodeId = generateNodeId(source);
        await fileSystemService.moveNode(nodeId, target);
      }

      // Refresh affected directories
      await refreshDirectory(target);
      for (const source of sources) {
        await refreshDirectory(getParentPath(source));
      }
    } catch (error) {
      throw new Error(`Failed to move files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, []);

  const copyNodes = useCallback(async (sources: string[], target: string) => {
    // In a real implementation, this would copy files
    // For now, we'll just simulate by creating new nodes
    try {
      for (const source of sources) {
        const sourceId = generateNodeId(source);
        const sourceNode = state.nodes[sourceId];
        if (sourceNode) {
          const copyName = `${sourceNode.name} - Copy`;
          await createNode(target, copyName, sourceNode.type);
        }
      }
    } catch (error) {
      throw new Error(`Failed to copy files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [state.nodes, createNode]);

  const renameNode = useCallback(async (path: string, newName: string) => {
    if (!isValidFileName(newName)) {
      throw new Error('Invalid file name');
    }

    try {
      const nodeId = generateNodeId(path);
      const updatedNode = await fileSystemService.renameNode(nodeId, newName);
      
      setState(prev => {
        const newNodes = { ...prev.nodes };
        newNodes[nodeId] = updatedNode;
        return { ...prev, nodes: newNodes };
      });
    } catch (error) {
      throw new Error(`Failed to rename file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, []);

  const expandNode = useCallback((path: string) => {
    const nodeId = generateNodeId(path);
    setState(prev => {
      const newExpandedNodes = new Set(prev.expandedNodes);
      newExpandedNodes.add(nodeId);
      
      const newNodes = { ...prev.nodes };
      if (newNodes[nodeId]) {
        newNodes[nodeId] = { ...newNodes[nodeId], isExpanded: true };
      }

      return { ...prev, expandedNodes: newExpandedNodes, nodes: newNodes };
    });

    loadDirectory(path);
  }, [loadDirectory]);

  const collapseNode = useCallback((path: string) => {
    const nodeId = generateNodeId(path);
    setState(prev => {
      const newExpandedNodes = new Set(prev.expandedNodes);
      newExpandedNodes.delete(nodeId);
      
      const newNodes = { ...prev.nodes };
      if (newNodes[nodeId]) {
        newNodes[nodeId] = { ...newNodes[nodeId], isExpanded: false };
      }

      return { ...prev, expandedNodes: newExpandedNodes, nodes: newNodes };
    });
  }, []);

  const selectNode = useCallback((path: string, multiSelect: boolean = false) => {
    const nodeId = generateNodeId(path);
    setState(prev => {
      let newSelectedNodes: string[];
      
      if (multiSelect) {
        if (prev.selectedNodes.includes(nodeId)) {
          newSelectedNodes = prev.selectedNodes.filter(id => id !== nodeId);
        } else {
          newSelectedNodes = [...prev.selectedNodes, nodeId];
        }
      } else {
        newSelectedNodes = [nodeId];
      }

      const newNodes = { ...prev.nodes };
      Object.keys(newNodes).forEach(id => {
        newNodes[id] = { ...newNodes[id], isSelected: newSelectedNodes.includes(id) };
      });

      return { ...prev, selectedNodes: newSelectedNodes, nodes: newNodes };
    });
  }, []);

  const debouncedSearch = useCallback(
    debounce(async (query: string, options?: Partial<FileSearchOptions>) => {
      if (!query.trim()) {
        setState(prev => ({ ...prev, searchResults: [], searchQuery: '' }));
        return;
      }

      try {
        const results = await fileSystemService.searchFiles(query, options);
        setState(prev => ({
          ...prev,
          searchResults: results.map(node => node.id),
          searchQuery: query
        }));
      } catch (error) {
        console.error('Search failed:', error);
      }
    }, 300),
    []
  );

  const searchFiles = useCallback(async (query: string, options?: Partial<FileSearchOptions>) => {
    debouncedSearch(query, options);
  }, [debouncedSearch]);

  const clearSearch = useCallback(() => {
    setState(prev => ({ ...prev, searchQuery: '', searchResults: [] }));
  }, []);

  const copyToClipboard = useCallback((paths: string[]) => {
    setState(prev => ({
      ...prev,
      clipboard: {
        operation: 'copy',
        nodes: paths.map(path => generateNodeId(path))
      }
    }));
  }, []);

  const cutToClipboard = useCallback((paths: string[]) => {
    setState(prev => ({
      ...prev,
      clipboard: {
        operation: 'cut',
        nodes: paths.map(path => generateNodeId(path))
      }
    }));
  }, []);

  const pasteFromClipboard = useCallback(async (targetPath: string) => {
    if (state.clipboard.operation && state.clipboard.nodes.length > 0) {
      const sourcePaths = state.clipboard.nodes.map(nodeId => state.nodes[nodeId]?.path).filter(Boolean);
      
      if (state.clipboard.operation === 'copy') {
        await copyNodes(sourcePaths, targetPath);
      } else if (state.clipboard.operation === 'cut') {
        await moveNodes(sourcePaths, targetPath);
        setState(prev => ({ ...prev, clipboard: { operation: null, nodes: [] } }));
      }
    }
  }, [state.clipboard, state.nodes, copyNodes, moveNodes]);

  const refreshDirectory = useCallback(async (path?: string) => {
    const targetPath = path || state.currentPath;
    await loadDirectory(targetPath);
  }, [state.currentPath, loadDirectory]);

  const setViewMode = useCallback((mode: FileExplorerState['viewMode']) => {
    setState(prev => ({ ...prev, viewMode: mode }));
  }, []);

  const setSortOptions = useCallback((
    sortBy: FileExplorerState['sortBy'], 
    sortOrder: FileExplorerState['sortOrder']
  ) => {
    setState(prev => ({ ...prev, sortBy, sortOrder }));
  }, []);

  const toggleHidden = useCallback(() => {
    setState(prev => ({ ...prev, showHidden: !prev.showHidden }));
  }, []);

  return {
    state,
    actions: {
      loadDirectory,
      createNode,
      deleteNodes,
      moveNodes,
      copyNodes,
      renameNode,
      expandNode,
      collapseNode,
      selectNode,
      searchFiles,
      clearSearch,
      copyToClipboard,
      cutToClipboard,
      pasteFromClipboard,
      refreshDirectory,
      setViewMode,
      setSortOptions,
      toggleHidden
    },
    utils: {
      getNodeIcon,
      getNodeColor,
      formatFileSize,
      formatDate,
      isValidFileName,
      getRelativePath
    }
  };
}