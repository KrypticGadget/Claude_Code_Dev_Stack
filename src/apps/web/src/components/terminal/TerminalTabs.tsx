import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Tabs,
  Tab,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Chip,
  Tooltip
} from '@mui/material';
import {
  Add,
  Close,
  MoreVert,
  Edit,
  ContentCopy,
  SplitScreen,
  Download,
  Refresh,
  Terminal as TerminalIcon,
  Settings
} from '@mui/icons-material';
import { useDrag, useDrop, DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import { useTerminalStore } from '../../store/terminalStore';
import { TerminalTab, TerminalSession } from '../../types/terminal';

interface DragItem {
  type: string;
  tabId: string;
  workspaceId: string;
}

interface TabItemProps {
  tab: TerminalTab;
  workspaceId: string;
  isActive: boolean;
  onActivate: () => void;
  onClose: () => void;
  onRename: (newTitle: string) => void;
  onDuplicate: () => void;
  onSplit: () => void;
  onExport: () => void;
  canClose: boolean;
}

const TabItem: React.FC<TabItemProps> = ({
  tab,
  workspaceId,
  isActive,
  onActivate,
  onClose,
  onRename,
  onDuplicate,
  onSplit,
  onExport,
  canClose
}) => {
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null);
  const [renameDialog, setRenameDialog] = useState(false);
  const [newTitle, setNewTitle] = useState(tab.title);

  const ref = useRef<HTMLDivElement>(null);

  // Drag and drop functionality
  const [{ isDragging }, drag] = useDrag({
    type: 'TAB',
    item: { type: 'TAB', tabId: tab.id, workspaceId },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  const [{ isOver }, drop] = useDrop({
    accept: 'TAB',
    drop: (item: DragItem) => {
      if (item.tabId !== tab.id) {
        // Handle tab reordering logic here
        console.log('Reorder tabs:', item.tabId, 'to', tab.id);
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver()
    })
  });

  drag(drop(ref));

  const handleContextMenu = useCallback((event: React.MouseEvent) => {
    event.preventDefault();
    setContextMenu({ x: event.clientX, y: event.clientY });
  }, []);

  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  const handleRename = useCallback(() => {
    setNewTitle(tab.title);
    setRenameDialog(true);
    setContextMenu(null);
  }, [tab.title]);

  const handleRenameConfirm = useCallback(() => {
    if (newTitle.trim()) {
      onRename(newTitle.trim());
    }
    setRenameDialog(false);
  }, [newTitle, onRename]);

  const handleDuplicate = useCallback(() => {
    onDuplicate();
    setContextMenu(null);
  }, [onDuplicate]);

  const handleSplit = useCallback(() => {
    onSplit();
    setContextMenu(null);
  }, [onSplit]);

  const handleExport = useCallback(() => {
    onExport();
    setContextMenu(null);
  }, [onExport]);

  const getTabColor = () => {
    if (isActive) return 'primary.main';
    if (tab.badge?.type === 'error') return 'error.main';
    if (tab.badge?.type === 'warning') return 'warning.main';
    return 'text.secondary';
  };

  return (
    <>
      <Box
        ref={ref}
        sx={{
          display: 'flex',
          alignItems: 'center',
          minWidth: 120,
          maxWidth: 200,
          height: 32,
          px: 1,
          cursor: 'pointer',
          backgroundColor: isActive ? 'action.selected' : 'transparent',
          borderRight: '1px solid',
          borderColor: 'divider',
          opacity: isDragging ? 0.5 : 1,
          borderBottom: isOver ? '2px solid' : 'none',
          borderBottomColor: 'primary.main',
          '&:hover': {
            backgroundColor: isActive ? 'action.selected' : 'action.hover'
          }
        }}
        onClick={onActivate}
        onContextMenu={handleContextMenu}
      >
        <TerminalIcon
          sx={{
            fontSize: 16,
            mr: 0.5,
            color: getTabColor()
          }}
        />
        
        <Box
          sx={{
            flex: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontSize: '0.875rem',
            color: isActive ? 'text.primary' : 'text.secondary'
          }}
        >
          {tab.title}
        </Box>

        {tab.badge && (
          <Chip
            size="small"
            label={tab.badge.count}
            color={tab.badge.type === 'error' ? 'error' : tab.badge.type === 'warning' ? 'warning' : 'info'}
            sx={{
              height: 16,
              fontSize: '0.65rem',
              ml: 0.5,
              mr: 0.5
            }}
          />
        )}

        {canClose && (
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            sx={{
              width: 20,
              height: 20,
              ml: 0.5,
              opacity: isActive ? 1 : 0,
              transition: 'opacity 0.2s',
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            }}
          >
            <Close sx={{ fontSize: 14 }} />
          </IconButton>
        )}
      </Box>

      <Menu
        open={!!contextMenu}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={contextMenu}
      >
        <MenuItem onClick={handleRename}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Rename Tab</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleDuplicate}>
          <ListItemIcon>
            <ContentCopy fontSize="small" />
          </ListItemIcon>
          <ListItemText>Duplicate Tab</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleSplit}>
          <ListItemIcon>
            <SplitScreen fontSize="small" />
          </ListItemIcon>
          <ListItemText>Split Terminal</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleExport}>
          <ListItemIcon>
            <Download fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Session</ListItemText>
        </MenuItem>

        {canClose && (
          <>
            <Divider />
            <MenuItem onClick={onClose}>
              <ListItemIcon>
                <Close fontSize="small" />
              </ListItemIcon>
              <ListItemText>Close Tab</ListItemText>
            </MenuItem>
          </>
        )}
      </Menu>

      <Dialog open={renameDialog} onClose={() => setRenameDialog(false)}>
        <DialogTitle>Rename Tab</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            variant="outlined"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleRenameConfirm();
              } else if (e.key === 'Escape') {
                setRenameDialog(false);
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialog(false)}>Cancel</Button>
          <Button onClick={handleRenameConfirm} variant="contained">
            Rename
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

