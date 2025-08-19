import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Code as CodeIcon,
  Description as DocsIcon,
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  CloudDone as ConnectedIcon,
  Refresh as RefreshIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

import { useAppStore } from '../../store/appStore';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { isConnected, messages, notifications } = useAppStore();

  // Mock data for dashboard metrics
  const metrics = {
    totalMessages: messages.length,
    activeProjects: 3,
    documentsGenerated: 12,
    codeGenerated: '2.4k lines',
    systemStatus: {
      cpu: 45,
      memory: 62,
      storage: 23,
    },
    recentActivity: [
      {
        id: 1,
        type: 'chat',
        title: 'New chat session started',
        time: '2 minutes ago',
        icon: ChatIcon,
      },
      {
        id: 2,
        type: 'code',
        title: 'React component generated',
        time: '15 minutes ago',
        icon: CodeIcon,
      },
      {
        id: 3,
        type: 'docs',
        title: 'Documentation updated',
        time: '1 hour ago',
        icon: DocsIcon,
      },
    ],
    quickActions: [
      {
        title: 'Start Chat',
        description: 'Begin a new conversation with Claude',
        icon: ChatIcon,
        color: 'primary',
        path: '/chat',
      },
      {
        title: 'View Docs',
        description: 'Browse interactive documentation',
        icon: DocsIcon,
        color: 'secondary',
        path: '/docs',
      },
      {
        title: 'Components',
        description: 'Explore UI component library',
        icon: CodeIcon,
        color: 'info',
        path: '/components',
      },
    ],
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <>
      <Helmet>
        <title>Dashboard - Claude Code Dev Stack</title>
        <meta name="description" content="Overview of your Claude Code development environment" />
      </Helmet>

      <Box sx={{ p: 3 }}>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Header */}
          <motion.div variants={itemVariants}>
            <Box sx={{ mb: 4 }}>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                Welcome to Claude Code Dev Stack
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Your AI-powered development environment is ready. Let's build something amazing together.
              </Typography>
            </Box>
          </motion.div>

          {/* Status Overview */}
          <motion.div variants={itemVariants}>
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <ChatIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h5" fontWeight={600}>
                          {metrics.totalMessages}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Chat Messages
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}>
                        <CodeIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h5" fontWeight={600}>
                          {metrics.activeProjects}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Active Projects
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'info.main' }}>
                        <DocsIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h5" fontWeight={600}>
                          {metrics.documentsGenerated}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Docs Generated
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'success.main' }}>
                        <TimelineIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h5" fontWeight={600}>
                          {metrics.codeGenerated}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Code Generated
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>

          <Grid container spacing={3}>
            {/* Quick Actions */}
            <Grid item xs={12} md={6}>
              <motion.div variants={itemVariants}>
                <Card sx={{ height: 'fit-content' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Quick Actions
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      {metrics.quickActions.map((action) => (
                        <Grid item xs={12} key={action.title}>
                          <motion.div
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <Card
                              variant="outlined"
                              sx={{
                                cursor: 'pointer',
                                transition: 'all 0.2s ease-in-out',
                                '&:hover': {
                                  bgcolor: 'action.hover',
                                  borderColor: `${action.color}.main`,
                                },
                              }}
                              onClick={() => navigate(action.path)}
                            >
                              <CardContent sx={{ py: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                  <Avatar sx={{ bgcolor: `${action.color}.main` }}>
                                    <action.icon />
                                  </Avatar>
                                  <Box sx={{ flex: 1 }}>
                                    <Typography variant="subtitle1" fontWeight={600}>
                                      {action.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {action.description}
                                    </Typography>
                                  </Box>
                                  <LaunchIcon color="action" />
                                </Box>
                              </CardContent>
                            </Card>
                          </motion.div>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* System Status */}
            <Grid item xs={12} md={6}>
              <motion.div variants={itemVariants}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" fontWeight={600}>
                        System Status
                      </Typography>
                      <Chip
                        icon={<ConnectedIcon />}
                        label={isConnected ? 'Connected' : 'Disconnected'}
                        color={isConnected ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <SpeedIcon color="primary" fontSize="small" />
                          <Typography variant="body2">
                            CPU Usage
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                            {metrics.systemStatus.cpu}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={metrics.systemStatus.cpu}
                          color="primary"
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>

                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <MemoryIcon color="secondary" fontSize="small" />
                          <Typography variant="body2">
                            Memory Usage
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                            {metrics.systemStatus.memory}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={metrics.systemStatus.memory}
                          color="secondary"
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>

                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <StorageIcon color="info" fontSize="small" />
                          <Typography variant="body2">
                            Storage Usage
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                            {metrics.systemStatus.storage}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={metrics.systemStatus.storage}
                          color="info"
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Recent Activity */}
            <Grid item xs={12}>
              <motion.div variants={itemVariants}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" fontWeight={600}>
                        Recent Activity
                      </Typography>
                      <Tooltip title="Refresh">
                        <IconButton size="small">
                          <RefreshIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      {metrics.recentActivity.map((activity) => (
                        <Box
                          key={activity.id}
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            p: 2,
                            border: 1,
                            borderColor: 'divider',
                            borderRadius: 1,
                            '&:hover': {
                              bgcolor: 'action.hover',
                            },
                          }}
                        >
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                            <activity.icon fontSize="small" />
                          </Avatar>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="body2" fontWeight={500}>
                              {activity.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {activity.time}
                            </Typography>
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        </motion.div>
      </Box>
    </>
  );
};

export default Dashboard;