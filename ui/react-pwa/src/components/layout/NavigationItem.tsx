import React from 'react';
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Box,
  Typography,
} from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

interface NavigationItemProps {
  path: string;
  label: string;
  icon: SvgIconComponent;
  description?: string;
  isActive: boolean;
  onClick?: () => void;
}

const NavigationItem: React.FC<NavigationItemProps> = ({
  path,
  label,
  icon: Icon,
  description,
  isActive,
  onClick,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(path);
    onClick?.();
  };

  return (
    <ListItem disablePadding sx={{ mb: 0.5 }}>
      <Tooltip
        title={description || label}
        placement="right"
        arrow
        PopperProps={{
          modifiers: [
            {
              name: 'offset',
              options: {
                offset: [0, 8],
              },
            },
          ],
        }}
      >
        <Box sx={{ width: '100%' }}>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <ListItemButton
              onClick={handleClick}
              selected={isActive}
              sx={{
                borderRadius: 2,
                mx: 1,
                position: 'relative',
                overflow: 'hidden',
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': {
                    color: 'inherit',
                  },
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                },
                '&:hover': {
                  bgcolor: isActive ? 'primary.dark' : 'action.hover',
                },
                '&:before': {
                  content: '""',
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: 3,
                  bgcolor: isActive ? 'primary.contrastText' : 'transparent',
                  borderRadius: '0 2px 2px 0',
                  transition: 'all 0.2s ease-in-out',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 40,
                  color: isActive ? 'inherit' : 'text.secondary',
                  transition: 'color 0.2s ease-in-out',
                }}
              >
                <Icon />
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Typography
                    variant="body2"
                    fontWeight={isActive ? 600 : 500}
                    sx={{
                      transition: 'font-weight 0.2s ease-in-out',
                    }}
                  >
                    {label}
                  </Typography>
                }
                secondary={
                  description && (
                    <Typography
                      variant="caption"
                      sx={{
                        color: isActive ? 'rgba(255, 255, 255, 0.7)' : 'text.secondary',
                        fontSize: '0.75rem',
                        lineHeight: 1.2,
                        mt: 0.5,
                        display: 'block',
                      }}
                    >
                      {description}
                    </Typography>
                  )
                }
              />
              
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                >
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      bgcolor: 'primary.contrastText',
                      borderRadius: '50%',
                      ml: 1,
                    }}
                  />
                </motion.div>
              )}
            </ListItemButton>
          </motion.div>
        </Box>
      </Tooltip>
    </ListItem>
  );
};

export default NavigationItem;