interface TerminalTabsProps {
  workspaceId: string;
  className?: string;
}

export const TerminalTabs: React.FC<TerminalTabsProps> = ({
  workspaceId,
  className
}) => {
  const {
    workspaces,
    createTab,
    closeTab,
    setActiveTab,
    renameTab,
    createSession
  } = useTerminalStore();

  const workspace = workspaces.find(w => w.id === workspaceId);
  
  if (!workspace) {
    return null;
  }

  const handleCreateTab = useCallback(() => {
    const tabId = createTab(workspaceId, `Terminal ${workspace.tabs.length + 1}`);
    createSession(workspaceId, tabId);
  }, [workspaceId, workspace.tabs.length, createTab, createSession]);

  const handleCloseTab = useCallback((tabId: string) => {
    closeTab(workspaceId, tabId);
  }, [workspaceId, closeTab]);

  const handleActivateTab = useCallback((tabId: string) => {
    setActiveTab(workspaceId, tabId);
  }, [workspaceId, setActiveTab]);

  const handleRenameTab = useCallback((tabId: string, newTitle: string) => {
    renameTab(workspaceId, tabId, newTitle);
  }, [workspaceId, renameTab]);

  const handleDuplicateTab = useCallback((tab: TerminalTab) => {
    const newTabId = createTab(workspaceId, `${tab.title} (Copy)`);
    
    // Duplicate sessions from original tab
    tab.sessions.forEach(session => {
      createSession(workspaceId, newTabId, {
        title: session.title,
        cwd: session.cwd,
        shell: session.shell,
        environment: { ...session.environment }
      });
    });
  }, [workspaceId, createTab, createSession]);

  const handleSplitTab = useCallback((tab: TerminalTab) => {
    // Create a new session in the same tab
    if (tab.sessions.length > 0) {
      const activeSession = tab.sessions.find(s => s.id === tab.activeSessionId) || tab.sessions[0];
      createSession(workspaceId, tab.id, {
        title: activeSession.title,
        cwd: activeSession.cwd,
        shell: activeSession.shell,
        environment: { ...activeSession.environment }
      });
    }
  }, [workspaceId, createSession]);

  const handleExportTab = useCallback((tab: TerminalTab) => {
    const exportData = {
      tab: {
        title: tab.title,
        sessions: tab.sessions.map(session => ({
          title: session.title,
          cwd: session.cwd,
          history: session.history,
          shell: session.shell,
          environment: session.environment
        }))
      },
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `terminal-session-${tab.title}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  return (
    <DndProvider backend={HTML5Backend}>
      <Box
        className={className}
        sx={{
          display: 'flex',
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper',
          minHeight: 32
        }}
      >
        <Box sx={{ display: 'flex', flex: 1, overflow: 'auto' }}>
          {workspace.tabs.map((tab) => (
            <TabItem
              key={tab.id}
              tab={tab}
              workspaceId={workspaceId}
              isActive={tab.id === workspace.activeTabId}
              onActivate={() => handleActivateTab(tab.id)}
              onClose={() => handleCloseTab(tab.id)}
              onRename={(newTitle) => handleRenameTab(tab.id, newTitle)}
              onDuplicate={() => handleDuplicateTab(tab)}
              onSplit={() => handleSplitTab(tab)}
              onExport={() => handleExportTab(tab)}
              canClose={workspace.tabs.length > 1}
            />
          ))}
        </Box>

        <Tooltip title="New Tab (Ctrl+Shift+T)">
          <IconButton
            size="small"
            onClick={handleCreateTab}
            sx={{
              mx: 0.5,
              width: 28,
              height: 28
            }}
          >
            <Add fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </DndProvider>
  );
};