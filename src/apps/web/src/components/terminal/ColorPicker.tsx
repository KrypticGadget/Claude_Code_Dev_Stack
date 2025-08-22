import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Paper
} from '@mui/material';

interface ColorPickerProps {
  open: boolean;
  color: string;
  title?: string;
  onClose: () => void;
  onChange: (color: string) => void;
}

export const ColorPicker: React.FC<ColorPickerProps> = ({
  open,
  color,
  title = 'Choose Color',
  onClose,
  onChange
}) => {
  const [currentColor, setCurrentColor] = useState(color);
  const [inputValue, setInputValue] = useState(color);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Predefined color palette
  const presetColors = [
    // Grays
    '#000000', '#333333', '#666666', '#999999', '#cccccc', '#ffffff',
    // Reds
    '#ff0000', '#cc0000', '#990000', '#660000', '#ff3333', '#ff6666',
    // Greens
    '#00ff00', '#00cc00', '#009900', '#006600', '#33ff33', '#66ff66',
    // Blues
    '#0000ff', '#0000cc', '#000099', '#000066', '#3333ff', '#6666ff',
    // Yellows
    '#ffff00', '#cccc00', '#999900', '#666600', '#ffff33', '#ffff66',
    // Purples
    '#ff00ff', '#cc00cc', '#990099', '#660066', '#ff33ff', '#ff66ff',
    // Cyans
    '#00ffff', '#00cccc', '#009999', '#006666', '#33ffff', '#66ffff',
    // Terminal colors
    '#1e1e1e', '#2d2d2d', '#3c3c3c', '#4b4b4b', '#5a5a5a', '#696969',
    '#cd3131', '#0dbc79', '#e5e510', '#2472c8', '#bc3fbc', '#11a8cd',
    '#f14c4c', '#23d18b', '#f5f543', '#3b8eea', '#d670d6', '#29b8db'
  ];

  useEffect(() => {
    setCurrentColor(color);
    setInputValue(color);
  }, [color]);

  useEffect(() => {
    if (open) {
      drawColorWheel();
    }
  }, [open]);

  const drawColorWheel = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;

    // Draw color wheel
    for (let angle = 0; angle < 360; angle += 1) {
      const startAngle = (angle - 1) * Math.PI / 180;
      const endAngle = angle * Math.PI / 180;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.lineWidth = 2;
      ctx.strokeStyle = `hsl(${angle}, 100%, 50%)`;
      ctx.stroke();
    }

    // Draw brightness gradient
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = gradient;
    ctx.fill();
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const deltaX = x - centerX;
    const deltaY = y - centerY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    const radius = Math.min(centerX, centerY) - 10;

    if (distance <= radius) {
      const angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;
      const hue = (angle + 360) % 360;
      const saturation = Math.min(distance / radius * 100, 100);
      const lightness = 50;

      const hslColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
      const hexColor = hslToHex(hue, saturation / 100, lightness / 100);
      
      setCurrentColor(hexColor);
      setInputValue(hexColor);
    }
  };

  const hslToHex = (h: number, s: number, l: number): string => {
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;
    
    let r = 0, g = 0, b = 0;
    
    if (0 <= h && h < 60) {
      r = c; g = x; b = 0;
    } else if (60 <= h && h < 120) {
      r = x; g = c; b = 0;
    } else if (120 <= h && h < 180) {
      r = 0; g = c; b = x;
    } else if (180 <= h && h < 240) {
      r = 0; g = x; b = c;
    } else if (240 <= h && h < 300) {
      r = x; g = 0; b = c;
    } else if (300 <= h && h < 360) {
      r = c; g = 0; b = x;
    }
    
    const red = Math.round((r + m) * 255);
    const green = Math.round((g + m) * 255);
    const blue = Math.round((b + m) * 255);
    
    return `#${red.toString(16).padStart(2, '0')}${green.toString(16).padStart(2, '0')}${blue.toString(16).padStart(2, '0')}`;
  };

  const isValidHex = (hex: string): boolean => {
    return /^#[0-9A-F]{6}$/i.test(hex);
  };

  const handleInputChange = (value: string) => {
    setInputValue(value);
    if (isValidHex(value)) {
      setCurrentColor(value);
    }
  };

  const handlePresetClick = (presetColor: string) => {
    setCurrentColor(presetColor);
    setInputValue(presetColor);
  };

  const handleConfirm = () => {
    onChange(currentColor);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box display="flex" flexDirection="column" alignItems="center">
              <canvas
                ref={canvasRef}
                width={200}
                height={200}
                style={{
                  cursor: 'crosshair',
                  border: '1px solid #ccc',
                  borderRadius: '50%'
                }}
                onClick={handleCanvasClick}
              />
              
              <Box mt={2} display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    backgroundColor: currentColor,
                    border: '1px solid #ccc',
                    borderRadius: 1
                  }}
                />
                <TextField
                  size="small"
                  value={inputValue}
                  onChange={(e) => handleInputChange(e.target.value)}
                  placeholder="#ffffff"
                  error={!isValidHex(inputValue)}
                  helperText={!isValidHex(inputValue) ? 'Invalid hex color' : ''}
                />
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 1, maxHeight: 300, overflow: 'auto' }}>
              <Grid container spacing={0.5}>
                {presetColors.map((presetColor, index) => (
                  <Grid item key={index} xs={2}>
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: presetColor,
                        border: currentColor === presetColor ? '2px solid #000' : '1px solid #ccc',
                        borderRadius: 0.5,
                        cursor: 'pointer',
                        '&:hover': {
                          transform: 'scale(1.1)',
                          transition: 'transform 0.1s'
                        }
                      }}
                      onClick={() => handlePresetClick(presetColor)}
                      title={presetColor}
                    />
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleConfirm} variant="contained" disabled={!isValidHex(inputValue)}>
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  );
};