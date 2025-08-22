import React, { useCallback, useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useHotkeys } from 'react-hotkeys-hook';
import {
  Box,
  Paper,
  Toolbar,
  IconButton,
  Tooltip,
  ButtonGroup,
  Divider,
  LinearProgress,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  Breadcrumbs,
  Link,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  ViewList as ListViewIcon,
  ViewModule as GridViewIcon,
  AccountTree as TreeViewIcon,
  Sort as SortIcon,
  Visibility as ShowHiddenIcon,
  VisibilityOff as HideHiddenIcon,
  CreateNewFolder as CreateFolderIcon,
  NoteAdd as CreateFileIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Settings as SettingsIcon,
  Upload as UploadIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { FileExplorerProps, FileSystemNode, FileOperation } from '../../types';
import { useFileExplorer } from '../../hooks/useFileExplorer';
import { FileSearchBar } from './FileSearchBar';
import { AutoSizedVirtualizedTree } from './VirtualizedTree';
import { getParentPath, joinPaths } from '../../utils/fileExplorerUtils';

interface CreateDialogState {
  open: boolean;
  type: 'file' | 'directory';
  parentPath: string;
}

interface ConfirmDialogState {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  rootPath = '/',
  height = 600,
  width,
  showSearch = true,
  showContextMenu = true,
  enableDragDrop = true,
  enableKeyboardNavigation = true,
  enableVirtualization = true,
  multiSelect = true,
  customActions = [],
  onFileSelect,
  onFileOpen,
  onFileOperation,
  onError,
  className,
  style,
  'data-testid': testId
}) => {
  const {
    state,
    actions,
    utils
  } = useFileExplorer(rootPath);

  const [createDialog, setCreateDialog] = useState<CreateDialogState>({
    open: false,
    type: 'file',
    parentPath: rootPath
  });
  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialogState>({
    open: false,
    title: '',
    message: '',
    onConfirm: () => {}
  });
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  const [sortMenuAnchor, setSortMenuAnchor] = useState<null | HTMLElement>(null);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Keyboard shortcuts
  useHotkeys('ctrl+n', () => handleCreateFile(), { enabled: enableKeyboardNavigation });
  useHotkeys('ctrl+shift+n', () => handleCreateFolder(), { enabled: enableKeyboardNavigation });
  useHotkeys('f5', () => handleRefresh(), { enabled: enableKeyboardNavigation });
  useHotkeys('ctrl+h', () => actions.toggleHidden(), { enabled: enableKeyboardNavigation });
  useHotkeys('ctrl+f', (e) => {
    e.preventDefault();
    // Focus search input
    const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
    searchInput?.focus();
  }, { enabled: enableKeyboardNavigation });

  // Handle file operations
  useEffect(() => {
    if (state.selectedNodes.length > 0 && onFileSelect) {
      const selectedFiles = state.selectedNodes
        .map(nodeId => state.nodes[nodeId])
        .filter(Boolean);
      onFileSelect(selectedFiles);
    }
  }, [state.selectedNodes, state.nodes, onFileSelect]);

  const showNotification = useCallback((
    message: string, 
    severity: 'success' | 'error' | 'warning' | 'info' = 'info'
  ) => {
    setNotification({ open: true, message, severity });
  }, []);

  const handleError = useCallback((error: string) => {
    showNotification(error, 'error');
    onError?.(error);
  }, [showNotification, onError]);

  const handleNodeSelect = useCallback((nodeId: string, multiSelectMode?: boolean) => {
    actions.selectNode(nodeId, multiSelect && multiSelectMode);
  }, [actions.selectNode, multiSelect]);

  const handleNodeOpen = useCallback((node: FileSystemNode) => {
    if (node.type === 'directory') {
      actions.expandNode(node.path);
    } else {
      onFileOpen?.(node);
    }
  }, [actions.expandNode, onFileOpen]);

  const handleNodeRename = useCallback(async (nodeId: string, newName: string) => {
    try {
      const node = state.nodes[nodeId];
      if (!node) return;
      
      await actions.renameNode(node.path, newName);
      showNotification(`Renamed "${node.name}" to "${newName}"`, 'success');
      
      onFileOperation?.({
        id: Date.now().toString(),
        type: 'rename',
        source: [node.path],
        newName,
        status: 'completed',
        timestamp: new Date()
      });
    } catch (error) {
      handleError(`Failed to rename: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [state.nodes, actions.renameNode, showNotification, onFileOperation, handleError]);

  const handleNodeCreate = useCallback(async (parentId: string, name: string, type: 'file' | 'directory') => {
    try {
      const parentNode = state.nodes[parentId];
      if (!parentNode) return;
      
      await actions.createNode(parentNode.path, name, type);
      showNotification(`Created ${type} "${name}"`, 'success');
      
      onFileOperation?.({
        id: Date.now().toString(),
        type: 'create',
        source: [joinPaths(parentNode.path, name)],
        status: 'completed',
        timestamp: new Date()
      });
    } catch (error) {
      handleError(`Failed to create ${type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [state.nodes, actions.createNode, showNotification, onFileOperation, handleError]);

  const handleNodeDelete = useCallback(async (nodeIds: string[]) => {
    const nodes = nodeIds.map(id => state.nodes[id]).filter(Boolean);
    const nodeNames = nodes.map(node => node.name).join(', ');
    
    setConfirmDialog({
      open: true,
      title: 'Confirm Delete',
      message: `Are you sure you want to delete ${nodes.length === 1 ? `"${nodeNames}"` : `${nodes.length} items`}?`,
      onConfirm: async () => {
        try {
          const paths = nodes.map(node => node.path);
          await actions.deleteNodes(paths);
          showNotification(`Deleted ${nodeNames}`, 'success');
          
          onFileOperation?.({
            id: Date.now().toString(),
            type: 'delete',
            source: paths,
            status: 'completed',
            timestamp: new Date()
          });
        } catch (error) {
          handleError(`Failed to delete: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
        setConfirmDialog(prev => ({ ...prev, open: false }));
      }
    });
  }, [state.nodes, actions.deleteNodes, showNotification, onFileOperation, handleError]);

  const handleNodeCopy = useCallback((nodeIds: string[]) => {
    const paths = nodeIds.map(id => state.nodes[id]?.path).filter(Boolean);
    actions.copyToClipboard(paths);
    showNotification(`Copied ${nodeIds.length} item(s) to clipboard`, 'success');
  }, [state.nodes, actions.copyToClipboard, showNotification]);

  const handleNodeCut = useCallback((nodeIds: string[]) => {
    const paths = nodeIds.map(id => state.nodes[id]?.path).filter(Boolean);
    actions.cutToClipboard(paths);
    showNotification(`Cut ${nodeIds.length} item(s) to clipboard`, 'success');
  }, [state.nodes, actions.cutToClipboard, showNotification]);

  const handleNodePaste = useCallback(async (targetId: string) => {
    try {
      const targetNode = state.nodes[targetId];
      if (!targetNode || targetNode.type !== 'directory') return;
      
      await actions.pasteFromClipboard(targetNode.path);
      showNotification(`Pasted items to "${targetNode.name}"`, 'success');
      
      onFileOperation?.({
        id: Date.now().toString(),
        type: state.clipboard.operation === 'copy' ? 'copy' : 'move',
        source: state.clipboard.nodes.map(id => state.nodes[id]?.path).filter(Boolean),
        target: targetNode.path,
        status: 'completed',
        timestamp: new Date()
      });
    } catch (error) {
      handleError(`Failed to paste: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [state.nodes, state.clipboard, actions.pasteFromClipboard, showNotification, onFileOperation, handleError]);

  const handleRefresh = useCallback(async () => {
    try {
      await actions.refreshDirectory();
      showNotification('Refreshed successfully', 'success');
    } catch (error) {
      handleError(`Failed to refresh: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [actions.refreshDirectory, showNotification, handleError]);

  const handleCreateFile = useCallback(() => {
    const selectedNode = state.selectedNodes.length > 0 ? state.nodes[state.selectedNodes[0]] : null;
    const parentPath = selectedNode?.type === 'directory' ? selectedNode.path : getParentPath(selectedNode?.path || state.currentPath);
    
    setCreateDialog({
      open: true,
      type: 'file',
      parentPath
    });
  }, [state.selectedNodes, state.nodes, state.currentPath]);

  const handleCreateFolder = useCallback(() => {
    const selectedNode = state.selectedNodes.length > 0 ? state.nodes[state.selectedNodes[0]] : null;
    const parentPath = selectedNode?.type === 'directory' ? selectedNode.path : getParentPath(selectedNode?.path || state.currentPath);
    
    setCreateDialog({
      open: true,
      type: 'directory',
      parentPath
    });
  }, [state.selectedNodes, state.nodes, state.currentPath]);

  const handleCreateDialogSubmit = useCallback(async (name: string) => {
    if (!utils.isValidFileName(name)) {
      handleError('Invalid file name');
      return;
    }
    
    try {
      await actions.createNode(createDialog.parentPath, name, createDialog.type);
      showNotification(`Created ${createDialog.type} "${name}"`, 'success');
      setCreateDialog({ ...createDialog, open: false });
    } catch (error) {
      handleError(`Failed to create ${createDialog.type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }, [createDialog, actions.createNode, utils.isValidFileName, showNotification, handleError]);

  const handleSearchSave = useCallback((query: string) => {
    if (!recentSearches.includes(query)) {
      setRecentSearches(prev => [query, ...prev].slice(0, 10));
    }
  }, [recentSearches]);

  const breadcrumbPaths = state.currentPath.split('/').filter(Boolean);

  return (
    <DndProvider backend={HTML5Backend}>
      <Paper
        className={className}
        style={{ height, width, ...style }}
        data-testid={testId}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        {/* Toolbar */}
        <Toolbar variant="dense" sx={{ minHeight: 48, gap: 1 }}>
          {/* Navigation and Actions */}
          <ButtonGroup size="small" variant="outlined">
            <Tooltip title="Refresh (F5)">
              <IconButton onClick={handleRefresh} disabled={state.loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="New File (Ctrl+N)">
              <IconButton onClick={handleCreateFile}>
                <CreateFileIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="New Folder (Ctrl+Shift+N)">
              <IconButton onClick={handleCreateFolder}>
                <CreateFolderIcon />
              </IconButton>
            </Tooltip>
          </ButtonGroup>

          <Divider orientation="vertical" flexItem />

          {/* View Options */}
          <ButtonGroup size="small" variant="outlined">
            <Tooltip title="Tree View">
              <IconButton 
                onClick={() => actions.setViewMode('tree')}
                color={state.viewMode === 'tree' ? 'primary' : 'default'}
              >
                <TreeViewIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="List View">
              <IconButton 
                onClick={() => actions.setViewMode('list')}
                color={state.viewMode === 'list' ? 'primary' : 'default'}
              >
                <ListViewIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Grid View">
              <IconButton 
                onClick={() => actions.setViewMode('grid')}
                color={state.viewMode === 'grid' ? 'primary' : 'default'}
              >
                <GridViewIcon />
              </IconButton>
            </Tooltip>
          </ButtonGroup>

          <Divider orientation="vertical" flexItem />

          {/* Sort and Filter */}
          <Tooltip title="Sort Options">
            <IconButton 
              size="small"
              onClick={(e) => setSortMenuAnchor(e.currentTarget)}
            >
              <SortIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title={state.showHidden ? "Hide Hidden Files (Ctrl+H)" : "Show Hidden Files (Ctrl+H)"}>
            <IconButton 
              size="small"
              onClick={actions.toggleHidden}
              color={state.showHidden ? 'primary' : 'default'}
            >
              {state.showHidden ? <HideHiddenIcon /> : <ShowHiddenIcon />}
            </IconButton>
          </Tooltip>

          <Box flex={1} />

          {/* Status */}
          {state.loading && (
            <Typography variant="caption" color="text.secondary">
              Loading...
            </Typography>
          )}
        </Toolbar>

        {/* Breadcrumbs */}
        <Box px={2} py={1} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Breadcrumbs 
            separator={<NavigateNextIcon fontSize="small" />}
            maxItems={4}
            itemsBeforeCollapse={1}
            itemsAfterCollapse={2}
          >
            <Link
              component="button"
              variant="body2"
              onClick={() => actions.loadDirectory('/')}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <HomeIcon fontSize="small" />
              Root
            </Link>
            {breadcrumbPaths.map((segment, index) => {
              const path = '/' + breadcrumbPaths.slice(0, index + 1).join('/');
              return (
                <Link
                  key={path}
                  component="button"
                  variant="body2"
                  onClick={() => actions.loadDirectory(path)}
                >
                  {segment}
                </Link>
              );
            })}
          </Breadcrumbs>
        </Box>

        {/* Search Bar */}
        {showSearch && (
          <Box p={2} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <FileSearchBar
              searchQuery={state.searchQuery}
              searchResults={state.searchResults.map(id => state.nodes[id]).filter(Boolean)}
              isSearching={state.loading}
              onSearch={actions.searchFiles}
              onClear={actions.clearSearch}
              onResultSelect={(node) => handleNodeOpen(node)}
              recentSearches={recentSearches}
              onSaveSearch={handleSearchSave}
            />
          </Box>
        )}

        {/* Loading Progress */}
        {state.loading && (
          <LinearProgress />
        )}

        {/* Error Display */}
        {state.error && (
          <Alert severity="error" onClose={() => {
            // Clear error in state would go here
          }}>
            {state.error}
          </Alert>
        )}

        {/* File Tree */}
        <Box flex={1} sx={{ overflow: 'hidden' }}>
          {enableVirtualization ? (
            <AutoSizedVirtualizedTree
              itemHeight={32}
              nodes={state.nodes}
              rootNodeIds={state.rootNodes}
              expandedNodes={state.expandedNodes}
              selectedNodes={state.selectedNodes}
              searchQuery={state.searchQuery}
              searchResults={state.searchResults}
              sortBy={state.sortBy}
              sortOrder={state.sortOrder}
              showHidden={state.showHidden}
              enableDragDrop={enableDragDrop}
              enableContextMenu={showContextMenu}
              onNodeSelect={handleNodeSelect}
              onNodeExpand={actions.expandNode}
              onNodeCollapse={actions.collapseNode}
              onNodeRename={handleNodeRename}
              onNodeCreate={handleNodeCreate}
              onNodeDelete={handleNodeDelete}
              onNodeCopy={handleNodeCopy}
              onNodeCut={handleNodeCut}
              onNodePaste={handleNodePaste}
              onNodeRefresh={(nodeId) => {
                const node = state.nodes[nodeId];
                if (node) actions.refreshDirectory(node.path);
              }}
            />
          ) : (
            <Box p={1} sx={{ overflow: 'auto', height: '100%' }}>
              {/* Non-virtualized tree would go here */}
              <Typography color="text.secondary">
                Non-virtualized tree view not implemented in this demo
              </Typography>
            </Box>
          )}
        </Box>

        {/* Sort Menu */}
        <Menu
          anchorEl={sortMenuAnchor}
          open={Boolean(sortMenuAnchor)}
          onClose={() => setSortMenuAnchor(null)}
        >
          {[
            { key: 'name', label: 'Name' },
            { key: 'size', label: 'Size' },
            { key: 'modified', label: 'Modified' },
            { key: 'type', label: 'Type' }
          ].map((option) => (
            <MenuItem
              key={option.key}
              onClick={() => {
                const newOrder = state.sortBy === option.key && state.sortOrder === 'asc' ? 'desc' : 'asc';
                actions.setSortOptions(option.key as any, newOrder);
                setSortMenuAnchor(null);
              }}
              selected={state.sortBy === option.key}
            >
              <ListItemText>
                {option.label}
                {state.sortBy === option.key && (
                  <Typography component="span" variant="caption" sx={{ ml: 1 }}>
                    ({state.sortOrder === 'asc' ? '↑' : '↓'})
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
          ))}
        </Menu>

        {/* Create Dialog */}
        <Dialog 
          open={createDialog.open} 
          onClose={() => setCreateDialog({ ...createDialog, open: false })}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Create New {createDialog.type === 'file' ? 'File' : 'Folder'}
          </DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              fullWidth
              label="Name"
              variant="outlined"
              margin="normal"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const input = e.target as HTMLInputElement;
                  handleCreateDialogSubmit(input.value);
                }
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialog({ ...createDialog, open: false })}>
              Cancel
            </Button>
            <Button 
              onClick={(e) => {
                const input = (e.target as HTMLElement).closest('.MuiDialog-root')
                  ?.querySelector('input') as HTMLInputElement;
                if (input) {
                  handleCreateDialogSubmit(input.value);
                }
              }}
              variant="contained"
            >
              Create
            </Button>
          </DialogActions>
        </Dialog>

        {/* Confirm Dialog */}
        <Dialog
          open={confirmDialog.open}
          onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
        >
          <DialogTitle>{confirmDialog.title}</DialogTitle>
          <DialogContent>
            <Typography>{confirmDialog.message}</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}>
              Cancel
            </Button>
            <Button onClick={confirmDialog.onConfirm} color="error" variant="contained">
              Confirm
            </Button>
          </DialogActions>
        </Dialog>

        {/* Notification Snackbar */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={() => setNotification({ ...notification, open: false })}
        >
          <Alert
            onClose={() => setNotification({ ...notification, open: false })}
            severity={notification.severity}
            variant="filled"
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Paper>
    </DndProvider>
  );
};