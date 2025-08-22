import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Badge,
  Tooltip,
  Button,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Settings,
  Add,
  MoreVert,
  Fullscreen,
  FullscreenExit,
  Refresh,
  Download,
  Upload,
  SplitScreen,
  Tab as TabIcon,
  Terminal as TerminalIcon,
  Info,
  Warning,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useHotkeys } from 'react-hotkeys-hook';
import SplitPane from 'react-split-pane';

import { useTerminalStore } from '../../store/terminalStore';
import { Terminal } from './Terminal';
import { TerminalTabs } from './TerminalTabs';
import { TerminalSettings } from './TerminalSettings';
import { TerminalSession } from '../../types/terminal';

interface TerminalContainerProps {
  className?: string;
  height?: string | number;
  workspaceId?: string;
  showToolbar?: boolean;
  allowFullscreen?: boolean;
}

export const TerminalContainer: React.FC<TerminalContainerProps> = ({
  className,
  height = '100vh',
  workspaceId: propWorkspaceId,
  showToolbar = true,
  allowFullscreen = true
}) => {
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [splitLayout, setSplitLayout] = useState<'none' | 'horizontal' | 'vertical'>('none');
  const [notifications, setNotifications] = useState<{
    open: boolean;
    message: string;
    severity: 'info' | 'warning' | 'error' | 'success';
  }>({ open: false, message: '', severity: 'info' });

  const {
    workspaces,
    activeWorkspaceId,
    createWorkspace,
    createTab,
    createSession,
    getActiveSession,
    getAllSessions
  } = useTerminalStore();

  // Use prop workspace ID or active workspace ID
  const currentWorkspaceId = propWorkspaceId || activeWorkspaceId;
  const currentWorkspace = workspaces.find(w => w.id === currentWorkspaceId);
  const currentTab = currentWorkspace?.tabs.find(t => t.id === currentWorkspace.activeTabId);
  const sessions = currentTab?.sessions || [];
  const activeSession = sessions.find(s => s.id === currentTab?.activeSessionId);

  // Initialize workspace if none exists
  useEffect(() => {
    if (workspaces.length === 0) {
      const workspaceId = createWorkspace('Default');
      const tabId = createTab(workspaceId, 'Terminal');
      createSession(workspaceId, tabId);
    }
  }, [workspaces.length, createWorkspace, createTab, createSession]);

  // Keyboard shortcuts
  useHotkeys('ctrl+shift+t', () => {
    if (currentWorkspaceId) {
      const tabId = createTab(currentWorkspaceId, `Terminal ${(currentWorkspace?.tabs.length || 0) + 1}`);
      createSession(currentWorkspaceId, tabId);
    }
  });

  useHotkeys('ctrl+shift+n', () => {
    const workspaceId = createWorkspace(`Workspace ${workspaces.length + 1}`);
    const tabId = createTab(workspaceId, 'Terminal');
    createSession(workspaceId, tabId);
  });

  useHotkeys('f11', () => {
    if (allowFullscreen) {
      toggleFullscreen();
    }
  });

  useHotkeys('ctrl+shift+d', () => {
    setSplitLayout(prev => prev === 'horizontal' ? 'none' : 'horizontal');
  });

  useHotkeys('ctrl+alt+d', () => {
    setSplitLayout(prev => prev === 'vertical' ? 'none' : 'vertical');
  });

  const handleMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  }, []);

  const handleMenuClose = useCallback(() => {
    setMenuAnchor(null);
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!allowFullscreen) return;

    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  }, [allowFullscreen]);

  const handleNewTab = useCallback(() => {
    if (currentWorkspaceId) {
      const tabId = createTab(currentWorkspaceId, `Terminal ${(currentWorkspace?.tabs.length || 0) + 1}`);
      createSession(currentWorkspaceId, tabId);
    }
    handleMenuClose();
  }, [currentWorkspaceId, currentWorkspace?.tabs.length, createTab, createSession, handleMenuClose]);

  const handleNewWindow = useCallback(() => {
    const workspaceId = createWorkspace(`Workspace ${workspaces.length + 1}`);
    const tabId = createTab(workspaceId, 'Terminal');
    createSession(workspaceId, tabId);
    handleMenuClose();
  }, [workspaces.length, createWorkspace, createTab, createSession, handleMenuClose]);

  const handleSplitHorizontal = useCallback(() => {
    setSplitLayout(prev => prev === 'horizontal' ? 'none' : 'horizontal');
    handleMenuClose();
  }, [handleMenuClose]);

  const handleSplitVertical = useCallback(() => {
    setSplitLayout(prev => prev === 'vertical' ? 'none' : 'vertical');
    handleMenuClose();
  }, [handleMenuClose]);

  const handleExportSession = useCallback(() => {
    if (activeSession) {
      const exportData = {
        session: {
          title: activeSession.title,
          cwd: activeSession.cwd,
          history: activeSession.history,
          shell: activeSession.shell,
          environment: activeSession.environment
        },
        timestamp: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `terminal-session-${activeSession.title}-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showNotification('Session exported successfully', 'success');
    }
    handleMenuClose();
  }, [activeSession, handleMenuClose]);

  const handleImportSession = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && currentWorkspaceId) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          const tabId = createTab(currentWorkspaceId, data.session.title || 'Imported Terminal');
          createSession(currentWorkspaceId, tabId, {
            title: data.session.title,
            cwd: data.session.cwd,
            shell: data.session.shell,
            environment: data.session.environment,
            history: data.session.history || []
          });
          showNotification('Session imported successfully', 'success');
        } catch (error) {
          showNotification('Failed to import session', 'error');
          console.error('Import error:', error);
        }
      };
      reader.readAsText(file);
    }
    handleMenuClose();
  }, [currentWorkspaceId, createTab, createSession, handleMenuClose]);

  const showNotification = useCallback((message: string, severity: 'info' | 'warning' | 'error' | 'success') => {
    setNotifications({ open: true, message, severity });
  }, []);

  const handleCloseNotification = useCallback(() => {
    setNotifications(prev => ({ ...prev, open: false }));
  }, []);

  const renderTerminal = useCallback((session: TerminalSession, index?: number) => (
    <Terminal
      key={session.id}
      sessionId={session.id}
      onTitleChange={(title) => {
        // Update session title
        console.log('Title changed:', title);
      }}
      onCommand={(command) => {
        // Handle command execution
        console.log('Command executed:', command);
      }}
      onResize={(cols, rows) => {
        // Handle terminal resize
        console.log('Terminal resized:', cols, rows);
      }}
    />
  ), []);

  const renderSplitView = useCallback(() => {
    if (splitLayout === 'none' || sessions.length < 2) {
      return activeSession ? renderTerminal(activeSession) : (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          height="100%"
          color="text.secondary"
        >
          No active terminal session
        </Box>
      );
    }

    const [firstSession, secondSession] = sessions.slice(0, 2);

    return (
      <SplitPane
        split={splitLayout === 'horizontal' ? 'horizontal' : 'vertical'}
        defaultSize="50%"
        resizerStyle={{
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
          width: splitLayout === 'vertical' ? 4 : '100%',
          height: splitLayout === 'horizontal' ? 4 : '100%',
          cursor: splitLayout === 'vertical' ? 'col-resize' : 'row-resize'
        }}
      >
        {renderTerminal(firstSession)}
        {renderTerminal(secondSession)}
      </SplitPane>
    );
  }, [splitLayout, sessions, activeSession, renderTerminal]);

  if (!currentWorkspace) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        flexDirection="column"
        gap={2}
      >
        <TerminalIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
        <Typography variant="h6" color="text.secondary">
          No workspace available
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            const workspaceId = createWorkspace('Default');
            const tabId = createTab(workspaceId, 'Terminal');
            createSession(workspaceId, tabId);
          }}
        >
          Create Terminal
        </Button>
      </Box>
    );
  }

  return (
    <Box
      className={className}
      sx={{
        height,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.paper',
        overflow: 'hidden'
      }}
    >
      {showToolbar && (
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar variant="dense" sx={{ minHeight: 40 }}>
            <TerminalIcon sx={{ mr: 1, fontSize: 20 }} />
            <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
              {currentWorkspace.name}
            </Typography>

            <Badge
              badgeContent={getAllSessions().length}
              color="primary"
              sx={{ mr: 1 }}
            >
              <TabIcon />
            </Badge>

            <Tooltip title="New Tab (Ctrl+Shift+T)">
              <IconButton size="small" onClick={handleNewTab}>
                <Add />
              </IconButton>
            </Tooltip>

            <Tooltip title={`Split ${splitLayout === 'horizontal' ? 'Off' : 'Horizontal'}`}>
              <IconButton
                size="small"
                onClick={handleSplitHorizontal}
                color={splitLayout === 'horizontal' ? 'primary' : 'default'}
              >
                <SplitScreen />
              </IconButton>
            </Tooltip>

            {allowFullscreen && (
              <Tooltip title={isFullscreen ? 'Exit Fullscreen (F11)' : 'Fullscreen (F11)'}>
                <IconButton size="small" onClick={toggleFullscreen}>
                  {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                </IconButton>
              </Tooltip>
            )}

            <Tooltip title="Settings">
              <IconButton size="small" onClick={() => setSettingsOpen(true)}>
                <Settings />
              </IconButton>
            </Tooltip>

            <IconButton size="small" onClick={handleMenuOpen}>
              <MoreVert />
            </IconButton>
          </Toolbar>
        </AppBar>
      )}

      <TerminalTabs workspaceId={currentWorkspaceId} />

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {renderSplitView()}
      </Box>

      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleNewTab}>
          <ListItemIcon>
            <Add fontSize="small" />
          </ListItemIcon>
          <ListItemText>New Tab</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleNewWindow}>
          <ListItemIcon>
            <TabIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>New Window</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleSplitHorizontal}>
          <ListItemIcon>
            <SplitScreen fontSize="small" />
          </ListItemIcon>
          <ListItemText>Split Horizontal</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleSplitVertical}>
          <ListItemIcon>
            <SplitScreen 
              fontSize="small" 
              sx={{ transform: 'rotate(90deg)' }}
            />
          </ListItemIcon>
          <ListItemText>Split Vertical</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleExportSession}>
          <ListItemIcon>
            <Download fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Session</ListItemText>
        </MenuItem>

        <MenuItem component="label">
          <ListItemIcon>
            <Upload fontSize="small" />
          </ListItemIcon>
          <ListItemText>Import Session</ListItemText>
          <input
            type="file"
            accept=".json"
            hidden
            onChange={handleImportSession}
          />
        </MenuItem>

        <Divider />

        <MenuItem onClick={() => { setSettingsOpen(true); handleMenuClose(); }}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
      </Menu>

      <TerminalSettings
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      <Snackbar
        open={notifications.open}
        autoHideDuration={4000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notifications.severity}
          variant="filled"
        >
          {notifications.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};