import React from 'react';
import {
  Box,
  Chip,
  Tooltip,
  Typography,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  CloudDone as ConnectedIcon,
  CloudOff as DisconnectedIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../../store/appStore';

interface ConnectionInfo {
  host: string;
  port: number;
  protocol: 'ws' | 'wss';
  lastConnected?: Date;
  retryCount: number;
  maxRetries: number;
}

interface ConnectionStatusProps {
  isConnected: boolean;
  connectionInfo: ConnectionInfo;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  connectionInfo,
}) => {
  const { isConnecting, reconnect } = useAppStore();
  const [expanded, setExpanded] = React.useState(false);

  const handleReconnect = async () => {
    try {
      await reconnect();
    } catch (error) {
      console.error('Reconnection failed:', error);
    }
  };

  const formatLastConnected = (date?: Date) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getConnectionUrl = () => {
    return `${connectionInfo.protocol === 'wss' ? 'wss' : 'ws'}://${connectionInfo.host}:${connectionInfo.port}`;
  };

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          borderRadius: 1,
          bgcolor: isConnected ? 'success.main' : 'error.main',
          color: 'white',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <motion.div
          animate={{ rotate: isConnecting ? 360 : 0 }}
          transition={{ duration: 1, repeat: isConnecting ? Infinity : 0 }}
        >
          {isConnected ? <ConnectedIcon /> : <DisconnectedIcon />}
        </motion.div>
        
        <Typography variant="body2" sx={{ flex: 1 }}>
          {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Disconnected'}
        </Typography>
        
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ExpandIcon fontSize="small" />
        </motion.div>
      </Box>

      <Collapse in={expanded}>
        <Box
          sx={{
            mt: 1,
            p: 2,
            bgcolor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
          }}
        >
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Connection Details
          </Typography>
          
          <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Server:
              </Typography>
              <Typography variant="body2" fontFamily="monospace">
                {getConnectionUrl()}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Status:
              </Typography>
              <Chip
                size="small"
                label={isConnected ? 'Online' : 'Offline'}
                color={isConnected ? 'success' : 'error'}
                variant="outlined"
              />
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Last connected:
              </Typography>
              <Typography variant="body2">
                {formatLastConnected(connectionInfo.lastConnected)}
              </Typography>
            </Box>
            
            {connectionInfo.retryCount > 0 && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Retry attempts:
                </Typography>
                <Typography variant="body2" color="warning.main">
                  {connectionInfo.retryCount}/{connectionInfo.maxRetries}
                </Typography>
              </Box>
            )}
            
            <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
              <Tooltip title="Reconnect to server">
                <IconButton
                  size="small"
                  onClick={handleReconnect}
                  disabled={isConnecting}
                  sx={{ 
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                  }}
                >
                  <motion.div
                    animate={{ rotate: isConnecting ? 360 : 0 }}
                    transition={{ duration: 1, repeat: isConnecting ? Infinity : 0 }}
                  >
                    <RefreshIcon fontSize="small" />
                  </motion.div>
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>
      </Collapse>
    </Box>
  );
};

export default ConnectionStatus;