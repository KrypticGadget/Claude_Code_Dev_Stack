import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Alert,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  Terminal as TerminalIcon,
  Code,
  Settings,
  Speed,
  Security,
  CloudSync,
  Palette,
  Keyboard
} from '@mui/icons-material';

import { TerminalContainer } from '../components/terminal/TerminalContainer';
import { useTerminalStore } from '../store/terminalStore';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
);

export const TerminalPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [demoMode, setDemoMode] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);

  const {
    workspaces,
    getAllSessions,
    config,
    themes
  } = useTerminalStore();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const features = [
    {
      icon: <TerminalIcon color="primary" />,
      title: 'XTerm.js Integration',
      description: 'Full terminal emulation with complete escape sequence support and high performance rendering.',
      details: [
        'WebGL and Canvas rendering',
        'UTF-8 support',
        'Mouse support',
        'True color support'
      ]
    },
    {
      icon: <Code color="primary" />,
      title: 'Claude Code Integration',
      description: 'Built-in Claude Code commands for seamless AI-powered development workflow.',
      details: [
        'Agent invocation',
        'Smart completions',
        'Context awareness',
        'Workflow automation'
      ]
    },
    {
      icon: <Settings color="primary" />,
      title: 'Advanced Configuration',
      description: 'Comprehensive customization options for fonts, themes, keyboard shortcuts, and behavior.',
      details: [
        'Custom themes',
        'Font configuration',
        'Keyboard shortcuts',
        'Session persistence'
      ]
    },
    {
      icon: <Speed color="primary" />,
      title: 'Performance Optimized',
      description: 'Optimized for handling large outputs and multiple concurrent sessions efficiently.',
      details: [
        'Efficient scrollback',
        'Memory management',
        'Background processes',
        'Connection pooling'
      ]
    },
    {
      icon: <Security color="primary" />,
      title: 'Secure by Design',
      description: 'Secure WebSocket connections with proper authentication and authorization.',
      details: [
        'Encrypted connections',
        'Session isolation',
        'Permission management',
        'Audit logging'
      ]
    },
    {
      icon: <CloudSync color="primary" />,
      title: 'Session Management',
      description: 'Persistent sessions across browser restarts with tab management and workspace organization.',
      details: [
        'Session persistence',
        'Multi-tab support',
        'Workspace management',
        'Export/Import'
      ]
    }
  ];

  const shortcuts = [
    { key: 'Ctrl+Shift+T', action: 'New terminal tab' },
    { key: 'Ctrl+Shift+N', action: 'New terminal window' },
    { key: 'Ctrl+Shift+W', action: 'Close current tab' },
    { key: 'Ctrl+Shift+F', action: 'Search in terminal' },
    { key: 'Ctrl+Shift+C', action: 'Copy selection' },
    { key: 'Ctrl+Shift+V', action: 'Paste from clipboard' },
    { key: 'Ctrl++', action: 'Increase font size' },
    { key: 'Ctrl+-', action: 'Decrease font size' },
    { key: 'Ctrl+0', action: 'Reset font size' },
    { key: 'F11', action: 'Toggle fullscreen' }
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* Header */}
      <Box sx={{ backgroundColor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="xl">
          <Box sx={{ py: 3 }}>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <TerminalIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              <Box>
                <Typography variant="h3" component="h1" gutterBottom>
                  Claude Code Terminal
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Full-featured terminal emulator with XTerm.js and advanced session management
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="center" gap={2}>
              <Chip
                label={`${workspaces.length} Workspaces`}
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`${getAllSessions().length} Active Sessions`}
                color="secondary"
                variant="outlined"
              />
              <Chip
                label={`${Object.keys(themes).length} Themes`}
                color="info"
                variant="outlined"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={demoMode}
                    onChange={(e) => setDemoMode(e.target.checked)}
                  />
                }
                label="Demo Mode"
              />
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} sx={{ mb: 3 }}>
          <Tab label="Terminal" />
          <Tab label="Features" />
          <Tab label="Configuration" />
          <Tab label="Shortcuts" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <Paper elevation={2} sx={{ height: '70vh', overflow: 'hidden' }}>
            <TerminalContainer
              height="100%"
              showToolbar={true}
              allowFullscreen={true}
            />
          </Paper>

          {demoMode && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <strong>Demo Mode Active:</strong> The terminal is running in demonstration mode. 
              All Claude Code commands are available for testing. Try commands like:
              <br />
              • <code>claude-help</code> - Show available commands
              <br />
              • <code>claude-agent-list</code> - List all agents
              <br />
              • <code>claude-invoke @agent-testing "Create unit tests"</code> - Invoke an agent
            </Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      {feature.icon}
                      <Typography variant="h6" component="h3">
                        {feature.title}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {feature.description}
                    </Typography>

                    <Box>
                      {feature.details.map((detail, idx) => (
                        <Chip
                          key={idx}
                          label={detail}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Palette color="primary" />
                    <Typography variant="h6">Current Theme</Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Theme: {Object.keys(themes).find(name => themes[name] === config.theme) || 'Custom'}
                  </Typography>

                  <Box display="flex" gap={1} flexWrap="wrap">
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: config.theme.foreground,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 0.5
                      }}
                      title="Foreground"
                    />
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: config.theme.background,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 0.5
                      }}
                      title="Background"
                    />
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: config.theme.red,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 0.5
                      }}
                      title="Red"
                    />
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: config.theme.green,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 0.5
                      }}
                      title="Green"
                    />
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: config.theme.blue,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 0.5
                      }}
                      title="Blue"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Settings color="primary" />
                    <Typography variant="h6">Current Settings</Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary">
                    Font Family: {config.fontFamily}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Font Size: {config.fontSize}px
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cursor Style: {config.cursorStyle}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Scrollback: {config.scrollback} lines
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Renderer: {config.rendererType}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <Keyboard color="primary" />
                <Typography variant="h6">Keyboard Shortcuts</Typography>
              </Box>

              <Grid container spacing={2}>
                {shortcuts.map((shortcut, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        p: 1,
                        backgroundColor: 'action.hover',
                        borderRadius: 1
                      }}
                    >
                      <Typography variant="body2" fontFamily="monospace">
                        {shortcut.key}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {shortcut.action}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Claude Code Commands
              </Typography>
              
              <Box sx={{ fontFamily: 'monospace', backgroundColor: 'action.hover', p: 2, borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  <strong>claude-help</strong> - Show available commands<br />
                  <strong>claude-agent-list</strong> - List all Claude Code agents<br />
                  <strong>claude-invoke &lt;agent&gt; &lt;task&gt;</strong> - Invoke a specific agent<br />
                  <strong>claude-status</strong> - Show system status<br />
                  <strong>claude-config &lt;action&gt;</strong> - Manage configuration
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </TabPanel>
      </Container>
    </Box>
  );
};