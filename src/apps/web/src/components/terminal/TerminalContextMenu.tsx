import React from 'react';
import {
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  MenuProps
} from '@mui/material';
import {
  ContentCopy,
  ContentPaste,
  SelectAll,
  Clear,
  Search,
  Settings,
  ZoomIn,
  ZoomOut,
  Refresh,
  Download
} from '@mui/icons-material';

interface TerminalContextMenuProps {
  open: boolean;
  anchorPosition?: { x: number; y: number } | null;
  onClose: () => void;
  onCopy: () => void;
  onPaste: () => void;
  onSelectAll: () => void;
  onClear: () => void;
  onSearch: () => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onReload?: () => void;
  onSettings?: () => void;
  onExport?: () => void;
  hasSelection: boolean;
}

export const TerminalContextMenu: React.FC<TerminalContextMenuProps> = ({
  open,
  anchorPosition,
  onClose,
  onCopy,
  onPaste,
  onSelectAll,
  onClear,
  onSearch,
  onZoomIn,
  onZoomOut,
  onReload,
  onSettings,
  onExport,
  hasSelection
}) => {
  return (
    <Menu
      open={open}
      onClose={onClose}
      anchorReference="anchorPosition"
      anchorPosition={anchorPosition}
      slotProps={{
        paper: {
          sx: {
            minWidth: 200,
            '& .MuiMenuItem-root': {
              fontSize: '0.875rem'
            }
          }
        }
      }}
    >
      <MenuItem onClick={onCopy} disabled={!hasSelection}>
        <ListItemIcon>
          <ContentCopy fontSize="small" />
        </ListItemIcon>
        <ListItemText>Copy</ListItemText>
        <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
          Ctrl+Shift+C
        </ListItemText>
      </MenuItem>

      <MenuItem onClick={onPaste}>
        <ListItemIcon>
          <ContentPaste fontSize="small" />
        </ListItemIcon>
        <ListItemText>Paste</ListItemText>
        <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
          Ctrl+Shift+V
        </ListItemText>
      </MenuItem>

      <Divider />

      <MenuItem onClick={onSelectAll}>
        <ListItemIcon>
          <SelectAll fontSize="small" />
        </ListItemIcon>
        <ListItemText>Select All</ListItemText>
        <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
          Ctrl+A
        </ListItemText>
      </MenuItem>

      <MenuItem onClick={onSearch}>
        <ListItemIcon>
          <Search fontSize="small" />
        </ListItemIcon>
        <ListItemText>Find</ListItemText>
        <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
          Ctrl+Shift+F
        </ListItemText>
      </MenuItem>

      <Divider />

      <MenuItem onClick={onClear}>
        <ListItemIcon>
          <Clear fontSize="small" />
        </ListItemIcon>
        <ListItemText>Clear Terminal</ListItemText>
        <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
          Ctrl+Shift+K
        </ListItemText>
      </MenuItem>

      {onReload && (
        <MenuItem onClick={onReload}>
          <ListItemIcon>
            <Refresh fontSize="small" />
          </ListItemIcon>
          <ListItemText>Reload Session</ListItemText>
        </MenuItem>
      )}

      <Divider />

      {onZoomIn && (
        <MenuItem onClick={onZoomIn}>
          <ListItemIcon>
            <ZoomIn fontSize="small" />
          </ListItemIcon>
          <ListItemText>Zoom In</ListItemText>
          <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
            Ctrl++
          </ListItemText>
        </MenuItem>
      )}

      {onZoomOut && (
        <MenuItem onClick={onZoomOut}>
          <ListItemIcon>
            <ZoomOut fontSize="small" />
          </ListItemIcon>
          <ListItemText>Zoom Out</ListItemText>
          <ListItemText sx={{ textAlign: 'right', color: 'text.secondary' }}>
            Ctrl+-
          </ListItemText>
        </MenuItem>
      )}

      {onExport && (
        <>
          <Divider />
          <MenuItem onClick={onExport}>
            <ListItemIcon>
              <Download fontSize="small" />
            </ListItemIcon>
            <ListItemText>Export Session</ListItemText>
          </MenuItem>
        </>
      )}

      {onSettings && (
        <>
          <Divider />
          <MenuItem onClick={onSettings}>
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            <ListItemText>Terminal Settings</ListItemText>
          </MenuItem>
        </>
      )}
    </Menu>
  );
};