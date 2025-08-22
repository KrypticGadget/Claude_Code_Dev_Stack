import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useHotkeys } from 'react-hotkeys-hook';
import {
  Box,
  Typography,
  IconButton,
  TextField,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  InsertDriveFile as FileIcon,
  MoreVert as MoreVertIcon,
  CreateNewFolder as CreateFolderIcon,
  NoteAdd as CreateFileIcon,
  Delete as DeleteIcon,
  Edit as RenameIcon,
  ContentCopy as CopyIcon,
  ContentCut as CutIcon,
  ContentPaste as PasteIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { FileSystemNode, ContextMenuAction } from '../../types';
import { getNodeIcon, getNodeColor, formatFileSize, formatDate } from '../../utils/fileExplorerUtils';

interface TreeNodeProps {
  node: FileSystemNode;
  level: number;
  isSelected: boolean;
  isExpanded: boolean;
  isDragging?: boolean;
  children?: FileSystemNode[];
  onSelect: (nodeId: string, multiSelect?: boolean) => void;
  onExpand: (nodeId: string) => void;
  onCollapse: (nodeId: string) => void;
  onContextMenu?: (nodeId: string, actions: ContextMenuAction[]) => void;
  onRename?: (nodeId: string, newName: string) => Promise<void>;
  onCreate?: (parentId: string, name: string, type: 'file' | 'directory') => Promise<void>;
  onDelete?: (nodeIds: string[]) => Promise<void>;
  onCopy?: (nodeIds: string[]) => void;
  onCut?: (nodeIds: string[]) => void;
  onPaste?: (targetId: string) => Promise<void>;
  onRefresh?: (nodeId: string) => Promise<void>;
  enableDragDrop?: boolean;
  enableContextMenu?: boolean;
  customActions?: ContextMenuAction[];
}

const DRAG_TYPE = 'file-node';

export const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  level,
  isSelected,
  isExpanded,
  children = [],
  onSelect,
  onExpand,
  onCollapse,
  onContextMenu,
  onRename,
  onCreate,
  onDelete,
  onCopy,
  onCut,
  onPaste,
  onRefresh,
  enableDragDrop = true,
  enableContextMenu = true,
  customActions = []
}) => {
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(node.name);
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
  } | null>(null);
  const [isCreating, setIsCreating] = useState<'file' | 'directory' | null>(null);
  const [createValue, setCreateValue] = useState('');

  const nodeRef = useRef<HTMLDivElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);
  const createInputRef = useRef<HTMLInputElement>(null);

  // Drag and drop setup
  const [{ isDragging }, drag] = useDrag(
    () => ({
      type: DRAG_TYPE,
      item: { nodeId: node.id, path: node.path },
      canDrag: enableDragDrop,
      collect: (monitor) => ({
        isDragging: monitor.isDragging()
      })
    }),
    [node.id, node.path, enableDragDrop]
  );

  const [{ isOver, canDrop }, drop] = useDrop(
    () => ({
      accept: DRAG_TYPE,
      canDrop: (item: { nodeId: string; path: string }) => {
        return node.type === 'directory' && item.nodeId !== node.id;
      },
      drop: (item: { nodeId: string; path: string }) => {
        if (onPaste && item.nodeId !== node.id) {
          onPaste(node.id);
        }
      },
      collect: (monitor) => ({
        isOver: monitor.isOver(),
        canDrop: monitor.canDrop()
      })
    }),
    [node.id, node.type, onPaste]
  );

  // Combine drag and drop refs
  const dragDropRef = useCallback((element: HTMLDivElement | null) => {
    drag(element);
    drop(element);
    if (nodeRef.current !== element) {
      nodeRef.current = element;
    }
  }, [drag, drop]);

  // Keyboard shortcuts
  useHotkeys('f2', () => handleRename(), { enabled: isSelected && !isRenaming });
  useHotkeys('delete', () => handleDelete(), { enabled: isSelected && !isRenaming });
  useHotkeys('ctrl+c', () => handleCopy(), { enabled: isSelected && !isRenaming });
  useHotkeys('ctrl+x', () => handleCut(), { enabled: isSelected && !isRenaming });
  useHotkeys('ctrl+v', () => handlePaste(), { enabled: isSelected && !isRenaming && node.type === 'directory' });
  useHotkeys('enter', () => handleSelect(), { enabled: isSelected && !isRenaming });

  // Focus rename input when renaming starts
  useEffect(() => {
    if (isRenaming && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [isRenaming]);

  // Focus create input when creating starts
  useEffect(() => {
    if (isCreating && createInputRef.current) {
      createInputRef.current.focus();
    }
  }, [isCreating]);

  const handleSelect = useCallback((event?: React.MouseEvent) => {
    const multiSelect = event?.ctrlKey || event?.metaKey;
    onSelect(node.id, multiSelect);
  }, [node.id, onSelect]);

  const handleToggleExpand = useCallback(() => {
    if (node.type !== 'directory') return;
    
    if (isExpanded) {
      onCollapse(node.id);
    } else {
      onExpand(node.id);
    }
  }, [node.type, node.id, isExpanded, onExpand, onCollapse]);

  const handleContextMenu = useCallback((event: React.MouseEvent) => {
    if (!enableContextMenu) return;
    
    event.preventDefault();
    event.stopPropagation();
    
    setContextMenu(
      contextMenu === null
        ? { mouseX: event.clientX + 2, mouseY: event.clientY - 6 }
        : null
    );
  }, [enableContextMenu, contextMenu]);

  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  const handleRename = useCallback(() => {
    setIsRenaming(true);
    setRenameValue(node.name);
    handleCloseContextMenu();
  }, [node.name]);

  const handleRenameSubmit = useCallback(async () => {
    if (renameValue.trim() !== node.name && onRename) {
      try {
        await onRename(node.id, renameValue.trim());
      } catch (error) {
        console.error('Rename failed:', error);
        setRenameValue(node.name);
      }
    }
    setIsRenaming(false);
  }, [node.id, node.name, renameValue, onRename]);

  const handleRenameCancel = useCallback(() => {
    setIsRenaming(false);
    setRenameValue(node.name);
  }, [node.name]);

  const handleRenameKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleRenameSubmit();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      handleRenameCancel();
    }
  }, [handleRenameSubmit, handleRenameCancel]);

  const handleCreate = useCallback((type: 'file' | 'directory') => {
    setIsCreating(type);
    setCreateValue('');
    handleCloseContextMenu();
  }, []);

  const handleCreateSubmit = useCallback(async () => {
    if (createValue.trim() && onCreate) {
      try {
        await onCreate(node.id, createValue.trim(), isCreating!);
      } catch (error) {
        console.error('Create failed:', error);
      }
    }
    setIsCreating(null);
    setCreateValue('');
  }, [node.id, createValue, isCreating, onCreate]);

  const handleCreateCancel = useCallback(() => {
    setIsCreating(null);
    setCreateValue('');
  }, []);

  const handleCreateKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleCreateSubmit();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      handleCreateCancel();
    }
  }, [handleCreateSubmit, handleCreateCancel]);

  const handleDelete = useCallback(() => {
    if (onDelete) {
      onDelete([node.id]);
    }
    handleCloseContextMenu();
  }, [node.id, onDelete]);

  const handleCopy = useCallback(() => {
    if (onCopy) {
      onCopy([node.id]);
    }
    handleCloseContextMenu();
  }, [node.id, onCopy]);

  const handleCut = useCallback(() => {
    if (onCut) {
      onCut([node.id]);
    }
    handleCloseContextMenu();
  }, [node.id, onCut]);

  const handlePaste = useCallback(() => {
    if (onPaste && node.type === 'directory') {
      onPaste(node.id);
    }
    handleCloseContextMenu();
  }, [node.id, node.type, onPaste]);

  const handleRefresh = useCallback(() => {
    if (onRefresh) {
      onRefresh(node.id);
    }
    handleCloseContextMenu();
  }, [node.id, onRefresh]);

  const getNodeIconComponent = useCallback(() => {
    if (node.type === 'directory') {
      return isExpanded ? <FolderOpenIcon /> : <FolderIcon />;
    }
    return <FileIcon />;
  }, [node.type, isExpanded]);

  const contextMenuActions: ContextMenuAction[] = [
    ...(node.type === 'directory' ? [
      {
        id: 'create-file',
        label: 'New File',
        icon: 'note-add',
        action: () => handleCreate('file')
      },
      {
        id: 'create-folder',
        label: 'New Folder',
        icon: 'create-new-folder',
        action: () => handleCreate('directory')
      },
      { id: 'separator-1', label: '', separator: true, action: () => {} },
    ] : []),
    {
      id: 'rename',
      label: 'Rename',
      icon: 'edit',
      shortcut: 'F2',
      action: handleRename
    },
    {
      id: 'delete',
      label: 'Delete',
      icon: 'delete',
      shortcut: 'Del',
      action: handleDelete
    },
    { id: 'separator-2', label: '', separator: true, action: () => {} },
    {
      id: 'copy',
      label: 'Copy',
      icon: 'content-copy',
      shortcut: 'Ctrl+C',
      action: handleCopy
    },
    {
      id: 'cut',
      label: 'Cut',
      icon: 'content-cut',
      shortcut: 'Ctrl+X',
      action: handleCut
    },
    ...(node.type === 'directory' ? [
      {
        id: 'paste',
        label: 'Paste',
        icon: 'content-paste',
        shortcut: 'Ctrl+V',
        action: handlePaste
      }
    ] : []),
    { id: 'separator-3', label: '', separator: true, action: () => {} },
    {
      id: 'refresh',
      label: 'Refresh',
      icon: 'refresh',
      action: handleRefresh
    },
    ...customActions
  ];

  const nodeStyle = {
    paddingLeft: `${level * 20 + 8}px`,
    backgroundColor: isSelected ? 'action.selected' : 'transparent',
    opacity: isDragging ? 0.5 : 1,
    borderLeft: isOver && canDrop ? '2px solid' : 'none',
    borderColor: 'primary.main',
    cursor: 'pointer',
    userSelect: 'none' as const,
    '&:hover': {
      backgroundColor: 'action.hover'
    }
  };

  return (
    <>
      <Box
        ref={dragDropRef}
        sx={nodeStyle}
        onClick={handleSelect}
        onContextMenu={handleContextMenu}
        data-testid={`tree-node-${node.id}`}
      >
        <Box
          display="flex"
          alignItems="center"
          py={0.5}
          gap={1}
          minHeight={32}
        >
          {/* Expand/Collapse Icon */}
          {node.type === 'directory' && (
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleToggleExpand();
              }}
              sx={{ width: 20, height: 20 }}
            >
              {isExpanded ? (
                <ExpandMoreIcon fontSize="small" />
              ) : (
                <ChevronRightIcon fontSize="small" />
              )}
            </IconButton>
          )}
          
          {/* File/Folder Icon */}
          <Box
            sx={{
              color: getNodeColor(node),
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {getNodeIconComponent()}
          </Box>

          {/* Node Name or Rename Input */}
          {isRenaming ? (
            <TextField
              ref={renameInputRef}
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onBlur={handleRenameSubmit}
              onKeyDown={handleRenameKeyDown}
              size="small"
              variant="outlined"
              sx={{ flex: 1, '& .MuiInputBase-input': { py: 0.25 } }}
            />
          ) : (
            <Box display="flex" alignItems="center" flex={1} gap={1}>
              <Typography
                variant="body2"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  flex: 1
                }}
              >
                {node.name}
              </Typography>
              
              {/* File Size and Date */}
              {node.type === 'file' && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ minWidth: 'fit-content' }}
                >
                  {formatFileSize(node.size || 0)} • {formatDate(node.modified)}
                </Typography>
              )}
            </Box>
          )}
        </Box>

        {/* Create new file/folder input */}
        {isCreating && (
          <Box
            sx={{
              paddingLeft: `${(level + 1) * 20 + 8}px`,
              py: 0.5
            }}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <Box sx={{ width: 20, height: 20 }} />
              <Box sx={{ color: 'primary.main' }}>
                {isCreating === 'directory' ? <FolderIcon /> : <FileIcon />}
              </Box>
              <TextField
                ref={createInputRef}
                value={createValue}
                onChange={(e) => setCreateValue(e.target.value)}
                onBlur={handleCreateSubmit}
                onKeyDown={handleCreateKeyDown}
                placeholder={`New ${isCreating}`}
                size="small"
                variant="outlined"
                sx={{ flex: 1, '& .MuiInputBase-input': { py: 0.25 } }}
              />
            </Box>
          </Box>
        )}
      </Box>

      {/* Children */}
      {node.type === 'directory' && (
        <Collapse in={isExpanded} timeout={200}>
          <Box>
            {children.map((child) => (
              <TreeNode
                key={child.id}
                node={child}
                level={level + 1}
                isSelected={child.isSelected || false}
                isExpanded={child.isExpanded || false}
                onSelect={onSelect}
                onExpand={onExpand}
                onCollapse={onCollapse}
                onRename={onRename}
                onCreate={onCreate}
                onDelete={onDelete}
                onCopy={onCopy}
                onCut={onCut}
                onPaste={onPaste}
                onRefresh={onRefresh}
                enableDragDrop={enableDragDrop}
                enableContextMenu={enableContextMenu}
                customActions={customActions}
              />
            ))}
          </Box>
        </Collapse>
      )}

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left'
        }}
      >
        {contextMenuActions.map((action) => (
          action.separator ? (
            <Divider key={action.id} />
          ) : (
            <MenuItem
              key={action.id}
              onClick={() => {
                action.action([node.id]);
                handleCloseContextMenu();
              }}
              disabled={action.disabled}
            >
              {action.icon && (
                <ListItemIcon>
                  {action.icon === 'note-add' && <CreateFileIcon />}
                  {action.icon === 'create-new-folder' && <CreateFolderIcon />}
                  {action.icon === 'edit' && <RenameIcon />}
                  {action.icon === 'delete' && <DeleteIcon />}
                  {action.icon === 'content-copy' && <CopyIcon />}
                  {action.icon === 'content-cut' && <CutIcon />}
                  {action.icon === 'content-paste' && <PasteIcon />}
                  {action.icon === 'refresh' && <RefreshIcon />}
                </ListItemIcon>
              )}
              <ListItemText>
                {action.label}
                {action.shortcut && (
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                    {action.shortcut}
                  </Typography>
                )}
              </ListItemText>
            </MenuItem>
          )
        ))}
      </Menu>
    </>
  );
};