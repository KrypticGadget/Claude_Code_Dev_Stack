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
  Tabs,
  Tab,
  Button,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  ViewModule as ComponentIcon,
  Palette as DesignIcon,
  Code as CodeIcon,
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  Launch as LaunchIcon,
  Favorite as FavoriteIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Helmet } from 'react-helmet-async';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Component {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  complexity: 'Simple' | 'Medium' | 'Complex';
  usage: string;
  props: Array<{
    name: string;
    type: string;
    required: boolean;
    default?: string;
    description: string;
  }>;
  example: string;
  preview?: React.ReactNode;
}

const Components: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('All');

  const componentCategories = [
    'All',
    'Layout',
    'Navigation',
    'Data Display',
    'Input',
    'Feedback',
    'Charts',
    'Editor',
  ];

  const sampleComponents: Component[] = [
    {
      id: 'loading-spinner',
      name: 'LoadingSpinner',
      description: 'Animated loading spinner with customizable message and size',
      category: 'Feedback',
      tags: ['loading', 'spinner', 'progress', 'animation'],
      complexity: 'Simple',
      usage: 'Used to indicate loading states in applications',
      props: [
        {
          name: 'message',
          type: 'string',
          required: false,
          default: 'Loading...',
          description: 'Message to display below the spinner',
        },
        {
          name: 'size',
          type: 'number',
          required: false,
          default: '40',
          description: 'Size of the spinner in pixels',
        },
        {
          name: 'color',
          type: "'primary' | 'secondary' | 'inherit'",
          required: false,
          default: 'primary',
          description: 'Color theme of the spinner',
        },
      ],
      example: `import LoadingSpinner from '@components/ui/LoadingSpinner';

function MyComponent() {
  return (
    <LoadingSpinner 
      message="Loading data..." 
      size={48} 
      color="primary" 
    />
  );
}`,
    },
    {
      id: 'connection-status',
      name: 'ConnectionStatus',
      description: 'Real-time connection status indicator with detailed information',
      category: 'Data Display',
      tags: ['connection', 'status', 'websocket', 'indicator'],
      complexity: 'Medium',
      usage: 'Shows connection state and provides reconnection functionality',
      props: [
        {
          name: 'isConnected',
          type: 'boolean',
          required: true,
          description: 'Current connection status',
        },
        {
          name: 'connectionInfo',
          type: 'ConnectionInfo',
          required: true,
          description: 'Connection details and metadata',
        },
      ],
      example: `import ConnectionStatus from '@components/ui/ConnectionStatus';

function App() {
  const { isConnected, connectionInfo } = useAppStore();
  
  return (
    <ConnectionStatus 
      isConnected={isConnected}
      connectionInfo={connectionInfo}
    />
  );
}`,
    },
    {
      id: 'navigation-item',
      name: 'NavigationItem',
      description: 'Animated navigation item with active state and hover effects',
      category: 'Navigation',
      tags: ['navigation', 'menu', 'router', 'animation'],
      complexity: 'Medium',
      usage: 'Building navigation menus and sidebars',
      props: [
        {
          name: 'path',
          type: 'string',
          required: true,
          description: 'Navigation path/route',
        },
        {
          name: 'label',
          type: 'string',
          required: true,
          description: 'Display label for the navigation item',
        },
        {
          name: 'icon',
          type: 'SvgIconComponent',
          required: true,
          description: 'Material-UI icon component',
        },
        {
          name: 'isActive',
          type: 'boolean',
          required: true,
          description: 'Whether this item is currently active',
        },
      ],
      example: `import NavigationItem from '@components/layout/NavigationItem';
import { Dashboard as DashboardIcon } from '@mui/icons-material';

function Sidebar() {
  return (
    <NavigationItem
      path="/dashboard"
      label="Dashboard"
      icon={DashboardIcon}
      isActive={true}
      description="Main dashboard view"
    />
  );
}`,
    },
    {
      id: 'user-menu',
      name: 'UserMenu',
      description: 'User profile menu with avatar, role, and actions',
      category: 'Navigation',
      tags: ['user', 'menu', 'profile', 'dropdown'],
      complexity: 'Complex',
      usage: 'User authentication and profile management',
      props: [
        {
          name: 'user',
          type: 'User',
          required: true,
          description: 'User object with profile information',
        },
      ],
      example: `import UserMenu from '@components/ui/UserMenu';

function Layout() {
  const { currentUser } = useAppStore();
  
  return (
    <UserMenu user={currentUser} />
  );
}`,
    },
  ];

  const filteredComponents = sampleComponents.filter(component => {
    const matchesSearch = component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         component.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         component.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'All' || component.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Simple':
        return 'success';
      case 'Medium':
        return 'warning';
      case 'Complex':
        return 'error';
      default:
        return 'default';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Show toast notification
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

  const ComponentCard: React.FC<{ component: Component }> = ({ component }) => (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            bgcolor: 'action.hover',
            boxShadow: 4,
          },
        }}
      >
        <CardContent sx={{ flex: 1 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                {component.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {component.description}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Tooltip title="Add to favorites">
                <IconButton size="small">
                  <FavoriteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Rate component">
                <IconButton size="small">
                  <StarIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Tags and Complexity */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              size="small"
              label={component.complexity}
              color={getComplexityColor(component.complexity) as any}
              variant="outlined"
            />
            <Chip
              size="small"
              label={component.category}
              color="primary"
              variant="outlined"
            />
            {component.tags.slice(0, 2).map(tag => (
              <Chip
                key={tag}
                size="small"
                label={tag}
                variant="outlined"
              />
            ))}
          </Box>

          {/* Usage */}
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>Usage:</strong> {component.usage}
          </Typography>

          {/* Props Table */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">
                Props ({component.props.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ overflow: 'auto' }}>
                {component.props.map(prop => (
                  <Box key={prop.name} sx={{ mb: 2, pb: 1, borderBottom: 1, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body2" fontWeight={600} component="code">
                        {prop.name}
                      </Typography>
                      {prop.required && (
                        <Chip size="small" label="required" color="error" variant="outlined" />
                      )}
                    </Box>
                    <Typography variant="caption" color="text.secondary" component="code" display="block">
                      {prop.type}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {prop.description}
                    </Typography>
                    {prop.default && (
                      <Typography variant="caption" color="text.secondary">
                        Default: {prop.default}
                      </Typography>
                    )}
                  </Box>
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Code Example */}
          <Accordion sx={{ mt: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">
                Code Example
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ position: 'relative' }}>
                <Box sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}>
                  <Tooltip title="Copy code">
                    <IconButton
                      size="small"
                      onClick={() => copyToClipboard(component.example)}
                      sx={{ bgcolor: 'background.paper' }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <SyntaxHighlighter
                  language="typescript"
                  style={vscDarkPlus}
                  customStyle={{
                    borderRadius: 4,
                    fontSize: '0.75rem',
                    margin: 0,
                  }}
                >
                  {component.example}
                </SyntaxHighlighter>
              </Box>
            </AccordionDetails>
          </Accordion>
        </CardContent>

        {/* Actions */}
        <Divider />
        <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
          <Button
            size="small"
            startIcon={<LaunchIcon />}
            variant="outlined"
            fullWidth
          >
            View in Storybook
          </Button>
          <Button
            size="small"
            startIcon={<CodeIcon />}
            variant="contained"
            fullWidth
          >
            View Source
          </Button>
        </Box>
      </Card>
    </motion.div>
  );

  return (
    <>
      <Helmet>
        <title>Components - Claude Code Dev Stack</title>
        <meta name="description" content="Explore the unified UI component library with examples and documentation" />
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
                Component Library
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Reusable UI components built with Material-UI and React. All components are fully documented with examples and props.
              </Typography>
            </Box>
          </motion.div>

          {/* Search and Filters */}
          <motion.div variants={itemVariants}>
            <Box sx={{ mb: 4 }}>
              <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                <TextField
                  placeholder="Search components..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ minWidth: 300 }}
                />
              </Box>

              <Tabs
                value={selectedCategory}
                onChange={(_, newValue) => setSelectedCategory(newValue)}
                variant="scrollable"
                scrollButtons="auto"
              >
                {componentCategories.map((category) => (
                  <Tab
                    key={category}
                    label={category}
                    value={category}
                  />
                ))}
              </Tabs>
            </Box>
          </motion.div>

          {/* Stats */}
          <motion.div variants={itemVariants}>
            <Box sx={{ mb: 4 }}>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={600} color="primary.main">
                        {filteredComponents.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Components
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={600} color="secondary.main">
                        {componentCategories.length - 1}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Categories
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={600} color="info.main">
                        100%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        TypeScript
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" fontWeight={600} color="success.main">
                        ✓
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Documented
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          </motion.div>

          {/* Components Grid */}
          <motion.div variants={itemVariants}>
            <AnimatePresence>
              {filteredComponents.length > 0 ? (
                <Grid container spacing={3}>
                  {filteredComponents.map((component) => (
                    <Grid item xs={12} md={6} lg={4} key={component.id}>
                      <ComponentCard component={component} />
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Box
                    sx={{
                      textAlign: 'center',
                      py: 8,
                      px: 3,
                    }}
                  >
                    <ComponentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No components found
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Try adjusting your search or filter criteria
                    </Typography>
                  </Box>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      </Box>
    </>
  );
};

export default Components;