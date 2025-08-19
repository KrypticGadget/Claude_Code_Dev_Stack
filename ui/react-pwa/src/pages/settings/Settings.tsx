import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Button,
  Divider,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet-async';

import { useAppStore } from '../../store/appStore';

const Settings: React.FC = () => {
  const { settings, updateSettings, currentUser } = useAppStore();
  const [hasChanges, setHasChanges] = useState(false);
  const [savedRecently, setSavedRecently] = useState(false);

  const handleSettingChange = (key: string, value: any) => {
    updateSettings({ [key]: value });
    setHasChanges(true);
  };

  const handleSave = () => {
    // Settings are automatically saved via Zustand persistence
    setHasChanges(false);
    setSavedRecently(true);
    setTimeout(() => setSavedRecently(false), 3000);
  };

  const handleReset = () => {
    // Reset to default settings
    const defaultSettings = {
      theme: 'dark',
      language: 'en',
      autoSave: true,
      notifications: true,
      sound: true,
      fontSize: 14,
      codeTheme: 'github-dark',
      compactMode: false,
    };
    
    Object.entries(defaultSettings).forEach(([key, value]) => {
      updateSettings({ [key]: value });
    });
    
    setHasChanges(false);
  };

  const settingSections = [
    {
      title: 'Appearance',
      icon: PaletteIcon,
      items: [
        {
          key: 'theme',
          label: 'Theme',
          type: 'select',
          options: [
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
            { value: 'system', label: 'System' },
          ],
          description: 'Choose your preferred color theme',
        },
        {
          key: 'fontSize',
          label: 'Font Size',
          type: 'slider',
          min: 10,
          max: 20,
          step: 1,
          description: 'Adjust the base font size for the interface',
        },
        {
          key: 'compactMode',
          label: 'Compact Mode',
          type: 'switch',
          description: 'Use a more compact layout with reduced spacing',
        },
        {
          key: 'codeTheme',
          label: 'Code Theme',
          type: 'select',
          options: [
            { value: 'github-dark', label: 'GitHub Dark' },
            { value: 'github-light', label: 'GitHub Light' },
            { value: 'vscode-dark', label: 'VS Code Dark' },
            { value: 'dracula', label: 'Dracula' },
            { value: 'monokai', label: 'Monokai' },
          ],
          description: 'Color scheme for code blocks and editor',
        },
      ],
    },
    {
      title: 'Language & Region',
      icon: LanguageIcon,
      items: [
        {
          key: 'language',
          label: 'Language',
          type: 'select',
          options: [
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Español' },
            { value: 'fr', label: 'Français' },
            { value: 'de', label: 'Deutsch' },
            { value: 'ja', label: '日本語' },
            { value: 'zh', label: '中文' },
          ],
          description: 'Interface language',
        },
      ],
    },
    {
      title: 'Notifications',
      icon: NotificationsIcon,
      items: [
        {
          key: 'notifications',
          label: 'Enable Notifications',
          type: 'switch',
          description: 'Show system notifications for important events',
        },
        {
          key: 'sound',
          label: 'Sound Effects',
          type: 'switch',
          description: 'Play sounds for notifications and actions',
        },
      ],
    },
    {
      title: 'Editor',
      icon: CodeIcon,
      items: [
        {
          key: 'autoSave',
          label: 'Auto Save',
          type: 'switch',
          description: 'Automatically save changes as you type',
        },
      ],
    },
  ];

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

  const renderSettingControl = (item: any) => {
    const value = settings[item.key as keyof typeof settings];

    switch (item.type) {
      case 'switch':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={Boolean(value)}
                onChange={(e) => handleSettingChange(item.key, e.target.checked)}
              />
            }
            label={item.label}
          />
        );

      case 'select':
        return (
          <FormControl fullWidth size="small">
            <InputLabel>{item.label}</InputLabel>
            <Select
              value={value || ''}
              label={item.label}
              onChange={(e) => handleSettingChange(item.key, e.target.value)}
            >
              {item.options.map((option: any) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );

      case 'slider':
        return (
          <Box>
            <Typography variant="body2" gutterBottom>
              {item.label}: {value}
            </Typography>
            <Slider
              value={Number(value) || 0}
              onChange={(_, newValue) => handleSettingChange(item.key, newValue)}
              min={item.min}
              max={item.max}
              step={item.step}
              marks={[
                { value: item.min, label: `${item.min}` },
                { value: item.max, label: `${item.max}` },
              ]}
            />
          </Box>
        );

      case 'text':
        return (
          <TextField
            fullWidth
            size="small"
            label={item.label}
            value={value || ''}
            onChange={(e) => handleSettingChange(item.key, e.target.value)}
          />
        );

      default:
        return null;
    }
  };

  return (
    <>
      <Helmet>
        <title>Settings - Claude Code Dev Stack</title>
        <meta name="description" content="Customize your Claude Code development environment settings" />
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
                Settings
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Customize your Claude Code development environment
              </Typography>
            </Box>
          </motion.div>

          {/* Save notification */}
          {savedRecently && (
            <motion.div
              variants={itemVariants}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Alert severity="success" sx={{ mb: 3 }}>
                Settings saved successfully!
              </Alert>
            </motion.div>
          )}

          <Grid container spacing={3}>
            {/* Settings Sections */}
            <Grid item xs={12} lg={8}>
              <motion.div variants={itemVariants}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {settingSections.map((section) => (
                    <Accordion key={section.title} defaultExpanded>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <section.icon color="primary" />
                          <Typography variant="h6" fontWeight={600}>
                            {section.title}
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                          {section.items.map((item) => (
                            <Box key={item.key}>
                              {renderSettingControl(item)}
                              {item.description && (
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                  display="block"
                                  sx={{ mt: 0.5 }}
                                >
                                  {item.description}
                                </Typography>
                              )}
                            </Box>
                          ))}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              </motion.div>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} lg={4}>
              <motion.div variants={itemVariants}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Actions */}
                  <Card>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        Actions
                      </Typography>
                      
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Button
                          variant="contained"
                          startIcon={<SaveIcon />}
                          onClick={handleSave}
                          disabled={!hasChanges}
                          fullWidth
                        >
                          Save Changes
                        </Button>
                        
                        <Button
                          variant="outlined"
                          startIcon={<RefreshIcon />}
                          onClick={handleReset}
                          fullWidth
                        >
                          Reset to Defaults
                        </Button>
                      </Box>
                      
                      {hasChanges && (
                        <Alert severity="info" sx={{ mt: 2 }}>
                          You have unsaved changes
                        </Alert>
                      )}
                    </CardContent>
                  </Card>

                  {/* Profile Info */}
                  {currentUser && (
                    <Card>
                      <CardContent>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                          Profile
                        </Typography>
                        
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Name
                            </Typography>
                            <Typography variant="body1">
                              {currentUser.name}
                            </Typography>
                          </Box>
                          
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Email
                            </Typography>
                            <Typography variant="body1">
                              {currentUser.email}
                            </Typography>
                          </Box>
                          
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Role
                            </Typography>
                            <Chip
                              size="small"
                              label={currentUser.role}
                              color="primary"
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  )}

                  {/* System Info */}
                  <Card>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        System Information
                      </Typography>
                      
                      <List>
                        <ListItem>
                          <ListItemText
                            primary="Version"
                            secondary="v3.0.0"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Last Updated"
                            secondary="December 2024"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Environment"
                            secondary="Development"
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>

                  {/* Storage Usage */}
                  <Card>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        Storage Usage
                      </Typography>
                      
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">
                            Local Storage
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            2.4 MB / 10 MB
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            width: '100%',
                            height: 8,
                            bgcolor: 'grey.300',
                            borderRadius: 1,
                            overflow: 'hidden',
                          }}
                        >
                          <Box
                            sx={{
                              width: '24%',
                              height: '100%',
                              bgcolor: 'primary.main',
                              transition: 'width 0.3s ease',
                            }}
                          />
                        </Box>
                      </Box>

                      <Button
                        size="small"
                        startIcon={<DeleteIcon />}
                        variant="outlined"
                        fullWidth
                      >
                        Clear Cache
                      </Button>
                    </CardContent>
                  </Card>
                </Box>
              </motion.div>
            </Grid>
          </Grid>
        </motion.div>
      </Box>
    </>
  );
};

export default Settings;