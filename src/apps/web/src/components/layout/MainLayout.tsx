import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  useMediaQuery,
  useTheme,
  Avatar,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  Description as DocsIcon,
  ViewModule as ComponentsIcon,
  Settings as SettingsIcon,
  Code as CodeIcon,
  Notifications as NotificationsIcon,
  Brightness4 as ThemeIcon,
  CloudDone as ConnectedIcon,
  CloudOff as DisconnectedIcon,
  FolderOpen as FileExplorerIcon,
} from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

import NavigationItem from './NavigationItem';
import ConnectionStatus from '../ui/ConnectionStatus';
import UserMenu from '../ui/UserMenu';
import { useAppStore } from '../../store/appStore';

const drawerWidth = 280;

interface MainLayoutProps {
  children: React.ReactNode;
}

const navigationItems = [
  {
    path: '/dashboard',
    label: 'Dashboard',
    icon: DashboardIcon,
    description: 'Overview and quick actions',
  },
  {
    path: '/chat',
    label: 'AI Chat',
    icon: ChatIcon,
    description: 'Chat with Claude Code',
  },
  {
    path: '/file-explorer',
    label: 'File Explorer',
    icon: FileExplorerIcon,
    description: 'Advanced file management',
  },
  {
    path: '/docs',
    label: 'Documentation',
    icon: DocsIcon,
    description: 'Interactive documentation',
  },
  {
    path: '/components',
    label: 'Components',
    icon: ComponentsIcon,
    description: 'UI component library',
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: SettingsIcon,
    description: 'Application settings',
  },
];

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const { 
    isConnected, 
    notifications, 
    currentUser,
    connectionInfo 
  } = useAppStore();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigationClick = () => {
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const currentPage = navigationItems.find(item => 
    location.pathname.startsWith(item.path)
  )?.label || 'Claude Code Dev Stack';

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{ 
              bgcolor: 'primary.main',
              width: 40,
              height: 40,
            }}
          >
            <CodeIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" noWrap>
              Claude Code
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Dev Stack v3.0
            </Typography>
          </Box>
        </Box>
        
        {/* Connection Status */}
        <Box sx={{ mt: 2 }}>
          <ConnectionStatus 
            isConnected={isConnected}
            connectionInfo={connectionInfo}
          />
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ px: 2, py: 1 }}>
          {navigationItems.map((item) => (
            <NavigationItem
              key={item.path}
              {...item}
              isActive={location.pathname.startsWith(item.path)}
              onClick={handleNavigationClick}
            />
          ))}
        </List>
      </Box>

      {/* Bottom section */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        {currentUser && (
          <UserMenu user={currentUser} />
        )}
        
        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            size="small"
            icon={isConnected ? <ConnectedIcon /> : <DisconnectedIcon />}
            label={isConnected ? 'Online' : 'Offline'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
          <Chip
            size="small"
            label="PWA"
            color="primary"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ flexGrow: 1 }}
          >
            {currentPage}
          </Typography>

          {/* Header actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {notifications.length > 0 && (
              <Tooltip title={`${notifications.length} notifications`}>
                <IconButton color="inherit">
                  <NotificationsIcon />
                  <Box
                    component="span"
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      bgcolor: 'error.main',
                      color: 'white',
                      borderRadius: '50%',
                      width: 18,
                      height: 18,
                      fontSize: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {notifications.length}
                  </Box>
                </IconButton>
              </Tooltip>
            )}
            
            <Tooltip title="Toggle theme">
              <IconButton color="inherit">
                <ThemeIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawerContent}
        </Drawer>
        
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar /> {/* Spacer for fixed AppBar */}
        
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;