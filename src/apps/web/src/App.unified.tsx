import React, { useEffect, useState, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline, Box, Drawer, AppBar, Toolbar, IconButton, Typography, List, ListItem, ListItemIcon, ListItemText, Badge, Divider, Avatar, Chip } from '@mui/material'
import { 
  Menu as MenuIcon, 
  Dashboard as DashboardIcon,
  SmartToy as AgentIcon,
  Extension as HookIcon,
  VolumeUp as AudioIcon,
  Code as GeneratorIcon,
  BugReport as LSPIcon,
  Analytics as SemanticIcon,
  Pattern as PatternIcon,
  PhotoLibrary as VisualIcon,
  AccountTree as PlanningIcon,
  Chat as ChatIcon,
  Web as BrowserIcon,
  Hub as MCPIcon,
  Settings as SettingsIcon,
  Notifications as NotificationIcon,
  CheckCircle as ConnectedIcon,
  Error as DisconnectedIcon,
  Mic as VoiceIcon,
  Task as TaskIcon
} from '@mui/icons-material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useWebSocketStore, useWebSocketConnection, useAgents, useTasks, useHooks, useAudio, useStatusline } from './services/unifiedWebSocket'
import { LoadingSpinner } from './components/ui/LoadingSpinner'

// Lazy load all feature pages
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'))
const AgentsPage = lazy(() => import('./features/agents/AgentsPage'))
const HooksPage = lazy(() => import('./features/hooks/HooksPage'))
const AudioPage = lazy(() => import('./features/audio/AudioPage'))
const GeneratorsPage = lazy(() => import('./features/generators/GeneratorsPage'))
const LSPPage = lazy(() => import('./features/lsp/LSPPage'))
const SemanticPage = lazy(() => import('./features/semantic/SemanticPage'))
const PatternsPage = lazy(() => import('./features/patterns/PatternsPage'))
const VisualDocsPage = lazy(() => import('./features/visual-docs/VisualDocsPage'))
const PlanningPage = lazy(() => import('./features/planning/PlanningPage'))
const ChatPage = lazy(() => import('./pages/chat/Chat'))
const BrowserPage = lazy(() => import('./features/browser/BrowserPage'))
const MCPManagerPage = lazy(() => import('./features/mcp-manager/MCPManagerPage'))
const TasksPage = lazy(() => import('./features/agents/TaskMonitor'))
const VoicePage = lazy(() => import('./features/voice/VoicePage'))
const SettingsPage = lazy(() => import('./pages/settings/Settings'))

const queryClient = new QueryClient()

const drawerWidth = 280

// Navigation structure with all features
const navigationItems = [
  { 
    category: 'Core',
    items: [
      { title: 'Dashboard', icon: <DashboardIcon />, path: '/', badge: null },
      { title: 'Agents (28)', icon: <AgentIcon />, path: '/agents', badge: 'active' },
      { title: 'Hooks (37)', icon: <HookIcon />, path: '/hooks', badge: 'triggered' },
      { title: 'Tasks', icon: <TaskIcon />, path: '/tasks', badge: null },
      { title: 'Audio System', icon: <AudioIcon />, path: '/audio', badge: 'playing' },
    ]
  },
  {
    category: 'Generators & Analysis',
    items: [
      { title: 'MCP Generators', icon: <GeneratorIcon />, path: '/generators', badge: null },
      { title: 'LSP Diagnostics', icon: <LSPIcon />, path: '/lsp', badge: 'errors' },
      { title: 'Semantic Analysis', icon: <SemanticIcon />, path: '/semantic', badge: null },
      { title: 'Pattern Detection', icon: <PatternIcon />, path: '/patterns', badge: 'detected' },
    ]
  },
  {
    category: 'Documentation & Planning',
    items: [
      { title: 'Visual Docs', icon: <VisualIcon />, path: '/visual-docs', badge: null },
      { title: 'BMAD Planning', icon: <PlanningIcon />, path: '/planning', badge: null },
    ]
  },
  {
    category: 'Communication',
    items: [
      { title: 'AI Chat', icon: <ChatIcon />, path: '/chat', badge: 'unread' },
      { title: 'Voice Assistant', icon: <VoiceIcon />, path: '/voice', badge: null },
    ]
  },
  {
    category: 'Services',
    items: [
      { title: 'Browser Monitor', icon: <BrowserIcon />, path: '/browser', badge: null },
      { title: 'MCP Manager', icon: <MCPIcon />, path: '/mcp-manager', badge: 'services' },
      { title: 'Settings', icon: <SettingsIcon />, path: '/settings', badge: null },
    ]
  }
]

