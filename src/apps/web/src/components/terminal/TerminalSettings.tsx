import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Switch,
  FormControlLabel,
  Grid,
  Paper,
  IconButton,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Close,
  ExpandMore,
  Refresh,
  Download,
  Upload,
  Add,
  Delete,
  Edit,
  Palette
} from '@mui/icons-material';
import { ColorPicker } from './ColorPicker';

import { useTerminalStore } from '../../store/terminalStore';
import { TerminalTheme, TerminalShortcut } from '../../types/terminal';

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

interface TerminalSettingsProps {
  open: boolean;
  onClose: () => void;
}

export const TerminalSettings: React.FC<TerminalSettingsProps> = ({
  open,
  onClose
}) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [colorPicker, setColorPicker] = useState<{
    open: boolean;
    color: string;
    property: string;
  }>({ open: false, color: '', property: '' });
  const [newThemeName, setNewThemeName] = useState('');
  const [editingShortcut, setEditingShortcut] = useState<TerminalShortcut | null>(null);

  const {
    config,
    themes,
    shortcuts,
    updateConfig,
    setTheme,
    addTheme,
    exportConfig,
    importConfig
  } = useTerminalStore();

  const handleTabChange = useCallback((event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  }, []);

  const handleConfigChange = useCallback((updates: Partial<typeof config>) => {
    updateConfig(updates);
  }, [updateConfig]);

  const handleThemeChange = useCallback((themeName: string) => {
    setTheme(themeName);
  }, [setTheme]);

  const handleColorChange = useCallback((color: string) => {
    setColorPicker(prev => ({ ...prev, color }));
  }, []);

  const handleColorConfirm = useCallback((newColor: string) => {
    if (colorPicker.property) {
      const newTheme = {
        ...config.theme,
        [colorPicker.property]: newColor
      };
      updateConfig({ theme: newTheme });
    }
    setColorPicker({ open: false, color: '', property: '' });
  }, [colorPicker.property, config.theme, updateConfig]);

  const handleAddTheme = useCallback(() => {
    if (newThemeName.trim() && !themes[newThemeName]) {
      addTheme(newThemeName, config.theme);
      setNewThemeName('');
    }
  }, [newThemeName, themes, config.theme, addTheme]);

  const handleExportConfig = useCallback(() => {
    const configStr = exportConfig();
    const blob = new Blob([configStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `terminal-config-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [exportConfig]);

  const handleImportConfig = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const configStr = e.target?.result as string;
          importConfig(configStr);
        } catch (error) {
          console.error('Failed to import config:', error);
        }
      };
      reader.readAsText(file);
    }
  }, [importConfig]);

  const ColorButton: React.FC<{ color: string; property: string; label: string }> = ({
    color,
    property,
    label
  }) => (
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      <Box
        sx={{
          width: 32,
          height: 24,
          backgroundColor: color,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          cursor: 'pointer'
        }}
        onClick={() => setColorPicker({ open: true, color, property })}
      />
      <Typography variant="body2">{label}</Typography>
    </Box>
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          Terminal Settings
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Appearance" />
          <Tab label="Behavior" />
          <Tab label="Keyboard" />
          <Tab label="Advanced" />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Font Settings</Typography>
              
              <TextField
                fullWidth
                label="Font Family"
                value={config.fontFamily}
                onChange={(e) => handleConfigChange({ fontFamily: e.target.value })}
                margin="normal"
              />

              <Box sx={{ mt: 2 }}>
                <Typography gutterBottom>Font Size: {config.fontSize}px</Typography>
                <Slider
                  value={config.fontSize}
                  min={8}
                  max={32}
                  onChange={(_, value) => handleConfigChange({ fontSize: value as number })}
                />
              </Box>

              <Box sx={{ mt: 2 }}>
                <Typography gutterBottom>Line Height: {config.lineHeight}</Typography>
                <Slider
                  value={config.lineHeight}
                  min={0.8}
                  max={2.0}
                  step={0.1}
                  onChange={(_, value) => handleConfigChange({ lineHeight: value as number })}
                />
              </Box>

              <FormControl fullWidth margin="normal">
                <InputLabel>Font Weight</InputLabel>
                <Select
                  value={config.fontWeight}
                  onChange={(e) => handleConfigChange({ fontWeight: e.target.value as any })}
                >
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="bold">Bold</MenuItem>
                  <MenuItem value="100">100</MenuItem>
                  <MenuItem value="200">200</MenuItem>
                  <MenuItem value="300">300</MenuItem>
                  <MenuItem value="400">400</MenuItem>
                  <MenuItem value="500">500</MenuItem>
                  <MenuItem value="600">600</MenuItem>
                  <MenuItem value="700">700</MenuItem>
                  <MenuItem value="800">800</MenuItem>
                  <MenuItem value="900">900</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Theme</Typography>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>Select Theme</InputLabel>
                <Select
                  value={Object.keys(themes).find(name => themes[name] === config.theme) || 'custom'}
                  onChange={(e) => handleThemeChange(e.target.value)}
                >
                  {Object.keys(themes).map(name => (
                    <MenuItem key={name} value={name}>
                      {name.charAt(0).toUpperCase() + name.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Colors</Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <ColorButton
                      color={config.theme.foreground}
                      property="foreground"
                      label="Foreground"
                    />
                    <ColorButton
                      color={config.theme.background}
                      property="background"
                      label="Background"
                    />
                    <ColorButton
                      color={config.theme.cursor}
                      property="cursor"
                      label="Cursor"
                    />
                    <ColorButton
                      color={config.theme.selection}
                      property="selection"
                      label="Selection"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <ColorButton
                      color={config.theme.red}
                      property="red"
                      label="Red"
                    />
                    <ColorButton
                      color={config.theme.green}
                      property="green"
                      label="Green"
                    />
                    <ColorButton
                      color={config.theme.blue}
                      property="blue"
                      label="Blue"
                    />
                    <ColorButton
                      color={config.theme.yellow}
                      property="yellow"
                      label="Yellow"
                    />
                  </Grid>
                </Grid>
              </Box>

              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <TextField
                  size="small"
                  placeholder="Theme name"
                  value={newThemeName}
                  onChange={(e) => setNewThemeName(e.target.value)}
                />
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={handleAddTheme}
                  disabled={!newThemeName.trim() || !!themes[newThemeName]}
                >
                  Save as Theme
                </Button>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Cursor</Typography>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>Cursor Style</InputLabel>
                <Select
                  value={config.cursorStyle}
                  onChange={(e) => handleConfigChange({ cursorStyle: e.target.value as any })}
                >
                  <MenuItem value="block">Block</MenuItem>
                  <MenuItem value="underline">Underline</MenuItem>
                  <MenuItem value="bar">Bar</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={config.cursorBlink}
                    onChange={(e) => handleConfigChange({ cursorBlink: e.target.checked })}
                  />
                }
                label="Cursor Blinking"
              />

              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Scrolling</Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography gutterBottom>Scrollback Lines: {config.scrollback}</Typography>
                <Slider
                  value={config.scrollback}
                  min={100}
                  max={10000}
                  step={100}
                  onChange={(_, value) => handleConfigChange({ scrollback: value as number })}
                />
              </Box>

              <Box sx={{ mt: 2 }}>
                <Typography gutterBottom>Scroll Sensitivity: {config.scrollSensitivity}</Typography>
                <Slider
                  value={config.scrollSensitivity}
                  min={1}
                  max={10}
                  onChange={(_, value) => handleConfigChange({ scrollSensitivity: value as number })}
                />
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Behavior</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={config.bellSound}
                    onChange={(e) => handleConfigChange({ bellSound: e.target.checked })}
                  />
                }
                label="Bell Sound"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={config.allowTransparency}
                    onChange={(e) => handleConfigChange({ allowTransparency: e.target.checked })}
                  />
                }
                label="Allow Transparency"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={config.rightClickSelectsWord}
                    onChange={(e) => handleConfigChange({ rightClickSelectsWord: e.target.checked })}
                  />
                }
                label="Right Click Selects Word"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={config.macOptionIsMeta}
                    onChange={(e) => handleConfigChange({ macOptionIsMeta: e.target.checked })}
                  />
                }
                label="macOS Option as Meta"
              />

              <FormControl fullWidth margin="normal">
                <InputLabel>Renderer</InputLabel>
                <Select
                  value={config.rendererType}
                  onChange={(e) => handleConfigChange({ rendererType: e.target.value as any })}
                >
                  <MenuItem value="dom">DOM</MenuItem>
                  <MenuItem value="canvas">Canvas</MenuItem>
                  <MenuItem value="webgl">WebGL</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <Typography variant="h6" gutterBottom>Keyboard Shortcuts</Typography>
          
          {shortcuts.map((shortcut, index) => (
            <Paper key={index} sx={{ p: 2, mb: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    {shortcut.description}
                  </Typography>
                  <Box display="flex" gap={0.5} mt={0.5}>
                    {shortcut.ctrlKey && <Chip size="small" label="Ctrl" />}
                    {shortcut.shiftKey && <Chip size="small" label="Shift" />}
                    {shortcut.altKey && <Chip size="small" label="Alt" />}
                    {shortcut.metaKey && <Chip size="small" label="Meta" />}
                    <Chip size="small" label={shortcut.key} color="primary" />
                  </Box>
                </Box>
                <IconButton
                  size="small"
                  onClick={() => setEditingShortcut(shortcut)}
                >
                  <Edit />
                </IconButton>
              </Box>
            </Paper>
          ))}
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>Import/Export</Typography>
          
          <Box display="flex" gap={1} mb={3}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportConfig}
            >
              Export Settings
            </Button>
            <Button
              variant="outlined"
              startIcon={<Upload />}
              component="label"
            >
              Import Settings
              <input
                type="file"
                accept=".json"
                hidden
                onChange={handleImportConfig}
              />
            </Button>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>Reset</Typography>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Refresh />}
            onClick={() => {
              // Reset to defaults
              window.location.reload();
            }}
          >
            Reset to Defaults
          </Button>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Color Picker Dialog */}
      <ColorPicker
        open={colorPicker.open}
        color={colorPicker.color}
        title="Choose Terminal Color"
        onClose={() => setColorPicker({ open: false, color: '', property: '' })}
        onChange={handleColorConfirm}
      />
    </Dialog>
  );
};