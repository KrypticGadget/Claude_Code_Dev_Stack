import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Breadcrumbs,
  Link,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Description as DocsIcon,
  Code as CodeIcon,
  Architecture as ArchitectureIcon,
  QuestionAnswer as GuideIcon,
  Api as ApiIcon,
  BugReport as TroubleshootIcon,
  Launch as LaunchIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet-async';

const Documentation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const documentationSections = [
    {
      title: 'Getting Started',
      description: 'Quick start guide and installation instructions',
      icon: GuideIcon,
      color: 'primary',
      items: [
        'Installation Guide',
        'Quick Start Tutorial',
        'Configuration',
        'First Project Setup',
      ],
    },
    {
      title: 'API Reference',
      description: 'Complete API documentation and examples',
      icon: ApiIcon,
      color: 'secondary',
      items: [
        'REST API Endpoints',
        'WebSocket Events',
        'Authentication',
        'Rate Limiting',
      ],
    },
    {
      title: 'Architecture',
      description: 'System architecture and design patterns',
      icon: ArchitectureIcon,
      color: 'info',
      items: [
        'System Overview',
        'Component Architecture',
        'Data Flow',
        'Security Model',
      ],
    },
    {
      title: 'Code Examples',
      description: 'Sample code and implementation patterns',
      icon: CodeIcon,
      color: 'success',
      items: [
        'React Components',
        'API Integration',
        'Custom Hooks',
        'Testing Examples',
      ],
    },
    {
      title: 'Troubleshooting',
      description: 'Common issues and solutions',
      icon: TroubleshootIcon,
      color: 'warning',
      items: [
        'Connection Issues',
        'Performance Problems',
        'Error Messages',
        'Debug Tools',
      ],
    },
  ];

  const recentDocs = [
    {
      title: 'React PWA Implementation',
      description: 'How to build a Progressive Web App with React',
      lastUpdated: '2 hours ago',
      category: 'Guide',
    },
    {
      title: 'WebSocket Integration',
      description: 'Real-time communication setup and best practices',
      lastUpdated: '1 day ago',
      category: 'API',
    },
    {
      title: 'Component Library Usage',
      description: 'Using the unified UI component library effectively',
      lastUpdated: '3 days ago',
      category: 'Components',
    },
    {
      title: 'State Management Patterns',
      description: 'Best practices for managing application state',
      lastUpdated: '1 week ago',
      category: 'Architecture',
    },
  ];

  const popularSearches = [
    'API authentication',
    'Component props',
    'WebSocket setup',
    'Error handling',
    'Performance optimization',
    'Testing strategies',
  ];

  const filteredSections = documentationSections.filter(section =>
    section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.items.some(item => item.toLowerCase().includes(searchQuery.toLowerCase()))
  );

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
        <title>Documentation - Claude Code Dev Stack</title>
        <meta name="description" content="Comprehensive documentation for Claude Code development environment" />
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
              <Breadcrumbs
                separator={<NavigateNextIcon fontSize="small" />}
                sx={{ mb: 2 }}
              >
                <Link color="inherit" href="/">
                  Home
                </Link>
                <Typography color="text.primary">Documentation</Typography>
              </Breadcrumbs>
              
              <Typography variant="h4" fontWeight={700} gutterBottom>
                Documentation
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Everything you need to know about Claude Code Dev Stack
              </Typography>
            </Box>
          </motion.div>

          {/* Search Bar */}
          <motion.div variants={itemVariants}>
            <Box sx={{ mb: 4 }}>
              <TextField
                fullWidth
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ maxWidth: 600 }}
              />
              
              {!searchQuery && (
                <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                    Popular searches:
                  </Typography>
                  {popularSearches.map((search) => (
                    <Chip
                      key={search}
                      label={search}
                      size="small"
                      variant="outlined"
                      onClick={() => setSearchQuery(search)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              )}
            </Box>
          </motion.div>

          <Grid container spacing={3}>
            {/* Main Documentation Sections */}
            <Grid item xs={12} md={8}>
              <motion.div variants={itemVariants}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Documentation Sections
                </Typography>
                
                <Grid container spacing={2}>
                  {filteredSections.map((section) => (
                    <Grid item xs={12} sm={6} key={section.title}>
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card
                          sx={{
                            height: '100%',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease-in-out',
                            '&:hover': {
                              bgcolor: 'action.hover',
                              borderColor: `${section.color}.main`,
                            },
                          }}
                          variant="outlined"
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
                              <Box
                                sx={{
                                  p: 1,
                                  borderRadius: 1,
                                  bgcolor: `${section.color}.main`,
                                  color: 'white',
                                }}
                              >
                                <section.icon />
                              </Box>
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="h6" fontWeight={600} gutterBottom>
                                  {section.title}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" paragraph>
                                  {section.description}
                                </Typography>
                              </Box>
                            </Box>
                            
                            <List dense>
                              {section.items.slice(0, 3).map((item) => (
                                <ListItem key={item} sx={{ py: 0.5, px: 0 }}>
                                  <ListItemIcon sx={{ minWidth: 24 }}>
                                    <DocsIcon fontSize="small" color="action" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={
                                      <Typography variant="body2">
                                        {item}
                                      </Typography>
                                    }
                                  />
                                </ListItem>
                              ))}
                              {section.items.length > 3 && (
                                <ListItem sx={{ py: 0.5, px: 0 }}>
                                  <ListItemText
                                    primary={
                                      <Typography variant="caption" color="text.secondary">
                                        +{section.items.length - 3} more items
                                      </Typography>
                                    }
                                  />
                                </ListItem>
                              )}
                            </List>
                          </CardContent>
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </motion.div>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} md={4}>
              <motion.div variants={itemVariants}>
                {/* Recent Updates */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Recent Updates
                    </Typography>
                    
                    <List>
                      {recentDocs.map((doc, index) => (
                        <React.Fragment key={doc.title}>
                          <ListItem
                            sx={{
                              px: 0,
                              cursor: 'pointer',
                              '&:hover': {
                                bgcolor: 'action.hover',
                              },
                            }}
                          >
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="body2" fontWeight={500}>
                                    {doc.title}
                                  </Typography>
                                  <IconButton size="small">
                                    <LaunchIcon fontSize="small" />
                                  </IconButton>
                                </Box>
                              }
                              secondary={
                                <Box>
                                  <Typography variant="caption" color="text.secondary" paragraph>
                                    {doc.description}
                                  </Typography>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Chip
                                      size="small"
                                      label={doc.category}
                                      variant="outlined"
                                    />
                                    <Typography variant="caption" color="text.secondary">
                                      {doc.lastUpdated}
                                    </Typography>
                                  </Box>
                                </Box>
                              }
                            />
                          </ListItem>
                          {index < recentDocs.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  </CardContent>
                </Card>

                {/* Quick Links */}
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Quick Links
                    </Typography>
                    
                    <List>
                      <ListItem
                        button
                        sx={{
                          px: 1,
                          borderRadius: 1,
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemIcon>
                          <CodeIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="GitHub Repository"
                          secondary="View source code"
                        />
                        <Tooltip title="Open in new tab">
                          <IconButton size="small">
                            <LaunchIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </ListItem>
                      
                      <ListItem
                        button
                        sx={{
                          px: 1,
                          borderRadius: 1,
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemIcon>
                          <ApiIcon color="secondary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="API Explorer"
                          secondary="Interactive API testing"
                        />
                        <Tooltip title="Open in new tab">
                          <IconButton size="small">
                            <LaunchIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </ListItem>
                      
                      <ListItem
                        button
                        sx={{
                          px: 1,
                          borderRadius: 1,
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemIcon>
                          <GuideIcon color="info" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Video Tutorials"
                          secondary="Step-by-step guides"
                        />
                        <Tooltip title="Open in new tab">
                          <IconButton size="small">
                            <LaunchIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </ListItem>
                    </List>
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

export default Documentation;