function UnifiedApp() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(true)
  const { connected, reconnecting } = useWebSocketConnection()
  const agents = useAgents()
  const tasks = useTasks()
  const hooks = useHooks()
  const audio = useAudio()
  const statusline = useStatusline()

  // Create theme
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#6366f1',
      },
      secondary: {
        main: '#8b5cf6',
      },
      success: {
        main: '#10b981',
      },
      error: {
        main: '#ef4444',
      },
      warning: {
        main: '#f59e0b',
      },
      background: {
        default: darkMode ? '#0f172a' : '#f8fafc',
        paper: darkMode ? '#1e293b' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    },
    shape: {
      borderRadius: 12,
    },
  })

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  // Badge content logic
  const getBadgeContent = (badge: string | null) => {
    if (!badge) return null
    
    switch (badge) {
      case 'active':
        return agents.active
      case 'triggered':
        return hooks.triggered
      case 'playing':
        return audio.playing ? '♪' : null
      case 'errors':
        return 3 // Mock
      case 'detected':
        return 5 // Mock
      case 'unread':
        return 2 // Mock
      case 'services':
        return 4 // Mock
      default:
        return null
    }
  }

  const drawer = (
    <Box sx={{ overflow: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
            CC
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight="bold">
              Claude Code v3
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {connected ? (
                <>
                  <ConnectedIcon sx={{ fontSize: 14, color: 'success.main' }} />
                  <Typography variant="caption" color="success.main">
                    Connected
                  </Typography>
                </>
              ) : reconnecting ? (
                <>
                  <DisconnectedIcon sx={{ fontSize: 14, color: 'warning.main' }} />
                  <Typography variant="caption" color="warning.main">
                    Reconnecting...
                  </Typography>
                </>
              ) : (
                <>
                  <DisconnectedIcon sx={{ fontSize: 14, color: 'error.main' }} />
                  <Typography variant="caption" color="error.main">
                    Disconnected
                  </Typography>
                </>
              )}
            </Box>
          </Box>
        </Box>

        {/* Quick Stats */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip size="small" label={`${agents.active}/${agents.total} Agents`} color="primary" variant="outlined" />
          <Chip size="small" label={`${tasks.completed}/${tasks.total} Tasks`} color="secondary" variant="outlined" />
          <Chip size="small" label={`${hooks.triggered} Hooks`} color="success" variant="outlined" />
        </Box>
      </Box>

      {/* Navigation */}
      <List sx={{ flexGrow: 1, py: 0 }}>
        {navigationItems.map((category, idx) => (
          <Box key={idx}>
            <ListItem>
              <Typography variant="overline" color="text.secondary" sx={{ px: 2, py: 1 }}>
                {category.category}
              </Typography>
            </ListItem>
            {category.items.map((item) => {
              const badgeContent = getBadgeContent(item.badge)
              return (
                <ListItem
                  button
                  key={item.path}
                  component={Link}
                  to={item.path}
                  sx={{
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                    '&.active': {
                      bgcolor: 'action.selected',
                      borderLeft: '3px solid',
                      borderColor: 'primary.main',
                    }
                  }}
                >
                  <ListItemIcon>
                    <Badge badgeContent={badgeContent} color="error" variant={typeof badgeContent === 'string' ? 'standard' : 'dot'}>
                      {item.icon}
                    </Badge>
                  </ListItemIcon>
                  <ListItemText primary={item.title} />
                </ListItem>
              )
            })}
            {idx < navigationItems.length - 1 && <Divider sx={{ my: 1 }} />}
          </Box>
        ))}
      </List>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          v3.0.0 • All systems operational
        </Typography>
      </Box>
    </Box>
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', height: '100vh' }}>
            {/* App Bar */}
            <AppBar
              position="fixed"
              sx={{
                width: { sm: `calc(100% - ${drawerWidth}px)` },
                ml: { sm: `${drawerWidth}px` },
              }}
            >
              <Toolbar>
                <IconButton
                  color="inherit"
                  aria-label="open drawer"
                  edge="start"
                  onClick={handleDrawerToggle}
                  sx={{ mr: 2, display: { sm: 'none' } }}
                >
                  <MenuIcon />
                </IconButton>
                
                <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                  Claude Code Dev Stack - Unified Experience
                </Typography>

                {/* Status Line */}
                {statusline && (
                  <Typography variant="body2" sx={{ mr: 2, fontFamily: 'monospace' }}>
                    {statusline}
                  </Typography>
                )}

                {/* Notifications */}
                <IconButton color="inherit">
                  <Badge badgeContent={4} color="error">
                    <NotificationIcon />
                  </Badge>
                </IconButton>
              </Toolbar>
            </AppBar>

            {/* Drawer */}
            <Box
              component="nav"
              sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            >
              <Drawer
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{ keepMounted: true }}
                sx={{
                  display: { xs: 'block', sm: 'none' },
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
              >
                {drawer}
              </Drawer>
              <Drawer
                variant="permanent"
                sx={{
                  display: { xs: 'none', sm: 'block' },
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
                open
              >
                {drawer}
              </Drawer>
            </Box>

            {/* Main Content */}
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                p: 3,
                width: { sm: `calc(100% - ${drawerWidth}px)` },
                mt: 8,
                overflow: 'auto',
              }}
            >
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/agents" element={<AgentsPage />} />
                  <Route path="/hooks" element={<HooksPage />} />
                  <Route path="/tasks" element={<TasksPage />} />
                  <Route path="/audio" element={<AudioPage />} />
                  <Route path="/generators" element={<GeneratorsPage />} />
                  <Route path="/lsp" element={<LSPPage />} />
                  <Route path="/semantic" element={<SemanticPage />} />
                  <Route path="/patterns" element={<PatternsPage />} />
                  <Route path="/visual-docs" element={<VisualDocsPage />} />
                  <Route path="/planning" element={<PlanningPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/voice" element={<VoicePage />} />
                  <Route path="/browser" element={<BrowserPage />} />
                  <Route path="/mcp-manager" element={<MCPManagerPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </Box>
          </Box>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default UnifiedApp